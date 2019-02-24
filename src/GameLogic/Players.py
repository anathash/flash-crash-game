import random
from math import floor
from typing import List, Dict

from GameLogic.SysConfig import SysConfig
from GameLogic.Orders import Sell, Move, Order, Buy
from GameLogic.AssetFundNetwork import Asset, Fund


class Player:
    def __init__(self, initial_capital, initial_portfolio: Dict[str, int], asset_slicing: int,
                 max_assets_in_action: int):
        self.initial_capital = initial_capital
        self.portfolio = initial_portfolio
        self.max_assets_in_action = max_assets_in_action
        self.asset_slicing = asset_slicing

    def apply_action(self, orders: Move):
        for order in orders:
            self.apply_order(order)

    def get_valid_actions(self, assets: Dict[str, Asset]):
        raise NotImplementedError


    def gen_random_action(self, assets: Dict[str, Asset]):
        raise NotImplementedError

    def is_legal(self, orders: List[Order]):
        return True

    def resources_exhusted(self):
        raise NotImplementedError()

    def apply_order(self, order: Move):
        raise NotImplementedError

    def game_reward(self, funds: Dict[str, Fund],  history=None):
        raise NotImplementedError
"""    def get_valid_actions(self, assets: Dict[str, Asset] = None):
        actions = []
        orders_lists = self.gen_orders(assets)
        selected_assets_comb = itertools.combinations(orders_lists, self.max_assets_in_action)
        for comb in selected_assets_comb:
            orders = list(itertools.product(tuple(comb)))
            if self.is_legal(orders):
                actions.append(Action(orders))
"""


class Attacker(Player):
    def __init__(self, initial_portfolio: Dict[str, int], goals: List[str], asset_slicing, max_assets_in_action):
        super().__init__(0, initial_portfolio, asset_slicing, max_assets_in_action)
        self.goals = goals
        self.resources_exhusted_flag = False

    def resources_exhusted(self):
        if not self.portfolio:
            self.resources_exhusted_flag = True
        return self.resources_exhusted_flag

    def is_goal_achieved(self, funds: Dict[str, Fund]):
        for fund_symbol in self.goals:
            if not funds[fund_symbol].is_liquidated():
                return False
        return True

    def apply_order(self, order: Sell):
        if not isinstance(order, Sell):
            raise ValueError("attacker only sells")

        self.initial_capital += order.share_price * order.num_shares
        num_shares = self.portfolio[order.asset_symbol]
        num_shares -= order.num_shares
        if num_shares == 0:
            del self.portfolio[order.asset_symbol]
        else:
            self.portfolio[order.asset_symbol] = num_shares

    def game_reward(self, funds: List[Fund], history=None):
        for fund in self.goals:
            if not funds[fund].is_liquidated():
                return -1
        return 1

    def get_valid_actions(self, assets: Dict[str, Asset]):
        assets_list = [assets[x] for x in self.portfolio.keys()]
        if self.max_assets_in_action > 1:
            orders = self.gen_orders_rec(assets_list)
        else:
            orders = self.gen_single_asset_orders(assets_list)
        if not orders:
            self.resources_exhusted_flag = True
        return orders

    def gen_single_asset_orders(self, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        for asset in assets:
            for i in range(1, self.asset_slicing + 1):
                shares_to_sell = int(i * self.portfolio[asset.symbol] / self.asset_slicing)
                if asset.price * shares_to_sell < SysConfig.get(SysConfig.MIN_ORDER_VALUE): #ignore small orders
                    continue
                order = Sell(asset.symbol, shares_to_sell, asset.price)
                orders_list.append([order])
        return orders_list


    def gen_orders_rec(self, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        orders_to_add = self.gen_orders_rec(assets[1:])
        orders_list.extend(orders_to_add)
        for i in range(1, self.asset_slicing + 1):
            shares_to_sell = int(i * self.portfolio[asset.symbol] / self.asset_slicing)
            if asset.price * shares_to_sell < SysConfig.get(SysConfig.MIN_ORDER_VALUE): #ignore small orders
                continue
            order = Sell(asset.symbol, shares_to_sell, asset.price)
            orders_list.append([order])
            for orders in orders_to_add:
                if len(orders) < self.max_assets_in_action:
                    order_including_asset = list(orders)
                    order_including_asset.append(order)
                    orders_list.append(order_including_asset)
        return orders_list

    def gen_orders_rec_old(self, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        sell_percent = self.sell_share_portion_jump
        orders_to_add = self.gen_orders_rec(assets[1:])
        orders_list.extend(orders_to_add)
        while sell_percent <= 1:
            shares_to_sell = int(sell_percent * self.portfolio[asset.symbol])
            order = Sell(asset.symbol, shares_to_sell, asset.price)
            orders_list.append([order])
            for orders in orders_to_add:
                if len(orders) < self.max_assets_in_action:
                    order_including_asset = list(orders)
                    order_including_asset.append(order)
                    orders_list.append(order_including_asset)
            sell_percent += self.sell_share_portion_jump
        return orders_list

    def gen_random_action(self, assets: Dict[str, Asset] = None):
        orders = []
        portfolio_assets = list(self.portfolio.keys())
        num_assets = min(len(portfolio_assets), random.randint(1, self.max_assets_in_action))
        chosen_assets = random.sample(portfolio_assets, num_assets)

        for sym in chosen_assets:
            asset = assets[sym]
            portion = random.randint(1, self.asset_slicing)
            shares_to_sell = int(portion * self.portfolio[asset.symbol] / self.asset_slicing)
            order = Sell(asset.symbol, shares_to_sell, asset.price)
            orders.append(order)

        return orders

    def __str__(self):
        return 'Attacker'


class Defender(Player):
    def __init__(self, initial_capital, asset_slicing, max_assets_in_action):
        super().__init__(initial_capital, {}, asset_slicing, max_assets_in_action)
        self.resources_exhusted_flag = False

    ' think: should we allow selling of assets when capital is zero?'
    def resources_exhusted(self):
        'allow overdraft?'
        if self.initial_capital <= 0:
            self.resources_exhusted_flag = True

        return self.resources_exhusted_flag

        'TODO: make sure we dont get to very small numbers'

    def apply_order(self, order: Buy):
        if not isinstance(order, Buy):
            raise ValueError("attacker only buys")
        self.initial_capital -= order.share_price * order.num_shares
        num_shares = self.portfolio[order.asset_symbol] if order.asset_symbol in self.portfolio else 0
        num_shares += order.num_shares
        self.portfolio[order.asset_symbol] = num_shares

    def game_reward(self, funds: Dict[str, Fund], history=None):
        raise NotImplementedError

    def is_legal(self, orders: List[Order]):
        capital_needed = 0
        for order in orders:
            capital_needed += order.share_price * order.num_shares
            if capital_needed > self.initial_capital:
                return True
        return False

    def get_valid_actions(self, assets: Dict[str, Asset] = None):
        if self.max_assets_in_action > 1:
            orders_list_tup = self.gen_orders_rec(list(assets.values()))
            orders_list = [x[0] for x in orders_list_tup]
        else:
            orders_list = self.gen_single_asset_orders(list(assets.values()))
        if not orders_list:
            self.resources_exhusted_flag = True
            return []
        return orders_list

    def gen_random_action(self, assets: Dict[str, Asset] = None):
        orders = []
        num_assets = random.randint(1, self.max_assets_in_action)
        chosen_assets = random.sample(list(assets.values()), num_assets)
        action_required_capital = 0
        while not orders: #in case no valid orders for the entire iteration
            i = 0
            while i < num_assets and action_required_capital < self.initial_capital:
                asset = chosen_assets[i]
                portion = random.randint(1, self.asset_slicing)
                order_required_capital = portion * asset.price * asset.daily_volume/ self.asset_slicing
                if order_required_capital + action_required_capital > self.initial_capital:
                    portion = int(floor((self.initial_capital * self.asset_slicing) / (asset.price * asset.daily_volume)))
                order = Buy(asset.symbol, portion*chosen_assets[i].daily_volume/self.asset_slicing, asset.price)
                action_required_capital += order_required_capital
                orders.append(order)
                i += 1
        return orders

    def gen_single_asset_orders(self, assets: List[Asset]):
        orders_list = []
        for asset in assets:
            buy_slice = 1
            capital_jump = asset.price * asset.daily_volume / self.asset_slicing
            capital_needed = capital_jump
            while buy_slice <= self.asset_slicing and capital_needed <= self.initial_capital:
                shares_to_buy = int(asset.daily_volume * buy_slice / self.asset_slicing)
                if asset.price * shares_to_buy < SysConfig.get(SysConfig.MIN_ORDER_VALUE):  # ignore small orders
                    buy_slice += 1
                    continue
                order = Buy(asset.symbol, shares_to_buy, asset.price)
                orders_list.append([order])
                buy_slice += 1
                capital_needed += capital_jump
        return orders_list

    def gen_orders_rec(self, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        buy_slice = 1
        orders_to_add = self.gen_orders_rec(assets[1:])
        orders_list.extend(orders_to_add)
        capital_jump = asset.price * asset.daily_volume / self.asset_slicing
        capital_needed = capital_jump
        while buy_slice <= self.asset_slicing and capital_needed <= self.initial_capital:
            shares_to_buy = int(asset.daily_volume * buy_slice / self.asset_slicing)
            if asset.price * shares_to_buy < SysConfig.get(SysConfig.MIN_ORDER_VALUE):  # ignore small orders
                buy_slice += 1
                continue
            order = Buy(asset.symbol, shares_to_buy, asset.price)
            orders_list.append(([order], capital_needed))
            for tup in orders_to_add:
                orders = tup[0]
                orders_capital = tup[1]
                total_capital = capital_needed + orders_capital
                if len(orders) < self.max_assets_in_action and total_capital <= self.initial_capital:
                    order_including_asset = list(orders)
                    order_including_asset.append(order)
                    orders_list.append((order_including_asset, total_capital))
            buy_slice += 1
            capital_needed += capital_jump
        return orders_list

    def gen_orders_rec_old(self, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        buy_percent = self.buy_share_portion_jump
        orders_to_add = self.gen_orders_rec(assets[1:])
        orders_list.extend(orders_to_add)
        capital_jump = self.buy_share_portion_jump * asset.price * asset.daily_volume
        capital_needed = capital_jump
        while buy_percent <= 1 and capital_needed <= self.initial_capital:
            shares_to_buy = int(buy_percent * asset.daily_volume)
            order = Buy(asset.symbol, shares_to_buy, asset.price)
            orders_list.append(([order], capital_needed))
            for tup in orders_to_add:
                orders = tup[0]
                orders_capital = tup[1]
                total_capital = capital_needed + orders_capital
                if len(orders) < self.max_assets_in_action and total_capital <= self.initial_capital:
                    order_including_asset = list(orders)
                    order_including_asset.append(order)
                    orders_list.append((order_including_asset, total_capital))
            buy_percent += self.buy_share_portion_jump
            capital_needed += capital_jump
        return orders_list


class RobustDefender(Defender):
    def game_reward(self, funds: Dict[str, Fund],  history=None):
        reward = 0
        for fund in funds.values():
            if fund.is_liquidated():
                reward -= 1
        return reward

    def __repr__(self):
        return 'Robust Defender'


class OracleDefender(Defender):
    def __init__(self, initial_capital, asset_slicing, max_assets_in_action, goals):
        super().__init__(initial_capital, asset_slicing, max_assets_in_action)
        self.goals = goals

    def game_reward(self, funds: Dict[str, Fund],  history=None):
        for fund in self.goals:
            if not funds[fund].is_liquidated():
                return 1
        return -1

    def __repr__(self):
        return 'Oracle Defender'

class NNDefender(Defender):
    def __init__(self, initial_capital, asset_slicing, max_assets_in_action, neural_network):
        super().__init__(initial_capital, asset_slicing, max_assets_in_action)
        self.neural_network = neural_network

    def game_reward(self, funds: Dict[str, Fund], history):
        reward = 0
        for fund in funds:
            if funds[fund].is_liquidated():
                reward -= self.neural_network.predict(fund.symbol, history)
        return reward

"""

    def gen_orders(self, assets: Dict[str, Asset] = None):
        orders_lists = []
        for sym, asset in assets.items():
            buy_percent = self.buy_share_portion_jump
            capital_needed = buy_percent * asset.price * asset.daily_volume
            orders = []
            while buy_percent <= 1 and capital_needed <= self.capital:
                orders.append(Buy(sym, int(buy_percent * asset.daily_volume), asset.price))
                buy_percent += self.buy_share_portion_jump
                capital_needed = buy_percent * asset.price * asset.daily_volume
            if orders:
                orders_lists.append(orders)
        return orders_lists

   def gen_orders(self, assets: Dict[str, Asset]):
        orders_lists = []
        'TODO: make sure we dont get to ver small numbers'
        for asset_symbol, num_shares in self.portfolio.items():
            orders = []
            sell_percent = self.sell_share_portion_jump
            while sell_percent <= 1:
                orders.append(Sell(asset_symbol, int(sell_percent * num_shares), assets[asset_symbol].price))
                sell_percent += self.sell_share_portion_jump
            if orders:
                orders_lists.append(orders)
        return orders_lists
        
    def gen_orders_rec(self, money_left, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        buy_percent = self.buy_share_portion_jump
        capital_jump = self.buy_share_portion_jump * asset.price * asset.daily_volume
        capital_needed = capital_jump
        'orders without current asset'
        if len(assets) > 1:
            orders_list.extend(self.gen_orders_rec(money_left, assets[1:]))
        while buy_percent <= 1 and capital_needed <= money_left:
            shares_to_buy = int(buy_percent * asset.daily_volume)
            order = Buy(asset.symbol, shares_to_buy, asset.price)
            orders_list.append([order])
            'orders that include current asset'
            orders_to_add = self.gen_orders_rec(money_left - capital_needed, assets[1:])
            for orders in orders_to_add:
                if len(orders) < self.max_assets_in_action:
                    orders.append(order)
            if orders_to_add:
                orders_list.extend(orders_to_add)
            buy_percent += self.buy_share_portion_jump
            capital_needed += capital_jump
        return orders_list
        
        
    def gen_orders_rec(self, money_left, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        buy_percent = self.buy_share_portion_jump
        capital_jump = self.buy_share_portion_jump * asset.price * asset.daily_volume
        capital_needed = capital_jump
        'orders without current asset'
        if len(assets) > 1:
            orders_list.extend(self.gen_orders_rec(money_left, assets[1:]))
        while buy_percent <= 1 and capital_needed <= money_left:
            shares_to_buy = int(buy_percent * asset.daily_volume)
            order = Buy(asset.symbol, shares_to_buy, asset.price)
            orders_list.append(([order], capital_needed))
            orders_to_add = self.gen_orders_rec(money_left - capital_needed, assets[1:])
            for tup in orders_to_add:
                orders = tup[0]
                orders_capital = tup[1]
                total_capital = capital_needed + orders_capital
                if len(orders) < self.max_assets_in_action and total_capital <= self.capital:
                    orders.append(order)
                    orders_list.append((new_orders, total_capital))
            buy_percent += self.buy_share_portion_jump
            capital_needed += capital_jump
        return orders_list

"""

