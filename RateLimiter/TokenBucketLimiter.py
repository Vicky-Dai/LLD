import time # !!! 用time而不是datetime 因为datetime是python内置类型
from typing import Dict # !!! 用Dict而不是dict 因为dict是python内置类型
class TokenBucketLimiter(Limiter):
    # request come in
    # check if we have this user's bucket, get the bucket else create one
    # check the remaining token and add new tokens, min(capacity, remain+new)
    # if tokens > 0, allow request, tokens -= 1
    # else return False
    def __init__(self, capacity, rate):
        self.capacity = capacity
        self.refill_rate_per_second = rate
        self.buckets:Dict[str, tuple[float, float]] = {}
        
    def allow(self, clientID):
        last_time, current_tokens = self._get_or_create_bucket(clientID)
        now = time.time()
        time_elapsed = now - last_time
        tokens_to_add = time_elapsed*self.refill_rate_per_second
        current_tokens = min(self.capacity, current_tokens + tokens_to_add)
        if current_tokens > 0:
            self.buckets[clientID] = (now, current_tokens - 1)
            return # result 等会儿补上
        else:
            return 


    def _get_or_create_bucket(self, key: str):
        if key not in self.buckets:
            self.buckets[key] = (time.time(), self.capacity)
        return self.buckets[key]