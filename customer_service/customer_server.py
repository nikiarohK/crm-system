from concurrent import futures
import grpc
import uuid
from datetime import datetime
import psycopg2
from psycopg2 import pool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from crm_pb2 import *
from crm_pb2_grpc import *
import os

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "crm_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "123456")
}

class PostgresConnectionPool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_pool()
        return cls._instance

    def _init_pool(self):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **POSTGRES_CONFIG
        )

    def get_conn(self):
        return self.pool.getconn()

    def put_conn(self, conn):
        self.pool.putconn(conn)

class CustomerService(CustomerServiceServicer):
    def __init__(self):
        self.pool = PostgresConnectionPool()
        self._init_db()

    def _init_db(self):
        conn = self.pool.get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP NOT NULL
                    )
                ''')
                conn.commit()
        finally:
            self.pool.put_conn(conn)

    def _execute_query(self, query, params=None, fetchone=False, fetchall=False):
        conn = self.pool.get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.put_conn(conn)

    def CreateCustomer(self, request, context):
        customer_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        try:
            self._execute_query(
                '''INSERT INTO customers (id, name, email, created_at)
                   VALUES (%s, %s, %s, %s)''',
                (customer_id, request.name, request.email, created_at)
            )
            return CustomerResponse(
                id=customer_id,
                name=request.name,
                email=request.email,
                created_at=created_at.isoformat()
            )
        except psycopg2.IntegrityError as e:
            if "duplicate key" in str(e):
                context.abort(grpc.StatusCode.ALREADY_EXISTS, "Email уже существует")
            context.abort(grpc.StatusCode.INTERNAL, f"Ошибка базы данных: {str(e)}")

    def GetCustomer(self, request, context):
        customer = self._execute_query(
            '''SELECT id, name, email, created_at 
               FROM customers WHERE id = %s''',
            (request.id,),
            fetchone=True
        )
        
        if not customer:
            context.abort(grpc.StatusCode.NOT_FOUND, "Клиент не найден")
            
        return CustomerResponse(
            id=customer[0],
            name=customer[1],
            email=customer[2],
            created_at=customer[3].isoformat()
        )

    def UpdateCustomer(self, request, context):
        try:
            self._execute_query(
                '''UPDATE customers 
                   SET name = %s, email = %s 
                   WHERE id = %s''',
                (request.name, request.email, request.id)
            )
            return CustomerResponse(
                id=request.id,
                name=request.name,
                email=request.email,
                created_at="" 
            )
        except psycopg2.Error as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Ошибка базы данных: {str(e)}")

    def DeleteCustomer(self, request, context):
        try:
            self._execute_query(
                '''DELETE FROM customers WHERE id = %s''',
                (request.id,)
            )
            return DeleteCustomerResponse(success=True)
        except psycopg2.Error as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Ошибка базы данных: {str(e)}")

    def ListCustomers(self, request, context):
        customers = self._execute_query(
            '''SELECT id, name, email, created_at 
               FROM customers
               ORDER BY created_at DESC
               LIMIT %s OFFSET %s''',
            (request.limit, (request.page - 1) * request.limit),
            fetchall=True
        )
        
        customer_list = [
            CustomerResponse(
                id=row[0],
                name=row[1],
                email=row[2],
                created_at=row[3].isoformat()
            ) for row in customers
        ]
        
        total = self._execute_query(
            '''SELECT COUNT(*) FROM customers''',
            fetchone=True
        )[0]
        
        return ListCustomersResponse(
            customers=customer_list,
            total=total
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_CustomerServiceServicer_to_server(CustomerService(), server)
    server.add_insecure_port('[::]:50051')  
    print("Customer Service запущен на порту 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()