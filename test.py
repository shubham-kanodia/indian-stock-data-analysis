from collection.data_collection import Crawler
from collection.config import CONFIG
from pymongo import MongoClient

crawler = Crawler()

cluster = MongoClient(CONFIG.MONGO_URI)

db = cluster["stocker"]
collection_stock_prices = db["stock_prices"]
collection_stock_names = db["stock_names"]

# Create documents for each stock in stock_prices
# results = collection_stock_names.find()
# stock_symbols = [result["_id"] for result in results]
#
# stock_prices = [{"_id": stock_symbol} for stock_symbol in stock_symbols]
# collection_stock_prices.insert_many(stock_prices)

# collection_stock_prices.insert_one(
#     {
#         "_id": "temp",
#         "d1": "abcd"
#     }
# )

results = collection_stock_prices.find({"_id": "temp"})
print(results[0])
