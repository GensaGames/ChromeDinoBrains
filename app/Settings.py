import os
import pathlib

########################################################
# Main Rules of the game. It's every object separated with
# two colors, light and darker. This still unchanged during day/night builds.
# - Resolution 3860x2160 produce Image 1200x300
# - Resolution 1360x768 produce Image 600x150


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
# Brains Hyper Parameters and Schemes
DINO_REWARD_PADDING = 5.5
POPULATION_SIZE = 3
HIDDEN_LAYER_NEURONS = 8
LEARN_RATE = 0.5
LEARN_SIGMA = 1
NEARBY_SIGMA = 1
JUMP_THRESHOLD = 0.8
DINO_START_DELAY_PADDING = 1

###################################################
# Scanner Settings! List of items with possible improvements, which
# were skipped for now, to save performance.
# - CACTI. Skipper several pixels for cacti top height.
# - CACTI. Skipped Branch calculation for both sides.
# - CACTI. Skipped stem width calculation.
# - BIRD. Skipped calculation for the Width!
# - BIRD. Hardcoded Bird Height, since bird always static.
# - BIRD. Searching to the bird on Bird Head range!
# - OTHER. Game End checking hardcoded position.


# ################## HD Settings #######################
# Scanner General Settings
IMAGE_SIZE = (600, 150)
SCANNER_SPEED_BUFFER = 5

# Main star working area for Dino barriers
DINO_BARRIERS_STARTS_AT_X = 67
# Main end working area for Dino barriers
DINO_BARRIERS_ENDS_AT_X = 425
# Static Dino X location
DINO_STATIC_X_LOCATION = 53

# Retry button for checking end game
# top left corner should start on this location.
RETRY_BUTTON_POINT = (286, 79)

# Vertical position for looking birds
# BIRDS_PRIMARY_WIDTH = 85
BIRDS_BARRIER_START_AT_Y = 125
BIRDS_BARRIER_ENDS_AT_Y = 40
# Just believe it's main body height of Bird
BIRDS_SEARCH_BODY_HEIGHT = 16
# Step to Search. Should be smaller then head!
BIRDS_SEARCH_Y_STEP = 10

# Starting Y Line for looking Cacti Starts
CACTI_SEARCH_START_AT_Y = 135
# Max spread for Cacti Branches
CACTI_MAX_BRANCH_WIDTH = 10


# ################# QHD SETTINGS ####################
# # Scanner General Settings
# IMAGE_SIZE = (1200, 300)
# SCANNER_SPEED_BUFFER = 5
#
# # Main star working area for Dino barriers
# DINO_BARRIERS_STARTS_AT_X = 135
# # Main end working area for Dino barriers
# DINO_BARRIERS_ENDS_AT_X = 650
# # Static Dino X location
# DINO_STATIC_X_LOCATION = 105
#
# # Retry button for checking end game
# # top left corner should start on this location.
# RETRY_BUTTON_POINT = (572, 158)
#
# # Vertical position for looking birds
# # BIRDS_PRIMARY_WIDTH = 85
# BIRDS_BARRIER_START_AT_Y = 250
# BIRDS_BARRIER_ENDS_AT_Y = 120
# # Just believe it's main body height of Bird
# BIRDS_SEARCH_BODY_HEIGHT = 32
# # Step to Search. Should be smaller then head!
# BIRDS_SEARCH_Y_STEP = 18
#
# # Starting Y Line for looking Cacti Starts
# CACTI_SEARCH_START_AT_Y = 270
# # Max spread for Cacti Branches
# CACTI_MAX_BRANCH_WIDTH = 18
