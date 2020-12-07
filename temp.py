from collection.dao import DAO
from pprint import pprint
#
# with open("res/raw-documents/INFY.pkl", "rb") as fl:
#     doc = pickle.load(fl)
from models.stocks import Stock, SectorStocks, Stocks

exporter = DAO()
# pprint(exporter.get_stock_financial_data("AARTIIND"))

# utilities = Utilities()
# utilities.update_self_built_parameters()
# print(exporter.get_sector_rms_change("Shipping"))

# pprint(exporter.get_sectors_list())
# sector_stocks = SectorStocks('Pharmaceuticals')
# print(sector_stocks.find_top_n_stocks_by_profit(5))

# stock = Stock("VAKRANGEE", exporter)
# print(stock.calculate_profit_consistency())

# stocks = Stocks()
# pprint(stocks.find_top_stocks_by_profit())

stock = Stock("BRITANNIA", exporter)
stock.calculate_profit_consistency()
