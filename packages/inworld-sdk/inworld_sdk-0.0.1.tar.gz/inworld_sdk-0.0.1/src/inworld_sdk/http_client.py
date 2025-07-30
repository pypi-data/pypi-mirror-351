import json
from typing import Literal, Optional
from urllib.parse import urljoin

import requests


class HttpClient:
    """HTTP client"""

    def __init__(
        self,
        api_key: str,
        auth_type: Optional[Literal["basic", "bearer"]] = None,
        base_url: Optional[str] = None,
    ):
        """Constructor for HTTP client

        Args:
            api_key: The API key to use for authentication
            auth_type: Authentication type, either "basic" or "bearer". Defaults to "basic"
            base_url: Optional base URL for the API, defaults to https://api.inworld.ai/v1
        """
        auth_type = auth_type or "basic"
        self.__base_url = base_url or "https://api.inworld.ai/v1"

        if auth_type.lower() not in ["basic", "bearer"]:
            raise ValueError("auth_type must be either 'basic' or 'bearer'")

        auth_prefix = "Basic" if auth_type.lower() == "basic" else "Bearer"
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"{auth_prefix} {api_key}",
        }

    def request(
        self,
        method: str,
        path: str,
        data: dict = {},
    ) -> dict:
        requestData = None
        requestParams = None
        requestUrl = urljoin(self.__base_url, path)

        if method == "post":
            requestData = json.dumps(data) if len(data.keys()) > 0 else ""
        elif method == "get":
            requestParams = data

        response = requests.request(
            method,
            requestUrl,
            data=requestData,
            headers=self.__headers,
            params=requestParams,
        )

        return self.__validateRequestResponse(response)

    def stream(
        self,
        method: str,
        path: str,
        data: dict = {},
    ) -> requests.Response:
        requestData = None
        requestParams = None
        requestUrl = urljoin(self.__base_url, path)
        session = requests.Session()

        if method == "post":
            requestData = json.dumps(data) if len(data.keys()) > 0 else ""
        elif method == "get":
            requestParams = data

        response = session.request(
            method,
            requestUrl,
            data=requestData,
            headers=self.__headers,
            params=requestParams,
            stream=True,
        )

        return self.__validateStreamResponse(response)

    def __validateRequestResponse(self, response: requests.Response) -> dict:
        self.__validateStreamResponse(response)
        return response.json()

    def __validateStreamResponse(self, response: requests.Response) -> requests.Response:
        try:
            body = response.json()
            if isinstance(body, dict) and body.get("code") is not None:
                raise Exception(body.get("message"))
        except Exception:
            pass
            response.raise_for_status()

        return response
