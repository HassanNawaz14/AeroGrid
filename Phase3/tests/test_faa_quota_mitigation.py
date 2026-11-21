"""Unit tests for WP-P3-H2: FAA ArcGIS Quota Mitigation & Caching.

Authored by: Member B (HarveyWebbs / Abdullah Zia)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PHASE2_ROOT = Path(__file__).resolve().parents[2] / "Phase2"
if str(PHASE2_ROOT) not in sys.path:
    sys.path.insert(0, str(PHASE2_ROOT))

from etl.quota_mitigation import (
    ArcGisCache,
    BackoffBudget,
    QuotaMitigationPolicy,
    is_arcgis_quota_or_rate_error,
)
from etl.fetch import fetch_airspace_layer


def test_is_arcgis_quota_or_rate_error():
    assert is_arcgis_quota_or_rate_error(429) is True
    assert is_arcgis_quota_or_rate_error(503) is True
    assert is_arcgis_quota_or_rate_error(200) is False
    assert is_arcgis_quota_or_rate_error(None, {"error": {"code": 429, "message": "Too many requests"}}) is True
    assert is_arcgis_quota_or_rate_error(None, {"error": {"message": "Service rate limit exceeded"}}) is True
    assert is_arcgis_quota_or_rate_error(None, {"error": "Server busy, quota exhausted"}) is True
    assert is_arcgis_quota_or_rate_error(200, {"type": "FeatureCollection", "features": []}) is False


def test_backoff_budget_delay_calculation():
    budget = BackoffBudget(max_retries=4, base_delay_seconds=1.0, max_delay_seconds=10.0, jitter=False)
    assert budget.calculate_delay(0) == 0.0
    assert budget.calculate_delay(1) == 1.0
    assert budget.calculate_delay(2) == 2.0
    assert budget.calculate_delay(3) == 4.0
    assert budget.calculate_delay(4) == 8.0
    assert budget.calculate_delay(5) == 10.0  # capped at max_delay_seconds

    jitter_budget = BackoffBudget(base_delay_seconds=2.0, max_delay_seconds=10.0, jitter=True)
    d = jitter_budget.calculate_delay(2)
    assert 2.0 <= d <= 4.0


def test_arcgis_cache_read_write_ttl(tmp_path: Path):
    cache = ArcGisCache(cache_dir=tmp_path)
    sample = {"type": "FeatureCollection", "features": [{"id": 1, "properties": {"GLOBAL_ID": "ABC"}}]}

    assert cache.get("test_key") is None
    cache.set("test_key", sample)

    # Read back immediately
    loaded = cache.get("test_key", max_age_seconds=60)
    assert loaded == sample

    # Stale fallback when TTL is 0
    time.sleep(0.01)
    assert cache.get("test_key", max_age_seconds=0.001) is None
    assert cache.get_stale("test_key") == sample

    # Clear cache
    assert cache.clear("test_key") == 1
    assert cache.get_stale("test_key") is None


def test_fetch_airspace_layer_uses_cache_when_available(tmp_path: Path, monkeypatch):
    cache = ArcGisCache(cache_dir=tmp_path)
    bbox = (-80.0, 40.0, -79.0, 41.0)
    cached_features = [{"type": "Feature", "properties": {"GLOBAL_ID": "CACHED_1"}}]
    cache_key = f"Class_Airspace_{bbox[0]:.4f}_{bbox[1]:.4f}_{bbox[2]:.4f}_{bbox[3]:.4f}"
    cache.set(cache_key, {"type": "FeatureCollection", "features": cached_features})

    http_mock = MagicMock(side_effect=AssertionError("Network should not be called on cache hit!"))
    import etl.fetch as fetch_module
    monkeypatch.setattr(fetch_module, "_http_json", http_mock)

    policy = QuotaMitigationPolicy(use_cache=True, cache_ttl_seconds=3600)
    results = fetch_airspace_layer("Class_Airspace", bbox, cache=cache, policy=policy)
    assert results == cached_features
    assert http_mock.call_count == 0


def test_fetch_airspace_layer_stale_fallback_on_network_failure(tmp_path: Path, monkeypatch):
    cache = ArcGisCache(cache_dir=tmp_path)
    bbox = (-80.0, 40.0, -79.0, 41.0)
    stale_features = [{"type": "Feature", "properties": {"GLOBAL_ID": "STALE_1"}}]
    cache_key = f"Class_Airspace_{bbox[0]:.4f}_{bbox[1]:.4f}_{bbox[2]:.4f}_{bbox[3]:.4f}"
    cache.set(cache_key, {"type": "FeatureCollection", "features": stale_features})

    import etl.fetch as fetch_module
    monkeypatch.setattr(fetch_module, "_http_json", MagicMock(side_effect=RuntimeError("ArcGIS rate limit 429")))

    # With TTL = 0 (stale), it falls back to stale cache on network failure
    policy = QuotaMitigationPolicy(use_cache=True, cache_ttl_seconds=0.0001, allow_stale_fallback=True)
    time.sleep(0.01)
    results = fetch_airspace_layer("Class_Airspace", bbox, cache=cache, policy=policy)
    assert results == stale_features


def test_fetch_airspace_layer_optional_mode_graceful_degradation(monkeypatch):
    bbox = (-80.0, 40.0, -79.0, 41.0)
    import etl.fetch as fetch_module
    monkeypatch.setattr(fetch_module, "_http_json", MagicMock(side_effect=RuntimeError("503 Service Unavailable")))

    # In optional mode, returns []
    opt_policy = QuotaMitigationPolicy(use_cache=False, optional_airspace=True)
    res = fetch_airspace_layer("Route_Airspace", bbox, policy=opt_policy)
    assert res == []

    # In strict mode (optional_airspace=False), raises RuntimeError
    strict_policy = QuotaMitigationPolicy(use_cache=False, optional_airspace=False)
    with pytest.raises(RuntimeError):
        fetch_airspace_layer("Route_Airspace", bbox, policy=strict_policy)
