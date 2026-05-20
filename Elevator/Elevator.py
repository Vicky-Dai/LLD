from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    IDLE = 3

class Elevator:
    def __init__(self):
        self.current_floor = 0
        self.direction = Direction.IDLE
        self.requests = set()

    def add_request(self, request):
        if request.get_floor() < 0 or request.get_floor() > 9:
            return False
        if request.get_floor() == self.current_floor:
            return True
        if request in self.requests:
            return False
        self.requests.add(request)
        return True

    def step(self):
        if not self.requests:
            self.direction = Direction.IDLE
            return

        if self.direction == Direction.IDLE:
            # Find nearest request to establish initial direction (deterministic)
            nearest = None
            min_distance = float('inf')
            
            for req in self.requests:
                distance = abs(req.get_floor() - self.current_floor)
                if distance < min_distance or (distance == min_distance and (nearest is None or req.get_floor() < nearest.get_floor())):
                    min_distance = distance
                    nearest = req
            
            self.direction = Direction.UP if nearest.get_floor() > self.current_floor else Direction.DOWN

        pickup_type = RequestType.PICKUP_UP if self.direction == Direction.UP else RequestType.PICKUP_DOWN
        pickup_request = Request(self.current_floor, pickup_type)
        destination_request = Request(self.current_floor, RequestType.DESTINATION)

        if pickup_request in self.requests or destination_request in self.requests:
            self.requests.discard(pickup_request)
            self.requests.discard(destination_request)
            if not self.requests:
                self.direction = Direction.IDLE
            return

        if not self.has_requests_ahead(self.direction):
            self.direction = Direction.DOWN if self.direction == Direction.UP else Direction.UP
            return

        if self.direction == Direction.UP:
            self.current_floor += 1
        elif self.direction == Direction.DOWN:
            self.current_floor -= 1

    def has_requests_ahead(self, dir):
        for request in self.requests:
            if dir == Direction.UP and request.get_floor() > self.current_floor:
                return True
            if dir == Direction.DOWN and request.get_floor() < self.current_floor:
                return True
        return False

    def has_requests_at_or_beyond(self, floor, dir):
        for request in self.requests:
            if dir == Direction.UP and request.get_floor() >= floor:
                if request.get_type() in (RequestType.PICKUP_UP, RequestType.DESTINATION):
                    return True
            if dir == Direction.DOWN and request.get_floor() <= floor:
                if request.get_type() in (RequestType.PICKUP_DOWN, RequestType.DESTINATION):
                    return True
        return False

    def get_current_floor(self):
        return self.current_floor

    def get_direction(self):
        return self.direction

""" step()
step() 不是自己循环的
👉 它是被外部不断调用（tick 驱动）
🧠 什么是 “tick”？
👉 可以理解为：
系统每过一小段时间，就推进一步状态
1. 没有请求

先看是否空队列，没有就直接 idle

2. 如果当前 idle

先决定一个初始方向

3. 先看当前楼层要不要停

因为如果电梯已经在该楼层，就应该先处理停靠，而不是先移动

4. 看当前方向前方还有没有请求

如果没有，说明该换方向了

5. 最后才移动一层

因为前面的判断都做完了，才能确定这一 tick 是否真的要走 """