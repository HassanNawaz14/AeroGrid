"""WP-11 ingestion configuration: approved sources, sites, and limitations.

Only values already documented in Phase 2 sources belong here. Anything that
would add a source, change a site, or change a licence is a human decision.
"""
from __future__ import annotations

ARC_GIS_ROOT = (
    "https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services"
)
AIRSPACE_SERVICES = (
    ("Class_Airspace", "Class_Airspace", "CLASS"),
    ("Special_Use_Airspace", "Special_Use_Airspace", "SPECIAL_USE"),
    ("Route_Airspace", "Route_Airspace", "ROUTE"),
)

# Receiver/home coordinates documented in the WP-03 source validations.
# KAGC has no documented anchor, so it is not used for spatial filtering.
SITE_ANCHORS: dict[str, tuple[float, float]] = {
    "KBTP": (40.777888, -79.949864),
    "NIGHTJAR_PA": (41.5347, -75.5953),
    "DJI_CO": (39.62655794, -105.0007319),
    "DJI_CA": (33.7332532, -118.3346817),
    "DJI_SF": (37.62066361, -122.49619),
}
# Documented METAR station fallbacks (docs/03). Stations absent here map to -1.
STATION_SITE_CODES: dict[str, str] = {
    "KBTP": "KBTP",
    "KAGC": "KAGC",
    "KAVP": "NIGHTJAR_PA",
    "KMPO": "NIGHTJAR_PA",
    "KBKF": "DJI_CO",
    "KDEN": "DJI_CO",
    "KLGB": "DJI_CA",
    "KLAX": "DJI_CA",
    "KSQL": "DJI_SF",
}

IEM_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
AWC_URL = "https://aviationweather.gov/api/data/metar"

NIGHTJAR_URL = (
    "https://huggingface.co/datasets/joshruby/nightjar-flight-20260804/"
    "resolve/main/dji/FlightRecord_2026-08-04_%5B12-46-25%5D.csv"
)
DJI_FILES: tuple[tuple[str, str, str | None], ...] = (
    (
        "colorado-drone-data/FlightRecord_2024-08-02.csv",
        "colorado",
        "DJI_CO",
    ),
    (
        "Palos Verdes/DJIFlightRecord_2025-02-17_[17-46-47].csv",
        "palos_verdes",
        None,
    ),
    ("drone_ocean/FlightRecord_2024-06-29.csv", "offshore_sf", None),
)
DJI_ROOT = (
    "https://huggingface.co/datasets/nominal-io/dji-drone-telemetry/resolve/main"
)

SOURCE_LICENSES = {
    "IEM": (
        "Public domain (Iowa Environmental Mesonet); NWS ASOS/AWOS observations",
        "Iowa Environmental Mesonet, Iowa State University",
    ),
    "AWC": (
        "U.S. government open data (NOAA/NWS)",
        "NOAA/NWS Aviation Weather Center",
    ),
    "Nightjar": (
        "CC BY 4.0",
        "Nightjar flight telemetry dataset (joshruby), Hugging Face",
    ),
    "Nominal-DJI": (
        "MIT (dataset card)",
        "nominal-io dji-drone-telemetry, Hugging Face",
    ),
    "FAA-Airspace": (
        "U.S. government open data",
        "FAA UAS Data Delivery System ArcGIS services",
    ),
}

STUDY_BOX_HALF_WIDTH_DEG = 0.25
DEFAULT_STATIONS = ("KBTP", "KAGC")
DEFAULT_SOURCES = ("weather", "uas", "airspace")
KNOWN_SOURCES = frozenset({"weather", "uas", "airspace", "tartan"})

# Stable limitation IDs from docs/13; the run summary must list every one.
LIMITATIONS: tuple[tuple[str, str, str], ...] = (
    ("L-001", "No weather linkage on tracking facts", "DQ-C-003"),
    ("L-002", "Ground state unobserved", "DQ-C-008"),
    ("L-003", "Occupancy is 2D with a 60-second cap", "DQ-U-003"),
    ("L-004", "Encounter predicate requires identical timestamps", "DQ-U-004"),
    ("L-005", "No historical restriction snapshot", "DQ-T-003"),
    ("L-006", "Reject ledger spans multiple ETL runs", "DQ-R-001"),
    ("L-007", "Corridor views are screening metrics only", "WP-10"),
    ("L-008", "UAS sources are validated but never ingested", "DQ-G-003"),
    ("L-009", "Airspace zones are never staged; OpenSky is unused", "DQ-G-004"),
    ("L-010", "Fetched raw files are not archived to object storage", "NONE"),
)

DEFAULT_WINDOW_DAYS = 7


def site_bbox(lat: float, lon: float, half_width: float = STUDY_BOX_HALF_WIDTH_DEG):
    """Return (min_lon, min_lat, max_lon, max_lat) in WGS 84."""
    return (lon - half_width, lat - half_width, lon + half_width, lat + half_width)


def study_boxes() -> list[tuple[str, tuple[float, float, float, float]]]:
    return [(code, site_bbox(*anchor)) for code, anchor in SITE_ANCHORS.items()]
