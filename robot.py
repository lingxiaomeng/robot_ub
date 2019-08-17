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
on_blue = 0
on_yellow = 0
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


def find_near_lines(lines):
    # print lines
    maxindex = 0
    min_rho = 500
    i_index = 0
    for line_ in lines:
        if line_[0] <= min_rho:
            min_rho = line_[0]
            maxindex = i_index
        i_index += 1
    return lines[maxindex]

def find_fast_lines(lines):
    # print lines
    maxindex = 0
    max_rho = 0
    i_index = 0
    for line_ in lines:
        if line_[0] <= max_rho:
            max_rho = line_[0]
            maxindex = i_index
        i_index += 1
    return lines[maxindex]


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
            print "turn left tiny"
            RobotApi.ubtStartRobotAction('left_tiny', 1)
            RobotApi.ubtStartRobotAction('first', 1)

        elif angle <= -0.07:
            print "turn right tiny"
            RobotApi.ubtStartRobotAction('right_tiny', 1)
            RobotApi.ubtStartRobotAction('first', 1)

        cx = result_angle[0][1]
        if cx >= 261.5:
            print "turn right tiny dis"
            RobotApi.ubtStartRobotAction('right_tiny', 1)
            RobotApi.ubtStartRobotAction('first', 1)

            # RobotApi.ubtStartRobotAction('right_tiny', 1)
        elif cx <= 181.5:
            print "turn left tiny dis"
            RobotApi.ubtStartRobotAction('left_tiny', 1)
            RobotApi.ubtStartRobotAction('first', 1)

            # RobotApi.ubtStartRobotAction('left_tiny', 1)

        return -0.07 <= angle <= 0.07 and 181.5 <= cx <= 261.5


def inline(result):
    # print result
    result_angle = result['angle']
    if len(result_angle) > 0:
        angle = result_angle[0][0]
        if angle >= 0.07:
            print "turn left tiny"

            RobotApi.ubtStartRobotAction('left_tiny', 1)
            RobotApi.ubtStartRobotAction("first", 1)  # 待调

        elif angle <= -0.07:
            print "turn right tiny"

            RobotApi.ubtStartRobotAction('right_tiny', 1)
            RobotApi.ubtStartRobotAction("first", 1)  # 待调

        cx = result_angle[0][1]
        if cx >= 261.5:
            print "turn right dis"
            RobotApi.ubtStartRobotAction('rightDis', 1)
            RobotApi.ubtStartRobotAction("first", 1)  # 待调

            # RobotApi.ubtStartRobotAction('right_tiny', 1)
        elif cx <= 181.5:
            print "turn left dis"
            RobotApi.ubtStartRobotAction('leftDis', 1)
            RobotApi.ubtStartRobotAction("first", 1)  # 待调

            # RobotApi.ubtStartRobotAction('left_tiny', 1)
        return -0.07 <= angle <= 0.07 and 181.5 <= cx <= 261.5
        # ------------------------------------------------------


def find_max_color():
    return


def judge(frame):
    global up_stair, on_green, gouhe, on_blue, on_yellow
    color_result = color_detection.get_color(frame)
    # 返回红、黄、绿
    red = color_result['red']
    green = color_result['green']
    yellow = color_result['yellow']
    blue = color_result['blue']

    if on_yellow == 1:
        print "rejust yellow"
        yellow_lines = color_detection.yellow_lines(frame)
#192 0.13
        y_v_line = yellow_lines['v_lines']
        if len(y_v_line) > 0:
            fast_line = find_near_lines(y_v_line)
            (y_rho, y_theta) = fast_line
            on_yellow = 1
            if y_theta > 0.2:
                print "黄色角度偏大"
                RobotApi.ubtStartRobotAction("right_tiny", 1)
            elif y_theta < 0.03:
                print "黄色角度偏小"
                RobotApi.ubtStartRobotAction("left_tiny", 1)
            else:
                if y_rho < 175:
                    print "黄色r偏小"
                    RobotApi.ubtStartRobotAction("leftDisTiny", 1)
                elif y_rho > 210:
                    print "黄色r偏大"
                    RobotApi.ubtStartRobotAction("rightDisTiny", 1)
                else:
                    print "yellow 中"
                    RobotApi.ubtStartRobotAction("for", 5)
        else:
            print "黄色没有v_lines"
            RobotApi.ubtStartRobotAction("for", 1)
            on_yellow=2

        return
    if gouhe == 1:
        print "前面是沟壑"
        black_result = color_detection.black_lines(frame=frame)
        h_lines = black_result['h_lines']
        v_lines = black_result['v_lines']

        if len(h_lines) == 2:
            cr = (h_lines[0][0] + h_lines[1][0]) / 2
            if cr >= 195:
                print "go"
                RobotApi.ubtStartRobotAction("cross", 1)
                gouhe = 0
            else:
                print "for gou he"
                RobotApi.ubtStartRobotAction("for", 1)
        elif len(h_lines) == 3:
            cr = (h_lines[0][0] + h_lines[1][0]) + h_lines[2][0] / 3
            if cr >= 195:
                print "go"
                RobotApi.ubtStartRobotAction("cross", 1)
                gouhe = 0
            else:
                print "for gou he"
                RobotApi.ubtStartRobotAction("for", 1)
        elif len(h_lines) ==0 and h_lines[0][0]>=190:
            RobotApi.ubtStartRobotAction("cross", 1)
        else:
            print "no enough v_lines"
            RobotApi.ubtStartRobotAction("for", 1)

        return

    if up_stair == 1:
        if len(red) > 0:
            red_max = find_max_area(red)
            cx = red_max[0] + red_max[2] / 2
            if cx < 150 and red_max[3] > 40:
                pass
                # RobotApi.ubtStartRobotAction("leftDisTiny", 1)  # 待调
            elif cx > 290 and red_max[3] > 40:
                pass
                # RobotApi.ubtStartRobotAction("rightDisTiny", 1)  # 待调
            if red_max[1] <= 220:
                print "在楼梯上"

                # if inline(res):
                RobotApi.ubtStartRobotAction("for", 1)  # 待调
            else:
                print "red <20"
                RobotApi.ubtStartRobotAction("down stair", 1)
                RobotApi.ubtStartRobotAction("first", 1)
                up_stair = 2

        else:
            print "no red"
            RobotApi.ubtStartRobotAction("down stair", 1)
            RobotApi.ubtStartRobotAction("first", 1)
            up_stair = 2

        return

    if len(red) > 0 and up_stair == 0:
        maxred = find_max_area(red)

        if maxred[3] > 80 and up_stair == 0:
            if maxred[1] + maxred[3] >= 225:
                print "上楼梯"
                RobotApi.ubtStartRobotAction("for", 1)  # 待调a
                RobotApi.ubtStartRobotAction("for", 1)  # 待调a
                RobotApi.ubtStartRobotAction("up stair", 1)
                RobotApi.ubtStartRobotAction("right_tiny", 1)  # 待调

                RobotApi.ubtStartRobotAction("first", 1)  # 待调

                RobotApi.ubtStartRobotAction("for", 10)  # 待调

                # result = color_detection.red_lines(frame)
                # inline(result)
                up_stair = 1
            else:
                print "no stair forward"
                RobotApi.ubtStartRobotAction("for", 1)
                RobotApi.ubtStartRobotAction("for", 1)
        else:
            print "红色不足"
            RobotApi.ubtStartRobotAction("for", 1)

        return
    if len(blue) > 0 and on_blue == 0:
        max_blue = find_max_area(blue)
        if max_blue[2] >= 400:
            print "blue"
            RobotApi.ubtStartRobotAction("for", 1)
            RobotApi.ubtStartRobotAction("for", 1)
            on_blue = 1
        else:
            print "蓝色不足"
            RobotApi.ubtStartRobotAction("for", 1)
        return

    if on_blue == 1:
        print "面前蓝色"
        max_blue = find_max_area(blue)
        if max_blue[1] + max_blue[3] >= 180:
            print "kua guo"
            RobotApi.ubtStartRobotAction("for", 1)
            RobotApi.ubtStartRobotAction("claiming", 1)
            RobotApi.ubtStartRobotAction("first", 1)

            on_blue = 2
        else:
            print "gou he 蓝色不足"
            RobotApi.ubtStartRobotAction("for", 1)

        return

    if len(yellow) > 0 and on_yellow == 0:
        # 263.5 -0.06
        max_yellow = find_max_area(yellow)
        if max_yellow[3]+max_yellow[1] >= 220:
            print "rejust yellow"
            yellow_lines = color_detection.yellow_lines(frame)
            y_v_line = yellow_lines['v_lines']
            if len(y_v_line) > 0:
                fast_line = find_fast_lines(y_v_line)
                (y_rho, y_theta) = fast_line
                if y_rho < 175:
                    print "黄色r偏小"
                    RobotApi.ubtStartRobotAction("leftDisTiny", 1)
                elif y_rho > 210:
                    print "黄色r偏大"
                    RobotApi.ubtStartRobotAction("rightDisTiny", 1)
                else:
                    print "yellow 中"
                    on_yellow = 1
                    RobotApi.ubtStartRobotAction("first", 1)
                    RobotApi.ubtStartRobotAction("for", 4)
            else:
                print "no yellow lines"
                RobotApi.ubtStartRobotAction("for", 1)
        # elif max_yellow[3] >= 180:
        #     print "yellow right"
        #     RobotApi.ubtStartRobotAction("for", 1)
        #     # RobotApi.ubtStartRobotAction("rightDisTiny", 1)
        else:
            print "go for yellow"
            RobotApi.ubtStartRobotAction("for", 1)
        return

    # 矫正方位
    if len(green) > 0 and on_green == 0:

        max_green = find_max_area(green)
        print max_green
        print "find green"
        green_lines = color_detection.green_lines(frame)
        if 140 >= max_green[1] + max_green[3] >= 0:
            print "go for green"
            # RobotApi.ubtStartRobotAction("vertical", 1)
            # while 矫正方位，矫正位置
            # RobotApi.ubtStartRobotAction("first", 1)
            RobotApi.ubtStartRobotAction("for", 1)  # 待调
        elif 220 >= max_green[1] + max_green[3] > 140:
            print "调整"
            print green_lines
            # while 矫正方位，矫正位置
            if inline(green_lines):
                print "green for"
                RobotApi.ubtStartRobotAction("for", 1)  # 待调
                #RobotApi.ubtStartRobotAction("for", 2)  # 待调
        elif max_green[1] + max_green[3] > 220:
            print "上绿色"
            on_green = 1
            # while 矫正方位，矫正位置
            if in_green(green_lines):
                RobotApi.ubtStartRobotAction("first", 1)  # 待调
                RobotApi.ubtStartRobotAction("for", 2)  # 待调

        else:
            RobotApi.ubtStartRobotAction("for", 1)
        return
    if on_green == 1:
        print "在绿色上"
        if len(green) > 0:
            max_green = find_max_area(green)

            green_lines = color_detection.green_lines(frame)
            print green_lines
            if in_green(green_lines):
                RobotApi.ubtStartRobotAction("for", 1)  # 待调
                return
            print "not"
            print max_green
            if max_green[3] <= 70:
                print "out"
                RobotApi.ubtStartRobotAction("for", 1)  # 待调

        else:
            print "绿色完成"
            RobotApi.ubtStartRobotAction("for", 3)  # 待调
            on_green = 2
        return

    black_result = color_detection.black_lines(frame=frame)
    h_lines = black_result['h_lines']
    v_lines = black_result['v_lines']
    if len(h_lines) == 1 and h_lines[0][0] <= 40:
        # RobotApi.ubtStartRobotAction("first", 1)
        RobotApi.ubtStartRobotAction("for", 2)
        print "发现横线"
        print h_lines
        return
    if len(h_lines) == 1 and h_lines[0][0] > 40 and len(v_lines) <= 1:
        RobotApi.ubtStartRobotAction("Left", 1)
        print h_lines

        print "左转"
        return
    if len(h_lines) == 2 and h_lines[0][0] > 60 and gouhe == 0:
        print "沟壑"
        gouhe = 1
        return

    inline(black_result)
    print "hei xian tiao zheng"
    print black_result

    RobotApi.ubtStartRobotAction("for", 5)  # 待调
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
            frame = color_detection.balanced(frame)
            if color_detection.find_yellow(frame):
                flag = 1
                print "find yellow"
            elif flag == 1:
                print "start forward"
                RobotApi.ubtStartRobotAction("first", 1)
                RobotApi.ubtStartRobotAction("for", 6)
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
            frame = color_detection.balanced(frame)
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
