import requests

from collection.config import CONFIG
from nsetools.utils import byte_adaptor
from urllib.request import Request
from collection.dao import DAO
from time import sleep
import datetime


class Crawler:

    @staticmethod
    def crawl_weekly_price_history_html(stock_symbol):
        url = CONFIG.HISTORICAL_DATA_WEEK_URL.replace("STOCK_SYMBOL", stock_symbol)
        req = Request(url, None, CONFIG.HEADERS)

        resp = CONFIG.OPENER.open(req)
        resp = byte_adaptor(resp)

        return resp.read()

    @staticmethod
    def crawl_date_to_date_history(stock_symbol, from_date, to_date):
        url = CONFIG.HISTORICAL_DATA_DATE_TO_DATE_URL\
            .replace("STOCK_SYMBOL", stock_symbol)\
            .replace("FROM_DATE", from_date)\
            .replace("TO_DATE", to_date)
        req = Request(url, None, CONFIG.HEADERS)

        resp = CONFIG.OPENER.open(req)
        return resp.read()

    @staticmethod
    def crawl_financial_data(stock_symbol):
        url = CONFIG.SCREENER_URL.replace("STOCK_SYMBOL", stock_symbol)
        page = requests.get(url)
        return page


class Parser:

    @staticmethod
    def parse_price_table(resp):
        """
        ['Date', 'Symbol', 'Series', 'Open Price', 'High Price', 'Low Price',
        'Last Traded Price ', 'Close Price', 'Total Traded Quantity', 'Turnover (in Lakhs)']
        """
        data = {}
        from lxml import etree
        table = etree.HTML(resp).find("body/table/tbody")
        rows = iter(table)
        headers = [col.text for col in next(rows)]
        for row in rows:
            values = [col.text for col in row]
            data[values[0]] = {
                "close_price": values[7]
            }
        return data


class Fetcher:
    """Wrapper Class for using crawler and fetcher classes"""

    @staticmethod
    def fetch_weekly_data(stock_symbol):
        resp = Crawler.crawl_weekly_price_history_html(stock_symbol)
        data = Parser.parse_price_table(resp)
        return data

    @staticmethod
    def export_weekly_data(stock_symbol, exporter):
        data = Fetcher.fetch_weekly_data(stock_symbol)
        exporter.add_data(stock_symbol, data)

    @staticmethod
    def fetch_last_five_years_data(stock_symbol):
        to_date = datetime.date.today().strftime('%d-%m-%Y')
        split_date = to_date.split("-")
        from_date = "-".join([split_date[0],
                              split_date[1],
                              str(int(split_date[2]) - 5)])

        resp = Crawler.crawl_date_to_date_history(stock_symbol, from_date, to_date)
        data = Parser.parse_price_table(resp)

        return data

    @staticmethod
    def export_five_years_data(stock_symbol, exporter):
        data = Fetcher.fetch_last_five_years_data(stock_symbol)
        exporter.add_data(stock_symbol, data)


class DataCollection:
    """Handle multiple tickers' collection"""

    def __init__(self):
        self.dao = DAO()
        self.fetcher = Fetcher()
        self.all_symbols = self.dao.get_symbols()

    def collect_weekly_data_all(self):
        for symbol in self.all_symbols:
            print(f"[Added] {symbol}")
            self.fetcher.export_weekly_data(symbol, self.dao)
        sleep(1)

    def collect_five_years_data_all(self):
        for symbol in self.all_symbols:
            print(f"[Added] {symbol}")
            self.fetcher.export_five_years_data(symbol, self.dao)
        sleep(1)
