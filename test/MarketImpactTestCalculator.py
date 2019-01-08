from math import exp
from Actions import Order, Sell
from MarketImpactCalculator import MarketImpactCalculator


class MarketImpactTestCalculator(MarketImpactCalculator):
    'aacording to   Caccioli1,: mi = e^(-ALPHA*frac_of_asset_liquidated)'
    def get_market_impact(self, order: Order, asset_total_shares):
        sign = -1 if isinstance(order, Sell) else 1
        return sign *2
