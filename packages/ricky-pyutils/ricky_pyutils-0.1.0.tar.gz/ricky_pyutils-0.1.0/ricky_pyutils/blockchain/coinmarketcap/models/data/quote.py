from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class QuoteData(BaseModel):
    """Représente les données de cotation d'une cryptomonnaie."""

    price: float | None = Field(ge=0)
    volume_24h: float = Field(ge=0)
    volume_change_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float
    percent_change_60d: float
    percent_change_90d: float
    market_cap: float | None = Field(ge=0)
    market_cap_dominance: float = Field(ge=0, le=100)
    fully_diluted_market_cap: float = Field(ge=0)
    tvl: float | None = Field(ge=0)
    last_updated: datetime

    @field_validator(
        "percent_change_1h",
        "percent_change_24h",
        "percent_change_7d",
        "percent_change_30d",
        "percent_change_60d",
        "percent_change_90d",
    )
    def validate_percent_change(cls, v):  # type: ignore
        if not -100 <= v <= 100:
            raise ValueError(f"Le pourcentage doit être entre -100 et 100, reçu: {v}")
        return v
