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
            data = []
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Fetching {endpoint} [offset={query_params['offset']}, limit={query_params['limit']}]")
                    start_t = time.time()
                    resp = self.session.get(url, params=query_params, timeout=45)
                    latency = round((time.time() - start_t) * 1000)

                    if resp.status_code == 429:
                        wait = 2 ** attempt * 2
                        logger.warning(f"Rate limited (429). Retrying in {wait}s...")
                        time.sleep(wait)
                        continue

                    resp.raise_for_status()
                    payload = resp.json()
                    data = payload.get("data", [])
                    logger.debug(f"Received {len(data)} records in {latency}ms")
                    break
                except (requests.RequestException, ValueError) as e:
                    if attempt == max_retries:
                        logger.error(f"Fatal error fetching {endpoint} after {max_retries} attempts: {e}")
                        raise
                    wait = 2 ** attempt
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)

            if not data:
                break

            all_records.extend(data)
            logger.info(f"Retrieved {len(data)} records from {endpoint} (Cumulative: {len(all_records)})")

            if len(data) < query_params["limit"] or (max_records and len(all_records) >= max_records):
                break

            query_params["offset"] += len(data)

        return all_records[:max_records] if max_records else all_records
