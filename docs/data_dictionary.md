# Nigeria Humanitarian Intelligence Platform (N-HIP)
## Complete Data Dictionary & Schema Specification

This document details every table, view, column, data type, and business logic definition across the `core`, `marts`, and `audit` database schemas in the N-HIP warehouse.

---

## 1. Schema: `core` (Normalized Data Warehouse)

### Table: `core.dim_location`
Master country dimension representing the national geographic boundary.
- **`location_code`** (`VARCHAR(10)`, Primary Key): ISO3 country code (`NGA`).
- **`location_name`** (`VARCHAR(255)`): Country name (`Nigeria`).
- **`has_hno`** (`BOOLEAN`): Indicates presence of Humanitarian Needs Overview.
- **`has_hrp`** (`BOOLEAN`): Indicates presence of Humanitarian Response Plan.
- **`in_gho`** (`BOOLEAN`): Indicates inclusion in Global Humanitarian Overview.
- **`reference_period_start`** (`TIMESTAMPTZ`): Start of validity period.
- **`reference_period_end`** (`TIMESTAMPTZ`): End of validity period.
- **`updated_at`** (`TIMESTAMPTZ`): Last warehouse update timestamp.

### Table: `core.dim_admin1`
First-level administrative divisions (36 States + Federal Capital Territory).
- **`admin1_code`** (`VARCHAR(15)`, Primary Key): Official OCHA P-code (e.g. `NG001` to `NG037`).
- **`admin1_name`** (`VARCHAR(255)`): Standardized State name (e.g. `Borno`, `Adamawa`, `Yobe`).
- **`location_code`** (`VARCHAR(10)`, Foreign Key -> `dim_location.location_code`): Country code.
- **`is_unspecified`** (`BOOLEAN`): Flag for unspecified locations.
- **`latitude`** (`NUMERIC(10,6)`): Geometric centroid latitude coordinate.
- **`longitude`** (`NUMERIC(10,6)`): Geometric centroid longitude coordinate.
- **`geom`** (`GEOMETRY(MultiPolygon, 4326)`): PostGIS vector geometry polygon in WGS84.
- **`updated_at`** (`TIMESTAMPTZ`): Last update timestamp.

### Table: `core.dim_admin2`
Second-level administrative divisions (774 Local Government Areas).
- **`admin2_code`** (`VARCHAR(20)`, Primary Key): Official OCHA LGA P-code (e.g. `NG001001`).
- **`admin2_name`** (`VARCHAR(255)`): Standardized LGA name (e.g. `Maiduguri`, `Jere`, `Bama`).
- **`admin1_code`** (`VARCHAR(15)`, Foreign Key -> `dim_admin1.admin1_code`): Parent State P-code.
- **`location_code`** (`VARCHAR(10)`): Country code.
- **`latitude`** (`NUMERIC(10,6)`): Geometric centroid latitude coordinate.
- **`longitude`** (`NUMERIC(10,6)`): Geometric centroid longitude coordinate.
- **`geom`** (`GEOMETRY(MultiPolygon, 4326)`): PostGIS vector geometry polygon.
- **`updated_at`** (`TIMESTAMPTZ`): Last update timestamp.

### Table: `core.dim_organization`
Master registry of humanitarian partner organizations.
- **`org_acronym`** (`VARCHAR(100)`, Primary Key): Organization acronym (e.g. `UNICEF`, `MSF`, `INTERSOS`, `WFP`).
- **`org_name`** (`VARCHAR(255)`): Full official organization name.
- **`org_type_code`** (`VARCHAR(50)`): Organization classification code (`433`, `441`, etc.).
- **`org_type_description`** (`VARCHAR(100)`): Descriptive type (`UN Agency`, `International NGO`, `National NGO`).
- **`updated_at`** (`TIMESTAMPTZ`): Last update timestamp.

### Table: `core.dim_sector`
Humanitarian sectors and cluster coordination mechanisms.
- **`sector_code`** (`VARCHAR(50)`, Primary Key): Official sector acronym (`CCM`, `EDU`, `FSC`, `HEA`, `NUT`, `PRO`, `SHL`, `WSH`, `INTERSECTORAL`).
- **`sector_name`** (`VARCHAR(255)`): Full cluster title (e.g. `Food Security`, `Health`, `Water Sanitation Hygiene`).
- **`updated_at`** (`TIMESTAMPTZ`): Last update timestamp.

### Table: `core.fact_population`
Demographic baseline population estimates at State level.
- **`id`** (`UUID`, Primary Key): Auto-generated unique record identifier.
- **`admin1_code`** (`VARCHAR(15)`, Foreign Key -> `dim_admin1.admin1_code`): State P-code.
- **`year`** (`INTEGER`): Reference year.
- **`gender`** (`VARCHAR(50)`): Gender disaggregation (`all`, `f`, `m`).
- **`age_range`** (`VARCHAR(50)`): Age cohort (`all`, `0-4`, `5-17`, `18-59`, `60+`).
- **`min_age`** (`INTEGER`, Nullable): Lower bound of age cohort.
- **`max_age`** (`INTEGER`, Nullable): Upper bound of age cohort.
- **`population`** (`BIGINT`): Population count.
- **`reference_period_start`** (`TIMESTAMPTZ`): Start of reference validity.
- **`reference_period_end`** (`TIMESTAMPTZ`): End of reference validity.
- **`dataset_hdx_id`** (`VARCHAR(100)`): HDX dataset UUID.
- **`resource_hdx_id`** (`VARCHAR(100)`): HDX resource UUID.
- **`extracted_at`** (`TIMESTAMPTZ`): Pipeline extraction timestamp.

### Table: `core.fact_humanitarian_needs`
People in Need (PIN) and target population figures at LGA level.
- **`id`** (`UUID`, Primary Key): Unique record identifier.
- **`admin2_code`** (`VARCHAR(20)`, Foreign Key -> `dim_admin2.admin2_code`): LGA P-code.
- **`sector_code`** (`VARCHAR(100)`, Foreign Key -> `dim_sector.sector_code`): Sector cluster code.
- **`category`** (`VARCHAR(255)`): Demographic cohort (`total`, `Adult - Female - Host Communities`, etc.).
- **`population_group`** (`VARCHAR(255)`): Group status (`all`, `idp`, `returnees`, `host communities`).
- **`population_status`** (`VARCHAR(255)`): Indicator code (`INN` for In Need, `TAR` for Targeted).
- **`population`** (`BIGINT`): Affected population count.
- **`reference_period_start`** (`TIMESTAMPTZ`): HNO assessment start date.
- **`reference_period_end`** (`TIMESTAMPTZ`): HNO assessment end date.
- **`extracted_at`** (`TIMESTAMPTZ`): Extraction timestamp.

### Table: `core.fact_idps`
Internally Displaced Persons baseline and site assessment figures.
- **`id`** (`UUID`, Primary Key): Unique record identifier.
- **`admin2_code`** (`VARCHAR(20)`, Foreign Key -> `dim_admin2.admin2_code`): LGA P-code.
- **`assessment_type`** (`VARCHAR(100)`): IOM DTM survey type (`BA` for Baseline Assessment, `SA` for Site Assessment).
- **`reporting_round`** (`INTEGER`, Nullable): DTM survey round number.
- **`operation`** (`VARCHAR(255)`): Crisis operation title (`Lake Chad Basin Crisis`, etc.).
- **`population`** (`BIGINT`): Displaced individuals count.
- **`reference_period_start`** (`TIMESTAMPTZ`): Survey date.
- **`extracted_at`** (`TIMESTAMPTZ`): Extraction timestamp.

### Table: `core.fact_operational_presence`
Who does What Where (3W) matrix mapping partner activity.
- **`id`** (`UUID`, Primary Key): Unique record identifier.
- **`admin2_code`** (`VARCHAR(20)`, Foreign Key -> `dim_admin2.admin2_code`): LGA P-code.
- **`org_acronym`** (`VARCHAR(100)`, Foreign Key -> `dim_organization.org_acronym`): Partner acronym.
- **`sector_code`** (`VARCHAR(100)`, Foreign Key -> `dim_sector.sector_code`): Sector cluster code.
- **`reference_period_start`** (`TIMESTAMPTZ`): Operational quarter start.
- **`reference_period_end`** (`TIMESTAMPTZ`): Operational quarter end.
- **`extracted_at`** (`TIMESTAMPTZ`): Extraction timestamp.

---

## 2. Schema: `marts` (Analytical SQL Views)

### View: `marts.vw_bi_lga_humanitarian_summary` (774 rows)
The primary analytical mart providing single-period LGA summaries for Power BI map visuals and tables.
- `admin2_code`: LGA P-code.
- `lga_name`: LGA Name.
- `admin1_code`: State P-code.
- `state_name`: State Name.
- `latitude`: Centroid latitude.
- `longitude`: Centroid longitude.
- `lga_geom`: PostGIS geometry.
- `people_in_need`: Intersectoral People in Need for the latest HNO cycle.
- `people_targeted`: Targeted population.
- `hno_assessment_date`: Date of latest HNO assessment.
- `idp_count`: Latest IOM DTM baseline IDP count.
- `idp_assessment_date`: Date of DTM assessment.
- `active_partners_count`: Number of distinct organizations active in the LGA.
- `active_clusters_count`: Number of distinct active sectors.
- `partner_presence_density_per_10k_pin`: Density metric `(active_partners_count / people_in_need) * 10,000`.
- `target_coverage_pct`: Target ratio `(people_targeted / people_in_need) * 100`.

### View: `marts.vw_bi_state_humanitarian_profile` (37 rows)
State-level rollups for choropleth severity mapping.
- `admin1_code`: State P-code.
- `state_name`: State Name.
- `baseline_population`: State census baseline projection.
- `people_in_need`: Aggregated State PIN.
- `people_targeted`: Aggregated State Targeted population.
- `idp_count`: Aggregated State IDPs.
- `pin_prevalence_pct`: State population in need ratio `(people_in_need / baseline_population) * 100`.
- `active_partners_count`: Total distinct partners operating in the State.
- `active_clusters_count`: Total active clusters in the State.
- `lgas_with_needs_count`: Count of LGAs in the State where PIN > 0.
- `lgas_with_presence_count`: Count of LGAs with active partner presence.

### View: `marts.vw_bi_3w_operational_matrix` (985 rows)
Granular partner-cluster presence records for operational matrix drill-downs.
- `presence_record_id`: Record UUID.
- `state_name`: State name.
- `lga_name`: LGA name.
- `lga_latitude`, `lga_longitude`: Centroid coordinates.
- `org_acronym`: Partner acronym.
- `org_name`: Full organization title.
- `org_type`: Classification (`UN Agency`, `International NGO`, `National NGO`).
- `sector_code`, `sector_name`: Sector details.
- `operational_quarter`: Quarter string (e.g. `2025-Q3`).

---

## 3. Schema: `audit` (Pipeline Observability)

### Table: `audit.pipeline_runs`
Tracks every ETL pipeline execution.
- `run_id` (`UUID`, Primary Key): Unique run identifier.
- `endpoint_name` (`VARCHAR(100)`): Ingested dataset endpoint.
- `status` (`VARCHAR(20)`): Execution outcome (`SUCCESS`, `WARNING`, `FAILURE`).
- `records_extracted` (`INTEGER`): Total raw records fetched from API.
- `records_inserted` (`INTEGER`): Total records loaded into database.
- `records_quarantined` (`INTEGER`): Corrupt records routed to quarantine.
- `api_latency_ms` (`INTEGER`): API response time in milliseconds.
- `execution_time_seconds` (`NUMERIC(8,2)`): Total pipeline run duration.
- `error_message` (`TEXT`): Stack trace if execution failed.
- `created_at` (`TIMESTAMPTZ`): Timestamp of run.

### Table: `audit.pipeline_quarantine_log`
Isolates malformed records for debugging without breaking ETL flow.
- `quarantine_id` (`BIGSERIAL`, Primary Key): Log identifier.
- `run_id` (`UUID`, Foreign Key -> `pipeline_runs.run_id`): Parent run ID.
- `endpoint_name` (`VARCHAR(100)`): Originating endpoint.
- `record_payload` (`JSONB`): Full raw JSON record.
- `failure_rule_id` (`VARCHAR(100)`): Validation rule broken (`SCHEMA_VALIDATION_ERROR`, etc.).
- `failure_reason` (`TEXT`): Specific Pydantic validation error details.
- `quarantined_at` (`TIMESTAMPTZ`): Quarantine timestamp.
