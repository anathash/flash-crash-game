#from __future__ import division

from GameLogic import GameState
from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.GameConfig import GameConfig
from GameRunners.MCTS import UCT
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator


def UCTPlayGame(config, network_file_name, marketImpactCalc):
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO
    network = AssetFundsNetwork.load_from_file(network_file_name, marketImpactCalc, marketImpactCalc)
    goals = []
    attacker_portfolio = {}
    #num_goals = random.randint(1, num_funds/2)
    #goals_index = random.sample(range(0, num_funds), num_goals)
    goals_index = [0]
    for i in range(len(goals_index)):
        goal_fund_sym = 'f' + str(i)
        goals.append(goal_fund_sym)
        goal_fund = g.funds[goal_fund_sym]
        for asset in goal_fund.portfolio:
            attacker_portfolio[asset] = network.assets[asset].daily_volume*0.2

    state = GameState.SinglePlayerGameState(network, 100000, attacker_portfolio, goals, 10, 10, 1)
    while (not state.game_ended()):
        print(str(state))
        m = UCT(rootstate=state, itermax=100, verbose=False) #Attacker
        print("Best Move: " + str(m) + "\n")
        state.apply_action(m)
    if state.game_ended():
        state.print_winner()



if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    config = GameConfig()
    config.num_assets = 10
    config.num_funds = 10
    UCTPlayGame()
    exit(0)