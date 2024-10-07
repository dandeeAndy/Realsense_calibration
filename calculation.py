import cv2
import numpy as np

# 카메라 매트릭스와 왜곡 계수 (예시 값, 실제 값으로 대체해야 함)

Width = 848
Height = 480
cx = 426.886
cy = 238.556
fx = 417.532
fy = 417.532
 
# 0.999999 -0.00154659 -0.000750733 
# 0.00154663 0.999999 5.97449e-05   
# 0.00075064 -6.09059e-05 1         
# Translation Vector:
# 0.0150654 9.5295e-05 -0.000237623

K = np.array([[fx, 0, cx],
              [0, fy, cy],
              [0, 0, 1]])
D = np.array([k1, k2, p1, p2, k3])

def pixel_to_robot_coordinates(x, y, z, roi_index):
    # 픽셀 좌표를 (u, v) 형태로 변환
    pixel_coords = np.array([[[x, y]]], dtype=np.float32)
    
    # 왜곡 보정
    undistorted_coords = cv2.undistortPoints(pixel_coords, K, D, None, K)
    ux, uy = undistorted_coords[0][0]
    
    if roi_index == 0:
        diff_x, diff_y = camera_diff_roi1_x, camera_diff_roi1_y
    elif roi_index == 1:
        diff_x, diff_y = camera_diff_roi2_x, camera_diff_roi2_y
    elif roi_index == 2:
        diff_x, diff_y = camera_diff_roi3_x, camera_diff_roi3_y
    elif roi_index == 3:
        diff_x, diff_y = camera_diff_roi4_x, camera_diff_roi4_y
    else:
        diff_x, diff_y = 0, 0  # 기본값 설정
    
    robot_x = ((ux + diff_x) * pixel_to_mm) + X_OFFSET
    robot_y = ((uy + diff_y) * pixel_to_mm) + Y_OFFSET
    robot_z = z  
    return robot_x, robot_y, robot_z