import itertools
from typing import List, Dict

from Actions import Sell, Action, Order, Buy
from Constants import SELL_SHARE_PORTION_JUMP, BUY_SHARE_PORTION_JUMP, MAX_ASSETS_IN_ACTION
from AssetFundNetwork import AssetFundsNetwork, Asset, Fund


class Player:
    def __init__(self, initial_capital, initial_portfolio: Dict[str, int]):
        self.capital = initial_capital
        self.portfolio = initial_portfolio

    def apply_buy_order(self, order: Buy, assets: Dict[str, Asset]):
        self.capital -= assets[order.asset_symbol] * order.num_shares
        num_shares = self.portfolio[order.asset_symbol] if self.portfolio[order.asset_symbol] else 0
        num_shares += order.num_shares
        self.portfolio[order.asset_symbol] = num_shares

    def apply_sell_order(self, order: Sell, assets: Dict[str, Asset]):
        self.capital += assets[order.asset_symbol] * order.num_shares
        num_shares = self.portfolio[order.asset_symbol]
        num_shares -= order.num_shares
        if num_shares == 0:
            del self.portfolio[order.asset_symbol]
        else:
            self.portfolio[order.asset_symbol] = num_shares

    def apply_action(self, action: Action, assets):
        for order in action.orders:
            if isinstance(order, Buy):
                self.apply_buy_order(order, assets)
            if isinstance(order, Sell):
                self.apply_sell_order(order, assets)

    def resources_exhusted(self):
        raise NotImplementedError()

    def get_valid_actions(self, assets):
        actions = []
        orders_lists = self.gen_orders(assets)
        selected_assets_comb = itertools.combinations(orders_lists, MAX_ASSETS_IN_ACTION)
        for comb in selected_assets_comb:
            orders = itertools.product(tuple(comb))
            self.append_action_if_legal(actions, orders)
            if self.is_legal(orders):
                actions.append(Action(orders))

    def is_legal(self, orders: List[Order]):
        return True


class Attacker(Player):
    def __init__(self, initial_portfolio, goals):
        super().__init__(0, initial_portfolio)
        self.goals = goals

    def resources_exhusted(self):
        return not self.portfolio

    def gen_orders(self, assets):
        orders_lists = []
        'TODO: make sure we dont get to ver small numbers'
        for asset_symbol, num_shares in self.portfolio:
            orders = []
            sell_percent = SELL_SHARE_PORTION_JUMP
            while sell_percent < 100:
                orders.append(Sell(asset_symbol, sell_percent * num_shares))
                sell_percent += SELL_SHARE_PORTION_JUMP
            orders_lists.append(orders)
        return orders

    def is_goal_achieved(self, funds: Dict[str,Fund]):
        for fund_symbol in self.goals:
            if not funds[fund_symbol].is_liquidated():
                return False
        return True


class Defender(Player):
    def __init__(self, initial_capital):
        super().__init__(initial_capital, [])
        return

    ' thisk: should we allow selling of assets when capital is zero?'
    def resources_exhusted(self):
        'allow overdraft?'
        return self.capital <= 0

        'TODO: make sure we dont get to very small numbers'
    def gen_orders(self, assets):
        orders = []
        for asset in assets:
            buy_percent = BUY_SHARE_PORTION_JUMP
            capital_needed = buy_percent * asset.price
            while buy_percent < 100 and capital_needed < self.capital:
                orders.append(Sell(buy_percent * asset.total_shares))
                buy_percent += BUY_SHARE_PORTION_JUMP
                capital_needed = buy_percent * asset.price

    def is_legal(self, orders: List[Order]):
        capital_needed = 0
        for order in orders:
            capital_needed += order.asset.price * order.num_shares
            if capital_needed > self.capital:
                return True
        return False

    @staticmethod
    def game_reward(network: AssetFundsNetwork):
        reward = 0
        for fund in network.funds:
            if fund.is_liquidated():
                reward -= 1
        return reward
