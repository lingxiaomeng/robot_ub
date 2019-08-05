#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cv2
import numpy as np

# define HSV color value
red_min = np.array([0, 128, 46])
red_max = np.array([5, 255, 255])
red2_min = np.array([156, 128, 46])
red2_max = np.array([180, 255, 255])
green_min = np.array([35, 128, 46])
green_max = np.array([77, 255, 255])
blue_min = np.array([100, 128, 46])
blue_max = np.array([124, 255, 255])
yellow_min = np.array([15, 128, 46])
yellow_max = np.array([34, 255, 255])
black_min = np.array([0, 0, 0])
black_max = np.array([180, 255, 10])
white_min = np.array([0, 0, 70])
white_max = np.array([180, 30, 255])

COLOR_ARRAY = [[red_min, red_max, 'red'], [red2_min, red2_max, 'red'], [green_min, green_max, 'green'],
               [blue_min, blue_max, 'blue'], [yellow_min, yellow_max, 'yellow']]
print(cv2.__version__)


def getcolor(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    result = []
    for (color_min, color_max, name) in COLOR_ARRAY:
        mask = cv2.inRange(hsv, color_min, color_max)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        blured = cv2.blur(res, (5, 5))
        ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)
        gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
        opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        _, contours, hierarchy = cv2.findContours(closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(res, contours, -1, (0, 0, 255), 3)
        number = len(contours)
        sub_results = []
        rects_results = []
        if number >= 1:
            for i in range(0, number):
                x, y, w, h = cv2.boundingRect(contours[i])
                cv2.rectangle(res, (x, y), (x + w, y + h), (0, 255, 0), 2)
                rects_results.append([x, y, w, h])
            cv2.imwrite("result.jpg", res)
            sub_results.append(name)
            sub_results.append(rects_results)
            result.append(sub_results)
    return result
