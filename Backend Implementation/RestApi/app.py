import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from config import settings
from exceptions import AppError
from middleware import RequestContextMiddleware
from routes import router
from schemas import ApiResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title=settings.app_name)
app.add_middleware(RequestContextMiddleware)
app.include_router(router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None)
    body = ApiResponse(code=exc.code, message=exc.message, data=None, trace_id=trace_id)
    return JSONResponse(status_code=exc.http_status, content=body.model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None)
    message = "; ".join(
        f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}" for err in exc.errors()
    )
    body = ApiResponse(code="VALIDATION_ERROR", message=message, data=None, trace_id=trace_id)
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).exception("Unhandled exception trace_id=%s", getattr(request.state, "trace_id", None))
    trace_id = getattr(request.state, "trace_id", None)
    body = ApiResponse(code="INTERNAL_ERROR", message="Internal server error", data=None, trace_id=trace_id)
    return JSONResponse(status_code=500, content=body.model_dump(mode="json"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
