from math import exp, sqrt
from GameLogic.Orders import Order, Sell


class MarketImpactCalculator:
    def get_market_impact(self, order: Order, asset_daily_volume):
        raise NotImplementedError


class ExponentialMarketImpactCalculator(MarketImpactCalculator):
    def __init__(self, alpha):
        self.alpha = alpha

    'aacording to   Caccioli1,: mi = e^(-ALPHA*frac_of_asset_liquidated)'
    def get_market_impact(self, order: Order, asset):
        frac_liquidated = order.num_shares / asset.daily_volume
        sign = -1 if isinstance(order, Sell) else 1
        return exp(sign * self.alpha * frac_liquidated)


class SquareRootMarketImpactCalculator(MarketImpactCalculator):
    def __init__(self, Y):
        self.Y = Y

    'aacording to   Caccioli1,: mi = e^(-ALPHA*frac_of_asset_liquidated)'
    def get_market_impact(self, order: Order, asset):
        frac_liquidated = sqrt(order.num_shares / asset.daily_volume) * self.Y * asset.volatility
        sign = -1 if isinstance(order, Sell) else 1
        return frac_liquidated * sign
