from pydantic import BaseModel, Field, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=1000)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=5, max_length=40)
    address: str = ""
    notes: str = ""
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str


class OrderOut(BaseModel):
    id: int
    order_number: str
    status: str
    total: float
    notes: str
    created_at: str
    customer_name: str
    phone: str
    item_count: int
