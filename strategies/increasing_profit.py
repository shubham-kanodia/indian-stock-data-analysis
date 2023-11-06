from collection.dao import DAO
from pprint import pprint
from tqdm import tqdm


class ProfitStrategy:
    def __init__(self):
        self.dao = DAO()
        self.symbols = self.dao.get_symbols()
        self.num_of_years_into_consideration = 5

    def sort_data(self, data):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        keys = list(data.keys())
        keys.remove("_id")

        key_nums = {}

        for key in keys:
            month, year = key.split()
            month_idx = months.index(month)
            year = int(year)
            key_nums[key] = year*100 + month_idx

        sorted_keys = sorted(keys, key=lambda x: key_nums[x])
        sorted_financial_data = [data[x] for x in sorted_keys]
        return sorted_financial_data

    def get_profit_for_symbol(self, symbol):
        data = self.dao.get_stock_financial_data(symbol)
        sorted_data = self.sort_data(data)
        return [elem["net_profit"] for elem in sorted_data]

    def calculate_growth_rate_metric(self, numbers):
        numbers = [float(number) for number in numbers]

        last_n = numbers[-1 * self.num_of_years_into_consideration:]

        growth_metric = 0
        for idx in range(1, len(last_n)):
            growth_rate = ((last_n[idx] - last_n[idx - 1]) / last_n[idx - 1]) * 100

            if growth_rate > 0:
                growth_metric += growth_rate
            else:
                # Subtract twice, stock gets double the reduction for negative growth
                growth_metric += -2 * 100000000

        return growth_metric / self.num_of_years_into_consideration

    def rank_on_growth_metric(self):
        symbol_growth_metric = {}

        for symbol in tqdm(self.symbols):
            try:
                sales = self.get_profit_for_symbol(symbol)
                growth_metric = self.calculate_growth_rate_metric(sales)

                symbol_growth_metric[symbol] = growth_metric
            except Exception as exp:
                continue
                # print(f"Skipped for symbol: {symbol}")

        symbols_ranked = sorted(
            symbol_growth_metric, key=lambda x: symbol_growth_metric[x], reverse=True
        )

        return symbols_ranked


profit_strategy = ProfitStrategy()
ranked_stocks = profit_strategy.rank_on_growth_metric()

pprint(ranked_stocks)
