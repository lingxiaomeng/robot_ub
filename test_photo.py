# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 10:51:08 2019

@author: 11712
"""

# !/usr/bin/python
# _*_ coding:utf-8  -*-

import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray

import color_detection

if __name__ == "__main__":
    if __name__ == "__main__":
        camera = PiCamera()
        camera.resolution = (480, 320)
        camera.framerate = 25
        flag = 0
        i = 0
        with picamera.array.PiRGBArray(camera, size=(480, 320)) as output:
            for frame in camera.capture_continuous(output, format="bgr", use_video_port=True):
                frame = frame.array
                frame = color_detection.balanced(frame)
                color=color_detection.get_color(frame)

                blacklines = color_detection.yellow_lines(frame)
                print blacklines['v_lines']

                print color
                color_detection.cv2.imshow('balanced', frame)
                k = color_detection.cv2.waitKey(500)
                if k == 27:
                    color_detection.cv2.imwrite('yellow_gou.jpg',frame)

                i += 1
                # if i % 15 == 0:
                #     # res = color_detection.black_lines(frame)
                #     # print "h_lines:" + str(res['h_lines'])
                #     res = color_detection.yellow_lines(frame)
                #     print res

                output.truncate(0)

