from typing import List, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import InstrumentParameterDto

class InstrumentParametersClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_instrument_parameters_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/instruments/parameters
        Fetches all available instrument parameters used in characteristics and returns raw JSON data.
        """
        response = self._client.get("/v1/instruments/parameters")
        return response.json()

    def get_instrument_parameters(self) -> List[InstrumentParameterDto]:
        """
        GET /v1/instruments/parameters
        Fetches all available instrument parameters used in characteristics and returns typed models.
        """
        data = self.get_instrument_parameters_raw()
        return [InstrumentParameterDto(**item) for item in data]

    def get_instrument_parameters_df(self) -> pd.DataFrame:
        """
        GET /v1/instruments/parameters
        Fetches all available instrument parameters used in characteristics and returns a pandas DataFrame.
        """
        data = self.get_instrument_parameters_raw()
        return pd.DataFrame(data)
