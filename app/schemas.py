from datetime import datetime
from typing import List
from pydantic import BaseModel

class ProductBaseSchema(BaseModel):
    sku: str

    class Config:
        orm_mode = True


class CreateProductSchema(ProductBaseSchema):
    pass


class ProductResponse(ProductBaseSchema):
    id: int
    sku: str
    created_at: datetime
    updated_at: datetime | None


class UpdateProductSchema(BaseModel):
    id: int
    sku: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True


class ListProductResponse(BaseModel):
    status: str
    results: int
    data: List[ProductResponse]


class WarehouseBaseSchema(BaseModel):
    sub_inventory: str
    name: str

    class Config:
        orm_mode = True


class CreateWarehouseSchema(WarehouseBaseSchema):
    pass


class WarehouseResponse(WarehouseBaseSchema):
    id: int
    sub_inventory: str
    name: str
    created_at: datetime


class UpdateWarehouseSchema(BaseModel):
    id: int
    sub_inventory: str
    name: str
    created_at: datetime | None

    class Config:
        orm_mode = True


class ListWarehouseResponse(BaseModel):
    status: str
    results: int
    data: List[WarehouseResponse]
