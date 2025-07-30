import unittest
import asyncio
import logging

from kitoboy_optimizator.exchanges.abstract.exchange_api_adapter import ExchangeApiAdapter
from kitoboy_optimizator.exchanges import BinanceSpotAPI


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    # filename="tests.log"
)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logger = logging.getLogger("kitoboy-optimizator")


class TestMacro(unittest.TestCase):

    def setUp(self) -> None:
        self.api_client = BinanceSpotAPI()
        return super().setUp()
    

    def tearDown(self) -> None:
        return super().tearDown()
    

    def test_get_symbol_info(self):
        symbol = "BTCUSDT"
        asyncio.run(get_symbol_info(self.api_client, symbol))
        self.assertEqual(1, 1)

    
    def test_get_historical_klines(self):
        symbol = "ETHUSDT"
        interval = "1h"
        start_timestamp=1685577600000 # 2023-06-01 00:00:00
        end_timestamp=1690844400000 # 2023-07-31 23:00:00
        ohlcv = asyncio.run(self.api_client.fetch_ohlcv(symbol, interval, start_timestamp, end_timestamp))
        klines_count = ohlcv.shape[0]
        first_kline_close = float(ohlcv[0][4])
        last_kline_close = float(ohlcv[-1][4])
        sum_close_prices = round(ohlcv[:, 4].sum(), 2)
        self.assertEqual(klines_count, 1464, f"Expected 1464 klines, got {klines_count}")
        self.assertEqual(first_kline_close, 1871.27, f"Expected first_kline_close = 1871.27, got {first_kline_close}")
        self.assertEqual(last_kline_close, 1856.14, f"Expected last_kline_close = 1856.14, got {last_kline_close}")
        self.assertEqual(sum_close_prices, 2719030.44, f"Expected sum_close_prices = 2719030.44, got {sum_close_prices}")



async def get_symbol_info(api_client: ExchangeApiAdapter, symbol: str):
    result = await api_client.get_symbol_params(symbol)
    print(f"test result: {result}")


if __name__ == '__main__':
    unittest.main()