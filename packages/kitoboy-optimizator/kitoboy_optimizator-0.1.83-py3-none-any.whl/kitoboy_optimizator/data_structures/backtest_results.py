from numpy import ndarray
class BacktestResults:

    def __init__(self, net_profit: float, max_drawdown: float, log: ndarray):
        self.net_profit = net_profit
        self.max_drawdown = max_drawdown
        self.log = log