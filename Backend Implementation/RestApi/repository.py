from models import Order


class OrderRepository:
    """In-memory persistence layer. Swap for SQL/NoSQL in production."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._idempotency_index: dict[str, str] = {}

    def save(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

    def find_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def find_by_user(self, user_id: str, page: int, page_size: int) -> tuple[list[Order], int]:
        user_orders = [order for order in self._orders.values() if order.user_id == user_id]
        user_orders.sort(key=lambda item: item.created_at, reverse=True)
        total = len(user_orders)
        start = (page - 1) * page_size
        end = start + page_size
        return user_orders[start:end], total

    def find_by_idempotency_key(self, key: str) -> Order | None:
        order_id = self._idempotency_index.get(key)
        if order_id is None:
            return None
        return self._orders.get(order_id)

    def bind_idempotency_key(self, key: str, order_id: str) -> None:
        self._idempotency_index[key] = order_id
