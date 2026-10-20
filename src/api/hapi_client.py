import base64
import time
import logging
from typing import Dict, Any, List, Optional
import requests
from src.config.settings import settings

logging.basicConfig(level=settings.pipeline_log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("hapi_client")

class HAPIClient:
    def __init__(
        self, 
        app_name: Optional[str] = None, 
        email: Optional[str] = None, 
        base_url: Optional[str] = None
    ):
        self.app_name = app_name or settings.hdx_hapi_app_name
        self.email = email or settings.hdx_hapi_email
        self.base_url = (base_url or settings.hdx_hapi_base_url).rstrip("/")
        
        # Base64 encoded App Identifier header
        raw_id = f"{self.app_name}:{self.email}"
        self.app_id = base64.b64encode(raw_id.encode("utf-8")).decode("utf-8")
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-HDX-HAPI-APP-IDENTIFIER": self.app_id,
            "Accept": "application/json",
            "User-Agent": f"N-HIP-Pipeline/1.0 ({self.app_name})"
        })
        logger.info(f"Initialized HAPIClient for application '{self.app_name}'")

    def fetch_paginated(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches all records from a given HAPI v2 endpoint with automatic pagination
        and exponential backoff retry handling.
        """
        url = f"{self.base_url}{endpoint}"
        query_params = {
            "location_code": settings.target_country_code,
            "output_format": "json",
            "limit": settings.max_page_limit,
            "offset": 0
        }
        if params:
            query_params.update(params)

        all_records = []
        max_retries = 3
        
        while True:
            data = self._fetch_page(url, endpoint, query_params, max_retries)

            if not data:
                break

            all_records.extend(data)
            logger.info(f"Retrieved {len(data)} records from {endpoint} (Cumulative: {len(all_records)})")

            if self._should_stop_pagination(data, query_params["limit"], max_records, len(all_records)):
                break

            query_params["offset"] += len(data)

        return all_records[:max_records] if max_records else all_records

    def _fetch_page(
        self,
        url: str,
        endpoint: str,
        query_params: Dict[str, Any],
        max_retries: int,
    ) -> List[Dict[str, Any]]:
        """Fetch one HAPI page with bounded retries."""
        for attempt in range(1, max_retries + 1):
            try:
                return self._request_page(url, endpoint, query_params, attempt, max_retries)
            except (requests.RequestException, ValueError) as error:
                if attempt == max_retries:
                    logger.error(
                        f"Fatal error fetching {endpoint} after {max_retries} attempts: {error}"
                    )
                    raise
                wait = 2 ** attempt
                logger.warning(f"Attempt {attempt} failed: {error}. Retrying in {wait}s...")
                time.sleep(wait)
        return []

    def _request_page(
        self,
        url: str,
        endpoint: str,
        query_params: Dict[str, Any],
        attempt: int,
        max_retries: int,
    ) -> List[Dict[str, Any]]:
        """Issue one HAPI request and decode its records."""
        logger.info(
            f"Fetching {endpoint} "
            f"[offset={query_params['offset']}, limit={query_params['limit']}]"
        )
        start_t = time.time()
        response = self.session.get(url, params=query_params, timeout=45)
        latency = round((time.time() - start_t) * 1000)

        if response.status_code == 429:
            if attempt == max_retries:
                response.raise_for_status()
            wait = 2 ** attempt * 2
            logger.warning(f"Rate limited (429). Retrying in {wait}s...")
            time.sleep(wait)
            raise requests.RequestException("HAPI rate limit response")

        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        logger.debug(f"Received {len(data)} records in {latency}ms")
        return data

    @staticmethod
    def _should_stop_pagination(
        page: List[Dict[str, Any]],
        page_limit: int,
        max_records: Optional[int],
        total_records: int,
    ) -> bool:
        """Return whether the current page completes the requested fetch."""
        return len(page) < page_limit or bool(max_records and total_records >= max_records)
