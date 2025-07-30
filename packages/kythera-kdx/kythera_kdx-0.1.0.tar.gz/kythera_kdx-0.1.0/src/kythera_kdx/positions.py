from datetime import date
from typing import List, Optional, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import PositionDto


class PositionsClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_positions_raw(
        self,
        position_date: Optional[date] = None,
        is_open: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/positions
        Fetches all position entries for a given date and returns raw JSON data.
        """
        params: dict = {}
        if position_date:
            params["positionDate"] = position_date.isoformat()
        params["isOpen"] = is_open
        response = self._client.get("/v1/positions", params=params)
        return response.json()

    def get_positions(
        self,
        position_date: Optional[date] = None,
        is_open: bool = True,
    ) -> List[PositionDto]:
        """
        GET /v1/positions
        Fetches all position entries for a given date and returns typed models.
        """
        data = self.get_positions_raw(position_date, is_open)
        return [PositionDto(**item) for item in data]

    def get_positions_df(
        self,
        position_date: Optional[date] = None,
        is_open: bool = True,
    ) -> pd.DataFrame:
        """
        GET /v1/positions
        Fetches all position entries for a given date and returns a pandas DataFrame.
        """
        data = self.get_positions_raw(position_date, is_open)
        return pd.DataFrame(data)
