from pydantic import BaseModel, Field


class Platform(BaseModel):
    """Représente la plateforme d'une cryptomonnaie."""

    id: int = Field(gt=0)
    name: str
    symbol: str
    slug: str
    token_address: str | None = None
