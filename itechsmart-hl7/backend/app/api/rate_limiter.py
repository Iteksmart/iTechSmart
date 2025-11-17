"""
Rate Limiting
Protect API endpoints from abuse
"""

from fastapi import HTTPException, Request, status
from typing import Dict, Callable
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter
    """

    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.cleanup_task = None

    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request
        """
        # Try to get user from auth
        if hasattr(request.state, "user"):
            return f"user:{request.state.user.username}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"

        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    def _cleanup_old_requests(self):
        """
        Clean up old request records
        """
        now = datetime.now()
        for client_id in list(self.requests.keys()):
            # Remove requests older than 1 hour
            self.requests[client_id] = [
                req_time
                for req_time in self.requests[client_id]
                if now - req_time < timedelta(hours=1)
            ]

            # Remove client if no requests
            if not self.requests[client_id]:
                del self.requests[client_id]

    async def start_cleanup_task(self):
        """
        Start background cleanup task
        """
        while True:
            await asyncio.sleep(300)  # Clean up every 5 minutes
            self._cleanup_old_requests()

    def check_rate_limit(
        self, client_id: str, max_calls: int, time_window: int
    ) -> bool:
        """
        Check if client has exceeded rate limit

        Args:
            client_id: Client identifier
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds

        Returns:
            True if within limit, False if exceeded
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=time_window)

        # Get client's request history
        if client_id not in self.requests:
            self.requests[client_id] = []

        # Filter requests within time window
        recent_requests = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        # Check if limit exceeded
        if len(recent_requests) >= max_calls:
            return False

        # Add current request
        self.requests[client_id] = recent_requests + [now]
        return True

    def get_rate_limit_info(self, client_id: str, time_window: int) -> Dict[str, int]:
        """
        Get rate limit information for client
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=time_window)

        if client_id not in self.requests:
            return {"requests_made": 0, "window_seconds": time_window}

        recent_requests = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        return {"requests_made": len(recent_requests), "window_seconds": time_window}


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_calls: int = 100, time_window: int = 60):
    """
    Rate limiting decorator for API endpoints

    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # Try to get from kwargs
                request = kwargs.get("request")

            if request:
                client_id = rate_limiter._get_client_id(request)

                if not rate_limiter.check_rate_limit(client_id, max_calls, time_window):
                    rate_info = rate_limiter.get_rate_limit_info(client_id, time_window)

                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Maximum {max_calls} requests per {time_window} seconds.",
                        headers={
                            "X-RateLimit-Limit": str(max_calls),
                            "X-RateLimit-Window": str(time_window),
                            "X-RateLimit-Remaining": "0",
                            "Retry-After": str(time_window),
                        },
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class RateLimitMiddleware:
    """
    Rate limiting middleware for FastAPI
    """

    def __init__(self, app, max_calls: int = 1000, time_window: int = 60):
        self.app = app
        self.max_calls = max_calls
        self.time_window = time_window

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request object
        from fastapi import Request

        request = Request(scope, receive)

        client_id = rate_limiter._get_client_id(request)

        if not rate_limiter.check_rate_limit(
            client_id, self.max_calls, self.time_window
        ):
            response = {
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"x-ratelimit-limit", str(self.max_calls).encode()],
                    [b"x-ratelimit-window", str(self.time_window).encode()],
                    [b"retry-after", str(self.time_window).encode()],
                ],
            }
            await send(response)

            body = {
                "type": "http.response.body",
                "body": b'{"detail":"Rate limit exceeded"}',
            }
            await send(body)
            return

        await self.app(scope, receive, send)


def get_rate_limit_status(request: Request, time_window: int = 60) -> Dict[str, int]:
    """
    Get current rate limit status for client
    """
    client_id = rate_limiter._get_client_id(request)
    return rate_limiter.get_rate_limit_info(client_id, time_window)
