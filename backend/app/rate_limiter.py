import time
from collections import defaultdict
from fastapi import HTTPException, Request, status

class InMemoryRateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        """
        Sets up rate-limiting thresholds.
        e.g., 5 requests per 10 seconds.
        """
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        # Stores client IPs and their associated list of request timestamps
        self.client_history = defaultdict(list)

    def check_rate_limit(self, request: Request):
        """
        Tracks incoming IP signatures and drops requests exceeding the threshold.
        """
        client_ip = request.client.host if request.client else "unknown-ip"
        current_time = time.time()
        
        # Isolate the timestamps associated with this specific IP address
        timestamps = self.client_history[client_ip]
        
        # Slide the window forward: remove timestamps older than our lookback window boundary
        while timestamps and timestamps[0] < current_time - self.window_seconds:
            timestamps.pop(0)
            
        # Check if the remaining active timestamps breach our allowed maximum limit
        if len(timestamps) >= self.requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too Many Requests. Rate limit exceeded. Please wait {self.window_seconds} seconds."
            )
            
        # Log the current incoming request timestamp vector
        timestamps.append(current_time)

# Instantiate a global rate limiter instance: max 10 platform hits every 60 seconds per IP
limiter = InMemoryRateLimiter(requests_limit=10, window_seconds=60)

def rate_limit_guard(request: Request):
    """Dependency injection helper hook for FastAPI routers."""
    limiter.check_rate_limit(request)