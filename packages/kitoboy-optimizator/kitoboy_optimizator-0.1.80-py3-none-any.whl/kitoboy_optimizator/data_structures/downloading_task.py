from pydantic import BaseModel

from kitoboy_optimizator.enums import Exchanges


class DownloadingTask(BaseModel):

    exchange: Exchanges
    symbol: str
    interval: str
    start_timestamp: int
    end_timestamp: int
