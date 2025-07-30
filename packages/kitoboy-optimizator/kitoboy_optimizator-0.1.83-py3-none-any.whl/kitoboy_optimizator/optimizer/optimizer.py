import random
import numpy as np
import datetime as dt
import os
import logging
from colorama import Fore, Back, Style

from kitoboy_optimizator.report_builder import (
    StrategyTestResultCalculator,
    Reporter,
    HTMLBuilder,
)
from kitoboy_optimizator.backtester import Backtester
from kitoboy_optimizator.downloader import HistoricalDataManager
from kitoboy_optimizator.enums import Exchanges
from kitoboy_optimizator.data_structures import BacktestResults


logger = logging.getLogger("kitoboy-optimizator")


class Optimizer:

    def __init__(
        self,
        optimization_id: str,
        optimization_group_id: str,
        strategy,
        symbol: str,
        optimizer_options: dict,
        backtest_options: dict,
        forwardtest_options: dict,
        exchange: Exchanges,
        # ohlcv: np.ndarray,
        interval: str,
        loop_id: str,
        data_manager: HistoricalDataManager,
        # symbol_params: dict,
        results_dir: str,
        tg_id: int,
    ):
        self.strategy = strategy
        self.iterations = optimizer_options.get("iterations")
        self.optimization_type = optimizer_options.get("optimization_type")
        self.min_max_drawdown = optimizer_options.get("min_max_drawdown")
        self.population_size = optimizer_options.get("population_size")
        self.max_population_size = optimizer_options.get("max_population_size")
        self.mutation_probability = optimizer_options.get("mutation_probability")
        self.assimilation_probability = optimizer_options.get(
            "assimilation_probability"
        )
        self.final_results = optimizer_options.get("final_results")
        self.backtest_options = backtest_options
        self.forwardtest_options = forwardtest_options
        self.exchange = exchange
        self.exchange_name = exchange.value
        self.interval = interval
        self.loop_id = loop_id
        self.start_timestamp = optimizer_options.get("start_timestamp")
        self.end_timestamp = optimizer_options.get("end_timestamp")
        self.data_manager = data_manager
        self.symbol = symbol
        self.start_forwardtest_after_optimization = optimizer_options.get(
            "start_forwardtest_after_optimization"
        )

        self.backtester = Backtester()
        self.reporter = Reporter(
            optimization_id=optimization_id,
            optimization_group_id=optimization_group_id,
            tg_id=tg_id,
            strategy_name=strategy.name,
            exchange_name=exchange.value,
            symbol=symbol,
            interval=interval,
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            reports_dir=os.path.join(results_dir, "reports"),
        )
        self.html_builder = HTMLBuilder()
        self.html_builder.init_bootstrap_folder(os.path.join(results_dir, "html"))
        self.results_dir = results_dir

    @property
    def actual_population_size(self) -> int:
        return len(self.population)

    async def execute(self):
        title = "OPTIMIZATION STARTED"
        print(
            f"\n{title}: {self.exchange_name} {self.strategy.name} {self.symbol} {self.interval} (loop #{self.loop_id})"
        )
        self.reporter.report_start_optimization()
        # logger.debug(f"EXECUTE {self}")
        await self.prepare_execution()
        if self.ohlcv is None:
            print(
                "No historical data for {self.symbol} {self.interval}. Exiting loop #{self.loop_id}"
            )
            return 0

        for j in range(self.iterations):
            self.iteration = j + 1
            self.select()
            self.cross()
            self.mutate()
            self.expand()
            self.assimilate()
            self.elect()
            self.kill()

        # print("Let's process results!")
        for i in range(self.final_results):
            report = await self.process_results()
            print(report)
            del self.population[self.best_score]
            self.best_score = self.__get_best_score_of_population(self.population)

        await self.reporter.finish_optimisation(loop_id=self.loop_id)
        return 1

    async def prepare_execution(self):
        self.symbol_params = await self.data_manager.get_symbol_params(
            exchange=self.exchange, symbol=self.symbol
        )
        self.ohlcv = await self.data_manager.get_ohlcv(
            exchange=self.exchange,
            symbol=self.symbol,
            interval=self.interval,
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
        )
        try:
            self.create_initial_population()
        except Exception as e:
            logger.critical(f"Error of creating population: {e}")

    def create_initial_population(self):
        self.samples = [
            [random.choice(j) for j in self.strategy.opt_parameters.values()]
            for i in range(self.population_size)
        ]
        self.population = {
            k[0]: (v, k[1], k[2])
            for k, v in zip(map(self.fit, self.samples), self.samples)
        }
        self.sample_length = len(self.strategy.opt_parameters)
        self.best_score = float("-inf")
        self.reporter.report_initial_population(self.population)
        return self.population

    def fit(self, sample):
        log = self.backtester.execute_backtest(
            strategy=self.strategy,
            strategy_params=sample,
            ohlcv=self.ohlcv,
            symbol_params=self.symbol_params,
            backtest_options=self.backtest_options,
        )
        metrics = StrategyTestResultCalculator.get_optimized_metrics(
            log, self.backtest_options.get("initial_capital")
        )

        if self.optimization_type == 0:
            score = metrics[0]
        else:
            if metrics[1] > self.min_max_drawdown:
                score = metrics[0] / metrics[1]
            else:
                score = 0

        metrics = (score, metrics[0], metrics[1])
        return metrics

    def select(self):
        if (random.randint(0, 1) == 0) or (self.actual_population_size <= 2):
            score = self.__get_best_score_of_population(self.population)
            parent_1 = self.population[score][0]
            population_copy = self.population.copy()
            del population_copy[score]
            if len(population_copy) < 2:
                population_copy = self.create_new_population(10)
            parent_2 = random.choice(list(population_copy.values()))[0]
            self.parents = [parent_1, parent_2]
        else:
            parents = random.sample(list(self.population.values()), 2)
            self.parents = [parents[0][0], parents[1][0]]

    def cross(self):
        r_number = random.randint(0, 1)

        if r_number == 0:
            delimiter = random.randint(1, self.sample_length - 1)
            self.child = self.parents[0][:delimiter] + self.parents[1][delimiter:]
        else:
            delimiter_1 = random.randint(1, self.sample_length // 2 - 1)
            delimiter_2 = random.randint(
                self.sample_length // 2 + 1, self.sample_length - 1
            )
            self.child = (
                self.parents[0][:delimiter_1]
                + self.parents[1][delimiter_1:delimiter_2]
                + self.parents[0][delimiter_2:]
            )

    def mutate(self):
        if random.randint(0, 100) < self.mutation_probability:
            gene_number = random.randint(0, self.sample_length - 1)
            gene_value = random.choice(
                list(self.strategy.opt_parameters.values())[gene_number]
            )
            self.child[gene_number] = gene_value

    def expand(self):
        metrics = self.fit(self.child)
        self.population[metrics[0]] = (self.child, metrics[1], metrics[2])
        self.reporter.report_expand_results(self.population[metrics[0]])
        return self.population[metrics[0]]

    def assimilate(self):
        if random.randint(0, 1000) / 10 < self.assimilation_probability:
            samples = [
                [random.choice(j) for j in self.strategy.opt_parameters.values()]
                for i in range(len(self.population) // 2)
            ]
            population = {
                k[0]: (v, k[1], k[2]) for k, v in zip(map(self.fit, samples), samples)
            }
            self.population.update(population)
            self.reporter.report_assimilation_results(population)
            return population

    def elect(self):
        if self.best_score < self.__get_best_score_of_population(self.population):
            self.best_score = self.__get_best_score_of_population(self.population)
            self.reporter.report_new_best_scores(self.iteration, self.best_score)
        return self.best_score

    def kill(self):
        while len(self.population) > self.max_population_size:
            del self.population[min(self.population)]

    def create_new_population(self, population_size: int):
        samples = [
            [random.choice(j) for j in self.strategy.opt_parameters.values()]
            for i in range(population_size)
        ]
        population = {
            k[0]: (v, k[1], k[2]) for k, v in zip(map(self.fit, samples), samples)
        }
        return population

    def __get_best_score_of_population(self, population: np.ndarray) -> float:
        if len(population):
            return max(population)
        else:
            return 0.0

    async def process_results(self) -> str:
        # print("Process results")
        logger.debug("PROCESS RESULTS!")
        logger.debug(f"POPULATION: {len(self.population)} units")
        result_id = f"{int(dt.datetime.now().timestamp())}_{random.randint(0, 1000)}"
        report = f"\nID: {result_id} ({self.symbol} {self.interval} {self.exchange_name} { self.strategy.name})"
        # for key, value in self.population.items():
        #     logger.debug(f"{key} => {value}")
        best_params = self.population[self.best_score][0]
        backtest_results = await self.get_backtest_results(
            strategy_params=best_params,
            initial_capital=self.backtest_options.get("initial_capital"),
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
        )
        if self.pass_backtest_results_filter(backtest_results):
            report += f"\nBacktest results {Back.GREEN}{Fore.BLACK} PASSED! {Style.RESET_ALL} (Profit:{backtest_results.net_profit} Drawdown: {backtest_results.max_drawdown})"
            if self.start_forwardtest_after_optimization:
                forwardtest_results = await self.get_backtest_results(
                    strategy_params=best_params,
                    initial_capital=self.backtest_options.get("initial_capital"),
                    start_timestamp=self.forwardtest_options.get("start_timestamp"),
                    end_timestamp=self.forwardtest_options.get("end_timestamp"),
                )
                if self.pass_forwardtest_results_filter(forwardtest_results):
                    await self.create_and_save_params_txt(best_params, result_id)
                    self.reporter.backtest_results_report(
                        result_id,
                        best_params,
                        backtest_results,
                        self.start_timestamp,
                        self.end_timestamp,
                    )
                    self.reporter.backtest_results_report(
                        result_id,
                        best_params,
                        forwardtest_results,
                        self.forwardtest_options.get("start_timestamp"),
                        self.forwardtest_options.get("end_timestamp"),
                    )
                    await self.create_and_save_html_report(
                        backtest_results=backtest_results,
                        start_timestamp=self.start_timestamp,
                        end_timestamp=self.end_timestamp,
                        result_id=result_id,
                    )
                    await self.create_and_save_html_report(
                        backtest_results=forwardtest_results,
                        start_timestamp=self.forwardtest_options.get("start_timestamp"),
                        end_timestamp=self.forwardtest_options.get("end_timestamp"),
                        result_id=result_id,
                    )
                    report += f"\nForwardtest results {Back.GREEN}{Fore.BLACK} PASSED! {Style.RESET_ALL} (Profit:{forwardtest_results.net_profit} Drawdown: {forwardtest_results.max_drawdown})"
                else:
                    report += f"\nForwardtest results {Back.RED}{Fore.BLACK} NOT PASSED! {Style.RESET_ALL} (Profit:{forwardtest_results.net_profit} Drawdown: {forwardtest_results.max_drawdown})"
                    return report
            else:
                await self.create_and_save_params_txt(best_params, result_id)
                self.reporter.backtest_results_report(
                    result_id,
                    best_params,
                    backtest_results,
                    self.start_timestamp,
                    self.end_timestamp,
                )
                await self.create_and_save_html_report(
                    backtest_results=backtest_results,
                    start_timestamp=self.start_timestamp,
                    end_timestamp=self.end_timestamp,
                    result_id=result_id,
                )
        else:
            report += f"\nBacktest results NOT PASSED! (Profit:{backtest_results.net_profit} Drawdown: {backtest_results.max_drawdown})"

            return report
        # del self.population[self.best_score]
        # self.best_score = self.__get_best_score_of_population(self.population)
        return report

    async def get_backtest_results(
        self,
        strategy_params: dict,
        initial_capital: float,
        start_timestamp: int,
        end_timestamp: int,
    ):
        ohlcv = await self.data_manager.get_ohlcv(
            exchange=self.exchange,
            symbol=self.symbol,
            interval=self.interval,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )
        backtest_log = self.backtester.execute_backtest(
            strategy=self.strategy,
            strategy_params=strategy_params,
            ohlcv=ohlcv,
            symbol_params=self.symbol_params,
            backtest_options=self.backtest_options,
        )
        net_profit, max_drawdown = StrategyTestResultCalculator.get_optimized_metrics(
            backtest_log, initial_capital
        )
        results = BacktestResults(
            net_profit=net_profit, max_drawdown=max_drawdown, log=backtest_log
        )
        return results

    def pass_backtest_results_filter(self, backtest_results: BacktestResults):
        filters = self.backtest_options.get("filters")
        return self.pass_results_filters(backtest_results, filters)

    def pass_forwardtest_results_filter(self, forwardtest_results: BacktestResults):
        filters = self.forwardtest_options.get("filters")
        return self.pass_results_filters(forwardtest_results, filters)

    def pass_results_filters(
        self, backtest_results: BacktestResults, filters: dict | None
    ) -> bool:
        if filters is None:
            return True

        if filters.get("min_profit") is None:
            min_profit_filter_result = True
        else:
            min_profit_filter_result = backtest_results.net_profit >= filters.get(
                "min_profit"
            )

        if filters.get("max_drawdown") is None:
            max_drawdown_filter_result = True
        else:
            max_drawdown_filter_result = backtest_results.max_drawdown <= filters.get(
                "max_drawdown"
            )

        return min_profit_filter_result and max_drawdown_filter_result

    async def create_and_save_html_report(
        self,
        backtest_results: BacktestResults,
        start_timestamp: int,
        end_timestamp: int,
        result_id: str,
    ):

        html = self.html_builder.generate_html(
            strategy_name=self.strategy.name,
            exchange_name=self.exchange_name,
            symbol=self.symbol,
            interval=self.interval,
            log=backtest_results.log,
            initial_capital=self.backtest_options.get("initial_capital"),
        )
        start_date = dt.datetime.fromtimestamp(
            round(0.001 * start_timestamp),
            tz=dt.UTC
        ).strftime("%Y-%m-%d")
        end_date = dt.datetime.fromtimestamp(
            round(0.001 * end_timestamp),
            tz=dt.UTC
        ).strftime("%Y-%m-%d")

        html_file_path = os.path.join(
            f"{self.results_dir}/{self.exchange_name}/{self.strategy.name}/{self.symbol}",
            f"{self.symbol}_{self.interval}_{result_id}_{start_date}_{end_date}_{backtest_results.net_profit}_{backtest_results.max_drawdown}.html",
        )

        html_file_dir = os.path.dirname(html_file_path)

        # if not os.path.exists(html_file_dir):
        os.makedirs(html_file_dir, exist_ok=True)

        start_time = dt.datetime.fromtimestamp(
            round(0.001 * self.start_timestamp),
            tz=dt.UTC
        ).strftime("%Y-%m-%d %H:%M:%S")
        end_time = dt.datetime.fromtimestamp(
            round(0.001 * self.end_timestamp),
            tz=dt.UTC
        ).strftime("%Y-%m-%d %H:%M:%S")

        if html:
            with open(html_file_path, "w") as f:
                f.write(html)
        else:
            print(
                f"{self.strategy.name} {self.symbol} {self.interval} {self.exchange_name} {result_id} 0 сделок с {start_time} по {end_time}"
            )
        return html

    async def create_and_save_params_txt(
        self,
        strategy_params: dict,
        result_id: str,
    ):
        txt = self.__generate_txt(strategy_params)

        txt_file_path = os.path.join(
            f"{self.results_dir}/{self.exchange_name}/{self.strategy.name}/{self.symbol}",
            f"{self.symbol}_{self.interval}_{result_id}.txt",
        )
        txt_file_dir = os.path.dirname(txt_file_path)

        # if not os.path.exists(txt_file_dir):
        os.makedirs(txt_file_dir, exist_ok=True)

        if txt:
            with open(txt_file_path, "w") as f:
                f.write(txt)
        else:
            print(f"TXT is none!\n {txt_file_path}")

        return txt

    def __generate_txt(self, strategy_params: dict) -> str:
        result = ""
        for key, param_name in enumerate(self.strategy.opt_parameters.keys()):
            if isinstance(strategy_params[key], np.ndarray):
                param_value = list(strategy_params[key])
            else:
                param_value = strategy_params[key]
            result += f"{param_name} = {param_value}\n"
        return result
