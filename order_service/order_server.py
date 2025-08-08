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

class OrderService(OrderServiceServicer):
    def __init__(self):
        self.pool = PostgresConnectionPool()
        self._init_db()

    def _init_db(self):
        conn = self.pool.get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id TEXT PRIMARY KEY,
                        customer_id TEXT NOT NULL,
                        product_name TEXT NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        CONSTRAINT valid_price CHECK (price > 0),
                        CONSTRAINT fk_customer 
                            FOREIGN KEY (customer_id) 
                            REFERENCES customers(id)
                            ON DELETE CASCADE
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

    def CreateOrder(self, request, context):

        order_id = str(uuid.uuid4())
        created_at = datetime.now()

        try:
            self._execute_query(
                '''INSERT INTO orders (id, customer_id, product_name, price, created_at)
                   VALUES (%s, %s, %s, %s, %s)''',
                (order_id, request.customer_id, request.product_name, request.price, created_at)
            )
            return OrderResponse(
                id=order_id,
                customer_id=request.customer_id,
                product_name=request.product_name,
                price=request.price,
                created_at=created_at.isoformat()
            )
        except psycopg2.IntegrityError as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Ошибка базы данных: {str(e)}")

    def ListOrders(self, request, context):
        try:
            if request.page <= 0 or request.limit <= 0:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "page and limit must be positive integers")

            orders = self._execute_query(
                '''SELECT id, customer_id, product_name, price, created_at 
                FROM orders
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s''',
                (request.limit, (request.page - 1) * request.limit),
                fetchall=True
            )
            
            total = self._execute_query(
                '''SELECT COUNT(*) FROM orders''',
                fetchone=True
            )[0]
            
            return ListOrdersResponse(
                orders=[
                    OrderResponse(
                        id=row[0],
                        customer_id=row[1],
                        product_name=row[2],
                        price=row[3],
                        created_at=row[4].isoformat()
                    ) for row in orders
                ],
                total=total
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Database error: {str(e)}")
            
    def GetCustomerOrder(self, request, context):
        if not request.customer_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "customer_id is required")

        try:
            orders = self._execute_query(
                '''SELECT id, customer_id, product_name, price, created_at 
                FROM orders 
                WHERE customer_id = %s
                ORDER BY created_at DESC''',
                (request.customer_id,),
                fetchall=True
            )
            
            if not orders:
                context.abort(grpc.StatusCode.NOT_FOUND, "No orders found")

            first_order = orders[0]
            return OrderResponse(
                id=first_order[0],
                customer_id=first_order[1],
                product_name=first_order[2],
                price=first_order[3],
                created_at=first_order[4].isoformat()
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Database error: {str(e)}")
            
    def DeleteOrder(self, request, context):
        try:
            self._execute_query(
                '''DELETE FROM orders WHERE id = %s''',
                (request.id,)
            )
            return DeleteOrderResponse(success=True)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Database error: {str(e)}")
            
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50052')
    print("Order Service запущен на порту 50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()