from collection.dao import DAO
from nsetools import Nse
from datetime import datetime
from time import sleep

from technical_analysis.covid_effect import CovidEffect
from technical_analysis.golden_crossover import GoldenCrossover


class Runner:

    def __init__(self):
        self.dao = DAO()
        self.nse = Nse()
        self.gc = GoldenCrossover(self.dao)
        self.covid_effect = CovidEffect(self.dao)

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

    def golden_crossover_update(self):
        top_stocks = self.gc.get_top_stocks()
        self.dao.update_golden_crossover_collection(top_stocks)

    def covid_effect_update(self):
        top_stocks = self.covid_effect.get_top_stocks()
        self.dao.update_covid_effect_collection(top_stocks)


runner = Runner()
runner.covid_effect_update()
