from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class LocationRecord(BaseModel):
    code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1)
    has_hno: Optional[bool] = True
    has_hrp: Optional[bool] = True
    in_gho: Optional[bool] = True
    reference_period_start: Optional[datetime] = None
    reference_period_end: Optional[datetime] = None

class Admin1Record(BaseModel):
    code: str = Field(..., min_length=2, max_length=15)
    name: str = Field(..., min_length=1)
    location_code: str = Field(default="NGA")
    is_unspecified: Optional[bool] = False
    reference_period_start: Optional[datetime] = None
    reference_period_end: Optional[datetime] = None

class Admin2Record(BaseModel):
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=1)
    admin1_code: str = Field(...)
    location_code: str = Field(default="NGA")
    is_unspecified: Optional[bool] = False
    reference_period_start: Optional[datetime] = None
    reference_period_end: Optional[datetime] = None

class OrgRecord(BaseModel):
    acronym: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1)
    org_type_code: Optional[str] = None
    org_type_description: Optional[str] = None

class SectorRecord(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1)

class PopulationRecord(BaseModel):
    admin1_code: str = Field(...)
    year: Optional[int] = None
    gender: Optional[str] = "all"
    age_range: Optional[str] = "all"
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    population: int = Field(..., ge=0)
    reference_period_start: datetime = Field(...)
    reference_period_end: Optional[datetime] = None
    dataset_hdx_id: Optional[str] = None
    resource_hdx_id: Optional[str] = None

    @model_validator(mode="after")
    def populate_year(self):
        if self.year is None and self.reference_period_start:
            self.year = self.reference_period_start.year
        return self

class HumanitarianNeedsRecord(BaseModel):
    admin2_code: str = Field(...)
    sector_code: str = Field(...)
    category: Optional[str] = "inneed"
    population_group: Optional[str] = "all"
    population_status: Optional[str] = "INN"
    gender: Optional[str] = "all"
    age_range: Optional[str] = "all"
    disabled_marker: Optional[str] = "n"
    population: int = Field(..., ge=0)
    reference_period_start: datetime = Field(...)
    reference_period_end: Optional[datetime] = None
    dataset_hdx_id: Optional[str] = None
    resource_hdx_id: Optional[str] = None

class IDPRecord(BaseModel):
    admin2_code: str = Field(...)
    assessment_type: Optional[str] = "BA"
    reporting_round: Optional[int] = None
    operation: Optional[str] = None
    population: int = Field(..., ge=0)
    reference_period_start: datetime = Field(...)
    reference_period_end: Optional[datetime] = None
    dataset_hdx_id: Optional[str] = None
    resource_hdx_id: Optional[str] = None

class OperationalPresenceRecord(BaseModel):
    admin2_code: str = Field(...)
    org_acronym: str = Field(...)
    sector_code: str = Field(...)
    reference_period_start: datetime = Field(...)
    reference_period_end: Optional[datetime] = None
    org_name: Optional[str] = None
    sector_name: Optional[str] = None
    org_type_code: Optional[str] = None
    org_type_description: Optional[str] = None
    dataset_hdx_id: Optional[str] = None
    resource_hdx_id: Optional[str] = None
