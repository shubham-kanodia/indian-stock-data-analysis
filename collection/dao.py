from pymongo import MongoClient
from collection.config import CONFIG


class DAO:
    def __init__(self):
        cluster = MongoClient(CONFIG.MONGO_URI)
        _db = cluster["stocker"]
        self.collection_stock_names = _db["stock_names"]
        self.collection_stock_prices = _db["stock_prices"]

    def get_symbols(self):
        results = self.collection_stock_names.find()
        return [result["_id"] for result in results]

    def add_data(self, symbol, data):
        self.collection_stock_prices.update_one({"_id": symbol}, {"$set": data})

    def get_stock_data(self, symbol):
        return self.collection_stock_prices.update_one({"_id": symbol})[0]
