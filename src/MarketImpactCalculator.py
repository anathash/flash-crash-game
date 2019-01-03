from math import exp
from Actions import Order, Sell
from Constants import ALPHA


class ExponentialMarketImpactCalculator:
    'aacording to   Caccioli1,: mi = e^(-ALPHA*frac_of_asset_liquidated)'
    @staticmethod
    def get_market_impact(order: Order, asset_total_shares):
        frac_liquidated = order.num_shares / asset_total_shares
        sign = -1 if isinstance(order, Sell) else 1
        return exp(sign * ALPHA * frac_liquidated)
