# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 10:51:08 2019

@author: 11712
"""

# !/usr/bin/python
# _*_ coding:utf-8  -*-
import time

import RobotApi
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray

import color_detection

# ---------------------------------
up_stair = 0
on_green = 0
gouhe = 0
# ------------------------------------
RobotApi.ubtRobotInitialize()
# ---------------------------------
gIPAddr = ""
robotinfo = RobotApi.UBTEDU_ROBOTINFO_T()
robotinfo.acName = "Yanshee_65CE"
ret = RobotApi.ubtRobotDiscovery("SDK", 15, robotinfo)

if 0 != ret:
    print("Return value: %d" % ret)
    exit(1)
gIPAddr = robotinfo.acIPAddr
ret = RobotApi.ubtRobotConnect("SDK", "1", gIPAddr)
if 0 != ret:
    print("Can not connect to robot %s" % robotinfo.acNme)
    exit(1)


def find_max_area(color_rect_array):
    maxindex = 0
    max_area = 0
    i_index = 0
    for [_, _, _, _, area] in color_rect_array:
        if max_area <= area:
            max_area = area
            maxindex = i_index
        i_index += 1
    return color_rect_array[maxindex]


def in_green(result):
    # print result
    result_angle = result['angle']
    if len(result_angle) > 0:
        angle = result_angle[0][0]
        if angle >= 0.07:
            RobotApi.ubtStartRobotAction('left_tiny', 1)
            print "turn left"
        elif angle <= -0.07:
            RobotApi.ubtStartRobotAction('right_tiny', 1)
            print "turn right"
        cx = result_angle[0][1]
        if cx >= 261.5:
            RobotApi.ubtStartRobotAction('right_tiny', 1)
            print "turn left"
        elif cx <= 181.5:
            RobotApi.ubtStartRobotAction('left_tiny', 1)
            print "turn right"
        return -0.07 < angle < 0.07 and 181.5 <= cx <= 261.5


def inline(result):
    # print result
    result_angle = result['angle']
    if len(result_angle) > 0:
        angle = result_angle[0][0]
        if angle >= 0.07:
            RobotApi.ubtStartRobotAction('left_tiny', 1)
            print "turn left"
        elif angle <= -0.07:
            RobotApi.ubtStartRobotAction('right_tiny', 1)
            print "turn right"
        cx = result_angle[0][1]
        if cx >= 261.5:
            RobotApi.ubtStartRobotAction('right_tiny', 1)
            RobotApi.ubtStartRobotAction('rightDisTiny', 1)
            print "turn left"
        elif cx <= 181.5:
            RobotApi.ubtStartRobotAction('left_tiny', 1)
            RobotApi.ubtStartRobotAction('leftDisTiny', 1)
            print "turn right"
        return -0.07 < angle < 0.07 and 181.5 <= cx <= 261.5

        # ------------------------------------------------------


def find_max_color():
    return


def judge(frame):
    global up_stair, on_green, gouhe
    color_result = color_detection.get_color(frame)
    # 返回红、黄、绿
    red = color_result['red']
    green = color_result['green']
    yellow = color_result['yellow']
    if gouhe == 1:
        print "前面是沟壑"
        black_result = color_detection.black_lines(frame=frame)
        h_lines = black_result['h_lines']
        v_lines = black_result['v_lines']
        if len(h_lines) == 2:
            print "h_lines2"
        return

    if up_stair == 1:
        if len(red) > 0:
            print "在楼梯上"
            RobotApi.ubtStartRobotAction("first", 1)
            RobotApi.ubtStartRobotAction("for", 1)  # 待调
        else:
            print "no red"
            RobotApi.ubtStartRobotAction("down_stair", 1)
            up_stair = 2

        return

    if len(red) > 0 and up_stair == 0:
        maxred = find_max_area(red)

        if maxred[3] > 80 and up_stair == 0:
            if maxred[3] > 205:
                print "上楼梯"
                RobotApi.ubtStartRobotAction("for", 2)  # 待调a
                RobotApi.ubtStartRobotAction("up stair", 1)
                result = color_detection.red_lines(frame)
                inline(result)
                up_stair = 1
            else:
                print "no stair forward"
                ret = RobotApi.ubtStartRobotAction("for", 2)

    # 矫正方位
    if len(green) > 0 and on_green == 0:

        max_green = find_max_area(green)
        print max_green
        print "find green"
        green_lines = color_detection.green_lines(frame)
        if 150 >= max_green[1] + max_green[3] >= 0:
            print "go for green"
            # RobotApi.ubtStartRobotAction("vertical", 1)
            # while 矫正方位，矫正位置
            RobotApi.ubtStartRobotAction("first", 1)
            RobotApi.ubtStartRobotAction("for", 1)  # 待调
        elif 220 >= max_green[1] + max_green[3] > 150:
            print "调整"
            # while 矫正方位，矫正位置
            if inline(green_lines):
                RobotApi.ubtStartRobotAction("for", 1)  # 待调
        elif max_green[1] + max_green[3] > 220:
            print "上绿色"
            on_green = 1
            # while 矫正方位，矫正位置
            if in_green(green_lines):
                RobotApi.ubtStartRobotAction("for", 1)  # 待调
        return
    if on_green == 1:
        print "在绿色上"
        if len(green) > 0:
            # green_lines = color_detection.green_lines(frame)
            # if in_green(green_lines):
            RobotApi.ubtStartRobotAction("for", 1)  # 待调
        else:
            print "绿色完成"
            RobotApi.ubtStartRobotAction("for", 1)  # 待调
            on_green = 2
        return

    # if yellow[0][3] > 20:
    #     RobotApi.ubtStartRobotAction("vertical", 1)
    #     # 拐弯，调整位置
    #     while True:
    #         if yellow[0][3] > 150:
    #             RobotApi.ubtStartRobotAction("Left", 1)  # 左或者右
    #             break
    #         RobotApi.ubtStartRobotAction("first", 1)
    #         RobotApi.ubtStartRobotAction("for", 4)
    #         while True:
    #             if 1:  # 我也不知道怎么地
    #                 break
    #             RobotApi.ubtStartRobotAction("for", 1)
    #     while True:
    #         if yellow[0][2] < 300:
    #             RobotApi.ubtStartRobotAction("vertical", 1)
    #             RobotApi.ubtStartRobotAction("Right", 1)  # 左或者右
    #             # 矫正方位
    #             RobotApi.ubtStartRobotAction("rightDis", 5)  # 待调
    #             # 矫正方位
    #             break
    #         RobotApi.ubtStartRobotAction("rightDis", 5)
    #     return
    #

    # if color_detection.find_yellow(frame):
    #     RobotApi.ubtStartRobotAction("first", 1)
    #     RobotApi.ubtStartRobotAction("for", 10)  # 待调
    #     return
    black_result = color_detection.black_lines(frame=frame)
    h_lines = black_result['h_lines']
    v_lines = black_result['v_lines']
    if len(h_lines) == 1 and h_lines[0][0] <= 40:
        # RobotApi.ubtStartRobotAction("first", 1)
        RobotApi.ubtStartRobotAction("for", 1)
        print "发现横线"
        print h_lines
        return
    if len(h_lines) == 1 and h_lines[0][0] > 40 and len(v_lines) <= 1:
        RobotApi.ubtStartRobotAction("Left", 1)
        print h_lines

        print "左转"
        return
    if len(h_lines) == 2 and len(v_lines) >= 2 and gouhe == 0:
        print "沟壑"
        gouhe = 1
        return


        # RobotApi.ubtStartRobotAction("first", 1)
        # RobotApi.ubtStartRobotAction("for", 2)  # 待调
        # while True:
        #     if black_result['bot_point']:
        #         RobotApi.ubtStartRobotAction("vertical", 1)
        #         RobotApi.ubtStartRobotAction("cross", 1)
        #         break
        #     else:
        #         RobotApi.ubtStartRobotAction("for", 2)
        return
    inline(black_result)
    print black_result
    #
    # if 蓝色门:
    #     # 矫正方位、矫正位置
    #     RobotApi.ubtStartRobotAction("first", 1)
    #     RobotApi.ubtStartRobotAction("for", 5)  # 待调
    #     # 矫正方位、矫正位置
    #     return

    RobotApi.ubtStartRobotAction("first", 1)
    RobotApi.ubtStartRobotAction("for", 3)  # 待调
    # 矫正方位


if __name__ == "__main__":
    camera = PiCamera()
    camera.resolution = (480, 320)
    camera.framerate = 25
    flag = 0
    start = time.time()
    with picamera.array.PiRGBArray(camera, size=(480, 320)) as output:
        for frame in camera.capture_continuous(output, format="bgr", use_video_port=True):
            frame = frame.array

            if color_detection.find_yellow(frame):
                flag = 1
                print "find yellow"
            elif flag == 1:
                print "start forward"
                RobotApi.ubtStartRobotAction("first", 1)
                RobotApi.ubtStartRobotAction("for", 1)
                break
            else:
                print "find nothing"
            end = time.time()
            if end - start >= 20:
                print "time out"
                break
            output.truncate(0)

    print "pass first"
    i = 0
    with picamera.array.PiRGBArray(camera, size=(480, 320)) as output:
        for frame in camera.capture_continuous(output, format="bgr", use_video_port=True):
            frame = frame.array
            # frame = color_detection.balanced(frame)
            # color_detection.cv2.imshow('balanced', frame)
            # k = color_detection.cv2.waitKey(500)
            # if k == 27:
            #     break
            i += 1
            if i % 15 == 0:
                judge(frame=frame)
            output.truncate(0)

# ----------------------------------------------------------
    RobotApi.ubtRobotDisconnect("SDK", "1", gIPAddr)
    RobotApi.ubtRobotDeinitialize()
