import numpy as np
import cv2
import glob

mtx = np.array([[195.2195786600618, 0, 243.8702905959468],
                [0, 187.1211872269851, 214.2502222927143],
                [0, 0, 1]]
               )
dist = np.array(
    [[-0.1395365798775013, 0.01847486190780475, -0.006487336053286973, 0.002973805775375551, -0.0006586561922608219]])

imge = cv2.imread('./photo1/1.jpg')
h, w = imge.shape[:2]
print(h)
print(w)
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
# undistort
dst = cv2.undistort(imge, mtx, dist, None, newcameramtx)

# crop the image
x, y, w, h = roi
# dst = dst[y:y + h, x:x + w]
cv2.imwrite('calibresult1.png', dst)
