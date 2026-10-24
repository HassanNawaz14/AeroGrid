# AeroGrid: Data Warehouse Dimensional Schema Architecture

## 1. Schema Architecture Overview
The AeroGrid Data Warehouse implements a **Star Schema** design centered around five core business process fact tables surrounded by robust, standardized dimension tables. This architecture optimizes analytical query performance, reduces join complexity, and enables rapid OLAP aggregation across spatial, temporal, and vehicle dimensions.

---

## 2. Fact-to-Dimension Relationship Mapping

| Fact Table | Primary Dimensions (Star Links) | Supporting / Snowflake Dimensions |
|---|---|---|
| **FactVehicleTracking** | `DimTime`, `DimVehicle`, `DimSpatialGrid` | `DimWeather` (linked via Time & Spatial Grid) |
| **FactFlightJourney** | `DimTime`, `DimVehicle` | `DimSpatialGrid` (Origin/Destination grids) |
| **FactCloseEncounter** | `DimTime`, `DimVehicle` (Vehicle 1 & 2), `DimSpatialGrid` | `DimWeather` |
| **FactRestrictionActivation**| `DimTime`, `DimAirspaceZone` | `DimSpatialGrid` |
| **FactAirspaceOccupancy** | `DimTime`, `DimSpatialGrid` | `DimVehicle` (aggregated by category) |

---

## 3. Dimensional Relationships & Star Topology

### Star Core: `DimTime`
* Connected to **all five fact tables** via `time_key`.
* Supports drill-down paths: `Year` $\rightarrow$ `Quarter` $\rightarrow$ `Month` $\rightarrow$ `Date` $\rightarrow$ `Hour`.

### Spatial Star: `DimSpatialGrid` & `DimAirspaceZone`
* **`DimSpatialGrid`** connects position tracking, close encounters, and occupancy snapshots.
* **`DimAirspaceZone`** connects restriction activations, enabling spatial compliance auditing.

### Actor Star: `DimVehicle`
* Connects tracking, journeys, and close encounters.
* Supports role-playing dimensions in `FactCloseEncounter` (`vehicle_key_1` and `vehicle_key_2` for multi-vehicle conflict analysis).
