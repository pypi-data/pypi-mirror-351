from typing import List, Dict, Any

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import CalendarDto, CountryDto, CurrencyDto, InstitutionDto, InstitutionTypeDto, IssuerDto

class GlobalsClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_calendars_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/globals/calendars
        Fetches all available calendars and returns raw JSON data.
        """
        response = self._client.get("/v1/globals/calendars")
        return response.json()

    def get_calendars(self) -> List[CalendarDto]:
        """
        GET /v1/globals/calendars
        Fetches all available calendars and returns typed models.
        """
        data = self.get_calendars_raw()
        return [CalendarDto(**item) for item in data]

    def get_calendars_df(self) -> pd.DataFrame:
        """
        GET /v1/globals/calendars
        Fetches all available calendars and returns a pandas DataFrame.
        """
        data = self.get_calendars_raw()
        return pd.DataFrame(data)

    def get_countries_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/globals/countries
        Fetches all available countries and returns raw JSON data.
        """
        response = self._client.get("/v1/globals/countries")
        return response.json()

    def get_countries(self) -> List[CountryDto]:
        """
        GET /v1/globals/countries
        Fetches all available countries and returns typed models.
        """
        data = self.get_countries_raw()
        return [CountryDto(**item) for item in data]

    def get_countries_df(self) -> pd.DataFrame:
        """
        GET /v1/globals/countries
        Fetches all available countries and returns a pandas DataFrame.
        """
        data = self.get_countries_raw()
        return pd.DataFrame(data)

    def get_currencies_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/globals/currencies
        Fetches all available currencies and returns raw JSON data.
        """
        response = self._client.get("/v1/globals/currencies")
        return response.json()

    def get_currencies(self) -> List[CurrencyDto]:
        """
        GET /v1/globals/currencies
        Fetches all available currencies and returns typed models.
        """
        data = self.get_currencies_raw()
        return [CurrencyDto(**item) for item in data]

    def get_currencies_df(self) -> pd.DataFrame:
        """
        GET /v1/globals/currencies
        Fetches all available currencies and returns a pandas DataFrame.
        """
        data = self.get_currencies_raw()
        return pd.DataFrame(data)

    def get_institutions_raw(
        self,
        fetch_characteristics: bool = False,
        fetch_nomenclatures: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/globals/institutions
        Fetches all available institutions and returns raw JSON data.
        """
        params = {
            "fetchCharacteristics": fetch_characteristics,
            "fetchNomenclatures": fetch_nomenclatures,
        }
        response = self._client.get("/v1/globals/institutions", params=params)
        return response.json()

    def get_institutions(
        self,
        fetch_characteristics: bool = False,
        fetch_nomenclatures: bool = False,
    ) -> List[InstitutionDto]:
        """
        GET /v1/globals/institutions
        Fetches all available institutions and returns typed models.
        """
        data = self.get_institutions_raw(fetch_characteristics, fetch_nomenclatures)
        return [InstitutionDto(**item) for item in data]

    def get_institutions_df(
        self,
        fetch_characteristics: bool = False,
        fetch_nomenclatures: bool = False,
    ) -> pd.DataFrame:
        """
        GET /v1/globals/institutions
        Fetches all available institutions and returns a pandas DataFrame.
        """
        data = self.get_institutions_raw(fetch_characteristics, fetch_nomenclatures)
        return pd.DataFrame(data)

    def get_institution_types_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/globals/institutions/types
        Fetches all available institution types and returns raw JSON data.
        """
        response = self._client.get("/v1/globals/institutions/types")
        return response.json()

    def get_institution_types(self) -> List[InstitutionTypeDto]:
        """
        GET /v1/globals/institutions/types
        Fetches all available institution types and returns typed models.
        """
        data = self.get_institution_types_raw()
        return [InstitutionTypeDto(**item) for item in data]

    def get_institution_types_df(self) -> pd.DataFrame:
        """
        GET /v1/globals/institutions/types
        Fetches all available institution types and returns a pandas DataFrame.
        """
        data = self.get_institution_types_raw()
        return pd.DataFrame(data)

    def get_issuers_raw(self, fetch_characteristics: bool = False) -> List[Dict[str, Any]]:
        """
        GET /v1/globals/issuers
        Fetches all available issuers and returns raw JSON data.
        """
        params = {"fetchCharacteristics": fetch_characteristics}
        response = self._client.get("/v1/globals/issuers", params=params)
        return response.json()

    def get_issuers(self, fetch_characteristics: bool = False) -> List[IssuerDto]:
        """
        GET /v1/globals/issuers
        Fetches all available issuers and returns typed models.
        """
        data = self.get_issuers_raw(fetch_characteristics)
        return [IssuerDto(**item) for item in data]

    def get_issuers_df(self, fetch_characteristics: bool = False) -> pd.DataFrame:
        """
        GET /v1/globals/issuers
        Fetches all available issuers and returns a pandas DataFrame.
        """
        data = self.get_issuers_raw(fetch_characteristics)
        return pd.DataFrame(data)
