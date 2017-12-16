
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
# Main Image Side during scanning
IMAGE_SIZE = (600, 150)
# Speed buffer for calculation average
SCANNER_SPEED_BUFFER = 5
# Static Dino X location
DINO_STATIC_X_LOCATION = 53
# Retry button X1, Y1.
RETRY_BUTTON_POINT = (286, 79)

# Main working area for Dino barriers. X1, X2.
DINO_BARRIERS_X_POSITIONS = (67, 425)

# Starting Y Line for looking Cacti Starts
# Max spread for Cacti Branches
CACTI_SEARCH_START_AT_Y = 135
CACTI_MAX_BRANCH_WIDTH = 10

# Vertical position for looking Birds. Inverted Y1, Y2.
# BIRDS_PRIMARY_WIDTH = 85
BIRDS_BARRIERS_Y_POSITIONS = (125, 40)

# Just believe it's main body height of Bird
# Step to Search. Should be smaller then head!
BIRDS_SEARCH_BODY_HEIGHT = 16
BIRDS_SEARCH_Y_STEP = 10
