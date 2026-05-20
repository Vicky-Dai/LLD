from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Order API Demo"
    api_prefix: str = "/api/v1"
    api_key: str = "demo-api-key-12345"
    jwt_secret: str = "demo-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    request_timeout_seconds: float = 5.0
    rate_limit_per_minute: int = 60
    default_page_size: int = 20
    max_page_size: int = 100
    valid_products: frozenset[str] = frozenset({"sku-001", "sku-002", "sku-003"})


settings = Settings()
