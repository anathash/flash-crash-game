#from __future__ import division

from copy import deepcopy

# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in
# the UCTPlayGame() function at the bottom of the code.
#
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
# http://mcts.ai/code/python.html
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import random

from GameLogic import GameState
from GameLogic.Orders import Move
from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator
from GameLogic.Players import Attacker, RobustDefender, OracleDefender


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move: Move  =None, parent =None, state: GameState =None, exploration_constant = 2):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.get_valid_actions()  # future child nodes
        self.playerJustMoved = state.current_player()  # the only part of the state that the Node needs later
        self.explorationConstant = exploration_constant

    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key=lambda c: c.wins / c.visits + sqrt(self.explorationConstant * log(self.visits) / c.visits))[-1]
        return s

    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def UCT(rootstate: GameState, itermax, verbose=False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = deepcopy(rootstate)

        # Select
        while node.untriedMoves == [] and node.childNodes != []:  # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.apply_action(node.move)

        # Expand
        if node.untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.apply_action(m)
            node = node.AddChild(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.get_valid_actions() != []:  # while state is non-terminal
            state.apply_action(state.gen_random_action())

        # Backpropagate
        while node != None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(
                node.playerJustMoved))  # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose):
        print(rootnode.TreeToString(0))
    else:
        print(rootnode.ChildrenToString())

    if not rootnode.childNodes:
       return rootnode.childNodes
    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def UCTPlayTwoPlayersGame():
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO
    num_funds = 10
    num_assets = 10

    assets_num_shares = [10000]*num_assets
    initial_prices = [100]*num_assets

    initial_capitals = [10000000]*num_funds
    initial_leverages = [2]*num_funds
    tolerances = [0.7]*num_funds

    g = AssetFundsNetwork.generate_random_network(0.5, num_funds, num_assets, initial_capitals,
                                                  initial_leverages, initial_prices,
                                                  tolerances, assets_num_shares, ExponentialMarketImpactCalculator(1))
    goals = []
    attacker_portfolio = {}
    #num_goals = random.randint(1, num_funds/2)
    #goals_index = random.sample(range(0, num_funds), num_goals)
    goals_index = [0, 1]
    for i in range(len(goals_index)):
        goal_fund_sym = 'f' + str(i)
        goals.append(goal_fund_sym)
        goal_fund = g.funds[goal_fund_sym]
        for asset in goal_fund.portfolio:
            attacker_portfolio[asset] = g.assets[asset].total_shares*0.1

    attacker = Attacker(initial_portfolio=attacker_portfolio, goals=goals, asset_slicing=10, max_assets_in_action=1)
    defender = OracleDefender(initial_capital=100000, asset_slicing=10, max_assets_in_action=2, goals=goals)

    state = GameState.TwoPlayersGameState(g, attacker, defender)
    while (not state.game_ended()):
        print(str(state))
        if state.turn == 1:
            if state.players[state.turn].resources_exhusted(): #insert bayesian here
                state.move_turn()
                continue
            else:
                m = UCT(rootstate=state, itermax=100, verbose=False) #changed from 1000 for debugginf # play with values for itermax and verbose = True
        else:
            m = UCT(rootstate=state, itermax=100, verbose=False) #Attacker
        print("Best Move: " + str(m) + "\n")
        state.apply_action(m)
    if state.game_ended():
        state.print_winner()



def UCTPlaySinglePlayersGame(state):
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO
    while (not state.game_ended()):
        print(str(state))
        m = UCT(rootstate=state, itermax=100, verbose=False)  # Attacker
        print("Best Move: " + str(m) + "\n")
        state.apply_action(m)
    if state.game_ended():
        state.print_winner()


if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    num_funds = 5
    num_assets = 5

    assets_num_shares = [10000] * num_assets
    initial_prices = [100] * num_assets

    initial_capitals = [10000000] * num_funds
    initial_leverages = [2] * num_funds
    tolerances = [1.2] * num_funds

    g = AssetFundsNetwork.generate_random_network(0.5, num_funds, num_assets, initial_capitals,
                                                  initial_leverages, initial_prices,
                                                  tolerances, assets_num_shares, ExponentialMarketImpactCalculator(1))
    goals = []
    attacker_portfolio = {}
    # num_goals = random.randint(1, num_funds/2)
    # goals_index = random.sample(range(0, num_funds), num_goals)
    goals_index = [0]
    for i in range(len(goals_index)):
        goal_fund_sym = 'f' + str(i)
        goals.append(goal_fund_sym)
        goal_fund = g.funds[goal_fund_sym]
        for asset in goal_fund.portfolio:
            attacker_portfolio[asset] = g.assets[asset].total_shares * 0.2

    UCTPlayTwoPlayersGame()

    #    state = GameState.SinglePlayerGameState(network=g, attacker_initial_portfolio=attacker_portfolio,
#                                            attacker_goals=goals, attacker_asset_slicing=10, max_assets_in_action=2)
#    UCTPlaySinglePlayersGame(state)
    exit(0)