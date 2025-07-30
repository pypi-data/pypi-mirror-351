from enum import Enum


class HttpMethod(Enum):
    GET = "get"
    POST = "post"


class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"