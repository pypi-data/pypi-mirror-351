from typing import Any

def async_retry(max_attempts: int = 3, delay: float = 1.0):
    """Simple retry decorator without flood wait handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts:
                        print(f"Attempt {attempt} failed, retrying...")
            raise last_error
        return wrapper
    return decorator
