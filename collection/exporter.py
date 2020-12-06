import pickle
import sqlite3
from sqlite3 import Error
from sqlitedict import SqliteDict
import datetime


class Exporter:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("resources/stock-data.db")
            self.cursor = self.conn.cursor()
            self.date = datetime.date.today().strftime('%d%m%Y')

            sql_create_stock_symbol_table = """ CREATE TABLE IF NOT EXISTS stock_symbols (
                                                name text,
                                                symbol text
                                            )"""

            sql_create_stock_sector_table = """ CREATE TABLE IF NOT EXISTS stock_sectors (
                                                symbol text,
                                                sector text
                                            )"""

            sql_create_rms_change_table = """ CREATE TABLE IF NOT EXISTS rms_change_table (
                                                    sector text,
                                                    value real
                                            )"""
            try:
                self.cursor.execute(sql_create_stock_symbol_table)
                self.cursor.execute(sql_create_stock_sector_table)
                self.cursor.execute(sql_create_rms_change_table)
            except Error as e:
                print(e)
        except Error as e:
            print(e)

    def _add_stock_symbol(self, symbol_with_name):
        try:
            sql_add_stock_symbol = f"""
                                    INSERT INTO stock_symbols VALUES("{symbol_with_name[0]}", "{symbol_with_name[1]}")
                                    """
            self.cursor.execute(sql_add_stock_symbol)
        except Error as e:
            print(f"Exception inserting symbol {symbol_with_name}: " + e)

    def add_stock_symbols(self, symbols_list):
        for symbol in symbols_list:
            self._add_stock_symbol(symbol)
        self.conn.commit()

    def add_stock_sector(self, symbol, sector):
        try:
            sql_add_stock_sector = f"""
                                    INSERT INTO stock_sectors VALUES("{symbol}", "{sector}")
                                    """
            self.cursor.execute(sql_add_stock_sector)
            self.conn.commit()
        except Error as e:
            print(f"Exception inserting stock sector {symbol}: " + e)

    def get_symbols(self):
        sql_fetch = """
                    SELECT symbol FROM stock_symbols
                    """
        data_rows = self.cursor.execute(sql_fetch).fetchall()

        return [data_row[0] for data_row in data_rows]

    @staticmethod
    def add_data(symbol, data):
        data_dict = SqliteDict(f"resources/prices/{symbol}.sqlite", autocommit=True)
        for key in data:
            data_dict[key] = data[key]

    @staticmethod
    def get_stock_data(symbol):
        data_dict = SqliteDict(f"resources/prices/{symbol}.sqlite", autocommit=True)
        return dict(data_dict)

    @staticmethod
    def generate_insert_statement(data_dict, table_name):
        """ Generate insert statement from dictionary """

        query = f"INSERT INTO {table_name}({','.join(data_dict.keys())})" \
                f" VALUES({','.join(map(str, data_dict.values()))})"\
                .replace("None", "NULL")

        return query

    @staticmethod
    def add_stock_financial_data(data, symbol):
        data_dict = SqliteDict(f"resources/financial-data/{symbol}.sqlite", autocommit=True)
        for key in data:
            if key not in data_dict:
                data_dict[key] = data[key]
            else:
                existing_data = data_dict[key]
                for data_key in data[key]:
                    existing_data[data_key] = data[key][data_key]
                data_dict[key] = existing_data

    @staticmethod
    def get_financial_doc(symbol):
        with open(f"resources/raw-documents/{symbol}.pkl", "rb") as fl:
            page = pickle.load(fl)
        return page

    @staticmethod
    def get_stock_financial_data(symbol):
        return dict(SqliteDict(f"resources/financial-data/{symbol}.sqlite"))

    def get_stocks_from_sector(self, sector):
        sql_fetch = f"""
                    SELECT symbol FROM stock_sectors WHERE sector="{sector}"
                    """
        data_rows = self.cursor.execute(sql_fetch).fetchall()

        return [data_row[0] for data_row in data_rows]

    def get_sector_from_stock(self, symbol):
        sql_fetch = f"""
                    SELECT sector FROM stock_sectors WHERE symbol="{symbol}"
                    """
        data_rows = self.cursor.execute(sql_fetch).fetchall()

        return data_rows[0][0]

    def add_sector_rms_change(self, sector, change):
        sql_add_sector_rms_change = f"""
                                    INSERT INTO rms_change_table VALUES("{sector}", {change})
                                    """
        self.cursor.execute(sql_add_sector_rms_change)
        self.conn.commit()

    def get_sector_rms_change(self, sector):
        sql_fetch = f"""
                    SELECT value FROM rms_change_table WHERE sector="{sector}"
                    """
        data_rows = self.cursor.execute(sql_fetch).fetchall()

        return data_rows[0][0]

    def get_sectors_list(self):
        sql_fetch = f"""
                    SELECT DISTINCT(sector) FROM stock_sectors
                    """
        data_rows = self.cursor.execute(sql_fetch).fetchall()

        return [data_row[0] for data_row in data_rows]
