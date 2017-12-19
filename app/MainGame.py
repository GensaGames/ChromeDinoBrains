import sys
import getopt
import os
import time

# noinspection PyUnresolvedReferences
import datetime

import psutil
import jsonpickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from app import Settings, DinoScanner
from app.Abstract import OnActionCallback
from app.FiniteLearner import FiniteLearner

from app.Settings import DINO_WEB_ELEMENT, DINO_WEBSITE_PATH, \
    DINO_START_DELAY_PADDING, JUMP_THRESHOLD, SYSTEM_MAX_REC


###########################################################
class DinoGame(OnActionCallback):

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get(DINO_WEBSITE_PATH)

        self.element = self.driver \
            .find_element_by_class_name(DINO_WEB_ELEMENT)
        self.source, self.scanner, self.learner = None, None, None

    def load_generation(self, source, population):
        self.learner = FiniteLearner(self, population)
        if source is None or \
                not os.path.isfile(source):
            return

        file_obj = open(source, 'rb')
        source_object = jsonpickle.decode(file_obj.read())
        file_obj.close()

        self.learner.on_load_source(source_object)
        self.source = source

    def __save_generation(self):
        if self.source is None:
            self.source = os.path.join(Settings.TEMP_FOLDER,
                    "." + self.learner.__class__.__name__)
        file_obj = open(self.source, 'wb')
        frozen = jsonpickle.encode(self.learner.on_get_source())
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
            scan_object = self.scanner.scan_new()
            # --------------------------------------
            # Uncomment below statement to check FPS
            # time_to_scan = datetime.datetime.now()
            if scan_object.is_end():
                self.__save_generation()
                self.relaunch()
                return

            barrier = scan_object.get_barrier()
            params = [barrier.get_start(), barrier.get_height(), barrier.get_width(),
                      scan_object.get_dino_height(), scan_object.get_speed()]
            self.learner.on_receive(params)
            # --------------------------------------
            # print(str((datetime.datetime.now()
            #       - time_to_scan).total_seconds()))

    def on_action(self, value):
        if value > JUMP_THRESHOLD:
            self.element.send_keys(Keys.ARROW_UP)


###########################################################
def main(argv):
    try:
        opts, args = getopt.getopt(argv, 's:p:', ['source=', 'population='])
    except getopt.GetoptError:
        sys.exit(2)

    source, population = None, None
    for opt, arg in opts:
        if opt in ('-s', '--source'):
            source = arg
        if opt in ('-p', '--population'):
            population = int(arg)

    sys.setrecursionlimit(SYSTEM_MAX_REC)
    process = psutil.Process(os.getpid())
    process.nice(psutil.HIGH_PRIORITY_CLASS)

    game = DinoGame()
    game.load_generation(source, population)
    game.relaunch()


if __name__ == "__main__":
    main(sys.argv[1:])
