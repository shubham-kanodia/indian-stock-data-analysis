from datetime import datetime
import datetime as dt


class Stock:
    def __init__(self, stock_symbol, exporter):
        self.symbol = stock_symbol
        self.exporter = exporter
        self.data = self.exporter.get_stock_data(stock_symbol)

    def convert_date(self, date):
        date = datetime.strptime(date, "%d-%m-%Y").date()
        return date.strftime("%d-%b-%Y")

    def get_closing_price(self, date):
        """Note: date format should be dd-mm-yyyy"""
        date = self.convert_date(date)
        price = self.data.get(date, None)
        return price["close_price"] if price else None

    def prev_day(self, date):
        date = (datetime.strptime(date, "%d-%m-%Y").date() - dt.timedelta(1)) \
            .strftime("%d-%m-%Y")
        return date

    def get_prev_day_price(self, date):
        """Note: date format should be dd-mm-yyyy"""
        date = self.prev_day(date)
        return self.get_closing_price(date)

    def get_last_n_days_data(self, n):
        day = dt.date.today()\
            .strftime("%d-%m-%Y")
        data = [self.get_closing_price(day)]
        num_of_days = 1
        while num_of_days < n:
            if int(day.split("-")[2]) < 2016:
                break
            price = self.get_prev_day_price(day)
            if price:
                data.append(price)
                num_of_days += 1
            day = self.prev_day(day)
        return list(reversed(data))
