"""Small in-memory sliding-window rate limiter helpers."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable

_Clock = Callable[[], float]

_attempts: dict[str, deque[float]] = defaultdict(deque)


def is_rate_limited(
    key: str,
    *,
    limit: int,
    window_seconds: int,
    clock: _Clock = time.monotonic,
) -> tuple[bool, int]:
    """Return whether a key has exceeded its request budget.

    The current attempt is counted when the key is still under the limit.
    When the key is already limited, the returned retry value is the number
    of whole seconds until the oldest attempt leaves the window.
    """
    now = clock()
    cutoff = now - window_seconds
    attempts = _attempts[key]

    while attempts and attempts[0] <= cutoff:
        attempts.popleft()

    if len(attempts) >= limit:
        retry_after = max(1, int(attempts[0] + window_seconds - now))
        return True, retry_after

    attempts.append(now)
    return False, 0


def reset_rate_limits() -> None:
    """Clear rate-limit state, primarily for tests."""
    _attempts.clear()
