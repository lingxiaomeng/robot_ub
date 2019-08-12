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
        angle = result_angle[0]
        if angle >= 0.07:
            Action.action('left_tiny', 1)
            print "turn left"
        elif angle <= -0.07:
            Action.action('right_tiny', 1)
            print "turn right"
        else:
            Action.action('for', 1)
            print "forward"
        cx =result_angle[1]


if __name__ == "__main__":
    camera = PiCamera()
    camera.resolution = (480, 320)
    camera.framerate = 10
    # rawCapture = PiRGBArray(camera, size=(480, 320))
    with picamera.array.PiRGBArray(camera, size=(480, 320)) as output:
        # --first  --------
        for frame in camera.capture_continuous(output, format="bgr", use_video_port=True):
            frame = frame.array
            # print frame
            result = color_detection.black_lines_detection(frame)
            inline(result)
            output.truncate(0)
