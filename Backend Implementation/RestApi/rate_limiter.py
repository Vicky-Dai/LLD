import logging
import time
from collections import defaultdict, deque
from threading import Lock

from config import settings
from exceptions import RateLimitError

logger = logging.getLogger(__name__)


class RateLimiter:
    """Fixed-window rate limiter keyed by client identifier."""

    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self._limit = limit
        self._window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self._window_seconds

        with self._lock:
            bucket = self._requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self._limit:
                logger.warning("Rate limit exceeded for key=%s", key)
                raise RateLimitError()

            bucket.append(now)


rate_limiter = RateLimiter(settings.rate_limit_per_minute)
