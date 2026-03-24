from datetime import datetime # !!!!

class AccessToken:
    def __init__(self, code:str, expiration:datetime, locker:Locker):
        self.code = code
        self.expiration = expiration
        self.locker = locker
        
    def isExpired(self):
        now = datetime.now()
        if now >= self.expiration: #!!! 等于也要考虑
            return True
        return False
    
    def getLocker(self):
        return self.locker
    
    def getCode(self):
        return self.code