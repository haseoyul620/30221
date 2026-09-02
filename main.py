import cv2
import numpy as np
import mediapipe as mp
from scipy.interpolate import griddata

def get_landmarks(image):
    """MediaPipe를 이용해 468개의 얼굴 특징점을 추출합니다."""
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None
        
        h, w = image.shape[:2]
        landmarks = []
        for point in results.multi_face_landmarks[0].landmark:
            landmarks.append([point.x * w, point.y * h])
        return np.array(landmarks)

def warp_image(image, src_points, dst_points):
    """
    원본 좌표(src)에서 목표 좌표(dst-황금비율)로 이미지를 자연스럽게 픽셀 유동화(Warping)합니다.
    """
    h, w = image.shape[:2]
    
    # 이미지 전체 격자 생성
    grid_x, grid_y = np.mgrid[0:w, 0:h]
    
    # 외곽선 고정 (얼굴 외의 배경이 일그러지지 않도록 테두리 점 추가)
    boundary_points = np.array([[0,0], [w/2,0], [w-1,0], 
                                [0,h/2], [w-1,h/2], 
                                [0,h-1], [w/2,h-1], [w-1,h-1]])
    
    src_all = np.vstack((src_points, boundary_points))
    dst_all = np.vstack((dst_points, boundary_points))
    
    # 픽셀이 이동해야 할 방향(Vector) 계산
    diff_x = dst_all[:, 0] - src_all[:, 0]
    diff_y = dst_all[:, 1] - src_all[:, 1]
    
    # SciPy를 이용해 부드러운 왜곡 맵(Map) 생성
    map_x = griddata(src_all, diff_x, (grid_x, grid_y), method='cubic', fill_value=0)
    map_y = griddata(src_all, diff_y, (grid_x, grid_y), method='cubic', fill_value=0)
    
    map_x = (grid_x + map_x).astype(np.float32).T
    map_y = (grid_y + map_y).astype(np.float32).T
    
    # OpenCV remap을 통해 최종 이미지 생성
    warped_img = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return warped_img

def apply_golden_ratio(image_path):
    """전체 파이프라인 실행 함수"""
    image = cv2.imread(image_path)
    if image is None:
        print("이미지 파일을 찾을 수 없습니다.")
        return

    # 1. 원본 얼굴 좌표 추출
    src_landmarks = get_landmarks(image)
    if src_landmarks is None:
        print("얼굴을 인식하지 못했습니다.")
        return

    # 2. 목표 좌표 계산 (황금비율 로직)
    # 여기서는 예시로 '턱선(하관)을 5% 위로 올려 갸름하게' 만드는 목표 좌표를 만듭니다.
    # 실제 앱에서는 눈, 코, 입의 황금비율 공식을 적용해 dst_landmarks를 세밀하게 계산해야 합니다.
    dst_landmarks = src_landmarks.copy()
    
    # 턱선에 해당하는 좌표(대략적인 인덱스 152번 부근)를 Y축으로 살짝 올림
    chin_indices = [152, 148, 176, 149, 150, 136, 172, 132] 
    for idx in chin_indices:
        dst_landmarks[idx][1] -= 15  # 위로 15픽셀 이동 (갸름하게)

    # 3. 이미지 변형 (Warping)
    print("황금비율을 계산하여 이미지를 변형 중입니다. (수 초 정도 소요될 수 있습니다)")
    result_image = warp_image(image, src_landmarks, dst_landmarks)

    # 4. 결과 출력
    combined = np.hstack((image, result_image)) # 원본과 결과 나란히 붙이기
    cv2.imshow("Original vs Golden Ratio (Warped)", combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 실행
# apply_golden_ratio("내얼굴사진.jpg")
