"""
Rate limiting utilities for conditional application of rate limits.
"""
from functools import wraps
from typing import Callable, Any

from ..config import settings

# Initialize limiter based on production mode
limiter = None
if settings.production:
    try:
        from slowapi import Limiter
        from slowapi.util import get_remote_address
        limiter = Limiter(key_func=get_remote_address)
    except ImportError:
        pass


def apply_rate_limit(rate_limit_str: str) -> Callable:
    """
    Apply rate limiting conditionally based on production mode.
    
    This decorator allows us to cleanly apply rate limiting when in production mode
    and skip it entirely when in development mode, without invalid Python syntax.
    
    Args:
        rate_limit_str: Rate limit string (e.g., "10/minute", "30/second")
        
    Returns:
        Decorator function that applies rate limiting if limiter is available
    """
    def decorator(func: Callable) -> Callable:
        if settings.production and limiter:
            # Apply the rate limit decorator
            return limiter.limit(rate_limit_str)(func)
        else:
            # Return the function unchanged
            return func
    return decorator
