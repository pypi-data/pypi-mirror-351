import numba as nb
import numpy as np

class StrategyTestResultCalculator:

    @classmethod
    def get_optimized_metrics(cls, log: np.ndarray, initial_capital: float):
        if log.shape[0] > 0:
            pnl = log[8::11]
            net_profit_per, max_drawdown = cls.__calculate_optimized_metrics(
                pnl, initial_capital
            )
        else:
            net_profit_per, max_drawdown = (0.0, 0.0)

        return (net_profit_per, max_drawdown)

    @staticmethod
    @nb.jit(
        (nb.float64[:], nb.float64), nopython=True, nogil=True, cache=True
    )
    def __calculate_optimized_metrics(pnl, initial_capital):
        net_profit_per = round(pnl.sum() / initial_capital * 100, 2)
        equity = np.concatenate(
            (np.array([initial_capital]), pnl)
        ).cumsum()
        max_equity = equity[0]
        max_drawdown = 0.0
     
        for i in range(1, equity.shape[0]):
            if equity[i] > max_equity:
                max_equity = equity[i]

            if equity[i] < equity[i - 1]:
                min_equity = equity[i]
                drawdown = -(min_equity / max_equity - 1) * 100

                if drawdown > max_drawdown:
                    max_drawdown = round(drawdown, 2)

        metrics = (net_profit_per, max_drawdown)
        return metrics
