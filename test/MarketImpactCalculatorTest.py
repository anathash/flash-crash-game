import unittest
import numpy.testing as npt

from Actions import Buy, Sell
from MarketImpactCalculator import ExponentialMarketImpactCalculator


class TestFlashCrashGameBoard  (unittest.TestCase):

    def test_buy_oder(self):
        calc = ExponentialMarketImpactCalculator(2)
        order = Buy('a1', 10)
        mi = calc.get_market_impact(order, 100)
        npt.assert_almost_equal(1.2214, mi, decimal=4)

    def test_sell_oder(self):
        calc = ExponentialMarketImpactCalculator(2)
        order = Sell('a1', 10)
        mi = calc.get_market_impact(order, 100)
        npt.assert_almost_equal(0.8187, mi, decimal=4)


if __name__ == '__main__':
    unittest.main()
