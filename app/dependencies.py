from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException, status

# Very simple IP rate‑limiter for /login
WINDOW = timedelta(minutes=1)
MAX_ATTEMPTS = 5
_buckets: dict[str, list[datetime]] = defaultdict(list)


def rate_limit_login(request: Request):
    ip = request.client.host
    now = datetime.now(timezone.utc)
    _buckets[ip] = [t for t in _buckets[ip] if now - t < WINDOW]

    if len(_buckets[ip]) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
        )
    _buckets[ip].append(now)
