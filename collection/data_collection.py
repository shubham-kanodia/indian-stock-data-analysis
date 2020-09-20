from collection.config import CONFIG
from nsetools.utils import byte_adaptor
from urllib.request import Request
from collection.exporter import Exporter
from time import sleep


class Crawler:

    @staticmethod
    def crawl_weekly_price_history_html(stock_symbol):
        url = CONFIG.HISTORICAL_DATA_WEEK_URL.replace("STOCK_SYMBOL", stock_symbol)
        req = Request(url, None, CONFIG.HEADERS)

        resp = CONFIG.OPENER.open(req)
        resp = byte_adaptor(resp)

        return resp.read()

    @staticmethod
    def crawl_nifty500_from_csv(file_name):
        symbol_lst = []
        with open(file_name, "r") as fl:
            next(fl)
            for line in fl:
                line = line.strip("\n")
                symbol_lst.append((line.split(",")[0], line.split(",")[2]))
        return symbol_lst


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

    @staticmethod
    def fetch_weekly_data(stock_symbol):
        resp = Crawler.crawl_weekly_price_history_html(stock_symbol)
        data = Parser.parse_price_table(resp)
        return data

    @staticmethod
    def export_weekly_data(stock_symbol, exporter):
        try:
            data = Fetcher.fetch_weekly_data(stock_symbol)
            exporter.add_weekly_data(stock_symbol, data)
        except Exception as exp:
            print(
                f"Could not export prices for symbol {stock_symbol}, Exception: "
            )


class DataCollection:

    @staticmethod
    def collect_weekly_data_all():
        exporter = Exporter()
        fetcher = Fetcher()

        all_symbols = exporter.get_symbols()
        for symbol in all_symbols:
            print(f"[Added] {symbol}")
            fetcher.export_weekly_data(symbol, exporter)
        sleep(1)


data_collection = DataCollection()
data_collection.collect_weekly_data_all()
