import glob

import color_detection

fs = glob.glob('/home/pi/Desktop/test0816/*.jpg')

for f in fs:
    if 'balance' in f:
        img = color_detection.cv2.imread(f)

        balance = color_detection.balanced(img)
        color_detection.cv2.imwrite(f, balance)

print fs
