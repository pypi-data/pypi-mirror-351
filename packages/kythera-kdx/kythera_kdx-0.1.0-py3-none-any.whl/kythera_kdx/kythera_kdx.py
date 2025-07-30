"""
KytheraKdx - Main unified client class for the Kythera API

This module provides a unified client that inherits from AuthenticatedClient
and provides convenient access to all specialized client modules through properties.
"""

from typing import Optional, List

from .authenticated_client import AuthenticatedClient
from .addin import AddInClient
from .funds import FundsClient
from .globals import GlobalsClient
from .instrument_groups import InstrumentGroupsClient
from .instrument_parameters import InstrumentParametersClient
from .instruments import InstrumentsClient
from .intraday import IntradayClient
from .pnl import PnlClient
from .positions import PositionsClient
from .prices import PricesClient
from .risk_factors import RiskFactorsClient
from .trades import TradesClient


class KytheraKdx(AuthenticatedClient):
    """
    Unified Kythera API client with convenient access to all API modules.
    
    This class inherits from AuthenticatedClient and provides properties for accessing
    all specialized client modules. It supports both service principal authentication
    (with client_secret) and interactive device flow authentication (without client_secret).
    
    Example usage:
        # Service principal authentication
        kdx = KytheraKdx(
            client_id="your-client-id",
            client_secret="your-client-secret",
            tenant_id="your-tenant-id"
        )
        
        # Interactive device flow authentication
        kdx = KytheraKdx(client_id="your-client-id")
        
        # Access positions
        positions = kdx.positions.get_positions()
        
        # Access funds
        funds = kdx.funds.get_funds()
        
        # Access prices
        prices = kdx.prices.get_all_prices(price_date=date.today(), price_type_name="CLOSE")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
        scopes: Optional[List[str]] = None,
    ):
        """
        Initialize the unified Kythera client.

        Args:
            base_url: The base URL for the Kythera API
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret (for service principal auth)
            timeout: Request timeout in seconds
            scopes: List of OAuth scopes to request
        """
        super().__init__(
            base_url=base_url,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            timeout=timeout,
            scopes=scopes,
        )
        
        # Initialize all client modules lazily
        self._addin_client: Optional[AddInClient] = None
        self._funds_client: Optional[FundsClient] = None
        self._globals_client: Optional[GlobalsClient] = None
        self._instrument_groups_client: Optional[InstrumentGroupsClient] = None
        self._instrument_parameters_client: Optional[InstrumentParametersClient] = None
        self._instruments_client: Optional[InstrumentsClient] = None
        self._intraday_client: Optional[IntradayClient] = None
        self._pnl_client: Optional[PnlClient] = None
        self._positions_client: Optional[PositionsClient] = None
        self._prices_client: Optional[PricesClient] = None
        self._risk_factors_client: Optional[RiskFactorsClient] = None
        self._trades_client: Optional[TradesClient] = None

    @property
    def addin(self) -> AddInClient:
        """Access to AddIn endpoints."""
        if self._addin_client is None:
            self._addin_client = AddInClient(self)
        return self._addin_client

    @property
    def funds(self) -> FundsClient:
        """Access to Funds endpoints."""
        if self._funds_client is None:
            self._funds_client = FundsClient(self)
        return self._funds_client

    @property
    def globals(self) -> GlobalsClient:
        """Access to Globals (reference data) endpoints."""
        if self._globals_client is None:
            self._globals_client = GlobalsClient(self)
        return self._globals_client

    @property
    def instrument_groups(self) -> InstrumentGroupsClient:
        """Access to Instrument Groups endpoints."""
        if self._instrument_groups_client is None:
            self._instrument_groups_client = InstrumentGroupsClient(self)
        return self._instrument_groups_client

    @property
    def instrument_parameters(self) -> InstrumentParametersClient:
        """Access to Instrument Parameters endpoints."""
        if self._instrument_parameters_client is None:
            self._instrument_parameters_client = InstrumentParametersClient(self)
        return self._instrument_parameters_client

    @property
    def instruments(self) -> InstrumentsClient:
        """Access to Instruments endpoints."""
        if self._instruments_client is None:
            self._instruments_client = InstrumentsClient(self)
        return self._instruments_client

    @property
    def intraday(self) -> IntradayClient:
        """Access to Intraday endpoints."""
        if self._intraday_client is None:
            self._intraday_client = IntradayClient(self)
        return self._intraday_client

    @property
    def pnl(self) -> PnlClient:
        """Access to P&L endpoints."""
        if self._pnl_client is None:
            self._pnl_client = PnlClient(self)
        return self._pnl_client

    @property
    def positions(self) -> PositionsClient:
        """Access to Positions endpoints."""
        if self._positions_client is None:
            self._positions_client = PositionsClient(self)
        return self._positions_client

    @property
    def prices(self) -> PricesClient:
        """Access to Prices endpoints."""
        if self._prices_client is None:
            self._prices_client = PricesClient(self)
        return self._prices_client

    @property
    def risk_factors(self) -> RiskFactorsClient:
        """Access to Risk Factors endpoints."""
        if self._risk_factors_client is None:
            self._risk_factors_client = RiskFactorsClient(self)
        return self._risk_factors_client

    @property
    def trades(self) -> TradesClient:
        """Access to Trades endpoints."""
        if self._trades_client is None:
            self._trades_client = TradesClient(self)
        return self._trades_client
