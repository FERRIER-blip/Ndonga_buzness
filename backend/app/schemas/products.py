from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = ""
    category: str = "Autres"
    price: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    image_url: str = ""
    active: bool = True


class ProductUpdate(ProductCreate):
    pass


class ProductOut(ProductCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
