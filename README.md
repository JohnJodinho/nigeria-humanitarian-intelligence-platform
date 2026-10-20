# Nigeria Humanitarian Information Management & Intelligence Platform (N-HIP)

[![Live Interactive Power BI Report](https://img.shields.io/badge/Power_BI_Service-Live_Interactive_Report-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjYwNWNkMGQtMmQ3NS00OTI2LThkODktNDYyZDhhNGYxMmEwIiwidCI6ImRhOWM1Yzg5LWI2MmEtNDdhNC05MmEyLTY4Y2FjNjFmYTg1YyIsImMiOjh9&pageName=ad3927a0e6f554a8cdb5)
[![CI Quality Assurance](https://github.com/JohnJodinho/nigeria-humanitarian-intelligence-platform/actions/workflows/ci_test_suite.yml/badge.svg)](https://github.com/JohnJodinho/nigeria-humanitarian-intelligence-platform/actions/workflows/ci_test_suite.yml)
[![Daily Automated ETL Pipeline](https://github.com/JohnJodinho/nigeria-humanitarian-intelligence-platform/actions/workflows/etl_daily_pipeline.yml/badge.svg)](https://github.com/JohnJodinho/nigeria-humanitarian-intelligence-platform/actions/workflows/etl_daily_pipeline.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PostGIS 3.4](https://img.shields.io/badge/PostGIS-3.4-00599C?logo=postgis&logoColor=white)](https://postgis.net/)
[![HDX HAPI v2](https://img.shields.io/badge/Data_Source-UN_OCHA_HDX_HAPI-0072BC)](https://hapi.humdata.org/)

An enterprise-grade, end-to-end humanitarian data engineering and business intelligence platform designed for crisis monitoring in Nigeria. The platform automates data extraction from the **United Nations OCHA Humanitarian Data Exchange (HDX HAPI v2)**, performs strict Pydantic validation, cleans and harmonizes PostGIS spatial boundaries across all 37 States and 774 LGAs, stores normalized relational facts in **Supabase PostgreSQL**, and exposes analytical SQL data marts to **Power BI** for executive humanitarian response coordination.

---

## 🌐 Live Interactive Power BI Report

Access the live cloud interactive dashboard directly in your browser:
🔗 **[Launch Nigeria Humanitarian Intelligence Platform (Power BI Service)](https://app.powerbi.com/view?r=eyJrIjoiMjYwNWNkMGQtMmQ3NS00OTI2LThkODktNDYyZDhhNGYxMmEwIiwidCI6ImRhOWM1Yzg5LWI2MmEtNDdhNC05MmEyLTY4Y2FjNjFmYTg1YyIsImMiOjh9&pageName=ad3927a0e6f554a8cdb5)**

```html
<iframe title="N-HIP-Report" width="100%" height="600" src="https://app.powerbi.com/view?r=eyJrIjoiMjYwNWNkMGQtMmQ3NS00OTI2LThkODktNDYyZDhhNGYxMmEwIiwidCI6ImRhOWM1Yzg5LWI2MmEtNDdhNC05MmEyLTY4Y2FjNjFmYTg1YyIsImMiOjh9&pageName=ad3927a0e6f554a8cdb5" frameborder="0" allowFullScreen="true"></iframe>
```

---

## 📊 Executive Dashboard & Report Suite Gallery

### 1. Executive Humanitarian Overview (Page 1)
*Macro operational briefing for the Humanitarian Coordinator (HC) and Humanitarian Country Team (HCT).*
![Executive Overview](power-bi/screenshots/page1.png)

---

### 2. Humanitarian Needs & Sector Vulnerability Analysis (Page 2)
*Demographic disaggregation (Gender, Age Cohort, Population Group) and interactive cluster severity heatmap matrix.*
![Humanitarian Needs](power-bi/screenshots/page2.png)

---

### 3. Displacement Tracking & IDP Dynamics (Page 3)
*Geographic displacement concentration, IOM DTM survey round timeline, and top IDP burden LGAs.*
![Displacement and IDPs](power-bi/screenshots/page3.png)

---

### 4. 3W Operational Presence & Response Matrix (Page 4)
*Who does What Where coordination, organization type localization (National NGOs 67.3%), and cluster presence matrix.*
![3W Operational Presence](power-bi/screenshots/page4.png)

---

### 5. Partner Presence Density & Needs Gap Analysis (Page 5)
*Decision-support scatter quadrant matrix identifying 32 critical gap LGAs where PIN is acute but presence is sparse.*
![Needs Gap Analysis](power-bi/screenshots/page5.png)

---

### 6. Data Pipeline Observability & Telemetry (Page 6)
*Real-time engineering audit log, multi-environment telemetry (Production vs. Development), API latency benchmarks, and throughput.*
![Pipeline Health](power-bi/screenshots/page6.png)

---

### 7. Power BI Service Executive Command Center (Dashboard)
*Single-screen executive board consolidating top KPIs and strategic visuals with one-click drill-through navigation.*
![Executive Dashboard](power-bi/screenshots/dashboard.png)

---

### 8. Star Schema Modeling & Power Query Engineering
*Deduplicated dimension modeling, 1-to-many relationship topology, case normalization, and VertiPaq memory optimization.*
| Star Schema Data Model (Model View) | Power Query M-Engine Transformations |
| :---: | :---: |
| ![Model View](power-bi/screenshots/model_view.png) | ![Power Query](power-bi/screenshots/power_query.png) |

---

## 📈 Key Measured Indicators (Empirical Baseline)

*Calculated directly from the live HDX HAPI dataset in the N-HIP warehouse:*

- **People in Need (PIN)**: **7,847,048** (7.85 Million across 65 crisis-affected LGAs in Borno, Adamawa, and Yobe states)
- **Displaced Population (IDPs)**: **3,825,197** (3.83 Million displaced individuals across 331 surveyed LGAs)
- **Active Humanitarian Partners**: **147 distinct organizations** (99 National NGOs, 27 INGOs, 8 UN Agencies, 12 Government Entities)
- **Critical Response Gap LGAs**: **32 LGAs** identified with $\text{PIN} \ge 50,000$ and $< 10$ operating partners (affecting **2.96M** individuals)
- **State Severity Breakdown**:
  - **Borno State**: 3,751,949 PIN (**61.39%** population prevalence | 116 active partners)
  - **Adamawa State**: 2,053,334 PIN (**41.89%** population prevalence | 46 active partners)
  - **Yobe State**: 2,041,765 PIN (**55.94%** population prevalence | 48 active partners)

---

## 🏗️ Technical Architecture & Data Flow

```mermaid
flowchart TD
    subgraph EXT["1. External Data Sources"]
        HAPI["UN OCHA HDX HAPI REST API v2<br/>(Humanitarian Needs, IDPs, 3W, Orgs)"]
        COD["UN OCHA COD GeoJSON<br/>(Admin1 & Admin2 Boundaries)"]
    end

    subgraph ETL["2. Automated Python Pipeline (GitHub Actions CI/CD)"]
        CLIENT["HAPI Client<br/>(Base64 Auth & Exponential Backoff)"]
        VAL["Pydantic Validator<br/>(Type Enforcement & Quarantine)"]
        TRANS["Data Transformer<br/>(P-Code Normalization & Deduplication)"]
        SPATIAL["Spatial Processor<br/>(GeoPandas & TopoJSON Engine)"]
        LOADER["Database Loader<br/>(Bulk PostgreSQL ON CONFLICT UPSERT)"]
        AUDIT["Observability Logger<br/>(Multi-Environment Telemetry)"]
    end

    subgraph DB["3. Cloud Data Warehouse (Supabase PostgreSQL 17 + PostGIS)"]
        subgraph CORE["Schema: core (Normalized Star Schema)"]
            D_ADM1["dim_admin1 (37 States)"]
            D_ADM2["dim_admin2 (774 LGAs)"]
            D_ORG["dim_org (147 Orgs)"]
            D_SEC["dim_sector (19 Clusters)"]
            F_NEEDS["fact_humanitarian_needs (23.9K rows)"]
            F_IDP["fact_idps (12.1K rows)"]
            F_3W["fact_operational_presence (985 rows)"]
        end
        subgraph MARTS["Schema: marts (Analytical Views)"]
            V_LGA["vw_bi_lga_humanitarian_summary"]
            V_STATE["vw_bi_state_humanitarian_profile"]
            V_3W["vw_bi_3w_operational_matrix"]
            V_PIPE["vw_bi_pipeline_observability"]
        end
    end

    subgraph BI["4. Power BI Intelligence Suite (Desktop & Service)"]
        P1["Page 1: Executive Overview"]
        P2["Page 2: Sector Vulnerability"]
        P3["Page 3: Displacement & IDPs"]
        P4["Page 4: 3W Operational Response"]
        P5["Page 5: Needs Gap Analysis"]
        P6["Page 6: Pipeline Health"]
        DASH["Cloud Command Center Dashboard"]
    end

    EXT --> ETL
    ETL --> DB
    MARTS --> BI
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Ingestion & ETL** | Python 3.12, Requests | Resilient HTTP extraction with Base64 authentication & exponential backoff |
| **Data Validation** | Pydantic v2 | Strict schema validation and quarantine routing for corrupted records |
| **Spatial Processing**| GeoPandas, Shapely, TopoJSON | PostGIS polygon boundary normalization and choropleth mapping |
| **Database & GIS** | PostgreSQL 17, PostGIS 3.4, Supabase | High-performance spatial data warehousing and relational star schema |
| **BI & Analytics** | Power BI Desktop & Service, DAX, Power Query | Interactive executive intelligence suite, custom themes, and cloud dashboard |
| **CI/CD & Automation**| GitHub Actions, Pytest | Daily automated 02:00 UTC pipeline cron and automated unit testing |

---

## 🚀 Getting Started & Local Setup

### Prerequisites
* Python 3.11+
* PostgreSQL 15+ (or Supabase instance with PostGIS enabled)
* Power BI Desktop (for `.pbix` report editing)

### 1. Clone Repository
```bash
git clone https://github.com/JohnJodinho/nigeria-humanitarian-intelligence-platform.git
cd nigeria-humanitarian-intelligence-platform
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database connection URL
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# HDX HAPI API Credentials
HDX_HAPI_APP_NAME=NigeriaHIMS
HDX_HAPI_EMAIL=your_email@example.com
HDX_HAPI_BASE_URL=https://hapi.humdata.org

# Environment Tagging
APP_ENV=development
```

The workflow uses the same variables through GitHub Actions secrets. Do not commit
`.env`; use `.env.example` as the local template.

### 3. Install Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Run Migrations & Ingestion Pipeline
```bash
# Execute the SQL files in sql/001 through sql/005 against PostgreSQL/Supabase
# Then run the full end-to-end extraction and load pipeline
python -m src.pipeline.orchestrator --country NGA
```

### 5. Run Test Suite
```bash
pytest tests/ -v
```

---

## 📄 License & Attribution
* **Data Sources**: United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA) - [HDX HAPI](https://hapi.humdata.org/) and [IOM DTM](https://dtm.iom.int/nigeria).
* **License**: Released under the [MIT License](LICENSE).
