import datetime

import cv2
import numpy as np
import collections

from app.Settings import DINO_WEB_CANVAS
from app.ScanSetting import SCANNER_SPEED_BUFFER, DINO_LOCATION_X, RETRY_BUTTON_X_Y, \
    PLAYABLE_AREA_Y, PLAYABLE_AREA_X, PLAYABLE_SEARCH_Y_RANGE, \
    PLAYABLE_NEARBY_X_RANGE, RETRY_BUTTON_SIZE


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
        # noinspection PyUnresolvedReferences
        return cv2.imdecode(image_base64, cv2.IMREAD_GRAYSCALE)

    def scan_new(self):
        image = self.__make_capture()
        barrier = resolve_barriers(image)

        self.speed.add_new_state(barrier)
        speed = self.speed.get_average()

        if barrier is None:
            barrier = Barrier(0, 0, 0)
        return Parameters(barrier, check_dino_height(image),
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
            return round(sum(self.speed_buffer) \
                   / len(self.speed_buffer), -1)
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
        return "Start at: " + str(self.start) + " Height: "\
               + str(self.height) + " Width: " + str(self.width)


###########################################################################
###########################################################################
# Main function resolving Barriers throw methods below, checking for invert
# color spread of color and moving to the closes same color point.
def resolve_barriers(image):
    barrier = None

    for y in range(PLAYABLE_AREA_Y[0], PLAYABLE_AREA_Y[1], PLAYABLE_SEARCH_Y_RANGE):
        last = find_horizontal_barriers(image, (PLAYABLE_AREA_X[0], y),
            (PLAYABLE_AREA_X[1], PLAYABLE_AREA_Y[1]))
        if last is not None:
            if barrier is None or last[0] < barrier[0]:
                barrier = last

    if barrier is None:
        return None

    main_start = move_closest(image, barrier, [1, 2, 3],
            lambda _x, _y: _x[0] < _y[0])[0]
    main_height = move_closest(image, barrier, [0, 1, 3],
            lambda _x, _y: _x[1] < _y[1])[1]

    # Searching nearby Barriers, which might be
    # connected to the first in Range of Min Nearby
    nearby = move_closest(image, barrier, [3, 0, 2],
            lambda _x, _y: _x[0] > _y[0])
    while True:
        last = find_horizontal_barriers(image, (nearby[0], nearby[1]),
                (nearby[0] + PLAYABLE_NEARBY_X_RANGE, nearby[1]))
        if last is not None:
            # Move again to the most nearby point!
            # And checking their connected Barriers
            nearby = move_closest(image, last, [3, 0, 2],
                    lambda _x, _y: _x[0] > _y[0])
        else:
            break

    main_width = nearby[0] - main_start
    return Barrier(main_start, main_height, main_width)


# Just check button location from Setting,
# and vertical/horizontal spread is Bigger then Bird.
def check_end_game(image):
    point = RETRY_BUTTON_X_Y
    background = int(image[0, 0])

    if int(image[point[1],
                 point[0]]) is background:
        return False

    return find_vertical_spread(image, point, +1)[1] - point[1] > RETRY_BUTTON_SIZE and \
           find_horizontal_spread(image, point, +1)[0] - point[0] > RETRY_BUTTON_SIZE


# Just check button location from Setting,
# and vertical/horizontal spread is Bigger then Bird.
def check_dino_height(image):
    start_p = (DINO_LOCATION_X, 0)
    barrier = find_vertical_barriers(image, start_p,
        (DINO_LOCATION_X, PLAYABLE_AREA_Y[1]))
    if barrier is None:
        return 0
    return barrier[1]


# Find object start point, based on any another point.
# Moving in direction, which is specified as list of
# top(0), left(1), bottom(2), right(3)
def move_closest(image, object_p, priority, predict):
    closest_p = object_p
    moving_p = object_p
    moving_d = -1

    while True:
        temp = list(priority)
        if moving_d in temp:
            temp.remove(moving_d)
        _d, _p = move_to_closest(image, moving_p, temp)
        if predict(_p, closest_p):
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
