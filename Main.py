#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2
import time
import color_detection
from picamera import PiCamera
import Action


def find_green(results_1):
    for color1, rects1 in results_1:
        if color1 == 'green':
            maxw = 0
            index = 0
            for i in range(len(rects1)):
                if rects1[i][2] >= maxw:
                    index = i
            if rects1[index][2] >= 60:
                center = rects1[index][0] + rects1[index][2] / 2
                return center
    return -1


def inline(rect, block1):
    for i in range(len(block1)):
        r = block1[i]
        if abs(r[1] - rect[1]) < 5 or abs(r[1] - rect[1] + r[3] - rect[3]) < 5:
            return i
    return -1


def has_black(results_1):
    for color1, rects1 in results_1:
        if color1 == 'black':
            block = []
            for rect in rects1:
                line = inline(rect, block)
                if len(block) == 0 or line == -1:
                    block.append(rect)
                else:
                    block[line][2] += rect[2]
            print block
            for rect in block:
                if rect[2] >= 160:
                    return True
    return False


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
        # break
    elif num == 1 and flag == 1:
        print "find red forward"
        Action.action("for", 1)
    elif (num == 0 or num == 2) and flag == 0:
        Action.action("for", 1)
        print "not find red start forward"
    elif num == 3 and flag == 0:
        Action.action("for", 1)
        print "not find red start forward"
    elif num == 0 and flag == 1:
        print "not find red start down stair"
        Action.action("down_stair", 1)
        flag = 2
        break

flag = 0
while 1:
    forward = False
    camera.capture("tmp_frame.jpg")
    frame = cv2.imread("tmp_frame.jpg")
    results = color_detection.get_color(frame)
    has = has_black(results)
    if has:
        Action.action("left tiny", 1)
        Action.action("left tiny", 1)
        Action.action("left tiny", 1)
        print "turn left"
        break
    else:
        Action.action("for", 1)

flag = 0
while 1:
    forward = False
    camera.capture("tmp_frame.jpg")
    frame = cv2.imread("tmp_frame.jpg")
    results = color_detection.get_color(frame)
    cen = find_green(results)
    if cen != -1:
        if cen < 155:
            Action.action("right", 1)
        elif cen > 165:
            Action.action("left", 1)
        else:
            Action.action("for", 1)
            break
    else:
        Action.action("for", 1)

Action.end()
