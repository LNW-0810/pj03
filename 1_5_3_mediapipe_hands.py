## 만약에 웹캠이 켜지지 않는다. 
## uv add opencv-contrib-python 

## mediapipe 라이브러리 설치 uv add mediapipe==0.10.14
import sys 
import cv2 
import mediapipe as mp 

# 모델 불러오기
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

##########################################################
# 카메라 시작
##########################################################
vcap = cv2.VideoCapture(0)

while True:
    # 카메라 이미지 추출하기 
    ret, frame = vcap.read()

    # 카메라 작동 확인
    if not ret:
        print("카메라가 작동하지 않습니다.")
        sys.exit()

    # 좌우 반전 
    flipped_frame = cv2.flip(frame, 1)  # 그릴 도화지 입니다.

    #------------------------------------------------------
    # 손 그리기 준비 
    flipped_frame.flags.writeable = True 

    # 손 감지하기 
    results = hands.process(flipped_frame)

    # 추출 및 그리기
    if results.multi_hand_landmarks:
        print(f"{len(results.multi_hand_landmarks)}개의 손이 감지되었습니다.")
        ## 손 하나하나 가져오기 
        for hand_landmarks in results.multi_hand_landmarks:
            print(f"이 손에는 {len(hand_landmarks.landmark)}개의 좌표가 있습니다.")
            
            landmarks = hand_landmarks.landmark
            #---------------------------------------------------
            # 실습. 포인트 하나 그리기 
            #---------------------------------------------------
            # for idx, landmark in enumerate(landmarks):
            #     print(landmark)
            #     if idx == 4:
            #         print(f"Point {idx} = {landmark.x} | {landmark.y} | {landmark.z}")
            #         print("="*100)

            #         # landmark.x,landmark.y -> 0.3922814130783081 | 0.7097784876823425
            #         # 실제 좌표가 아닌 상대적인 좌표
            #         h, w, c = flipped_frame.shape
            #         point_x = int(landmark.x * w)
            #         point_y = int(landmark.y * h)
            #         # 원 그리기 (이미지 - 중심점 - 반지름 - 색상 - 두께 - (옵션))
            #         cv2.circle(flipped_frame, (point_x, point_y), 5, (0,255,0), 2)
            #---------------------------------------------------
            # 과제 1-2. 내가 원하는 좌표만 그리기 (손가락 끝점, V)
            #---------------------------------------------------
            # endpoints = [4, 8, 12, 16, 20]
            # v_points = [5, 6, 7, 8, 9, 10, 11, 12]

            # for idx, landmark in enumerate(landmarks):
            #     if idx in v_points:
            #         print(f"Point {idx} = {landmark.x} | {landmark.y} | {landmark.z}")
            #         print("="*100)

            #         h, w, c = flipped_frame.shape
            #         point_x = int(landmark.x * w)
            #         point_y = int(landmark.y * h)
            #         # 원 그리기 (이미지 - 중심점 - 반지름 - 색상 - 두께 - (옵션))
            #         cv2.circle(flipped_frame, (point_x, point_y), 5, (0,255,0), 2)
            #---------------------------------------------------
            # 과제 3. 두 점 사이의 거리 구하기
            #---------------------------------------------------
            point1_idx = 4
            point2_idx = 8

            point1_landmark = landmarks[point1_idx]
            point2_landmark = landmarks[point2_idx]

            h, w, c = flipped_frame.shape
            point1_x = int(point1_landmark.x * w)
            point1_y = int(point1_landmark.y * h)

            point2_x = int(point2_landmark.x * w)
            point2_y = int(point2_landmark.y * h)

            # 피타고라스 공식 ( c^2 = a^2 + b^2 )
            distance = ((point1_x - point2_x)**2 + (point1_y - point2_y)**2) ** 0.5

            # 텍스트로 그리기 
            cv2.putText(
                flipped_frame, 
                f"distance: {distance}", 
                (50, 50), 
                cv2.FONT_HERSHEY_COMPLEX, 
                1, 
                (255,0,0), 
                2
            )
            







            ## 자동그리기
            # mp_drawing.draw_landmarks(
            #     flipped_frame,
            #     hand_landmarks,
            #     mp_hands.HAND_CONNECTIONS,
            #     mp_drawing_styles.get_default_hand_landmarks_style(),
            #     mp_drawing_styles.get_default_hand_connections_style()
            # )
    #------------------------------------------------------

    # 화면 띄우기
    cv2.imshow("webcam", flipped_frame)

    # 화면 끄기 
    key = cv2.waitKey(1)
    if key == 27: # ESC(ASCII Code)
        break

vcap.release()
cv2.destroyAllWindows()