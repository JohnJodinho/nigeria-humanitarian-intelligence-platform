import pytest
from datetime import datetime
from src.validation.models import LocationRecord, Admin1Record, Admin2Record, PopulationRecord, HumanitarianNeedsRecord
from src.validation.validator import DataValidator

def test_location_validation():
    valid_record = {"code": "NGA", "name": "Nigeria", "has_hno": True}
    valid, quarantined = DataValidator.validate_batch([valid_record], LocationRecord, "metadata_location")
    assert len(valid) == 1
    assert len(quarantined) == 0

def test_invalid_location_quarantine():
    invalid_record = {"code": "INVALID_CODE_TOO_LONG", "name": "Nigeria"}
    valid, quarantined = DataValidator.validate_batch([invalid_record], LocationRecord, "metadata_location")
    assert len(valid) == 0
    assert len(quarantined) == 1
    assert quarantined[0]["failure_rule_id"] == "SCHEMA_VALIDATION_ERROR"

def test_population_validation():
    pop_record = {
        "admin1_code": "NGA001",
        "year": 2026,
        "gender": "all",
        "age_range": "all",
        "population": 4124970,
        "reference_period_start": "2026-01-01T00:00:00",
        "reference_period_end": "2026-12-31T23:59:59"
    }
    valid, quarantined = DataValidator.validate_batch([pop_record], PopulationRecord, "fact_population")
    assert len(valid) == 1
    assert valid[0]["population"] == 4124970
