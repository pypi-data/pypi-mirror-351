import os
from typing import Any, Dict, Optional

import httpx


class MixgardenSDK:
    """Very small Python wrapper around the Mixgarden REST API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.mixgarden.ai/api/v1") -> None:
        self.api_key = api_key or os.getenv("MIXGARDEN_API_KEY")
        if not self.api_key:
            raise ValueError("Mixgarden API key missing (set MIXGARDEN_API_KEY or pass api_key).")
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={ "Authorization": f"MixgardenAPIKey {self.api_key}" },
            timeout=30.0,
        )

    # ---- internal -------------------------------------------------------
    def _request(self, method: str, path: str, *, json: Optional[dict] = None, params: Optional[dict] = None):
        response = self._client.request(method.upper(), path, json=json, params=params)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    # ---- public helpers -------------------------------------------------
    def get_models(self):
        return self._request("GET", "/models")

    def chat(self, **params):
        return self._request("POST", "/chat", json=params)

    def get_completion(self, **params):
        return self._request("POST", "/chat/completions", json=params)

    def get_plugins(self):
        return self._request("GET", "/plugins")

    def get_conversations(self, **params):
        return self._request("GET", "/conversations", params=params)

    def get_conversation(self, conversation_id: str):
        return self._request("GET", f"/conversations/{conversation_id}")

    def close(self):
        self._client.close()
