import pandas as pd
import numpy as np
from .utils import create_bootstrap_folder

class HTMLBuilder():
    def __init__(self):
        self.bootstrap_relative_path = "../../../html/bootstrap/"
        pass


    def init_bootstrap_folder(self, base_dir: str):
        create_bootstrap_folder(base_dir)


    def generate_html(self, strategy_name: str, exchange_name: str, symbol: str, interval: str, log: np.ndarray, initial_capital: float) -> str|None:
        preprocessed_log = self.log_preprocessing(log)
        # print(f"log: {log}")
        # print(f"preprocessed log: {preprocessed_log}")
        if preprocessed_log.shape[0] > 0:
            performance_metrics = self.calculate_performance(preprocessed_log, initial_capital)
            return self.create_html(
                strategy_name=strategy_name,
                exchange_name=exchange_name,
                symbol=symbol,
                interval=interval,
                log=preprocessed_log,
                performance_metrics=performance_metrics)
        else:
            return None
        


    def log_preprocessing(self, result_log: np.ndarray) -> np.ndarray:
        deal_type_keywords = {
            0: 'long',
            1: 'short'
        }
        entry_signal_keywords = {
            0: 'Long',
            1: 'Short',
            2: 'Long #1',
            3: 'Long #2',
            4: 'Long #3',
            5: 'Long #4',
            6: 'Long #5',
            7: 'Long #6',
            8: 'Long #7',
            9: 'Long #8',
            10: 'Long #9',
            11: 'Long #10',
            12: 'Short #1',
            13: 'Short #2',
            14: 'Short #3',
            15: 'Short #4',
            16: 'Short #5',
            17: 'Short #6',
            18: 'Short #7',
            19: 'Short #8',
            20: 'Short #9',
            21: 'Short #10'
        }
        exit_signal_keywords = {
            0: 'Liquidation',
            1: 'Stop-loss',
            2: 'Take-profit #1',
            3: 'Take-profit #2',
            4: 'Take-profit #3',
            5: 'Take-profit #4',
            6: 'Take-profit #5',
            7: 'Take-profit #6',
            8: 'Take-profit #7',
            9: 'Take-profit #8',
            10: 'Take-profit #9',
            11: 'Take-profit #10',
            12: 'Take-profit',
            13: 'Exit long',
            14: 'Exit short'
        }
        result_log = pd.DataFrame(
            result_log.reshape(result_log.shape[0] // 11, 11),
            columns=[
                'deal_type', 'entry_signal', 'exit_signal',
                'entry_date', 'exit_date', 'entry_price',
                'exit_price', 'position_size', 'pnl',
                'pnl_per', 'commission'
            ]
        )

        for key, values in deal_type_keywords.items():
            result_log['deal_type'] = result_log['deal_type'].replace(key, values)

        for key, values in entry_signal_keywords.items():
            result_log['entry_signal'] = result_log['entry_signal'].replace(key, values)

        for key, values in exit_signal_keywords.items():
            result_log['exit_signal'] = result_log['exit_signal'].replace(key, values)

        result_log['entry_date'] = pd.to_datetime(
            pd.to_numeric(result_log['entry_date']),
            unit='ms'
        ).dt.strftime('%Y-%m-%d %H:%M')
        result_log['exit_date'] = pd.to_datetime(
            pd.to_numeric(result_log['exit_date']),
            unit='ms'
        ).dt.strftime('%Y-%m-%d %H:%M')
        return result_log


    def calculate_performance(self, log: np.ndarray, initial_capital: float) -> pd.DataFrame:
        equity = pd.concat(
            [pd.Series(initial_capital), log.pnl],
            ignore_index=True  
        ).cumsum()
        equity.index += 1

        try:
            gross_profit = log.loc[:, ['deal_type','pnl']]. \
                query('pnl > 0').groupby('deal_type'). \
                    agg('sum', numeric_only=True)
        except:
            pass
        try:
            all_gross_profit = round(
                gross_profit.pnl.sum(), 2
            )
            all_gross_profit_per = round(
                all_gross_profit / initial_capital * 100, 2
            )
        except:
             all_gross_profit = 0.0
             all_gross_profit_per = 0.0
        try:
            long_gross_profit = round(
                gross_profit.at['long', 'pnl'], 2
            )
            long_gross_profit_per = round(
                long_gross_profit / initial_capital * 100, 2
            )
        except:
            long_gross_profit = 0.0
            long_gross_profit_per = 0.0
        try:
            short_gross_profit = round(
                gross_profit.at['short', 'pnl'], 2
            )
            short_gross_profit_per = round(
                short_gross_profit / initial_capital * 100, 2
            )
        except:
            short_gross_profit = 0.0
            short_gross_profit_per = 0.0

        try:
            gross_loss = log.loc[:, ['deal_type','pnl']]. \
                query('pnl <= 0').groupby('deal_type'). \
                    agg('sum', numeric_only=True)
        except:
            pass
        try:
            all_gross_loss = round(
                abs(gross_loss.pnl.sum()), 2
            )
            all_gross_loss_per = round(
                all_gross_loss / initial_capital * 100, 2
            )
        except:
            all_gross_loss = 0.0
            all_gross_loss_per = 0.0
        try:
            long_gross_loss = round(
                abs(gross_loss.at['long', 'pnl']), 2
            )
            long_gross_loss_per = round(
                long_gross_loss / initial_capital * 100, 2
            )
        except:
            long_gross_loss = 0.0
            long_gross_loss_per = 0.0
        try:
            short_gross_loss = round(
                abs(gross_loss.at['short', 'pnl']), 2
            )
            short_gross_loss_per = round(
                short_gross_loss / initial_capital * 100, 2
            )
        except:
            short_gross_loss = 0.0
            short_gross_loss_per = 0.0

        try:
            all_net_profit = round(
                all_gross_profit - all_gross_loss, 2
            )
            all_net_profit_per = round(
                all_net_profit / initial_capital * 100, 2
            )
        except:
            all_net_profit = 0.0
            all_net_profit_per = 0.0
        try:
            long_net_profit = round(
                long_gross_profit - long_gross_loss, 2
            )
            long_net_profit_per = round(
                long_net_profit / initial_capital * 100, 2
            )
        except:
            long_net_profit = 0.0
            long_net_profit_per = 0.0
        try:
            short_net_profit = round(
                short_gross_profit - short_gross_loss, 2
            )
            short_net_profit_per = round(
                short_net_profit / initial_capital * 100, 2
            )
        except:
            short_net_profit = 0.0
            short_net_profit_per = 0.0

        try:
            max_equity = equity.iloc[0]
            all_max_drawdown = 0.0
            all_max_drawdown_per = 0.0

            for i in range(1, equity.shape[0]):
                if equity.iloc[i] > max_equity:
                    max_equity = equity.iloc[i]

                if equity.iloc[i] < equity.iloc[i - 1]:
                    min_equity = equity.iloc[i]
                    drawdown = max_equity - min_equity
                    drawdown_per = -(min_equity / max_equity - 1) * 100

                    if drawdown > all_max_drawdown:
                        all_max_drawdown = round(drawdown, 2)

                    if drawdown_per > all_max_drawdown_per:
                        all_max_drawdown_per = round(drawdown_per, 2)
        except:
            all_max_drawdown = 0.0
            all_max_drawdown_per = 0.0

        try:
            all_skew = round(log.pnl_per.skew(), 3)
        except:
            all_skew = None

        try:
            if all_gross_loss != 0:
                all_profit_factor = round(
                    all_gross_profit / all_gross_loss, 3
                )
            else:
                all_profit_factor = None
        except:
            all_profit_factor = None
        try:
            if long_gross_loss != 0:
                long_profit_factor =  round(
                    long_gross_profit / long_gross_loss, 3
                )
            else:
                long_profit_factor = None
        except:
            long_profit_factor = None
        try:
            if short_gross_loss != 0:
                short_profit_factor = round(
                    short_gross_profit / short_gross_loss, 3
                )
            else:
                short_profit_factor = None
        except:
            short_profit_factor = None

        try:
            commission_paid = log.loc[:, ['deal_type','commission']]. \
                groupby('deal_type').agg('sum', numeric_only=True)
        except:
            pass
        try:
            all_commission_paid = round(
                commission_paid.commission.sum(), 2
            )
        except:
            all_commission_paid = 0.0
        try:
            long_commission_paid = round(
                commission_paid.at['long', 'commission'], 2
            )
        except:
            long_commission_paid = 0.0
        try:
            short_commission_paid = round(
                commission_paid.at['short', 'commission'], 2
            )
        except:
            short_commission_paid = 0.0

        all_total_closed_trades = int(log.shape[0])
        long_total_closed_trades = int(
            log.query('deal_type == "long"').shape[0]
        )
        short_total_closed_trades = int(
            log.query('deal_type == "short"').shape[0]
        )

        all_number_winning_trades = int(log.query('pnl > 0').shape[0])
        long_number_winning_trades = int(
            log.query('deal_type == "long" and pnl > 0').shape[0]
        )
        short_number_winning_trades = int(
            log.query('deal_type == "short" and pnl > 0').shape[0]
        )

        all_number_losing_trades = int(log.query('pnl <= 0').shape[0])
        long_number_losing_trades = int(
            log.query('deal_type == "long" and pnl <= 0').shape[0]
        )
        short_number_losing_trades = int(
            log.query('deal_type == "short" and pnl <= 0').shape[0]
        )

        try:
            all_percent_profitable = round(
                all_number_winning_trades / 
                    all_total_closed_trades * 100,
                2
            )
        except:
            all_percent_profitable = None
        try:
            long_percent_profitable = round(
                long_number_winning_trades / 
                    long_total_closed_trades * 100,
                2
            )
        except:
            long_percent_profitable = None
        try:
            short_percent_profitable = round(
                short_number_winning_trades / 
                    short_total_closed_trades * 100,
                2
            )
        except:
            short_percent_profitable = None

        try:
            all_avg_trade = round(log.pnl.mean(), 2)
            all_avg_trade_per = round(log.pnl_per.mean(), 2)
        except:
            all_avg_trade = None
        try:
            long_avg_trade = round(
                log.query('deal_type == "long"').pnl.mean(), 2
            )
            long_avg_trade_per = round(
                log.query('deal_type == "long"').pnl_per.mean(), 2
            )
        except:
            long_avg_trade = None
        try:
            short_avg_trade = round(
                log.query('deal_type == "short"').pnl.mean(), 2
            )
            short_avg_trade_per = round(
                log.query('deal_type == "short"').pnl_per.mean(), 2
            )
        except:
            short_avg_trade = None

        try:
            all_avg_winning_trade = round(
                log.query('pnl > 0').pnl.mean(), 2
            )
            all_avg_winning_trade_per = round(
                log.query('pnl_per > 0').pnl_per.mean(), 2
            )
        except:
            all_avg_winning_trade = None
        try:
            long_avg_winning_trade = round(
                log.query('deal_type == "long" and pnl > 0'). \
                    pnl.mean(), 2
            )
            long_avg_winning_trade_per = round(
                log.query('deal_type == "long" and pnl_per > 0'). \
                    pnl_per.mean(),
                2
            )
        except:
            long_avg_winning_trade = None
        try:
            short_avg_winning_trade = round(
                log.query('deal_type == "short" and pnl > 0'). \
                    pnl.mean(), 2
            )
            short_avg_winning_trade_per = round(
                log.query('deal_type == "short" and pnl_per > 0'). \
                    pnl_per.mean(),
                2
            )
        except:
            short_avg_winning_trade = None

        try:
            all_avg_losing_trade = round(
                abs(log.query('pnl <= 0').pnl.mean()), 2
            )
            all_avg_losing_trade_per = round(
                abs(log.query('pnl_per <= 0').pnl_per.mean()), 2
            )
        except:
            all_avg_losing_trade = None
        try:
            long_avg_losing_trade = round(
                abs(log.query('deal_type == "long" and pnl <= 0'). \
                    pnl.mean()),
                2
            )
            long_avg_losing_trade_per = round(
                abs(log.query(
                    'deal_type == "long" and pnl_per <= 0'
                ).pnl_per.mean()),
                2
            )
        except:
            long_avg_losing_trade = None
        try:
            short_avg_losing_trade = round(
                abs(log.query('deal_type == "short" and pnl <= 0'). \
                    pnl.mean()),
                2
            )
            short_avg_losing_trade_per = round(
                abs(log.query(
                    'deal_type == "short" and pnl_per <= 0'
                ).pnl_per.mean()),
                2
            )
        except:
            short_avg_losing_trade = None

        if all_avg_losing_trade == 0:
            all_ratio_avg_win_loss = None
        else:
            all_ratio_avg_win_loss = round(
                all_avg_winning_trade / all_avg_losing_trade, 3
            )
        # try:
        #     all_ratio_avg_win_loss = round(
        #         all_avg_winning_trade / all_avg_losing_trade, 3
        #     )
        # except:
        #     all_ratio_avg_win_loss = None
            
        if long_avg_losing_trade == 0:
            long_ratio_avg_win_loss = None
        else:
            long_ratio_avg_win_loss = round(
                long_avg_winning_trade / long_avg_losing_trade, 3
            )
        # try:
        #     long_ratio_avg_win_loss = round(
        #         long_avg_winning_trade / long_avg_losing_trade, 3
        #     )
        # except:
        #     long_ratio_avg_win_loss = None

        if short_avg_losing_trade == 0:
            short_ratio_avg_win_loss = None
        else:
            short_ratio_avg_win_loss = round(
                short_avg_winning_trade / short_avg_losing_trade, 3
            )
        # try:
        #     short_ratio_avg_win_loss = round(
        #         short_avg_winning_trade / short_avg_losing_trade, 3
        #     )
        # except:
        #     short_ratio_avg_win_loss = None

        try:
            all_sortino_ratio = round(
                all_avg_trade_per / ((log.query('pnl_per <= 0'). \
                    pnl_per ** 2).mean() ** 0.5),
                3
            )
        except:
            all_sortino_ratio = None

        try:
            all_largest_winning_trade = round(
                log.query('pnl > 0').max().loc['pnl'], 2
            )
            all_largest_winning_trade_per = round(
                log.query('pnl_per > 0').max().loc['pnl_per'], 2
            )
        except:
            all_largest_winning_trade = None
        try:
            long_largest_winning_trade = round(
                log.query('deal_type == "long" and pnl > 0'). \
                    max().loc['pnl'], 
                2
            )
            long_largest_winning_trade_per = round(
                log.query('deal_type == "long" and pnl_per > 0'). \
                    max().loc['pnl_per'], 
                2
            )
        except:
            long_largest_winning_trade = None
        try:
            short_largest_winning_trade = round(
                log.query('deal_type == "short" and pnl > 0'). \
                    max().loc['pnl'], 
                2
            )
            short_largest_winning_trade_per = round(
                log.query('deal_type == "short" and pnl_per > 0'). \
                    max().loc['pnl_per'], 
                2
            )
        except:
            short_largest_winning_trade = None

        try:
            all_largest_losing_trade = round(
                abs(log.query('pnl <= 0').min().loc['pnl']), 2
            )
            all_largest_losing_trade_per = round(
                abs(log.query('pnl_per <= 0').min().loc['pnl_per']), 2
            )
        except:
            all_largest_losing_trade = None
        try:
            long_largest_losing_trade = round(
                abs(log.query(
                    'deal_type == "long" and pnl <= 0'
                ).min().loc['pnl']),
                2
            )
            long_largest_losing_trade_per = round(
                abs(log.query(
                    'deal_type == "long" and pnl_per <= 0'
                ).min().loc['pnl_per']),
                2
            )
        except:
            long_largest_losing_trade = None
        try:
            short_largest_losing_trade = round(
                abs(log.query(
                    'deal_type == "short" and pnl <= 0'
                ).min().loc['pnl']),
                2
            )
            short_largest_losing_trade_per = round(
                abs(log.query(
                    'deal_type == "short" and pnl_per <= 0'
                ).min().loc['pnl_per']),
                2
            )
        except:
            short_largest_losing_trade = None

        metrics = pd.DataFrame(
            {
                'Title': [
                    'Net profit, USDT',
                    'Net profit, %',
                    'Gross profit, USDT',
                    'Gross profit, %',
                    'Gross loss, USDT',
                    'Gross loss, %',
                    'Max drawdown, USDT',
                    'Max drawdown, %',
                    'Sortino ratio',
                    'Skew',
                    'Profit factor',
                    'Commission paid, USDT',
                    'Total closed trades',
                    'Number winning trades',
                    'Number losing trades',
                    'Percent profitable',
                    'Avg trade, USDT',
                    'Avg trade, %',
                    'Avg winning trade, USDT',
                    'Avg winning trade, %',
                    'Avg losing trade, USDT',
                    'Avg losing trade, %',
                    'Ratio avg win / avg loss',
                    'Largest winning trade, USDT',
                    'Largest winning trade, %',
                    'Largest losing trade, USDT',
                    'Largest losing trade, %',
            ],
                'All': [
                    all_net_profit,
                    all_net_profit_per,
                    all_gross_profit,
                    all_gross_profit_per,
                    all_gross_loss,
                    all_gross_loss_per,
                    all_max_drawdown,
                    all_max_drawdown_per,
                    all_sortino_ratio,
                    all_skew,
                    all_profit_factor,
                    all_commission_paid,
                    str(all_total_closed_trades),
                    str(all_number_winning_trades),
                    str(all_number_losing_trades),
                    all_percent_profitable,
                    all_avg_trade,
                    all_avg_trade_per,
                    all_avg_winning_trade,
                    all_avg_winning_trade_per,
                    all_avg_losing_trade,
                    all_avg_losing_trade_per,
                    all_ratio_avg_win_loss,
                    all_largest_winning_trade,
                    all_largest_winning_trade_per,
                    all_largest_losing_trade,
                    all_largest_losing_trade_per
                ],
                'Long': [
                    long_net_profit,
                    long_net_profit_per,
                    long_gross_profit,
                    long_gross_profit_per,
                    long_gross_loss,
                    long_gross_loss_per,
                    '',
                    '',
                    '',
                    '',
                    long_profit_factor,
                    long_commission_paid,
                    str(long_total_closed_trades),
                    str(long_number_winning_trades),
                    str(long_number_losing_trades),
                    long_percent_profitable,
                    long_avg_trade,
                    long_avg_trade_per,
                    long_avg_winning_trade,
                    long_avg_winning_trade_per,
                    long_avg_losing_trade,
                    long_avg_losing_trade_per,
                    long_ratio_avg_win_loss,
                    long_largest_winning_trade,
                    long_largest_winning_trade_per,
                    long_largest_losing_trade,
                    long_largest_losing_trade_per
                ],
                'Short': [
                    short_net_profit,
                    short_net_profit_per,
                    short_gross_profit,
                    short_gross_profit_per,
                    short_gross_loss,
                    short_gross_loss_per,
                    '',
                    '',
                    '',
                    '',
                    short_profit_factor,
                    short_commission_paid,
                    str(short_total_closed_trades),
                    str(short_number_winning_trades),
                    str(short_number_losing_trades),
                    short_percent_profitable,
                    short_avg_trade,
                    short_avg_trade_per,
                    short_avg_winning_trade,
                    short_avg_winning_trade_per,
                    short_avg_losing_trade,
                    short_avg_losing_trade_per,
                    short_ratio_avg_win_loss,
                    short_largest_winning_trade,
                    short_largest_winning_trade_per,
                    short_largest_losing_trade,
                    short_largest_losing_trade_per
                ]
            }
        )
        metrics = metrics.fillna('').astype(str)
        return metrics
        
    def create_html(self, strategy_name: str, exchange_name: str, symbol: str, interval: str, log: np.ndarray, performance_metrics: np.ndarray):
        
        html_head = self.generate_html_head()
        html_body = self.generate_html_body(
            strategy_name=strategy_name,
            exchange_name=exchange_name,
            symbol=symbol,
            interval=interval,
            log=log,
            performance_metrics=performance_metrics
        )
        html = f"""<!DOCTYPE html>
<html lang="en">
    {html_head}
    {html_body}
</html>
"""
        return html

        
    def generate_html_head(self) -> str:
        head = f"""<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <title>Statistics</title>
    <link rel="stylesheet" href="{self.bootstrap_relative_path}bootstrap.css" />
</head>
"""
        return head

    
    def generate_html_body(self, strategy_name: str, exchange_name: str, symbol: str, interval: str, log: np.ndarray, performance_metrics: np.ndarray) -> str:
        title = f"{strategy_name} {symbol} {interval} - {exchange_name}"
        list_of_trades = self.generate_list_of_trades_html_table(symbol, log)
        perfomance_summary = self.generate_performance_summary_html_table(performance_metrics)
        body = f"""
<body>
    <h4 class="text-center my-2">{title}</h4>
    <div class="accordion accordion-flush">
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#flush-collapseOne" aria-expanded="false" aria-controls="flush-collapseOne">
                    List of trades
                </button>
            </h2>
            <div id="flush-collapseOne" class="accordion-collapse collapse">
                <div class="accordion-body">
                    {list_of_trades}
                </div>
            </div>
        </div>
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#flush-collapseTwo" aria-expanded="false" aria-controls="flush-collapseTwo">
                    Performance summary
                </button>
            </h2>
            <div id="flush-collapseTwo" class="accordion-collapse collapse">
                <div class="accordion-body">
                    {perfomance_summary}
                </div>
            </div>
        </div>
    </div>
    <script src="{self.bootstrap_relative_path}bootstrap.js"></script>
</body>
"""
        return body
    

    def generate_list_of_trades_html_table(self, symbol: str, log: np.ndarray) -> str:
        table_body = self.generate_list_of_trades_table_body(symbol=symbol, log=log)
        table = f"""<table class="table table-bordered align-middle">
    <thead class="table-dark">
        <tr>
            <th scope="col">Trade #</th>
            <th scope="col">Type</th>
            <th scope="col">Signal</th>
            <th scope="col">Date/time</th>
            <th class="text-end" scope="col">Price</th>
            <th class="text-end" scope="col">Quantity</th>
            <th class="text-end" scope="col">Profit</th>
        </tr>
    </thead>
    <tbody>
        {table_body}
    </tbody>
</table>
"""
        return table



    def generate_list_of_trades_table_body(self, symbol: str, log: np.ndarray) -> str:
        table_body = ""
        for i in range(log.shape[0]):
            table_body += f"""<tr>
    <td rowspan="2">{i + 1}</td>
    <td>Exit {log.iat[i, 0]}</td>
    <td>{log.iat[i, 2]}</td>
    <td>{log.iat[i, 4]}</td>
    <td class="text-end">{log.iat[i, 6]} USDT</td>
    <td class="text-end" rowspan="2">{log.iat[i, 7]} {symbol[:symbol.rfind('USDT')]}</td>
    <td class="text-end" rowspan="2">
        <div>{log.iat[i, 8]} USDT</div>
        <div>{log.iat[i, 9]}%</div>
    </td>
</tr>
<tr>
    <td>Entry {log.iat[i, 0]}</td>
    <td>{log.iat[i, 1]}</td>
    <td>{log.iat[i, 3]}</td>
    <td class="text-end">{log.iat[i, 5]} USDT</td>
</tr>
"""
        return table_body
    

    def generate_performance_summary_html_table(self, performance_metrics: np.ndarray) -> str:
        table_body = self.generate_performance_summary_table_body(performance_metrics)
        table = f""" <table class="table table-hover table-bordered align-middle">
    <thead class="table-dark">
    <tr>
        <th scope="col">Title</th>
        <th class="text-end" scope="col">All</th>
        <th class="text-end" scope="col">Long</th>
        <th class="text-end" scope="col">Short</th>
    </tr>
    </thead>
    <tbody>
        {table_body}
    </tbody>
</table>
"""
        return table
    

    def generate_performance_summary_table_body(self, metrics: np.ndarray) -> str:
        table_body = f"""<tr>
    <td>Net profit</td>
    <td class="text-end">
    <div>{metrics.iat[0, 1]} USDT</div>
    <div>{metrics.iat[1, 1]}%</div>
    </td>
    <td class="text-end">
    <div>{metrics.iat[0, 2]} USDT</div>
    <div>{metrics.iat[1, 2]}%</div>
    </td>
    <td class="text-end">
    <div>{metrics.iat[0, 3]} USDT</div>
    <div>{metrics.iat[1, 3]}%</div>
    </td>
</tr>
<tr>
    <td>Gross profit</td>
    <td class="text-end">
    <div>{metrics.iat[2, 1]} USDT</div>
    <div>{metrics.iat[3, 1]}%</div>
    </td>
    <td class="text-end">
    <div>{metrics.iat[2, 2]} USDT</div>
    <div>{metrics.iat[3, 2]}%</div>
    </td>
    <td class="text-end">
    <div>{metrics.iat[2, 3]} USDT</div>
    <div>{metrics.iat[3, 3]}%</div>
    </td>
</tr>
<tr>
    <td>Gross loss</td>
    <td class="text-end">
    <div>{metrics.iat[4, 1]} USDT</div>
    <div>{metrics.iat[5, 1]}%</div>
    </td>
    <td class="text-end">
    <div>{metrics.iat[4, 2]} USDT</div>
    <div>{metrics.iat[5, 2]}%</div>
    </td>
    <td class="text-end">
    <div>{metrics.iat[4, 3]} USDT</div>
    <div>{metrics.iat[5, 3]}%</div>
    </td>
</tr>
<tr>
    <td>Profit factor</td>
    <td class="text-end">{metrics.iat[10, 1]}</td>
    <td class="text-end">{metrics.iat[10, 2]}</td>
    <td class="text-end">{metrics.iat[10, 3]}</td>
</tr>
<tr>
    <td>Commission paid</td>
    <td class="text-end">{metrics.iat[11, 1]} USDT</td>
    <td class="text-end">{metrics.iat[11, 2]} USDT</td>
    <td class="text-end">{metrics.iat[11, 3]} USDT</td>
</tr>
<tr>
    <td>Total closed trades</td>
    <td class="text-end">{metrics.iat[12, 1]}</td>
    <td class="text-end">{metrics.iat[12, 2]}</td>
    <td class="text-end">{metrics.iat[12, 3]}</td>
</tr>
<tr>
    <td>Number winning trades</td>
    <td class="text-end">{metrics.iat[13, 1]}</td>
    <td class="text-end">{metrics.iat[13, 2]}</td>
    <td class="text-end">{metrics.iat[13, 3]}</td>
</tr>
<tr>
    <td>Number losing trades</td>
    <td class="text-end">{metrics.iat[14, 1]}</td>
    <td class="text-end">{metrics.iat[14, 2]}</td>
    <td class="text-end">{metrics.iat[14, 3]}</td>
</tr>
<tr>
    <td>Percent profitable</td>
    <td class="text-end">{metrics.iat[15, 1]}{"%" if {metrics.iat[15, 1]} != "" else ""}</td>
    <td class="text-end">{metrics.iat[15, 2]}{"%" if {metrics.iat[15, 1]} != "" else ""}</td>
    <td class="text-end">{metrics.iat[15, 3]}{"%" if {metrics.iat[15, 1]} != "" else ""}</td>
</tr>
<tr>
    <td>Avg trade</td>
    <td class="text-end">
        <div>{metrics.iat[16, 1]}{"USDT" if {metrics.iat[16, 1]} != "" else ""}</div>
        <div">{metrics.iat[17, 1]}{"%" if {metrics.iat[17, 1]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[16, 2]}{"USDT" if {metrics.iat[16, 2]} != "" else ""}</div>
        <div">{metrics.iat[17, 2]}{"%" if {metrics.iat[17, 2]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[16, 3]}{"USDT" if {metrics.iat[16, 3]} != "" else ""}</div>
        <div">{metrics.iat[17, 3]}{"%" if {metrics.iat[17, 3]} != "" else ""}</div>
    </td>
</tr>
<tr>
    <td>Avg winning trades</td>
    <td class="text-end">
        <div>{metrics.iat[18, 1]}{"USDT" if {metrics.iat[18, 1]} != "" else ""}</div>
        <div">{metrics.iat[19, 1]}{"%" if {metrics.iat[19, 1]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[18, 2]}{"USDT" if {metrics.iat[18, 2]} != "" else ""}</div>
        <div">{metrics.iat[19, 2]}{"%" if {metrics.iat[19, 2]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[18, 3]}{"USDT" if {metrics.iat[18, 3]} != "" else ""}</div>
        <div">{metrics.iat[19, 3]}{"%" if {metrics.iat[19,3]} != "" else ""}</div>
    </td>
</tr>
<tr>
    <td>Avg losing trades</td>
    <td class="text-end">
        <div>{metrics.iat[20, 1]}{"USDT" if {metrics.iat[20, 1]} != "" else ""}</div>
        <div">{metrics.iat[21, 1]}{"%" if {metrics.iat[21, 1]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[20, 2]}{"USDT" if {metrics.iat[20, 2]} != "" else ""}</div>
        <div">{metrics.iat[21, 2]}{"%" if {metrics.iat[21, 2]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[20, 3]}{"USDT" if {metrics.iat[20, 3]} != "" else ""}</div>
        <div">{metrics.iat[21, 3]}{"%" if {metrics.iat[21, 3]} != "" else ""}</div>
    </td>
</tr>
<tr>
    <td>Ratio avg win / avg loss</td>
    <td class="text-end">{metrics.iat[22, 1]}</td>
    <td class="text-end">{metrics.iat[22, 2]}</td>
    <td class="text-end">{metrics.iat[22, 3]}</td>
</tr>
<tr>
    <td>Largest winning trade</td>
    <td class="text-end">
        <div>{metrics.iat[23, 1]}{"USDT" if {metrics.iat[23, 1]} != "" else ""}</div>
        <div">{metrics.iat[24, 1]}{"%" if {metrics.iat[24, 1]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[23, 2]}{"USDT" if {metrics.iat[23, 2]} != "" else ""}</div>
        <div">{metrics.iat[24, 2]}{"%" if {metrics.iat[24, 2]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[23, 3]}{"USDT" if {metrics.iat[23, 3]} != "" else ""}</div>
        <div">{metrics.iat[24, 3]}{"%" if {metrics.iat[24, 3]} != "" else ""}</div>
    </td>
</tr>
<tr>
    <td>Largest losing trade</td>
    <td class="text-end">
        <div>{metrics.iat[25, 1]}{"USDT" if {metrics.iat[25, 1]} != "" else ""}</div>
        <div">{metrics.iat[26, 1]}{"%" if {metrics.iat[26, 1]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[25, 2]}{"USDT" if {metrics.iat[25, 2]} != "" else ""}</div>
        <div">{metrics.iat[26, 2]}{"%" if {metrics.iat[26, 2]} != "" else ""}</div>
    </td>
    <td class="text-end">
        <div>{metrics.iat[25, 3]}{"USDT" if {metrics.iat[25, 3]} != "" else ""}</div>
        <div">{metrics.iat[26, 3]}{"%" if {metrics.iat[26, 3]} != "" else ""}</div>
    </td>
</tr>
<tr>
    <td>Max drawdown</td>
    <td class="text-end">
        <div>{metrics.iat[6, 1]} USDT</div>
        <div>{metrics.iat[7, 1]}%</div>
    </td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>Sortino ratio</td>
    <td class="text-end">
        <div>{metrics.iat[8, 1]} USDT</div>
    </td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td>Skew</td>
    <td class="text-end">
        <div>{metrics.iat[9, 1]} USDT</div>
    </td>
    <td></td>
    <td></td>
</tr>
"""
        return table_body

