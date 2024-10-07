import os
import cv2
import pyrealsense2 as rs
import numpy as np
import time

def capture_and_save_images(num_images=20, folder_name="calibration_images"):
    """RealSense 카메라로부터 캘리브레이션 이미지를 캡처하고 저장합니다."""
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    
    pipeline.start(config)
    time.sleep(2)
    
    for i in range(num_images):
        print(f"Capturing image {i+1}/{num_images}. Press 'c' to capture, 'q' to quit.")
        
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            
            frame = np.asanyarray(color_frame.get_data())
            cv2.imshow('Capture', frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('c'):
                filename = f"calibration_image_{i+1}.jpg"
                full_path = os.path.join(folder_name, filename)
                cv2.imwrite(full_path, frame)
                print(f"Image saved: {full_path}")
                break
            elif key == ord('q'):
                pipeline.stop()
                cv2.destroyAllWindows()
                return
    
    pipeline.stop()
    cv2.destroyAllWindows()
    print(f"All images saved in folder: {os.path.abspath(folder_name)}")

# 이미지 캡처 및 저장 실행
if __name__ == "__main__":
    capture_and_save_images()