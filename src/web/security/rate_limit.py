"""Minimal in-memory fixed-window rate limiter for the login endpoint.

Deliberately simple — single-process, in-memory, no Redis. Good enough to
blunt naive credential-stuffing scripts; not a substitute for a real WAF.
"""
from __future__ import annotations

import threading
import time

_WINDOW_SECONDS = 60
_MAX_ATTEMPTS = 10

_attempts: dict[str, list[float]] = {}
_lock = threading.Lock()


def is_rate_limited(key: str) -> bool:
    now = time.time()
    with _lock:
        timestamps = [t for t in _attempts.get(key, []) if now - t < _WINDOW_SECONDS]
        _attempts[key] = timestamps
        return len(timestamps) >= _MAX_ATTEMPTS


def record_attempt(key: str) -> None:
    with _lock:
        _attempts.setdefault(key, []).append(time.time())


def reset(key: str) -> None:
    with _lock:
        _attempts.pop(key, None)
