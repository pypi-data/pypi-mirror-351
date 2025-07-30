from datetime import date
from typing import List, Optional, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import TradeDto

class TradesClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_trades_raw(
        self,
        effective_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/trades
        Fetches all trades for a given effective date and returns raw JSON data.
        """
        params: dict = {}
        if effective_date:
            params["effectiveDate"] = effective_date.isoformat()
        response = self._client.get("/v1/trades", params=params)
        return response.json()

    def get_trades(
        self,
        effective_date: Optional[date] = None,
    ) -> List[TradeDto]:
        """
        GET /v1/trades
        Fetches all trades for a given effective date and returns typed models.
        """
        data = self.get_trades_raw(effective_date)
        return [TradeDto(**item) for item in data]

    def get_trades_df(
        self,
        effective_date: Optional[date] = None,
    ) -> pd.DataFrame:
        """
        GET /v1/trades
        Fetches all trades for a given effective date and returns a pandas DataFrame.
        """
        data = self.get_trades_raw(effective_date)
        return pd.DataFrame(data)
