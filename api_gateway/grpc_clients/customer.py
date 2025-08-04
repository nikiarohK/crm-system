import grpc
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from crm_pb2 import *
from crm_pb2_grpc import *

class CustomerClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.client = CustomerServiceStub(self.channel)
        
    def create(self, name, email):
        request = CreateCustomerRequest(name=name, email=email)
        response = self.client.CreateCustomer(request)
        return {
            "id": response.id,
            "name": response.name,
            "email": response.email,
            "created_at": response.created_at
        }
    
    def get(self, id):
        request = GetCustomerRequest(id=id)
        response = self.client.GetCustomer(request)
        if not response.id:
            raise ValueError("Customer not found")
        return {
            "id": response.id,
            "name": response.name,
            "email": response.email,
            "created_at": response.created_at
        }
    
    def update(self, id, name, email):
        request = UpdateCustomerRequest(id=id, name=name, email=email)
        response = self.client.UpdateCustomer(request)
        return {
            "id": response.id,
            "name": response.name,
            "email": response.email,
            "created_at": response.created_at
        }
    
    def delete(self, id):
        request = DeleteCustomerRequest(id=id)
        response = self.client.DeleteCustomer(request)
        return {"success": response.success}
    
    def list_customers(self, page: int, limit: int):
        request = ListCustomersRequest(page=page, limit=limit)
        response = self.client.ListCustomers(request)
        return {
            "customers": [
                {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "created_at": customer.created_at
                } for customer in response.customers
            ],
            "total": response.total
        }