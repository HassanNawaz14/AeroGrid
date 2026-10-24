# AeroGrid: AeroGrid Low-Altitude Airspace Intelligence Warehouse

## Project Overview
**AeroGrid** is an advanced data warehousing and intelligence system designed for low-altitude airspace management, Unmanned Aircraft System (UAS) traffic management (UTM), and mixed-traffic operations (drones, manned aircraft, and emerging eVTOL/thruster vehicles).

---

## Repository Structure
```text
AeroGrid/
├── Phase1/
│   ├── DWBI Lab Phase 1.pdf                # Lab guidelines
│   ├── Project_Proposal.tex / .pdf          # Deliverable 1: Project Proposal
│   ├── Business_Requirements_Document.tex / .pdf # Deliverable 2: BRD
│   └── Business_Questions.tex / .pdf        # Deliverable 3: 10 Business Questions
├── data/
│   └── all_data_summary.md                  # Comprehensive data source & ingestion guide
├── docs/
│   └── LowAltitude_Airspace_Intelligence_Warehouse_Phase1_Guide.md # Core project guide
└── README.md                                # Project monitoring & documentation
```

---

## Phase 1 Status & Deliverables
| Deliverable | Status | File Location |
|---|---|---|
| **Project Proposal** | Completed | `Phase1/Project_Proposal.pdf` |
| **Business Requirements Document (BRD)** | Completed | `Phase1/Business_Requirements_Document.pdf` |
| **10 Business Questions** | Completed | `Phase1/Business_Questions.pdf` |
| **Fact & Dimension Identification** | Pending | Next in Phase 1 |
| **Grain Definition Document** | Pending | Next in Phase 1 |
| **Star/Snowflake Schema Diagram** | Pending | Next in Phase 1 |
| **Data Dictionary** | Pending | Next in Phase 1 |

---

## Automated Data Warehouse Pipeline & CI/CD
AeroGrid is engineered as a fully automated data pipeline:
- **Live Ingestion via GitHub Actions:** Automated cron workflows poll live APIs (OpenSky Network state vectors and NOAA Weather observations) to feed staging tables without manual intervention.
- **Incremental Schedules:**
  - **OpenSky Live State Vectors:** Polled every **5 minutes**.
  - **Aviation Weather (METAR):** Polled **hourly**.
  - **FAA Airspace Restrictions (UDDS):** Checked **weekly**.
  - **TartanAviation & Telemetry Logs:** Bulk batch loaded initially with scheduled updates.
- **Pipeline Architecture:** Bronze (Staging) $\rightarrow$ Silver (Cleaned/Integrated) $\rightarrow$ Gold (Dimensional Star Schema Warehouse).
