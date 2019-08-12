import numpy as np
import cv2
import glob

#
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# print criteria
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 6, 3), np.float32)
objp[:, :2] = np.mgrid[0:6, 0:6].T.reshape(-1, 2)
objp = objp * 2.1

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

images = glob.glob('./photo1/*.jpg')

for frame in images:
    print frame
    img = cv2.imread(frame)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (6, 6), None)

    # If found, add object points, image points (after refining them)
    if ret:
        print "find"
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (6, 6), corners2, ret)
        cv2.imwrite('img_corner.jpg', img)
        # cv2.waitKey(500)
# cv2.destroyAllWindows()
# print objpoints
# print imgpoints
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print mtx
        print dist


# mtx = np.array([[253.20539331, 0., 248.55414116],
#                 [0., 252.76911519, 202.42935334],
#                 [0., 0., 1.]])
# dist = np.array([[-2.96386685e-01, 1.05971922e-01, 3.04389193e-03, -1.88796145e-05
#                   - 1.87157061e-02]])
# #
# imge = cv2.imread('chess.jpg')
# h, w = imge.shape[:2]
# newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
#
# print newcameramtx
#
# # undistort
# dst = cv2.undistort(imge, mtx, dist, None, newcameramtx)
#
# # crop the image
# x, y, w, h = roi
# dst = dst[y:y + h, x:x + w]
# cv2.imwrite('calibresult.png', dst)
