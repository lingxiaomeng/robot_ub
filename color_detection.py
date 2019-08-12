#!/usr/bin/python
# -*- coding: UTF-8 -*-
from time import time

import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

mtx = np.array([[195.2195786600618, 0, 243.8702905959468],
                [0, 187.1211872269851, 214.2502222927143],
                [0, 0, 1]
                ]
               )
dist = np.array(
    [[-0.1395365798775013, 0.01847486190780475, -0.006487336053286973, 0.002973805775375551, -0.0006586561922608219]])
# define HSV color value
red_min = np.array([0, 128, 46])
red_max = np.array([5, 255, 255])
red2_min = np.array([156, 128, 46])
red2_max = np.array([180, 255, 255])
green_min = np.array([35, 128, 46])
green_max = np.array([77, 255, 255])
blue_min = np.array([100, 128, 46])
blue_max = np.array([124, 255, 255])
yellow_min = np.array([15, 128, 46])
yellow_max = np.array([34, 255, 255])
black_min = np.array([0, 0, 0])
black_max = np.array([180, 255, 30])
white_min = np.array([0, 0, 70])
white_max = np.array([180, 30, 255])

COLOR_ARRAY = [[red_min, red_max, 'red'], [red2_min, red2_max, 'red'], [green_min, green_max, 'green'],
               [blue_min, blue_max, 'blue'], [yellow_min, yellow_max, 'yellow'], [black_min, black_max, 'black']]
print(cv2.__version__)


# closed = cv2.imread("closed.jpg")
# _, contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# print contours
def get_crossing(xa, ya, xb, yb, xc, yc, xd, yd):
    a = np.matrix(
        [
            [xb - xa, -(xd - xc)],
            [yb - ya, -(yd - yc)]
        ]
    )
    delta = np.linalg.det(a)
    if np.fabs(delta) < 1e-6:
        print(delta)
        return [0]
    c = np.matrix(
        [
            [xc - xa, -(xd - xc)],
            [yc - ya, -(yd - yc)]
        ]
    )
    d = np.matrix(
        [
            [xb - xa, xc - xa],
            [yb - ya, yc - ya]
        ]
    )
    lamb = np.linalg.det(c) / delta
    miu = np.linalg.det(d) / delta
    # print lamb, miu
    # if 1 >= lamb >= 0 and 0 <= miu <= 1:
    x = xc + miu * (xd - xc)
    y = yc + miu * (yd - yc)
    return [1, x, y]
    # else:
    #     return [0]


def black_lines_detection(frame):
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    frame = dst[y:y + h, x:x + w]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # cv2.imwrite("hsv.jpg", hsv)
    # print hsv[40]
    result = dict()
    result['v_lines'] = []
    result['h_lines'] = []
    result['bot_point'] = []
    result['top_point'] = []
    result['angle'] = []
    mask = cv2.inRange(hsv, black_min, black_max)
    # cv2.imwrite(name + "_mask.jpg", mask)
    gray = cv2.GaussianBlur(mask, (5, 5), 0)
    cv2.imwrite("black_gray.jpg", gray)
    edges = cv2.Canny(gray, 75, 225, apertureSize=3)
    # cv2.imwrite(name + "_edges.jpg", edges)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 60)
    x = []
    if lines is not None:
        for i in range(0, len(lines)):
            rho, theta = lines[i][0][0], lines[i][0][1]
            x.append([rho, theta])
            # cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # cv2.imwrite(name + "hough_result.jpg", frame)
        start = time()
        print 'Running scikit-learn implementation...'
        db = DBSCAN(eps=10, min_samples=1).fit(x)
        skl_labels = db.labels_
        end = time()
        print end - start
        n_clusters_ = len(set(skl_labels)) - (1 if -1 in skl_labels else 0)  # 获取分簇的数目
        print('分簇的数目: %d' % n_clusters_)
        # print skl_labels
        dbscan_result = []
        for i in range(n_clusters_):
            one_cluster = []
            rho = 0
            theta = 0
            for ii in range(len(x)):
                if skl_labels[ii] == i:
                    rho += x[ii][0]
                    theta += x[ii][1]
                    one_cluster.append(x[ii])
            rho = rho / len(one_cluster)
            theta = theta / len(one_cluster)

            dbscan_result.append([rho, theta])

            if 0 <= theta <= 0.7:
                result['v_lines'].append([rho, theta])
            elif 0 <= np.pi - theta <= 0.7:
                result['v_lines'].append([rho, theta])
            elif 1.04719 <= theta <= 1.570796327:
                result['h_lines'].append([rho, theta])
            elif 1.04719 <= np.pi - theta <= 1.570796327:
                result['h_lines'].append([rho, theta])
        # print(one_cluster)
        print dbscan_result
        for (rho, theta) in dbscan_result:
            # print rho, theta
            a = np.cos(theta)
            b = np.sin(theta)
            # print a, b
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        points = []
        if len(result['v_lines']) == 1:
            rho = result['v_lines'][0][0]
            theta = result['v_lines'][0][1]
            if theta > 1.57:
                result['angle'].append(
                    [0, 0, 0])
            else:
                result['angle'].append(
                    [0, 480, 0])
        if len(result['v_lines']) == 2:
            rho = result['v_lines'][0][0]
            theta = result['v_lines'][0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            rho = result['v_lines'][1][0]
            theta = result['v_lines'][1][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x3 = int(x0 + 1000 * (-b))
            y3 = int(y0 + 1000 * a)
            x4 = int(x0 - 1000 * (-b))
            y4 = int(y0 - 1000 * a)
            h, w = frame.shape[:2]
            print h, w
            top_point = get_crossing(x1, y1, x2, y2, x3, y3, x4, y4)
            if top_point[0] == 1:
                result['top_point'] = [top_point[1], top_point[2]]
                bot_point1 = get_crossing(x1, y1, x2, y2, -1000, h, 1000, h)
                bot_point2 = get_crossing(x3, y3, x4, y4, -1000, h, 1000, h)
                bot_point = [(bot_point1[1] + bot_point2[1]) / 2, (bot_point1[2] + bot_point2[2]) / 2]
                result['bot_point'] = bot_point
                delta_x = result['top_point'][0] - result['bot_point'][0]
                delta_y = result['top_point'][1] - result['bot_point'][1]
                result['angle'].append(
                    [delta_x / delta_y, (bot_point1[1] + bot_point2[1]) / 2, (bot_point1[2] + bot_point2[2]) / 2])

        for i in range(len(dbscan_result) - 1):
            for j in range(i + 1, len(dbscan_result)):
                rho = dbscan_result[i][0]
                theta = dbscan_result[i][1]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * a)
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * a)

                rho = dbscan_result[j][0]
                theta = dbscan_result[j][1]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x3 = int(x0 + 1000 * (-b))
                y3 = int(y0 + 1000 * a)
                x4 = int(x0 - 1000 * (-b))
                y4 = int(y0 - 1000 * a)
                point = get_crossing(x1, y1, x2, y2, x3, y3, x4, y4)
                if point[0] == 1:
                    points.append(point)
        cv2.imshow('frame', frame)
        k = cv2.waitKey(500)
        if k == 27:
            exit(1)
        print points
        cv2.imwrite("black_after_db_scan_result.jpg", frame)

        # plt.plot(one_cluster[:, 0], one_cluster[:, 1], 'o')

    # # gray = cv2.fastNlMeansDenoising(gray)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    # opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    # cv2.imwrite("opened.jpg", gray)
    # closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # cv2.imwrite("closed.jpg", closed)
    # _, contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # print contours
    # cv2.drawContours(res, contours, -1, (0, 0, 255), 3)
    # number = len(contours)
    # if number >= 1:
    #      for i in range(0, number):
    #         area = cv2.contourArea(contours[i])
    #         x, y, w, h = cv2.boundingRect(contours[i])
    #         if area >= 500 or w >= 50 or h >= 50:
    #             cv2.rectangle(res, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #             rects_results.append([x, y, w, h])
    #     cv2.imwrite(name + "result.jpg", res)
    #     if len(rects_results) > 0:
    #         sub_results.append(name)
    #         sub_results.append(rects_results)
    #         result.append(sub_results)

    return result


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
