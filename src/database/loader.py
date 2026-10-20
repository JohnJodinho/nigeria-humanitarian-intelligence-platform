import logging
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import execute_values
from src.config.settings import settings

logger = logging.getLogger("db_loader")

class DatabaseLoader:
    def __init__(self):
        self.db_url = settings.get_db_connection_url()

    def upsert_locations(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.dim_location (
                location_code, location_name, has_hno, has_hrp, in_gho,
                reference_period_start, reference_period_end
            ) VALUES %s
            ON CONFLICT (location_code) DO UPDATE SET
                location_name = EXCLUDED.location_name,
                has_hno = EXCLUDED.has_hno,
                has_hrp = EXCLUDED.has_hrp,
                in_gho = EXCLUDED.in_gho,
                updated_at = NOW();
        """
        tuples = [
            (
                r["location_code"], r["location_name"], r.get("has_hno", True),
                r.get("has_hrp", True), r.get("in_gho", True),
                r.get("reference_period_start"), r.get("reference_period_end")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0,))
        return self._execute_bulk(query, tuples)

    def upsert_admin1(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.dim_admin1 (
                admin1_code, admin1_name, location_code, is_unspecified,
                reference_period_start, reference_period_end
            ) VALUES %s
            ON CONFLICT (admin1_code) DO UPDATE SET
                admin1_name = EXCLUDED.admin1_name,
                is_unspecified = EXCLUDED.is_unspecified,
                updated_at = NOW();
        """
        tuples = [
            (
                r["admin1_code"], r["admin1_name"], r.get("location_code", "NGA"),
                r.get("is_unspecified", False), r.get("reference_period_start"),
                r.get("reference_period_end")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0,))
        return self._execute_bulk(query, tuples)

    def upsert_admin2(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.dim_admin2 (
                admin2_code, admin2_name, admin1_code, location_code, is_unspecified,
                reference_period_start, reference_period_end
            ) VALUES %s
            ON CONFLICT (admin2_code) DO UPDATE SET
                admin2_name = EXCLUDED.admin2_name,
                admin1_code = EXCLUDED.admin1_code,
                is_unspecified = EXCLUDED.is_unspecified,
                updated_at = NOW();
        """
        tuples = [
            (
                r["admin2_code"], r["admin2_name"], r["admin1_code"],
                r.get("location_code", "NGA"), r.get("is_unspecified", False),
                r.get("reference_period_start"), r.get("reference_period_end")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0,))
        return self._execute_bulk(query, tuples)

    def upsert_orgs(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.dim_organization (
                org_acronym, org_name, org_type_code, org_type_description
            ) VALUES %s
            ON CONFLICT (org_acronym) DO UPDATE SET
                org_name = EXCLUDED.org_name,
                org_type_code = EXCLUDED.org_type_code,
                org_type_description = EXCLUDED.org_type_description,
                updated_at = NOW();
        """
        tuples = [
            (
                r["org_acronym"], r["org_name"],
                r.get("org_type_code"), r.get("org_type_description")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0,))
        return self._execute_bulk(query, tuples)

    def upsert_sectors(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.dim_sector (sector_code, sector_name)
            VALUES %s
            ON CONFLICT (sector_code) DO UPDATE SET
                sector_name = EXCLUDED.sector_name,
                updated_at = NOW();
        """
        tuples = [(r["sector_code"], r["sector_name"]) for r in records]
        tuples = self._deduplicate_tuples(tuples, (0,))
        return self._execute_bulk(query, tuples)

    def upsert_population(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.fact_population (
                admin1_code, year, gender, age_range, min_age, max_age,
                population, reference_period_start, reference_period_end,
                dataset_hdx_id, resource_hdx_id
            ) VALUES %s
            ON CONFLICT (admin1_code, year, gender, age_range, reference_period_start) 
            DO UPDATE SET
                population = EXCLUDED.population,
                extracted_at = NOW();
        """
        tuples = [
            (
                r["admin1_code"], r["year"], r["gender"], r["age_range"],
                r.get("min_age"), r.get("max_age"), r["population"],
                r["reference_period_start"], r.get("reference_period_end") or r["reference_period_start"],
                r.get("dataset_hdx_id"), r.get("resource_hdx_id")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0, 1, 2, 3, 4))
        return self._execute_bulk(query, tuples)

    def upsert_humanitarian_needs(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        
        # Ensure any missing sectors exist in dim_sector to avoid FK errors
        sector_codes = {r["sector_code"] for r in records}
        self._ensure_sectors_exist(sector_codes)

        query = """
            INSERT INTO core.fact_humanitarian_needs (
                admin2_code, sector_code, category, population_group, population_status,
                gender, age_range, disabled_marker, population,
                reference_period_start, reference_period_end,
                dataset_hdx_id, resource_hdx_id
            ) VALUES %s
            ON CONFLICT (
                admin2_code, sector_code, category, population_group, 
                gender, age_range, disabled_marker, reference_period_start
            ) DO UPDATE SET
                population = EXCLUDED.population,
                extracted_at = NOW();
        """
        tuples = [
            (
                r["admin2_code"], r["sector_code"], r.get("category", "inneed"),
                r.get("population_group", "all"), r.get("population_status", "INN"),
                r.get("gender", "all"), r.get("age_range", "all"), r.get("disabled_marker", "n"),
                r["population"], r["reference_period_start"],
                r.get("reference_period_end") or r["reference_period_start"], r.get("dataset_hdx_id"),
                r.get("resource_hdx_id")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0, 1, 2, 3, 4, 5, 6, 7))
        return self._execute_bulk(query, tuples)

    def upsert_idps(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        query = """
            INSERT INTO core.fact_idps (
                admin2_code, assessment_type, reporting_round, operation,
                population, reference_period_start, reference_period_end,
                dataset_hdx_id, resource_hdx_id
            ) VALUES %s
            ON CONFLICT (admin2_code, assessment_type, reference_period_start)
            DO UPDATE SET
                population = EXCLUDED.population,
                extracted_at = NOW();
        """
        tuples = [
            (
                r["admin2_code"], r.get("assessment_type", "BA"), r.get("reporting_round"),
                r.get("operation"), r["population"], r["reference_period_start"],
                r.get("reference_period_end") or r["reference_period_start"], r.get("dataset_hdx_id"),
                r.get("resource_hdx_id")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0, 1, 2))
        return self._execute_bulk(query, tuples)

    def upsert_operational_presence(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        
        # Ensure any missing orgs or sectors exist to satisfy foreign keys
        orgs = {(r["org_acronym"], r.get("org_name") or r["org_acronym"], r.get("org_type_code"), r.get("org_type_description")) for r in records}
        self._ensure_orgs_exist(orgs)
        sector_codes = {r["sector_code"] for r in records}
        self._ensure_sectors_exist(sector_codes)

        query = """
            INSERT INTO core.fact_operational_presence (
                admin2_code, org_acronym, sector_code,
                reference_period_start, reference_period_end,
                dataset_hdx_id, resource_hdx_id
            ) VALUES %s
            ON CONFLICT (admin2_code, org_acronym, sector_code, reference_period_start)
            DO NOTHING;
        """
        tuples = [
            (
                r["admin2_code"], r["org_acronym"], r["sector_code"],
                r["reference_period_start"], r.get("reference_period_end") or r["reference_period_start"],
                r.get("dataset_hdx_id"), r.get("resource_hdx_id")
            )
            for r in records
        ]
        tuples = self._deduplicate_tuples(tuples, (0, 1, 2, 3))
        return self._execute_bulk(query, tuples)

    def _ensure_sectors_exist(self, sector_codes: set):
        if not sector_codes:
            return
        conn = psycopg2.connect(self.db_url)
        conn.autocommit = True
        cur = conn.cursor()
        tuples = [(sc, sc) for sc in sector_codes if sc]
        execute_values(cur, """
            INSERT INTO core.dim_sector (sector_code, sector_name)
            VALUES %s
            ON CONFLICT (sector_code) DO NOTHING;
        """, tuples)
        cur.close()
        conn.close()

    def _ensure_orgs_exist(self, org_tuples: set):
        if not org_tuples:
            return
        conn = psycopg2.connect(self.db_url)
        conn.autocommit = True
        cur = conn.cursor()
        execute_values(cur, """
            INSERT INTO core.dim_organization (org_acronym, org_name, org_type_code, org_type_description)
            VALUES %s
            ON CONFLICT (org_acronym) DO NOTHING;
        """, self._deduplicate_tuples(list(org_tuples), (0,)))
        cur.close()
        conn.close()

    def _execute_bulk(self, query: str, tuples: list, page_size: int = 5000) -> int:
        conn = psycopg2.connect(self.db_url)
        conn.autocommit = True
        cur = conn.cursor()
        total_rows = 0
        for i in range(0, len(tuples), page_size):
            batch = tuples[i:i + page_size]
            execute_values(cur, query, batch)
            total_rows += len(batch)
        cur.close()
        conn.close()
        return total_rows

    @staticmethod
    def _deduplicate_tuples(
        tuples: list,
        conflict_indexes: tuple[int, ...],
    ) -> list:
        """Remove duplicate rows for a database conflict key before bulk upsert."""
        seen = set()
        deduplicated = []
        for row in tuples:
            conflict_key = tuple(row[index] for index in conflict_indexes)
            if conflict_key not in seen:
                seen.add(conflict_key)
                deduplicated.append(row)
        return deduplicated
