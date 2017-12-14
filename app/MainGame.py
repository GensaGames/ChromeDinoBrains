import sys
import getopt
import pickle
import os
import time

import datetime
import psutil
import jsonpickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from app import Settings, DinoScanner
from app.Abstract import OnActionCallback
from app.FiniteLearner import FiniteLearner

from app.Settings import DINO_WEB_ELEMENT, DINO_WEBSITE_PATH, DINO_START_DELAY_PADDING, \
    JUMP_THRESHOLD, SYSTEM_MAX_REC, TEMP_FOLDER


###########################################################
class DinoGame(OnActionCallback):

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get(DINO_WEBSITE_PATH)
        self.element = self.driver \
            .find_element_by_class_name(DINO_WEB_ELEMENT)

        self.learner = FiniteLearner(self)
        self.source, self.scanner = None, None

    def load_generation(self, source):
        if source is None:
            return
        file_obj = open(source, 'rb')
        source_object = jsonpickle.decode(file_obj.read())
        file_obj.close()

        self.learner.on_load_source(source_object)
        self.source = source

    def __save_generation(self):
        if self.source is None:
            self.source = os.path.join(Settings.TEMP_FOLDER,
                    self.learner.__class__.__name__)
        file_obj = open(self.source, 'wb')
        frozen = jsonpickle.encode(self.learner.on_get_source())
        print(frozen)
        file_obj.write(frozen)
        file_obj.close()

    def relaunch(self):
        time.sleep(DINO_START_DELAY_PADDING)
        self.scanner = DinoScanner.Scanner(self.driver)
        self.element.send_keys(Keys.ARROW_UP)

        time.sleep(DINO_START_DELAY_PADDING)
        self.learner.on_start()
        self.__continue_game()

    def __continue_game(self):
        while True:
            scan_object = self.scanner.scan()
            # --------------------------------------
            # Uncomment below statement to check FPS
            # time_to_scan = datetime.datetime.now()
            if scan_object.is_end():
                self.__save_generation()
                self.relaunch()
                return
            self.learner.on_receive(scan_object)
            # print(str((datetime.datetime.now()
            #       - time_to_scan).total_seconds()))

    def on_action(self, value):
        if value > JUMP_THRESHOLD:
            self.element.send_keys(Keys.ARROW_UP)


###########################################################
def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'h:s:', ['help', 'source'])
    except getopt.GetoptError:
        sys.exit(2)
    gen_source = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print("Run Script with own source -s (--source) and path to the new "
                  "Resource, which will be saved, or using previous trained. ")
            sys.exit()
        if opt in ('-s', '--source'):
            gen_source = arg

    sys.setrecursionlimit(SYSTEM_MAX_REC)
    process = psutil.Process(os.getpid())
    process.nice(psutil.HIGH_PRIORITY_CLASS)

    game = DinoGame()
    if gen_source is None:
        files = os.listdir(TEMP_FOLDER)
        gen_source = None if not files else \
            os.path.join(TEMP_FOLDER, files[0])
    game.load_generation(gen_source)
    game.relaunch()


if __name__ == "__main__":
    main(sys.argv)
