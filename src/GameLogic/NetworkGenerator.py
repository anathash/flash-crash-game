from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.GameConfig import GameConfig
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator, SqrtMarketImpactCalculator


class NetworkGenerator():
    """DENSITY = 0.5
    INITIAL_NUM_SHARES = 500
    INITIAL_ASSET_PRICE = 1000
    INITIAL_FUND_CAPITAL = 500000
    INITIAL_LEVERAGE = 2
    TOLERANCE = 1.01
"""
    @staticmethod
    def generate_and_save_rand_network(file_name, game_config: GameConfig):
        assets_num_shares = [game_config.asset_daily_volume] * game_config.num_assets
        initial_prices = [game_config.initial_asset_price] * game_config.num_assets
        volatility = [game_config.asset_volatility] * game_config.num_assets

        initial_capitals = [game_config.initial_fund_capital] * game_config.num_funds
        initial_leverages = [game_config.initial_leverage] * game_config.num_funds
        tolerances = [game_config.tolerance] * game_config.num_funds


        g = AssetFundsNetwork.generate_random_network(game_config.density,
                                                      game_config.num_funds,
                                                      game_config.num_assets,
                                                      initial_capitals,
                                                      initial_leverages, initial_prices,
                                                      tolerances, assets_num_shares,
                                                      volatility,
                                                      SqrtMarketImpactCalculator())
        g.save_to_file(file_name)




if __name__ == "__main__":
    config = GameConfig()
    config.num_assets = 10
    config.num_funds = 10
    NetworkGenerator.generate_and_save_rand_network('../../resources/ten_by_ten.json', config )
