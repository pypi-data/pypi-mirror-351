import logging
import aiohttp
import json
from contextlib import asynccontextmanager

from ..schemas.api_request_schema import ExchangeApiRequest
from ..enums import HttpMethod
from ..utils.retry_decorator import retry
from ..abstract.request_executor import RequestExecutor
from .exceptions import BitgetParamsException, BitgetRequestException
from kitoboy_optimizator.http_session_manager.http_session_manager import HTTPSessionManager

logger = logging.getLogger(__name__)


class BitgetRequestExecutor(RequestExecutor):

    def __init__(self, http_session_manager: HTTPSessionManager):
        self.http_session_manager = http_session_manager

    
    # @asynccontextmanager
    # async def get_http_session(self):
    #     session = aiohttp.ClientSession()
    #     try:
    #         yield session
    #     finally:
    #         await session.close()


    @retry(BitgetRequestException, tries=5, delay=1, backoff=2, logger=logger)
    async def call(self, request: ExchangeApiRequest):
        response_text = await self._call_async(request)
        result = json.loads(response_text)
        if result.get("msg") != "success":
            if result.get("code") == "40034":
                raise BitgetParamsException(f"{result.get('msg')}")
            print(f"RESULT: {result}")
            raise ValueError(f"UNKNOWN ERROR {result.get('msg')}")
        return result.get("data")


    async def _call_async(self, request: ExchangeApiRequest):
        if request.method == HttpMethod.GET:
            return await self._call_get_method(request)
        elif request.method == HttpMethod.POST:
            return await self._call_post_method(request)
        else:
            raise Exception(f"Unsupported HTTP method: {request.method}")


    async def _call_get_method(self, request: ExchangeApiRequest):
        # async with self.__get_http_session() as client:
        async with self.http_session_manager.get_session() as session:
            async with session.get(request.url, headers=request.headers, params=request.params) as response:
                return await response.text()


    async def _call_post_method(self, request: ExchangeApiRequest):
        data = request.body_params_list if request.body_params_list else request.body
        async with self.http_session_manager.get_session() as session:
            async with session.post(request.url, json=data, headers=request.headers) as response:
                return await response.text()