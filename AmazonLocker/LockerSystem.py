# locker system
# - lockers: Locker[]
# - accessTokenMapping: Map<string, AccessToken>
# + putPackage() -> accesstoken
# + getPackage(accesstoken)
# + openExpiredLocker() -> void #！！！
import uuid
from datetime import datetime, timedelta #!!!!
from typing import Dict, Optional
import random

class LockerSystem:
    def __init__(self, lockers: list["Locker"]): #!!!!
        self.lockers = lockers
        self.accessTokenMapping: Dict[str, "AccessToken"] = {}
    
    def depositPackage(self, size) -> "AccessToken":
        # find empty, compatible (size) locker
        # open locker, put pakage in: create a token, create an aacesstoken instance, mapping together
        # mark locker occupied
        # return code
        target_locker = self.get_available_locker(size)
        if not target_locker:
            raise Exception(f"No available compartment of size {size}") #!!! ValueError 是在参数错误的时候抛出的，这里不是参数错误，所以用Exception
        target_locker.open()
        access_token = self.generateAccessToken(target_locker)
        self.accessTokenMapping[access_token.code] = access_token
        target_locker.markOccupied()
        return access_token.get_code()

    def getPackage(self, tokenCode):
        # use tokenCode to find the locker
        # if expire, not exist, raise error
        # else: open locker
        # mark locker free
        # remove accesstokenmapping
        if tokenCode not in self.accessTokenMapping:
            raise ValueError(f"code does not exist")
        access_token = self.tokenCodeMappping[tokenCode]
        if access_token.isExpired():
            raise Exception("Access token has expired")
        locker = access_token.get_locker()
        locker.open()
        self._clear_deposit(access_token)

    def get_available_locker(self, size: "Size") -> Optional["Locker"]: # !!! extract this to a helper function
        for l in self.lockers:
            if l.size == size and not l.isOccupied():
                return l
        return None
    
    def generateAccessToken(self, locker: "Locker") -> "AccessToken": #!!!!
        code = f"{random.randint(0, 999999):06d}" # !!! 6位随机数
        expiration = datetime.now() + timedelta(days=7) #!!!! 加7天
        return AccessToken(code, expiration, locker)

    def _clear_deposit(self, access_token: "AccessToken"):
        locker = access_token.get_locker()
        locker.markFree()
        self.accessTokenMapping.pop(access_token.get_code(), None) # !!! dict删除是pop

    
    def openExpiredLocker(self):
        for access_token in self.accessTokenMapping.values():
            if access_token.isExpired():
                locker = access_token.get_locker()
                locker.open()