import cv2
import mediapipe as mp
import numpy as np

def analyze_and_warp_face(image_path):
    # 1. MediaPipe Face Mesh 초기화 (with문 사용으로 자동 자원 해제)
    mp_face_mesh = mp.solutions.face_mesh
    
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        # 이미지 불러오기
        image = cv2.imread(image_path)
        if image is None:
            print("❌ 이미지를 불러올 수 없습니다. 경로를 확인해주세요.")
            return
            
        h, w, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 2. 얼굴 랜드마크 추출
        results = face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            print("❌ 얼굴을 인식하지 못했습니다.")
            return
            
        landmarks = results.multi_face_landmarks[0].landmark
        
        # 정규화된 좌표를 실제 이미지의 픽셀 좌표로 변환
        points = np.array([(int(pt.x * w), int(pt.y * h)) for pt in landmarks])
        
        # --- 황금 비율 계산 및 좌표 이동 (개념적 로직) ---
        # target_points = calculate_golden_ratio_points(points) 
        
        # 3. 인식된 랜드마크 시각화 (녹색 점으로 표시)
        for point in points:
            # OpenCV 호환성을 위해 명시적으로 int 형변환
            pt_x, pt_y = int(point[0]), int(point[1])
            cv2.circle(image, (pt_x, pt_y), 1, (0, 255, 0), -1)
            
        # 결과 보여주기
        cv2.imshow("Face Mesh Detected", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# 사용 예시
# analyze_and_warp_face('my_face.jpg')
