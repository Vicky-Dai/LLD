from datetime import datetime
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class CreateOrderRequest(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=64)
    quantity: int = Field(..., ge=1, le=1000)
    note: Optional[str] = Field(default=None, max_length=500)

    @field_validator("product_id")
    @classmethod
    def strip_product_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("product_id cannot be blank")
        return cleaned


class OrderResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: OrderStatus
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaginationQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str = "OK"
    message: str = "success"
    data: Optional[T] = None
    trace_id: Optional[str] = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
