#!/usr/bin/python
import json
import random
from math import floor

import networkx as nx
import numpy


from typing import Dict, List
import jsonpickle

from GameLogic import MarketImpactCalculator
from GameLogic.Fund import Fund
from GameLogic.Asset import Asset
from GameLogic.Orders import Order

'TODO: do we need the total market cap of assets or do funds hold the entire market'

class AssetFundsNetwork:
    def __init__(self, funds: Dict[str, Fund], assets: Dict[str, Asset], mi_calc: MarketImpactCalculator, intraday_asset_gain_max_range =None):
        self.mi_calc = mi_calc
        self.funds = funds
        self.assets = assets
        if intraday_asset_gain_max_range:
            self.run_intraday_simulation(intraday_asset_gain_max_range, 0.7)

    def __eq__(self, other):
        return isinstance(other, AssetFundsNetwork) and isinstance(other.mi_calc, type(self.mi_calc)) and \
               self.funds == other.funds and self.assets == other.assets

    def __repr__(self):
        return str(self.funds)

    def are_funds_leveraged_less_than(self, leverage_goal):
        for fund in self.funds.values():
            if leverage_goal < fund.compute_curr_leverage(self.assets):
                return False
        return True

    def run_intraday_simulation_2(self, intraday_asset_gain_max_range):
        if (intraday_asset_gain_max_range < 1):
            raise ValueError
        for asset in self.assets.values():
            price_gain = random.uniform(1, intraday_asset_gain_max_range)
            asset.set_price(asset.price * price_gain)

    def run_intraday_simulation(self, intraday_asset_gain_max_range, leverage_goal):
        if intraday_asset_gain_max_range < 1:
            raise ValueError
        while not self.are_funds_leveraged_less_than(leverage_goal):
            for asset in self.assets.values():
                price_gain = random.uniform(1, intraday_asset_gain_max_range)
                asset.set_price(asset.price * price_gain)

    @classmethod
    def generate_random_network(cls, density, num_funds, num_assets, initial_capitals, initial_leverages,
                                assets_initial_prices, tolerances, assets_num_shares, volatility, mi_calc: MarketImpactCalculator):
        connected = False
        while not connected:
            g = nx.algorithms.bipartite.random_graph(num_funds, num_assets, density, directed=True)
            connected = True
            try:
                fund_nodes, asset_nodes = nx.bipartite.sets(g)
            except nx.AmbiguousSolution:
                connected = False

        investment_proportions = {}
        for fund_node in list(fund_nodes):
            fund_symbol = 'f' + str(fund_node)
            investments = list(g.out_edges(fund_node))
            rand = list(numpy.random.randint(1, 10, size=len(investments)))
            rand_sum = sum(rand)
            investment_proportions[fund_symbol] = [float(i) / rand_sum for i in rand]

        return cls.gen_network_from_graph(g, investment_proportions, initial_capitals,
                                          initial_leverages, assets_initial_prices,
                                          tolerances, assets_num_shares, volatility, mi_calc)

    @classmethod
    def gen_network_from_graph(cls, g, investment_proportions,
                               initial_capitals, initial_leverages, assets_initial_prices,
                               tolerances, assets_num_shares, volatility, mi_calc: MarketImpactCalculator):
        funds = {}
        assets = {}
        fund_nodes, asset_nodes = nx.bipartite.sets(g)
        num_funds = len(fund_nodes)
        for i in range(len(asset_nodes)):
            symbol = 'a' + str(i)
            assets[symbol] = Asset(assets_initial_prices[i], assets_num_shares[i], volatility[i], symbol)
        for i in range(num_funds):
            portfolio = {}
            fund_symbol = 'f' + str(i)
            investments = list(g.out_edges(i))
            if investments:
                fund_capital = initial_capitals[i] * (1 + initial_leverages[i])
                for j in range(len(investments)):
                    asset_index = investments[j][1] - num_funds
                    asset_symbol = 'a' + str(asset_index)
                    asset = assets[asset_symbol]
                    portfolio[asset_symbol] = floor(investment_proportions[fund_symbol][j] * fund_capital/asset.price)
            funds[fund_symbol] = Fund(fund_symbol, portfolio, initial_capitals[i], initial_leverages[i], tolerances[i])
        return cls(funds, assets, mi_calc)


    @classmethod
    def load_from_file(cls, file_name, mi_calc: MarketImpactCalculator):
        class_dict = json.load(open(file_name))
        class_funds = class_dict['funds']
        class_assets = class_dict['assets']
        funds = jsonpickle.decode(class_funds)
        assets = jsonpickle.decode(class_assets)
        return cls(funds, assets, mi_calc)

    def save_to_file(self, filename):
        funds_dict = jsonpickle.encode(self.funds)
        asset_dict = jsonpickle.encode(self.assets)
        class_dict = {'funds': funds_dict, 'assets': asset_dict}
        with open(filename, 'w') as fp:
            json.dump(class_dict, fp)

    def get_canonical_form(self):
        num_funds = len(self.funds)
        num_assets = len(self.assets)
        board = numpy.zeros([num_funds, num_assets])
        for i in range(num_funds):
            fund = self.funds['f' + str(i)]
            for j in range(num_assets):
                sym = 'a' + str(j)
                if sym in fund.portfolio:
                    board[i, j] = fund.portfolio[sym] * self.assets[sym].price
        return board

    def get_liquidation_orders(self):
        orders = []
        for fund in self.funds.values():
            orders.append(fund.get_orders(self.assets))
        return orders

    def update_funds(self):
        for fund in self.funds.values():
            fund.update_state(self.assets)

    def apply_action_old(self, orders: List[Order]):
        liquidation_orders = []
        for order in orders:
            asset = self.assets[order.asset_symbol]
            new_price = asset.price * self.mi_calc.get_market_impact(order, asset)
            asset.set_price(new_price)
        for fund in self.funds.values():
            if not fund.is_liquidated():
                if fund.marginal_call(self.assets):
                    liquidation_orders.extend(fund.gen_liquidation_orders())
                    fund.liquidate()
        if liquidation_orders:
            self.apply_action(liquidation_orders)


"""
    def __init__(self, portfolio_matrix, num_funds, num_assets, initial_capitals, initial_leverages,
                 assets_initial_prices, tolerances, assets_num_shares, mi_calc: MarketImpactCalculator):
        self.mi_calc = mi_calc
        self.funds = {}
        self.assets = {}
        for i in range(num_assets):
            symbol = 'a' + str(i)
            self.assets[symbol] = Asset(assets_initial_prices[i], assets_num_shares[i], symbol)
        funds = {}
        for i in range(num_funds):
            portfolio = {}
            fund_symbol = 'f' + str(i)
            for j in range(num_assets):
                asset_symbol = 'a'+str(j)
                if portfolio_matrix[i][j] != 0:
                    'TODO: verify no fractions'
                    'portfolio.append(Holding(self.assets[j], portfolio_matrix[i][j] / self.assets[j].price))'
                    portfolio[fund_symbol] = portfolio_matrix[i][j] / self.assets['A' + str(j)].price
            funds[fund_symbol] = Fund(fund_symbol, portfolio, initial_capitals[i], initial_leverages[i], tolerances[i])
        return

            def __init__(self, g: nx.DiGraph, num_funds, num_assets, initial_capitals, initial_leverages,
                 assets_initial_prices, tolerances, assets_num_shares, mi_calc: MarketImpactCalculator):
        self.mi_calc = mi_calc
        self.funds = {}
        self.assets = {}
        for i in range(num_assets):
            symbol = 'a' + str(i)
            self.assets[symbol] = Asset(assets_initial_prices[i], assets_num_shares[i], symbol)
        fund_nodes, asset_nodes = nx.bipartite.sets(g)
        for fund_node in list(fund_nodes):
            portfolio = {}
            fund_symbol = 'f' + str(fund_node)
            investments = g.out_edges(fund_node)
            for investment in investments:
                asset_index = num_funds - investment[1]
                asset_symbol = 'a'+str(asset_index)
                portfolio[asset_symbol] = 100
            self.funds[fund_symbol] = Fund(fund_symbol, portfolio, initial_capitals[i], initial_leverages[i], tolerances[i])

                def load_from_file(cls, file_name):
        d2 = json.load(open(file_name))
        instance = object.__new__(Fund.__class__)
        for key, value in d2['funds']['f0'].items():
            setattr(instance, key, value)
        setattr(instance, key, value)

           def save_to_file(self, filename):
        funds_dict = {}
        for fund_sym, fund in self.funds.items():
            funds_dict[fund_sym] = json.dumps(fund.__dict__)
        asset_dict = {}
        for asset_sym, asset in self.assets.items():
            asset_dict[asset_sym] = json.dumps(asset.__dict__)
        class_dict = {'funds': funds_dict, 'assets': asset_dict}
        with open(filename, 'w') as fp:
            json.dump(class_dict, fp)


   @classmethod
    def load_from_file(cls, input_file, assets_initial_prices, tolerances, assets_num_shares, mi_calc: MarketImpactCalculator):
        params = np.load(input_file).item()
        num_assets = int(params['num_assets'])
        num_funds = int(params['num_funds'])
        initial_capitals = ast.literal_eval(params['initial_capitals'])
        initial_leverages = ast.literal_eval(params['initial_leverages'])
        a = np.zeros((num_funds, num_assets), numpy.int8)
        lines = params['portfolio_matrix'].split(';')
        for i in range(num_funds):
            vals = lines[i].split(',')
            for j in range(num_assets):
                a[i][j] += int(vals[j])

        cls(a, num_funds, num_assets, initial_capitals,initial_leverages,
            assets_initial_prices, tolerances, assets_num_shares, mi_calc)

    @classmethod
    def generate_random_network(cls, density,  num_funds, num_assets, initial_capitals, initial_leverages,
                                assets_initial_prices, tolerances, assets_num_shares, mi_calc: MarketImpactCalculator):
        connected = False
        while not connected:
            g = nx.algorithms.bipartite.random_graph(num_funds, num_assets, density, directed=True)
            connected = True
            try:
                fund_nodes, asset_nodes = nx.bipartite.sets(g)
            except nx.AmbiguousSolution:
                connected = False

        funds = {}
        assets = {}
        for i in range(num_assets):
            symbol = 'a' + str(i)
            assets[symbol] = Asset(assets_initial_prices[i], assets_num_shares[i], symbol)
        for fund_node in list(fund_nodes):
            portfolio = {}
            fund_symbol = 'f' + str(fund_node)
            investments = list(g.out_edges(fund_node))
            rand = list(numpy.random.randint(0, 10, len(investments)))
            rand_sum = sum(rand)
            investment_proportion = [float(i)/rand_sum for i in rand]
            fund_capital = initial_capitals[fund_node] * (1 + initial_leverages[fund_node])
            for i in range(len(investments)):
                asset_index = num_funds - investments[i][1]
                asset_symbol = 'a'+str(asset_index)
                portfolio[asset_symbol] = investment_proportion[i] * fund_capital
            funds[fund_symbol] = Fund(fund_symbol, portfolio, initial_capitals[i], initial_leverages[i], tolerances[i])
        return cls(funds, assets, mi_calc)

"""
