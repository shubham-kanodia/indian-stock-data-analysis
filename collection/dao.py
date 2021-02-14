import pickle
import numpy as np
from datetime import datetime
from pymongo import MongoClient
from collection.config import CONFIG


class DAO:
    def __init__(self):
        cluster = MongoClient(CONFIG.MONGO_URI)
        _db = cluster["stocker"]
        self.collection_stock_names = _db["stock_names"]
        self.collection_stock_prices = _db["stock_prices"]
        self.collection_stock_financials = _db["financial_data"]
        self.collection_screener_prices = _db["screener_prices"]
        self.collection_golden_crossover = _db["golden_crossover"]
        self.collection_covid_effect = _db["covid_effect"]

        self.screener_id_dict = pickle.load(open("res/screener_id.pkl", "rb"))

    def get_symbols(self):
        results = self.collection_stock_names.find()
        return [result["_id"] for result in results]

    def add_data(self, symbol, data):
        if self.collection_stock_prices.find_one({"_id": symbol}):
            self.collection_stock_prices.update_one({"_id": symbol}, {"$set": data})
        else:
            data["_id"] = symbol
            self.collection_stock_prices.insert_one(data)

    def add_screener_price_data(self, symbol, data):
        if self.collection_screener_prices.find_one({"_id": symbol}):
            self.collection_screener_prices.update_one({"_id": symbol}, {"$set": data})
        else:
            data["_id"] = symbol
            self.collection_screener_prices.insert_one(data)

    def get_stock_data(self, symbol):
        return self.collection_stock_prices.find({"_id": symbol})[0]

    @staticmethod
    def get_financial_doc(symbol):
        with open(f"res/screener-docs/{symbol}.pkl", "rb") as fl:
            page = pickle.load(fl)
        return page

    @staticmethod
    def _merge_financial_data(prior_data, recent_financial_data):
        for key in prior_data:
            if key in recent_financial_data:
                recent_financial_data[key] = {**prior_data[key], **recent_financial_data[key]}
            else:
                recent_financial_data[key] = prior_data[key]
        return recent_financial_data

    def add_stock_financial_data(self, symbol, financial_data):
        prior_data = self.collection_stock_financials.find_one({"_id": symbol})
        if prior_data:
            merged_data = self._merge_financial_data(prior_data, financial_data)
            self.collection_stock_financials.update_one({"_id": symbol}, {"$set": merged_data})
        else:
            self.collection_stock_financials.insert({"_id": symbol, **financial_data})

    def get_screener_id(self, stock_symbol):
        return self.screener_id_dict.get(stock_symbol, None)

    def update_golden_crossover_collection(self, data):
        self.collection_golden_crossover.remove({})

        data["_id"] = 1
        self.collection_golden_crossover.insert_one(data)

    def get_golden_crossover_data(self):
        return self.collection_golden_crossover.find({"_id": 1})[0]

    def update_covid_effect_collection(self, data):
        data["_id"] = datetime.today().date().strftime("%d-%b-%Y")
        self.collection_covid_effect.insert_one(data)

    def get_stock_price_history(self, symbol):
        symbol_price = self.get_stock_data(symbol)
        dates = sorted(
            list(
                symbol_price.keys())[1:],
                key=lambda date: datetime.strptime(date, "%d-%b-%Y")
        )
        prices = [float(symbol_price[date]["close_price"].replace(",", "")) for date in dates]
        return dates, prices

    def check_stock_split(self, symbol, period):
        try:
            _, prices = self.get_stock_price_history(symbol)
            prices = np.array(prices[-1 * period:])

            for ind in range(1, len(prices)):
                prev_price = prices[ind - 1]
                price = prices[ind]

                if abs(price - prev_price) * 100 / prev_price > 20:
                    return True
            return False
        except Exception:
            return False
