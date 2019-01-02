from math import exp
from typing import  Dict

import MarketImpactCalculator
from Actions import Order, Action, Sell
from Constants import ALPHA

'TODO: do we need the total market cap of assets or do funds hold the entire market'


class Asset:
    def __init__(self, price, total_shares, symbol):
        self.price = price
        self.total_shares = total_shares
        self.symbol = symbol

    def set_price(self, new_price):
        self.price = new_price

    'exponential market impact function accprding to Caccioli 2012'
    def get_market_impact(self, order: Order):
        frac_liquidated = order.num_shares / self.total_shares
        return exp(-ALPHA * frac_liquidated)


class Fund:
    def __init__(self, symbol, portfolio: Dict[str,int], initial_capital, initial_leverage, tolerance,):
        self.symbol = symbol
        self.portfolio = portfolio
        self.initial_leverage = initial_leverage
        self.capital = initial_capital
        self.tolerance = tolerance

    def gen_liquidation_orders(self):
        orders = []
        for asset_symbol, num_shares in self.portfolio:
            orders.append(Sell(asset_symbol, num_shares))
        return orders

    def liquidate(self):
        self.portfolio = []

    def is_liquidated(self):
        return not self.portfolio

    def compute_portfolio_value(self, assets):
        v = 0
        for asset_symbol, num_shares in self.portfolio.items():
            v += num_shares * assets[asset_symbol].price
        return v

    def compute_curr_leverage(self, assets):
        return self.compute_portfolio_value(assets)/self.capital - 1

    def marginal_call(self, assets):
        return self.compute_curr_leverage(assets) / self.initial_leverage < self.tolerance


class AssetFundsNetwork:
    def __init__(self, input_file):
        self.funds = {}
        self.assets = {}
        self.mi_calc = MarketImpactCalculator()
        return

    def __init__(self, portfolio_matrix, num_assets, initial_capitals, initial_leverages, tolerances,
                 assets_initial_prices, assets_num_shares, mi_calc: MarketImpactCalculator):
        self.mi_calc = mi_calc
        self.funds = {}
        self.assets = {}
        for i in range(num_assets):
            symbol = 'A' + str(i)
            self.assets[symbol] = Asset(assets_initial_prices[i], assets_num_shares[i], symbol)
        funds = {}
        for i in range(portfolio_matrix):
            portfolio = {}
            for j in portfolio_matrix[i]:
                if portfolio_matrix[i][j] != 0:
                    'TODO: verify no fractions'
                    'portfolio.append(Holding(self.assets[j], portfolio_matrix[i][j] / self.assets[j].price))'
                    portfolio['A' + self.assets[j]] = portfolio_matrix[i][j] / self.assets[j].price
            fund_symbol = 'F' + str(i)
            funds[fund_symbol] = Fund(fund_symbol, portfolio, initial_capitals[i], initial_leverages[i], tolerances[i])
        return

    def apply_action(self, action: Action):
        liquidation_orders = []
        for order in action.orders:
            asset = self.assets[order.asset_symbol]
            new_price = asset.price * self.mi_calc.get_market_impact(order, asset.total_shares)
            asset.set_price(new_price)
        for fund in self.funds.itervalues:
            if not fund.is_liquidated():
                if fund.marginal_call(self.assets):
                    liquidation_orders.append(fund.gen_liquidation_orders())
                    fund.liquidate()
        if liquidation_orders:
            self.apply_action(Action(liquidation_orders))





