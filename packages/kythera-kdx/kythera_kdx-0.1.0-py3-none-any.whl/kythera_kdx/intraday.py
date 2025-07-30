from typing import List, Dict, Any
import pandas as pd
from .authenticated_client import AuthenticatedClient
from .models_v1 import IntradayPriceDto, IntradayRiskFactorValueDto


class IntradayClient:
    """Client for intraday data endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_intraday_prices_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/intraday-prices
        Fetches all current instrument prices and returns raw JSON data.
        """
        response = self._client.get("/v1/intraday-prices")
        return response.json()

    def get_intraday_prices(self) -> List[IntradayPriceDto]:
        """
        GET /v1/intraday-prices
        Fetches all current instrument prices and returns typed models.
        """
        data = self.get_intraday_prices_raw()
        return [IntradayPriceDto(**item) for item in data]

    def get_intraday_prices_df(self) -> pd.DataFrame:
        """
        GET /v1/intraday-prices
        Fetches all current instrument prices and returns as pandas DataFrame.
        """
        data = self.get_intraday_prices_raw()
        return pd.DataFrame(data)

    def get_intraday_risk_factor_values_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/intraday-risk-factor-values
        Fetches current risk factor values and returns raw JSON data.
        """
        response = self._client.get("/v1/intraday-risk-factor-values")
        return response.json()

    def get_intraday_risk_factor_values(self) -> List[IntradayRiskFactorValueDto]:
        """
        GET /v1/intraday-risk-factor-values
        Fetches current risk factor values and returns typed models.
        """
        data = self.get_intraday_risk_factor_values_raw()
        return [IntradayRiskFactorValueDto(**item) for item in data]

    def get_intraday_risk_factor_values_df(self) -> pd.DataFrame:
        """
        GET /v1/intraday-risk-factor-values
        Fetches current risk factor values and returns as pandas DataFrame.
        """
        data = self.get_intraday_risk_factor_values_raw()
        return pd.DataFrame(data)
