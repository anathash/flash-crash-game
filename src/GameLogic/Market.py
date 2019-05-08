from typing import Dict, List

from GameLogic.Asset import Asset
from GameLogic.MarketImpactCalculator import MarketImpactCalculator
from GameLogic.Orders import Buy, Sell, Order
from GameLogic.SysConfig import SysConfig


class Market:

    def __init__(self, mic:MarketImpactCalculator, timestep_minute, timestep_order_limit, assets: Dict[str, Asset]):
        self.buy_orders_log = {}
        self.sell_orders_log = {}
        self.orders = []
        self.mic = mic
        self.timestep_order_limit = timestep_order_limit
        self.timestep_seconds = timestep_minute
        self.minute_counter = 0
        self.avg_minute_volume = {}
        self.assets = assets
        for sym, asset in assets:
            self.minute_volume_counter[sym] = asset.avg_minute_volume

    def submit_sell_orders(self, orders:List[Sell]):
        self.submit_orders(orders, self.sell_orders_log)

    def submit_buy_orders(self, orders:List[Buy]):
        self.submit_orders(orders, self.buy_orders_log)

    @staticmethod
    def submit_orders(orders_log, orders: List[Order]):
        for order in orders:
            num_shares = orders_log[order.asset_symbol] if order.asset_symbol in orders_log else 0
            num_shares += order.num_shares
            orders_log[order.asset_symbol] = num_shares

    def apply_actions(self):
        self.minute_counter += self.timestep_seconds
        indexes_to_remove = []
        for i in len(self.orders):
            sym = self.orders[i]
            asset = self.assets[sym]
            buy = self.buy_orders[sym] if sym in self.buy_orders else 0
            sell = self.sell_orders[sym] if sym in self.sell_orders else 0
            limit = self.timestep_order_limit * asset.avg_minute_volume
            buys_per_timestep = min(buy, buy * limit)
            sells_per_timestep = min(sell, buy * limit)
            self.avg_minute_volume += max(buys_per_timestep, sells_per_timestep)
            num_shares = buys_per_timestep - sells_per_timestep
            new_price = self.mic.get_updated_price(num_shares, asset)
            asset.set_price(new_price)

            if self.minute_counter == 1:
                # curr minute average is the previous minutes average + this minutes distressed trades
                asset.avg_minute_volume = (asset.avg_minute_volume*2 + self. avg_minute_volume[sym])/2
            buy -= buys_per_timestep
            sell -= sells_per_timestep
            if buy == 0 and sell == 0:
                indexes_to_remove.append(i)
            else:
                self.buy_orders[sym] = buy
                self.sell_orders[sym] = sell
        for index_to_remove in indexes_to_remove:
            self.orders.pop(index_to_remove)

    def get_valid_buy_actions(self, assets: Dict[str, Asset] = None):
        if self.max_assets_in_action > 1:
            orders_list_tup = self.gen_buy_orders_rec(list(assets.values()))
            orders_list = [x[0] for x in orders_list_tup]
        else:
            orders_list = self.gen_single_asset_buy_orders(list(assets.values()))
        if not orders_list:
            self.resources_exhusted_flag = True
            return []
        return orders_list

    def gen_single_asset_buy_orders(self, assets: List[Asset]):
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

    def gen_buy_orders_rec(self, assets: List[Asset]):
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

    def gen_buy_orders_rec_old(self, assets: List[Asset]):
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


