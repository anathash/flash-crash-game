class GameConfig:
    def __init__(self, num_assets=10,
                 num_funds=10,
                 min_order_value=1000,
                 density=0.5,
                 initial_num_shares=500,
                 initial_asset_price=1000,
                 initial_fund_capital=500000,
                 initial_leverage=2,
                 tolerance=1.01,
                 attacker_portfolio_ratio=0.2,
                 attacker_max_assets_in_action=3,
                 attacker_asset_slicing=10,
                 defender_max_assets_in_action=3,
                 defender_asset_slicing=10,
                 defender_initial_capital=1000000,
                 impact_calc_constant=1.0536):

        self.num_assets = num_assets
        self.num_funds = num_funds
        self.min_order_value = min_order_value
        self.density = density
        self.initial_num_shares = initial_num_shares
        self.initial_asset_price = initial_asset_price
        self.initial_fund_capital = initial_fund_capital
        self.initial_leverage = initial_leverage
        self.tolerance = tolerance
        self.attacker_portfolio_ratio = attacker_portfolio_ratio
        self.attacker_max_assets_in_action = attacker_max_assets_in_action
        self.attacker_asset_slicing = attacker_asset_slicing
        self.defender_max_assets_in_action = defender_max_assets_in_action
        self.defender_asset_slicing = defender_asset_slicing
        self.defender_initial_capital = defender_initial_capital
        self.impact_calc_constant = impact_calc_constant



