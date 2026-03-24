class RateLimiter:
    def __init__(self):
        limiterFactory = LimiterFactory(configs)
        self.limiters:Dict[str, Limiter] = {}
        
        for config in configs:
            endpoint = config.get("endpoint", 0)
            if endpoint:
                self.limiters[endpoint] = limiterFactory.create(config)
        self._default_limiter = factory.create(default_config)
            
    def allow(self, client_id:str,endpoint:str): # !!! 用client_id而不是key 因为key可能为空
        limiter = self.limiters.get(endpoint, self._default_limiter)
        return limiter.allow(client_id)
    