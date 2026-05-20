import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt

from config import settings
from exceptions import ForbiddenError, UnauthorizedError

logger = logging.getLogger(__name__)


def create_access_token(user_id: str, expires_minutes: int = 60) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token payload")
        return user_id
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> str:
    if x_api_key:
        if x_api_key != settings.api_key:
            raise UnauthorizedError("Invalid API key")
        return "service-account"

    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing Bearer token or X-API-Key")

    token = authorization.removeprefix("Bearer ").strip()
    return decode_access_token(token)


def require_admin(user_id: str = Depends(get_current_user)) -> str:
    if user_id != "admin":
        raise ForbiddenError("Admin role required")
    return user_id
