import cv2
import mediapipe as mp
import numpy as np
from scipy.interpolate import Rbf

def get_facial_landmarks(image):
    """MediaPipe를 사용하여 얼굴의 468개 3D 랜드마크를 추출합니다."""
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
        
        h, w, _ = image.shape
        landmarks = []
        for lm in results.multi_face_landmarks[0].landmark:
            landmarks.append([lm.x * w, lm.y * h])
        return np.array(landmarks, dtype=np.float32)

def calculate_golden_ratio_targets(landmarks):
    """
    주요 랜드마크 위치를 기반으로 황금비율에 가깝도록 목표(Target) 좌표를 계산합니다.
    """
    targets = landmarks.copy()
    
    # MediaPipe 주요 랜드마크 인덱스
    # 33: 왼쪽 눈 외곽, 263: 오른쪽 눈 외곽, 1: 코 끝, 61: 입술 왼쪽, 291: 입술 오른쪽, 152: 턱 끝
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    nose_tip = landmarks[1]
    chin = landmarks[152]
    
    # 1. 양 눈 사이 거리를 기준으로 황금비율 폭 계산
    eye_distance = np.linalg.norm(right_eye - left_eye)
    
    # 황금비율(1.618)에 맞춘 이상적인 눈 중심-턱 끝 수직 거리
    ideal_face_height = eye_distance * 1.618
    
    # 현재 눈 중심과 턱 끝 수직 거리
    eye_center = (left_eye + right_eye) / 2.0
    current_height = chin[1] - eye_center[1]
    
    # 수직 비율 조정 계수
    scale_y = ideal_face_height / (current_height + 1e-6)
    
    # 2. 턱 위치 조정 (황금비율 길이에 맞춤)
    targets[152][1] = eye_center[1] + ideal_face_height
    
    # 3. 코 끝 위치 조정 (눈-코-턱 사이 황금 분할)
    # 이상적인 코 위치: 눈 중심과 턱 끝 사이의 약 1 / 1.618 지점
    ideal_nose_y = eye_center[1] + (ideal_face_height / 1.618)
    targets[1][1] = ideal_nose_y
    
    # 4. 입술 너비 조정 (양 눈동자 사이 거리와 황금비율)
    mouth_left = landmarks[61]
    mouth_right = landmarks[291]
    ideal_mouth_width = eye_distance / 1.618
    current_mouth_width = np.linalg.norm(mouth_right - mouth_left)
    
    width_scale = ideal_mouth_width / (current_mouth_width + 1e-6)
    mouth_center = (mouth_left + mouth_right) / 2.0
    
    targets[61][0] = mouth_center[0] - (ideal_mouth_width / 2.0)
    targets[291][0] = mouth_center[0] + (ideal_mouth_width / 2.0)
    
    return targets

def warp_image(image, src_points, dst_points):
    """
    Thin Plate Spline (TPS) 알고리즘을 사용해 이미지를 매끄럽게 변형합니다.
    """
    h, w, _ = image.shape
    
    # 이미지 외곽 테두리 점 추가 (배경 왜곡 방지)
    margin_points = np.array([
        [0, 0], [w/2, 0], [w-1, 0],
        [0, h/2], [w-1, h/2],
        [0, h-1], [w/2, h-1], [w-1, h-1]
    ], dtype=np.float32)
    
    src_all = np.vstack([src_points, margin_points])
    dst_all = np.vstack([dst_points, margin_points])
    
    # Grid 생성
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    
    # Rbf(Radial Basis Function)를 이용한 좌표 매핑
    rbf_x = Rbf(dst_all[:, 0], dst_all[:, 1], src_all[:, 0], function='thin_plate')
    rbf_y = Rbf(dst_all[:, 0], dst_all[:, 1], src_all[:, 1], function='thin_plate')
    
    map_x = rbf_x(grid_x, grid_y).astype(np.float32)
    map_y = rbf_y(grid_x, grid_y).astype(np.float32)
    
    # Remap 실행
    warped = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)
    return warped

def apply_golden_ratio_transform(image_path, output_path):
    image = cv2.imread(image_path)
    if image is None:
        print("이미지를 불러올 수 없습니다.")
        return

    # 1. 랜드마크 추출
    landmarks = get_facial_landmarks(image)
    if landmarks is None:
        print("얼굴을 인식하지 못했습니다.")
        return

    # 2. 황금비율 타겟 좌표 계산
    target_landmarks = calculate_golden_ratio_targets(landmarks)

    # 3. 이미지 변형(보정) 실행
    result_image = warp_image(image, landmarks, target_landmarks)

    # 4. 결과 저장
    cv2.imwrite(output_path, result_image)
    print(f"보정 완료: {output_path}")

# --- 실행 예시 ---
# apply_golden_ratio_transform("input.jpg", "output_golden_ratio.jpg")
