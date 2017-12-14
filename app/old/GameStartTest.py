import base64
import time
import unittest

import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import app.Settings

#  WARNING!
# ----------------------------------------
# This class is unused, and left here just
# as the reference to basic OpenCV work!
# ----------------------------------------

IMG_FILE_1 = os.path.join(app.Settings.IMAGES_QHD, "test-dino-idle.png")
IMG_FILE_2 = os.path.join(app.Settings.IMAGES_QHD, "test-dino-run1.png")
IMG_FILE_3 = os.path.join(app.Settings.IMAGES_QHD, "test-dino-run2.png")


# noinspection PyAttributeOutsideInit
class StartTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.startTime = time.time()

    def tearDown(self):
        self.driver.close()
        print "\n%s: %.3f ms" % (self.id(), time.time() - self.startTime)

    def test_check_dino_page(self):
        driver = self.driver
        driver.get("https://chromedino.com/")
        assert "T-Rex" in driver.title

    def test_check_dino_objects(self):
        driver = self.driver
        driver.get("https://chromedino.com/")

        canvas = driver.find_element_by_class_name("runner-canvas")
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
        with open(IMG_FILE_1, 'wb') as f:
            f.write(base64.b64decode(canvas_base64))
        assert canvas_base64 is not None

    def test_check_dino_objects_jump(self):
        driver = self.driver
        driver.get("https://chromedino.com/")
        driver.find_element_by_id("t").send_keys(Keys.ARROW_UP)

        time.sleep(4)
        driver.find_element_by_id("t").send_keys(Keys.ARROW_UP)
        canvas = driver.find_element_by_class_name("runner-canvas")
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
        with open(IMG_FILE_2, 'wb') as f:
            f.write(base64.b64decode(canvas_base64))
        assert canvas_base64 is not None

    def test_check_dino_objects_down(self):
        driver = self.driver
        driver.get("https://chromedino.com/")
        driver.find_element_by_id("t").send_keys(Keys.ARROW_UP)

        time.sleep(2)
        action_chains = ActionChains(driver)
        action_chains.key_down(Keys.ARROW_DOWN).perform()

        canvas = driver.find_element_by_class_name("runner-canvas")
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
        with open(IMG_FILE_3, 'wb') as f:
            f.write(base64.b64decode(canvas_base64))
        assert canvas_base64 is not None


if __name__ == "__main__":
    unittest.main()
