import time
import argparse
import logging
from typing import Optional
from src.config.settings import settings
from src.api.hapi_client import HAPIClient
from src.api import endpoints
from src.validation.models import (
    LocationRecord, Admin1Record, Admin2Record, OrgRecord, SectorRecord,
    PopulationRecord, HumanitarianNeedsRecord, IDPRecord, OperationalPresenceRecord
)
from src.validation.validator import DataValidator
from src.transformation.transformer import DataTransformer
from src.database.loader import DatabaseLoader
from src.database.audit_logger import AuditLogger
from src.geospatial.spatial_processor import SpatialProcessor

logging.basicConfig(level=settings.pipeline_log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("pipeline_orchestrator")

class PipelineOrchestrator:
    def __init__(self):
        self.client = HAPIClient()
        self.loader = DatabaseLoader()
        self.audit = AuditLogger()
        self.spatial = SpatialProcessor()

    def run_all(self, country_code: str = "NGA"):
        start_time = time.time()
        logger.info("=" * 65)
        logger.info(f"STARTING N-HIP DATA PIPELINE EXECUTION FOR {country_code}")
        logger.info("=" * 65)

        # ---------------------------------------------------------------------
        # 1. METADATA & DIMENSIONS
        # ---------------------------------------------------------------------
        logger.info("\n>>> [1/9] Ingesting Location (Country) Dimension...")
        self._ingest_endpoint(
            name="metadata_location",
            endpoint=endpoints.EP_METADATA_LOCATION,
            model_cls=LocationRecord,
            transform_fn=DataTransformer.transform_locations,
            upsert_fn=self.loader.upsert_locations,
            params={"code": country_code}
        )

        logger.info("\n>>> [2/9] Ingesting Admin1 (States) Dimension...")
        self._ingest_endpoint(
            name="metadata_admin1",
            endpoint=endpoints.EP_METADATA_ADMIN1,
            model_cls=Admin1Record,
            transform_fn=DataTransformer.transform_admin1,
            upsert_fn=self.loader.upsert_admin1
        )

        logger.info("\n>>> [3/9] Ingesting Admin2 (LGAs) Dimension...")
        self._ingest_endpoint(
            name="metadata_admin2",
            endpoint=endpoints.EP_METADATA_ADMIN2,
            model_cls=Admin2Record,
            transform_fn=DataTransformer.transform_admin2,
            upsert_fn=self.loader.upsert_admin2
        )

        logger.info("\n>>> [4/9] Ingesting Organization Master Dimension...")
        self._ingest_endpoint(
            name="metadata_org",
            endpoint=endpoints.EP_METADATA_ORG,
            model_cls=OrgRecord,
            transform_fn=DataTransformer.transform_orgs,
            upsert_fn=self.loader.upsert_orgs,
            params={"limit": 10000}
        )

        logger.info("\n>>> [5/9] Ingesting Sector / Cluster Dimension...")
        self._ingest_endpoint(
            name="metadata_sector",
            endpoint=endpoints.EP_METADATA_SECTOR,
            model_cls=SectorRecord,
            transform_fn=DataTransformer.transform_sectors,
            upsert_fn=self.loader.upsert_sectors,
            params={"limit": 10000}
        )

        # ---------------------------------------------------------------------
        # 2. GEOSPATIAL REFERENCE SEEDING
        # ---------------------------------------------------------------------
        logger.info("\n>>> [*] Seeding Geospatial PostGIS Boundaries & Centroids...")
        try:
            geom_stats = self.spatial.process_and_seed_boundaries()
            logger.info(f"Geospatial Seeding Successful: {geom_stats}")
        except Exception as e:
            logger.warning(f"Spatial seeding skipped or encountered warning: {e}")

        # ---------------------------------------------------------------------
        # 3. FACT DATASETS
        # ---------------------------------------------------------------------
        logger.info("\n>>> [6/9] Ingesting Baseline Population...")
        self._ingest_endpoint(
            name="fact_population",
            endpoint=endpoints.EP_BASELINE_POPULATION,
            model_cls=PopulationRecord,
            transform_fn=DataTransformer.transform_population,
            upsert_fn=self.loader.upsert_population
        )

        logger.info("\n>>> [7/9] Ingesting Humanitarian Needs (PIN)...")
        self._ingest_endpoint(
            name="fact_humanitarian_needs",
            endpoint=endpoints.EP_HUMANITARIAN_NEEDS,
            model_cls=HumanitarianNeedsRecord,
            transform_fn=DataTransformer.transform_needs,
            upsert_fn=self.loader.upsert_humanitarian_needs
        )

        logger.info("\n>>> [8/9] Ingesting IDPs / Displacement...")
        self._ingest_endpoint(
            name="fact_idps",
            endpoint=endpoints.EP_IDPS,
            model_cls=IDPRecord,
            transform_fn=DataTransformer.transform_idps,
            upsert_fn=self.loader.upsert_idps
        )

        logger.info("\n>>> [9/9] Ingesting Operational Presence (3W)...")
        self._ingest_endpoint(
            name="fact_operational_presence",
            endpoint=endpoints.EP_OPERATIONAL_PRESENCE,
            model_cls=OperationalPresenceRecord,
            transform_fn=DataTransformer.transform_operational_presence,
            upsert_fn=self.loader.upsert_operational_presence
        )

        total_runtime = round(time.time() - start_time, 2)
        logger.info("=" * 65)
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY IN {total_runtime} SECONDS")
        logger.info("=" * 65)

    def _ingest_endpoint(
        self,
        name: str,
        endpoint: str,
        model_cls,
        transform_fn,
        upsert_fn,
        params: Optional[dict] = None
    ):
        t0 = time.time()
        try:
            raw_records = self.client.fetch_paginated(endpoint, params=params)
            latency_ms = round((time.time() - t0) * 1000)

            valid, quarantined = DataValidator.validate_batch(raw_records, model_cls, name)
            transformed = transform_fn(valid)
            inserted_count = upsert_fn(transformed)

            run_id = self.audit.log_run(
                endpoint_name=name,
                status="WARNING" if quarantined else "SUCCESS",
                records_extracted=len(raw_records),
                records_inserted=inserted_count,
                records_quarantined=len(quarantined),
                api_latency_ms=latency_ms,
                execution_time_seconds=round(time.time() - t0, 2)
            )
            if quarantined:
                self.audit.log_quarantine_batch(quarantined, run_id=run_id)

            logger.info(f"Completed {name}: {len(raw_records)} extracted, {inserted_count} upserted, {len(quarantined)} quarantined.")
        except Exception as e:
            logger.error(f"Error during {name} ingestion: {e}", exc_info=True)
            self.audit.log_run(
                endpoint_name=name,
                status="FAILURE",
                error_message=str(e),
                execution_time_seconds=round(time.time() - t0, 2)
            )
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nigeria Humanitarian Intelligence Platform ETL Pipeline")
    parser.add_argument("--country", default="NGA", help="ISO3 Country Code (default: NGA)")
    args = parser.parse_args()

    orchestrator = PipelineOrchestrator()
    orchestrator.run_all(country_code=args.country)
