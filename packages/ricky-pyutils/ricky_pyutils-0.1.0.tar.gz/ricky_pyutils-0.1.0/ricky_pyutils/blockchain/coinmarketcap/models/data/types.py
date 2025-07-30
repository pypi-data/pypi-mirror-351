from pydantic import BaseModel, Field, field_validator


class CryptoSymbol(BaseModel):
    """Type personnalisé pour le symbole d'une cryptomonnaie avec validation."""

    symbol: str = Field(min_length=1, max_length=10, pattern=r"^[A-Z0-9]+$")

    def __str__(self) -> str:
        return self.symbol

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls: type["CryptoSymbol"], v: str) -> str:
        if not v.isalnum():
            raise ValueError(
                "Le symbole doit contenir uniquement des lettres et des chiffres"
            )
        return v.upper()
