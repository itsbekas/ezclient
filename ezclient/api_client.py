from os import getenv
from typing import Any, Callable, Optional

import requests

from abc import ABC, abstractproperty, abstractmethod

def request_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "APIClient", endpoint: str, params: dict[str, Any]) -> Any:
        try:
            url = f"{self.base_url}/{endpoint}"
            res = func(self, url, params)
            if res.status_code != 200:
                raise APIException(
                    type(self).__name__, url, res.status_code, self._error_msg(res)
                )
            return res.json()
        except requests.exceptions.RequestException as e:
            raise APIException(
                type(self).__name__,
                url,
                500,
                f"Error accessing {self.base_url}: {str(e)}",
            )

    return wrapper


class APIException(Exception):
    def __init__(self, api: str, url: str, status_code: int, msg: str) -> None:
        self.api = api
        self.url = url
        self.status_code = status_code
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.api} API: Error accessing {self.url} - HTTP {self.status_code}: {self.msg}"


class APIClient:
    provider_name: str
    base_url: str
    headers: Optional[dict[str, str]]
    cookies: Optional[dict[str, str]]
    
    @abstractproperty
    def token(self) -> str:
        pass

    @property
    def _token_headers(self) -> dict[str, str]:
        return {"Authorization": self.token}

    @property
    def _token_bearer_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    @abstractmethod
    def _get(self, endpoint: str, params: dict[str, Any] = {}) -> Any:
        """
        GET request to the API
        """
        pass

    @abstractmethod
    def _post(self, endpoint: str, data: dict[str, Any] = {}) -> Any:
        """
        POST request to the API
        """
        pass

    @request_handler
    def _get_basic(self, url: str, params: dict[str, Any]) -> Any:
        """
        Basic GET request to the API
        """
        return requests.get(url, params=params)

    @request_handler
    def _get_with_headers(self, url: str, params: dict[str, Any]) -> Any:
        """
        GET request to the API with custom headers
        """
        return requests.get(url, headers=self.headers, params=params)

    @request_handler
    def _get_with_cookies(self, url: str, params: dict[str, Any]) -> Any:
        """
        GET request to the API with cookies
        """
        return requests.get(url, cookies=self.cookies, params=params)

    @request_handler
    def _post_basic(self, url: str, data: dict[str, Any]) -> Any:
        """
        Basic POST request to the API
        """
        return requests.post(url, data=data)

    @request_handler
    def _post_with_headers(self, url: str, data: dict[str, Any]) -> Any:
        """
        POST request to the API with custom headers
        """
        return requests.post(url, headers=self.headers, json=data)

    @request_handler
    def _post_with_cookies(self, url: str, data: dict[str, Any]) -> Any:
        """
        POST request to the API with cookies
        """
        return requests.post(url, cookies=self.cookies, data=data)

    @abstractmethod
    def _error_msg(self, res: requests.Response) -> str:
        """
        Get the error message from the response
        """
        pass

    def _load_env_token(self, env_var: str) -> str | None:
        """
        Load token from environment variable
        """

        return getenv(env_var)

    @abstractmethod
    def _test(self) -> None:
        """
        Test connection to the API
        """
        pass

    def test_connection(self) -> bool:
        """
        Test connection to the API
        """
        try:
            self._test()
            return True
        except APIException:
            return False
