import numpy as np
import cv2

dist = np.array([k1, k2, p1, p2, k3])
mtx = np.array([[fx, 0, cx],
      [0, fy, cy],
      [0, 0, 1]])

image = cv2.imread('./cali_images/WIN_20230110_13_21_30_Pro.jpg')

h, w = image.shape[:2]

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,
                                                 dist,
                                                 (w, h),
                                                 1, (w, h))

# undistort
dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imshow('result', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()