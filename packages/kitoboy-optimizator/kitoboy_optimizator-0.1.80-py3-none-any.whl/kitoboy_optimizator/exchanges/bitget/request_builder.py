from typing import Any

from ..abstract.request_builder import RequestBuilder
from ..schemas.api_request_schema import ExchangeApiRequest
from ..enums import HttpMethod


class BitgetRequestBuilder(RequestBuilder):
    BASE_URL = "https://api.bitget.com"

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.url_params = {}
        self.body_params = {}


    def create_request(self, endpoint: str, method: HttpMethod, url_params: dict | None = None, body_params: dict | None = None, execute_at: int| None = None) -> ExchangeApiRequest:
        self.url = f"{self.base_url}/{endpoint}"
        self.method = method
        if url_params:
            self.__put_url_params_batch(url_params)
        if body_params:
            self.__put_body_params_batch(body_params)

        return ExchangeApiRequest(
            url=self.url,
            method=self.method,
            params=self.url_params,
            body=self.body_params,
            execute_at=execute_at
        )
    
    
    def create_signed_request(self) -> ExchangeApiRequest:
        raise NotImplementedError


    def __put_url_param(self, name: str, value: Any) -> None:
        """
        Adds a parameter to the url parameters.

        :param name: The name of the parameter.
        :param value: The value of the parameter.
        """
        if value is None:
            return
        if isinstance(value, (list, dict)):
            self.url_params[name] = value
        else:
            self.url_params[name] = str(value)

    
    def __put_body_param(self, name: str, value: Any) -> None:
        """
        Adds a parameter to the body post parameters.

        :param name: The name of the parameter.
        :param value: The value of the parameter.
        """
        if value is None:
            return
        if isinstance(value, (list, dict)):
            self.body_params[name] = value
        else:
            self.body_params[name] = str(value)

    
    def __put_url_params_batch(self, batch: dict[str, Any]) -> None:
        if batch and len(batch):
            for key, value in batch.items():
                self.__put_url_param(key, value)
    
    
    def __put_body_params_batch(self, batch: dict[str, Any]) -> None:
        if batch and len(batch):
            for key, value in batch.items():
                self.__put_body_param(key, value)