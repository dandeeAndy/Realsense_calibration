import cv2
import numpy as np
import glob
import os

def calibrate_from_saved_images(folder_name="calibration_images", board_size=(5,4)):
    """저장된 이미지를 사용하여 카메라 캘리브레이션을 수행합니다."""
    
    # 체커보드의 3D 점 준비
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1,2)
    
    objpoints = []  # 3D 점
    imgpoints = []  # 2D 점

    images = glob.glob(f"{folder_name}/*.jpg")
    
    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            print(f"Failed to read image: {fname}")
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 체스보드 코너 찾기
        ret, corners = cv2.findChessboardCorners(gray, board_size, 
                                                 cv2.CALIB_CB_ADAPTIVE_THRESH + 
                                                 cv2.CALIB_CB_FAST_CHECK + 
                                                 cv2.CALIB_CB_NORMALIZE_IMAGE)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), 
                                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)

            # 코너 그리기 및 표시
            cv2.drawChessboardCorners(img, board_size, corners2, ret)
            cv2.imwrite(f'debug_corners_{os.path.basename(fname)}', img)
            print(f"Chessboard found in {fname}")
        else:
            print(f"Chessboard not found in {fname}")
            cv2.imwrite(f'debug_failed_{os.path.basename(fname)}', img)

    print(f"Found chessboard in {len(objpoints)} out of {len(images)} images")

    if len(objpoints) == 0:
        raise ValueError("No valid chessboard corners found in any image. Please check your images and board_size.")

    print("Starting camera calibration...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    print("Camera calibration completed.")

    return mtx, dist, rvecs, tvecs

# 메인 실행 코드
if __name__ == "__main__":
    try:
        mtx, dist, rvecs, tvecs = calibrate_from_saved_images()
        print("Calibration successful!")
        print("Camera matrix:")
        print(mtx)
        print("\nDistortion coefficients:")
        print(dist)
        np.savez('calibration_results.npz', mtx=mtx, dist=dist)
        print("Calibration results saved to 'calibration_results.npz'")
    except Exception as e:
        print(f"Calibration failed: {str(e)}")
        print("Please check the debug images and your chessboard pattern.")