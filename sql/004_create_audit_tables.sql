-- =============================================================================
-- Phase 1: 004_create_audit_tables.sql
-- Observability, Ingestion Logs, and Quarantine Storage
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    run_id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_name           VARCHAR(100) NOT NULL,
    status                  VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'WARNING', 'FAILURE')),
    records_extracted       INT NOT NULL DEFAULT 0,
    records_inserted        INT NOT NULL DEFAULT 0,
    records_updated         INT NOT NULL DEFAULT 0,
    records_quarantined     INT NOT NULL DEFAULT 0,
    api_latency_ms          INT,
    execution_time_seconds  NUMERIC(8,2),
    error_message           TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_time ON audit.pipeline_runs(created_at DESC);

CREATE TABLE IF NOT EXISTS audit.pipeline_quarantine_log (
    quarantine_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id                  UUID REFERENCES audit.pipeline_runs(run_id) ON DELETE SET NULL,
    endpoint_name           VARCHAR(100) NOT NULL,
    record_payload          JSONB NOT NULL,
    failure_rule_id         VARCHAR(50) NOT NULL,
    failure_reason          TEXT NOT NULL,
    quarantined_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_quarantine_rule ON audit.pipeline_quarantine_log(failure_rule_id);
CREATE INDEX IF NOT EXISTS idx_quarantine_time ON audit.pipeline_quarantine_log(quarantined_at DESC);
