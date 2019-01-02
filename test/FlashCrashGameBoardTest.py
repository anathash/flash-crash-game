import unittest


from AssetFundNetwork import Asset,  Fund


class TestFlashCrashGameBoard  (unittest.TestCase):

    def test_fund_computations(self):
        assets = {'XXX': Asset(1, 10, 'XXX'), 'YYY': Asset(4, 10, 'yyy')}
        holdings = {'XXX': 10, 'YYY': 10}
        fund = Fund('F1', holdings, 5, 2, 3)
        self.assertEqual(50, fund.compute_portfolio_value(assets))
        self.assertEqual(9, fund.compute_curr_leverage(assets))
        self.assertEqual(False, fund.marginal_call(assets))

        assets['YYY'].set_price(1)
        self.assertEqual(assets['YYY'].price, 1)

        self.assertEqual(20, fund.compute_portfolio_value(assets))
        self.assertEqual(3, fund.compute_curr_leverage(assets))
        self.assertEqual(True, fund.marginal_call(assets))

    def test_fund_liquidation(self):
        holdings = {'XXX': 10, 'YYY': 10}
        fund = Fund('F1', holdings, 5, 2, 3)
        self.assertTrue(fund.portfolio)
        self.assertEqual(fund.is_liquidated(), False)
        fund.liquidate()
        self.assertFalse(fund.portfolio)


if __name__ == '__main__':
    unittest.main()
