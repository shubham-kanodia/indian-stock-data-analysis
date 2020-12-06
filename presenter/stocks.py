import pprint

from collection.exporter import Exporter
from datetime import datetime
import datetime as dt
import logging
from evaluators.metrics import Metrics


class Stock:

    def __init__(self, stock_symbol, exporter):
        self.symbol = stock_symbol
        self.exporter = exporter
        self.data = self.exporter.get_stock_data(stock_symbol)
        self.financial = self.exporter.get_stock_financial_data(stock_symbol)
        self.metrics = Metrics(exporter)
        self.sector = self.exporter.get_sector_from_stock(stock_symbol)

    def convert_date(self, date):
        date = datetime.strptime(date, "%d-%m-%Y").date()
        return date.strftime("%d-%b-%Y")

    def get_closing_price(self, date):
        """Note: date format should be dd-mm-yyyy"""
        date = self.convert_date(date)
        price = self.data.get(date, None)
        return price["close_price"] if price else None

    def prev_day(self, date):
        date = (datetime.strptime(date, "%d-%m-%Y").date() - dt.timedelta(1)) \
            .strftime("%d-%m-%Y")
        return date

    def get_prev_day_price(self, date):
        """Note: date format should be dd-mm-yyyy"""
        date = self.prev_day(date)
        return self.get_closing_price(date)

    def get_last_n_days_data(self, n):
        day = dt.date.today()\
            .strftime("%d-%m-%Y")
        data = [self.get_closing_price(day)]
        num_of_days = 1
        while num_of_days < n:
            if int(day.split("-")[2]) < 2016:
                break
            price = self.get_prev_day_price(day)
            if price:
                data.append(price)
                num_of_days += 1
            day = self.prev_day(day)
        return list(reversed(data))

    def calculate_profit_consistency(self):
        return self.metrics.calculate_earning_consistency_score(self)


# Under Construction
class Stocks:

    def __init__(self):
        self.exporter = Exporter()
        self.stock_symbols = self.exporter.get_symbols()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler('logs/stock_evaluation.log')
        fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        self.logger.addHandler(fh)

    def apply_metric(self, metric, num_of_days):
        scores = {}

        for stock_symbol in self.stocks:
            stock = Stock(stock_symbol, self.exporter)

            # For stock whose values are yet not populated
            try:
                price_list = stock.get_last_n_days_data(num_of_days)
                assert len(price_list) == num_of_days

            except Exception as exp:
                print(f"[SKIPPING] Stock {stock_symbol}")

            print(f"[ASSESSING] Stock {stock_symbol}")
            try:
                score = metric.score(price_list)

                scores[stock_symbol] = score
            except Exception as exp:
                print(f"[SKIPPING] Stock {stock_symbol}")
        return scores

    def find_top_stocks_by_profit(self):
        stocks_score = {}
        self.logger.info("[Processing] Stocks earnings consistency score calculation")
        for stock_symbol in self.stock_symbols:
            try:
                stock = Stock(stock_symbol, self.exporter)
                self.logger.info(f"[Processing] Stock: {stock.symbol}")
                score = stock.calculate_profit_consistency()
                stocks_score[stock.symbol] = score
            except Exception:
                self.logger.info(f"[Skipping] Stock: {stock_symbol}")

        sorted_by_scores = sorted(stocks_score.items(), key=lambda x: x[1], reverse=True)
        self.logger.info(f"Stock earnings consistency data for NIFTY 500")
        self.logger.info(pprint.pformat(sorted_by_scores))
        return sorted_by_scores


class SectorStocks:

    def __init__(self, sector):
        self.sector = sector
        self.exporter = Exporter()
        self.stock_symbols = self.exporter.get_stocks_from_sector(sector)
        self.stocks = [Stock(stock_symbol, self.exporter) for stock_symbol in self.stock_symbols]
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename='logs/stock_evaluation.log',
                            level=logging.INFO)

    def find_top_stocks_by_profit(self):
        stocks_score = {}
        logging.info("[Processing] Stocks earnings consistency score calculation")
        for stock in self.stocks:
            try:
                logging.info(f"[Processing] Stock: {stock.symbol}")
                score = stock.calculate_profit_consistency()
                stocks_score[stock.symbol] = score
            except Exception:
                logging.info(f"[Skipping] Stock: {stock.symbol}")

        sorted_by_scores = sorted(stocks_score.items(), key=lambda x: x[1], reverse=True)
        logging.info(f"Stock earnings consistency data for sector: {self.sector}")
        logging.info(pprint.pformat(sorted_by_scores))
        return sorted_by_scores
