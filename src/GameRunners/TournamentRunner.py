#from __future__ import division
import csv
import itertools
from copy import deepcopy
from GameLogic import GameState, GameConfig
from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.Players import Attacker, RobustDefender, OracleDefender, Defender
from GameRunners.MCTS import UCT


class Stats:
    def __init__(self):
        self.attacker_wins = 0
        self.defender_wins = 0

    def update_attacker_win(self):
        self.attacker_wins += 1

    def update_attacker_win(self):
        self.defender_wins += 1

    def update_win_stats(self, winner):
        if isinstance(winner, Attacker):
            self.attacker_wins += 1
            return
        if isinstance(winner, Defender):
            self.defender_wins += 1
            return
        raise ValueError


class SingleTournamentRunner:
    def __init__(self, num_games, network, defender_alg, attacker_goals, config: GameConfig):
        self.num_games = num_games
        self.network = network
        self.config = config
        self.goals = attacker_goals
        self.attacker = self.gen_attacker(network,attacker_goals, config.attacker_asset_slicing,
                                          config.max_assets_in_action, config.attacker_portfolio_ratio)
        self.defender = self.gen_defender(defender_alg, goals=attacker_goals)

        self.stats = Stats()

    @staticmethod
    def gen_defender(alg, goals, config: GameConfig):
        if alg =='robust':
            return RobustDefender(config.defender_initial_capital,
                                  config.defender_asset_slicing, config.defender_max_assets_in_action)
        if alg == 'oracle':
            return OracleDefender(goals, config.defender_initial_capital,
                                  config.defender_asset_slicing, config.defender_max_assets_in_action)
        raise ValueError

    def gen_attacker(self, network, goals, attacker_asset_slicing, max_assets_in_action, portfolio_ratio):
        attacker_portfolio = {}
        for goal in goals:
            goal_fund = self.network.funds[goal]
            for asset in goal_fund.portfolio:
                attacker_portfolio[asset] = network.assets[asset].total_shares * portfolio_ratio

        return Attacker(initial_portfolio=attacker_portfolio, goals=goals, asset_slicing=attacker_asset_slicing,
                         max_assets_in_action=max_assets_in_action)

    def play_single_game(self, network, attacker, defender):
        state = GameState.TwoPlayersGameState(network, attacker, defender)
        while not state.game_ended():
            if state.turn == 1:
                if state.players[state.turn].resources_exhusted():  # insert bayesian here
                    state.move_turn()
                    continue
                else:
                    m = UCT(rootstate=state, itermax=100,
                            verbose=False)  # changed from 1000 for debugging # play with values for itermax and verbose = True
            else:
                m = UCT(rootstate=state, itermax=100, verbose=False)  # Attacker
            state.apply_action(m)
        if state.game_ended():
            self.stats.update_win_stats(state.get_winner())

    def run_single_tournament(self):
        for s in range(self.num_games):
            self.play_single_game(deepcopy(self.network), deepcopy(self.attacker), deepcopy(self.attacker))
        return self.stats


class MultipleTournamentRunner:
    def __init__(self, csv_file_name, num_games_per_tournaments, network_file_name, defender_alg,
                 config: GameConfig):
        self.num_games_per_tournaments = num_games_per_tournaments
        self.network = AssetFundsNetwork.load_from_file(network_file_name)
        self.defender_alg = defender_alg
        self.config = config
        fieldnames = ['goals', 'attacker_wins', 'defender_wins', 'defender_alg']
        fieldnames.extend(self.config.__dict__.keys())
        self.csv_file = open(csv_file_name, 'w')
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.writer.writeheader()
        one_time_params = {'defender_alg': defender_alg}
        one_time_params.update(self.writer.writerow(self.config.__dict__))
        self.writer.writerow(one_time_params)

    def run_for_goals_set(self, goals_set):
        for goals in goals_set:
            tournament_runner = SingleTournamentRunner(self.num_games, self.network,
                                                       self.defender_alg, goals, self.config)
            params = {'goals': goals.join('')}
            stats = tournament_runner.run_single_tournament()
            params.update(stats.__dict__)
            self.writer.writerow(params)
        self.csv_file.close()

    def gen_goals_fund_list(self, goals_vector):
        goals_list = []
        for i in range(len(goals_vector)):
            if goals_vector[i]:
                goals_list.append('f' + str(i))
        return goals_list

    def run_for_all_goals(self):
        goals_set = []
        goals_indexes = list(itertools.product([0, 1], repeat=self.config.num_funds))
        goals_indexes = goals_indexes[1:]
        for goals in goals_indexes[:1]:
            goals_vector = list(goals)
            goals_set.append(self.gen_goals_fund_list(goals_vector))
        self.run_for_goals_set(goals_set)

