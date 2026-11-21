"""WP-P3-H2: FAA ArcGIS Quota Mitigation & Source Caching.

Provides caching, exponential backoff with jitter, and optional-airspace fallback
to protect pipeline runs against external FAA ArcGIS REST rate limits and quotas.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

DEFAULT_CACHE_DIR = Path(".cache/arcgis")
DEFAULT_CACHE_TTL_SECONDS = 86400.0  # 24 hours (airspace data is on 28-day AIRAC cycle)
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 15.0


def is_arcgis_quota_or_rate_error(status_code: int | None, payload: Any | None = None) -> bool:
    """Return True if the HTTP status or JSON body signals an ArcGIS rate limit or quota block."""
    if status_code in (429, 503):
        return True
    if isinstance(payload, Mapping) and "error" in payload:
        err = payload["error"]
        if isinstance(err, Mapping):
            code = err.get("code")
            message = str(err.get("message") or "").lower()
            details = str(err.get("details") or "").lower()
            if code in (429, 503):
                return True
            for kw in ("rate limit", "quota", "too many requests", "busy", "exceeded"):
                if kw in message or kw in details:
                    return True
        elif isinstance(err, (str, int)):
            err_str = str(err).lower()
            for kw in ("rate limit", "quota", "too many requests", "busy", "429"):
                if kw in err_str:
                    return True
    return False


@dataclass
class BackoffBudget:
    """Calculates bounded exponential backoff delays with random jitter."""

    max_retries: int = DEFAULT_MAX_RETRIES
    base_delay_seconds: float = DEFAULT_BASE_DELAY
    max_delay_seconds: float = DEFAULT_MAX_DELAY
    jitter: bool = True

    def calculate_delay(self, attempt: int) -> float:
        """Compute delay for attempt (1-based index)."""
        if attempt < 1:
            return 0.0
        exp_delay = self.base_delay_seconds * (2.0 ** (attempt - 1))
        bounded = min(exp_delay, self.max_delay_seconds)
        if self.jitter:
            return bounded * (0.5 + random.random() * 0.5)
        return bounded


class ArcGisCache:
    """File-backed JSON cache for static FAA airspace FeatureServer responses."""

    def __init__(self, cache_dir: Path | str | None = None) -> None:
        if cache_dir is not None:
            self.root = Path(cache_dir)
        else:
            env_dir = os.environ.get("AEROGRID_CACHE_DIR")
            self.root = Path(env_dir) if env_dir else DEFAULT_CACHE_DIR

    def _cache_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)[:40]
        return self.root / f"{safe_name}_{hashed}.json"

    def get(self, key: str, max_age_seconds: float | None = DEFAULT_CACHE_TTL_SECONDS) -> dict[str, Any] | None:
        path = self._cache_path(key)
        if not path.is_file():
            return None
        try:
            stat = path.stat()
            if max_age_seconds is not None:
                age = time.time() - stat.st_mtime
                if age > max_age_seconds:
                    return None
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def get_stale(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached payload regardless of TTL for emergency fallback."""
        return self.get(key, max_age_seconds=None)

    def set(self, key: str, payload: Mapping[str, Any]) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._cache_path(key)
        temp_path = path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(dict(payload), f, ensure_ascii=False)
        temp_path.replace(path)
        return path

    def clear(self, key: str | None = None) -> int:
        if not self.root.is_dir():
            return 0
        removed = 0
        if key is not None:
            path = self._cache_path(key)
            if path.is_file():
                path.unlink()
                removed = 1
        else:
            for p in self.root.glob("*.json"):
                try:
                    p.unlink()
                    removed += 1
                except OSError:
                    pass
        return removed


@dataclass(frozen=True)
class QuotaMitigationPolicy:
    """Configurable policy for FAA ArcGIS fetch calls."""

    use_cache: bool = True
    cache_ttl_seconds: float = DEFAULT_CACHE_TTL_SECONDS
    allow_stale_fallback: bool = True
    optional_airspace: bool = False
    backoff: BackoffBudget = BackoffBudget()
