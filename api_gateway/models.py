from pydantic import BaseModel
from typing import List, Optional

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CustomerCreate(BaseModel):
    name: str
    email: str

class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str

class OrderCreate(BaseModel):
    customer_id: str
    product_name: str
    price: float

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    product_name: str
    price: float
    created_at: str