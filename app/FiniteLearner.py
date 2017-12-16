from __future__ import division

import datetime
import random as rd
import numpy as np
import logging

from app.DinoScanner import Barrier
from app.Abstract import OnLearnerCallback
from app.Settings import DINO_REWARD_PADDING, POPULATION_SIZE, HIDDEN_LAYER_NEURONS,\
    LEARN_RATE, LEARN_SIGMA, NEARBY_SIGMA


################################################
class FiniteLearner(OnLearnerCallback):

    def __init__(self, on_action_callback):
        super(FiniteLearner, self).__init__(on_action_callback)
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

        self.ideal_genome = Genome.empty()
        self.active, self.population = None, None
        self.start_noise()

    def on_load_source(self, source):
        self.ideal_genome = source
        self.start_noise()

    def on_get_source(self):
        return self.ideal_genome

    def on_start(self):
        if self.active is None:
            self.active = self.ideal_genome
            logging.info("Running Ideal Genome: " + str(0)
                  + " " + str(self.active))
            return

        if self.active is self.ideal_genome:
            self.active = self.population[0]
            logging.info("Working Index: " + str(0)
                       + " " + str(self.active))
            self.active.start_work()
            return

        self.active.stop_work()
        logging.info("Last Genome End with Rewards: "
                     + str(self.active.get_reward()))

        index = self.population.index(self.active) + 1
        if index < len(self.population):
            self.active = self.population[index]

            logging.info("Working Index: " + str(index)
                  + " " + str(self.active))
            self.active.start_work()
        else:
            self.active = None
            self.move_population()
            self.on_start()

    def on_receive(self, params):
        action = self.active.apply_action(params)
        self.on_action_callback.on_action(action)

    def start_noise(self):
        self.population = []
        for item in range(POPULATION_SIZE):
            self.population.append(Genome.nearby(self.ideal_genome))

    def move_population(self):
        self.__print_generation()

        rewards = []
        for genome in self.population:
            rewards.append(genome.get_reward())

        size = len(self.population)
        reward_mean = np.sum(rewards) / size
        reward_std = np.std(rewards) + .00001

        #-------------------------------------------------
        # Main function for rewards Moving for each Genome,
        # and sum all them with priority to most Rewarded!
        correction = Genome.empty()
        for index in range(size):
            genome = self.population[index]

            for n in range(len(genome.get_neurons())):
                if len(correction.get_neurons()) <= n:
                    correction.get_neurons().append(Neuron.empty(0))

                correction_n_weights = correction.get_neurons()[n].get_weights()
                for w in range(len(genome.get_neurons()[n].get_weights())):
                    if len(correction_n_weights) <= w:
                        correction_n_weights.append(0)

                    correction_n_weights[w] = correction_n_weights[w] \
                           + genome.get_neurons()[n].get_weights()[w] \
                             * (rewards[index] - reward_mean) / reward_std

            # This for calculation output layer weights
            correction_o_weights = correction.get_output_neurons().get_weights()
            for i in range(len(genome.get_output_neurons().get_weights())):
                if len(correction_o_weights) <= i:
                    correction_o_weights.append(0)
                correction_o_weights[i] = correction_o_weights[i] + genome.get_output_neurons()\
                        .get_weights()[i] * (rewards[index] - reward_mean) / reward_std

        # ------------------------------------------
        # Move Ideal Genome from calculated previous
        # results, and Divide to their total Size.
        ideal_neurons = self.ideal_genome.get_neurons()
        for n in range(len(correction.get_neurons())):
            if len(ideal_neurons) <= n:
                ideal_neurons.append(Neuron.empty(0))

            ideal_n_weights = ideal_neurons[n].get_weights()
            for w in range(len(correction.get_neurons()[n].get_weights())):
                if len(ideal_n_weights) <= w:
                    ideal_n_weights.append(0)

                ideal_n_weights[w] = float(ideal_n_weights[w] \
                            + (correction.get_neurons()[n].get_weights()[w]
                               * LEARN_RATE / (size * LEARN_SIGMA)))

        # This for calculation output layer weights
        ideal_o_weights = self.ideal_genome.get_output_neurons().get_weights()
        for w in range(len(correction.get_output_neurons().get_weights())):
            if len(ideal_o_weights) <= w:
                ideal_o_weights.append(0)

            ideal_o_weights[w] = float(ideal_o_weights[w] +
                (correction.get_output_neurons().get_weights()[w]
                 * LEARN_RATE / (size * LEARN_SIGMA)))

        logging.info("Working Ideal Genome: " + str(self.ideal_genome))
        self.ideal_genome.set_generation(self.ideal_genome.get_generation() + 1)
        self.active = None
        self.start_noise()

    def __print_generation(self):
        logging.info("Generation Done Work!")

        top_rewards_genome = None
        for genome in self.get_population():
            if top_rewards_genome is None:
                top_rewards_genome = genome
                continue
            if genome.get_reward() > top_rewards_genome.get_reward():
                top_rewards_genome = genome

        logging.info("Most Rewards for Genome: " + str(self.get_population().index(top_rewards_genome))
              + " Reward: " + str(top_rewards_genome.get_reward()) + "\n" + str(top_rewards_genome))

    def get_population(self):
        return self.population


################################################
# - Genome have fixed scheme of Neuron structure.
# - Genome velocity, it's time, which Genome playing.
class Genome:
    def __init__(self, neurons, output_neurons):
        self.__neurons = neurons
        self.__output_neurons = output_neurons
        self.__generation, self.__worked_time = 0, 0

    @classmethod
    def empty(cls):
        neurons = []
        for item in range(HIDDEN_LAYER_NEURONS):
            neurons.append(Neuron.empty(0))
        return Genome(neurons, Neuron.empty(0))

    @classmethod
    def nearby(cls, genome):
        neurons = []
        for neuron in genome.get_neurons():
            neurons.append(Neuron.nearby(neuron))
        return Genome(neurons, Neuron.nearby(genome.get_output_neurons()))

    def apply_action(self, params):
        neuron_effects = []

        # Single hidden layer of Neurons
        for neuron in self.__neurons:
            action = relu_activation(neuron.effect(params))
            neuron_effects.append(action)

        # Layer gathering outputs
        final_effect = sigmoid_activation(
            self.__output_neurons.effect(neuron_effects))
        return final_effect

    def start_work(self):
        self.__worked_time = datetime.datetime.now()

    def stop_work(self):
        self.__worked_time = (datetime.datetime.now()
                              - self.__worked_time).total_seconds()

    def get_worked_time(self):
        return self.__worked_time

    def set_reward(self, value):
        self.__worked_time = value

    def get_reward(self):
        return int(round(self.__worked_time - DINO_REWARD_PADDING))

    def get_neurons(self):
        return self.__neurons

    def get_output_neurons(self):
        return self.__output_neurons

    def set_generation(self, value):
        self.__generation = value

    def get_generation(self):
        return self.__generation

    def __str__(self):
        neuron_info = "Genome Generation " \
                      + str(self.__generation) + " with Neurons: \n"
        for neuron in self.get_neurons():
            neuron_info += str(neuron) + "\n"

        neuron_info += "And Output Layer " \
                       + str(self.get_output_neurons()) + "\n"
        return neuron_info


################################################
class Neuron:
    ROUND_SIZE = 8

    def __init__(self, weights):
        self.__weights = weights

    @classmethod
    def empty(cls, inputs):
        new_weights = []
        for item in range(inputs):
            new_weights.append(0)
        return Neuron(new_weights)

    @classmethod
    def nearby(cls, other_neuron):
        new_weights = []
        for w in other_neuron.get_weights():
            new_weights.append(round(np.random.normal(w, NEARBY_SIGMA, 1)
                                     [0], Neuron.ROUND_SIZE))
        return Neuron(new_weights)

    @classmethod
    def with_random(cls, length):
        weights = []
        for item in range(length):
            weights.append(round(rd.uniform(-NEARBY_SIGMA, NEARBY_SIGMA),
                                 Neuron.ROUND_SIZE))
        return Neuron(weights)

    def effect(self, values):
        effect = 0
        # Fill with empty result in case of not defined Weights
        for i in range(len(values) - len(self.__weights)):
            self.__weights.append(0)

        for val, weight in zip(values, self.__weights):
            effect += val * weight
        return effect

    def get_weights(self):
        return self.__weights

    def __str__(self):
        return "Neuron Weights: " \
               + str(self.get_weights())


################################################
def sigmoid_activation(val):
    return 1 / (1 + np.exp(-val))


def relu_activation(val):
    return val * (val > 0)



