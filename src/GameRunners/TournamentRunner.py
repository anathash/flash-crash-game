#from __future__ import division
import csv
import itertools
from copy import deepcopy
from GameLogic import GameState
from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.GameConfig import GameConfig
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator
from GameLogic.Players import Attacker, RobustDefender, OracleDefender, Defender
from GameRunners.MCTS import UCT


class Stats:
    def __init__(self):
        self.attacker_wins = 0
        self.defender_wins = 0
        self.avg_num_moves = 0

    def update_stats(self, winner, num_moves):
        self.avg_num_moves += num_moves
        if isinstance(winner, Attacker):
            self.attacker_wins += 1
            return
        if isinstance(winner, Defender):
            self.defender_wins += 1
            return
        raise ValueError

    def get_stats(self):
        self.avg_num_moves = self.avg_num_moves / (self.attacker_wins + self.defender_wins)
        return self.__dict__


class SingleTournamentRunner:
    def __init__(self, num_games, network, defender_alg, attacker_goals, config: GameConfig):
        self.num_games = num_games
        self.network = network
        self.config = config
        self.goals = attacker_goals
        self.attacker = self.gen_attacker(network, attacker_goals)
        self.defender = self.gen_defender(defender_alg, goals=attacker_goals)

        self.stats = Stats()

    def gen_defender(self, alg, goals):
        if alg == 'robust':
            return RobustDefender(config.defender_initial_capital,
                                  config.defender_asset_slicing, self.config.defender_max_assets_in_action)
        if alg == 'oracle':
            return OracleDefender(goals, config.defender_initial_capital,
                                  config.defender_asset_slicing, self.config.defender_max_assets_in_action)
        raise ValueError

    def gen_attacker(self, network, attacker_goals):
        attacker_portfolio = {}
        for goal in attacker_goals:
            goal_fund = self.network.funds[goal]
            for asset in goal_fund.portfolio:
                attacker_portfolio[asset] = network.assets[asset].daily_volume * self.config.attacker_portfolio_ratio

        return Attacker(initial_portfolio=attacker_portfolio, goals=attacker_goals, asset_slicing=self.config.attacker_asset_slicing,
                         max_assets_in_action=self.config.attacker_max_assets_in_action)

    def play_single_game(self, network, attacker, defender):
        state = GameState.TwoPlayersGameState(network, attacker, defender)
        moves_counter = 0
        while not state.game_ended():
            moves_counter += 1
            if state.turn == 1:
                if state.players[state.turn].resources_exhusted():  # insert bayesian here
                    state.move_turn()
                    continue
                else:
                    m = UCT(rootstate=state, itermax=1000,
                            verbose=False)  # changed from 1000 for debugging # play with values for itermax and verbose = True
            else:
                m = UCT(rootstate=state, itermax=1000, verbose=False)  # Attacker
            state.apply_action(m)
        if state.game_ended():
            self.stats.update_stats(state.get_winner(), moves_counter)

    def run_single_tournament(self):
        for g in range(self.num_games):
            print('iteration ' + str(g))
            self.play_single_game(deepcopy(self.network), deepcopy(self.attacker), deepcopy(self.attacker))
        return self.stats.get_stats()


class MultipleTournamentRunner:
    def __init__(self, csv_file_name, num_games_per_tournament, network_file_name, defender_alg,
                 config: GameConfig):
        self.config = config
        self.num_games_per_tournaments = num_games_per_tournament
        self.network = AssetFundsNetwork.load_from_file(network_file_name,
                                                        ExponentialMarketImpactCalculator(self.config.impact_calc_constant))
        self.network.run_intraday_simulation(config.intraday_asset_gain_max_range)
        self.defender_alg = defender_alg
        fieldnames = ['goals', 'attacker_wins', 'defender_wins', 'avg_num_moves', 'defender_alg']
        fieldnames.extend(self.config.__dict__.keys())
        self.csv_file = open(csv_file_name, 'w', newline='')
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.writer.writeheader()
        one_time_params = {'defender_alg': defender_alg}
        config_dict = self.config.__dict__
        one_time_params.update(config_dict)
        self.writer.writerow(one_time_params)

    def run_for_goals_set(self, goals_set):
        for goals in goals_set:
            tournament_runner = SingleTournamentRunner(self.num_games_per_tournaments, self.network,
                                                       self.defender_alg, goals, self.config)
            params = {'goals': '-'.join(goals)}
            stats = tournament_runner.run_single_tournament()
            params.update(stats)
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

if __name__ == "__main__":
    config = GameConfig()
    csv_file_name = '../../resources/ten_by_ten_oracle.csv'
    runner = MultipleTournamentRunner(csv_file_name, 10, '../../resources/ten_by_ten_network.json', 'oracle', config)
    goals = [['f0', 'f1'], ['f0']]
    runner.run_for_goals_set(goals)
    exit(0)

