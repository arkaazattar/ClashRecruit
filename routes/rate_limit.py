"""Flask route helpers for endpoint rate limiting."""

from functools import wraps

from flask import jsonify, request

from ..services.rate_limiter import is_rate_limited


def rate_limit(
    bucket: str,
    *,
    limit: int,
    window_seconds: int,
):
    """Return a decorator that rate limits requests by client IP."""

    def decorate(route_handler):
        @wraps(route_handler)
        def wrapper(*args, **kwargs):
            limiter_key = f"{bucket}:{request.remote_addr or 'unknown'}"
            limited, retry_after = is_rate_limited(
                limiter_key,
                limit=limit,
                window_seconds=window_seconds,
            )
            if limited:
                response = jsonify(
                    {
                        "message": (
                            "Too many requests. Please try again shortly."
                        )
                    }
                )
                response.headers["Retry-After"] = str(retry_after)
                return response, 429

            return route_handler(*args, **kwargs)

        return wrapper

    return decorate
