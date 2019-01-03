from typing import List


class Order:
    def __init__(self, asset_symbol: str, num_shares: int):
        self.asset_symbol = asset_symbol
        self.num_shares = num_shares


class Buy(Order):
    def __init__(self, asset_symbol: str, num_shares: int):
        super().__init__(asset_symbol, num_shares)


class Sell(Order):
    def __init__(self, asset_symbol: str, num_shares: int):
        super().__init__(asset_symbol, num_shares)


class Action:
    def __init__(self, orders: List[Order]):
        self.orders = orders
