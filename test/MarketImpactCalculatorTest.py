import unittest
import numpy.testing as npt

from GameLogic.AssetFundNetwork import Asset
from GameLogic.Orders import Buy, Sell
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator, SqrtMarketImpactCalculator


class TestFlashCrashGameBoard  (unittest.TestCase):

    def test_buy_oder_exp(self):
        calc = ExponentialMarketImpactCalculator(2)
        order = Buy('a1', 10, 1)
        a = Asset(price=2, daily_volume=100, volatility=1.5, symbol='a1')
        mi = calc.get_market_impact(order, a)
        npt.assert_almost_equal(1.2214, mi, decimal=4)

    def test_sell_oder_exp(self):
        calc = ExponentialMarketImpactCalculator(2)
        a = Asset(price=2, daily_volume=100, volatility=1.5, symbol='a1')
        order = Sell('a1', 10, 1)
        mi = calc.get_market_impact(order, a)
        npt.assert_almost_equal(0.8187, mi, decimal=4)

    def test_buy_oder_sqrt(self):
        calc = SqrtMarketImpactCalculator(0.5)
        order = Buy('a1', 10, 1)
        a = Asset(price=2, daily_volume=1000, volatility=1.5, symbol='a1')
        mi = calc.get_market_impact(order, a)
        npt.assert_almost_equal(1.075, mi, decimal=4)

    def test_sell_oder_sqrt(self):
        calc = SqrtMarketImpactCalculator(0.5)
        a = Asset(price=2, daily_volume=1000, volatility=1.5, symbol='a1')
        order = Sell('a1', 10, 1)
        mi = calc.get_market_impact(order, a)
        npt.assert_almost_equal(0.925, mi, decimal=4)



if __name__ == '__main__':
    unittest.main()
