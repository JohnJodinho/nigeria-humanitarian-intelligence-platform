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
