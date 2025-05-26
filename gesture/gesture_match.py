import cv2
import mediapipe as mp
import time
import Quadrotor_HTTP
import Quadrotor_websocket

# from Quadrotor_HTTP import action_Left, action_Right, action_Thumbs_Up, action_Thumbs_Down, action_Pause, \
#     action_Forward, action_Backward
from gesture_judgment import detect_all_finger_state, detect_hand_state

# 1. 实例化
ws_control = Quadrotor_websocket.WebSocketControl(ws_url='ws://192.168.24.136:5000')
ws_control.init_ws_connection()
time.sleep(2)

# 初始化 Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 存储最近 15 次的手势判断结果，用于稳定性检测
recent_states = [''] * 5

# 打开摄像头
cap = cv2.VideoCapture(0)

prev_time = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 先把画面顺时针旋转 90°
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    frame = cv2.flip(frame, 1)  # 水平镜像翻转
    h, w = frame.shape[:2]
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = hands.process(image)

    if keypoints.multi_hand_landmarks:
        lm = keypoints.multi_hand_landmarks[0]
        lmHand = mp_hands.HandLandmark

        # 提取关键点坐标
        landmark_list = [[] for _ in range(6)]
        for index, landmark in enumerate(lm.landmark):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            if index == lmHand.WRIST:
                landmark_list[0].append((x, y))
            elif 1 <= index <= 4:
                landmark_list[1].append((x, y))
            elif 5 <= index <= 8:
                landmark_list[2].append((x, y))
            elif 9 <= index <= 12:
                landmark_list[3].append((x, y))
            elif 13 <= index <= 16:
                landmark_list[4].append((x, y))
            elif 17 <= index <= 20:
                landmark_list[5].append((x, y))

        # 将所有关键点的坐标存储到一起，简化后续函数的参数
        all_points = {
            'point0': landmark_list[0][0],
            'point1': landmark_list[1][0], 'point2': landmark_list[1][1], 'point3': landmark_list[1][2], 'point4': landmark_list[1][3],
            'point5': landmark_list[2][0], 'point6': landmark_list[2][1], 'point7': landmark_list[2][2], 'point8': landmark_list[2][3],
            'point9': landmark_list[3][0], 'point10': landmark_list[3][1], 'point11': landmark_list[3][2], 'point12': landmark_list[3][3],
            'point13': landmark_list[4][0], 'point14': landmark_list[4][1], 'point15': landmark_list[4][2], 'point16': landmark_list[4][3],
            'point17': landmark_list[5][0], 'point18': landmark_list[5][1], 'point19': landmark_list[5][2], 'point20': landmark_list[5][3]
        }

        # 调用函数，判断每根手指的弯曲或伸直状态
        bend_states, straighten_states = detect_all_finger_state(all_points)

        # 调用函数，检测当前手势
        current_state = detect_hand_state(all_points, bend_states, straighten_states)

        # 更新最近状态列表
        recent_states.pop(0)
        recent_states.append(current_state)

        # 检查列表中的所有状态是否相同（连续 30 帧稳定）
        if len(set(recent_states)) == 1:
            gesture = recent_states[0]
            print("Detected consistent hand state:", gesture)

            # 模拟调用无人机控制接口
            if gesture == "OK":
                ws_control.action_Forward()
                #Quadrotor_HTTP.action_Forward()
                print("Drone action: Move forward")
            elif gesture == "Return":
                ws_control.action_Backward()
                #Quadrotor_HTTP.action_Backward()
                print("Drone action: Move backward")
            elif gesture == "Left":
                ws_control.action_Left()
                #Quadrotor_HTTP.action_Left()
                print("Move left")
            elif gesture == "Right":
                ws_control.action_Right()
                #Quadrotor_HTTP.action_Right()
                print("Move right")
            elif gesture == "Thumbs_up":
                ws_control.action_Thumbs_Up()
                #Quadrotor_HTTP.action_Thumbs_Up()
                print("Hover")
            elif gesture == "Rotation":
                # ws_control.action_Pause()
                ws_control.action_Rotate()
                #Quadrotor_HTTP.action_Pause()
                print("Emergency stop")
            elif gesture == "Thumbs_Down":
                ws_control.action_Thumbs_Down()
                #Quadrotor_HTTP.action_Thumbs_Down()
                print("down")
            elif gesture == "Palm_No_Thumb":
                ws_control.action_Rotate(R=1.0)
                # print("Gesture: Palm_No_Thumb detected — perform custom action")

        # 绘制关键点
        for hand_landmarks in keypoints.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2))

    # 计算帧率并显示
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # 显示画面
    cv2.imshow("Hand Detection", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()