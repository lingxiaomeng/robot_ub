#!/usr/bin/env python
# coding=utf-8

'''
Brief : track deer for robot.  Ver : V1.0
Author : Sanson   Date : 2019/01/22
'''
from picamera.array import PiRGBArray
from picamera import PiCamera
from functools import partial

import cv2
import os
import time
import threading
import numpy as np
import multiprocessing as mp
from socket import *
import RobotApi as api

resX = 450
resY = 250

lower_red = np.array([160, 40, 40])
upper_red = np.array([179, 255, 255])
lower_green = np.array([30, 100, 100])
upper_green = np.array([80, 255, 255])
lower_blue = np.array([100, 100, 100])
upper_blue = np.array([125, 255, 255])
lower_yellow = np.array([20, 30, 30])
upper_yellow = np.array([70, 255, 255])
lower_purple = np.array([125, 50, 50])
upper_purple = np.array([150, 255, 255])

center_x = 0
center_y = 0
radius = 0
hold_flag = 0
sensor_status = 0

# Setup the camera
camera = PiCamera()
camera.resolution = (resX, resY)
camera.framerate = 30

# Use this as our output
rawCapture = PiRGBArray(camera, size=(resX, resY))

HOST = '127.0.0.1'
PORT = 20001
ADDR = (HOST, PORT)
udp_client = socket(AF_INET, SOCK_DGRAM)


class RobotMotion:
    def __init__(self):
        pass

    def holding_deer(self):
        # data = str("{\"cmd\":\"set\",\"type\":\"led\",\"para\":{\"type\":\"camera\",\"mode\":\"on\",\"color\":\"red\"}}")
        data = str("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"hold_deer\",\"repeat\":1 }}")
        udp_client.sendto(data, ADDR)
        time.sleep(8)

    def releas_deer(self):
        # data = str("{\"cmd\":\"set\",\"type\":\"led\",\"para\":{\"type\":\"camera\",\"mode\":\"on\",\"color\":\"red\"}}")
        data = str("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"releas_deer\",\"repeat\":1 }}")
        udp_client.sendto(data, ADDR)
        time.sleep(10)

    def forward_step(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"step_forward\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(2 * num)

    def backward_step(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"step_backward\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(2 * num)

    def left_step(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"step_left\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(num)

    def right_step(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"step_right\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(num)

    def turn_left_step(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"step_turn_left\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(num)

    def turn_right_step(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"step_turn_right\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(num)

    def reset(self, num):
        data_list = []
        data_list.append("{\"cmd\":\"action\",\"type\":\"start\",\"para\":{\"name\":\"reset\",\"repeat\":")
        data_list.append(str(num))
        data_list.append("}}")
        data = ''.join(data_list)
        udp_client.sendto(data, ADDR)
        time.sleep(1)


def get_circles(img):
    x = 0
    y = 0
    z = 0
    blurred = cv2.GaussianBlur(img, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_purple, upper_purple)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), z) = cv2.minEnclosingCircle(c)
    return int(x), int(y), int(z), img


def draw_frame(img, x, y, z):
    if (z > 15):
        cv2.circle(img, (x, y), z, (0, 255, 0), 5)
        print("circle_center is : ", x, y)
        print("radius is : ", z)
    cv2.imshow('deer_tracking', img)


def go_back():
    api.ubtStartRobotAction("step_turn_right", 4)
    time.sleep(1)
    api.ubtStartRobotAction("step_turn_right", 2)
    api.ubtStartRobotAction("reset", 1)
    api.ubtStartRobotAction("step_forward", 10)
    api.ubtStartRobotAction("step_turn_left", 1)
    api.ubtStartRobotAction("step_forward", 10)
    api.ubtStartRobotAction("step_turn_left", 1)
    api.ubtStartRobotAction("step_forward", 10)
    api.ubtStartRobotAction("reset", 1)
    time.sleep(1)


def walk_track(x, y, z):
    global hold_flag
    global sensor_status
    if (hold_flag == 0):
        if (sensor_status == 1):
            print "camera_track start"
            if z > 20 and z < 40:
                my_robot.forward_step(1)
            elif z > 40 and z < 150:
                if (x < 200):
                    print"ok left"
                    my_robot.left_step(1)
                    my_robot.reset(1)
                elif x > 200 and x < 260:
                    my_robot.forward_step(1)
                    # my_robot.reset(1)
                elif (x > 260):
                    print"ok right"
                    my_robot.right_step(1)
                    my_robot.reset(1)
            elif z > 150:
                api.ubtStartRobotAction("hold_deer_small", 1)
                time.sleep(1)
                api.ubtStartRobotAction("step_turn_right", 4)
                time.sleep(1)
                api.ubtStartRobotAction("move_slow", 15)
                time.sleep(1)
                api.ubtStartRobotAction("release_deer_slow", 1)
                time.sleep(2)
                go_back()
                hold_flag = 1
    else:
        print "all done!"


def camera_thread():
    global center_x, center_y, radius
    print "camera_thread run."

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        x, y, z, l = get_circles(image)
        center_x = x
        center_y = y
        radius = z
        draw_frame(l, x, y, z)
        time.sleep(0.5)
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    # When everything done, release the capture
    camera.release()
    cv2.destroyAllWindows()


def track_thread():
    global center_x, center_y, radius
    print "track_thread run."
    while True:
        walk_track(center_x, center_y, radius)
        time.sleep(0.5)


def sensor_thread():
    global sensor_status
    count = 0
    ultrasonic_sensor = api.UBTEDU_ROBOTULTRASONIC_SENSOR_T()
    while True:
        time.sleep(1)
        ret = api.ubtReadSensorValue("ultrasonic", ultrasonic_sensor, 4)
        if ret != 0:
            print("Can not read Sensor value. Error code: %d" % (ret))
        else:
            sensor_data = ultrasonic_sensor.iValue
            print("Read Ultrasonic Sensor Value: %d mm" % (ultrasonic_sensor.iValue))
            if sensor_data < 150:
                api.ubtSetRobotMotion("walk", "left", 3, 1)
                api.ubtStartRobotAction("reset", 1)
                api.ubtSetRobotMotion("walk", "left", 3, 1)
                api.ubtStartRobotAction("reset", 1)
                count += 1
            if sensor_data > 150:
                my_robot.forward_step(1)
            if sensor_data > 300 and count > 0:
                # api.ubtSetRobotMotion("walk", "front", 3,6)
                api.ubtStartRobotAction("step_forward", 6)
                api.ubtStartRobotAction("reset", 1)
                api.ubtStartRobotAction("step_turn_left", 1)
                api.ubtStartRobotAction("reset", 1)
                sensor_status = 1
                break


if __name__ == '__main__':
    my_robot = RobotMotion()
    my_robot.reset(1)
    time.sleep(6)
    api.ubtRobotInitialize()
    api.ubtRobotConnect("sdk", "1", "127.0.0.1")
    threads = []
    t1 = threading.Thread(target=camera_thread, args=())
    threads.append(t1)
    t2 = threading.Thread(target=track_thread, args=())
    threads.append(t2)
    t3 = threading.Thread(target=sensor_thread, args=())
    threads.append(t3)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    print "exit all task."
