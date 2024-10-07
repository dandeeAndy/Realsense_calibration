import pyrealsense2 as rs
import numpy as np

# RealSense 파이프라인 설정
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 파이프라인 시작
profile = pipeline.start(config)

try:
    # 첫 번째 프레임을 기다림
    for _ in range(30):
        pipeline.wait_for_frames()

    # 컬러 스트림의 내부 파라미터 얻기
    color_stream = profile.get_stream(rs.stream.color)
    intrinsics = color_stream.as_video_stream_profile().get_intrinsics()

    # 카메라 행렬 생성
    camera_matrix = np.array([
        [intrinsics.fx, 0, intrinsics.ppx],
        [0, intrinsics.fy, intrinsics.ppy],
        [0, 0, 1]
    ])

    # 왜곡 계수 얻기
    distortion_coeffs = np.array(intrinsics.coeffs)

    print("Camera Matrix:")
    print(camera_matrix)
    print("\nDistortion Coefficients:")
    print(distortion_coeffs)

finally:
    pipeline.stop()