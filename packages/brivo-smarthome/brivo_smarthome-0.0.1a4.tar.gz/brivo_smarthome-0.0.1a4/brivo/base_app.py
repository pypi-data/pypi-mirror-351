from abc import ABC
from os import getenv

import httpx

from brivo.models.auth import BrivoAuth
from brivo.models.request_factory import BrivoRequests


class BaseBrivoClient(ABC):
    def __init__(self, username: str = None, password: str = None, base_url: str = None, company_id: int | None = None):
        username = username or getenv('BRIVO_USERNAME')
        password = password or getenv('BRIVO_PASSWORD')
        self.base_url = base_url.rstrip('/') if base_url else 'https://api.smarthome.brivo.com'
        self._company_id: int | None = company_id
        self.client: httpx.Client | httpx.AsyncClient
        self._requests: BrivoRequests = BrivoRequests(self.base_url)
        self.auth: BrivoAuth = BrivoAuth(self.base_url, username, password)

    def company_alerts(self, company_id: int, page: int) -> dict:
        """
        Fetches alerts for a given company and page from the Brivo SmartHome API.

        Args:
            company_id (int): The ID of the company to fetch alerts for.
            page (int): The page number of paginated results.

        Returns:
            dict: A dictionary with the following structure:
                {
                    "count": int,               # Total number of alerts available
                    "next": str or None,        # URL to the next page of results
                    "previous": str or None,    # URL to the previous page
                    "results": [                # List of alert objects
                        {
                            "message": str,
                            "device": str or None,
                            "deviceId": int,
                            "property": str,
                            "propertyId": int,
                            "type": str,         # "device" or "gateway"
                            "timestamp": str,    # Format: "YYYY-MM-DD HH:MM:SS"
                            "timezone": str      # e.g. "US/Pacific"
                        },
                        ...
                    ]
                }
        """
        endpoint = f'/v3/company/{company_id}/alert'
        query_params = {'page': page}

        return self._request('GET', endpoint, query_params=query_params)

