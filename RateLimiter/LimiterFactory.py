class LimiterFactory:
    def create(self, config: Config):
        algorithm = config.get("algorithm") # !!!! 用get而不是[] 因为config可能为空
        algoconfig = config.get("algoconfig", {})
        
        if algorithm == "TokenBucket":
            return TokenBucketLimiter(
                algoconfig.get("capacity", 0), 
                algoconfig.get("refill_rate", 0)
            )
        
        if algorithm == "WindowLog":
            return WindowLogLimiter(
                algoconfig.get("window",0), 
                algoconfig.get("max_requests", 0)
            )

        raise ValueError(f"Invalid algorithm: {algorithm}") #！！！！