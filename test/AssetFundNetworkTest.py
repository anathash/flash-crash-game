import unittest

import jsonpickle
import networkx as nx
from networkx.algorithms import bipartite

from Actions import Sell, Action, Buy
from AssetFundNetwork import Asset, Fund, AssetFundsNetwork
from MarketImpactCalculator import ExponentialMarketImpactCalculator


class TestAsset  (unittest.TestCase):
    def test_set_price(self):
        asset = Asset(2, 2, 'a1')
        asset.set_price(3)
        self.assertEqual(3, asset.price)


class TestFund  (unittest.TestCase):

    def test_gen_liquidation_orders(self):
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        expected_orders = [Sell('XXX', 10, None), Sell('YYY', 10, None)]
        actual_orders = fund.gen_liquidation_orders()
        self.assertEqual(expected_orders, actual_orders)

    def test_liquidate(self):
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        self.assertTrue(fund.portfolio)
        fund.liquidate()
        self.assertFalse(fund.portfolio)

    def test_is_liquidated(self):
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        self.assertFalse(fund.is_liquidated())
        fund.liquidate()
        self.assertFalse(fund.portfolio)

    def test_compute_portfolio_value(self):
        assets = {'XXX': Asset(1, 20, 'XXX'), 'YYY': Asset(4, 20, 'yyy')}
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        self.assertEqual(50, fund.compute_portfolio_value(assets))

    def test_compute_compute_curr_leverage(self):
        assets = {'XXX': Asset(1, 20, 'XXX'), 'YYY': Asset(4, 20, 'yyy')}
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        self.assertEqual(9, fund.compute_curr_leverage(assets))

    def test_marginal_call_false(self):
        assets = {'XXX': Asset(1, 20, 'XXX'), 'YYY': Asset(4, 20, 'yyy')}
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        self.assertFalse(False, fund.marginal_call(assets))

    def test_marginal_call_true(self):
        assets = {'XXX': Asset(1, 20, 'XXX'), 'YYY': Asset(1, 20, 'yyy')}
        fund = Fund('F1', {'XXX': 10, 'YYY': 10}, 5, 2, 3)
        self.assertTrue(True, fund.marginal_call(assets))


class TestFlashCrashGameBoard  (unittest.TestCase):

    def test_nx(self):
        network = AssetFundsNetwork.generate_random_network(0.5, 3, 2, [1]*3, [2]*3, [1]*2, [2]*3, [1]*3,
                                                            ExponentialMarketImpactCalculator(1))
        network.save_to_file('encoding_decoding_test.json')
        decoded_network = AssetFundsNetwork.load_from_file('x', ExponentialMarketImpactCalculator(1))
        funds_decoded = str(jsonpickle.encode(decoded_network.funds))
        asset_decoded = str(jsonpickle.encode(decoded_network.assets))
        print(funds_decoded)
        'a = AssetFundsNetwork( 3, 2, 0.5, [1]*3, [2]*3, [1]*2, [2]*3, [1]*3, ExponentialMarketImpactCalculator(1))'
"""
    def test_load_from_file(self):
        AssetFundsNetwork.from_file('a.txt.npy', [1] * 3, [0.5] * 4, [1] * 4, ExponentialMarketImpactCalculator(1))

    def test_pply_action_no_lliquidation(self):
        a = [[1, 1], [1, 1], [1, 1]]
        network = AssetFundsNetwork(a, 3, 2, [1]*3, [2]*3, [1]*2, [2]*3, [1]*3, ExponentialMarketImpactCalculator(1))
        a = Action([Sell('a1',10,10), Buy('a2',10,10)])
        network.apply_action(a)
"""


if __name__ == '__main__':
    unittest.main()
