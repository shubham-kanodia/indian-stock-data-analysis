class TrendMetric:

    # Static method score must be defined in each metric
    @staticmethod
    def score(price_list):
        """Given the price list, determines a score showing how much trending the stock has been"""
        growth_list = []
        start_index = 1

        price_list = [float(price.replace(',', '')) for price in price_list]

        for ind in range(start_index, len(price_list)):
            curr_price = price_list[ind]
            last_price = price_list[ind-1]

            growth_percent = ((curr_price - last_price)/last_price)*100
            growth_list.append(growth_percent)

        # Find percentage of positive growth in growth_list
        percentage_pos_growth = (sum([1 if growth > 0 else 0 for growth in growth_list])/len(growth_list))*100
        added_growth = ((price_list[-1] - price_list[0])/price_list[0])*100
        return percentage_pos_growth + added_growth


class StableStockMetric:

    @staticmethod
    def avg(lst):
        return float(sum(lst))/len(lst)

    @staticmethod
    def score(price_list):
        """Given the price list, determines a score showing how stable the stock is in terms of continous growth"""

        bucket_size = 15
        bucketed_avg_prices = []

        price_list = [float(price.replace(',', '')) for price in price_list]

        for ind in range(0, len(price_list), bucket_size):
            lst = price_list[ind: min(len(price_list), ind + bucket_size)]
            bucketed_avg_prices.append(
                StableStockMetric.avg(lst)
            )

        growth_list = []
        start_index = 1

        for ind in range(start_index, len(bucketed_avg_prices)):
            curr_price = bucketed_avg_prices[ind]
            last_price = bucketed_avg_prices[ind - 1]

            growth_percent = ((curr_price - last_price) / last_price) * 100
            growth_list.append(growth_percent)

        # Find percentage of positive growth in growth_list
        percentage_pos_growth = (sum([1 if growth > 0 else 0 for growth in growth_list]) / len(growth_list)) * 100
        # summed_growth = sum(growth_list)*100

        return percentage_pos_growth
