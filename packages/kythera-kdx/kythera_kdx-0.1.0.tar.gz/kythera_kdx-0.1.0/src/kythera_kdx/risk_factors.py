from datetime import date
from typing import List, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import (
    RiskFactorDto,
    RiskFactorValueDto,
    OverrideRiskFactorValueRequest,
    RiskValueTypeDto,
)


class RiskFactorsClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_risk_factors_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/risk-factors
        Fetches all risk factors and returns raw JSON data.
        """
        response = self._client.get("/v1/risk-factors")
        return response.json()

    def get_risk_factors(self) -> List[RiskFactorDto]:
        """
        GET /v1/risk-factors
        Fetches all risk factors and returns typed models.
        """
        data = self.get_risk_factors_raw()
        return [RiskFactorDto(**item) for item in data]

    def get_risk_factors_df(self) -> pd.DataFrame:
        """
        GET /v1/risk-factors
        Fetches all risk factors and returns a pandas DataFrame.
        """
        data = self.get_risk_factors_raw()
        return pd.DataFrame(data)

    def get_risk_factor_values_raw(
        self,
        valuation_date: date,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/risk-factor-values
        Fetches all risk factor values for a given date and returns raw JSON data.
        """
        params = {"valuation-date": valuation_date.isoformat()}
        response = self._client.get("/v1/risk-factor-values", params=params)
        return response.json()

    def get_risk_factor_values(
        self,
        valuation_date: date,
    ) -> List[RiskFactorValueDto]:
        """
        GET /v1/risk-factor-values
        Fetches all risk factor values for a given date and returns typed models.
        """
        data = self.get_risk_factor_values_raw(valuation_date)
        return [RiskFactorValueDto(**item) for item in data]

    def get_risk_factor_values_df(
        self,
        valuation_date: date,
    ) -> pd.DataFrame:
        """
        GET /v1/risk-factor-values
        Fetches all risk factor values for a given date and returns a pandas DataFrame.
        """
        data = self.get_risk_factor_values_raw(valuation_date)
        return pd.DataFrame(data)

    def post_risk_factor_values(
        self,
        requests: List[OverrideRiskFactorValueRequest],
    ) -> None:
        """
        POST /v1/risk-factor-values
        Publishes risk factor values.
        """
        body = [req.dict() for req in requests]
        response = self._client.post("/v1/risk-factor-values", data=body)  # type: ignore
        response.raise_for_status()

    def get_risk_factor_value_types_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/risk-factor-values/types
        Fetches all risk factor value types and returns raw JSON data.
        """
        response = self._client.get("/v1/risk-factor-values/types")
        return response.json()

    def get_risk_factor_value_types(self) -> List[RiskValueTypeDto]:
        """
        GET /v1/risk-factor-values/types
        Fetches all risk factor value types and returns typed models.
        """
        data = self.get_risk_factor_value_types_raw()
        return [RiskValueTypeDto(**item) for item in data]

    def get_risk_factor_value_types_df(self) -> pd.DataFrame:
        """
        GET /v1/risk-factor-values/types
        Fetches all risk factor value types and returns a pandas DataFrame.
        """
        data = self.get_risk_factor_value_types_raw()
        return pd.DataFrame(data)
