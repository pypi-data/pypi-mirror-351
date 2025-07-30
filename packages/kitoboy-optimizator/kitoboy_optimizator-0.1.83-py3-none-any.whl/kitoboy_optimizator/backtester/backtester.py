import numpy as np

from kitoboy_optimizator.exchanges.schemas.symbol_params_schema import SymbolParams

class Backtester():

    def __init__(self):
        pass


    def execute_backtest(
        self,
        strategy,
        strategy_params: dict,
        ohlcv: np.ndarray,
        symbol_params: SymbolParams,
        backtest_options: dict
    ) -> np.ndarray:
        # print("Let's execute backtest!")
        # print(f"{strategy}\n{strategy_params}\nOHLCV: {len(ohlcv)}\n===========")
        try:
            strategy = strategy(
                ohlcv=ohlcv,
                symbol_params={
                    "symbol": symbol_params.symbol, 
                    "price_precision": float(symbol_params.price_tick_size),
                    "qty_precision": float(symbol_params.qty_step_size)
                },
                opt_parameters=strategy_params
            )
        except Exception as e:
            print(f"Strategy start error: {e}\nStrategy: {strategy}")
        initial_capital = backtest_options.get('initial_capital')
        try:
            log = strategy.start(
                margin_type=backtest_options.get('margin_type'),             # 0 - 'ISOLATED', 1 - 'CROSSED'
                direction=backtest_options.get('direction'),              # 0 - 'all', 1 - 'longs', 2 - 'shorts'
                initial_capital=initial_capital,
                min_capital=backtest_options.get('min_capital'),
                commission=backtest_options.get('commission'),
                order_size_type=backtest_options.get('order_size_type'),         # 0 - 'PERCENT', 1 - 'CURRENCY'
                order_size=backtest_options.get('order_size'),
                leverage=backtest_options.get('leverage')
            )
        except Exception as e:
            print(f"Backtest execution error: {e}")
        # print("Backtest executed successful!")
        return log