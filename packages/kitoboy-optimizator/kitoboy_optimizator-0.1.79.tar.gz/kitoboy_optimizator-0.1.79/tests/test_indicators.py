import unittest
import asyncio
import logging

from kitoboy_optimizator.exchanges.abstract.exchange_api_adapter import ExchangeApiAdapter
from kitoboy_optimizator.exchanges.bitget.bitget_futures_api import BitgetFuturesAPI
from kitoboy_optimizator.http_session_manager.http_session_manager import HTTPSessionManager


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
        self.http_session_manager = HTTPSessionManager()
        self.api_client = BitgetFuturesAPI(http_session_manager=self.http_session_manager)
        return super().setUp()
    

    def tearDown(self) -> None:
        asyncio.run(self.http_session_manager.close_session())
        return super().tearDown()
    

    def test_get_symbol_info(self):
        symbol = "BTCUSDT"
        asyncio.run(get_symbol_info(self.api_client, symbol))
        self.assertEqual(1, 1)


async def get_symbol_info(api_client: ExchangeApiAdapter, symbol: str):
    result = await api_client.get_symbol_params(symbol)
    print(f"test result: {result}")


if __name__ == '__main__':
    unittest.main()