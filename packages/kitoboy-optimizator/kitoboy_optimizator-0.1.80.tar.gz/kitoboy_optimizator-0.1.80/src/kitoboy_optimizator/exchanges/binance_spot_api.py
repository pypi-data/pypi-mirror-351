import binance
from binance.exceptions import BinanceAPIException
from binance.enums import HistoricalKlinesType
import logging
import numpy as np
import asyncio
from .utils.filter_row_within_time_range import filter_rows_within_time_range
from .exceptions import NoExchangeDataForSymbolException
from .schemas.symbol_params_schema import SymbolParams

logger = logging.getLogger(__name__)
# DATA_SIZE_LIMIT = 5


kline_intervals = {
        '1m': '1m', 1: '1m',
        '3m': '3m', 3: '3m',
        '5m': '5m', 5: '5m',
        '15m': '15m', 15: '15m',
        '30m': '30m', 30: '30m',
        '1h': '1h', 60: '1h',
        '2h': '2h', 120: '2h',
        '4h': '4h', 240: '4h',
        '6h': '6h', 360: '6h',
        '12h': '12h', 720: '12h',
        '1d': '1d', 'D': '1d',
        '1w': '1w', 'W': '1w',
        '1M': '1M', 'M': '1M'   
    }


class BinanceSpotAPI():
    EXCHANGE_NAME = "binance_spot"
    

    def __init__(self, api_key: str| None = None, api_secret: str| None = None):
        self.client = binance.Client(testnet=False, api_key=api_key, api_secret=api_secret)
        logger.debug("BinanceAPI initiated!")


    @property
    def exchange_name(self) -> str:
        return self.EXCHANGE_NAME
    

    async def fetch_ohlcv(self, symbol: str, interval: str, start_timestamp: int, end_timestamp: int) -> np.ndarray:
        klines_type = HistoricalKlinesType.SPOT
        client = binance.Client(testnet=False)
        interval_corrected = kline_intervals[interval]

        ohlcv = []
        since = start_timestamp
        end = end_timestamp
        try:
            while since < end:
                klines = client.get_historical_klines(
                    symbol=symbol,
                    interval=interval_corrected,
                    start_str=str(since),
                    end_str=str(end),
                    klines_type=klines_type
                )
                if not klines:
                    break

                ohlcv.extend(klines)
                # Update start_timestamp for the next batch
                since = int(klines[-1][0]) + 1
                await asyncio.sleep(0.5) 

            result_ohlcv = np.array(ohlcv)[:, :6].astype(float)
            return filter_rows_within_time_range(data=result_ohlcv, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

        except BinanceAPIException as e:
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
        
    
    async def get_symbol_params(self, symbol) -> dict:
        client = binance.Client(testnet=False)
        symbols_info = client.get_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))

        return SymbolParams(
            symbol=symbol,
            price_tick_size=symbol_info['filters'][0]['tickSize'],
            qty_step_size=symbol_info['filters'][1]['stepSize'],
            min_qty=symbol_info['filters'][1]['minQty']
        )