from enum import Enum
from typing import TypedDict, cast


class EndpointConfig(TypedDict):
    """Configuration d'un endpoint de l'API."""

    name: str
    path: str
    version: str


class EndpointType(str, Enum):
    """Types d'endpoints disponibles."""

    QUOTES = "quotes"
    CRYPTO = "crypto"


class Endpoints:
    """Configuration des endpoints de l'API CoinMarketCap."""

    BASE_URL = "https://pro-api.coinmarketcap.com/"
    V1_URL = BASE_URL + "v1/"
    V2_URL = BASE_URL + "v2/"

    _ENDPOINTS = {
        EndpointType.QUOTES: {
            "name": EndpointType.QUOTES,
            "path": "cryptocurrency/quotes/latest",
            "version": "v2",
        },
        EndpointType.CRYPTO: {
            "name": EndpointType.CRYPTO,
            "path": "cryptocurrency/map",
            "version": "v1",
        },
    }

    @classmethod
    def get_endpoint(cls, endpoint_type: EndpointType) -> EndpointConfig:
        """Récupère la configuration d'un endpoint.

        Args:
            endpoint_type: Type d'endpoint à récupérer

        Returns:
            EndpointConfig: Configuration de l'endpoint

        Raises:
            ValueError: Si l'endpoint n'existe pas
        """
        if endpoint_type not in cls._ENDPOINTS:
            raise ValueError(f"Endpoint {endpoint_type} non trouvé")

        return cast(EndpointConfig, cls._ENDPOINTS[endpoint_type])

    @classmethod
    def get_url(cls, endpoint_type: EndpointType) -> str:
        """Récupère l'URL complète d'un endpoint.

        Args:
            endpoint_type: Type d'endpoint

        Returns:
            str: URL complète de l'endpoint
        """
        endpoint = cls.get_endpoint(endpoint_type)
        base_url = cls.V2_URL if endpoint["version"] == "v2" else cls.V1_URL
        return f"{base_url}{endpoint['path']}"
