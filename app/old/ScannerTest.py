import time
import unittest

import cv2
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import app
import app.Settings
from app.DinoScanner import Scanner

IMG_FILE_2 = os.path.join(app.Settings.IMAGES_QHD, "test-dino-run1.png")
IMG_FILE_3 = os.path.join(app.Settings.IMAGES_QHD, "test-dino-run2.png")
IMG_DINO = os.path.join(app.Settings.SOURCE_FOLDER, "dino-image-1.png")

#  WARNING!
# ----------------------------------------
# This class is unused, and left here just
# as the reference to basic OpenCV work!
# ----------------------------------------


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit
class ScannerTest(unittest.TestCase):

    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        print "\n%s: %.3f ms" % (self.id(), time.time() - self.startTime)

    @unittest.skip("Nothing new here.")
    def test_resolve_dino_image_1(self):
        test_image = cv2.imread(IMG_FILE_2)
        template = cv2.imread(IMG_DINO)

        result = cv2.matchTemplate(test_image, template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        h, w = template.shape[:-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(test_image, top_left, bottom_right, (0, 0, 255), 4)

        # Show result
        cv2.imshow("", test_image)
        cv2.waitKey(0)

        assert result is not None

    @unittest.skip("Nothing new here.")
    def test_resolve_dino_image_2(self):
        test_image = cv2.imread(IMG_FILE_3)
        template = cv2.imread(IMG_DINO)

        result = cv2.matchTemplate(test_image, template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        h, w = template.shape[:-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(test_image, top_left, bottom_right, (0, 0, 255), 4)

        # Show result
        cv2.imshow("", test_image)
        cv2.waitKey(0)

        assert result is not None

    @unittest.skip("Nothing new here.")
    def test_objects_contours(self):
        img_fil = cv2.medianBlur(cv2.imread(IMG_FILE_2, 0), 13)
        img_th = cv2.adaptiveThreshold(img_fil, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        im2, contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow('image', img_th)
        cv2.waitKey(0)

        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            print x, y, w, h
            cv2.rectangle(img_th, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow('image', img_th)
        cv2.waitKey(0)

    def test_game_scanner(self):
        driver = webdriver.Firefox()
        driver.get("https://chromedino.com/")
        driver.find_element_by_id("t").send_keys(Keys.ARROW_UP)
        time.sleep(1)
        game_scanner = Scanner(driver)

        image = game_scanner.__make_capture()
        dino_object = game_scanner.find_dino__(image)
        cv2.rectangle(image, dino_object.bottom_left_point, dino_object.top_right_point, (0, 0, 255), 4)
        cv2.imshow('image', image)
        cv2.waitKey(0)
        time.sleep(3)

        image = game_scanner.__make_capture()
        barrier_objects = game_scanner.find_dino_barriers__(image, dino_object)
        for i in barrier_objects:
            cv2.rectangle(image, i.bottom_left_point, i.top_right_point, (0, 0, 255), 4)

        cv2.imshow('image', image)
        cv2.waitKey(0)


if __name__ == "__main__":
    unittest.main()