from pydantic import BaseModel

class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class OrderUpdateStatus(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    status: str
    total_price: float

    class Config:
        from_attributes = True