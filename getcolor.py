import cv2

import color_detection

frame = cv2.imread('3.jpg')
# frame = cv2.resize(frame, (640, 480))
a = color_detection.getcolor(frame)
print(a)
for (name, rects) in a:
    print(name)
    print(len(rects))
    for rect in rects:
        print(rect)
