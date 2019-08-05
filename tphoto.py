#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
# take photo use piCamera
camera = PiCamera()
camera.resolution = (320, 320)
camera.framerate = 25
rawCapture = PiRGBArray(camera, size=(320, 320))
time.sleep(0.1)
num = 0
# read rgb_jpg file for test
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    cv2.imshow("frame", frame)
    k = cv2.waitKey(5)
    if k == 27:
        print(num)
        cv2.imwrite('/home/pi/Desktop/photo/' + str(num) + '.jpg', frame)
        num += 1

    rawCapture.truncate(0)
