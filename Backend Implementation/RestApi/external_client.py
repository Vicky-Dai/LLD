import logging
from typing import Any

import requests

from config import settings
from exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


def fetch_data(url: str, timeout: float | None = None) -> dict[str, Any]:
    """Call an external HTTP API with timeout and structured error handling."""
    timeout = timeout or settings.request_timeout_seconds

    try:
        response = requests.get(url, timeout=timeout)
    except requests.Timeout as exc:
        logger.error("External API timeout url=%s", url)
        raise ExternalServiceError(f"Timeout calling external service: {url}") from exc
    except requests.RequestException as exc:
        logger.error("External API request failed url=%s error=%s", url, exc)
        raise ExternalServiceError(f"Failed to call external service: {url}") from exc

    if response.status_code != 200:
        logger.warning(
            "External API non-200 url=%s status=%s body=%s",
            url,
            response.status_code,
            response.text[:200],
        )
        raise ExternalServiceError(
            f"External service returned {response.status_code} for {url}"
        )

    try:
        return response.json()
    except ValueError as exc:
        logger.error("External API invalid JSON url=%s", url)
        raise ExternalServiceError(f"Invalid JSON from external service: {url}") from exc
