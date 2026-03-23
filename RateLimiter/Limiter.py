from abc import ABC, abstractmethod

class Limiter(ABC):
    @abstractmethod
    def allow(self, key: str):
        pass

#!!!!! 练习这个abstractmethod