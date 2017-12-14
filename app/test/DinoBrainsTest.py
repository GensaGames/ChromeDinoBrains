from __future__ import print_function
import cv2  # .cv2 as cv2
import time
import unittest
import numpy as np

import os
import app.Settings
import app.DinoScanner
import app.FiniteLearner


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyUnresolvedReferences
class BrainsTest(unittest.TestCase):

    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        print("%s: %.3f ms" % (self.id(), time.time() - self.startTime))

    def log(self, msg):
        print(self.id() + ": " + msg)

    def __generation_move(self, brains, weight):
        new_ideal_neurons = []

        for _ in range(app.Settings.HIDDEN_LAYER_NEURONS):
            brains.get_population().pop()
            brains.get_population().append(app.FiniteLearner.Genome.empty())

        for _ in range(app.Settings.HIDDEN_LAYER_NEURONS):
            new_weights = []
            for __ in range(app.Settings.INPUT_LAYER_NEURONS):
                new_weights.append(weight)
            new_ideal_neurons \
                .append(app.FiniteLearner.Neuron(new_weights))

        out_output_weights = []
        for __ in range(app.Settings.HIDDEN_LAYER_NEURONS):
            out_output_weights.append(weight)
        new_output_neuron = app.FiniteLearner.Neuron(out_output_weights)

        brains.get_population().pop()
        new_ideal_genome = app.FiniteLearner\
            .Genome(new_ideal_neurons, new_output_neuron)

        new_ideal_genome.set_reward(1)
        brains.get_population().append(new_ideal_genome)
        brains.move_population()

    def test_generation_positive(self):
        brains = app.FiniteLearner.FiniteLearner(None, app.FiniteLearner.Genome.empty())
        initial_weights_value = 0
        for neuron in brains.on_get_source().get_neurons():
            initial_weights_value += sum(neuron.get_weights())

        self.log("Sum weights before generation: " + str(initial_weights_value))
        self.__generation_move(brains, 0.5)
        updated_weights_value = 0
        for neuron in brains.on_get_source().get_neurons():
            updated_weights_value += sum(neuron.get_weights())

        self.log("Sum weights after generation: " + str(updated_weights_value))
        self.assertTrue(updated_weights_value > initial_weights_value)

    def test_generation_negative(self):
        brains = app.FiniteLearner.FiniteLearner(None, app.FiniteLearner.Genome.empty())
        initial_weights_value = 0
        for neuron in brains.on_get_source().get_neurons():
            initial_weights_value += sum(neuron.get_weights())

        self.log("Sum weights before generation: " + str(initial_weights_value))
        self.__generation_move(brains, -0.5)
        updated_weights_value = 0
        for neuron in brains.on_get_source().get_neurons():
            updated_weights_value += sum(neuron.get_weights())

        self.log("Sum weights after generation: " + str(updated_weights_value))
        self.assertTrue(updated_weights_value < initial_weights_value)

    def test_generation_output_layer(self):
        brains = app.FiniteLearner.FiniteLearner(None, app.FiniteLearner.Genome.empty())
        initial_weights_value = sum(brains.on_get_source()
                                    .get_output_neurons().get_weights())

        self.log("Sum Output before generation: " + str(initial_weights_value))
        self.__generation_move(brains, 0.5)
        updated_weights_value = sum(brains.on_get_source()
                                    .get_output_neurons().get_weights())

        self.log("Sum Ouput after generation: " + str(updated_weights_value))
        self.assertTrue(updated_weights_value > initial_weights_value)

    def test_genome_apply_empty(self):
        genome = app.FiniteLearner.Genome.empty()
        action = genome.apply_action(app.DinoScanner.Barrier(80, 80, 80))
        self.log("Genome apply empty action: " + str(action))
        self.assertGreater(action, 0)

    def test_neuron_effect_empty(self):
        neuron = app.FiniteLearner.Neuron.empty(app.Settings.INPUT_LAYER_NEURONS)
        effect = neuron.effect(np.random.normal(1, 1, app.Settings.INPUT_LAYER_NEURONS))
        self.log("Neuron effect empty action: " + str(effect))
        self.assertEqual(effect, 0)


if __name__ == "__main__":
    unittest.main()
