# Nigeria Humanitarian Information Management & Intelligence Platform (N-HIP)

[![CI Quality Assurance](https://github.com/your-username/nigeria-humanitarian-intelligence-platform/actions/workflows/ci_test_suite.yml/badge.svg)](https://github.com/your-username/nigeria-humanitarian-intelligence-platform/actions/workflows/ci_test_suite.yml)
[![Daily Automated ETL Pipeline](https://github.com/your-username/nigeria-humanitarian-intelligence-platform/actions/workflows/etl_daily_pipeline.yml/badge.svg)](https://github.com/your-username/nigeria-humanitarian-intelligence-platform/actions/workflows/etl_daily_pipeline.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PostGIS 3.3](https://img.shields.io/badge/PostGIS-3.3-00599C?logo=postgis&logoColor=white)](https://postgis.net/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop_%26_Service-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![HDX HAPI v2](https://img.shields.io/badge/Data_Source-UN_OCHA_HDX_HAPI-0072BC)](https://hapi.humdata.org/)

An enterprise-grade, end-to-end humanitarian data engineering and business intelligence platform designed for crisis monitoring in Nigeria. The platform automates data extraction from the **United Nations OCHA Humanitarian Data Exchange (HDX HAPI v2)**, performs strict Pydantic validation, cleans and harmonizes PostGIS spatial boundaries across all 37 States and 774 LGAs, stores normalized relational facts in **Supabase PostgreSQL**, and exposes analytical SQL data marts to **Power BI** for executive humanitarian response coordination.

---

## 📊 Live Measured Humanitarian Indicators (Nigeria 2025 HNO)

*Calculated directly from the live HDX HAPI dataset in the N-HIP warehouse:*

- **People in Need (PIN)**: **7,847,048** (7.85 Million across 65 crisis-affected LGAs in Borno, Adamawa, and Yobe states)
- **Displaced Population (IDPs)**: **3,825,197** (3.83 Million displaced individuals across 326 surveyed LGAs)
- **Active Humanitarian Partners**: **147 distinct organizations** (UN Agencies, INGOs, National NGOs)
- **State Severity Breakdown**:
  - **Borno State**: 3,751,949 PIN (**61.39%** population prevalence | 116 active partners)
  - **Adamawa State**: 2,053,334 PIN (**41.89%** population prevalence | 46 active partners)
  - **Yobe State**: 2,041,765 PIN (**55.94%** population prevalence | 48 active partners)
- **Highest Priority LGAs**: Maiduguri (450k PIN), Jere (425k PIN), Gwoza (248k PIN), Ngala (237k PIN), Bama (223k PIN).

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph EXT["1. External Data Sources"]
        HAPI["HDX HAPI REST API v2<br/>(UN OCHA Humanitarian Endpoints)"]
        COD["UN OCHA COD GeoJSON<br/>(Admin1 & Admin2 Boundaries)"]
    end

    subgraph ETL["2. Automated Python Pipeline (GitHub Actions)"]
        CLIENT["HAPI Client<br/>(Base64 Auth & Exponential Backoff)"]
        VAL["Pydantic Validator<br/>(Type Enforcement & Quarantine)"]
        TRANS["Data Transformer<br/>(P-Code Normalization & Deduplication)"]
        SPATIAL["Spatial Processor<br/>(GeoPandas & Centroid Engine)"]
        LOADER["Database Loader<br/>(Bulk PostgreSQL ON CONFLICT UPSERT)"]
        AUDIT["Audit Logger<br/>(Pipeline Latency & Runs)"]
    end

    subgraph DB["3. Cloud Data Warehouse (Supabase PostgreSQL + PostGIS)"]
        subgraph CORE["Schema: core (Normalized Warehouse)"]
            D_ADM1["dim_admin1 (37 States + Geometries)"]
            D_ADM2["dim_admin2 (774 LGAs + Geometries)"]
            D_ORG["dim_organization (2,411 Partners)"]
            D_SEC["dim_sector (19 Clusters)"]
            F_PIN["fact_humanitarian_needs (46,334 Rows)"]
            F_IDP["fact_idps (12,112 Rows)"]
            F_3W["fact_operational_presence (985 Rows)"]
        end
        subgraph MARTS["Schema: marts (Analytical Views)"]
            V_LGA["vw_bi_lga_humanitarian_summary"]
            V_STATE["vw_bi_state_humanitarian_profile"]
            V_3W["vw_bi_3w_operational_matrix"]
        end
    end

    subgraph BI["4. Analytics & Executive Cockpit (Power BI Service)"]
        P1["Page 1: Executive Macro Overview"]
        P2["Page 2: Sector Needs & Vulnerability"]
        P3["Page 3: Displacement & IDP Dynamics"]
        P4["Page 4: 3W Operational Response Matrix"]
        P5["Page 5: Partner Presence Density Gap"]
        P6["Page 6: Pipeline Observability"]
    end

    HAPI --> CLIENT
    COD --> SPATIAL
    CLIENT --> VAL
    VAL --> TRANS
    TRANS --> LOADER
    SPATIAL --> LOADER
    LOADER --> CORE
    LOADER --> AUDIT
    CORE --> MARTS
    MARTS --> BI
```

---

## 🚀 Key Engineering & Analytical Features

1. **Zero Double-Counting Analytical Integrity**:
   - Enforces strict single-slice filtering on the `INTERSECTORAL` cluster and pre-aggregated `category = 'total'` rows in SQL analytical marts, completely eliminating Cartesian multiplication across multi-sector demographic subsets.
2. **True Idempotent Data Ingestion**:
   - All database loaders utilize PostgreSQL `ON CONFLICT (...) DO UPDATE` statements bound to composite natural keys (`admin2_code + sector_code + reference_period_start`), ensuring subsequent pipeline executions update existing records with zero duplicate creation.
3. **100% PostGIS Spatial Harmonization**:
   - Uses GeoPandas and fuzzy string resolution to map official UN OCHA COD GeoJSON boundaries to 37 States and 774 LGAs, providing full vector geometry and `ST_Centroid` coordinate coverage for spatial choropleth mapping.
4. **Partner Presence Density Metric**:
   - Implements the operational density metric: `(Active Organizations / People in Need) * 10,000` to pinpoint critical response gaps without misrepresenting organization scale.
5. **Observability & Quarantine Governance**:
   - Quarantines malformed records to `audit.pipeline_quarantine_log` and records full execution telemetry in `audit.pipeline_runs`.
6. **Cloud Automation**:
   - Scheduled via GitHub Actions (`.github/workflows/etl_daily_pipeline.yml`) to execute every morning at `02:00 UTC` with automated test suites on pull requests.

---

## 📁 Repository Structure

```text
nigeria-humanitarian-intelligence-platform/
├── .github/
│   └── workflows/
│       ├── etl_daily_pipeline.yml    # Daily 02:00 UTC automated sync
│       └── ci_test_suite.yml         # Automated pytest on push/PR
├── data/
│   └── spatial/                      # Official UN OCHA COD GeoJSON boundaries
├── docs/
│   ├── architecture.md               # Deep-dive system architecture specification
│   └── data_dictionary.md           # Schema definitions and data dictionary
├── sql/
│   ├── 001_init_extensions.sql       # PostGIS & UUID extension bootstrap
│   ├── 002_create_schemas.sql        # staging, core, marts, audit schemas
│   ├── 003_create_core_tables.sql    # Relational dimensions and fact tables
│   ├── 004_create_audit_tables.sql   # Pipeline runs and quarantine logs
│   └── 005_create_analytical_views.sql # Analytical SQL marts for Power BI
├── src/
│   ├── api/                          # HDX HAPI v2 client with exponential backoff
│   ├── config/                       # Pydantic environment settings
│   ├── database/                     # Connection pool, bulk loaders, and audit logger
│   ├── geospatial/                   # GeoPandas PostGIS boundary seeding
│   ├── pipeline/                     # Master CLI ETL orchestrator
│   ├── transformation/               # P-code standardization and deduplication
│   └── validation/                   # Pydantic v2 data validation schemas
├── tests/                            # Automated pytest test suite
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development & test dependencies
├── .env.example                      # Configuration template
└── README.md                         # Master documentation
```

---

## 🛠️ Quick Start & Local Installation

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/your-username/nigeria-humanitarian-intelligence-platform.git
cd nigeria-humanitarian-intelligence-platform

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Supabase connection URL:
```ini
HDX_HAPI_APP_NAME=NigeriaHIMS
HDX_HAPI_EMAIL=your_email@example.com
HDX_HAPI_BASE_URL=https://hapi.humdata.org
DATABASE_URL=postgresql://postgres:your_password@db.your_ref.supabase.co:5432/postgres
SUPABASE_DB_URL=postgresql://postgres:your_password@db.your_ref.supabase.co:5432/postgres
TARGET_COUNTRY_CODE=NGA
PIPELINE_LOG_LEVEL=INFO
```

### 3. Run Database Migrations
Execute the SQL bootstrap scripts against your Supabase PostgreSQL instance:
```bash
python run_migrations.py
```

### 4. Run the Master Ingestion Pipeline
```bash
python -m src.pipeline.orchestrator --country NGA
```

### 5. Run Automated Tests
```bash
pytest tests/ -v
```

---

## 📈 Power BI Report Suite

The platform feeds an interactive 6-page executive intelligence suite in Power BI Desktop & Service:

*Page previews will be displayed below once Power BI visuals are exported:*

- **Page 1: Executive Humanitarian Overview** (Macro KPIs, Nigeria State Choropleth, Cluster Breakdown)
- **Page 2: Humanitarian Needs & Vulnerability** (Demographic donuts: Gender, Age, IDP vs Host community, sector matrix)
- **Page 3: Displacement & IDP Dynamics** (LGA bubble map, DTM round timeline, site vs host community split)
- **Page 4: 3W Operational Presence & Response Matrix** (Organization treemap, partner matrix with drill-downs)
- **Page 5: Partner Presence Density & Needs Gap Analysis** (Needs vs Partners scatter quadrant chart pinpointing underserved high-need LGAs)
- **Page 6: Data Warehouse Observability & Pipeline Health** (ETL telemetry, latency charts, quarantine logs)

*(Detailed click-by-click build instructions are available in `POWER_BI_STEP_BY_STEP_GUIDE.md`)*

---

## 📜 Data Source & Attribution
Data is ingested strictly from the **United Nations OCHA Humanitarian Data Exchange (HDX) Humanitarian API (HAPI v2)** under the Creative Commons Attribution (CC BY-IGO) license.
