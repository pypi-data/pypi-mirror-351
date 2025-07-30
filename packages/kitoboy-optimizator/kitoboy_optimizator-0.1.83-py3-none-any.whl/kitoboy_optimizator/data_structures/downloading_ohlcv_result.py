from pydantic import BaseModel
import numpy as np

from kitoboy_optimizator.enums import Exchanges


class DownloadingOHLCVResult(BaseModel):

    exchange: Exchanges
    symbol: str
    interval: str
    start_timestamp: int
    end_timestamp: int
    ohlcv: np.ndarray | None
    status: str

    class Config:
        arbitrary_types_allowed = True