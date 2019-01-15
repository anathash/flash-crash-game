from typing import List


class Order:
    def __init__(self, asset_symbol: str, num_shares: int, share_price: int):
        self.asset_symbol = asset_symbol
        self.num_shares = num_shares
        self.share_price = share_price

    def __eq__(self, other):
        return isinstance(other, Order) and \
               self.asset_symbol == other.asset_symbol and\
               self.num_shares == other.num_shares and \
               self.share_price == other.share_price


class Buy(Order):
    def __init__(self, asset_symbol: str, num_shares: int, share_price: int):
        super().__init__(asset_symbol, num_shares, share_price)

    def __repr__(self):
        return 'Buy ' + self.asset_symbol + ' ' + str(self.num_shares) + ' at ' + \
               str(self.share_price)


class Sell(Order):
    def __init__(self, asset_symbol: str, num_shares: int, share_price: int):
        super().__init__(asset_symbol, num_shares, share_price)

    def __repr__(self):
        return 'Sell ' + self.asset_symbol + ' ' + str(self.num_shares) \
               + ' at ' + str(self.share_price)


class Action:
    def __init__(self, orders: List[Order]):
        self.orders = orders
