from pydantic import BaseModel


class Tag(BaseModel):
    """Représente un tag associé à une cryptomonnaie."""

    slug: str
    name: str
    category: str
