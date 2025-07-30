from typing import List, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import InstrumentDto


class InstrumentsClient:
    """Client for instrument-related endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_instruments_raw(
        self,
        enabled_only: bool = True,
        fetch_characteristics: bool = True,
        fetch_group: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/instruments
        Fetches all available instruments and returns raw JSON data.
        """
        params = {
            "enabledOnly": enabled_only,
            "fetchCharacteristics": fetch_characteristics,
            "fetchGroup": fetch_group,
        }
        response = self._client.get("/v1/instruments", params=params)
        return response.json()

    def get_instruments(
        self,
        enabled_only: bool = True,
        fetch_characteristics: bool = True,
        fetch_group: bool = True,
    ) -> List[InstrumentDto]:
        """
        GET /v1/instruments
        Fetches all available instruments and returns typed models.
        """
        data = self.get_instruments_raw(enabled_only, fetch_characteristics, fetch_group)
        return [InstrumentDto(**item) for item in data]

    def get_instruments_df(
        self,
        enabled_only: bool = True,
        fetch_characteristics: bool = True,
        fetch_group: bool = True,
    ) -> pd.DataFrame:
        """
        GET /v1/instruments
        Fetches all available instruments and returns a pandas DataFrame.
        """
        data = self.get_instruments_raw(enabled_only, fetch_characteristics, fetch_group)
        return pd.DataFrame(data)

    def create_instruments(self, instruments_data: List[Dict[str, Any]]) -> None:
        """
        POST /v1/instruments
        Creates new instruments.
        """
        body = instruments_data
        response = self._client.post("/v1/instruments", data=body)  # type: ignore
        response.raise_for_status()
