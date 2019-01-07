import itertools
from typing import List, Dict

from Actions import Sell, Action, Order, Buy
from AssetFundNetwork import Asset, Fund


class Player:
    def __init__(self, initial_capital, initial_portfolio: Dict[str, int], max_assets_in_action):
        self.capital = initial_capital
        self.portfolio = initial_portfolio
        self.max_assets_in_action = max_assets_in_action

    def apply_action(self, action: Action):
        for order in action.orders:
            self.apply_order(order)

    def get_valid_actions(self, assets: Dict[str, Asset]):
        raise NotImplementedError

    def is_legal(self, orders: List[Order]):
        return True

    def gen_orders(self, assets: Dict[str, Asset]):
        raise NotImplementedError()

    def resources_exhusted(self):
        raise NotImplementedError()

    def apply_order(self, order: Action):
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
    def __init__(self, initial_portfolio: Dict[str, int], goals: List[str], sell_share_portion_jump, max_assets_in_action):
        super().__init__(0, initial_portfolio, max_assets_in_action)
        self.goals = goals
        self.sell_share_portion_jump = sell_share_portion_jump

    def resources_exhusted(self):
        return not self.portfolio

    def is_goal_achieved(self, funds: Dict[str, Fund]):
        for fund_symbol in self.goals:
            if not funds[fund_symbol].is_liquidated():
                return False
        return True

    def apply_order(self, order: Sell):
        if not isinstance(order, Sell):
            raise ValueError("attacker only sells")

        self.capital += order.share_price * order.num_shares
        num_shares = self.portfolio[order.asset_symbol]
        num_shares -= order.num_shares
        if num_shares == 0:
            del self.portfolio[order.asset_symbol]
        else:
            self.portfolio[order.asset_symbol] = num_shares

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

    def get_valid_actions(self, assets: Dict[str, Asset]):
        return self.gen_orders_rec(list(assets.values()))

    def gen_orders_rec(self, assets: List[Asset]):
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


class Defender(Player):
    def __init__(self, initial_capital, buy_share_portion_jump, max_assets_in_action):
        super().__init__(initial_capital, {}, max_assets_in_action)
        self.buy_share_portion_jump = buy_share_portion_jump
        return

    ' think: should we allow selling of assets when capital is zero?'
    def resources_exhusted(self):
        'allow overdraft?'
        return self.capital <= 0

        'TODO: make sure we dont get to very small numbers'

    def apply_order(self, order: Buy):
        if not isinstance(order, Buy):
            raise ValueError("attacker only buys")
        self.capital -= order.share_price * order.num_shares
        num_shares = self.portfolio[order.asset_symbol] if order.asset_symbol in self.portfolio else 0
        num_shares += order.num_shares
        self.portfolio[order.asset_symbol] = num_shares

    @staticmethod
    def game_reward(funds: List[Fund]):
        reward = 0
        for fund in funds:
            if fund.is_liquidated():
                reward -= 1
        return reward

    def is_legal(self, orders: List[Order]):
        capital_needed = 0
        for order in orders:
            capital_needed += order.share_price * order.num_shares
            if capital_needed > self.capital:
                return True
        return False

    def gen_orders(self, assets: Dict[str, Asset] = None):
        orders_lists = []
        for sym, asset in assets.items():
            buy_percent = self.buy_share_portion_jump
            capital_needed = buy_percent * asset.price * asset.total_shares
            orders = []
            while buy_percent <= 1 and capital_needed <= self.capital:
                orders.append(Buy(sym, int(buy_percent * asset.total_shares), asset.price))
                buy_percent += self.buy_share_portion_jump
                capital_needed = buy_percent * asset.price * asset.total_shares
            if orders:
                orders_lists.append(orders)
        return orders_lists

    def get_valid_actions(self, assets: Dict[str, Asset] = None):
        orders_list = self.gen_orders_rec(list(assets.values()))
        return [x[0] for x in orders_list]

    def gen_orders_rec(self, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        buy_percent = self.buy_share_portion_jump
        orders_to_add = self.gen_orders_rec(assets[1:])
        orders_list.extend(orders_to_add)
        capital_jump = self.buy_share_portion_jump * asset.price * asset.total_shares
        capital_needed = capital_jump
        while buy_percent <= 1 and capital_needed <= self.capital:
            shares_to_buy = int(buy_percent * asset.total_shares)
            order = Buy(asset.symbol, shares_to_buy, asset.price)
            orders_list.append(([order], capital_needed))
            for tup in orders_to_add:
                orders = tup[0]
                orders_capital = tup[1]
                total_capital = capital_needed + orders_capital
                if len(orders) < self.max_assets_in_action and total_capital <= self.capital:
                    order_including_asset = list(orders)
                    order_including_asset.append(order)
                    orders_list.append((order_including_asset, total_capital))
            buy_percent += self.buy_share_portion_jump
            capital_needed += capital_jump
        return orders_list

"""
    def gen_orders_rec(self, money_left, assets: List[Asset]):
        if not assets:
            return []
        orders_list = []
        asset = assets[0]
        buy_percent = self.buy_share_portion_jump
        capital_jump = self.buy_share_portion_jump * asset.price * asset.total_shares
        capital_needed = capital_jump
        'orders without current asset'
        if len(assets) > 1:
            orders_list.extend(self.gen_orders_rec(money_left, assets[1:]))
        while buy_percent <= 1 and capital_needed <= money_left:
            shares_to_buy = int(buy_percent * asset.total_shares)
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
        capital_jump = self.buy_share_portion_jump * asset.price * asset.total_shares
        capital_needed = capital_jump
        'orders without current asset'
        if len(assets) > 1:
            orders_list.extend(self.gen_orders_rec(money_left, assets[1:]))
        while buy_percent <= 1 and capital_needed <= money_left:
            shares_to_buy = int(buy_percent * asset.total_shares)
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

