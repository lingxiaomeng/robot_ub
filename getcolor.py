import cv2
import color_detection


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


frame = cv2.imread('calibresult.png')
# frame = cv2.resize(frame, (640, 480))
a = color_detection.get_color(frame)
print(a)
c = find_green(a)
print c
for (name, rects) in a:
    print(name)
    print(len(rects))
    for rect in rects:
        print(rect)
