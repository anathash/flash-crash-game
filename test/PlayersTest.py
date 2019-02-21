import unittest
from typing import Dict

from numpy import sort

from GameLogic.SysConfig import SysConfig
from GameLogic.Orders import Sell, Buy
from GameLogic.AssetFundNetwork import Fund, Asset
from GameLogic.Players import Attacker, RobustDefender, OracleDefender


def to_string_list(orders):
    l = []
    for item in orders:
        l.append(list(sort(list(map(lambda x: str(x), item)))))
    l.sort(key=lambda x: (len(x), x[0]))
    return l


class AttackerTest  (unittest.TestCase):

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

    def assert_valid_order(self, attacker: Attacker, sell: Sell, assets: Dict[str, Asset]):
        asset = assets[sell.asset_symbol]
        self.assertEqual(sell.share_price, asset.price)
        self.assertTrue(sell.num_shares <= attacker.portfolio[sell.asset_symbol])

"""
   def test_gen_orders(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 0.5, 2)
        expected_orders = [[Sell('a1', 150, 2), Sell('a1', 300, 2)],
                           [Sell('a2', 200, 2), Sell('a2', 400, 2)]]
        actual_orders = attacker.gen_orders({'a1': Asset(2, 200, 'a1'), 'a2': Asset(2, 300, 'a2')})
        for i in range(2):
            self.assertListEqual(expected_orders[i], actual_orders[i])


"""


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

    def test_gen_random_action(self):
        assets = {'a1': Asset(2, 500, 1.5, 'a1'), 'a2': Asset(2, 500, 1.5, 'a2'), 'a3': Asset(2, 500, 1.5, 'a3')}
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


"""
   def test_gen_orders(self):
        defender = RobustDefender(400, 2, 2)
        expected_orders = [[Buy('a1', 100, 2), Buy('a1', 200, 2)], [Buy('a2', 150, 2)]]
        actual_orders = defender.gen_orders({'a1': Asset(2, 200, 'a1'), 'a2': Asset(2, 300, 'a2')})
        for i in range(2):
            self.assertListEqual(expected_orders[i], actual_orders[i])
"""
if __name__ == '__main__':
    unittest.main()


