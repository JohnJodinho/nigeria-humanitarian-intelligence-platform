import json
import logging
from typing import Dict, Any, List, Optional
import psycopg2
from src.config.settings import settings

logger = logging.getLogger("audit_logger")

class AuditLogger:
    def __init__(self):
        self.db_url = settings.get_db_connection_url()

    def log_run(
        self,
        endpoint_name: str,
        status: str,
        records_extracted: int = 0,
        records_inserted: int = 0,
        records_updated: int = 0,
        records_quarantined: int = 0,
        api_latency_ms: Optional[int] = None,
        execution_time_seconds: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> Optional[str]:
        query = """
            INSERT INTO audit.pipeline_runs (
                endpoint_name, status, records_extracted, records_inserted,
                records_updated, records_quarantined, api_latency_ms,
                execution_time_seconds, error_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING run_id;
        """
        try:
            conn = psycopg2.connect(self.db_url)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(query, (
                endpoint_name, status, records_extracted, records_inserted,
                records_updated, records_quarantined, api_latency_ms,
                execution_time_seconds, error_message
            ))
            run_id = str(cur.fetchone()[0])
            cur.close()
            conn.close()
            return run_id
        except Exception as e:
            logger.error(f"Failed logging pipeline run: {e}")
            return None

    def log_quarantine_batch(self, quarantined_records: List[Dict[str, Any]], run_id: Optional[str] = None):
        if not quarantined_records:
            return

        query = """
            INSERT INTO audit.pipeline_quarantine_log (
                run_id, endpoint_name, record_payload, failure_rule_id, failure_reason
            ) VALUES (%s, %s, %s, %s, %s);
        """
        try:
            conn = psycopg2.connect(self.db_url)
            conn.autocommit = True
            cur = conn.cursor()
            for q in quarantined_records:
                cur.execute(query, (
                    run_id,
                    q.get("endpoint_name"),
                    json.dumps(q.get("record_payload", {})),
                    q.get("failure_rule_id"),
                    q.get("failure_reason")
                ))
            cur.close()
            conn.close()
            logger.info(f"Logged {len(quarantined_records)} records to audit.pipeline_quarantine_log")
        except Exception as e:
            logger.error(f"Failed logging quarantine records: {e}")
