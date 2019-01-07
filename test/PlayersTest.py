import unittest

from numpy import sort

from Actions import Sell, Buy, Action
from AssetFundNetwork import Fund, Asset
from Players import Attacker, Defender


def to_string_list(orders):
    l = []
    for item in orders:
        l.append(list(sort(list(map(lambda x: str(x), item)))))
    l.sort(key=lambda x: (len(x), x[0]))
    return l


class AttackerTest  (unittest.TestCase):

    def test_resources_exhusted_false_when_portfolio_not_empty(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1'], 0.25, 2)
        self.assertFalse(attacker.resources_exhusted())

    def test_resources_exhusted_false_when_portfolio_empty(self):
        attacker = Attacker({}, ['f1'], 0.25, 2)
        self.assertTrue(attacker.resources_exhusted())

    def test_goal_achieved(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1'], 0.25, 2)
        f1 = Fund('f1', {}, 200, 2, 2, )
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertTrue(attacker.is_goal_achieved({'f1': f1, 'f2': f2}))

    def test_goal_not_achieved(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 0.25, 2)
        f1 = Fund('f1', {}, 200, 2, 2, )
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertFalse(attacker.is_goal_achieved({'f1': f1, 'f2': f2}))

    def test_gen_orders(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 0.5, 2)
        expected_orders = [[Sell('a1', 150, 2), Sell('a1', 300, 2)],
                           [Sell('a2', 200, 2), Sell('a2', 400, 2)]]
        actual_orders = attacker.gen_orders({'a1': Asset(2, 200, 'a1'), 'a2': Asset(2, 300, 'a2')})
        for i in range(2):
            self.assertListEqual(expected_orders[i], actual_orders[i])

    def test_apply_action(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 0.5, 2)
        orders = [Sell('a1', 150, 2), Sell('a2', 200, 2)]
        attacker.apply_action(Action(orders))
        self.assertEqual(attacker.portfolio['a1'], 150)
        self.assertEqual(attacker.portfolio['a2'], 200)
        self.assertEqual(attacker.capital, 700)
        self.assertEqual(len(attacker.portfolio.items()), 2)

    def test_apply_illegal_action(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 0.5, 2)
        orders = [Buy('a1', 100, 2), Sell('a2', 100, 2)]
        with self.assertRaises(ValueError):
            attacker.apply_action(Action(orders))

    def test_gen_orders_rec(self):
        attacker = Attacker({'a1': 300, 'a2': 400}, ['f1', 'f2'], 0.5, 2)
        expected_orders = \
            [[Sell('a1', 150, 2)], [Sell('a1', 300, 2)],
             [Sell('a2', 200, 2)], [Sell('a2', 400, 2)],
             [Sell('a1', 150, 2), Sell('a2', 200, 2)],
             [Sell('a1', 150, 2), Sell('a2', 400, 2)],
             [Sell('a1', 300, 2), Sell('a2', 200, 2)],
             [Sell('a1', 300, 2), Sell('a2', 400, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = attacker.get_actions({'a1': Asset(2, 200, 'a1'), 'a2': Asset(2, 300, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)


class DefenderTest  (unittest.TestCase):

    def test_resources_exhusted_false_when_capital_exists(self):
        defender = Defender(200, 0.5, 2)
        self.assertFalse(defender.resources_exhusted())

    def test_resources_exhusted_false_when_portfolio_empty(self):
        defender = Defender(200, 0.5, 2)
        self.assertFalse(defender.resources_exhusted())

    def test_game_reward(self):
        f1 = Fund('f1', {}, 200, 2, 2, )
        f2 = Fund('f2', {'a1': 200}, 200, 2, 2, )
        self.assertEqual(Defender.game_reward([f1, f2]), -1)

    def test_gen_orders(self):
        defender = Defender(400, 0.5, 2)
        expected_orders = [[Buy('a1', 100, 2), Buy('a1', 200, 2)], [Buy('a2', 150, 2)]]
        actual_orders = defender.gen_orders({'a1': Asset(2, 200, 'a1'), 'a2': Asset(2, 300, 'a2')})
        for i in range(2):
            self.assertListEqual(expected_orders[i], actual_orders[i])

    def test_apply_action(self):
        defender = Defender(400, 0.5, 2)
        orders = [Buy('a1', 100, 2), Buy('a2', 100, 2)]
        defender.apply_action(Action(orders))
        self.assertEqual(defender.portfolio['a1'], 100)
        self.assertEqual(defender.portfolio['a2'], 100)
        self.assertEqual(defender.capital, 0)
        self.assertEqual(len(defender.portfolio.items()), 2)

    def test_apply_illegal_action(self):
        defender = Defender(400, 0.5, 2)
        orders = [Buy('a1', 100, 2), Sell('a2', 100, 2)]
        with self.assertRaises(ValueError):
            defender.apply_action(Action(orders))

    def test_gen_orders_rec(self):
        defender = Defender(500, 0.5, 2)
        expected_orders = \
            [[Buy('a1', 100, 2)], [Buy('a1', 200, 2)], [Buy('a2', 150, 2)], [Buy('a1', 100, 2), Buy('a2', 150, 2)]]
        e = to_string_list(expected_orders)
        actual_orders = defender.get_actions({'a1': Asset(2, 200, 'a1'), 'a2': Asset(2, 300, 'a2')})
        a = to_string_list(actual_orders)
        self.assertListEqual(e, a)


if __name__ == '__main__':
    unittest.main()
