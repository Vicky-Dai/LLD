📦 What is Amazon Locker?
Amazon Locker is a self-service package pickup system. A delivery driver deposits a package into an available compartment, the system generates an access token, and the customer uses that code to retrieve their package.

You walk into the interview and get greeted with this prompt:
"Design a locker system like Amazon Locker where delivery drivers can deposit packages and customers can pick them up using a code."


Requirements: # 整个系统 从里到外，从上到下 每个部分 从里到外
1. Carrier deposits a package by specifying size (small, medium, large)
   - System assigns an available compartment of matching size
   - Opens compartment and returns access token, or error if no space
2. Upon successful deposit, an access token is generated and returned
   - One access token per package
3. User retrieves package by entering access token
   - System validates code and opens compartment
   - Throws specific error if code is invalid or expired
4. Access tokens expire after 7 days # !!!!!
   - Expired codes are rejected if used for pickup
   - Package remains in compartment until staff removes it
5. Staff can open all expired compartments to manually handle packages # !!!!
   - System opens all compartments with expired tokens
   - Staff physically removes packages and returns them to sender
6. Invalid access tokens are rejected with clear error messages 
   - Wrong code, already used, or expired - user gets specific feedback #!!!!

Out of scope:
- How the package gets to the locker (delivery logistics)
- How the access token reaches the customer (SMS/email notification)
- Lockout after failed access token attempts
- UI/rendering layer
- Multiple locker stations
- Payment or pricing

locker system
- lockers: Locker[]
- accessTokenMapping: Map<string, AccessToken>
+ putPackage() -> accesstoken
+ getPackage(accesstoken)
+ openExpiredLocker() -> void #！！！

accesstoken
- code
- expiration:timestamp #!!! 直接存这个方便
- locker
+ AccessToken(code, expiration, locker)
+ isExpired() -> boolean
+ getLocker() -> Locker
+ getCode() -> string

Locker:
- size: Size
- occupied: boolean
+ Locker(size)
+ getSize() -> Size
+ isOccupied() -> boolean
+ markOccupied() -> void
+ markFree() -> void
+ open() -> void


Locker
 ├── compartments: [Compartment A, B, C]
 └── accessTokenMapping:
        "ABC123" → AccessToken
                      └── compartment → B

enum Size:
    SMALL
    MEDIUM
    LARGE