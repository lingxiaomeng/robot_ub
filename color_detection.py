#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2
from time import time

import numpy as np
from sklearn.cluster import DBSCAN

mtx = np.array([[195.2195786600618, 0, 243.8702905959468],
                [0, 187.1211872269851, 214.2502222927143],
                [0, 0, 1]])
dist = np.array(
    [[-0.1395365798775013, 0.01847486190780475, -0.006487336053286973, 0.002973805775375551, -0.0006586561922608219]])

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
black_max = np.array([180, 255, 46])
white_min = np.array([0, 0, 70])
white_max = np.array([180, 30, 255])

COLOR_ARRAY = [[red_min, red_max, 'red'], [red2_min, red2_max, 'red'], [green_min, green_max, 'green'],
               [blue_min, blue_max, 'blue'], [yellow_min, yellow_max, 'yellow']]
print(cv2.__version__)


def balanced(img):
    r, g, b = cv2.split(img)
    r_avg = cv2.mean(r)[0]
    g_avg = cv2.mean(g)[0]
    b_avg = cv2.mean(b)[0]
    # 求各个通道所占增益
    k = (r_avg + g_avg + b_avg) / 3
    kr = k / r_avg
    kg = k / g_avg
    kb = k / b_avg
    r = cv2.addWeighted(src1=r, alpha=kr, src2=0, beta=0, gamma=0)
    g = cv2.addWeighted(src1=g, alpha=kg, src2=0, beta=0, gamma=0)
    b = cv2.addWeighted(src1=b, alpha=kb, src2=0, beta=0, gamma=0)
    balance_img = cv2.merge([r, g, b])
    return balance_img


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


def lines_detection(frame, colormin, colormax):
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
    mask = cv2.inRange(hsv, colormin, colormax)
    cv2.imwrite("_mask.jpg", mask)
    gray = cv2.GaussianBlur(mask, (5, 5), 0)
    cv2.imwrite("black_gray.jpg", gray)
    edges = cv2.Canny(gray, 75, 225, apertureSize=3)
    cv2.imwrite("_edges.jpg", edges)
    cv2.imshow('edge', edges)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 60)
    x = []
    if lines is not None:
        for i in range(0, len(lines)):
            rho, theta = lines[i][0][0], lines[i][0][1]
            if rho < 0:
                rho *= -1
                theta = theta - np.pi
            x.append([rho, theta])
            a = np.cos(theta)
            b = np.sin(theta)
            # print a, b
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # cv2.imwrite(name + "hough_result.jpg", frame)
        start = time()
        # print 'Running scikit-learn implementation...'
        db = DBSCAN(eps=12, min_samples=1).fit(x)
        skl_labels = db.labels_
        end = time()
        # print end - start
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
        if len(result['v_lines']) == 2 and ((result['v_lines'][0][1] > 1.57 >= result['v_lines'][1][1]) or (
                result['v_lines'][1][1] > 1.57 >= result['v_lines'][0][1])):
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
    # cv2.imshow('frame', frame)
    # k = cv2.waitKey(500)
    # if k == 27:
    #     exit(1)
    # print points
    cv2.imwrite("black_after_db_scan_result.jpg", frame)
    return result


def get_color(frame):
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    frame = dst[y:y + h, x:x + w]
    result = dict()
    result['red'] = []
    result['green'] = []
    result['blue'] = []
    result['yellow'] = []
    result['black'] = []
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # print hsv
    for [color_min, color_max, name] in COLOR_ARRAY:
        mask = cv2.inRange(hsv, color_min, color_max)
        gray = cv2.GaussianBlur(mask, (5, 5), 0)
        # # print color_min, color_max
        # mask = cv2.inRange(hsv, color_min, color_max)
        # res = cv2.bitwise_and(frame, frame, mask=mask)
        # blured = cv2.blur(res, (3, 3))
        # ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)
        # gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        # opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        # cv2.imwrite("opened.jpg", gray)
        # closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        # cv2.imwrite("closed.jpg", closed)
        _, contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(frame, contours, -1, (0, 0, 255), 3)
        number = len(contours)
        if number >= 1:
            for i in range(0, number):
                area = cv2.contourArea(contours[i])
                x, y, w, h = cv2.boundingRect(contours[i])
                if w >= 75 or h >= 75:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    result[name].append([x, y, w, h, area])
                    cv2.imwrite(name + "_result1.jpg", frame)
            # cv2.imshow('frame', frame)
            # k = cv2.waitKey(500)
            # if k == 27:
            #     exit(1)
    return result


def find_yellow(frame):
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    frame = dst[y:y + h, x:x + w]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # print hsv
    mask = cv2.inRange(hsv, yellow_min, yellow_max)
    gray = cv2.GaussianBlur(mask, (5, 5), 0)
    _, contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(frame, contours, -1, (0, 0, 255), 3)
    number = len(contours)
    if number >= 1:
        for i in range(0, number):
            area = cv2.contourArea(contours[i])
            x, y, w, h = cv2.boundingRect(contours[i])
            if w >= 65 and h >= 65:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # cv2.imshow('frame', frame)
                # k = cv2.waitKey(500)
                # if k == 27:
                #     exit(1)
                return True
        return False


def black_lines(frame):
    return lines_detection(frame, black_min, black_max)


def red_lines(frame):
    return lines_detection(frame, red_min, red_max)


def green_lines(frame):
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
    mask = cv2.inRange(hsv, green_min, green_max)
    # cv2.imwrite(name + "_mask.jpg", mask)
    gray = cv2.GaussianBlur(mask, (5, 5), 0)
    cv2.imwrite("black_gray.jpg", gray)
    edges = cv2.Canny(gray, 75, 225, apertureSize=3)
    # cv2.imwrite(name + "_edges.jpg", edges)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 45)
    x = []
    if lines is not None:
        for i in range(0, len(lines)):
            rho, theta = lines[i][0][0], lines[i][0][1]
            if rho <= 0:
                rho *= -1
                theta = theta - np.pi
            x.append([rho, theta])
            # cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # cv2.imwrite(name + "hough_result.jpg", frame)
        start = time()
        print 'Running scikit-learn implementation...'
        db = DBSCAN(eps=10, min_samples=1).fit(np.array(x))
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
        # cv2.imshow('frame', frame)
        # k = cv2.waitKey(500)
        # if k == 27:
        #     exit(1)
        # # print points
        cv2.imwrite("black_after_db_scan_result.jpg", frame)
    return result
