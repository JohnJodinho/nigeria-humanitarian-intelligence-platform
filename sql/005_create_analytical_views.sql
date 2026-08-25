-- ============================================================================
-- NIGERIA HUMANITARIAN INFORMATION MANAGEMENT & INTELLIGENCE PLATFORM (N-HIP)
-- SCRIPT 005: ANALYTICAL MARTS & BI VIEWS (PRECISION HNO TOTAL FILTERING)
-- ============================================================================

-- 1. LGA Humanitarian Executive Summary Mart
DROP VIEW IF EXISTS marts.vw_bi_lga_humanitarian_summary CASCADE;

CREATE OR REPLACE VIEW marts.vw_bi_lga_humanitarian_summary AS
WITH latest_hno AS (
    SELECT MAX(reference_period_start) AS max_period
    FROM core.fact_humanitarian_needs
    WHERE sector_code = 'INTERSECTORAL'
),
lga_needs AS (
    -- Authoritative Intersectoral Total PIN per LGA
    SELECT 
        n.admin2_code,
        SUM(n.population) AS people_in_need,
        MAX(n.reference_period_start)::date AS hno_assessment_date
    FROM core.fact_humanitarian_needs n
    JOIN latest_hno lh ON n.reference_period_start = lh.max_period
    WHERE n.sector_code = 'INTERSECTORAL'
      AND LOWER(n.category) = 'total'
      AND n.population_status = 'INN'
    GROUP BY n.admin2_code
),
lga_targeted AS (
    -- Targeted Population per LGA
    SELECT 
        n.admin2_code,
        SUM(n.population) AS people_targeted
    FROM core.fact_humanitarian_needs n
    JOIN latest_hno lh ON n.reference_period_start = lh.max_period
    WHERE n.sector_code = 'INTERSECTORAL'
      AND (LOWER(n.category) = 'total' OR n.category ILIKE '%targeted%')
      AND n.population_status = 'TAR'
    GROUP BY n.admin2_code
),
lga_idps AS (
    -- Latest baseline assessment per LGA
    SELECT DISTINCT ON (admin2_code)
        admin2_code,
        population AS idp_count,
        reference_period_start::date AS idp_assessment_date
    FROM core.fact_idps
    ORDER BY admin2_code, reference_period_start DESC
),
lga_presence AS (
    SELECT 
        admin2_code,
        COUNT(DISTINCT org_acronym) AS active_partners_count,
        COUNT(DISTINCT sector_code) AS active_clusters_count
    FROM core.fact_operational_presence
    GROUP BY admin2_code
)
SELECT 
    a2.admin2_code,
    a2.admin2_name AS lga_name,
    a1.admin1_code,
    a1.admin1_name AS state_name,
    a2.latitude,
    a2.longitude,
    a2.geom AS lga_geom,
    
    COALESCE(n.people_in_need, 0) AS people_in_need,
    COALESCE(t.people_targeted, 0) AS people_targeted,
    n.hno_assessment_date,
    COALESCE(i.idp_count, 0) AS idp_count,
    i.idp_assessment_date,
    COALESCE(p.active_partners_count, 0) AS active_partners_count,
    COALESCE(p.active_clusters_count, 0) AS active_clusters_count,
    
    -- Partner Presence Density (orgs per 10k PIN)
    CASE 
        WHEN COALESCE(n.people_in_need, 0) > 0 
        THEN ROUND((COALESCE(p.active_partners_count, 0)::numeric / n.people_in_need) * 10000, 2)
        ELSE 0.00
    END AS partner_presence_density_per_10k_pin,
    
    -- Target Coverage Rate
    CASE 
        WHEN COALESCE(n.people_in_need, 0) > 0 
        THEN ROUND((COALESCE(t.people_targeted, 0)::numeric / n.people_in_need) * 100, 2)
        ELSE 0.00
    END AS target_coverage_pct
FROM core.dim_admin2 a2
JOIN core.dim_admin1 a1 ON a2.admin1_code = a1.admin1_code
LEFT JOIN lga_needs n ON a2.admin2_code = n.admin2_code
LEFT JOIN lga_targeted t ON a2.admin2_code = t.admin2_code
LEFT JOIN lga_idps i ON a2.admin2_code = i.admin2_code
LEFT JOIN lga_presence p ON a2.admin2_code = p.admin2_code;


-- 2. State Humanitarian Profile Mart
DROP VIEW IF EXISTS marts.vw_bi_state_humanitarian_profile CASCADE;

CREATE OR REPLACE VIEW marts.vw_bi_state_humanitarian_profile AS
WITH state_pop AS (
    SELECT 
        admin1_code,
        SUM(population) AS baseline_population
    FROM core.fact_population
    WHERE gender = 'all' AND age_range = 'all'
    GROUP BY admin1_code
),
state_aggregated_summary AS (
    SELECT 
        admin1_code,
        SUM(people_in_need) AS total_people_in_need,
        SUM(people_targeted) AS total_people_targeted,
        SUM(idp_count) AS total_idps,
        COUNT(DISTINCT admin2_code) FILTER (WHERE people_in_need > 0) AS lgas_with_needs_count,
        COUNT(DISTINCT admin2_code) FILTER (WHERE active_partners_count > 0) AS lgas_with_presence_count
    FROM marts.vw_bi_lga_humanitarian_summary
    GROUP BY admin1_code
),
state_distinct_presence AS (
    SELECT 
        a2.admin1_code,
        COUNT(DISTINCT op.org_acronym) AS state_distinct_partners_count,
        COUNT(DISTINCT op.sector_code) AS state_active_clusters_count
    FROM core.fact_operational_presence op
    JOIN core.dim_admin2 a2 ON op.admin2_code = a2.admin2_code
    GROUP BY a2.admin1_code
)
SELECT 
    a1.admin1_code,
    a1.admin1_name AS state_name,
    a1.latitude,
    a1.longitude,
    a1.geom AS state_geom,
    
    COALESCE(sp.baseline_population, 0) AS baseline_population,
    COALESCE(sas.total_people_in_need, 0) AS people_in_need,
    COALESCE(sas.total_people_targeted, 0) AS people_targeted,
    COALESCE(sas.total_idps, 0) AS idp_count,
    
    -- PIN Prevalence Rate (% of state population in need)
    CASE 
        WHEN COALESCE(sp.baseline_population, 0) > 0 
        THEN ROUND((COALESCE(sas.total_people_in_need, 0)::numeric / sp.baseline_population) * 100, 2)
        ELSE 0.00
    END AS pin_prevalence_pct,
    
    COALESCE(sdp.state_distinct_partners_count, 0) AS active_partners_count,
    COALESCE(sdp.state_active_clusters_count, 0) AS active_clusters_count,
    COALESCE(sas.lgas_with_needs_count, 0) AS lgas_with_needs_count,
    COALESCE(sas.lgas_with_presence_count, 0) AS lgas_with_presence_count
FROM core.dim_admin1 a1
LEFT JOIN state_pop sp ON a1.admin1_code = sp.admin1_code
LEFT JOIN state_aggregated_summary sas ON a1.admin1_code = sas.admin1_code
LEFT JOIN state_distinct_presence sdp ON a1.admin1_code = sdp.admin1_code;


-- 3. 3W Operational Presence Matrix Mart
DROP VIEW IF EXISTS marts.vw_bi_3w_operational_matrix CASCADE;

CREATE OR REPLACE VIEW marts.vw_bi_3w_operational_matrix AS
SELECT 
    op.id AS presence_record_id,
    a1.admin1_code,
    a1.admin1_name AS state_name,
    a2.admin2_code,
    a2.admin2_name AS lga_name,
    a2.latitude AS lga_latitude,
    a2.longitude AS lga_longitude,
    
    o.org_acronym,
    COALESCE(o.org_name, op.org_acronym) AS org_name,
    COALESCE(o.org_type_description, 'Other') AS org_type,
    
    s.sector_code,
    COALESCE(s.sector_name, op.sector_code) AS sector_name,
    
    op.reference_period_start,
    op.reference_period_end,
    TO_CHAR(op.reference_period_start, 'YYYY-Q') AS operational_quarter
FROM core.fact_operational_presence op
JOIN core.dim_admin2 a2 ON op.admin2_code = a2.admin2_code
JOIN core.dim_admin1 a1 ON a2.admin1_code = a1.admin1_code
LEFT JOIN core.dim_organization o ON op.org_acronym = o.org_acronym
LEFT JOIN core.dim_sector s ON op.sector_code = s.sector_code;


-- 4. Warehouse & Pipeline Observability Mart
DROP VIEW IF EXISTS marts.vw_bi_pipeline_observability CASCADE;

CREATE OR REPLACE VIEW marts.vw_bi_pipeline_observability AS
SELECT 
    run_id,
    endpoint_name,
    status,
    records_extracted,
    records_inserted,
    records_quarantined,
    api_latency_ms,
    execution_time_seconds,
    error_message,
    created_at AS run_timestamp
FROM audit.pipeline_runs
ORDER BY created_at DESC;
