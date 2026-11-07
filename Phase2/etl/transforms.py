from __future__ import annotations

from typing import Any


def c_to_f(value: float | None) -> float | None:
    if value is None:
        return None
    return (float(value) * 9.0 / 5.0) + 32.0


def f_to_c(value: float | None) -> float | None:
    if value is None:
        return None
    return (float(value) - 32.0) * 5.0 / 9.0


def hpa_to_inhg(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value) * 0.0295299830714


def mps_to_kts(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value) * 1.9438444924406


def mph_to_kts(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value) * 0.86897624190065


def parse_visibility_sm(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text.upper() == "M":
        return None
    if text.endswith("+"):
        text = text[:-1].strip()
    try:
        return float(text)
    except ValueError:
        return None


def derive_ceiling_ft(layers: list[dict[str, Any]] | None) -> int | None:
    if not layers:
        return None
    candidates = [
        layer.get("base")
        for layer in layers
        if str(layer.get("cover", "")).upper() in {"BKN", "OVC", "VV"}
        and layer.get("base") is not None
    ]
    if not candidates:
        return None
    return int(min(candidates))


def derive_flight_category(
    visibility_sm: float | None, ceiling_ft: int | None
) -> str | None:
    if visibility_sm is None:
        return None
    vis = float(visibility_sm)
    ceiling = None if ceiling_ft is None else int(ceiling_ft)

    if vis < 1.0 or (ceiling is not None and ceiling < 500):
        return "LIFR"
    if vis < 3.0 or (ceiling is not None and ceiling < 1000):
        return "IFR"
    if vis <= 5.0 or (ceiling is not None and ceiling <= 3000):
        return "MVFR"
    return "VFR"
