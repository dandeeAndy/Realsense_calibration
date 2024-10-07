import numpy as np

# .npz 파일 로드
data = np.load('calibration_results.npz')

# 카메라 매트릭스와 왜곡 계수 추출
mtx = data['mtx']
dist = data['dist']

print("Camera Matrix:")
print(mtx)
print("\nDistortion Coefficients:")
print(dist)

# 파일 닫기 (선택사항이지만 권장됨)
data.close()