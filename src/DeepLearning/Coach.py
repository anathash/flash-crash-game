#from __future__ import division

from GameLogic import GameState
from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameRunners.MCTS import UCT
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator


def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO
    num_funds = 3
    num_assets = 3

    assets_num_shares = [10000]*num_assets
    initial_prices = [100]*num_assets

    initial_capitals = [10000000]*num_funds
    initial_leverages = [2]*num_funds
    tolerances = [1.2]*num_funds

    g = AssetFundsNetwork.generate_random_network(0.5, num_funds, num_assets, initial_capitals,
                                                  initial_leverages, initial_prices,
                                                  tolerances, assets_num_shares, ExponentialMarketImpactCalculator(1))
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
            attacker_portfolio[asset] = g.assets[asset].total_shares*0.2

    state = GameState.SinglePlayerGameState(g, 100000, attacker_portfolio, goals, 10, 10, 1)  # uncomment to play Nim with the given number of starting chips
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
    UCTPlayGame()
    exit(0)