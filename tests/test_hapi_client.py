import pytest
from unittest.mock import Mock, patch

import requests

from src.api.hapi_client import HAPIClient

def test_client_header_generation():
    client = HAPIClient(app_name="TestApp", email="test@example.com")
    header_val = client.session.headers.get("X-HDX-HAPI-APP-IDENTIFIER")
    assert header_val is not None
    assert len(header_val) > 0


def test_fetch_paginated_collects_multiple_pages():
    client = HAPIClient(app_name="TestApp", email="test@example.com")
    first_page = Mock(status_code=200)
    first_page.json.return_value = {"data": [{"id": 1}, {"id": 2}]}
    second_page = Mock(status_code=200)
    second_page.json.return_value = {"data": [{"id": 3}]}
    client.session.get = Mock(side_effect=[first_page, second_page])

    with patch("src.api.hapi_client.settings.max_page_limit", 2):
        records = client.fetch_paginated("/test")

    assert records == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert client.session.get.call_count == 2


def test_fetch_paginated_raises_after_rate_limit_retries():
    client = HAPIClient(app_name="TestApp", email="test@example.com")
    rate_limited = Mock(status_code=429)
    rate_limited.raise_for_status.side_effect = requests.HTTPError("rate limited")
    client.session.get = Mock(return_value=rate_limited)

    with patch("src.api.hapi_client.time.sleep"):
        with patch("src.api.hapi_client.settings.max_page_limit", 2):
            with pytest.raises(requests.HTTPError):
                client.fetch_paginated("/test")
