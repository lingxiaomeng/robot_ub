#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
# take photo use piCamera
import color_detection

camera = PiCamera()
camera.resolution = (480, 320)
camera.framerate = 25
rawCapture = PiRGBArray(camera, size=(480, 320))
time.sleep(0.1)
num = 0
# read rgb_jpg file for test
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(color_detection.mtx, color_detection.dist, (w, h), 1, (w, h))
    dst = cv2.undistort(frame, color_detection.mtx, color_detection.dist, None, newcameramtx)
    x, y, w, h = roi
    frame = dst[y:y + h, x:x + w]
    cv2.imshow("frame", frame)
    k = cv2.waitKey(5)
    if k == 27:
        print(num)
        bal = color_detection.balanced(frame)
        cv2.imwrite('/home/pi/Desktop/test0816/' + str(num) + '.jpg', frame)
        cv2.imwrite('/home/pi/Desktop/test0816/' + str(num) + '_balanced.jpg', bal)

        num += 1

    rawCapture.truncate(0)
