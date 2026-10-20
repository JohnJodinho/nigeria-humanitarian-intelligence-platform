import pytest
from src.transformation.transformer import DataTransformer

def test_transform_admin1_deduplication():
    records = [
        {"code": "NGA001", "name": "Abia", "location_code": "NGA"},
        {"code": "NGA001", "name": "Abia State", "location_code": "NGA"},
        {"code": "NGA002", "name": "Adamawa", "location_code": "NGA"}
    ]
    transformed = DataTransformer.transform_admin1(records)
    assert len(transformed) == 2
    assert transformed[0]["admin1_code"] == "NGA001"
    assert transformed[1]["admin1_code"] == "NGA002"

def test_transform_orgs_cleaning():
    records = [
        {"acronym": "  UNICEF  ", "name": "United Nations Children's Fund"},
        {"acronym": "UNICEF", "name": "UN Children's Fund"}
    ]
    transformed = DataTransformer.transform_orgs(records)
    assert len(transformed) == 1
    assert transformed[0]["org_acronym"] == "UNICEF"


def test_transform_humanitarian_needs_normalizes_categories():
    records = [
        {
            "admin2_code": "NGA001001",
            "sector_code": "INTERSECTORAL",
            "category": " total ",
            "population_status": "INN",
            "reference_period_start": "2026-01-01T00:00:00",
            "population": 100,
        },
        {
            "admin2_code": "NGA001001",
            "sector_code": "INTERSECTORAL",
            "category": "Total",
            "population_status": "INN",
            "reference_period_start": "2026-01-01T00:00:00",
            "population": 100,
        },
    ]

    transformed = DataTransformer.transform_humanitarian_needs(records)

    assert len(transformed) == 1
    assert transformed[0]["category"] == "Total"
