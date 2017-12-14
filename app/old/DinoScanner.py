from __future__ import print_function
from __future__ import print_function
from __future__ import division

import datetime
import os

import cv2
import numpy as np
from app import Settings

#  WARNING!
# ----------------------------------------
# This class is unused, and left here just
# as the reference to basic OpenCV work!
# ----------------------------------------


# noinspection PyMethodMayBeStatic
class DinoGameScanner:
    def __init__(self, web_driver):
        self.driver = web_driver
        self.dino_image = cv2.imread(os.path.join(Settings.SOURCE_FOLDER, "dino-image-1.png"))
        self.dino_height, self.dino_width = self.dino_image.shape[:-1]

        self.last_dino_barriers = None
        self.last_dino_speed = None
        self.scan_start_time = None
        pass

    def make_capture__(self):
        canvas = self.driver.find_element_by_class_name("runner-canvas")
        canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL"
                                                   "('image/png').substring(21);", canvas)
        numpy_src = np.fromstring(canvas_base64.decode('base64'), np.uint8)
        return cv2.imdecode(numpy_src, cv2.COLOR_BGR2GRAY)

    # Finding only dino object based on Template.
    # This might be optimized later with searching by contours

    def find_dino__(self, cv2_image):
        result = cv2.matchTemplate(cv2_image.astype(np.uint8), self.dino_image, cv2.TM_CCOEFF)
        _, _, _, dino_top_left = cv2.minMaxLoc(result)
        dino_bottom_right = (dino_top_left[0] + self.dino_width, dino_top_left[1] + self.dino_height)
        return GenericGameObject(dino_top_left, dino_bottom_right)

    # Find other Barrier Objects, based on position, and except
    # that, which behind Dino location. Use Dino position.
    def find_dino_barriers__(self, cv2_image, dino_object):
        img_fil = cv2.medianBlur(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY), 13)
        img_th = cv2.adaptiveThreshold(img_fil, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        im2, contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        objects = []
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            if y < Settings.DINO_WORKING_Y_AREA[0] \
                    or y > Settings.DINO_WORKING_Y_AREA[1]:
                continue
            if x <= dino_object.top_right_point[0]\
                    and y <= dino_object.top_right_point[1]:
                continue
            objects.append(GenericGameObject((x, y), (x + w, y + h)))

        return objects

    # Check the speed using previous saved value 'Dino Barriers'
    # Which return Pixels per Second. And take average with previous.
    def calculate_speed__(self, new_barriers, previous_barriers, last_known_speed,
                          time_from_last_scan):
        if previous_barriers is None\
                or new_barriers is None:
            return

        difference = None
        for i, j in ((i, j) for i in new_barriers for j in previous_barriers):
            if i.check_same(j):
                difference = j.bottom_left_point[0] - i.bottom_left_point[0]
                break

        if difference is None\
                or difference <= 0:
            return

        new_speed = float(difference) / time_from_last_scan.total_seconds()
        if last_known_speed is not None:
            new_speed = (last_known_speed + new_speed) / 2

        return round(new_speed, -1)

    # --------------------------------------------------------
    # Call this function to resolve all required Data!
    # --------------------------------------------------------
    def scan(self):
        image = self.make_capture__()

        time_from_last_scan = 0
        time_now = datetime.datetime.now()
        if self.scan_start_time is not None:
            time_from_last_scan = time_now - self.scan_start_time
        self.scan_start_time = time_now

        dino = self.find_dino__(image)
        last_barriers = self.last_dino_barriers
        barriers = self.find_dino_barriers__(image, dino)
        self.last_dino_barriers = barriers

        last_known_speed = self.last_dino_speed
        speed = self.calculate_speed__(barriers, last_barriers, last_known_speed,
                                       time_from_last_scan)
        self.last_dino_speed = speed
        return dino, barriers, speed


class GenericGameObject:

    # Check only Y position of objects, to compare. Sometimes we can get conflict,
    # cause object moving by X, and we should get first occurrence.
    def check_same(self, other):
        return self.height == other.height and \
               self.width == other.width

    @property
    def height(self):
        return self._top_right_p[1] - self._bot_left_p[1]

    @property
    def width(self):
        return self._top_right_p[0] - self._bot_left_p[0]

    @property
    def bottom_left_point(self):
        return self._bot_left_p

    @property
    def top_right_point(self):
        return self._top_right_p

    def __init__(self, bottom_left_p, top_right_p):
        self._bot_left_p = bottom_left_p
        self._top_right_p = top_right_p
        pass
