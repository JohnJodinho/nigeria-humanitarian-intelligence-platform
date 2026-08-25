import pytest
from src.api.hapi_client import HAPIClient

def test_client_header_generation():
    client = HAPIClient(app_name="TestApp", email="test@example.com")
    header_val = client.session.headers.get("X-HDX-HAPI-APP-IDENTIFIER")
    assert header_val is not None
    assert len(header_val) > 0
