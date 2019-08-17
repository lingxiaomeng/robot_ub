import cv2

import numpy as np

import color_detection

mtx = np.array([[195.2195786600618, 0, 243.8702905959468],
                [0, 187.1211872269851, 214.2502222927143],
                [0, 0, 1]])
dist = np.array(
    [[-0.1395365798775013, 0.01847486190780475, -0.006487336053286973, 0.002973805775375551,
      -0.0006586561922608219]])

if __name__ == "__main__":
    frame = cv2.imread('/home/pi/Desktop/test0816/107_balanced.jpg')
    frame = color_detection.balanced(frame)
    # a = color_detection.yellow_lines(frame)
    color = color_detection.edge_lines(frame)
    print color

    # print(a)
    # c = find_green(a)
    #     # print c
    #     # for (name, rects) in a:
    #     #     print(name)
    #     #     print(len(rects))
    #     #     for rect in rects:
    #     #         print(rect)
