from typing import List, Dict, Any
from datetime import date

import pandas as pd

from .authenticated_client import AuthenticatedClient
from .models_v1 import PriceDto, OverrideInstrumentPriceRequest, PriceTypeDto


class PricesClient:
    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def get_all_prices_raw(
        self,
        price_date: date,
        price_type_name: str,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/prices
        Fetches all prices for a given date and type, returns raw JSON data.
        """
        params = {"priceDate": price_date.isoformat(), "priceTypeName": price_type_name}
        response = self._client.get("/v1/prices", params=params)
        response.raise_for_status()
        return response.json()

    def get_all_prices(
        self,
        price_date: date,
        price_type_name: str,
    ) -> List[PriceDto]:
        """
        GET /v1/prices
        Fetches all prices for a given date and type.
        """
        data = self.get_all_prices_raw(price_date, price_type_name)
        return [PriceDto(**item) for item in data]

    def get_all_prices_df(
        self,
        price_date: date,
        price_type_name: str,
    ) -> pd.DataFrame:
        """
        GET /v1/prices
        Fetches all prices for a given date and type, returns as pandas DataFrame.
        """
        data = self.get_all_prices_raw(price_date, price_type_name)
        return pd.DataFrame(data)

    def get_prices_by_instrument_raw(
        self,
        instrument_id: int,
        price_date: date,
        price_type_name: str,
    ) -> List[Dict[str, Any]]:
        """
        GET /v1/prices/{instrumentId}
        Fetches prices for a given date, type and instrument, returns raw JSON data.
        """
        params = {"priceDate": price_date.isoformat(), "priceTypeName": price_type_name}
        response = self._client.get(f"/v1/prices/{instrument_id}", params=params)
        response.raise_for_status()
        return response.json()

    def get_prices_by_instrument(
        self,
        instrument_id: int,
        price_date: date,
        price_type_name: str,
    ) -> List[PriceDto]:
        """
        GET /v1/prices/{instrumentId}
        Fetches prices for a given date, type and instrument.
        """
        data = self.get_prices_by_instrument_raw(instrument_id, price_date, price_type_name)
        return [PriceDto(**item) for item in data]

    def get_prices_by_instrument_df(
        self,
        instrument_id: int,
        price_date: date,
        price_type_name: str,
    ) -> pd.DataFrame:        
        """
        GET /v1/prices/{instrumentId}
        Fetches prices for a given date, type and instrument, returns as pandas DataFrame.
        """
        data = self.get_prices_by_instrument_raw(instrument_id, price_date, price_type_name)
        return pd.DataFrame(data)

    def post_prices(
        self,
        requests: List[OverrideInstrumentPriceRequest],
    ) -> None:
        """
        POST /v1/prices
        Publishes instrument prices.
        """
        body = [req.dict() for req in requests]
        response = self._client.post("/v1/prices", data=body)  # type: ignore
        response.raise_for_status()

    def get_price_types_raw(self) -> List[Dict[str, Any]]:
        """
        GET /v1/prices/price-types
        Fetches all price types, returns raw JSON data.
        """
        response = self._client.get("/v1/prices/price-types")
        response.raise_for_status()
        return response.json()

    def get_price_types(self) -> List[PriceTypeDto]:
        """
        GET /v1/prices/price-types
        Fetches all price types.
        """
        data = self.get_price_types_raw()
        return [PriceTypeDto(**item) for item in data]

    def get_price_types_df(self) -> pd.DataFrame:
        """
        GET /v1/prices/price-types
        Fetches all price types, returns as pandas DataFrame.
        """
        data = self.get_price_types_raw()
        return pd.DataFrame(data)
