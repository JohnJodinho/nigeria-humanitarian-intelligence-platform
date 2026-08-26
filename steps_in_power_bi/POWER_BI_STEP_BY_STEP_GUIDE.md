# Nigeria Humanitarian Intelligence Platform (N-HIP)
## Complete Power BI End-to-End Build, Design & Deployment Master Guide

**Purpose of this Guide:** An exhaustive, click-by-click, drag-and-drop manual for constructing the complete 6-page interactive executive intelligence suite in Power BI Desktop, configuring Row-Level Security (RLS), publishing to Power BI Service, and building executive dashboards.

---

## Table of Contents
1. [Prerequisites & Environment Checklist](#1-prerequisites--environment-checklist)
2. [Database Connection to Supabase PostgreSQL (IPv4 Session Pooler)](#2-database-connection-to-supabase-postgresql-ipv4-session-pooler)
3. [Power Query Data Cleaning, Navigation Columns & Explicit Data Typing](#3-power-query-data-cleaning-navigation-columns--explicit-data-typing)
4. [Star Schema Relationship Modeling (Optimized Core Model)](#4-star-schema-relationship-modeling-optimized-core-model)
5. [Complete DAX Measures Library (`_Measures`)](#5-complete-dax-measures-library-_measures)
6. [Design System, Color Palette & Modern JSON Theme](#6-design-system-color-palette--modern-json-theme)
7. [Step-by-Step Report Page Construction (Pages 1–6)](#7-step-by-step-report-page-construction-pages-16)
   - [Page 1: Executive Humanitarian Overview](#page-1-executive-humanitarian-overview)
   - [Page 2: Humanitarian Needs & Sector Vulnerability](#page-2-humanitarian-needs--sector-vulnerability)
   - [Page 3: Displacement & IDP Dynamics](#page-3-displacement--idp-dynamics)
   - [Page 4: 3W Operational Presence & Response Matrix](#page-4-3w-operational-presence--response-matrix)
   - [Page 5: Partner Presence Density & Needs Gap Analysis](#page-5-partner-presence-density--needs-gap-analysis)
   - [Page 6: Data Warehouse Observability & Pipeline Health](#page-6-data-warehouse-observability--pipeline-health)
8. [Custom Nigeria Shape Map (GeoJSON / TopoJSON) Setup](#8-custom-nigeria-shape-map-geojson--topojson-setup)
9. [Row-Level Security (RLS) Configuration](#9-row-level-security-rls-configuration)
10. [Publishing to Power BI Service, Scheduled Refresh & Dashboard Creation](#10-publishing-to-power-bi-service-scheduled-refresh--dashboard-creation)

---

## 1. Prerequisites & Environment Checklist

1. **Power BI Desktop**: Latest version installed.
2. **Supabase Credentials (IPv4 Session Pooler)**:
   - **Host / Server**: `aws-0-<region>.pooler.supabase.com`
   - **Port**: `5432` (or `6543`)
   - **Database**: `postgres`
   - **User**: `postgres.<project-ref>` (e.g. `postgres.fusxxjppszljvwfgcfhr`)
   - **Password**: `<your-supabase-database-password>`
3. **Boundary Shapefiles**:
   - `data/spatial/nga_admin1_boundaries.geojson` (located in your local project folder).

---

## 2. Database Connection to Supabase PostgreSQL (IPv4 Session Pooler)

### Step 2.1: Open Power BI Desktop & Connect via PostgreSQL
1. Launch **Power BI Desktop**.
2. On the **Home** ribbon, click **Get Data** > **More...** > select **PostgreSQL database** > click **Connect**.
3. **Server**: Enter your Supabase IPv4 Pooler host and port:
   ```text
   aws-0-eu-central-1.pooler.supabase.com:5432
   ```
   *(Replace with your exact pooler host from Supabase)*.
4. **Database**: Type `postgres`.
5. **Data Connectivity mode**: Select **Import**.
6. Click **OK**.

### Step 2.2: Authenticate with Database Credentials
1. In the credentials window, click the **Database** tab on the left.
2. **User name**: Enter `postgres.<your-project-ref>` (e.g. `postgres.fusxxjppszljvwfgcfhr`).
3. **Password**: Enter your database password.
4. Click **Connect** (click *Continue* if prompted regarding unencrypted connection).

### Step 2.3: Select Tables & Analytical Marts in Navigator
In the **Navigator** window, check the boxes for:
- `marts.vw_bi_lga_humanitarian_summary`
- `marts.vw_bi_state_humanitarian_profile`
- `marts.vw_bi_3w_operational_matrix`
- `marts.vw_bi_pipeline_observability`
- `core.dim_organization`
- `core.dim_sector`
- `core.fact_humanitarian_needs`
- `core.fact_idps`

Click **Transform Data** to open the **Power Query Editor**.

---

## 3. Power Query Data Cleaning, Navigation Columns & Explicit Data Typing

In the **Power Query Editor**, perform the following systematic cleanup on each query:

### ⚡ Universal Rule for PostgreSQL Navigation Columns:
When Power BI connects to PostgreSQL, it automatically creates navigation columns for foreign keys at the end of tables showing `"Table"` or `"Value"` (e.g. `core.fact_operational_presence`, `core.dim_sector`, etc.).
👉 **ACTION: DO NOT EXPAND THESE. Right-click and Remove all navigation columns.** We handle relationships purely in the Power BI Model View.

---

### Query 1: `LGA Summary` (rename from `marts vw_bi_lga_humanitarian_summary`)
1. **Remove PostGIS Geometry Column**:
   - Right-click the `lga_geom` column > click **Remove**. *(PostGIS binary geometries cause errors in Power Query; Power BI uses `latitude`/`longitude` and custom GeoJSON shape maps instead)*.
2. **Remove Any Foreign Key Navigation Columns** (showing `[Table]` or `[Value]`).
3. **Set Column Data Types**:
   - `admin2_code` -> **Text** (`ABC`)
   - `lga_name` -> **Text** (`ABC`)
   - `admin1_code` -> **Text** (`ABC`)
   - `state_name` -> **Text** (`ABC`)
   - `latitude` -> **Decimal Number** (`1.2`)
   - `longitude` -> **Decimal Number** (`1.2`)
   - `people_in_need` -> **Whole Number** (`123`)
   - `people_targeted` -> **Whole Number** (`123`)
   - `hno_assessment_date` -> **Date** (📅) or **Date/Time**
   - `idp_count` -> **Whole Number** (`123`)
   - `idp_assessment_date` -> **Date** (📅) or **Date/Time**
   - `active_partners_count` -> **Whole Number** (`123`)
   - `active_clusters_count` -> **Whole Number** (`123`)
   - `partner_presence_density_per_10k_pin` -> **Decimal Number** (`1.2`)
   - `target_coverage_pct` -> **Decimal Number** (`1.2`)

---

### Query 2: `State Profile` (rename from `marts vw_bi_state_humanitarian_profile`)
1. **Remove PostGIS Geometry Column**:
   - Right-click `state_geom` > click **Remove**.
2. **Remove Navigation Columns**.
3. **Set Column Data Types**:
   - `admin1_code` -> **Text** (`ABC`)
   - `state_name` -> **Text** (`ABC`)
   - `latitude` -> **Decimal Number** (`1.2`)
   - `longitude` -> **Decimal Number** (`1.2`)
   - `baseline_population` -> **Whole Number** (`123`)
   - `people_in_need` -> **Whole Number** (`123`)
   - `people_targeted` -> **Whole Number** (`123`)
   - `idp_count` -> **Whole Number** (`123`)
   - `pin_prevalence_pct` -> **Decimal Number** (`1.2`)
   - `active_partners_count` -> **Whole Number** (`123`)
   - `active_clusters_count` -> **Whole Number** (`123`)
   - `lgas_with_needs_count` -> **Whole Number** (`123`)
   - `lgas_with_presence_count` -> **Whole Number** (`123`)

---

### Query 3: `3W Operational Matrix` (rename from `marts vw_bi_3w_operational_matrix`)
1. **Remove Navigation Columns**.
2. **Standardize Acronym Case**:
   - Select column `org_acronym` > Transform tab > **Format** > **UPPERCASE**.
3. **Set Column Data Types**:
   - `presence_record_id` -> **Text** (`ABC`)
   - `admin1_code` -> **Text** (`ABC`)
   - `state_name` -> **Text** (`ABC`)
   - `admin2_code` -> **Text** (`ABC`)
   - `lga_name` -> **Text** (`ABC`)
   - `lga_latitude` -> **Decimal Number** (`1.2`)
   - `lga_longitude` -> **Decimal Number** (`1.2`)
   - `org_acronym` -> **Text** (`ABC`)
   - `org_name` -> **Text** (`ABC`)
   - `org_type` -> **Text** (`ABC`)
   - `sector_code` -> **Text** (`ABC`)
   - `sector_name` -> **Text** (`ABC`)
   - `reference_period_start` -> **Date** (📅) or **Date/Time**
   - `reference_period_end` -> **Date** (📅) or **Date/Time**
   - `operational_quarter` -> **Text** (`ABC`, e.g. `2025-Q3`)

---

### Query 4: `Pipeline Observability` (rename from `marts vw_bi_pipeline_observability`)
*(Note: Left as a disconnected telemetry table for Page 6).*
1. **Set Column Data Types**:
   - `run_id` -> **Text** (`ABC`)
   - `endpoint_name` -> **Text** (`ABC`)
   - `status` -> **Text** (`ABC`)
   - `records_extracted` -> **Whole Number** (`123`)
   - `records_inserted` -> **Whole Number** (`123`)
   - `records_quarantined` -> **Whole Number** (`123`)
   - `api_latency_ms` -> **Whole Number** (`123`)
   - `execution_time_seconds` -> **Decimal Number** (`1.2`)
   - `error_message` -> **Text** (`ABC`)
   - `run_timestamp` -> **Date/Time** (🕒)

---

### Query 5: `Dim Organization` (rename from `core dim_organization`)
1. **Remove Foreign Key Navigation Column**:
   - Right-click `core.fact_operational_presence` (showing `"Table"`) > click **Remove**.
2. **Resolve VertiPaq Case-Insensitive Duplicates**:
   - Select column `org_acronym` > Transform tab > **Format** > **UPPERCASE**.
   - Right-click column header `org_acronym` > click **Remove Duplicates** *(Reduces 2,411 rows to 2,404 truly distinct acronyms, allowing Power BI to establish a clean 1-to-Many relationship)*.
3. **Set Column Data Types**:
   - `org_acronym` -> **Text** (`ABC`)
   - `org_name` -> **Text** (`ABC`)
   - `org_type_code` -> **Text** (`ABC`) *(Kept as Text to preserve leading zeros or alphanumeric types)*
   - `org_type_description` -> **Text** (`ABC`)
   - `updated_at` -> **Date/Time** (🕒)

---

### Query 6: `Dim Sector` (rename from `core dim_sector`)
1. **Remove Navigation Columns**:
   - Right-click `core.fact_humanitarian_needs` > click **Remove**.
   - Right-click `core.fact_operational_presence` > click **Remove**.
2. **Set Column Data Types**:
   - `sector_code` -> **Text** (`ABC`)
   - `sector_name` -> **Text** (`ABC`)
   - `updated_at` -> **Date/Time** (🕒)

---

### Query 7: `Fact Needs Demographics` (rename from `core fact_humanitarian_needs`)
1. **Remove Navigation Columns**:
   - Right-click `core.dim_sector` (showing `"Value"`) > click **Remove**.
   - Right-click `core.dim_admin2` (showing `"Value"`) > click **Remove**.
2. **Set Column Data Types**:
   - `id` -> **Text** (`ABC`)
   - `admin2_code` -> **Text** (`ABC`)
   - `sector_code` -> **Text** (`ABC`)
   - `category` -> **Text** (`ABC`)
   - `population_group` -> **Text** (`ABC`)
   - `population_status` -> **Text** (`ABC`)
   - `gender` -> **Text** (`ABC`)
   - `age_range` -> **Text** (`ABC`)
   - `disabled_marker` -> **Text** (`ABC`)
   - `population` -> **Whole Number** (`123`)
   - `reference_period_start` -> **Date** (📅) or **Date/Time**
   - `reference_period_end` -> **Date** (📅) or **Date/Time**
   - `dataset_hdx_id` -> **Text** (`ABC`)
   - `resource_hdx_id` -> **Text** (`ABC`)
   - `extracted_at` -> **Date/Time** (🕒)

---

### Query 8: `Fact IDP Assessments` (rename from `core fact_idps`)
1. **Remove Navigation Column**:
   - Right-click `core.dim_admin2` (showing `"Value"`) > click **Remove**.
2. **Set Column Data Types**:
   - `id` -> **Text** (`ABC`)
   - `admin2_code` -> **Text** (`ABC`)
   - `assessment_type` -> **Text** (`ABC`)
   - `reporting_round` -> **Whole Number** (`123`)
   - `operation` -> **Text** (`ABC`)
   - `population` -> **Whole Number** (`123`)
   - `reference_period_start` -> **Date** (📅) or **Date/Time**
   - `reference_period_end` -> **Date** (📅) or **Date/Time**
   - `dataset_hdx_id` -> **Text** (`ABC`)
   - `resource_hdx_id` -> **Text** (`ABC`)
   - `extracted_at` -> **Date/Time** (🕒)

---

### Step 3.4: Apply Changes to Power BI Model
On the **Home** ribbon of Power Query Editor, click **Close & Apply**.

---

## 4. Star Schema Relationship Modeling (Optimized Core Model)

Click the **Model View** icon on the left sidebar.

### Wiring Core Relationships:
1. **`State Profile` to `LGA Summary`**:
   - Drag `State Profile[admin1_code]` ──(1:*)──> `LGA Summary[admin1_code]`.
   - Cardinality: **1 to Many (1:*)** | Cross-filter direction: **Single**
2. **`LGA Summary` to `3W Operational Matrix`**:
   - Drag `LGA Summary[admin2_code]` ──(1:*)──> `3W Operational Matrix[admin2_code]`.
   - Cardinality: **1 to Many (1:*)** | Cross-filter direction: **Single**
3. **`LGA Summary` to `Fact Needs Demographics`**:
   - Drag `LGA Summary[admin2_code]` ──(1:*)──> `Fact Needs Demographics[admin2_code]`.
   - Cardinality: **1 to Many (1:*)** | Cross-filter direction: **Single**
4. **`LGA Summary` to `Fact IDP Assessments`**:
   - Drag `LGA Summary[admin2_code]` ──(1:*)──> `Fact IDP Assessments[admin2_code]`.
   - Cardinality: **1 to Many (1:*)** | Cross-filter direction: **Single**
5. **`Dim Sector` to `Fact Needs Demographics`**:
   - Drag `Dim Sector[sector_code]` ──(1:*)──> `Fact Needs Demographics[sector_code]`.
   - Cardinality: **1 to Many (1:*)** | Cross-filter direction: **Single**
6. **`Dim Organization` to `3W Operational Matrix`**:
   - Drag `Dim Organization[org_acronym]` ──(1:*)──> `3W Operational Matrix[org_acronym]`.
   - Cardinality: **1 to Many (1:*)** | Cross-filter direction: **Single**
7. **`Pipeline Observability`**: Disconnected (Dedicated Page 6 Telemetry Table).

---

## 5. Complete DAX Measures Library (`_Measures`)

### Step 5.1: Create Dedicated `_Measures` Table
1. On the **Home** ribbon, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.

### Step 5.2: Create the Core DAX Measures
Right-click `_Measures` > **New Measure** for each formula:

```dax
// 1. Total Measured People in Need (PIN)
Total PIN = 
CALCULATE(
    SUM('LGA Summary'[people_in_need]),
    REMOVEFILTERS('LGA Summary'[partner_presence_density_per_10k_pin])
)

// 2. Sector-Specific People in Need (For Sector Bar Charts & Cluster Breakdowns)
Sector PIN = 
VAR _MaxPeriod = CALCULATE(MAX('Fact Needs Demographics'[reference_period_start]), ALL('Fact Needs Demographics'))
RETURN
CALCULATE(
    SUM('Fact Needs Demographics'[population]),
    LOWER('Fact Needs Demographics'[category]) = "total",
    'Fact Needs Demographics'[population_status] = "INN",
    'Fact Needs Demographics'[sector_code] <> "INTERSECTORAL",
    'Fact Needs Demographics'[reference_period_start] = _MaxPeriod
)

// 3. Total People Targeted
Total Targeted = 
SUM('LGA Summary'[people_targeted])

// 3. Overall Target Coverage Rate (%)
Target Coverage Rate % = 
DIVIDE([Total Targeted], [Total PIN], 0)

// 4. Total Displaced Persons (IDPs)
Total IDPs = 
SUM('LGA Summary'[idp_count])

// 5. Total Baseline Population
Total Population = 
SUM('State Profile'[baseline_population])

// 6. National / Regional PIN Prevalence Rate (%)
PIN Prevalence % = 
DIVIDE([Total PIN], [Total Population], 0)

// 7. Distinct Active Humanitarian Partner Organizations
Active Partners Count = 
DISTINCTCOUNT('3W Operational Matrix'[org_acronym])

// 8. Active Operational Clusters
Active Clusters Count = 
DISTINCTCOUNT('3W Operational Matrix'[sector_code])

// 9. Affected LGAs Count (LGAs with PIN > 0)
Affected LGAs Count = 
CALCULATE(
    DISTINCTCOUNT('LGA Summary'[admin2_code]),
    'LGA Summary'[people_in_need] > 0
)

// 10. Covered LGAs Count (LGAs with Partner Presence > 0)
Covered LGAs Count = 
CALCULATE(
    DISTINCTCOUNT('LGA Summary'[admin2_code]),
    'LGA Summary'[active_partners_count] > 0
)

// 11. Geographic Response Coverage Ratio (%)
Geographic Coverage % = 
DIVIDE([Covered LGAs Count], [Affected LGAs Count], 0)

// 12. Partner Presence Density (Partners per 10,000 PIN)
Partner Presence Density = 
VAR _Pin = [Total PIN]
VAR _Partners = [Active Partners Count]
RETURN
IF(_Pin > 0, DIVIDE(_Partners * 10000, _Pin, 0), 0)

// 13. High Priority Critical LGAs Count (PIN > 50k & Partners < 5)
High Priority Critical LGAs Count = 
COUNTROWS(
    FILTER(
        'LGA Summary',
        'LGA Summary'[people_in_need] >= 50000 && 'LGA Summary'[active_partners_count] < 5
    )
)

// 14. Observability Pipeline Data Hygiene Rate (%)
Pipeline Data Hygiene Rate % = 
VAR _TotalExtracted = SUM('Pipeline Observability'[records_extracted])
VAR _TotalQuarantined = SUM('Pipeline Observability'[records_quarantined])
RETURN
IF(_TotalExtracted > 0, 1 - DIVIDE(_TotalQuarantined, _TotalExtracted, 0), 1)

// 15. Dynamic Header Subtitle Text
Summary Subtitle Text = 
"Data Source: UN OCHA HDX HAPI | 2025 HNO Assessment Cycle | " & FORMAT([Affected LGAs Count], "#,0") & " Priority LGAs"
```

---

## 6. Design System, Color Palette & Modern Layout

### Color Palette Tokens:
- **Canvas Background**: `#F8FAFC` (Slate Light 50)
- **Container / Card Background**: `#FFFFFF` (Pure White) with 1px border `#E2E8F0` and soft shadow
- **Primary Text**: `#0F172A` (Slate 900)
- **Secondary Text / Muted**: `#64748B` (Slate 500)
- **Humanitarian Primary Blue**: `#0072BC` (UN Blue)
- **Emergency Severity High / Red**: `#E11D48` (Rose 600)
- **IDP Accent Orange**: `#EA580C` (Amber/Orange 600)
- **Target / Success Green**: `#10B981` (Emerald 500)
- **Partner / Cluster Purple**: `#6366F1` (Indigo 500)

---

## 7. Step-by-Step Report Page Construction (Pages 1–6)

### Page 1: Executive Humanitarian Overview
- **Top Banner**: Dark rectangle (`#0F172A`), Title "Nigeria Humanitarian Intelligence Platform", Subtitle `[Summary Subtitle Text]`.
- **KPI Cards**: `[Total PIN]` (`7.85M`), `[Total Targeted]`, `[Total IDPs]` (`3.83M`), `[Active Partners Count]` (`147`).
- **Choropleth Map**: Custom Shape map with `State Profile[state_name]` and `[Total PIN]`.
- **Bar Chart**: Sector breakdown by `[Total PIN]`.
- **Top 10 Table**: Priority LGAs sorted by `[Total PIN]`.

### Page 2: Humanitarian Needs & Sector Vulnerability
- **Donut Charts**: Gender, Age, and Population Group (IDPs vs Returnees vs Host).
- **Matrix Visual**: State/LGA rows vs Sector columns with conditional formatting.

### Page 3: Displacement & IDP Dynamics
- **Bubble Map**: Latitude/Longitude of LGAs with Bubble Size = `[Total IDPs]`.
- **Timeline Line Chart**: IDP assessment trends by date.

### Page 4: 3W Operational Presence & Response Matrix
- **Treemap**: Partner organization types (`UN Agency`, `INGO`, `NNGO`).
- **Matrix**: State/LGA rows vs Sector columns showing active organization counts and drill-down to acronyms.

### Page 5: Partner Presence Density & Needs Gap Analysis
- **Scatter Quadrant**: X-Axis = `[Total PIN]`, Y-Axis = `active_partners_count`, Quadrant reference lines.
- **Priority Action Table**: Highlight LGAs with Density < 1.0 and PIN > 50k.

### Page 6: Data Warehouse Observability & Pipeline Health
- **Telemetry Cards**: `[Pipeline Data Hygiene Rate %]`, Latest Sync Timestamp, Total Records.
- **Table**: `Pipeline Observability` runs, latency, and status.

---

## 8. Custom Nigeria Shape Map Setup
1. In Power BI Desktop: **File** > **Options and settings** > **Options** > **Preview features** > check **Shape map visual** > click **OK**.
2. Insert **Shape Map** > drag `State Profile[state_name]` to **Location**.
3. In **Format visual** > **Map settings** > **Map type** = **Custom map** > Browse to `data/spatial/nga_admin1_boundaries.geojson`.

---

## 9. Row-Level Security (RLS) Configuration
1. In **Modeling** ribbon > click **Manage Roles**.
2. Create `Borno_State_Coordinator`: Table `State Profile` -> `[state_name] = "Borno"`.
3. Create `Health_Sector_Lead`: Table `Fact Needs Demographics` -> `[sector_code] = "HEA" || [sector_code] = "Health"`.
4. Test with **View as**.

---

## 10. Publishing & Power BI Service Dashboard Creation
1. Click **Publish** to your workspace.
2. In Power BI Service: Settings > Data source credentials > enter pooler credentials (`Basic`, `postgres.<ref>`, password).
3. Set **Daily Scheduled Refresh** at `03:00 AM UTC`.
4. Pin KPI visual tiles to create the **Executive Dashboard**.



