from copy import deepcopy

from Actions import Action
from AssetFundNetwork import AssetFundsNetwork
from Players import Defender, Attacker


class GameState:
    def __init__(self, input_file):
        self.network = AssetFundsNetwork(input_file)

    def game_reward(self):
        raise NotImplementedError

    def game_ended(self):
        raise NotImplementedError

    def get_valid_actions(self):
        raise NotImplementedError

    def apply_action(self, action: Action):
        raise NotImplementedError


class TwoPlayersGameState(GameState):
    def __init__(self, input_file, defender_initial_capital, attacker_initial_portfolio, attacker_goals):
        super().__init__(input_file)
        self.attacker = Attacker(attacker_initial_portfolio, attacker_goals)
        self.defender = Defender(defender_initial_capital)
        self.turn = 0
        self.players = [self.attacker, self.defender]

    def game_reward(self):
        return self.defender.game_reward(self.network.funds)

    def game_ended(self):
        return self.attacker.is_goal_achieved(self.network.funds) or \
               self.defender.resources_exhusted() or self.attacker.resources_exhusted()

    def get_valid_actions(self):
        return self.players[self.turn].get_valid_actions(self.network.assets)

    def apply_action(self, action: Action):
        self.players[self.turn].apply_action(action, self.network.assets)
        self.network.apply_action(action)
        self.move_turn()

    def move_turn(self):
        self.turn = (self.turn + 1) % len(self.players)


class SinglePlayerGameState(GameState):
    def __init__(self, input_file, attacker_initial_portfolio, attacker_goals):
        super().__init__(input_file)
        self.attacker = Attacker(attacker_initial_portfolio, attacker_goals)

    def game_reward(self):
        return self.attacker.game_reward(self.network)

    def game_ended(self):
        return self.attacker.is_goal_achieved(self.network.funds)

    def get_valid_actions(self):
        return self.attacker.get_valid_actions(self.network.assets)

    def apply_action(self, action: Action):
        self.attacker.apply_action(action, self.network.assets)
        self.network.apply_action(action)
