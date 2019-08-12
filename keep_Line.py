#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cv2
import time
import color_detection
from picamera import PiCamera
import picamera
import Action
from picamera.array import PiRGBArray


def inline(result):
    print result
    result_angle = result['angle']
    if len(result_angle) > 0:
        angle = result_angle[0][0]
        if angle >= 0.07:
            Action.action('left_tiny', 1)
            print "turn left"
        elif angle <= -0.07:
            Action.action('right_tiny', 1)
            print "turn right"
        cx = result_angle[0][1]
        if cx >= 261.5:
            Action.action('rightDis', 1)
            print "turn left"
        elif cx <= 181.5:
            Action.action('leftDis', 1)
            print "turn right"


if __name__ == "__main__":
    camera = PiCamera()
    camera.resolution = (480, 320)
    camera.framerate = 25
    i = 0
    # rawCapture = PiRGBArray(camera, size=(480, 320))
    with picamera.array.PiRGBArray(camera, size=(480, 320)) as output:
        # --first  --------
        for frame in camera.capture_continuous(output, format="bgr", use_video_port=True):
            frame = frame.array
            i += 1
            # print frame
            if i % 5 == 0:
                result = color_detection.black_lines_detection(frame)
                inline(result)

            Action.action('for', 1)
            output.truncate(0)
