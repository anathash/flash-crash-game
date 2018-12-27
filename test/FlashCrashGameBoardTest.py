import unittest


from FlashCrashGameBoard import Asset, Holding, Fund


class TestFlashCrashGameBoard  (unittest.TestCase) :

    def test_illegal_holding_raise_exception(self):
        a1 = Asset(1, 5, 'XXX')
        self.assertRaises(ValueError, Holding, a1, 6)

    def test_fund_computations(self):
        a1 = Asset(1, 10, 'XXX')
        a2 = Asset(4, 10, 'yyy')
        h1 = Holding(a1, 10)
        h2 = Holding(a2, 10)
        holdings = [h1,h2]
        fund = Fund(holdings, 5, 2, 3)
        self.assertEqual(50, fund.compute_protfolio_value())
        self.assertEqual(9, fund.compute_curr_leverage())
        self.assertEqual(False, fund.marginal_call())

        a2.update_price(1)
        self.assertEqual(a2.price, 1)

        self.assertEqual(20, fund.compute_protfolio_value())
        self.assertEqual(3, fund.compute_curr_leverage())
        self.assertEqual(True, fund.marginal_call())

    def test_fund_liquidation(self):
        a1 = Asset(1, 10, 'XXX')
        a2 = Asset(4, 10, 'yyy')
        h1 = Holding(a1, 10)
        h2 = Holding(a2, 10)
        holdings = [h1, h2]
        fund = Fund(holdings, 5, 2, 3)
        self.assertTrue(fund.holdings)
        self.assertEqual(fund.is_liquidated(), False)
        fund.liquidate()
        self.assertFalse(fund.holdings)


if __name__ == '__main__':
    unittest.main()