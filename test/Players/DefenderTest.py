import unittest
from typing import Dict


from GameLogic.Players.Defender import RobustDefender, OracleDefender
from GameLogic.SysConfig import SysConfig
from GameLogic.Orders import Sell, Buy
from GameLogic.AssetFundNetwork import Fund, Asset
from Players.PlayersTest import to_string_list


class RobustDefenderTest  (unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        SysConfig.set(SysConfig.MIN_ORDER_VALUE, 0.5)

    def test_no_actions_below_min(self):
        SysConfig.set(SysConfig.MIN_ORDER_VALUE, 100)
        defender = RobustDefender(200, 2, 2)
        actual_orders = defender.get_valid_actions({'a1': Asset(2, 60, 1.5, 'a1')})
        expected_orders = [[Buy('a1', 60, 2)]]
        e = to_string_list(expected_orders)
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_resources_exhusted_false_when_capital_exists(self):
        defender = RobustDefender(200, 2, 2)
        self.assertFalse(defender.resources_exhusted())

    def test_resources_exhusted_true_when_no_capital(self):
        defender = RobustDefender(0, 2, 2)
        self.assertTrue(defender.resources_exhusted())

    def test_set_resources_exhusted_when_no_valid_actions(self):
        defender = RobustDefender(10, 2, 2)
        orders = defender.get_valid_actions({'a1': Asset(600, 200, 1.5, 'a1'), 'a2': Asset(600, 300, 1.5, 'a2')})
        self.assertFalse(orders)
        self.assertTrue(defender.resources_exhusted())

    def test_game_reward_robust_defender(self):
        defender = RobustDefender(200, 2, 2)
        f1 = Fund('f1', {}, 200, 2, 2, )
        f1.is_liquidating = True
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertEqual(defender.game_reward({'f1': f1, 'f2': f2}), -1)

    def test_game_reward_oracle_defender(self):
        defender = OracleDefender(200, 2, 2, ['f1', 'f2'])
        f1 = Fund('f1', {}, 200, 2, 2, )
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertEqual(defender.game_reward({'f1': f1, 'f2': f2}), 1)

    def test_apply_action(self):
        defender = RobustDefender(400, 2, 2)
        orders = [Buy('a1', 100, 2), Buy('a2', 100, 2)]
        defender.apply_action(orders)
        self.assertEqual(defender.portfolio['a1'], 100)
        self.assertEqual(defender.portfolio['a2'], 100)
        self.assertEqual(defender.initial_capital, 0)
        self.assertEqual(len(defender.portfolio.items()), 2)

    def test_apply_illegal_action(self):
        defender = RobustDefender(400, 0.5, 2)
        orders = [Buy('a1', 100, 2), Sell('a2', 100, 2)]
        with self.assertRaises(ValueError):
            defender.apply_action(orders)

    def test_get_valid_actions(self):
        defender = RobustDefender(500, 2, 2)
        expected_orders = \
            [[Buy('a1', 100, 2)], [Buy('a1', 200, 2)], [Buy('a2', 150, 2)], [Buy('a1', 100, 2), Buy('a2', 150, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = defender.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions_single_asset(self):
        defender = RobustDefender(500, 2, 1)
        expected_orders = \
            [[Buy('a1', 100, 2)], [Buy('a1', 200, 2)], [Buy('a2', 150, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = defender.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions_max_assets(self):
        defender = RobustDefender(500, 2, 1)
        expected_orders = \
            [[Buy('a1', 100, 2)], [Buy('a1', 200, 2)], [Buy('a2', 150, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = defender.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5,'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)

    def test_get_valid_actions2(self):
        defender = RobustDefender(500, 2, 2)
        expected_orders = \
            [[Buy('a1', 100, 2)], [Buy('a1', 200, 2)], [Buy('a2', 150, 2)],
             [Buy('a3', 50, 2)], [Buy('a3', 100, 2)],
             [Buy('a1', 100, 2), Buy('a3', 50, 2)],
             [Buy('a1', 100, 2), Buy('a3', 100, 2)],
             [Buy('a1', 100, 2), Buy('a2', 150, 2)],
             [Buy('a1', 200, 2), Buy('a3', 50, 2)],
             [Buy('a2', 150, 2), Buy('a3', 50, 2)],
             [Buy('a2', 150, 2), Buy('a3', 100, 2)]]

        e = to_string_list(expected_orders)
        actual_orders = defender.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2'),
                                                    'a3': Asset(2, 100, 1.5, 'a3')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)


    def test_get_valid_actions2_single_asset(self):
        defender = RobustDefender(500, 2, 1)
        expected_orders = \
            [[Buy('a1', 100, 2)], [Buy('a1', 200, 2)], [Buy('a2', 150, 2)],
             [Buy('a3', 50, 2)], [Buy('a3', 100, 2)]]

        e = to_string_list(expected_orders)
        actual_orders = defender.get_valid_actions({'a1': Asset(2, 200, 1.5, 'a1'), 'a2': Asset(2, 300, 1.5, 'a2'),
                                                    'a3': Asset(2, 100, 1.5, 'a3')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)


    def test_gen_random_action(self):
        assets = {'a1': Asset(2, 500, 1.5, 'a1'), 'a2': Asset(2, 500, 1.5, 'a2'), 'a3': Asset(2, 500, 1.5, 'a3')}
        defender = RobustDefender(500, 2, 2)
        for i in range(100):
            orders = defender.gen_random_action(assets)
            required_capital = 0
            for order in orders:
                self.assert_valid_order(defender, order, assets)
                required_capital += order.num_shares * order.share_price
            self.assertTrue(required_capital <= defender.initial_capital)

        defender = RobustDefender(500, 2, 1)
        for i in range(100):
            orders = defender.gen_random_action(assets)
            required_capital = 0
            for order in orders:
                self.assert_valid_order(defender, order, assets)
                required_capital += order.num_shares * order.share_price
            self.assertTrue(required_capital <= defender.initial_capital)

    def assert_valid_order(self, defender: RobustDefender, buy: Buy, assets: Dict[str, Asset]):
        asset = assets[buy.asset_symbol]
        self.assertEqual(buy.share_price, asset.price)
        self.assertTrue(buy.num_shares <= asset.daily_volume)
        self.assertTrue(buy.num_shares * buy.share_price <= defender.initial_capital)

