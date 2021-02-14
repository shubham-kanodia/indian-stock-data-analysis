from datetime import datetime
import datetime as dt


class Stock:
    def __init__(self, stock_symbol, dao):
        self.symbol = stock_symbol
        self.dao = dao
        self.data = self.dao.get_stock_data(stock_symbol)

    def convert_date(self, date):
        date = datetime.strptime(date, "%d-%b-%Y").date()
        return date.strftime("%Y-%m-%d")

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

    def _sortable_date_format(self, date):
        date = datetime.strptime(date, "%d-%b-%Y").date()
        return date.strftime("%Y%m%d")

    def get_price_history(self):
        sorted_data = sorted(self.data,
                             key=lambda x: self._sortable_date_format(x) if not x == "_id" else "")
        dates = [self.convert_date(key) for key in sorted_data if key != "_id"]
        prices = [self.data[key]["close_price"] for key in sorted_data if key != "_id"]
        return dates, prices
