
class Asset:
    def __init__(self, price, daily_volume, volatility, symbol):
        self.price = price
        self.daily_volume = daily_volume
        self.avg_minute_volume = daily_volume/(60*6.5)
        self.symbol = symbol
        self.volatility = volatility

    def set_price(self, new_price):
        self.price = new_price

    def __eq__(self, other):
        return isinstance(other, Asset) and self.price == other.price and self.daily_volume == other.daily_volume \
               and self.volatility == other.volatility and self.symbol == other.symbol
