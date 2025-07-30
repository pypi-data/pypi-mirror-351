from typing import List, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import IntradayPnlEntryDto


class PnlClient:
    """Client for PnL (Profit and Loss) related endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_intraday_pnl_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/pnl/intraday
        Fetches current intraday PnL and returns raw JSON data.
        """
        response = self._client.get("/v1/pnl/intraday")
        return response.json()

    def get_intraday_pnl(self) -> List[IntradayPnlEntryDto]:
        """
        GET /v1/pnl/intraday
        Fetches current intraday PnL and returns typed models.
        """
        data = self.get_intraday_pnl_raw()
        return [IntradayPnlEntryDto(**item) for item in data]

    def get_intraday_pnl_df(self) -> pd.DataFrame:
        """
        GET /v1/pnl/intraday
        Fetches current intraday PnL and returns a pandas DataFrame.
        """
        data = self.get_intraday_pnl_raw()
        return pd.DataFrame(data)
