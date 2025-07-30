from pydantic import BaseModel

class SymbolParams(BaseModel):
    symbol: str
    price_tick_size: str
    qty_step_size: str
    min_qty: str
