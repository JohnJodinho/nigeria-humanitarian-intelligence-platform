"""Data transformation module for N-HIP."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Neutralize NaN/inf values and replace with None for psycopg2/PostgreSQL."""
    if df.empty:
        return df
    return df.astype(object).where(pd.notnull(df), None)


class DataTransformer:
    transform_orgs = staticmethod(lambda records: DataTransformer.transform_organizations(records))
    """Harmonizes and standardizes raw HAPI payloads."""

    @staticmethod
    def transform_locations(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform location records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df = df.rename(columns={"code": "location_code", "name": "location_name"})
        df["has_hno"] = df.get("has_hno", False).fillna(False)
        df["has_hrp"] = df.get("has_hrp", False).fillna(False)
        df["in_gho"] = df.get("in_gho", False).fillna(False)
        df = df.drop_duplicates(subset=["location_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_admin1(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform admin1 (State) records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df = df.rename(columns={"code": "admin1_code", "name": "admin1_name"})
        df = df.drop_duplicates(subset=["admin1_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_admin2(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform admin2 (LGA) records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df = df.rename(columns={"code": "admin2_code", "name": "admin2_name"})
        df = df.drop_duplicates(subset=["admin2_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_organizations(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform organization records with uppercase acronym standardization."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df = df.rename(columns={
            "acronym": "org_acronym",
            "name": "org_name",
            "org_type_code": "org_type_code",
            "org_type_description": "org_type_description"
        })
        df["org_acronym"] = df["org_acronym"].astype(str).str.strip().str.upper()
        df = df.drop_duplicates(subset=["org_acronym"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_sectors(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform sector records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df = df.rename(columns={"code": "sector_code", "name": "sector_name"})
        df = df.drop_duplicates(subset=["sector_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_population(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform baseline population records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        if "year" not in df.columns or df["year"].isnull().all():
            if "reference_period_start" in df.columns:
                df["year"] = pd.to_datetime(df["reference_period_start"]).dt.year
            else:
                df["year"] = datetime.now().year
        df["gender"] = df.get("gender", "all").fillna("all")
        df["age_range"] = df.get("age_range", "all").fillna("all")
        df = df.drop_duplicates(subset=["admin1_code", "year", "gender", "age_range"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_humanitarian_needs(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform humanitarian needs records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df = df.drop_duplicates(subset=["admin2_code", "sector_code", "category", "reference_period_start"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_idps(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform IDP records."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df["assessment_type"] = df.get("assessment_type", "BA").fillna("BA")
        df = df.drop_duplicates(subset=["admin2_code", "assessment_type", "reference_period_start"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_operational_presence(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform 3W operational presence records with uppercase acronym standardization."""
        if not raw_records:
            return []
        df = pd.DataFrame(raw_records)
        df["org_acronym"] = df["org_acronym"].astype(str).str.strip().str.upper()
        df = df.drop_duplicates(subset=["admin2_code", "org_acronym", "sector_code", "reference_period_start"])
        return clean_dataframe(df).to_dict(orient="records")

