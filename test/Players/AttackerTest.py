import unittest
from typing import Dict

from numpy import sort

from GameLogic.Players.Attacker import Attacker
from GameLogic.SysConfig import SysConfig
from GameLogic.Orders import Sell, Buy
from GameLogic.AssetFundNetwork import Fund, Asset
from Players.PlayersTest import to_string_list


class AttackerTest (unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        SysConfig.set("MIN_ORDER_VALUE", 0.5)

    def test_resources_exhusted_false_when_portfolio_not_empty(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1'], 4, 2)
        self.assertFalse(attacker.resources_exhusted())

    def test_resources_exhusted_false_when_portfolio_empty(self):
        attacker = Attacker({}, ['f1'], 4, 2)
        self.assertTrue(attacker.resources_exhusted())

    def test_goal_achieved(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1'], 4, 2)
        f1 = Fund('f1', {}, 200, 2, 2, )
        f1.is_liquidating = True
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertTrue(attacker.is_goal_achieved({'f1': f1, 'f2': f2}))

    def test_goal_not_achieved(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 4, 2)
        f1 = Fund('f1', {}, 200, 2, 2, )
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertFalse(attacker.is_goal_achieved({'f1': f1, 'f2': f2}))

    def test_apply_action(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 2, 2)
        orders = [Sell('a1', 150, 2), Sell('a2', 200, 2)]
        attacker.apply_action(orders)
        self.assertEqual(attacker.portfolio['a1'], 150)
        self.assertEqual(attacker.portfolio['a2'], 200)
        self.assertEqual(attacker.initial_capital, 700)
        self.assertEqual(len(attacker.portfolio.items()), 2)

    def test_apply_illegal_action(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 2, 2)
        orders = [Buy('a1', 100, 2), Sell('a2', 100, 2)]
        with self.assertRaises(ValueError):
            attacker.apply_action(orders)

    def test_no_actions_below_min(self):
        SysConfig.set(SysConfig.MIN_ORDER_VALUE, 500)
        attacker = Attacker({'a1': 300}, ['f1', 'f2'], 2, 2)
        expected_orders = [[Sell('a1', 300, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions_single_asset(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 2, 1)
        expected_orders = \
            [[Sell('a1', 150, 2)], [Sell('a1', 300, 2)],
             [Sell('a2', 200, 2)], [Sell('a2', 400, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 2, 2)
        expected_orders = \
            [[Sell('a1', 150, 2)], [Sell('a1', 300, 2)],
             [Sell('a2', 200, 2)], [Sell('a2', 400, 2)],
             [Sell('a1', 150, 2), Sell('a2', 200, 2)],
             [Sell('a1', 150, 2), Sell('a2', 400, 2)],
             [Sell('a1', 300, 2), Sell('a2', 200, 2)],
             [Sell('a1', 300, 2), Sell('a2', 400, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions_max_assets(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 2, 1)
        expected_orders = \
            [[Sell('a1', 150, 2)], [Sell('a1', 300, 2)],
             [Sell('a2', 200, 2)], [Sell('a2', 400, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions_single_asset2(self):
        attacker = Attacker({'a1': 300, 'a2': 400, 'a3': 100}, ['f1', 'f2'], 2, 1)
        expected_orders = \
            [[Sell('a1', 150, 2)], [Sell('a1', 300, 2)],
             [Sell('a2', 200, 2)], [Sell('a2', 400, 2)],
             [Sell('a3', 50, 2)], [Sell('a3', 100, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_valid_actions({'a1': Asset(2, 500, 1.5, 'a1'), 'a2': Asset(2, 500, 1.5, 'a2'),
                                                    'a3': Asset(2, 500, 1.5, 'a3')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions2(self):
        attacker = Attacker({'a1': 300, 'a2': 400, 'a3': 100}, ['f1', 'f2'], 2, 2)
        expected_orders = \
            [[Sell('a1', 150, 2)], [Sell('a1', 300, 2)],
             [Sell('a2', 200, 2)], [Sell('a2', 400, 2)],
             [Sell('a3', 50, 2)], [Sell('a3', 100, 2)],
             [Sell('a1', 150, 2), Sell('a3', 50, 2)],
             [Sell('a1', 150, 2), Sell('a3', 100, 2)],
             [Sell('a1', 150, 2), Sell('a2', 200, 2)],
             [Sell('a1', 150, 2), Sell('a2', 400, 2)],
             [Sell('a1', 300, 2), Sell('a3', 50, 2)],
             [Sell('a1', 300, 2), Sell('a3', 100, 2)],
             [Sell('a1', 300, 2), Sell('a2', 200, 2)],
             [Sell('a1', 300, 2), Sell('a2', 400, 2)],
             [Sell('a2', 200, 2), Sell('a3', 50, 2)],
             [Sell('a2', 200, 2), Sell('a3', 100, 2)],
             [Sell('a2', 400, 2), Sell('a3', 50, 2)],
             [Sell('a2', 400, 2), Sell('a3', 100, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_valid_actions({'a1': Asset(2, 500, 1.5, 'a1'), 'a2': Asset(2, 500, 1.5, 'a2'),
                                                    'a3': Asset(2, 500, 1.5, 'a3')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_gen_random_action(self):
        assets = {'a1': Asset(2, 500, 1.5, 'a1'), 'a2': Asset(2, 500, 1.5, 'a2'), 'a3': Asset(2, 500, 1.5, 'a3')}
        attacker = Attacker({'a1': 300, 'a2': 400, 'a3': 100}, ['f1', 'f2'], 2, 2)
        for i in range(0, 100):
            orders = attacker.gen_random_action(assets)
            for order in orders:
                self.assert_valid_order(attacker, order, assets)

        attacker = Attacker({'a1': 300, 'a2': 400, 'a3': 100}, ['f1', 'f2'], 2, 1)
        for i in range(0, 100):
            orders = attacker.gen_random_action(assets)
            for order in orders:
                self.assert_valid_order(attacker, order, assets)

    def assert_valid_order(self, attacker: Attacker, sell: Sell, assets: Dict[str, Asset]):
        asset = assets[sell.asset_symbol]
        self.assertEqual(sell.share_price, asset.price)
        self.assertTrue(sell.num_shares <= attacker.portfolio[sell.asset_symbol])
