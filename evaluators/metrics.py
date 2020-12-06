from evaluators.operations import Operations


class Metrics:
    """ Scores a stock based on chosen parameters """

    def __init__(self, exporter):
        self.exporter = exporter
        self.operations = Operations()

    def calculate_earning_consistency_score(self, stock):
        """ Calculates a weighted score to find out consistency of the earnings of stock """
        earnings = self.operations.get_ordered_earnings(stock.financial)

        percentage_changes = []
        for ind in range(1, len(earnings)):
            percentage_changes.append(((earnings[ind] - earnings[ind - 1]) * 100.0) / earnings[ind - 1])

        # if stock.sector == '':
        #     sector_rms_change = self.operations.calculate_rms(percentage_changes)
        # else:
        #     sector_rms_change = self.exporter.get_sector_rms_change(stock.sector)

        growth_param = sum([-1 if change < 1 else 1 for change in percentage_changes])
        # change_param = sum(percentage_changes)/sector_rms_change

        # Since the growth can be great during initial times but the price of stock at end might be too
        # low, hence multiplying with last_earning/max_earning
        last_earning = float(earnings[-1])
        max_earning = float(max(earnings))
        increment_rate = last_earning/max_earning if max_earning > 0 else 0

        # If the last earning is -ve and the max earning is also -ve, then the purpose of increment rate was being
        # defeated hence we consider only companies which have max_earning > 0

        if growth_param < 0 and increment_rate < 0:
            return -1 * float(growth_param) * increment_rate / 11.0
        else:
            return float(growth_param) * increment_rate / 11.0
