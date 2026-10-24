# Project Name: AeroGrid Warehouse

## Project Overview

**Full Title:** Low-Altitude Airspace Intelligence Warehouse for Unmanned Aircraft System Traffic Management and Mixed Traffic

This project builds a data warehouse focused on low-altitude airspace. The goal is to support safe and efficient management of drones, manned aircraft, and emerging aerial vehicles (such as vehicles capable of short flights using thrusters) that share the same airspace near the ground.

As automated drones expand and new types of aerial vehicles appear, organizations responsible for traffic management need better visibility into how crowded the lower skies are, where risks of close encounters occur, how restrictions and weather affect operations, and where new flight corridors can safely be opened. This warehouse answers those needs by combining real surveillance data, airspace restriction information, weather conditions, and trajectory records into one analytical system.

The warehouse is designed around clear business processes and analytical questions rather than simply copying operational tables. It enables decision makers (traffic management service providers, regulators, drone operators, and city planners) to understand current conditions, detect risks, measure utilization, and plan capacity.

---

## Exact Data Sources and Formats

The warehouse draws from multiple real and publicly available sources in different formats. This multi-source, multi-format approach reflects real industrial data challenges.

| Data Source | Information Provided | File / Response Formats | Access Method | Role in the Warehouse |
|-------------|----------------------|-------------------------|---------------|-----------------------|
| OpenSky Network | Real-time and historical aircraft position reports including location, altitude, speed, direction, identity, and whether the aircraft is on the ground | JSON from the live programming interface; CSV, JSON, and Avro for historical samples; SQL queries for large historical volumes | Free registration for research and educational use; higher limits and historical database access after registration | Main source of continuous position reports and flight paths for manned and some unmanned traffic |
| Federal Aviation Administration Unmanned Aircraft System Data Delivery System | Maps of areas where drones can fly under automatic approval, temporary and permanent flight restrictions, national security restrictions, and airspace boundary polygons | GeoJSON, CSV, KML, Shapefile | Fully public open data portal | Geographic context, restriction events, and airspace zone definitions |
| TartanAviation Dataset (Carnegie Mellon University) | High-quality aircraft trajectory records collected near airports over many months, together with related weather observations | CSV and text files (raw and cleaned versions) | Open download scripts available on public repositories | Detailed trajectory enrichment and terminal-area density analysis |
| Public Aviation Weather Services | Surface weather conditions including wind, visibility, cloud ceiling, and related observations | JSON, CSV, or standard meteorological text | Free public interfaces | Weather dimension for correlating conditions with traffic and risk |
| Public Unmanned Aircraft Telemetry Benchmarks and Generated Trajectories | Sample drone flight logs and synthetically generated low-altitude paths (including short hop-style movements that model emerging aerial vehicles) | CSV and JSON | Open academic benchmarks plus project-generated data for mixed-traffic scenarios | Pure drone traffic and future vehicle types so the warehouse covers mixed operations |

These sources together provide live streams, historical bulk files, geographic polygons, and structured trajectory records. The combination forces proper extraction, cleaning, and integration work that matches industrial data warehousing practice.

---

## Business Aims and Analytical Focus

The main aims of the project are:

- Give traffic management organizations a single, reliable view of activity in the lower sky.
- Measure how crowded different altitude layers and geographic areas become at different times.
- Detect and quantify close encounters between vehicles so safety risks can be understood and reduced.
- Show the real effect of temporary flight restrictions and weather on traffic patterns.
- Support forward-looking decisions such as recommending new flight corridors or estimating how much extra capacity a traffic management system will need when drone numbers grow.

The warehouse therefore serves both day-to-day monitoring and longer-term planning.

---

## Business Processes

The warehouse is organized around five clear business processes. Each process represents something that actually happens in low-altitude airspace and that decision makers care about measuring.

### 1. Continuous Vehicle Tracking
Every aircraft or drone that is flying regularly broadcasts or reports its current position, height, speed, and direction. This process captures those ongoing reports so the system always knows what is moving where in the lower sky. It is the foundation for all awareness and density calculations.

### 2. Complete Flight Journey Recording
A full journey begins when a vehicle takes off or becomes active and ends when it lands or leaves the monitored area. This process records the entire path of each journey (or meaningful segments of longer flights) so analysts can study route choices, duration, altitude profiles, and overall traffic flow.

### 3. Restriction Activation and Coverage
Authorities issue temporary or standing rules that limit where and when vehicles may fly (for example around airports, stadiums, or security sites). This process records when each restriction starts, how long it lasts, and exactly which geographic area it covers. It allows the warehouse to measure the real impact of these rules on traffic.

### 4. Close Encounter Detection
When two or more vehicles come closer than a safe separation distance in space and time, a potential conflict exists. This process identifies and records every such close encounter. It turns raw position data into concrete safety events that can be counted, located, and analyzed by type of vehicle or location.

### 5. Airspace Occupancy Snapshot
At regular time intervals the system calculates how many vehicles are present, how long they occupy each geographic grid cell, and which altitude bands are busiest. This process creates a periodic picture of utilization. It supports capacity planning and helps answer questions about where the sky is under-used or over-used.

These five processes are deliberately simple to understand yet directly tied to the real work of managing mixed low-altitude traffic.

---

## Ten Analytical Questions

The following ten questions drive the design of the warehouse. They are concrete, measurable, and useful to the intended users.

1. How crowded do different altitude layers and map grids become throughout a typical day and night in selected urban or airport areas?
2. Which parts of the low-altitude sky stay occupied the longest and therefore need the most careful capacity management?
3. How has the overall volume of low-altitude traffic and the average flying height changed from month to month and across seasons?
4. At what times of day or on which days of the week does traffic peak, and does the mix of manned aircraft versus drones shift noticeably?
5. How many close encounters occur each day, and where in the sky (by height and location) are they most common?
6. Which types of vehicles appear most often in close encounters, and are certain operators or aircraft categories involved more frequently?
7. When a temporary flight restriction is active, how much does traffic density drop or shift in the surrounding area?
8. Do stronger winds, lower visibility, or lower cloud ceilings reduce the number of operations or increase the number of close encounters?
9. If the number of drones in a busy corridor were suddenly doubled or tripled, how would density and the number of close encounters change?
10. Which altitude bands and geographic zones currently show both low traffic and few historical close encounters, making them the strongest candidates for new recommended drone corridors?

These questions ensure the dimensional model is built to answer real operational and planning needs rather than generic reporting.

---

## How the Remaining Phase 1 Deliverables Will Be Produced

Phase 1 requires several documents that build directly on the material above. Below is a brief explanation of how each remaining deliverable will be completed once the foundation is locked.

- **Project Proposal**  
  A short formal document that introduces the AeroGrid, states the business problem, lists the main aims, names the data sources, and explains why the chosen domain is both timely and suitable for a data warehousing project.

- **Business Requirements Document**  
  Expands the aims into clear stakeholder needs, lists the five business processes, describes the expected analytical capabilities, and records any constraints (for example public data only, academic time limits).

- **Ten Business Questions Document**  
  Presents the ten questions listed above in a clean, numbered format, each accompanied by a one-sentence explanation of why the question matters to traffic management users.

- **Fact and Dimension Identification**  
  For each of the five business processes a fact table is named and justified. All supporting dimensions (Time, Vehicle, Airspace Zone, Restriction, Weather, and others) are listed together with the hierarchies that will support drill-down analysis.

- **Grain Definition Document**  
  Each fact table receives an explicit grain statement written in plain English (for example: “One row represents one position report from one vehicle at one exact timestamp”). The grain statements prevent double-counting and guide later physical design.

- **Star or Snowflake Schema Diagram**  
  A visual model (created in a tool such as draw.io or dbdiagram.io) that shows every fact table, every dimension table, primary keys, foreign keys, important attributes, and the chosen grain. Both conceptual and logical views are included.

- **Data Dictionary**  
  A structured spreadsheet that lists every table and every column, together with data type, description, source system, and whether the column is a key, a measure, or a descriptive attribute.

All of these documents flow naturally from the business processes and analytical questions defined in this guide. Once the processes and questions are approved, the remaining artifacts become straightforward to complete within the Phase 1 timeline.