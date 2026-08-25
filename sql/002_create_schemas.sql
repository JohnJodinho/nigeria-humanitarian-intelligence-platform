-- =============================================================================
-- Phase 1: 002_create_schemas.sql
-- Partition warehouse into staging, core, marts, and audit schemas
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS audit;
