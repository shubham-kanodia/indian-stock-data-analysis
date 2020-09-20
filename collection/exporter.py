import sqlite3
from sqlite3 import Error
from sqlitedict import SqliteDict


class Exporter:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("../resources/stock-data.db")
            self.cursor = self.conn.cursor()
            sql_create_stock_symbol_table = """ CREATE TABLE IF NOT EXISTS stock_symbols (
                                                name text,
                                                symbol text
                                            )"""
            try:
                self.cursor.execute(sql_create_stock_symbol_table)
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

    def get_symbols(self):
        sql_fetch = """
                    SELECT symbol FROM stock_symbols
                    """
        data_rows = self.cursor.execute(sql_fetch).fetchall()

        return [data_row[0] for data_row in data_rows]

    @staticmethod
    def add_weekly_data(symbol, data):
        data_dict = SqliteDict(f"../resources/prices/{symbol}.sqlite", autocommit=True)
        for key in data:
            data_dict[key] = data[key]
