from copy import deepcopy

from GameState import GameState


class GameStateLogic:
    def __init__(self, input_file, defender_initial_capital, attacker_initial_portfolio, attacker_goals):
        self.state = GameState(input_file, defender_initial_capital, attacker_initial_portfolio, attacker_goals)

    def game_reward(self):
        return self.state.game_reward()

    def game_ended(self):
        return self.state.game_ended()

    def get_valid_actions(self):
        return self.state.get_valid_actions()

    def next_state(self, action):
        next_state = deepcopy(self.state)
        next_state.apply_action(action)
        next_state.move_turn()

