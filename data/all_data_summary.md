# AeroGrid: Comprehensive Data Sources & Ingestion Strategy

## 1. Overview & Data Architecture Principles
The AeroGrid is built on industrial data warehousing principles, treating low-altitude airspace intelligence as a multi-source ecosystem combining real-time surveillance, historical bulk records, spatial boundaries, and meteorological observations. 

To achieve a true automated data warehouse pipeline:
- **Raw Staging (Bronze Layer):** Ingests raw API responses and bulk downloads with zero transformation.
- **Cleaned & Integrated Layer (Silver Layer):** Standardizes formats, parses coordinates, filters anomalies, and deduplicates records.
- **Dimensional Warehouse (Gold Layer):** Implements star/snowflake schemas with surrogate keys, grain-compliant fact tables, and robust dimension hierarchies.
- **Automation & CI/CD:** Live data feeds and incremental updates are fully automated using GitHub Actions scheduled workflows, Python ingestion scripts, and cloud/local database loaders.

---

## 2. Detailed Data Sources, Acquisition & Formats

### Source 1: OpenSky Network
* **Domain:** Real-time and historical aircraft and drone state vectors.
* **Nature:** Hybrid (Continuous live streaming + historical bulk dumps).
* **Acquisition Method:** 
  * *Live Data:* Automated Python script querying the OpenSky REST API (`https://opensky-network.org/api/states/all`).
  * *Historical Data:* Bulk state vector CSV dumps or Impala database queries.
* **Format:** JSON (Live API), CSV (Historical).
* **Incremental Strategy & Schedule:** Polled every **5 minutes** via GitHub Actions cron trigger to capture continuous vehicle tracking and telemetry.

### Source 2: Federal Aviation Administration (FAA) UAS Data Delivery System (UDDS)
* **Domain:** Airspace restrictions, Temporary Flight Restrictions (TFRs), and automatic approval zones.
* **Nature:** Historical / Spatial Reference (Updated periodically by authorities).
* **Acquisition Method:** Manual download from the FAA Open Data Portal (`https://udds-faa.opendata.arcgis.com/`).
* **Format:** GeoJSON, Shapefile, CSV.
* **Incremental Strategy & Schedule:** Checked/updated **weekly** or upon advisory release via automated scraper / manual verification to update restriction activation dimensions.

### Source 3: TartanAviation Dataset (Carnegie Mellon University)
* **Domain:** High-resolution trajectory records and terminal-area density logs.
* **Nature:** Historical bulk archive (Multi-month research collections).
* **Acquisition Method:** Manual download from CMU aviation research repositories.
* **Format:** CSV, TXT trajectory logs.
* **Incremental Strategy & Schedule:** One-time full load during initial warehouse population; static baseline dataset.

### Source 4: Public Aviation Weather Services
* **Domain:** Surface weather observations (METAR), wind speed, visibility, cloud ceiling.
* **Nature:** Hybrid (Live METAR observations + historical weather archives).
* **Acquisition Method:** Automated API polling from the NOAA Aviation Weather Center (`https://aviationweather.gov/api/data/metar`).
* **Format:** JSON, CSV, raw METAR text.
* **Incremental Strategy & Schedule:** Polled **hourly** via GitHub Actions to maintain time-aligned weather dimensions for conflict and operation correlation.

### Source 5: Public Unmanned Aircraft Telemetry & Generated Paths
* **Domain:** Pure drone flight logs and synthetic low-altitude mixed-traffic paths.
* **Nature:** Historical benchmarks & synthetic simulation data.
* **Acquisition Method:** Manual download from open repositories / project simulation scripts.
* **Format:** CSV, JSON.
* **Incremental Strategy & Schedule:** Batch loaded during scenario testing and capacity planning updates.

---

## 3. Automation & GitHub Actions Pipeline Architecture
To make AeroGrid a true automated pipeline:
1. **Scheduled Workflows (`.github/workflows/ingest.yml`):**
   - Cron trigger for OpenSky live state vector polling (every 5 mins).
   - Cron trigger for NOAA Weather observation polling (every hour).
2. **ETL Execution Scripts (`src/etl/`):**
   - Python-based pipeline script that fetches data, validates schemas, writes to staging, and transforms into fact/dimension tables.
3. **Storage & State Management:**
   - Incremental watermark tracking using timestamps or sequence IDs to prevent duplicate loads.
