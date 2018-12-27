from functools import reduce
from typing import List


class Asset():
    def __init__(self, price, total_shares, symbol):
        self.symbol = symbol
        self.price = price
        self.total_shares = total_shares

    def update_price(self, new_price):
        self.price = new_price


class Holding:
    def __init__(self, asset:Asset, num_shares):
        self.asset = asset
        if num_shares > asset.total_shares:
            raise  ValueError('cannot hold more then available number of shares')
        self.num_shares = num_shares


class Fund():
    def __init__(self, holdings:List[Holding], capital, initial_leverage, tolerance):
        self.holdings = holdings
        self.initial_leverage = initial_leverage
        self.capital = capital
        self.tolerance = tolerance

    def liquidate(self):
        self.holdings = []

    def is_liquidated(self):
        return not self.holdings

    def compute_protfolio_value(self):
        v = 0
        for holding in self.holdings:
            v += holding.num_shares * holding.asset.price
        return v

    def compute_curr_leverage(self):
        return self.compute_protfolio_value()/self.capital - 1;

    def marginal_call(self):
        return self.compute_curr_leverage() / self.initial_leverage < self.tolerance;


class BipartiteNetwork:
    def __init__(self, funds):
        self.funds = funds

    def __init__(self, num_assets, num_funds, asset_diversification, preferential_asset_attachment):
        self.funds = []







