import uuid
from kitoboy_optimizator.enums import Exchanges, Strategies
from kitoboy_optimizator.data_structures import DownloadingTask, OptimizationTask


def generate_downloading_tasks_list(
    symbols: list[str], intervals: list[str], start: int, end: int, exchanges: list[Exchanges], missing_datasets: list[dict]
) -> list[DownloadingTask]:
    tasks = []
    for symbol in set(symbols):
        for interval in intervals:
            for exchange in exchanges:
                if {
                    "exchange": exchange,
                    "symbol": symbol,
                    "interval": interval
                } in missing_datasets:
                    break
                tasks.append(
                    DownloadingTask(
                        exchange=exchange,
                        symbol=symbol,
                        interval=interval,
                        start_timestamp=start,
                        end_timestamp=end,
                    )
                )
    return tasks


def generate_optimization_tasks_list(
    symbols: list[str],
    intervals: list[str],
    exchanges: list[Exchanges],
    strategies: list[Strategies],
    optimizer_options: dict,
    backtest_options: dict,
    forwardtest_options: dict,
    missing_datasets: list[dict]
) -> list[OptimizationTask]:
    tasks = []
    super_id = str(uuid.uuid4())
    for strategy in strategies:
        for exchange in exchanges:
            for symbol in symbols:
                for interval in intervals:
                    if {"exchange": exchange, "symbol": symbol, "interval": interval} in missing_datasets:
                        break
                    
                    for i in range(optimizer_options.get("number_of_starts")):
                        optimization_id = str(uuid.uuid4())
                        tasks.append(
                            OptimizationTask(
                                strategy=strategy,
                                exchange=exchange,
                                symbol=symbol,
                                interval=interval,
                                loop_id=str(i+1),
                                optimizer_options=optimizer_options,
                                backtest_options=backtest_options,
                                forwardtest_options=forwardtest_options,
                                id=optimization_id,
                                group_id=super_id
                            )
                        )
    return tasks
