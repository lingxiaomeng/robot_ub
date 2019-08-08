#!/usr/bin/python
# -*- coding: UTF-8 -*-
from time import time

import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

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


def get_color(frame):
    # print frame[40]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # cv2.imwrite("hsv.jpg", hsv)
    # print hsv[40]
    result = []
    for (color_min, color_max, name) in COLOR_ARRAY:
        mask = cv2.inRange(hsv, color_min, color_max)
        # cv2.imwrite(name + "_mask.jpg", mask)
        gray = cv2.GaussianBlur(mask, (5, 5), 0)
        # cv2.imwrite(name + "_gray.jpg", gray)
        edges = cv2.Canny(gray, 75, 225, apertureSize=3)
        # cv2.imwrite(name + "_edges.jpg", edges)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 60)
        x = []
        print lines
        if lines is not None:
            for i in range(0, len(lines)):
                rho, theta = lines[i][0][0], lines[i][0][1]
                x.append([rho, theta])
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imwrite(name + "hough_result.jpg", frame)
            start = time()
            print 'Runing scikit-learn implementation...'
            db = DBSCAN(eps=10, min_samples=1).fit(x)
            skl_labels = db.labels_
            end = time()
            print end - start
            n_clusters_ = len(set(skl_labels)) - (1 if -1 in skl_labels else 0)  # 获取分簇的数目
            print('分簇的数目: %d' % n_clusters_)
            print skl_labels
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
                print(one_cluster)
            for (rho, theta) in dbscan_result:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imwrite(name + "_after_dbscan_result.jpg", frame)

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
    sub_results = []
    rects_results = []
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
