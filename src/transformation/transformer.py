import logging
from typing import List, Dict, Any
import numpy as np
import pandas as pd

logger = logging.getLogger("transformer")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces NaN/NaT with None so psycopg2 sends clean NULLs to PostgreSQL."""
    return df.astype(object).where(pd.notnull(df), None)

class DataTransformer:
    @staticmethod
    def transform_locations(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df = df.rename(columns={"code": "location_code", "name": "location_name"})
        df["location_code"] = df["location_code"].str.upper().str.strip()
        df = df.drop_duplicates(subset=["location_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_admin1(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df = df.rename(columns={"code": "admin1_code", "name": "admin1_name"})
        df["admin1_code"] = df["admin1_code"].str.upper().str.strip()
        df["location_code"] = df.get("location_code", "NGA").str.upper().str.strip()
        df = df.drop_duplicates(subset=["admin1_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_admin2(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df = df.rename(columns={"code": "admin2_code", "name": "admin2_name"})
        df["admin2_code"] = df["admin2_code"].str.upper().str.strip()
        df["admin1_code"] = df["admin1_code"].str.upper().str.strip()
        df["location_code"] = df.get("location_code", "NGA").str.upper().str.strip()
        df = df.drop_duplicates(subset=["admin2_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_orgs(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df = df.rename(columns={"acronym": "org_acronym", "name": "org_name"})
        df["org_acronym"] = df["org_acronym"].str.strip()
        df = df.drop_duplicates(subset=["org_acronym"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_sectors(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df = df.rename(columns={"code": "sector_code", "name": "sector_name"})
        df["sector_code"] = df["sector_code"].str.upper().str.strip()
        df = df.drop_duplicates(subset=["sector_code"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_population(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df["admin1_code"] = df["admin1_code"].str.upper().str.strip()
        df["gender"] = df.get("gender", "all").fillna("all").str.lower().str.strip()
        df["age_range"] = df.get("age_range", "all").fillna("all").str.strip()
        df["year"] = pd.to_datetime(df["reference_period_start"]).dt.year
        df = df.drop_duplicates(subset=["admin1_code", "year", "gender", "age_range", "reference_period_start"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_needs(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df["admin2_code"] = df["admin2_code"].str.upper().str.strip()
        df["sector_code"] = df["sector_code"].str.upper().str.strip()
        df["category"] = df.get("category", "inneed").fillna("inneed").str.strip()
        df["population_group"] = df.get("population_group", "all").fillna("all").str.strip()
        df["gender"] = df.get("gender", "all").fillna("all").str.strip()
        df["age_range"] = df.get("age_range", "all").fillna("all").str.strip()
        df["disabled_marker"] = df.get("disabled_marker", "n").fillna("n").str.strip()
        
        subset = [
            "admin2_code", "sector_code", "category", "population_group", 
            "gender", "age_range", "disabled_marker", "reference_period_start"
        ]
        df = df.drop_duplicates(subset=subset)
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_idps(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df["admin2_code"] = df["admin2_code"].str.upper().str.strip()
        df["assessment_type"] = df.get("assessment_type", "BA").fillna("BA").str.strip()
        df = df.drop_duplicates(subset=["admin2_code", "assessment_type", "reference_period_start"])
        return clean_dataframe(df).to_dict(orient="records")

    @staticmethod
    def transform_operational_presence(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if df.empty:
            return []
        df["admin2_code"] = df["admin2_code"].str.upper().str.strip()
        df["org_acronym"] = df["org_acronym"].str.strip()
        df["sector_code"] = df["sector_code"].str.upper().str.strip()
        df = df.drop_duplicates(subset=["admin2_code", "org_acronym", "sector_code", "reference_period_start"])
        return clean_dataframe(df).to_dict(orient="records")
