from pydantic import BaseModel, field_validator

from .data_torename import CryptocurrencyMapData
from .quote import QuoteData
from .types import CryptoSymbol


class QuotesEndpointOutput(BaseModel):
    """Type de sortie pour la méthode get_quotes_stream."""

    data: dict[CryptoSymbol, list[QuoteData]]

    class Config:
        arbitrary_types_allowed = True


class CryptoEndpointOutput(BaseModel):
    """Type de sortie pour la méthode get_crypto_stream."""

    data: list[CryptocurrencyMapData]

    @field_validator("data", mode="before")
    @classmethod
    def convert_symbols(cls, data):  # type: ignore
        """Convertit les symboles en objets CryptoSymbol."""
        return [
            {**item, "symbol": CryptoSymbol(symbol=item["symbol"])} for item in data
        ]

    class Config:
        arbitrary_types_allowed = True
