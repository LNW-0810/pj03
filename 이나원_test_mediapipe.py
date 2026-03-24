# 1. Mediapipe에서 손가락 끝 점만 프레임에 표현할 수 있다.
# 2. V에 해당하는 랜드마크 점을 프레임에 표현할 수 있다.
# 3. (도전) 엄지손가락 끝(4)와 검지손가락 끝(8)의 거리를 구할 수 있다.

import sys
import math
import cv2
import mediapipe as mp

# ==============================
# MediaPipe 손 모델 준비
# ==============================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ==============================
# 카메라 열기
# ==============================
vcap = cv2.VideoCapture(0)

# 손가락 끝 랜드마크 번호
fingertip_ids = [4, 8, 12, 16, 20]

# V에 해당하는 랜드마크 점
v_ids = [5, 6, 7, 8, 9, 10, 11, 12]

while True:
    ret, frame = vcap.read()

    if not ret:
        print("카메라가 작동하지 않습니다.")
        sys.exit()

    # 좌우 반전
    flipped_frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)

    # 손 인식
    results = hands.process(rgb_frame)

    # 손이 감지되었는지 확인
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = hand_landmarks.landmark

            # ------------------------------
            # 1) 손가락 끝 점만 프레임에 표시
            # ------------------------------
            for idx in fingertip_ids:
                landmark = landmarks[idx]

                h, w, c = flipped_frame.shape
                point_x = int(landmark.x * w)
                point_y = int(landmark.y * h)

                # 손가락 끝 점 표시
                cv2.circle(flipped_frame, (point_x, point_y), 5, (255, 0, 0), 2)
            # ------------------------------
            # 2) V에 해당하는 랜드마크 점 표시
            # ------------------------------
            for idx in v_ids:
                landmark = landmarks[idx]

                h, w, c = flipped_frame.shape
                point_x = int(landmark.x * w)
                point_y = int(landmark.y * h)

                # V 관련 점은 빨간색으로 표시
                cv2.circle(flipped_frame, (point_x, point_y), 8, (0, 0, 255), 2)

            # ------------------------------
            # 3) 엄지 끝(4)와 검지 끝(8)의 거리 구하기
            # ------------------------------
            thumb = landmarks[4]
            index_finger = landmarks[8]

            h, w, c = flipped_frame.shape

            thumb_x = int(thumb.x * w)
            thumb_y = int(thumb.y * h)

            index_x = int(index_finger.x * w)
            index_y = int(index_finger.y * h)

            # 두 점 사이 직선 거리 계산
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
            print(distance)

            # 두 점 사이 선 그리기
            cv2.line(flipped_frame, (thumb_x, thumb_y), (index_x, index_y),(255, 0, 0), 2)


    cv2.imshow("webcam", flipped_frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

vcap.release()
cv2.destroyAllWindows()