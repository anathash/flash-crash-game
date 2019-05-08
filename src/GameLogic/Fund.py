from math import inf, floor
from typing import Dict

from GameLogic.Asset import Asset
from GameLogic.Orders import Sell
from GameLogic.SysConfig import SysConfig


class Fund:
    def __init__(self, symbol, portfolio: Dict[str, int], initial_capital, initial_leverage, tolerance):
        self.symbol = symbol
        self.portfolio = portfolio
        self.initial_leverage = initial_leverage
        self.initial_capital = initial_capital
        self.loan = initial_capital*initial_leverage
        self.tolerance = tolerance
        self.is_liquidating = False
        self.is_in_default = False

    def __eq__(self, other):
        return isinstance(other, Fund) and \
               self.symbol == other.symbol and \
               self.portfolio == other.portfolio and \
               self.initial_leverage == other.initial_leverage and \
               self.initial_capital == other.initial_capital and \
               self.tolerance == other.tolerance and \
               self.loan == other.loan

    def update_state(self, assets):
        curr_leverage = self.compute_curr_leverage(assets)
        if curr_leverage == inf:
            self.is_in_default = True
            self.is_liquidating = True
        else:
            if curr_leverage / self.initial_leverage > self.tolerance:
                self.is_liquidating = True

    def gen_liquidation_orders(self, assets: Dict[str, Asset]):
        orders = []
        assets_to_remove = []
        for asset_symbol, num_shares in self.portfolio.items():
            asset = assets[asset_symbol]
            shares_limit = floor(asset.avg_minute_volume * SysConfig.get("MINUTE_VOLUME_LIMIT"))
            shares_to_sell = min(shares_limit, num_shares)
            orders.append(Sell(asset_symbol, shares_to_sell, asset.price))
            self.portfolio[asset_symbol] -= shares_to_sell
            if self.portfolio[asset_symbol] == 0:
                assets_to_remove.append(asset_symbol)
        for asset_symbol in assets_to_remove:
            self.portfolio.pop(asset_symbol)
        return orders

    def get_orders(self, assets: Dict[str, Asset]):
        if self.is_liquidating:
            return self.gen_liquidation_orders(assets)
        return []

    def liquidate(self):
        self.is_liquidating = True

    def is_in_margin_call(self):
        return self.is_liquidating

    def default(self):
        return self.is_in_default

    def compute_curr_capital(self, assets):
        return self.compute_portfolio_value(assets) - self.loan

    def compute_portfolio_value(self, assets):
        v = 0
        for asset_symbol, num_shares in self.portfolio.items():
            v += num_shares * assets[asset_symbol].price
        return v

    """ leverage = curr_portfolio_value / curr_capital -1
       = curr_portfolio_value/(curr_portfolio_value - loan) -1
    """

    def compute_curr_leverage(self, assets):
        curr_portfolio_value = self.compute_portfolio_value(assets)
        curr_capital = curr_portfolio_value - self.loan
        if curr_capital <= 0:
            return inf
        return curr_portfolio_value / curr_capital - 1 #return self.compute_portfolio_value(assets) / self.capital - 1

    def marginal_call(self, assets):
        return self.compute_curr_leverage(assets) / self.initial_leverage > self.tolerance

