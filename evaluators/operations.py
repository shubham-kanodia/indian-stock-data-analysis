import math


class Operations:

    @staticmethod
    def calculate_rms(lst):
        sm = 0
        for elem in lst:
            sm += elem * elem
        sm = float(sm) / len(lst)
        return math.sqrt(sm)

    @staticmethod
    def get_ordered_earnings(stock_data):
        unordered_earnings = []
        for key in stock_data:
            split_key = key.split(" ")
            if split_key[0] == "Mar" and "net_profit" in stock_data[key]:
                unordered_earnings.append((int(split_key[1]), stock_data[key]["net_profit"]))
        ordered_earnings = sorted(unordered_earnings, key=lambda x: x[0])
        return [int(earning[1]) for earning in ordered_earnings]
