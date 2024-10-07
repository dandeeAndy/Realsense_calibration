
import os
import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt
import pyrealsense2 as rs
import time

def save_image(image, folder_path, filename):
    """이미지를 지정된 폴더에 저장합니다."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    full_path = os.path.join(folder_path, filename)
    cv2.imwrite(full_path, image)
    print(f"Image saved: {full_path}")
    
def capture_calibration_images(num_images=20):
    """RealSense 카메라로부터 캘리브레이션 이미지를 캡처합니다."""
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    
    pipeline.start(config)
    time.sleep(1)
    
    images = []
    save_folder = "calibration_images"
    
    for i in range(num_images):
        print(f"Capture image {i+1}/{num_images}. Press 'c' to capture, 'q' to quit.")
        while True:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue
                
                frame = np.asanyarray(color_frame.get_data())
                cv2.imshow('Capture', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    images.append(frame)
                    break
                elif key == ord('q'):
                    pipeline.stop()
                    cv2.destroyAllWindows()
                    return images
            except RuntimeError:
                print("카메라로부터 프레임을 받아오는 데 실패했습니다. 카메라 연결을 확인하세요.")
                pipeline.stop()
                return []
            
    
    pipeline.stop()
    cv2.destroyAllWindows()
    return images

def calibrate_camera(images, board_size=(9,6), square_size=0.025):
    """카메라 캘리브레이션을 수행합니다."""
    # 체커보드의 3D 점 준비
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1,2)
    objp *= square_size

    objpoints = []  # 3D 점
    imgpoints = []  # 2D 점

    for img in images:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, board_size, None)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), 
                                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)

            # 코너 그리기 및 표시
            cv2.drawChessboardCorners(img, board_size, corners2, ret)
            cv2.imshow('Chessboard Corners', img)
            cv2.waitKey(500)

    cv2.destroyAllWindows()

    # 카메라 캘리브레이션 수행
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return mtx, dist, rvecs, tvecs

def undistort_image(img, mtx, dist):
    """이미지의 왜곡을 보정합니다."""
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    return dst

def calculate_reprojection_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist):
    """재투영 오차를 계산합니다."""
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error
    return mean_error/len(objpoints)

def visualize_results(original, undistorted):
    """원본 이미지와 보정된 이미지를 시각화합니다."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
    ax1.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    ax1.set_title('Original Image')
    ax1.axis('off')
    ax2.imshow(cv2.cvtColor(undistorted, cv2.COLOR_BGR2RGB))
    ax2.set_title('Undistorted Image')
    ax2.axis('off')
    plt.show()

# 메인 실행 코드
if __name__ == "__main__":
    # 1. 캘리브레이션 이미지 캡처
    images = capture_calibration_images()
    
    if not images:
        print("No images captured. Exiting.")
        exit()

    # 2. 카메라 캘리브레이션 수행
    mtx, dist, rvecs, tvecs = calibrate_camera(images)

    print("Camera matrix:")
    print(mtx)
    print("\nDistortion coefficients:")
    print(dist)

    # 3. 재투영 오차 계산
    objpoints = [np.zeros((9*6,3), np.float32).reshape(-1,3) for _ in range(len(images))]
    imgpoints = [cv2.findChessboardCorners(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (9,6))[1] for img in images]
    error = calculate_reprojection_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist)
    print(f"\nMean reprojection error: {error}")

    # 4. 테스트 이미지에 대한 왜곡 보정
    test_image = images[-1]  # 마지막 캡처 이미지를 테스트 이미지로 사용
    undistorted = undistort_image(test_image, mtx, dist)

    # 5. 결과 시각화
    visualize_results(test_image, undistorted)

    # 6. 캘리브레이션 결과 저장
    np.savez('calibration_results.npz', mtx=mtx, dist=dist)
    print("Calibration results saved to 'calibration_results.npz'")
    
    # 7. 캘리브레이션 이미지 저장
    print(f"Calibration images saved in folder: {os.path.abspath('calibration_images')}")