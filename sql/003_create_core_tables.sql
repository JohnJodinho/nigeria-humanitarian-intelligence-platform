-- =============================================================================
-- Phase 1: 003_create_core_tables.sql
-- Core Dimension and Fact Tables for Nigeria Humanitarian Intelligence
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. DIMENSIONS
-- -----------------------------------------------------------------------------

-- Admin0 / Location Dimension
CREATE TABLE IF NOT EXISTS core.dim_location (
    location_code           VARCHAR(3) PRIMARY KEY,
    location_name           VARCHAR(100) NOT NULL,
    has_hno                 BOOLEAN NOT NULL DEFAULT TRUE,
    has_hrp                 BOOLEAN NOT NULL DEFAULT TRUE,
    in_gho                  BOOLEAN NOT NULL DEFAULT TRUE,
    reference_period_start  TIMESTAMPTZ,
    reference_period_end    TIMESTAMPTZ,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Admin1 / State Dimension
CREATE TABLE IF NOT EXISTS core.dim_admin1 (
    admin1_code             VARCHAR(10) PRIMARY KEY,
    admin1_name             VARCHAR(100) NOT NULL,
    location_code           VARCHAR(3) NOT NULL REFERENCES core.dim_location(location_code) ON DELETE CASCADE,
    geom                    GEOMETRY(MultiPolygon, 4326),
    latitude                NUMERIC(9,6),
    longitude               NUMERIC(9,6),
    is_unspecified          BOOLEAN NOT NULL DEFAULT FALSE,
    reference_period_start  TIMESTAMPTZ,
    reference_period_end    TIMESTAMPTZ,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_dim_admin1_geom ON core.dim_admin1 USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_dim_admin1_loc ON core.dim_admin1(location_code);

-- Admin2 / LGA Dimension
CREATE TABLE IF NOT EXISTS core.dim_admin2 (
    admin2_code             VARCHAR(15) PRIMARY KEY,
    admin2_name             VARCHAR(100) NOT NULL,
    admin1_code             VARCHAR(10) NOT NULL REFERENCES core.dim_admin1(admin1_code) ON DELETE CASCADE,
    location_code           VARCHAR(3) NOT NULL REFERENCES core.dim_location(location_code) ON DELETE CASCADE,
    geom                    GEOMETRY(MultiPolygon, 4326),
    latitude                NUMERIC(9,6),
    longitude               NUMERIC(9,6),
    is_unspecified          BOOLEAN NOT NULL DEFAULT FALSE,
    reference_period_start  TIMESTAMPTZ,
    reference_period_end    TIMESTAMPTZ,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_dim_admin2_geom ON core.dim_admin2 USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_dim_admin2_admin1 ON core.dim_admin2(admin1_code);

-- Organization Master Dimension
CREATE TABLE IF NOT EXISTS core.dim_organization (
    org_acronym             VARCHAR(50) PRIMARY KEY,
    org_name                VARCHAR(255) NOT NULL,
    org_type_code           VARCHAR(10),
    org_type_description    VARCHAR(100),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Humanitarian Sector / Cluster Dimension
CREATE TABLE IF NOT EXISTS core.dim_sector (
    sector_code             VARCHAR(20) PRIMARY KEY,
    sector_name             VARCHAR(100) NOT NULL,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 2. FACT TABLES
-- -----------------------------------------------------------------------------

-- Fact: Baseline Demographic Population (State Level)
CREATE TABLE IF NOT EXISTS core.fact_population (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin1_code             VARCHAR(10) NOT NULL REFERENCES core.dim_admin1(admin1_code) ON DELETE CASCADE,
    year                    INT NOT NULL,
    gender                  VARCHAR(5) NOT NULL,
    age_range               VARCHAR(15) NOT NULL,
    min_age                 INT,
    max_age                 INT,
    population              BIGINT NOT NULL CHECK (population >= 0),
    reference_period_start  TIMESTAMPTZ NOT NULL,
    reference_period_end    TIMESTAMPTZ NOT NULL,
    dataset_hdx_id          VARCHAR(100),
    resource_hdx_id         VARCHAR(100),
    extracted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_population UNIQUE (admin1_code, year, gender, age_range, reference_period_start)
);
CREATE INDEX IF NOT EXISTS idx_fact_population_admin1 ON core.fact_population(admin1_code, year);

-- Fact: Humanitarian Needs (PIN - LGA Level)
CREATE TABLE IF NOT EXISTS core.fact_humanitarian_needs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin2_code             VARCHAR(15) NOT NULL REFERENCES core.dim_admin2(admin2_code) ON DELETE CASCADE,
    sector_code             VARCHAR(20) NOT NULL REFERENCES core.dim_sector(sector_code) ON DELETE CASCADE,
    category                VARCHAR(20) NOT NULL,
    population_group        VARCHAR(20) NOT NULL,
    population_status       VARCHAR(20),
    gender                  VARCHAR(5) NOT NULL,
    age_range               VARCHAR(15) NOT NULL,
    disabled_marker         VARCHAR(1) NOT NULL,
    population              BIGINT NOT NULL CHECK (population >= 0),
    reference_period_start  TIMESTAMPTZ NOT NULL,
    reference_period_end    TIMESTAMPTZ NOT NULL,
    dataset_hdx_id          VARCHAR(100),
    resource_hdx_id         VARCHAR(100),
    extracted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_humanitarian_needs UNIQUE (
        admin2_code, sector_code, category, population_group, 
        gender, age_range, disabled_marker, reference_period_start
    )
);
CREATE INDEX IF NOT EXISTS idx_fact_needs_admin2 ON core.fact_humanitarian_needs(admin2_code);
CREATE INDEX IF NOT EXISTS idx_fact_needs_sector ON core.fact_humanitarian_needs(sector_code, category);
CREATE INDEX IF NOT EXISTS idx_fact_needs_ref ON core.fact_humanitarian_needs(reference_period_start);

-- Fact: Displacement / IDPs (LGA Level Baseline)
CREATE TABLE IF NOT EXISTS core.fact_idps (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin2_code             VARCHAR(15) NOT NULL REFERENCES core.dim_admin2(admin2_code) ON DELETE CASCADE,
    assessment_type         VARCHAR(50) NOT NULL,
    reporting_round         INT,
    operation               VARCHAR(100),
    population              BIGINT NOT NULL CHECK (population >= 0),
    reference_period_start  TIMESTAMPTZ NOT NULL,
    reference_period_end    TIMESTAMPTZ NOT NULL,
    dataset_hdx_id          VARCHAR(100),
    resource_hdx_id         VARCHAR(100),
    extracted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_idps UNIQUE (admin2_code, assessment_type, reference_period_start)
);
CREATE INDEX IF NOT EXISTS idx_fact_idps_admin2 ON core.fact_idps(admin2_code);
CREATE INDEX IF NOT EXISTS idx_fact_idps_ref ON core.fact_idps(reference_period_start);

-- Fact: Operational Presence / 3W (LGA Level)
CREATE TABLE IF NOT EXISTS core.fact_operational_presence (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin2_code             VARCHAR(15) NOT NULL REFERENCES core.dim_admin2(admin2_code) ON DELETE CASCADE,
    org_acronym             VARCHAR(50) NOT NULL REFERENCES core.dim_organization(org_acronym) ON DELETE CASCADE,
    sector_code             VARCHAR(20) NOT NULL REFERENCES core.dim_sector(sector_code) ON DELETE CASCADE,
    reference_period_start  TIMESTAMPTZ NOT NULL,
    reference_period_end    TIMESTAMPTZ NOT NULL,
    dataset_hdx_id          VARCHAR(100),
    resource_hdx_id         VARCHAR(100),
    extracted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_operational_presence UNIQUE (admin2_code, org_acronym, sector_code, reference_period_start)
);
CREATE INDEX IF NOT EXISTS idx_fact_op_admin2 ON core.fact_operational_presence(admin2_code);
CREATE INDEX IF NOT EXISTS idx_fact_op_org ON core.fact_operational_presence(org_acronym);
CREATE INDEX IF NOT EXISTS idx_fact_op_sector ON core.fact_operational_presence(sector_code);
CREATE INDEX IF NOT EXISTS idx_fact_op_ref ON core.fact_operational_presence(reference_period_start);
