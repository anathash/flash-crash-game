from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.Config import Config
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator


class NetworkGenerator():
    """DENSITY = 0.5
    INITIAL_NUM_SHARES = 500
    INITIAL_ASSET_PRICE = 1000
    INITIAL_FUND_CAPITAL = 500000
    INITIAL_LEVERAGE = 2
    TOLERANCE = 1.01
"""
    @staticmethod
    def generate_and_save_rand_10_by_10_network(file_name):
        num_funds = Config.get(Config.NUM_FUNDS)
        num_assets = Config.get(Config.NUM_ASSETS)
        assets_num_shares = [Config.get(Config.INITIAL_NUM_SHARES)] * num_assets
        initial_prices = [Config.get(Config.INITIAL_ASSET_PRICE)] * num_assets

        initial_capitals = [Config.get(Config.INITIAL_FUND_CAPITAL)] * num_funds
        initial_leverages = [Config.get(Config.INITIAL_LEVERAGE)] * num_funds
        tolerances = [Config.get(Config.TOLERANCE)] * num_funds

        g = AssetFundsNetwork.generate_random_network(Config.get(Config.DENSITY),
                                                      num_funds,
                                                      num_assets,
                                                      initial_capitals,
                                                      initial_leverages, initial_prices,
                                                      tolerances, assets_num_shares,
                                                      ExponentialMarketImpactCalculator(1))
        g.save_to_file(file_name)

    @staticmethod
    def generate_and_save_rand_network(file_name, num_funds, num_assets):
        assets_num_shares = [Config.get(Config.INITIAL_NUM_SHARES)] * num_assets
        initial_prices = [Config.get(Config.INITIAL_ASSET_PRICE)] * num_assets

        initial_capitals = [Config.get(Config.INITIAL_FUND_CAPITAL)] * num_funds
        initial_leverages = [Config.get(Config.INITIAL_LEVERAGE)] * num_funds
        tolerances = [Config.get(Config.TOLERANCE)] * num_funds

        g = AssetFundsNetwork.generate_random_network(Config.get(Config.DENSITY),
                                                      num_funds,
                                                      num_assets,
                                                      initial_capitals,
                                                      initial_leverages, initial_prices,
                                                      tolerances, assets_num_shares,
                                                      ExponentialMarketImpactCalculator(1))
        g.save_to_file(file_name)


if __name__ == "__main__":
    NetworkGenerator.generate_and_save_rand_network('../../resources/four_by_four_network.json', 4, 4)
