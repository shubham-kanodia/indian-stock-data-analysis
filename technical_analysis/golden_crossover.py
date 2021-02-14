import numpy as np
from talib import SMA


class GoldenCrossover:
    def __init__(self, dao):
        self.dao = dao
        self.period = 400

    def get_crossover_past_days(self, symbol):
        try:
            dates, prices = self.dao.get_stock_price_history(symbol)
            prices = np.array(prices[-1 * self.period:])

            sma_50 = SMA(prices, timeperiod=50)
            sma_200 = SMA(prices, timeperiod=200)

            sma_diff = sma_200 - sma_50

            for ind in range(sma_diff.shape[0] - 1, 0, -1):
                if sma_diff[ind] < 0 and sma_diff[ind - 1] >= 0:
                    return sma_diff.shape[0] - 1 - ind
            return self.period
        except Exception as exp:
            return self.period

    def get_top_stocks(self):
        symbol_period_map = {
            symbol: self.get_crossover_past_days(symbol) for symbol in self.dao.get_symbols()
        }
        data = sorted(symbol_period_map, key=lambda x: symbol_period_map[x])

        return {symbol: symbol_period_map[symbol] for symbol in data[:15]}
