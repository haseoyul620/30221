import cv2
import mediapipe as mp
import numpy as np

# 1. MediaPipe 얼굴 메쉬(Face Mesh) 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

def get_face_landmarks(image_path):
    # 2. 이미지 불러오기 및 색상 변환
    image = cv2.imread(image_path)
    if image is None:
        print("이미지를 찾을 수 없습니다.")
        return
        
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, c = image.shape

    # 3. 얼굴 특징점 추출
    results = face_mesh.process(image_rgb)

    if not results.multi_face_landmarks:
        print("얼굴을 인식하지 못했습니다.")
        return

    # 4. 특징점 좌표 저장 및 시각화
    landmarks = []
    for face_landmarks in results.multi_face_landmarks:
        for point in face_landmarks.landmark:
            # 정규화된 좌표(0~1)를 실제 이미지 픽셀 좌표로 변환
            x = int(point.x * w)
            y = int(point.y * h)
            landmarks.append((x, y))
            
            # 인식된 점을 이미지 위에 초록색으로 표시
            cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

    # 결과 이미지 출력
    cv2.imshow("Face Landmarks", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return landmarks

# 실행 예시 (테스트할 이미지 파일 경로를 넣어주세요)
# landmarks = get_face_landmarks('test_face.jpg')
