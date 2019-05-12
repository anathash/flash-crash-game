import unittest

from GameLogic.Asset import Asset
from GameLogic.Market import Market
from GameLogic.Orders import Sell, Buy, Order
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator, MarketImpactCalculator


class MockMarketImpactTestCalculator(MarketImpactCalculator):
    def get_updated_price(self, num_shares, asset):
        return asset.price * (1 + num_shares / 10)

class MarketTest  (unittest.TestCase):

    def test_submit_sell_orders(self):
        assets = {'XXX': Asset(1, 20, 1.5, 'XXX'), 'YYY': Asset(1, 20, 1.5, 'yyy')}
        market = Market(MockMarketImpactTestCalculator(), 1, 0.1, assets)
        market.submit_sell_orders([Sell('XXX', 1, 1)])
        self.assertEqual(market.sell_orders_log, {'XXX': 1, 'YYY': 0})

        market.submit_sell_orders([Sell('XXX', 1, 1), Sell('YYY', 1, 1)])
        self.assertEqual(market.sell_orders_log, {'XXX': 2, 'YYY': 1})

        #self.assertEqual(market.orders, set(['XXX', 'YYY']))

    def test_submit_buy_to_sell_raise_exception(self):
        assets = {'XXX': Asset(1, 20, 1.5, 'XXX'), 'YYY': Asset(1, 20, 1.5, 'yyy')}
        market = Market(MockMarketImpactTestCalculator(), 1, 0.1, assets)
        self.assertRaises(TypeError, market.submit_sell_orders, [Buy('XXX', 1, 1)])

    def test_submit_sell_to_buy_raise_exception(self):
        assets = {'XXX': Asset(1, 20, 1.5, 'XXX'), 'YYY': Asset(1, 20, 1.5, 'yyy')}
        market = Market(MockMarketImpactTestCalculator(), 1, 0.1, assets)
        self.assertRaises(TypeError, market.submit_buy_orders, [Sell('XXX', 1, 1)])

    def test_submit_buy_orders(self):
        assets = {'XXX': Asset(1, 20, 1.5, 'XXX'), 'YYY': Asset(1, 20, 1.5, 'yyy')}
        market = Market(MockMarketImpactTestCalculator(), 1, 0.1, assets)
        market.submit_buy_orders([Buy('XXX', 1, 1)])
        self.assertEqual(market.buy_orders_log, {'XXX': 1, 'YYY': 0})

        market.submit_buy_orders([Buy('XXX', 1, 1), Buy('YYY', 1, 1)])
        #self.assertEqual(market.orders, set(['XXX', 'YYY']))
        self.assertEqual(market.buy_orders_log, {'XXX': 2, 'YYY': 1})

    def test_apply_action_price_increase_asym_only(self):
        xxx = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='XXX')
        assets = {'XXX': xxx}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_buy_orders([Buy('XXX', 10, 100)])
        market.apply_actions()
        self.assertEqual(xxx.price, 150)
        self.assertEqual(market.buy_orders_log['XXX'], 5)
        self.assertEqual(market.sell_orders_log['XXX'], 0)
        self.assertEqual(market.minute_counter, 0.5)
        self.assertEqual(market.minute_volume_counter['XXX'], 5)
        self.assertEqual(xxx.avg_minute_volume, 10)

    def test_apply_action_price_increase_sym_only(self):
        yyy = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='YYY')
        assets = {'YYY': yyy}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_buy_orders([Buy('YYY', 20, 100)])
        market.submit_sell_orders([Sell('YYY', 10, 100)])
        market.apply_actions()
        self.assertEqual(yyy.price, 150)
        self.assertEqual(market.buy_orders_log['YYY'], 5)
        self.assertEqual(market.sell_orders_log['YYY'], 0)
        self.assertEqual(market.minute_counter, 0.5)
        self.assertEqual(market.minute_volume_counter['YYY'], 15)
        self.assertEqual(yyy.avg_minute_volume, 10)

    def test_apply_action_price_decreases_asym_only(self):
        zzz = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='XXX')
        assets = {'ZZZ': zzz}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_sell_orders([Sell('ZZZ', 10, 100)])
        market.apply_actions()
        self.assertEqual(zzz.price, 50)
        self.assertEqual(market.sell_orders_log['ZZZ'], 5)
        self.assertEqual(market.buy_orders_log['ZZZ'], 0)
        self.assertEqual(market.minute_counter, 0.5)
        self.assertEqual(market.minute_volume_counter['ZZZ'], 5)
        self.assertEqual(zzz.avg_minute_volume, 10)

    def test_apply_action_price_decreases_sym_only(self):
        www = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='WWW')
        assets = {'WWW': www}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_buy_orders([Buy('WWW', 10, 100)])
        market.submit_sell_orders([Sell('WWW', 20, 100)])
        market.apply_actions()
        self.assertEqual(www.price, 50)
        self.assertEqual(market.sell_orders_log['WWW'], 5)
        self.assertEqual(market.buy_orders_log['WWW'], 0)
        self.assertEqual(market.minute_counter, 0.5)
        self.assertEqual(market.minute_volume_counter['WWW'], 15)
        self.assertEqual(www.avg_minute_volume, 10)

    def test_apply_action_price_remains_the_same(self):
        vvv = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='VVV')
        assets = {'VVV': vvv}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_buy_orders([Buy('VVV', 10, 100)])
        market.submit_sell_orders([Sell('VVV', 10, 100)])
        market.apply_actions()
        self.assertEqual(vvv.price, 100)
        self.assertEqual(market.sell_orders_log['VVV'], 0)
        self.assertEqual(market.buy_orders_log['VVV'], 0)
        self.assertEqual(market.minute_counter, 0.5)
        self.assertEqual(market.minute_volume_counter['VVV'], 10)
        self.assertEqual(vvv.avg_minute_volume, 10)

    def test_apply_action(self):
        xxx = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='XXX')
        yyy = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='YYY')
        zzz = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='ZZZ')
        www = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='WWW')
        vvv = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='VVV')
        assets = {'VVV': vvv,'WWW': www, 'XXX': xxx, 'YYY': yyy, 'ZZZ': zzz}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_buy_orders([Buy('XXX', 10, 100), Buy('YYY', 20, 100),
                                   Buy('VVV', 10, 100), Buy('WWW', 10, 100)])
        market.submit_sell_orders([Sell('YYY', 10, 100), Sell('ZZZ', 10, 100),
                                  Sell('VVV', 10, 100), Sell('WWW', 20, 100)])
        market.apply_actions()
        self.assertEqual(xxx.price, 150)
        self.assertEqual(yyy.price, 150)
        self.assertEqual(zzz.price, 50)
        self.assertEqual(www.price, 50)
        self.assertEqual(vvv.price, 100)
        self.assertEqual(market.sell_orders_log, {'XXX':0, 'YYY':0, 'ZZZ': 5, 'WWW': 5,'VVV': 0})
        self.assertEqual(market.buy_orders_log, {'XXX':5, 'YYY':5, 'ZZZ': 0, 'WWW': 0,'VVV': 0})
        self.assertEqual(market.minute_counter, 0.5)
        self.assertEqual(market.minute_volume_counter, {'XXX': 5, 'YYY': 15, 'ZZZ': 5, 'WWW': 15, 'VVV': 10})
        self.assertEqual(xxx.price, 150)
        self.assertEqual(yyy.avg_minute_volume, 10)
        self.assertEqual(zzz.avg_minute_volume, 10)
        self.assertEqual(vvv.avg_minute_volume, 10)
        self.assertEqual(www.avg_minute_volume, 10)

    def test_time_ticks(self):
        xxx = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='XXX')
        yyy = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='YYY')
        zzz = Asset(price=100, daily_volume=3900, volatility=1.5, symbol='ZZZ')
        assets = {'XXX': xxx, 'YYY': yyy, 'ZZZ': zzz}
        market = Market(MockMarketImpactTestCalculator(), 0.5, 0.5, assets)
        market.submit_buy_orders([Buy('XXX', 10, 100), Buy('YYY', 10, 100)])
        market.submit_sell_orders([Sell('XXX', 10, 100), Sell('YYY', 20, 100)])
        market.apply_actions()
        market.submit_buy_orders([Buy('XXX', 20, 100), Buy('YYY', 20, 100)])
        market.submit_sell_orders([Sell('XXX', 10, 100), Sell('YYY', 20, 100)])
        market.apply_actions()
        self.assertEqual(xxx.price, 150)
        self.assertEqual(yyy.price, 25)
        self.assertEqual(zzz.price, 100)
        self.assertEqual(market.sell_orders_log, {'XXX': 0, 'YYY': 0, 'ZZZ': 0})
        self.assertEqual(market.buy_orders_log, {'XXX': 5, 'YYY': 0, 'ZZZ': 0})
        self.assertEqual(market.minute_counter, 0)
        self.assertEqual(xxx.avg_minute_volume, 22.5)
        self.assertEqual(yyy.avg_minute_volume, 30)
        self.assertEqual(zzz.avg_minute_volume, 10)
        self.assertEqual(market.minute_volume_counter, {'XXX': 0, 'YYY': 0, 'ZZZ': 0})



#unchnged but stayes in quue
#removed from queue
#update minute volume