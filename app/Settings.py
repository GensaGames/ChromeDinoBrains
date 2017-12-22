import os
# noinspection PyCompatibility
import pathlib

########################################################
# Main Rules of the Game Scanner. It's every object separated with
# two colors, light and darker. This still unchanged during day/night builds.
# - Resolution 3860x2160 produce Image 1200x300
# - Resolution 1360x768 produce Image 600x150


########################################################
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_FOLDER = os.path.join(os.path.abspath(__file__), "../..")
IMAGES_QHD = os.path.join(PROJECT_FOLDER, "images_qhd")
IMAGES_HD = os.path.join(PROJECT_FOLDER, "images_hd")
TEMP_FOLDER = os.path.join(PROJECT_FOLDER, "temp")

# Dino Website game. To skipp offline mode and other restrictions.
# This site also useful, cause we work with Firefox.
DINO_WEBSITE_PATH = pathlib.Path(os.path.abspath(os.path
        .join(PROJECT_FOLDER, "chrome_game", "index.html"))).as_uri()
DINO_WEB_ELEMENT = "offline"
DINO_WEB_CANVAS = "runner-canvas"
SYSTEM_MAX_REC = 100000


########################################################
# Parameters and Schemes for the Finite Difference Learner

HIDDEN_LAYER_NEURONS = 8
LEARN_RATE = 0.3
LEARN_SIGMA = 1
NEARBY_SIGMA = 1
DINO_REWARD_PADDING = 5.5

########################################################
WORKING_JUMP_DELAY = 0.01
START_DELAY_PADDING = 1
JUMP_THRESHOLD = 0.8
