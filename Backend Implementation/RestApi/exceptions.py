from dataclasses import dataclass


@dataclass
class AppError(Exception):
    code: str
    message: str
    http_status: int = 400

    def __str__(self) -> str:
        return self.message


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(code="VALIDATION_ERROR", message=message, http_status=400)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="UNAUTHORIZED", message=message, http_status=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(code="FORBIDDEN", message=message, http_status=403)


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found: {resource_id}",
            http_status=404,
        )


class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(code="CONFLICT", message=message, http_status=409)


class RateLimitError(AppError):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(code="RATE_LIMITED", message=message, http_status=429)


class ExternalServiceError(AppError):
    def __init__(self, message: str):
        super().__init__(code="EXTERNAL_SERVICE_ERROR", message=message, http_status=502)
