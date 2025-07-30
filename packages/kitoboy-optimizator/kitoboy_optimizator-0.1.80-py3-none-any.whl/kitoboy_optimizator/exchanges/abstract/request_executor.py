from abc import ABC, abstractmethod

from ..schemas.api_request_schema import ExchangeApiRequest


class RequestExecutor(ABC):

    @abstractmethod
    def call(self, request: ExchangeApiRequest) -> dict:
        raise NotImplementedError
