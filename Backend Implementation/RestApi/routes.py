import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, Query, Request

from auth import get_current_user
from config import settings
from exceptions import AppError
from rate_limiter import rate_limiter
from repository import OrderRepository
from schemas import ApiResponse, CreateOrderRequest, OrderResponse, PaginatedData
from service import OrderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_prefix, tags=["orders"])

_repository = OrderRepository()
_service = OrderService(_repository)


def get_order_service() -> OrderService:
    return _service


def enforce_rate_limit(request: Request, user_id: str = Depends(get_current_user)) -> str:
    client_key = user_id or (request.client.host if request.client else "anonymous")
    rate_limiter.check(client_key)
    return user_id


@router.get("/health")
def health() -> ApiResponse[dict]:
    return ApiResponse(data={"status": "up"})


@router.post("/orders", response_model=ApiResponse[OrderResponse], status_code=201)
def create_order(
    request: Request,
    payload: CreateOrderRequest,
    user_id: str = Depends(enforce_rate_limit),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    service: OrderService = Depends(get_order_service),
) -> ApiResponse[OrderResponse]:
    order = service.create_order(user_id, payload, idempotency_key)
    return ApiResponse(data=order, trace_id=request.state.trace_id)


@router.get("/orders/{order_id}", response_model=ApiResponse[OrderResponse])
def get_order(
    request: Request,
    order_id: str,
    user_id: str = Depends(enforce_rate_limit),
    service: OrderService = Depends(get_order_service),
) -> ApiResponse[OrderResponse]:
    order = service.get_order(user_id, order_id)
    return ApiResponse(data=order, trace_id=request.state.trace_id)


@router.get("/orders", response_model=ApiResponse[PaginatedData[OrderResponse]])
def list_orders(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.default_page_size, ge=1, le=settings.max_page_size),
    user_id: str = Depends(enforce_rate_limit),
    service: OrderService = Depends(get_order_service),
) -> ApiResponse[PaginatedData[OrderResponse]]:
    items, total = service.list_orders(user_id, page, page_size)
    payload = PaginatedData(items=items, total=total, page=page, page_size=page_size)
    return ApiResponse(data=payload, trace_id=request.state.trace_id)


@router.delete("/orders/{order_id}", response_model=ApiResponse[OrderResponse])
def cancel_order(
    request: Request,
    order_id: str,
    user_id: str = Depends(enforce_rate_limit),
    service: OrderService = Depends(get_order_service),
) -> ApiResponse[OrderResponse]:
    order = service.cancel_order(user_id, order_id)
    return ApiResponse(data=order, trace_id=request.state.trace_id)


@router.get("/products/{product_id}/external-info", response_model=ApiResponse[dict])
def get_external_product_info(
    request: Request,
    product_id: str,
    user_id: str = Depends(enforce_rate_limit),
    service: OrderService = Depends(get_order_service),
) -> ApiResponse[dict]:
    data = service.enrich_from_external_catalog(product_id)
    return ApiResponse(data=data, trace_id=request.state.trace_id)
