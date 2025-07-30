class NoExchangeDataForSymbolException(Exception):

    def __init__(self, message: str, symbol: str, exchange_name: str):
        self.message = message
        self.symbol = symbol
        self.exchange_name = exchange_name

    def __str__(self):
        return 'NoExchangeDataForSymbolException: %s' % self.message