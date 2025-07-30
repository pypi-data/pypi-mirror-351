from abc import ABC, abstractmethod

from ..schemas.api_request_schema import ExchangeApiRequest


class RequestBuilder(ABC):

    @abstractmethod
    def create_request(self) -> ExchangeApiRequest:
        raise NotImplementedError
    

    @abstractmethod
    def create_signed_request(self) -> ExchangeApiRequest:
        raise NotImplementedError
