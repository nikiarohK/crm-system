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
        request = CreateOrderRequest(
            customer_id=customer_id,
            product_name=product_name,
            price=price
        )
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
    
    def list_orders(self, page: int, limit: int):
        try:
            if page <= 0 or limit <= 0:
                raise ValueError("Отрицательное число")

            request = ListOrdersRequest(page=page, limit=limit)
            response = self.client.ListOrders(request)
            return {
                "orders": [
                    {
                        'id': order.id,
                        'customer_id': order.customer_id,
                        'product_name': order.product_name,
                        'price': order.price,
                        'created_at': order.created_at
                    } for order in response.orders
                ],
                "total": response.total
            }
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")
        
    def delete(self, order_id):
        request = DeleteOrderRequest(id=order_id)
        response = self.client.DeleteOrder(request)
        return {"success": response.success}