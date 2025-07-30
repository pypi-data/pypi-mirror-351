import os
from concurrent.futures import ProcessPoolExecutor
import asyncio
from typing import Callable
import logging

from kitoboy_optimizator.enums import Exchanges
from kitoboy_optimizator.downloader import HistoricalDataManager
from kitoboy_optimizator.data_structures import OptimizationTask, DownloadingOHLCVResult
from kitoboy_optimizator.utils import (
    generate_optimization_tasks_list,
    generate_downloading_tasks_list,
)
from kitoboy_optimizator.optimizer import Optimizer
from kitoboy_optimizator.http_session_manager.http_session_manager import HTTPSessionManager


logger = logging.getLogger(__name__)


class MultyOptimizer:

    def __init__(self, data_dir: str, results_dir: str, tg_id: int, http_session_manager: HTTPSessionManager):
        logger.debug("Multioptimizator start init")
        # if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
        self.http_session_manager = http_session_manager
        self.data_manager = HistoricalDataManager(data_dir, http_session_manager)
        self.results_dir = results_dir
        self.tg_id = tg_id
        self.optimization_tasks = []
    
    @property
    def tasks_count(self) -> int:
        return len(self.optimization_tasks)


    async def prepare_for_execution(
        self,
        symbols: list[str],
        intervals: list[str],
        strategies: list,
        exchanges: list[Exchanges],
        optimizer_options: dict,
        backtest_options: dict,
        forwardtest_options: dict,
    ):
        results: list[DownloadingOHLCVResult] = await self.prepare_ohlcv(
            symbols=symbols,
            intervals=intervals,
            start_timestamp=optimizer_options.get('start_timestamp'),
            end_timestamp=optimizer_options.get('end_timestamp'),
            exchanges=exchanges,
            missing_datasets=[]
        )

        missing_data = [{"exchange": result.exchange, "symbol": result.symbol, "interval": result.interval} for result in results if result.ohlcv is None]
        
        results: list[DownloadingOHLCVResult] = await self.prepare_ohlcv(
            symbols=symbols,
            intervals=intervals,
            start_timestamp=forwardtest_options.get('start_timestamp'),
            end_timestamp=forwardtest_options.get('end_timestamp'),
            exchanges=exchanges,
            missing_datasets=missing_data
        )

        missing_data.extend([{"exchange": result.exchange, "symbol": result.symbol, "interval": result.interval} for result in results if result.ohlcv is None])


        self.optimization_tasks = await self.prepare_optimization_tasks(
            symbols=symbols,
            intervals=intervals,
            exchanges=exchanges,
            strategies=strategies,
            optimizer_options=optimizer_options,
            backtest_options=backtest_options,
            forwardtest_options=forwardtest_options,
            missing_datasets=missing_data
        )

        for task in self.optimization_tasks:
            if {"exchange": task.exchange, "symbol": task.symbol, "interval": task.interval} in missing_data:
                # print(f"No historical data for optimization or forward test for {task.exchange.value} {task.symbol} {task.interval}. Skipping...")
                self.optimization_tasks.remove(task)
            
        print(f"{self.tasks_count} optimization tasks ready for execution!")

    


    async def prepare_ohlcv(
        self,
        symbols: list[str],
        intervals: list[str],
        start_timestamp: int,
        end_timestamp: int,
        exchanges: list[Exchanges],
        missing_datasets: list[dict]       
    ):
        downloading_tasks = generate_downloading_tasks_list(
            symbols=symbols,
            intervals=intervals,
            start=start_timestamp,
            end=end_timestamp,
            exchanges=exchanges,
            missing_datasets=missing_datasets
        )
        logger.debug(f"Downloading tasks generated ({len(downloading_tasks)})")
        return await self.data_manager.execute_downloading_tasks(downloading_tasks)


    async def prepare_optimization_tasks(
        self,
        symbols: list[str],
        intervals: list[str],
        exchanges: list[Exchanges],
        strategies: list[Callable],
        optimizer_options: dict,
        backtest_options: dict,
        forwardtest_options: dict,
        missing_datasets: list[dict]
    ) -> list[OptimizationTask]:
        
        optimization_tasks = generate_optimization_tasks_list(
            symbols=symbols,
            intervals=intervals,
            exchanges=exchanges,
            strategies=strategies,
            optimizer_options=optimizer_options,
            backtest_options=backtest_options,
            forwardtest_options=forwardtest_options,
            missing_datasets=missing_datasets
        )

        return optimization_tasks
        

    @staticmethod
    def sync_wrapper_execute_optimization_task(task_data):
        """
        Synchronous wrapper for the optimization task to be executed in the process pool.
        This function should handle converting the async `__execute_optimization_task` logic
        into a synchronous call, possibly using asyncio.run if needed.
        """
        try:
            # Create a new event loop for this process
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize a new MultyOptimizer instance with task data
            optimizer = MultyOptimizer(
                data_dir=task_data['data_dir'],
                results_dir=task_data['results_dir'],
                tg_id=task_data['tg_id'],
                http_session_manager=None  # Will be recreated in the process
            )
            
            result = loop.run_until_complete(optimizer.__execute_optimization_task(task_data['task']))
            loop.close()
            return result
            
        except Exception as e:
            print(f"FAILED to execute optimization task: {e}\n {task_data['task'].strategy.name} {task_data['task'].symbol} {task_data['task'].interval} {task_data['task'].exchange.value}\n")
            return None
        


    async def execute_optimizations(self, max_cpu_threads=1):
        available_cpu_cores = os.cpu_count()

        if max_cpu_threads > 0:
            cores_for_use = min(available_cpu_cores, max_cpu_threads)
        elif max_cpu_threads < 0:
            cores_for_use = max(1, available_cpu_cores + max_cpu_threads)
        else:
            cores_for_use = available_cpu_cores

        print(f"Доступно {available_cpu_cores} вычислительных потоков!")
        if cores_for_use == available_cpu_cores:
            print("LET'S MAKE CPU SCREAM! $)")
        else:
            print(f"Optimization will use {cores_for_use} threads")

        # for task in self.optimization_tasks:
        #     await self.__execute_optimization_task(task)
        # Prepare task data for each optimization task
        task_data_list = [
            {
                'task': task,
                'data_dir': self.data_manager.data_dir,
                'results_dir': self.results_dir,
                'tg_id': self.tg_id
            } for task in self.optimization_tasks
        ]
        
        with ProcessPoolExecutor(max_workers=cores_for_use) as executor:
            # Map each job to a separate process with its required data
            list(executor.map(self.sync_wrapper_execute_optimization_task, task_data_list))


    async def __execute_optimization_task(self, task: OptimizationTask):
        logger.debug(f"OPTIM TASK: {task}")
        strategy_class = task.strategy
        optimizer = Optimizer(
            optimization_id=task.id,
            optimization_group_id=task.group_id,
            tg_id=self.tg_id,
            strategy=strategy_class,
            symbol=task.symbol,
            optimizer_options=task.optimizer_options,
            backtest_options=task.backtest_options,
            forwardtest_options=task.forwardtest_options,
            exchange=task.exchange,
            interval=task.interval,
            loop_id=task.loop_id,
            data_manager=self.data_manager,
            results_dir=self.results_dir
        )
        await optimizer.execute()
