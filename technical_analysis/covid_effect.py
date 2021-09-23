import numpy as np


class CovidEffect:
    def __init__(self, dao):
        self.dao = dao
        self.baseline_date = "31-Jan-2020"

    def get_price_change_from_effect(self, symbol):
        try:
            dates, prices = self.dao.get_stock_price_history(symbol)
            period = len(dates) - dates.index(self.baseline_date) if self.baseline_date in dates else 260
            prices = np.array(prices[-1 * period:])

            prices = np.array(prices[-1 * period:])
            current_price = prices[-1]
            return (max(prices) - current_price) * 100 / current_price

        except Exception:
            return 0.0

    def get_top_stocks(self):
        price_diff_map = {}

        for symbol in self.dao.get_symbols():
            if not self.dao.check_stock_split(symbol, period=260):
                price_diff_precentage = self.get_price_change_from_effect(symbol)
                price_diff_map[symbol] = price_diff_precentage

        sorted_map = sorted(price_diff_map, key=lambda x: price_diff_map[x], reverse=True)

        response = {}

        for symbol in sorted_map:
            if price_diff_map[symbol] > 30:
                response[symbol] = price_diff_map[symbol]
        return response
