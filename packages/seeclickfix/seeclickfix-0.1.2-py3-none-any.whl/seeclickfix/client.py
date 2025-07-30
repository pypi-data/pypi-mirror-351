import logging

import aiohttp

from .adapter import RestAdapter
from .models.issue import RootObject, Status


class SeeClickFixClient:
    """Client for interacting with the SeeClickFix API"""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self._session = None
        self.adapter = RestAdapter(hostname="seeclickfix.com", base="api/v2")

    @property
    def session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.adapter.session = self.session
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if not self.session:
            return

        await self.session.close()
        self.session = None

    async def get_issues(
        self,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        status: list[Status],
        page: int = 1,
    ) -> RootObject:
        """Get a list of issues"""
        params = {
            "min_lat": min_lat,
            "min_lng": min_lng,
            "max_lat": max_lat,
            "max_lng": max_lng,
            "status": ",".join([s.value.lower() for s in status]),
            "fields[issue]": "id,status,summary,description,lat,lng,address,created_at,url,media",
            "page": page,
        }

        result = await self.adapter.get(self.session, "issues", ep_params=params)
        return RootObject(**result.data)
