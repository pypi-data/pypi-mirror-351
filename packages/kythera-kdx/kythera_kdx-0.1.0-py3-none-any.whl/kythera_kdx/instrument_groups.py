from typing import List, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import InstrumentGroupDto

class InstrumentGroupsClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_instrument_groups_raw(
        self,
        fetch_characteristics: bool = True,
        fetch_nomenclatures: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/instrument-groups
        Fetches all available instrument groups and returns raw JSON data.
        """
        params = {
            "fetchCharacteristics": fetch_characteristics,
            "fetchNomenclatures": fetch_nomenclatures,
        }
        response = self._client.get("/v1/instrument-groups", params=params)
        return response.json()

    def get_instrument_groups(
        self,
        fetch_characteristics: bool = True,
        fetch_nomenclatures: bool = True,
    ) -> List[InstrumentGroupDto]:
        """
        GET /v1/instrument-groups
        Fetches all available instrument groups and returns typed models.
        """
        data = self.get_instrument_groups_raw(fetch_characteristics, fetch_nomenclatures)
        return [InstrumentGroupDto(**item) for item in data]

    def get_instrument_groups_df(
        self,
        fetch_characteristics: bool = True,
        fetch_nomenclatures: bool = True,
    ) -> pd.DataFrame:
        """
        GET /v1/instrument-groups
        Fetches all available instrument groups and returns a pandas DataFrame.
        """
        data = self.get_instrument_groups_raw(fetch_characteristics, fetch_nomenclatures)
        return pd.DataFrame(data)
