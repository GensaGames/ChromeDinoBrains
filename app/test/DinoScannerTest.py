from __future__ import print_function
import cv2  # .cv2 as cv2
import time
import unittest

import os
import app.Settings
import app.DinoScanner

IMG_FILE_1 = os.path.join(app.Settings.IMAGES_HD, "test_dino_run1.png")
IMG_FILE_2 = os.path.join(app.Settings.IMAGES_HD, "test_dino_run2.png")
IMG_FILE_4 = os.path.join(app.Settings.IMAGES_HD, "test_dino_run3.png")

CACTI_HOR_START, CACTI_HOR_END = (67, 135), (325, 135)
CACTI_VER_START, CACTI_VER_END = (299, 20), (299, 145)


# This test only for testing Scanner work and 4k Resolution monitor!
# To check correct behavior with Dino Scanner, you should add your screens above!
# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyUnresolvedReferences
class ScannerTest(unittest.TestCase):

    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        print("%s: %.3f ms" % (self.id(), time.time() - self.startTime))

    def log(self, msg):
        print(self.id() + ": " + msg)

    def test_horizontal_occurrence(self):
        barrier_point = app.DinoScanner\
            .find_horizontal_barriers(cv2.imread(IMG_FILE_1, 0),
                                      CACTI_HOR_START, CACTI_HOR_END)
        self.log("Barrier Point is: " + str(barrier_point))
        self.assertIsNotNone(barrier_point)

    def test_vertical_occurrence(self):
        barrier_point = app.DinoScanner \
            .find_vertical_barriers(cv2.imread(IMG_FILE_1, 0),
                                    CACTI_VER_START, CACTI_VER_END)
        self.log("Barrier Point is: " + str(barrier_point))
        self.assertIsNotNone(barrier_point)

    def test_horizontal_spread(self):
        image = cv2.imread(IMG_FILE_1, 0)
        barrier_point = app.DinoScanner \
            .find_horizontal_barriers(image, CACTI_HOR_START, CACTI_HOR_END)

        color_length = app.DinoScanner \
            .find_horizontal_spread(image, barrier_point, +1)
        self.log("Color length from: " + str(barrier_point)
                 + " to: " + str(color_length))
        self.assertIsNotNone(color_length)

    def test_vertical_spread(self):
        image = cv2.imread(IMG_FILE_1, 0)
        barrier_point = app.DinoScanner \
            .find_horizontal_barriers(image, CACTI_HOR_START, CACTI_HOR_END)

        color_length = app.DinoScanner \
            .find_vertical_spread(image, barrier_point, -1)
        self.log("Color length from: " + str(barrier_point)
                 + " to: " + str(color_length))
        self.assertIsNotNone(color_length)

    def test_cacti_barrier(self):
        barrier = app.DinoScanner \
            .find_cacti_barrier(cv2.imread(IMG_FILE_1, 0))

        self.log("Cacti barriers on image is: " + str(barrier))
        self.assertIsNotNone(barrier)

    def test_bird_barrier(self):
        barrier = app.DinoScanner \
            .find_bird_barrier(cv2.imread(IMG_FILE_2, 0), None)

        self.log("Bird 1 barriers on image is: " + str(barrier))
        self.assertIsNotNone(barrier)

    def test_game_end(self):
        game_end = app.DinoScanner \
            .check_end_game(cv2.imread(IMG_FILE_2, 0))

        self.log("Game End 1: " + str(game_end))
        self.assertFalse(game_end)

        game_end = app.DinoScanner \
            .check_end_game(cv2.imread(IMG_FILE_4, 0))

        self.log("Game End 2: " + str(game_end))
        self.assertTrue(game_end)

    def test_dino_height(self):
        dino_height1 = app.DinoScanner \
            .get_dino_height(cv2.imread(IMG_FILE_1, 0))

        self.log("Dino Height 1: " + str(dino_height1))
        self.assertIsNotNone(dino_height1)
        self.assertGreater(dino_height1, 0)

        dino_height2 = app.DinoScanner \
            .get_dino_height(cv2.imread(IMG_FILE_2, 0))
        self.log("Dino Height 2: " + str(dino_height2))
        self.assertNotEqual(dino_height1, dino_height2)


if __name__ == "__main__":
    unittest.main()
