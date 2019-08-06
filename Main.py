#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2
import time
import color_detection
from picamera import PiCamera
import Action


def has_yellow(results_1):
    for color1, rects1 in results_1:
        if color1 == 'yellow' and len(rects1) >= 1:
            return True
    return False


def has_red(results_1):
    for color1, rects1 in results_1:
        if color1 == 'red' and len(rects1) >= 1:
            for rect1 in rects1:
                x = rect1[0]
                y = rect1[1]
                w = rect1[2]
                h = rect1[3]
                if h >= 312:
                    return 1
                elif h <= 100:
                    return 2
                else:
                    return 3
    return 0


camera = PiCamera()
camera.resolution = (320, 320)
camera.framerate = 25
# --first  --------
start = time.time()
flag = 0
while 1:
    forward = False
    camera.capture("tmp_frame.jpg")
    frame = cv2.imread("tmp_frame.jpg")
    results = color_detection.get_color(frame)
    if has_yellow(results):
        flag = 1
        print "find yellow"
    elif flag == 1:
        print "start forward"
        Action.action("for", 1)
        break
    else:
        print "find nothing"

    # print results
    end = time.time()
    if end - start >= 20:
        print "time out"
        break

# ---------------------------------------------------------------------
flag = 0
while 1:
    forward = False
    camera.capture("tmp_frame.jpg")
    frame = cv2.imread("tmp_frame.jpg")
    results = color_detection.get_color(frame)
    num = has_red(results)
    if num == 1 and flag == 0:
        print "find red start up stair"
        Action.action("for", 1)
        Action.action("up stair", 1)
        Action.action("left tiny", 1)
        flag = 1
        break
    elif num == 1 and flag == 1:
        print "find red forward"
    elif (num == 0 or num == 2) and flag == 0:
        Action.action("for", 1)
        print "not find red start forward"
    elif num == 3 and flag == 0:
        Action.action("for", 1)
        print "not find red start forward"
    elif num == 0 and flag == 1:
        print "not find red start down stair"
        flag = 2

Action.end()
