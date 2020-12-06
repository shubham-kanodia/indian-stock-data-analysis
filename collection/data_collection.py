import pickle

import requests
from bs4 import BeautifulSoup

from collection.config import CONFIG
from nsetools.utils import byte_adaptor
from urllib.request import Request
from collection.exporter import Exporter
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
    def crawl_nifty500_from_csv(file_name):
        symbol_lst = []
        with open(file_name, "r") as fl:
            next(fl)
            for line in fl:
                line = line.strip("\n")
                symbol_lst.append((line.split(",")[0], line.split(",")[2]))
        return symbol_lst

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

    @staticmethod
    def parse_balance_sheet_data(document):
        """
        Row 1 -> Time published (Annual)
        Row 2 -> Share Capital
        Row 3 -> Reserves
        Row 4 -> Borrowings
        Row 5 -> Other Liabilities
        Row 6 -> Total Liabilities
        Row 7 -> Fixed Assets
        Row 8 -> CWIP
        Row 9 -> Investments
        Row 10 -> Other Assets
        Row 11 -> Total Assets
        """

        soup = BeautifulSoup(document.content, 'html.parser')
        balance_sheet_table = soup.find(id="balance-sheet").find('table')

        lst = [
            [cell.string for cell in balance_sheet_table.find_all("tr")[0].find_all("th")[1:]]
        ]

        for row in balance_sheet_table.find_all("tr")[1:]:
            cells = row.find_all("td")
            lst.append(
                [cell.string.replace(",", "") for cell in cells[1:]]
            )
        return lst

    @staticmethod
    def parse_income_statement(document):
        """
        Row 1 -> Time published (Annual)
        Row 2 -> sales
        Row 3 -> expenses
        Row 4 -> operating_profit
        Row 5 -> opm_percentage
        Row 6 -> other_income
        Row 7 -> interest
        Row 8 -> depreciation
        Row 9 -> profit_before_tax
        Row 10 -> tax_percentage
        Row 11 -> net_profit
        Row 12 -> eps_in_rs
        Row 13 -> dividend_payout
        """

        soup = BeautifulSoup(document.content, 'html.parser')
        income_statement_table = soup.find(id="profit-loss").find('table')

        lst = [
            [cell.string for cell in income_statement_table.find_all("tr")[0].find_all("th")[1:-1]]
        ]

        for row in income_statement_table.find_all("tr")[1:]:
            cells = row.find_all("td")
            lst.append(
                [None if not cell.string else cell.string.replace(",", "") for cell in cells[1:-1]]
            )
        return lst

    @staticmethod
    def parse_sector(document):
        soup = BeautifulSoup(document.content, 'html.parser')
        sector = soup \
            .find(id="peers") \
            .find("small", class_="sub") \
            .find("a").string.strip()
        return sector


class Fetcher:
    """Wrapper Class for using crawler and fetcher classes"""

    @staticmethod
    def fetch_weekly_data(stock_symbol):
        resp = Crawler.crawl_weekly_price_history_html(stock_symbol)
        data = Parser.parse_price_table(resp)
        return data

    @staticmethod
    def export_weekly_data(stock_symbol, exporter):
        try:
            data = Fetcher.fetch_weekly_data(stock_symbol)
            exporter.add_data(stock_symbol, data)
        except Exception:
            print(
                f"Could not export prices for symbol {stock_symbol}"
            )

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
        try:
            data = Fetcher.fetch_last_five_years_data(stock_symbol)
            exporter.add_data(stock_symbol, data)
        except Exception:
            print(
                f"Could not export prices for symbol {stock_symbol}"
            )

    @staticmethod
    def export_stock_financial_docs(stock_symbol):
        try:
            data = Crawler.crawl_financial_data(stock_symbol)
            with open(f"resources/raw-documents/{stock_symbol}.pkl", "wb") as fl:
                pickle.dump(data, fl)
        except Exception:
            print(
                f"Could not export financial data for symbol {stock_symbol}"
            )

    @staticmethod
    def export_balance_sheet_data(exporter, stock_symbol):
        parameters = [
            "time_published",
            "share_capital",
            "reserves",
            "borrowing",
            "other_liabilities",
            "total_liabilities",
            "fixed_assets",
            "cwip",
            "investments",
            "other_assets",
            "total_assets"
        ]
        try:
            document = exporter.get_financial_doc(stock_symbol)
            financial_data = {}
            data = Parser.parse_balance_sheet_data(document)
            for time in data[0]:
                financial_data[time] = {}

            for row in range(1, len(data)):
                for col in range(len(data[0])):
                    financial_data[data[0][col]][parameters[row]] = data[row][col]

            exporter.add_stock_financial_data(financial_data, stock_symbol)

        except Exception:
            print(
                f"Could not parse balance sheet data"
            )

    @staticmethod
    def export_income_statement_data(exporter, stock_symbol):
        parameters = [
            "time_published",
            "sales",
            "expenses",
            "operating_profit",
            "opm_percentage",
            "other_income",
            "interest",
            "depreciation",
            "profit_before_tax",
            "tax_percentage",
            "net_profit",
            "eps_in_rs",
            "dividend_payout"
        ]
        try:
            document = exporter.get_financial_doc(stock_symbol)
            financial_data = {}
            data = Parser.parse_income_statement(document)
            for time in data[0]:
                financial_data[time] = {}

            for row in range(1, len(data)):
                for col in range(len(data[0])):
                    financial_data[data[0][col]][parameters[row]] = data[row][col]

            exporter.add_stock_financial_data(financial_data, stock_symbol)

        except Exception:
            print(
                f"[Skipped] Could not parse income statement data {stock_symbol}"
            )

    @staticmethod
    def export_stock_sector(exporter, stock_symbol):
        try:
            document = exporter.get_financial_doc(stock_symbol)
            stock_sector = Parser.parse_sector(document)
            exporter.add_stock_sector(stock_symbol, stock_sector)
        except Exception:
            print(
                f"Could not parse sector data"
            )


class DataCollection:
    """Handle multiple tickers' collection"""

    def __init__(self):
        self.exporter = Exporter()
        self.fetcher = Fetcher()
        self.all_symbols = self.exporter.get_symbols()

    def collect_weekly_data_all(self):
        for symbol in self.all_symbols:
            print(f"[Added] {symbol}")
            self.fetcher.export_weekly_data(symbol, self.exporter)
        sleep(1)

    def collect_five_years_data_all(self):
        for symbol in self.all_symbols:
            print(f"[Added] {symbol}")
            self.fetcher.export_five_years_data(symbol, self.exporter)
        sleep(1)

    def collect_stock_financial_docs(self):
        for symbol in self.all_symbols:
            self.fetcher.export_stock_financial_docs(symbol)
            print(f"[Added Financial Data] {symbol}")
        sleep(1)

    def collect_balance_sheet_data(self):
        for symbol in self.all_symbols:
            self.fetcher.export_balance_sheet_data(
                                                    self.exporter,
                                                    symbol
                                                    )
            print(f"[Added Financial Data - Balance Sheet] Symbol: {symbol}")

    def collect_income_statement_data(self):
        for symbol in self.all_symbols:
            self.fetcher.export_income_statement_data(
                                                    self.exporter,
                                                    symbol
                                                    )
            print(f"[Added Financial Data - Income Statement] Symbol: {symbol}")

    def collect_sector_data(self):
        for symbol in self.all_symbols:
            self.fetcher.export_stock_sector(self.exporter, symbol)
            print(f"[Added Stock Sector] Symbol: {symbol}")
