from math import exp, sqrt
from GameLogic.Orders import Order, Sell, Buy


class MarketImpactCalculator:
    def get_market_impact(self, order: Order, asset_daily_volume):
        raise NotImplementedError

    def get_updated_price(self, num_shares, asset):
        raise NotImplementedError


class ExponentialMarketImpactCalculator(MarketImpactCalculator):
    def __init__(self, alpha):
        self.alpha = alpha

    'aacording to   Caccioli1,: mi = e^(-ALPHA*frac_of_asset_liquidated)'
    def get_market_impact(self, order: Order, asset):
        frac_liquidated = order.num_shares / asset.daily_volume
        sign = -1 if isinstance(order, Sell) else 1
        return exp(sign * self.alpha * frac_liquidated)

    def get_updated_price(self, num_shares, asset):
        frac_liquidated = num_shares / asset.daily_volume
        return asset.price * exp(self.alpha * frac_liquidated)


class SqrtMarketImpactCalculator(MarketImpactCalculator):
    def __init__(self, Y=0.5):
        self.Y = Y

    def get_market_impact(self, order: Order, asset):
        delta = sqrt(order.num_shares / asset.daily_volume) * self.Y * asset.volatility
        if isinstance(order, Sell):
            return 1 - delta
        if isinstance(order, Buy):
            return 1 + delta
        raise ValueError

    def get_updated_price(self, num_shares, asset):
        frac_liquidated = num_shares / asset.daily_volume
        delta = sqrt(abs(frac_liquidated)) * self.Y * asset.volatility
        if frac_liquidated < 0:
            return 1 - delta
        else:
            return 1 + delta
        raise ValueError


