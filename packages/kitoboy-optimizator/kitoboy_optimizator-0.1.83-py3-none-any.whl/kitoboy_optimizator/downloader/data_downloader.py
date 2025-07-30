import asyncio
import os
import numpy as np
from typing import Protocol
import logging

from kitoboy_optimizator.enums import Exchanges
from kitoboy_optimizator.data_structures import DownloadingTask, DownloadingOHLCVResult
from kitoboy_optimizator.exchanges import BinanceFuturesAPI, BinanceSpotAPI, BybitFuturesAPI, BitgetFuturesAPI
from kitoboy_optimizator.exchanges.exceptions import NoExchangeDataForSymbolException
from kitoboy_optimizator.http_session_manager.http_session_manager import HTTPSessionManager

logger = logging.getLogger("kitoboy_optimizator")

class ExchangeAPIClient(Protocol):

    @property
    def exchange_name() -> str:
        ...

        
    async def fetch_ohlcv(
        self,
        symbol: str,
        interval: str,
        start_timestamp: int,
        end_timestamp: int
    ) -> np.ndarray:
        ...


class HistoricalDataManager:
    
    def __init__(self, data_dir: str, http_session_manager: HTTPSessionManager):
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        print(f"Data dir: {data_dir}")
        self.clients_pool = {}
        self.http_session_manager = http_session_manager


    async def get_client(self, exchange: Exchanges) -> ExchangeAPIClient:
        if exchange.value not in self.clients_pool:
            if exchange == Exchanges.BINANCE_FUTURES:
                self.clients_pool[exchange.value] = BinanceFuturesAPI()
            elif exchange == Exchanges.BINANCE_SPOT:
                self.clients_pool[exchange.value] = BinanceSpotAPI()
            elif exchange == Exchanges.BYBIT_FUTURES:
                self.clients_pool[exchange.value] = BybitFuturesAPI()
            elif exchange == Exchanges.BITGET_FUTURES:
                self.clients_pool[exchange.value] = BitgetFuturesAPI(self.http_session_manager)
            else:
                raise ValueError(f"Exchange {exchange} is not supported for ohlcv downloading!")
        return self.clients_pool[exchange.value]


    async def execute_downloading_tasks(self, tasks: list[DownloadingTask]) -> list[DownloadingOHLCVResult]:
        downloading_jobs = []
        for task in tasks:
            filepath = self.get_ohlcv_filepath(task.exchange.value, task.symbol, task.interval, task.start_timestamp, task.end_timestamp)
            if not os.path.exists(filepath):
                downloading_jobs.append(asyncio.create_task(self.download_and_save_ohlcv(task, filepath)))

        results = await asyncio.gather(*downloading_jobs)
        return results



    def get_ohlcv_filepath(self, exchange_name: str, symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> str:
        if exchange_name == "binance_futures":
            subfolder = "binance/futures"
        elif exchange_name == "binance_spot":
            subfolder = "binance/spot"
        elif exchange_name == "bybit_futures":
            subfolder = "bybit/futures"
        elif exchange_name == "bitget_futures":
            subfolder = "bitget/futures"
        else:
            raise ValueError(f"Exchange {exchange_name} is not supported for ohlcv downloading!")
        
        return f"{self.data_dir}/{subfolder}/{symbol}_{interval}_{str(start_timestamp)}_{str(end_timestamp)}.csv"
    

    async def download_and_save_ohlcv(self, task:DownloadingTask, filepath: str) -> DownloadingOHLCVResult:
        exchange_name = task.exchange.value
        print(f"Downloading {task.symbol} {task.interval}: {task.start_timestamp}-{task.end_timestamp} from {exchange_name}")
        try:
            client = await self.get_client(task.exchange)
            ohlcv = await client.fetch_ohlcv(task.symbol, task.interval, task.start_timestamp, task.end_timestamp)
            save_np_to_csv(filepath=filepath, data=ohlcv)
            print(f"{task.symbol} {task.interval}: {task.start_timestamp}-{task.end_timestamp} from {exchange_name} saved at {filepath}")
            return DownloadingOHLCVResult(
                exchange=task.exchange,
                symbol=task.symbol,
                interval=task.interval,
                start_timestamp=task.start_timestamp,
                end_timestamp=task.end_timestamp,
                ohlcv=ohlcv,
                status="OK"
            )
        except NoExchangeDataForSymbolException as e:
            print(f"Failed to download {task.symbol} {task.interval}: {task.start_timestamp}-{task.end_timestamp} from {exchange_name}")
            return DownloadingOHLCVResult(
                exchange=task.exchange,
                symbol=task.symbol,
                interval=task.interval,
                start_timestamp=task.start_timestamp,
                end_timestamp=task.end_timestamp,
                ohlcv=None,
                status="FAILED"
            )
    

    async def get_ohlcv(self, exchange: Exchanges, symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> np.ndarray:
        filepath = self.get_ohlcv_filepath(exchange.value, symbol, interval, start_timestamp, end_timestamp)
        if not os.path.exists(filepath):
            task = DownloadingTask(
                exchange=exchange,
                symbol=symbol,
                interval=interval,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp
            )
            ohlcv_result = await self.download_and_save_ohlcv(task, filepath)
            ohlcv = ohlcv_result.ohlcv
        else:
            ohlcv = np.loadtxt(filepath, delimiter=',')
        return ohlcv
    

    async def get_symbol_params(self, exchange: Exchanges, symbol: str) -> dict:
        client = await self.get_client(exchange)
        params = await client.get_symbol_params(symbol)
        return params


def save_np_to_csv(filepath: str, data: np.array, delimiter: str = ','):
    directory = os.path.dirname(filepath)
    # if not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)
    np.savetxt(filepath, data, delimiter=delimiter)
