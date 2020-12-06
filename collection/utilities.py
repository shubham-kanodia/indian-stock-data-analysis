from collection.data_collection import DataCollection
from collection.exporter import Exporter
from evaluators.operations import Operations


class Utilities:
    """ Updating data, one stop for all operations
        Make sure the raw documents are updated for
        - stock sector data
        - income statement data
     """
    def __init__(self):
        self.data_collection = DataCollection()
        self.exporter = Exporter()

    def update_stock_sector_data(self):
        self.data_collection.collect_sector_data()

    def update_income_statement_data(self):
        self.data_collection.collect_income_statement_data()

    @staticmethod
    def calculate_rms_change(stock_data):
        earnings = Operations.get_ordered_earnings(stock_data)
        change = []
        for ind in range(1, len(earnings)):
            change.append(((earnings[ind] - earnings[ind-1])*100.0)/earnings[ind-1])
        return Operations.calculate_rms(change)

    def update_self_built_parameters(self):
        """ Efficiency of rms change parameter is yet to be evaluated """
        # Calculate and update RMS change in earnings for each sector
        all_sectors = self.exporter.get_sectors_list()
        for sector in all_sectors:

            if sector == '':
                continue

            print(f"[Processing] Sector: {sector}")
            stocks = self.exporter.get_stocks_from_sector(sector)
            sector_change_sum = 0
            sector_stocks_count = 0
            for stock in stocks:
                try:
                    stock_financials = self.exporter.get_stock_financial_data(stock)
                    stock_change = self.calculate_rms_change(stock_financials)
                    sector_change_sum += stock_change
                    sector_stocks_count += 1
                except Exception:
                    continue

            sector_rms_change = sector_change_sum/sector_stocks_count
            self.exporter.add_sector_rms_change(sector, sector_rms_change)
