# Nigeria Humanitarian Intelligence Platform (N-HIP)
## System Architecture & Technical Specification

N-HIP is an automated, enterprise-grade humanitarian data intelligence platform designed for crisis monitoring in Nigeria. It automates data extraction from the United Nations OCHA Humanitarian Data Exchange (HDX HAPI), performs validation and PostGIS geospatial harmonization, stores structured facts in a Supabase PostgreSQL warehouse, and exposes analytical SQL marts to Power BI for executive decision-making.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph EXT["1. External Data Layer"]
        HAPI["HDX HAPI REST API v2<br/>(UN OCHA Automated Ingestion)"]
        COD["UN OCHA COD GeoJSON<br/>(Admin1 & Admin2 Boundaries)"]
    end

    subgraph ETL["2. Automated Python Pipeline (GitHub Actions / Local)"]
        CLIENT["HAPI Client<br/>(Base64 Auth & Retry Engine)"]
        VAL["Pydantic Validator<br/>(Type Checks & Quarantine)"]
        TRANS["Transformer<br/>(P-Code Deduplication & Normalization)"]
        SPATIAL["Spatial Processor<br/>(GeoPandas & ST_Centroid Engine)"]
        LOADER["Database Loader<br/>(psycopg2 Bulk ON CONFLICT UPSERT)"]
        AUDIT["Audit Logger<br/>(Pipeline Latency & Runs)"]
    end

    subgraph DB["3. Cloud Data Warehouse (Supabase PostgreSQL 17 + PostGIS)"]
        subgraph CORE["Schema: core"]
            D_LOC["dim_location"]
            D_ADM1["dim_admin1 (37 States + Geom)"]
            D_ADM2["dim_admin2 (774 LGAs + Geom)"]
            D_ORG["dim_organization (2,411 Orgs)"]
            D_SEC["dim_sector (19 Clusters)"]
            F_POP["fact_population (1,998 Rows)"]
            F_PIN["fact_humanitarian_needs (46,334 Rows)"]
            F_IDP["fact_idps (12,112 Rows)"]
            F_3W["fact_operational_presence (985 Rows)"]
        end
        subgraph MARTS["Schema: marts"]
            V_LGA["vw_bi_lga_humanitarian_summary"]
            V_STATE["vw_bi_state_humanitarian_profile"]
            V_3W["vw_bi_3w_operational_matrix"]
            V_AUDIT["vw_bi_pipeline_observability"]
        end
        subgraph AUDIT_S["Schema: audit"]
            T_RUNS["pipeline_runs"]
            T_QUAR["pipeline_quarantine_log"]
        end
    end

    subgraph BI["4. Analytics & Executive Presentation (Power BI Service)"]
        P1["Page 1: Executive Macro Overview"]
        P2["Page 2: Sector Needs & Vulnerability"]
        P3["Page 3: Displacement & IDP Dynamics"]
        P4["Page 4: 3W Operational Response Matrix"]
        P5["Page 5: Needs vs Partner Density Gap"]
        P6["Page 6: Pipeline Observability"]
    end

    HAPI --> CLIENT
    COD --> SPATIAL
    CLIENT --> VAL
    VAL -->|Valid Records| TRANS
    VAL -->|Corrupt Records| T_QUAR
    TRANS --> LOADER
    SPATIAL --> LOADER
    LOADER --> CORE
    LOADER --> AUDIT
    AUDIT --> T_RUNS
    CORE --> MARTS
    MARTS --> BI
```

---

## 2. Key Architecture Pillars

### 1. Zero-Double-Counting Analytical Integrity
Humanitarian assessments often suffer from Cartesian multiplication when summing multi-sector demographics. N-HIP enforces strict filtering on the `INTERSECTORAL` cluster and pre-aggregated `category = 'total'` rows in `marts.vw_bi_lga_humanitarian_summary`, mathematically eliminating demographic double-counting.

### 2. Idempotent Data Loading
All loaders in `src/database/loader.py` utilize PostgreSQL `ON CONFLICT (...) DO UPDATE` statements bound to composite natural business keys (e.g. `admin2_code + sector_code + category + reference_period_start`). Running the ETL pipeline repeatedly results in zero data duplication.

### 3. Spatial Reference Harmonization
HDX HAPI provides P-codes but lacks vector polygons. N-HIP incorporates `src/geospatial/spatial_processor.py`, which maps official UN OCHA COD GeoJSON boundaries to `dim_admin1` and `dim_admin2` using fuzzy matching, providing 100% PostGIS polygon and centroid coverage for spatial choropleth mapping.

### 4. Fully Autonomous Cloud Execution
Configured with GitHub Actions (`.github/workflows/etl_daily_pipeline.yml`) to execute on a daily cron schedule (`02:00 UTC`), automatically pulling updates from HDX HAPI, validating records, and feeding the live Power BI executive dashboards.
