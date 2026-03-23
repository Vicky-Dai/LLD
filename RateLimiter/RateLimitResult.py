from dataclasses import dataclass # 有了这个之后就省的写self. __init__ 这些了
from typing import Optional


@dataclass(frozen=True) # frozen=True 表示这个类是不可变的
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_ms: Optional[int]

    def is_allowed(self) -> bool:
        return self.allowed

    def get_remaining(self) -> int:
        return self.remaining

    def get_retry_after_ms(self) -> Optional[int]:
        return self.retry_after_ms
