from math import exp
from Orders import Order, Sell


class MarketImpactCalculator:
    def get_market_impact(self, order: Order, asset_total_shares):
        raise NotImplementedError


class ExponentialMarketImpactCalculator(MarketImpactCalculator):
    def __init__(self, alpha):
        self.alpha = alpha

    'aacording to   Caccioli1,: mi = e^(-ALPHA*frac_of_asset_liquidated)'
    def get_market_impact(self, order: Order, asset_total_shares):
        frac_liquidated = order.num_shares / asset_total_shares
        sign = -1 if isinstance(order, Sell) else 1
        return exp(sign * self.alpha * frac_liquidated)
