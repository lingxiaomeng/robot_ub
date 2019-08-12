import cv2
import numpy as np

import color_detection

mtx = np.array([[195.2195786600618, 0, 243.8702905959468],
                [0, 187.1211872269851, 214.2502222927143],
                [0, 0, 1]])
dist = np.array(
    [[-0.1395365798775013, 0.01847486190780475, -0.006487336053286973, 0.002973805775375551,
      -0.0006586561922608219]])


def inline(rect1, block1):
    for i in range(len(block1)):
        r = block1[i]
        if abs(r[1] - rect1[1]) < 5 or abs(r[1] - rect1[1] + r[3] - rect1[3]) < 5:
            return i
    return -1


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
    return False


if __name__ == "__main__":
    frame = cv2.imread('./257.jpg')
    # print frame
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    a = color_detection.get_color(frame)
    print(a)
    # c = find_green(a)
    # print c
    # for (name, rects) in a:
    #     print(name)
    #     print(len(rects))
    #     for rect in rects:
    #         print(rect)
