from __future__ import annotations

import time
from threading import Lock
from typing import Optional

from fastapi import HTTPException, Request

# In-memory sliding window limiter.
# Note: this is per-process. With multiple Cloud Run instances,
# limits may be imperfect unless you later move to a shared store (e.g., Redis).
_bucket: dict[str, list[float]] = {}
_lock = Lock()


def _get_client_ip(request: Request) -> str:
    # Cloud Run / proxies often set X-Forwarded-For.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # XFF can contain multiple IPs: "client, proxy1, proxy2"
        return xff.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def enforce_rate_limit(
    *,
    request: Request,
    key_suffix: Optional[str],
    limit: int,
    window_seconds: int,
) -> None:
    """
    Enforce a rate limit using a sliding time window.

    If the limit is exceeded, raises HTTP 429 with:
      - JSON detail
      - Retry-After header
    """
    ip = _get_client_ip(request)
    suffix = key_suffix or "anon"
    key = f"{ip}:{suffix}"

    now = time.time()
    cutoff = now - window_seconds

    with _lock:
        times = _bucket.get(key, [])
        # Keep only requests inside the window
        times = [t for t in times if t >= cutoff]

        if len(times) >= limit:
            # Compute when the next request becomes allowed
            oldest = times[0]
            retry_after = int(window_seconds - (now - oldest)) + 1
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        times.append(now)
        _bucket[key] = times