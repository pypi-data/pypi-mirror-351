from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class ApiStatus(BaseModel):
    """Représente le statut de la réponse API."""

    timestamp: datetime
    error_code: int = Field(ge=0)
    error_message: str | None = None
    elapsed: int
    credit_count: int = Field(ge=0)
    notice: str | None = None

    @field_validator("error_code")
    def validate_error_code(cls, v):  # type: ignore
        if v != 0:
            raise ValueError(f"Erreur API: {v}")
        return v


class ApiResponse(BaseModel, Generic[T]):
    """Représente une réponse de l'API CoinMarketCap.

    Type Parameters:
        T: Type des données contenues dans la réponse
    """

    status: ApiStatus
    data: T
