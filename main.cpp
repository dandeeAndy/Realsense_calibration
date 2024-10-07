#include <librealsense2/rs.hpp>
#include <iostream>

// 컴파일 명령어
// g++ main.cpp -o calibration_reader -I"C:\Program Files (x86)\Intel RealSense SDK 2.0\include" -L"C:\Program Files (x86)\Intel RealSense SDK 2.0\lib\x64" -lrealsense2

int main() {
    // RealSense 파이프라인 생성
    rs2::pipeline pipe;

    // 파이프라인 시작
    pipe.start();

    // 몇 프레임 기다리기
    for(int i = 0; i < 30; i++) {
        pipe.wait_for_frames();
    }

    // 최신 세트의 프레임 가져오기
    rs2::frameset frames = pipe.wait_for_frames();

    // 깊이 카메라에서 프레임 가져오기
    rs2::depth_frame depth = frames.get_depth_frame();

    // 깊이 카메라의 intrinsics 가져오기
    rs2::video_stream_profile depth_profile = depth.get_profile().as<rs2::video_stream_profile>();
    rs2_intrinsics intrinsics = depth_profile.get_intrinsics();

    // Intrinsics 출력
    std::cout << "Depth Camera Intrinsics:" << std::endl;
    std::cout << "Width: " << intrinsics.width << std::endl;
    std::cout << "Height: " << intrinsics.height << std::endl;
    std::cout << "PPX: " << intrinsics.ppx << std::endl;
    std::cout << "PPY: " << intrinsics.ppy << std::endl;
    std::cout << "FX: " << intrinsics.fx << std::endl;
    std::cout << "FY: " << intrinsics.fy << std::endl;

    // Extrinsics는 두 카메라 사이의 관계이므로, 색상 카메라와의 관계를 가져옵니다
    rs2::video_stream_profile color_profile = frames.get_color_frame().get_profile().as<rs2::video_stream_profile>();
    rs2_extrinsics extrinsics = depth_profile.get_extrinsics_to(color_profile);

    // Extrinsics 출력
    std::cout << "\nExtrinsics (Depth to Color):" << std::endl;
    std::cout << "Rotation Matrix:" << std::endl;
    for(int i = 0; i < 9; i++) {
        std::cout << extrinsics.rotation[i] << " ";
        if((i+1) % 3 == 0) std::cout << std::endl;
    }
    std::cout << "Translation Vector:" << std::endl;
    for(int i = 0; i < 3; i++) {
        std::cout << extrinsics.translation[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}