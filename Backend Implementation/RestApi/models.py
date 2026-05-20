from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from schemas import OrderStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Order:
    user_id: str
    product_id: str
    quantity: int
    note: str | None = None
    status: OrderStatus = OrderStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def confirm(self) -> None:
        if self.status == OrderStatus.CANCELLED:
            raise ValueError("Cancelled order cannot be confirmed")
        self.status = OrderStatus.CONFIRMED
        self.updated_at = utc_now()

    def cancel(self) -> None:
        if self.status == OrderStatus.CANCELLED:
            raise ValueError("Order already cancelled")
        self.status = OrderStatus.CANCELLED
        self.updated_at = utc_now()
