from collection.dao import DAO
from nsetools import Nse
from datetime import datetime
from time import sleep


class Runner:

    def __init__(self):
        self.dao = DAO()
        self.nse = Nse()

    def populate_today_price(self):
        """Run this daily to update values"""
        symbols = self.dao.get_symbols()
        for symbol in symbols:
            try:
                symbol_data = self.nse.get_quote(symbol)
                close_price = str(symbol_data["closePrice"])

                date_today = datetime.today().date().strftime("%d-%b-%Y")

                data = {
                    date_today: {
                        "close_price": close_price
                    }
                }
                self.dao.add_data(symbol, data)
                print(f"[Added] Today's Closing Price For: {symbol}")
                sleep(1)

            except Exception:
                print(f"[SKIPPED] Stock Symbol: {symbol}")

runner = Runner()
runner.populate_today_price()
