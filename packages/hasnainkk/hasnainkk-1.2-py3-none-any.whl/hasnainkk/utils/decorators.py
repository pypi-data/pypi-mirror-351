from functools import wraps
from typing import Callable, Any

def ignore_flood_wait(func: Callable) -> Callable:
    """Decorator to ignore flood wait errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                print(f"Ignoring flood wait: {e}")
                return None
            raise
    return wrapper
