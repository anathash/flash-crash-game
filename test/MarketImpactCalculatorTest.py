import unittest
import numpy.testing as npt

from Actions import Buy, Sell
from MarketImpactCalculator import ExponentialMarketImpactCalculator


class TestFlashCrashGameBoard  (unittest.TestCase):

    def test_buy_oder(self):
        order = Buy('a1', 10)
        mi = ExponentialMarketImpactCalculator.get_market_impact(order, 100)
        npt.assert_almost_equal(1.1111, mi, decimal=4)

    def test_sell_oder(self):
        order = Sell('a1', 10)
        mi = ExponentialMarketImpactCalculator.get_market_impact(order, 100)
        npt.assert_almost_equal(0.9000, mi, decimal=4)


if __name__ == '__main__':
    unittest.main()
