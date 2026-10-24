# AeroGrid: Data Dictionary & Semantic Model

## 1. Semantic Model Refinement & Loophole Analysis
Upon inspecting the sample data payloads (`OpenSky`, `FAA UDDS`, `TartanAviation`, `NOAA METAR`, and `Drone Telemetry`), several structural loopholes and integration challenges in the initial semantic model were identified and resolved:
1. **Altitude Unit Heterogeneity:** OpenSky and TartanAviation record altitude in feet (MSL), whereas drone telemetry logs record altitude in meters. *Resolution:* All fact table altitude measures are standardized to feet MSL (`altitude_ft`), with conversion applied in the Silver ETL staging layer.
2. **Vehicle Identity & Classification Gap:** Manned aircraft use ICAO24 hex codes and callsigns, while drones use mission IDs and serial numbers. *Resolution:* `DimVehicle` is expanded to encompass unified attributes (`vehicle_id`, `registration_number`, `vehicle_category` [Manned Fixed-Wing, Rotorcraft, UAS Quad, eVTOL], and `operator_id`).
3. **Weather Spatial Association:** Weather observations (METAR) are reported at discrete airport stations (e.g., `KDCA`), whereas traffic occurs across arbitrary map coordinates. *Resolution:* `DimWeather` links to Fact tables via station ID and nearest-hour timestamp alignment, coupled with a spatial grid mapping.
4. **Spatial Grid & Zone Containment:** Position points must be associated with FAA restriction polygons and grid cells. *Resolution:* Added `DimSpatialGrid` and `DimAirspaceZone` with spatial boundary metadata to enable point-in-polygon foreign key resolution during ETL.

---

## 2. Dimension Tables

### 2.1 DimTime
* **Description:** Time dimension supporting drill-down analysis from year down to the hour level for temporal density and peak traffic identification.
* **Analytical Value for BI:** Enables trend analysis across hours of the day, days of the week, months, and seasons.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `time_key` | Integer | Primary Key | Surrogate key (YYYYMMDDHH format) |
| `full_date` | Date | Attribute | Calendar date |
| `year` | Integer | Attribute | Year (e.g., 2026) |
| `quarter` | Integer | Attribute | Quarter (1-4) |
| `month` | Integer | Attribute | Month number (1-12) |
| `month_name` | Varchar | Attribute | Month name (January, etc.) |
| `day_of_week` | Varchar | Attribute | Day of week (Monday, etc.) |
| `hour_of_day` | Integer | Attribute | Hour (0-23) |
| `is_weekend` | Boolean | Attribute | Flag indicating weekend vs weekday |

### 2.2 DimVehicle
* **Description:** Master dimension for all aircraft, drones, and emerging aerial vehicles operating in low-altitude airspace.
* **Analytical Value for BI:** Allows operators to compare safety metrics and traffic volume between manned aircraft, commercial drones, and eVTOL vehicles.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `vehicle_key` | Integer | Primary Key | Surrogate key |
| `vehicle_id` | Varchar | Natural Key | Unique identifier (ICAO24 hex or drone serial number) |
| `callsign` | Varchar | Attribute | Flight callsign or mission designator |
| `registration_number` | Varchar | Attribute | Official aircraft/drone registration code |
| `vehicle_category` | Varchar | Attribute | Category (Manned Commercial, General Aviation, UAS Quad, eVTOL) |
| `operator_name` | Varchar | Attribute | Airline, delivery company, or drone operator name |
| `engine_type` | Varchar | Attribute | Propulsion type (Jet, Piston, Electric Battery, Hydrogen) |

### 2.3 DimAirspaceZone
* **Description:** Spatial dimension representing FAA restricted zones, TFRs, SFRA subzones, and automatic approval corridors.
* **Analytical Value for BI:** Evaluates regulatory compliance and measures how effectively traffic reroutes around active restrictions.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `zone_key` | Integer | Primary Key | Surrogate key |
| `restriction_id` | Varchar | Natural Key | FAA restriction identifier (e.g., TFR-9941) |
| `zone_name` | Varchar | Attribute | Descriptive name of the restriction or zone |
| `restriction_type` | Varchar | Attribute | Type (TFR, SFRA, Prohibited Area, Controlled Airspace) |
| `lower_limit_ft` | Float | Attribute | Lower altitude limit in feet MSL |
| `upper_limit_ft` | Float | Attribute | Upper altitude limit in feet MSL |
| `polygon_wkt` | Text | Attribute | Well-Known Text (WKT) representation of boundary polygon |

### 2.4 DimWeather
* **Description:** Meteorological dimension capturing surface observations and weather conditions near flight paths.
* **Analytical Value for BI:** Correlates adverse weather (wind gusts, low ceiling, reduced visibility) with traffic volume drops and close encounter spikes.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `weather_key` | Integer | Primary Key | Surrogate key |
| `station_icao` | Varchar | Natural Key | Weather station identifier (e.g., KDCA) |
| `observation_timestamp` | Timestamp | Attribute | Time of weather observation |
| `temperature_c` | Float | Attribute | Temperature in Celsius |
| `wind_speed_kts` | Float | Attribute | Wind speed in knots |
| `wind_direction_deg` | Integer | Attribute | Wind direction in degrees |
| `visibility_sm` | Float | Attribute | Visibility in statute miles |
| `cloud_ceiling_ft` | Integer | Attribute | Cloud ceiling height in feet |
| `altimeter_inhg` | Float | Attribute | Barometric pressure in inches of mercury |

### 2.5 DimSpatialGrid
* **Description:** Geographic grid partitioning the low-altitude sky into standardized 3D cells for occupancy and density measurement.
* **Analytical Value for BI:** Pinpoints congested urban corridors and identifies under-used altitude bands for new drone routes.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `grid_key` | Integer | Primary Key | Surrogate key |
| `grid_cell_id` | Varchar | Natural Key | Unique grid cell identifier |
| `latitude_center` | Float | Attribute | Center latitude of grid cell |
| `longitude_center` | Float | Attribute | Center longitude of grid cell |
| `altitude_band_name` | Varchar | Attribute | Altitude tier (e.g., Low Ground 0-400ft, Mid 400-2000ft) |

---

## 3. Fact Tables

### 3.1 FactVehicleTracking
* **Grain:** One row represents one position report (state vector) from one vehicle at one exact timestamp.
* **Analytical Value for BI:** Foundation for real-time tracking, instantaneous speed distribution, and immediate density mapping.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `tracking_id` | Integer | Primary Key | Unique transaction identifier |
| `time_key` | Integer | Foreign Key | Links to `DimTime` |
| `vehicle_key` | Integer | Foreign Key | Links to `DimVehicle` |
| `grid_key` | Integer | Foreign Key | Links to `DimSpatialGrid` |
| `altitude_ft` | Float | Measure | Current altitude in feet MSL |
| `ground_speed_kts` | Float | Measure | Ground speed in knots |
| `heading_deg` | Float | Measure | Direction of travel in degrees |
| `vertical_rate_fps` | Float | Measure | Climb or descent rate in feet per second |
| `on_ground` | Boolean | Measure | Flag indicating if vehicle is on the ground |

### 3.2 FactFlightJourney
* **Grain:** One row represents a complete flight journey or significant flight segment from takeoff/entry to landing/exit.
* **Analytical Value for BI:** Analyzes route efficiency, average flight duration, and operational range by vehicle category.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `journey_id` | Integer | Primary Key | Unique journey identifier |
| `time_key` | Integer | Foreign Key | Links to `DimTime` (Takeoff time) |
| `vehicle_key` | Integer | Foreign Key | Links to `DimVehicle` |
| `flight_duration_sec` | Integer | Measure | Total duration of the journey in seconds |
| `max_altitude_ft` | Float | Measure | Peak altitude reached during flight |
| `total_distance_nm` | Float | Measure | Total horizontal distance traveled in nautical miles |
| `avg_speed_kts` | Float | Measure | Average ground speed across journey |

### 3.3 FactCloseEncounter
* **Grain:** One row represents a detected safety conflict where two vehicles breach minimum safe separation thresholds in space and time.
* **Analytical Value for BI:** Core safety metric for quantifying near-midair collision risks across different airspace zones and weather conditions.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `encounter_id` | Integer | Primary Key | Unique encounter identifier |
| `time_key` | Integer | Foreign Key | Links to `DimTime` |
| `vehicle_key_1` | Integer | Foreign Key | Links to `DimVehicle` (Primary vehicle) |
| `vehicle_key_2` | Integer | Foreign Key | Links to `DimVehicle` (Secondary conflicting vehicle) |
| `grid_key` | Integer | Foreign Key | Links to `DimSpatialGrid` (Location of encounter) |
| `min_horizontal_sep_nm` | Float | Measure | Closest horizontal distance achieved in nautical miles |
| `min_vertical_sep_ft` | Float | Measure | Closest vertical distance achieved in feet |
| `conflict_duration_sec` | Integer | Measure | Total duration both vehicles remained within breach threshold |
| `risk_severity_score` | Float | Measure | Calculated risk index based on closing speed and separation |

### 3.4 FactRestrictionActivation
* **Grain:** One row represents an active restriction event or TFR evaluation per time interval.
* **Analytical Value for BI:** Evaluates the perimeter impact of temporary flight restrictions on surrounding traffic rerouting.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `activation_id` | Integer | Primary Key | Unique activation record identifier |
| `time_key` | Integer | Foreign Key | Links to `DimTime` |
| `zone_key` | Integer | Foreign Key | Links to `DimAirspaceZone` |
| `affected_traffic_count` | Integer | Measure | Number of vehicles operating within or adjacent to restriction |
| `compliance_rate_pct` | Float | Measure | Percentage of traffic successfully maintaining safe buffer outside restriction |

### 3.5 FactAirspaceOccupancy
* **Grain:** One row represents a periodic (hourly/daily) utilization snapshot of vehicles occupying a specific spatial grid cell and altitude band.
* **Analytical Value for BI:** Essential for long-term capacity planning, corridor congestion pricing, and opening new automated drone delivery routes.

| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| `occupancy_id` | Integer | Primary Key | Unique snapshot record identifier |
| `time_key` | Integer | Foreign Key | Links to `DimTime` |
| `grid_key` | Integer | Foreign Key | Links to `DimSpatialGrid` |
| `active_vehicle_count` | Integer | Measure | Total unique vehicles visiting the grid cell during the interval |
| `total_occupancy_minutes` | Float | Measure | Cumulative minutes vehicles spent occupying the cell |
| `avg_traffic_speed_kts` | Float | Measure | Average speed of all vehicles in the cell during snapshot |
