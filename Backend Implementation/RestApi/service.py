import logging

from config import settings
from exceptions import ConflictError, NotFoundError, ValidationError
from external_client import fetch_data
from models import Order
from repository import OrderRepository
from schemas import CreateOrderRequest, OrderResponse, OrderStatus

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def create_order(
        self,
        user_id: str,
        payload: CreateOrderRequest,
        idempotency_key: str | None = None,
    ) -> OrderResponse:
        if idempotency_key:
            existing = self._repository.find_by_idempotency_key(idempotency_key)
            if existing is not None:
                logger.info("Idempotent replay order_id=%s key=%s", existing.id, idempotency_key)
                return self._to_response(existing)

        self._validate_product(payload.product_id)

        order = Order(
            user_id=user_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            note=payload.note,
        )
        order.confirm()

        saved = self._repository.save(order)
        if idempotency_key:
            self._repository.bind_idempotency_key(idempotency_key, saved.id)

        logger.info("Order created order_id=%s user_id=%s", saved.id, user_id)
        return self._to_response(saved)

    def get_order(self, user_id: str, order_id: str) -> OrderResponse:
        order = self._require_order(order_id)
        if order.user_id != user_id and user_id != "service-account":
            raise ValidationError("Cannot access another user's order")
        return self._to_response(order)

    def list_orders(self, user_id: str, page: int, page_size: int) -> tuple[list[OrderResponse], int]:
        orders, total = self._repository.find_by_user(user_id, page, page_size)
        return [self._to_response(order) for order in orders], total

    def cancel_order(self, user_id: str, order_id: str) -> OrderResponse:
        order = self._require_order(order_id)
        if order.user_id != user_id:
            raise ValidationError("Cannot cancel another user's order")
        if order.status == OrderStatus.CANCELLED:
            raise ConflictError("Order already cancelled")

        order.cancel()
        saved = self._repository.save(order)
        logger.info("Order cancelled order_id=%s user_id=%s", saved.id, user_id)
        return self._to_response(saved)

    def enrich_from_external_catalog(self, product_id: str) -> dict:
        url = f"https://jsonplaceholder.typicode.com/posts/1"
        data = fetch_data(url)
        return {"product_id": product_id, "external_ref": data.get("id"), "title": data.get("title")}

    def _validate_product(self, product_id: str) -> None:
        if product_id not in settings.valid_products:
            raise ValidationError(f"Unknown product_id: {product_id}")

    def _require_order(self, order_id: str) -> Order:
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise NotFoundError("Order", order_id)
        return order

    @staticmethod
    def _to_response(order: Order) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            status=order.status,
            note=order.note,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
