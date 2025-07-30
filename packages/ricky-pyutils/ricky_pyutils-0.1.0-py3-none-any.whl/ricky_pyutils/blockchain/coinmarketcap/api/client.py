import logging
from typing import Any

import requests

from ..models import ApiResponse

logger = logging.getLogger(__name__)


class APIClient:
    """Client de base pour les requêtes HTTP vers l'API CoinMarketCap."""

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def _make_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> ApiResponse[Any]:
        """Effectue une requête HTTP vers l'API.

        Args:
            endpoint: Chemin de l'endpoint
            params: Paramètres de la requête

        Returns:
            ApiResponse: Réponse de l'API

        Raises:
            Exception: Si la requête échoue
        """
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }

        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making request to {url} with params {params}")

        response = requests.get(url, headers=headers, params=params)
        logger.info(
            f"Status code: {response.status_code}params: {params}, headers: {headers}"
        )

        if response.status_code != 200:
            raise Exception("Erreur: " + str(response.json()))

        api_response = ApiResponse(**response.json())

        if api_response.status.credit_count > 5:
            logger.warning(
                "Warning a lot of credit as been used :"
                f"{api_response.status.credit_count}"
            )

        return api_response
