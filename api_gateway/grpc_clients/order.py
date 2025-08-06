import grpc
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from crm_pb2 import *
from crm_pb2_grpc import *


class OrderClient:
    def __init__(self, host='localhost', port=50052):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.client = OrderServiceStub(self.channel)
    
    def create(self, customer_id, product_name, price):
        request = CreateOrderRequest(customer_id=customer_id, product_name=product_name, price=price)
        response = self.client.CreateOrder(request)
        return {
            'id': response.id,
            'customer_id': response.customer_id,
            'product_name': response.product_name,
            'price': response.price,
            'created_at': response.created_at
        }
    
    def get(self, customer_id):
        request = GetCustomerOrderRequest(customer_id=customer_id)
        response = self.client.GetCustomerOrder(request)
        return {
            'id': response.id,
            'customer_id': response.customer_id,
            'product_name': response.product_name,
            'price': response.price,
            'created_at': response.created_at
        }
    
    
    