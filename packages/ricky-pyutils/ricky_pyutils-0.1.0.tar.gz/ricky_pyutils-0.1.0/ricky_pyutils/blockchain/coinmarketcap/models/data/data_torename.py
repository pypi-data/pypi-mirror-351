from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .platform import Platform
from .quote import QuoteData
from .tag import Tag
from .types import CryptoSymbol


class QuotesLatestData(BaseModel):
    """
    Représente les données complètes d'une cryptomonnaie de l'endpoint
    /v2/cryptocurrency/quotes/latest.
    """

    id: int = Field(gt=0)
    name: str
    symbol: CryptoSymbol
    slug: str
    num_market_pairs: int = Field(ge=0)
    date_added: datetime
    tags: list[Tag]
    max_supply: int | None = Field(ge=0)
    circulating_supply: int = Field(ge=0)
    total_supply: int = Field(ge=0)
    is_active: int = Field(ge=0, le=1)
    infinite_supply: bool
    platform: Platform | None
    cmc_rank: int | None = Field(gt=0)
    is_fiat: int = Field(ge=0, le=1)
    self_reported_circulating_supply: int | None = Field(ge=0)
    self_reported_market_cap: float | None = Field(ge=0)
    tvl_ratio: float | None = Field(ge=0)
    last_updated: datetime
    quote: dict[str, QuoteData]

    @field_validator("circulating_supply", "total_supply", "max_supply")
    def validate_supply(cls, v, values):  # type: ignore
        if (
            v is not None
            and "max_supply" in values
            and values["max_supply"] is not None
        ):
            if v > values["max_supply"]:
                raise ValueError("La supply ne peut pas être supérieure à max_supply")
        return v


class CryptocurrencyMapData(BaseModel):
    """
    Représente les données de base d'une cryptomonnaie
    de l'endpoint /v1/cryptocurrency/map.
    """

    id: int = Field(gt=0)
    rank: int = Field(gt=0)
    name: str
    symbol: CryptoSymbol
    slug: str
    is_active: int = Field(ge=0, le=1)
    status: int = Field(ge=0)
    first_historical_data: datetime
    last_historical_data: datetime
    platform: Platform | None

    @field_validator("last_historical_data")
    def validate_dates(cls, v, values):  # type: ignore
        if (
            v is not None
            and "first_historical_data" in values
            and values["first_historical_data"] is not None
        ):
            if v < values["first_historical_data"]:
                raise ValueError(
                    "last_historical_data ne peut pas être"
                    "antérieur à first_historical_data"
                )
        return v
