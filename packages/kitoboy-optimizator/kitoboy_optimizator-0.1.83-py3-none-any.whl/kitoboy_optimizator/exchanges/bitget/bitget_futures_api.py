# https://www.bitget.com/api-doc/contract/market/Get-History-Candle-Data
# curl "https://api.bitget.com/api/v2/mix/market/history-candles?symbol=BTCUSDT&granularity=1W&limit=200&productType=usdt-futures"
import numpy as np
import asyncio
from enum import Enum
import datetime as dt

import logging

from .utils import safe_api_request

from .async_api_requests_executor import BitgetRequestExecutor
from .request_builder import BitgetRequestBuilder
from .exceptions import BitgetParamsException
from ..exceptions import NoExchangeDataForSymbolException
from ..abstract.request_executor import RequestExecutor
from ..schemas.symbol_params_schema import SymbolParams
from ..abstract.exchange_api_adapter import ExchangeApiAdapter
from ..enums import HttpMethod
from ..utils.filter_row_within_time_range import filter_rows_within_time_range
from kitoboy_optimizator.http_session_manager.http_session_manager import HTTPSessionManager


logger = logging.getLogger()


class ProductType(Enum):
    USDT_FUTURES = "usdt-futures"
    COIN_FUTURES = "coin-futures"
    USDC_FUTURES = "usdc-futures"
    SUSDT_FUTURES = "s-usdt-futures"
    SCOIN_FUTURES = "s-coin_futures"
    SUSDC_FUTURES = "s-usdc-futures"


interval_step = {
    "1m": 60 * 1000,
    "3m": 60 * 1000 * 3,
    "5m": 60 * 1000 * 5,
    "15m": 60 * 1000 * 15,
    "30m": 60 * 1000 * 30,
    "1H": 60 * 1000 * 60,
    "4H": 60 * 1000 * 60 * 4,
    "6H": 60 * 1000 * 60 * 6,
    "12H": 60 * 1000 * 60 * 12,
    "1D": 60 * 1000 * 60 * 24,
    "1W": 60 * 1000 * 60 * 24 * 7,
    "1M": 60 * 1000 * 60 * 24 * 30,
}

timeframes = {
    "1m": "1m",
    "3m": "3m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1H",
    "4h": "4H",
    "6h": "6H",
    "12h": "12H",
    "1d": "1D",
    "1w": "1W",
    "1M": "1M",
}


class BitgetFuturesAPI(ExchangeApiAdapter):
    BASE_URL = "https://api.bitget.com"
    EXCHANGE_NAME = "bitget_futures"
    PRODUCT_TYPE = "umcbl"

    def __init__(
        self,
        http_session_manager: HTTPSessionManager,
        api_key: str = "",
        api_secret: str = "",
        request_executor: RequestExecutor | None = None,
    ):
        if request_executor is None:
            request_executor = BitgetRequestExecutor(http_session_manager)
        self.request_executor = request_executor
        self.api_key = api_key
        self.api_secret = api_secret


    @property
    def exchange_name(self) -> str:
        return self.EXCHANGE_NAME


    async def fetch_ohlcv(
        self, symbol: str, interval: str, start_timestamp: int, end_timestamp: int
    ) -> np.ndarray:
        # product_type = ProductType.USDT_FUTURES

        interval = timeframes.get(interval)
        limit = self.__get_ohlcv_data_size_limit(interval)

        since = start_timestamp
        end = self.__get_end_time_for_historical_data_request(
            start_time=start_timestamp, timeframe=interval, limit=limit
        )
        all_ohlcv = []
        try:
            while since < end_timestamp:
                ohlcv = await self.__fetch_historical_candlestick_from_api(
                    symbol=symbol,
                    timeframe=interval,
                    start_timestamp=since,
                    end_timestamp=end,
                    limit=limit,
                )
                if not ohlcv:
                    if end < end_timestamp:
                        since = self.__get_end_time_for_historical_data_request(
                            start_time=end, timeframe=interval, limit=1
                        )  # Set 'since' to the timestamp of the last fetched candle + 1 candle
                        end = self.__get_end_time_for_historical_data_request(
                            start_time=since, timeframe=interval, limit=limit
                        )
                    else:
                        break  # No more data available
                else:
                    all_ohlcv.extend(ohlcv)
                    since = self.__get_end_time_for_historical_data_request(
                        start_time=int(ohlcv[-1][0]), timeframe=interval, limit=1
                    )  # Set 'since' to the timestamp of the last fetched candle + 1 candle
                    end = self.__get_end_time_for_historical_data_request(
                        start_time=since, timeframe=interval, limit=limit
                    )
                await asyncio.sleep(0.1)
            
            result_ohlcv = np.array(all_ohlcv)[:, :6].astype(float)
            return filter_rows_within_time_range(
                data=result_ohlcv,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )

        except BitgetParamsException as e:
            raise NoExchangeDataForSymbolException(
                symbol=symbol,
                exchange_name=self.exchange_name,
                message=e.message
            )
        except IndexError as e:
            raise NoExchangeDataForSymbolException(
                symbol=symbol,
                exchange_name=self.exchange_name,
                message=e.args
            )
        

    async def get_symbol_params(self, symbol: str) -> SymbolParams:
        endpoint = "/api/mix/v1/market/contracts"
        url_params = {
            "productType": self.PRODUCT_TYPE
        }
        body_params = {}
        request = BitgetRequestBuilder().create_request(
            endpoint=endpoint, 
            url_params=url_params, 
            body_params=body_params, 
            method=HttpMethod.GET
        )
        response = await self.request_executor.call(request)        
        symbol_info = [item for item in response if item["symbolName"] == symbol][0]
        return SymbolParams(
            symbol=symbol,
            price_tick_size=str(float(pow(10, -int(symbol_info["pricePlace"]))) * float(symbol_info["priceEndStep"])),
            qty_step_size=symbol_info["sizeMultiplier"],
            min_qty=symbol_info["minTradeNum"]
        )


    @safe_api_request
    async def __fetch_historical_candlestick_from_api(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
        start_timestamp: int,
        end_timestamp: int | None = None,
    ) -> list:
        endpoint = "/api/v2/mix/market/history-candles"
        if not end_timestamp:
            end_timestamp = self.__get_end_time_for_historical_data_request(
                start_time=start_timestamp, timeframe=timeframe, limit=limit
            )

        url_params = {
            "symbol": symbol,
            "granularity": timeframe,
            "startTime": start_timestamp,
            "endTime": end_timestamp,
            "limit": limit,
            "productType": self.PRODUCT_TYPE,
        }
        body_params = {}
        request = BitgetRequestBuilder().create_request(
            endpoint=endpoint, 
            url_params=url_params, 
            body_params=body_params, 
            method=HttpMethod.GET
        )

        return await self.request_executor.call(request) 

    @classmethod
    def __get_end_time_for_historical_data_request(
        cls, start_time: int, timeframe: str, limit: int
    ) -> int:
        end_time = start_time + limit * interval_step.get(timeframe)
        return end_time

    # @classmethod
    # async def __fetch_symbol_parameters_from_api(cls, symbol: str) -> dict:
    #     endpoint = "/api/v2/spot/public/symbols"
    #     params = {"symbol": symbol}
    #     url = f"{cls.BASE_URL}{endpoint}"


    #     async with http_session.get(url, params=params) as resp:
    #         response_json = await resp.json()
    #         if resp.status == 200:
    #             return response_json["data"][0]
    #         else:
    #             raise Exception(response_json["msg"])

    @classmethod
    def __get_ohlcv_data_size_limit(cls, timeframe: str) -> int:
        # Exchange limit 200 candles, but not more than 90 days
        if timeframe == "1D":
            return 90
        elif timeframe == "1W":
            return 12
        elif timeframe == "1M":
            return 2
        else:
            return 200


def print_timedelta(start: int, end: int):
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)

    # Calculate timedelta
    delta = end - start

    # Extract days, seconds and then hours and minutes from seconds
    days = delta.days
    seconds_in_day = delta.seconds
    hours = seconds_in_day // 3600
    minutes = (seconds_in_day % 3600) // 60

    total_seconds = delta.total_seconds()
    total_hours = total_seconds // 3600
    total_minutes = total_seconds // 60

    print(f"{days} days, {hours} hours and {minutes} minutes")
    print(f"HOURS: {total_hours}")
    print(f"MINUTES: {total_minutes}")


def get_timedelta_in_hours(start: int, end: int) -> float:
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    # Calculate timedelta
    delta = end - start
    total_seconds = delta.total_seconds()
    total_hours = total_seconds // 3600
    return total_hours


def get_timedelta_in_minutes(start: int, end: int) -> float:
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    # Calculate timedelta
    delta = end - start
    total_seconds = delta.total_seconds()
    total_hours = total_seconds // 60
    return total_hours


def get_timedelta_in_days(start: int, end: int) -> float:
    # Convert milliseconds to seconds
    start = dt.datetime.fromtimestamp(start / 1000)
    end = dt.datetime.fromtimestamp(end / 1000)
    # Calculate timedelta
    delta = end - start
    return delta.days


async def main():
    # start_timestamp = 1609459200000
    start_timestamp = 1577836800000
    # start_timestamp = 1622000400000
    # start_timestamp = 1702724400000
    # start_timestamp = 1706724400000
    end_timestamp = 1706826509000
    end_timestamp = 1672531200000
    symbol = "AAVEUSDT"
    # symbol = "BTCUSDT"
    api = BitgetFuturesAPI(api_key="", api_secret="")
    ohlcv = await api.fetch_ohlcv(
        symbol=symbol,
        interval="1h",
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    symbol_params = await api.get_symbol_params(symbol)

    print(ohlcv)
    # print(f"len: {len(ohlcv)}")
    print_timedelta(start=start_timestamp, end=end_timestamp)
    for item in ohlcv[:3, 0]:
        print(item)
    for item in ohlcv[-3:, 0]:
        print(item)
    # print(ohlcv[:1,0][0])
    # print(ohlcv[-1:,0][0])
    print(
        "Timedelta in hours:", get_timedelta_in_hours(ohlcv[:1, 0][0], ohlcv[-1:, 0][0])
    )
    print(
        "Timedelta in minutes:",
        get_timedelta_in_minutes(ohlcv[:1, 0][0], ohlcv[-1:, 0][0]),
    )
    print(f"Symbol params: {symbol_params}")
