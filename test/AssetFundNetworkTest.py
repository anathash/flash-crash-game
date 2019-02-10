import unittest

import networkx as nx
import numpy as np

from GameLogic.Orders import Sell, Buy, Order
from GameLogic.AssetFundNetwork import Asset, Fund, AssetFundsNetwork
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator, MarketImpactCalculator


class MockMarketImpactTestCalculator(MarketImpactCalculator):
    def get_market_impact(self, order: Order, asset_total_shares):
        sign = -1 if isinstance(order, Sell) else 1
        if sign > 0:
            return asset_total_shares/order.num_shares
        else:
            return order.num_shares/asset_total_shares


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


class TestAssetFundsNetwork  (unittest.TestCase):

    def test_encode_decode_network(self):
        network = AssetFundsNetwork.generate_random_network(0.5, 3, 2, [1]*3, [2]*3, [1]*2, [2]*3, [1]*3,
                                                            ExponentialMarketImpactCalculator(1))
        network.save_to_file('encoding_decoding_test.json')
        decoded_network = AssetFundsNetwork.load_from_file('encoding_decoding_test.json',
                                                           ExponentialMarketImpactCalculator(1))
        self.assertEqual(network, decoded_network)

    def test_generate_random_network(self):
        num_funds = 3
        num_assets = 2

        assets_num_shares = [3, 4]
        initial_prices = [1, 2]

        initial_capitals = [100, 200, 300]
        initial_leverages = [1, 2, 3]
        tolerances = [4, 5, 6]

        g = AssetFundsNetwork.generate_random_network(0.5, num_funds, num_assets,initial_capitals,
                                                      initial_leverages, initial_prices,
                                                      tolerances, assets_num_shares, ExponentialMarketImpactCalculator(1))
        assets = g.assets
        funds = g.funds
        self.assertEqual(len(assets), num_assets)
        self.assertEqual(len(funds), num_funds)
        for i in range(len(assets)):
            asset = assets['a' + str(i)]
            self.assertEqual(initial_prices[i], asset.price)
            self.assertEqual(assets_num_shares[i], asset.total_shares)
        for i in range(len(funds)):
            fund = funds['f' + str(i)]
            self.assertEqual(initial_capitals[i], fund.capital)
            self.assertEqual(initial_leverages[i], fund.initial_leverage)
            self.assertEqual(tolerances[i], fund.tolerance)

    def test_generate_network_from_graph(self):
        num_funds = 2
        num_assets = 2
        assets_num_shares = [3, 4]
        initial_prices = [1, 2]
        initial_capitals = [100, 200]
        initial_leverages = [1, 2]
        tolerances = [4, 5]
        investment_proportions = {'f0': [0.6, 0.4], 'f1': [1.0]}
        g = nx.DiGraph()
        g.add_nodes_from([0, 1, 2, 3])
        g.add_edges_from([(0, 2), (0, 3), (1, 3)])
        network = AssetFundsNetwork.gen_network_from_graph(g, investment_proportions, initial_capitals,
                                                           initial_leverages, initial_prices,
                                                           tolerances, assets_num_shares,
                                                           ExponentialMarketImpactCalculator(1))
        assets = network.assets
        funds = network.funds
        self.assertEqual(len(assets), num_assets)
        self.assertEqual(len(funds), num_funds)
        for i in range(len(assets)):
            asset = assets['a' + str(i)]
            self.assertEqual(initial_prices[i], asset.price)
            self.assertEqual(assets_num_shares[i], asset.total_shares)
        for i in range(len(funds)):
            fund = funds['f' + str(i)]
            self.assertEqual(initial_capitals[i], fund.capital)
            self.assertEqual(initial_leverages[i], fund.initial_leverage)
            self.assertEqual(tolerances[i], fund.tolerance)
        prot0 = funds['f0'].portfolio
        self.assertEqual(len(prot0.items()), 2)
        self.assertEqual(prot0['a0'], 120)
        self.assertEqual(prot0['a1'], 40)

        prot1 = funds['f1'].portfolio
        self.assertEqual(len(prot1.items()), 1)
        self.assertEqual(prot1['a1'], 300)
        self.assertTrue('a0' not in prot1)

    def test_apply_action_no_liquidation(self):
        a0 = Asset(price=2, total_shares=40, symbol='a0')
        a1 = Asset(price=2, total_shares=40, symbol='a1')
        f0 = Fund('f0', {'a0': 10, 'a1': 10}, 5, 2, 3)
        f1 = Fund('f1', {'a0': 10, 'a1': 10}, 5, 2, 3)
        f2 = Fund('f2', {'a0': 10, 'a1': 10}, 5, 2, 3)
        network = AssetFundsNetwork({'f0': f0, 'f1': f1,'f2': f2}, {'a0': a0, 'a1': a1},
                                    MockMarketImpactTestCalculator())
        a = [Sell('a0', num_shares=20, share_price=2), Buy('a1', num_shares=10, share_price=2)]
        network.apply_action(a)

        expected_a0 = Asset(price=1.0, total_shares=40, symbol='a0')
        expected_a1 = Asset(price=8.0, total_shares=40, symbol='a1')
        expected_network = AssetFundsNetwork({'f0': f0, 'f1': f1, 'f2': f2}, {'a0': expected_a0, 'a1': expected_a1},
                                             MockMarketImpactTestCalculator())

        self.assertEqual(network, expected_network)

    def test_apply_action_with_liquidation(self):
        a0 = Asset(price=1, total_shares=40, symbol='a0')
        a1 = Asset(price=2, total_shares=40, symbol='a1')
        f0 = Fund('f0', {'a0': 10}, initial_capital=2, initial_leverage=8, tolerance=2)
        f1 = Fund('f1', {'a0': 10, 'a1': 1}, initial_capital=1, initial_leverage=1, tolerance=3)
        network = AssetFundsNetwork({'f0': f0, 'f1': f1}, {'a0': a0, 'a1': a1},
                                    MockMarketImpactTestCalculator())
        a = [Sell('a0', num_shares=10, share_price=2), Buy('a1', num_shares=10, share_price=2)]
        network.apply_action(a)

        expected_a0 = Asset(price=0.0625, total_shares=40, symbol='a0')
        expected_a1 = Asset(price=8.0, total_shares=40, symbol='a1')
        expected_f0 = Fund('f0', {}, initial_capital=2, initial_leverage=8, tolerance=2)
        expected_network = AssetFundsNetwork({'f0': expected_f0, 'f1': f1}, {'a0': expected_a0, 'a1': expected_a1},
                                             MockMarketImpactTestCalculator())

        self.assertEqual(network, expected_network)

    def test_get_canonical_form(self):
        a0 = Asset(price=1, total_shares=40, symbol='a0')
        a1 = Asset(price=2, total_shares=40, symbol='a1')
        f0 = Fund('f0', {'a0': 10}, initial_capital=2, initial_leverage=8, tolerance=2)
        f1 = Fund('f1', {'a0': 10, 'a1': 10}, initial_capital=1, initial_leverage=1, tolerance=3)
        network = AssetFundsNetwork({'f0': f0, 'f1': f1}, {'a0': a0, 'a1': a1},
                                    MockMarketImpactTestCalculator())
        expected_canonical_form = np.array([[10., 0.], [10., 20.]])
        actual_canonical_form = network.get_canonical_form()
        self.assertTrue(np.array_equal(expected_canonical_form, actual_canonical_form))



if __name__ == '__main__':
    unittest.main()
