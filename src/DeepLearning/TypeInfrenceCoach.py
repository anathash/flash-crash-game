import itertools
from collections import deque
from copy import deepcopy

import numpy as np

import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle

from GameLogic import GameState
from GameLogic.AssetFundNetwork import AssetFundsNetwork
from GameLogic.GameConfig import GameConfig
from GameLogic.GameState import SinglePlayerGameState
from GameRunners.MCTS import UCT
from GameLogic.MarketImpactCalculator import ExponentialMarketImpactCalculator, SqrtMarketImpactCalculator


class TypeInfrenceCoach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, example_folder_path, config:GameConfig):
        self.trainExamplesHistory = []  # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.example_folder_path = example_folder_path
        self.config = config
        #self.pnet = self.nnet.__class__(self.game)  # the competitor network
        #self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()

    def executeEpisode(self, state: GameState, iter_num):
        states = []

        while (not state.game_ended()):
            m = UCT(rootstate=state, itermax=iter_num, verbose=False)  # Attacker
            states.append(state.network.get_canonical_form())
            state.apply_action(m)
        if state.game_ended():
            if state.attacker.game_reward(state.network.funds) == 1:
                print('win in ' + str(len(states)) + ' moves')
                return [(states, state.attacker.goals)]
            else:
                print('lose in ' + len(state) + ' moves')
                return []



    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximium length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters+1):
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration
            if not self.skipFirstSelfPlay or i>1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)

                eps_time = AverageMeter()
                bar = Bar('Self Play', max=self.args.numEps)
                end = time.time()

                for eps in range(self.args.numEps):
                    self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree
                    iterationTrainExamples += self.executeEpisode()

                    # bookkeeping + plot progress
                    eps_time.update(time.time() - end)
                    end = time.time()
                    bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args.numEps, et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                    bar.next()
                bar.finish()

                # save the iteration examples to the history
                self.trainExamplesHistory.append(iterationTrainExamples)

            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0)
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples(i-1)

            # shuffle examlpes before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            pmcts = MCTS(self.game, self.pnet, self.args)

            self.nnet.train(trainExamples)
            nmcts = MCTS(self.game, self.nnet, self.args)

            print('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                          lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
            pwins, nwins, draws = arena.playGames(self.args.arenaCompare)

            print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            if pwins+nwins == 0 or float(nwins)/(pwins+nwins) < self.args.updateThreshold:
                print('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            else:
                print('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed


    def loadTrainExamples(self, examplesFile):
        #modelFile = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        #examplesFile = modelFile+".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True

    def create_portofolio(self, netowrk, goals):
        portfolio = {}
        for goal in goals:
            goal_fund = netowrk.funds[goal]
            for asset in goal_fund.portfolio:
                portfolio[asset] = netowrk.assets[asset].daily_volume * self.config.attacker_portfolio_ratio
        return portfolio

    def saveGoalsExamples(self, goals, examples):
        folder = self.example_folder_path
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(goals) + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(examples)
        f.closed

    def examples_collected(self, goals):
        folder = self.example_folder_path
        if not os.path.exists(folder):
            return False
        filename = os.path.join(folder, self.getCheckpointFile(goals) + ".examples")
        if os.path.isfile(filename):
            return True

    def gen_goals_fund_list(self, goals_vector):
        goals_list = []
        for i in range(len(goals_vector)):
            if goals_vector[i]:
                goals_list.append('f' + str(i))
        return goals_list

    def gen_training_examples(self, network, episodes_per_goal, uct_iterations):
        goals_set = list(itertools.product([0, 1], repeat=self.config.num_funds))
        goals_set = goals_set[1:]
        for goals in goals_set:
            goals_vector = list(goals)
            goals_list = self.gen_goals_fund_list(goals_vector)
            goals_string = ''.join([str(x) for x in goals_list])
            if self.examples_collected(goals_string):
                continue
            portfolio = self.create_portofolio(network, goals_list)
            initial_state = SinglePlayerGameState(deepcopy(network), portfolio,goals_list,
                                                  self.config.attacker_asset_slicing,
                                                  self.config.attacker_max_assets_in_action)
            train_examples = []
            for i in range(episodes_per_goal):
                train_examples += self.executeEpisode(deepcopy(initial_state), uct_iterations)

            #self.trainExamplesHistory.extend(train_examples)
            self.saveGoalsExamples(goals_string, train_examples)

if __name__ == "__main__":
    config = GameConfig(num_funds=10, num_assets=10)
    coach = TypeInfrenceCoach('../../resources/examples/ten by ten', config)
    #coach.loadTrainExamples('../../resources/examples/checkpoint_f0.pth.tar.examples')
    network = AssetFundsNetwork.load_from_file('../../resources/ten_by_ten.json', SqrtMarketImpactCalculator())
    network.run_intraday_simulation(config.intraday_asset_gain_max_range, 0.7 * config.initial_leverage)
    coach.gen_training_examples(network, episodes_per_goal=10, uct_iterations=10)

