from ..api.client import APIClient
from ..api.endpoints import Endpoints, EndpointType
from ..models import CryptoSymbol
from ..models.outputs import CryptoStreamOutput, QuotesStreamOutput


class CryptoService:
    """Service pour interagir avec les données de cryptomonnaies."""

    def __init__(self, api_key: str) -> None:
        self.client = APIClient(api_key, Endpoints.BASE_URL)

    def get_quotes_stream(
        self, symbol: CryptoSymbol | None = None, currency: str = "USD"
    ) -> QuotesStreamOutput:
        """Récupère les cotations pour une cryptomonnaie.

        Args:
            symbol: Symbole de la cryptomonnaie
            currency: Devise pour le prix

        Returns:
            QuotesStreamOutput: Données de cotation
        """
        if symbol is None:
            symbol = CryptoSymbol(symbol="BTC")
        url = Endpoints.get_url(EndpointType.QUOTES)
        params = {"symbol": str(symbol), "convert": currency}
        api_response = self.client._make_request(url, params)
        return QuotesStreamOutput(data=api_response.data)

    def get_crypto_stream(self, limit: int = 2) -> CryptoStreamOutput:
        """Récupère la liste des cryptomonnaies par rang.

        Args:
            limit: Nombre maximum de résultats

        Returns:
            CryptoStreamOutput: Liste des cryptomonnaies
        """
        url = Endpoints.get_url(EndpointType.CRYPTO)
        params = {"sort": "cmc_rank", "limit": limit}
        api_response = self.client._make_request(url, params)
        return CryptoStreamOutput(data=api_response.data)
