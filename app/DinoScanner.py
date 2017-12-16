import datetime

import cv2
import numpy as np
import collections

from app.Settings import DINO_WEB_CANVAS
from app.ScanSetting import IMAGE_SIZE, SCANNER_SPEED_BUFFER, DINO_STATIC_X_LOCATION, RETRY_BUTTON_POINT,  \
    BIRDS_SEARCH_BODY_HEIGHT, BIRDS_SEARCH_Y_STEP, CACTI_SEARCH_START_AT_Y, CACTI_MAX_BRANCH_WIDTH, \
    DINO_BARRIERS_X_POSITIONS, BIRDS_BARRIERS_Y_POSITIONS


class Scanner:
    def __init__(self, web_driver):
        self.driver = web_driver
        self.canvas_element = self.driver \
            .find_element_by_class_name(DINO_WEB_CANVAS)
        self.speed = Speed()

    def __make_capture(self):
        canvas_byte_array = self.driver\
            .execute_script("return arguments[0].toDataURL('image/png').substring(21);",
                            self.canvas_element)
        image_base64 = np.fromstring(canvas_byte_array.decode('base64'), np.uint8)
        return cv2.imdecode(image_base64, cv2.IMREAD_GRAYSCALE)

    def scan(self):
        image = self.__make_capture()
        cacti = find_cacti_barrier(image)

        bird_search_start = None if cacti is None else cacti.get_start()
        bird = find_bird_barrier(image, bird_search_start)

        self.speed.add_new_state(cacti)
        speed = self.speed.get_average()

        barrier = bird if bird is not None else cacti
        if barrier is None:
            barrier = Barrier(0, 0, 0)

        return Parameters(barrier, get_dino_height(image),
                          speed, check_end_game(image))


class Speed:
    def __init__(self):
        self.speed_buffer = collections.deque(maxlen=SCANNER_SPEED_BUFFER)
        self.last_barrier_start, self.last_scan_time = None, None

    def add_new_state(self, barrier):
        if barrier is None:
            return

        if self.last_barrier_start is not None \
                or barrier.get_start() < self.last_barrier_start:
            dt_time = datetime.datetime.now() - self.last_scan_time

            speed = round((self.last_barrier_start - barrier.get_start())
                          / dt_time.total_seconds())
            self.speed_buffer.append(speed)

        self.last_barrier_start = barrier.get_start()
        self.last_scan_time = datetime.datetime.now()

    def get_average(self):
        if self.speed_buffer:
            return sum(self.speed_buffer) \
                   / len(self.speed_buffer)
        return 0


class Parameters:
    def __init__(self, barrier, dino_height, speed, end):
        self.barrier = barrier
        self.dino_height = dino_height
        self.speed = speed
        self.end = end

    def get_dino_height(self):
        return self.dino_height

    def get_barrier(self):
        return self.barrier

    def get_speed(self):
        return self.speed

    def is_end(self):
        return self.end

    def __str__(self):
        return "Barrier: " + str(self.barrier) + " Dino Height: " + str(self.dino_height) \
               + " Speed: " + str(self.speed) + " Game end: " + str(self.end)


class Barrier:
    def __init__(self, start, height, width):
        self.start = start
        self.height = height
        self.width = width

    def get_start(self):
        return self.start

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def __str__(self):
        return "Start at Y :" + str(self.start) + " Height: "\
               + str(self.height) + " Width: " + str(self.width)


#####################################################################################
# Main function for searching Cacti Barriers. This method doesn't search single barrier,
# but all Cacti in Range of Branches. Which staying nearby first barrier.
def find_cacti_barrier(image):
    working_start_p = (DINO_BARRIERS_X_POSITIONS[0], CACTI_SEARCH_START_AT_Y)
    working_end_p = (DINO_BARRIERS_X_POSITIONS[1], CACTI_SEARCH_START_AT_Y)

    barrier = find_horizontal_barriers(image, working_start_p, working_end_p)
    if barrier is None:
        return None

    # Searching nearby cacti, which might be connected to the first.
    height = find_vertical_spread(image, barrier, -1)[1]
    found_barriers = [barrier]
    while True:
        stem_width = find_horizontal_spread(image, barrier, +1)[0] - barrier[0]
        max_nearby_range = barrier[0] + stem_width + (CACTI_MAX_BRANCH_WIDTH * 2)
        barrier = find_horizontal_barriers(image, (barrier[0], working_start_p[1]),
                          (max_nearby_range, working_start_p[1]))
        if barrier is None:
            break
        found_barriers.append(barrier)
        nearby_height = find_vertical_spread(image, barrier, -1)[1]
        if nearby_height > height:
            height = nearby_height

    # Searching closes points from barriers. Most left and most right.
    start = find_closest_side(image, found_barriers[0], [1, 0], lambda _x, _y: _x < _y)[0]
    width = find_closest_side(image, found_barriers[-1], [3, 0], lambda _x, _y: _x > _y)[0] - start
    return Barrier(start, height, width)


# Main function for searching Birds.
def find_bird_barrier(image, max_x_range):
    if max_x_range is None:
        max_x_range = DINO_BARRIERS_X_POSITIONS[1]
    max_point = (max_x_range, BIRDS_BARRIERS_Y_POSITIONS[1])

    barrier = None
    for y in range(BIRDS_BARRIERS_Y_POSITIONS[0], BIRDS_BARRIERS_Y_POSITIONS[1],
                   -1 * BIRDS_SEARCH_Y_STEP):
        barrier = find_horizontal_barriers(image, (DINO_BARRIERS_X_POSITIONS[0], y), max_point)
        if barrier is not None:
            break
    if barrier is None:
        return None

    barrier = find_closest_side(image, barrier, [1, 0], lambda _x, _y: _x < _y)
    height = barrier[1] - BIRDS_SEARCH_BODY_HEIGHT
    # Looking for the Bird width, without legs!
    width = find_horizontal_spread(image, barrier, +1)[0] - barrier[0]
    return Barrier(barrier[0], height, width)


# Just check button location from Setting,
# and vertical/horizontal spread is Bigger then Bird.
def get_dino_height(image):
    start_p = (DINO_STATIC_X_LOCATION, 0)
    barrier = find_vertical_barriers(image, start_p,(DINO_STATIC_X_LOCATION,
                                                     IMAGE_SIZE[1]))
    if barrier is None:
        return 0
    return barrier[1]


# Just check button location from Setting,
# and vertical/horizontal spread is Bigger then Bird.
def check_end_game(image):
    button_point = RETRY_BUTTON_POINT
    background = int(image[0, 0])

    if int(image[button_point[1],
                 button_point[0]]) is background:
        return False

    return find_vertical_spread(image, button_point, +1)[1] - button_point[1] \
           > BIRDS_SEARCH_BODY_HEIGHT and \
           find_horizontal_spread(image, button_point, +1)[0] - button_point[0] \
           > BIRDS_SEARCH_BODY_HEIGHT


# Find object start point, based on any another point.
# Moving in direction, which is specified as list of
# top(0), left(1), bottom(2), right(3)
def find_closest_side(image, object_p, priority, predict):
    closest_p = object_p
    moving_p = object_p
    moving_d = -1

    while True:
        temp = list(priority)
        if moving_d in temp:
            temp.remove(moving_d)
        _d, _p = move_to_closest(image, moving_p, temp)
        if predict(_p[0], closest_p[0]):
            closest_p = _p

        if moving_p != _p:
            moving_p = _p
            moving_d = _d
        else:
            break
    return closest_p


# Move to closes point with same color, as start point.
# using priority from the method above.
def move_to_closest(image, point, priority):
    color = int(image[point[1], point[0]])
    for side in priority:
        _p = point

        if side == 0:
            _p = _p[0], _p[1] - 1
            if int(image[_p[1], _p[0]]) == color:
                return 2, _p
        if side == 1:
            _p = _p[0] - 1, _p[1]
            if int(image[_p[1], _p[0]]) == color:
                return 3, _p
        if side == 2:
            _p = _p[0], _p[1] + 1
            if int(image[_p[1], _p[0]]) == color:
                return 0, _p
        if side == 3:
            _p = _p[0] + 1, _p[1]
            if int(image[_p[1], _p[0]]) == color:
                return 1, _p
    return -1, point


def find_horizontal_barriers(image, start_p, end_p):
    background_c = int(image[0, 0])
    last_c = background_c

    for pix in range(start_p[0], end_p[0]):
        _c = int(image[start_p[1], pix])

        if _c is background_c:
            last_c = _c
            continue

        if last_c > _c:
            return pix, start_p[1]
        last_c = _c
    return None


def find_vertical_barriers(image, start_p, end_p):
    background_c = int(image[0, 0])
    last_c = background_c

    for pix in range(start_p[1], end_p[1]):
        _c = int(image[pix, start_p[0]])

        if _c is background_c:
            last_c = _c
            continue

        if last_c > _c:
            return start_p[0], pix
        last_c = _c
    return None


def find_horizontal_spread(image, start_p, step):
    looking_c = int(image[start_p[1], start_p[0]])
    move_p = start_p[0], start_p[1]

    try:
        while True:
            move_p = move_p[0] + step, move_p[1]
            _c = int(image[move_p[1], move_p[0]])
            if looking_c is not _c:
                return move_p

    except IndexError:
        return move_p[1], move_p[0] - step


def find_vertical_spread(image, start_p, step):
    looking_c = int(image[start_p[1], start_p[0]])
    move_p = start_p[0], start_p[1]

    try:
        while True:
            move_p = move_p[0], move_p[1] + step
            _c = int(image[move_p[1], move_p[0]])
            if looking_c is not _c:
                return move_p

    except IndexError:
        return move_p[1] - step, move_p[0]
