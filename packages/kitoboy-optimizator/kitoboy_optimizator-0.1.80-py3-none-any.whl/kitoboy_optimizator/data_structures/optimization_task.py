from kitoboy_optimizator.enums import Exchanges, Strategies


class OptimizationTask:
    def __init__(
        self,
        id: str,
        group_id: str,
        strategy: Strategies,
        exchange: Exchanges,
        symbol: str,
        interval: str,
        loop_id: str,
        optimizer_options: dict,
        backtest_options: dict,
        forwardtest_options: dict,
    ):
        self.id = id
        self.group_id = group_id
        self.strategy = strategy
        self.exchange = exchange
        self.symbol = symbol
        self.interval = interval
        self.loop_id = loop_id
        self.optimizer_options = optimizer_options
        self.backtest_options = backtest_options
        self.forwardtest_options = forwardtest_options
