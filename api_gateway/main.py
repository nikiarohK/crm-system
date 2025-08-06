from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
import grpc
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from crm_pb2 import *
from crm_pb2_grpc import *
from dotenv import load_dotenv
import os
from models import *
from typing import List, Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

customer_channel = grpc.insecure_channel('localhost:50051')
customer_client = CustomerServiceStub(customer_channel)

order_channel = grpc.insecure_channel('localhost:50052')
order_client = OrderServiceStub(order_channel)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    
    return username

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/register", response_model=Token)
async def register(user: UserRegister):
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/customers", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate, 
    current_user: str = Depends(get_current_user)
):
    try:
        request = CreateCustomerRequest(name=customer.name, email=customer.email)
        response = customer_client.CreateCustomer(request)
        return CustomerResponse(
            id=response.id,
            name=response.name,
            email=response.email,
            created_at=response.created_at
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail=e.details())

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        request = GetCustomerRequest(id=customer_id)
        response = customer_client.GetCustomer(request)
        return CustomerResponse(
            id=response.id,
            name=response.name,
            email=response.email,
            created_at=response.created_at  
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Customer not found")
        raise HTTPException(status_code=400, detail=e.details())

@app.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    page: int = 1,
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    try:
        request = ListCustomersRequest(page=page, limit=limit)
        response = customer_client.ListCustomers(request)
        return [
            CustomerResponse(
                id=customer.id,
                name=customer.name,
                email=customer.email,
                created_at=customer.created_at
            ) for customer in response.customers
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=e.details())

@app.post("/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user: str = Depends(get_current_user)
):
    try:
        request = CreateOrderRequest(
            customer_id=order.customer_id,
            product_name=order.product_name,
            price=order.price
        )
        response = order_client.CreateOrder(request)
        return OrderResponse(
            id=response.id,
            customer_id=response.customer_id,
            product_name=response.product_name,
            price=response.price,
            created_at=response.created_at
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Customer not found")
        raise HTTPException(status_code=400, detail=e.details())

@app.get("/orders/{customer_id}", response_model=OrderResponse)
async def get_customer_order(
    customer_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        request = GetCustomerOrderRequest(customer_id=customer_id)
        response = order_client.GetCustomerOrder(request)
        return OrderResponse(
            id=response.id,
            customer_id=response.customer_id,
            product_name=response.product_name,
            price=response.price,
            created_at=response.created_at
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Order not found")
        raise HTTPException(status_code=400, detail=e.details())