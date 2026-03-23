import time
from typing import Dict #!!! typing
from collections import deque
class SlidingWindowLogLimiter:
    # user request come in, get the current time
    # clear the request log out of window
    # check the number of remaining request log and use max to minus it
    # if > 0, allow the request, add new log
    # else, reject, return reject 
    def __init__(self, maxRequest:int, window_ms: int):
        self.maxRequest = maxRequest
        self.window_ms = window_ms
        self.logs:Dict[str:WindowLog] = {}
    
    def allow(self, key:str):
        now_ms = int(time.time()*1000) #
        q = self.get_or_create_log(key)
        last_time = now_ms - self.window_ms
        while q:
            if q[0] < last_time:
                q.popleft()
            else:
                break
        available = self.maxRequest - len(q)
        if available >0:
            q.append(now_ms)
            available -= 1
            return LimiterResult # True
        else:
            return LimiterResult # False
        
    def get_or_create_log(self, key):
        if key not in self.logs:
            self.logs[key] = WindowLog(deque())
            return self.logs[key]
        return self.logs[key]
        

class WindowLog:
    def __init__(self, q):
        self.logQ = q
           