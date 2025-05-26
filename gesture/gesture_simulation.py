import cv2
import mediapipe as mp
import numpy as np

import Quadrotor_websocket

def init_gesture_detector():
    """初始化手势检测模型"""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    return hands, mp_draw


# 全局变量用于低通滤波
prev_throttle = 0
prev_roll = 0
prev_pitch = 0
prev_throttle_x = 0

def detect_gesture(frame, hands, mp_draw=None):
    """
    核心手势识别函数（完整修正版）
    :param frame: BGR格式输入帧
    :param hands: 初始化后的手势模型
    :param mp_draw: 绘图工具（可选）
    :return: 控制指令字典 + 绘制后的帧
    """
    global prev_throttle, prev_roll, prev_pitch,prev_throttle_x

    # 默认控制指令
    control = {
        'throttle': 0,  # 垂直方向：-100~100
        'throttle_x':0, # 水平位置：用来判断是否旋转
        'roll': 0,  # 左右方向：-50~50
        'pitch': 0,  # 前后方向：-50~50
        'emergency_stop': False  # 急停标志
    }

    # ==================== 参数配置 ====================
    THROTTLE_DEADZONE = 0.15  # 油门死区（原0.1→0.15）
    DEADZONE_X = 0.15  # 新增：水平方向死区
    ROLL_DEADZONE = 0.1  # 横滚死区（原0.05→0.1）
    PITCH_DEADZONE = 0.1  # 俯仰死区（原0.05→0.1）
    EMERGENCY_STOP_DISTANCE = 0.05  # 握拳急停阈值
    SMOOTHING_FACTOR = 0.3  # 低通滤波系数（0~1，值越大越平滑）

    # ==================== 画面处理 ====================
    # 绘制参考线（中心±0.4窗口位置）
    # h, w = frame.shape[:2]
    # cv2.line(frame, (int(w * 0.1), 0, (int(w * 0.1), h), (0, 255, 0), 1))  # 左竖线
    # cv2.line(frame, (int(w * 0.9), 0, (int(w * 0.9), h), (0, 255, 0), 1))  # 右竖线
    # cv2.line(frame, (0, int(h * 0.1)), (w, int(h * 0.1)), (0, 255, 0), 1)  # 上横线
    # cv2.line(frame, (0, int(h * 0.9)), (w, int(h * 0.9)), (0, 255, 0), 1)  # 下横线

    # ==================== 手势检测 ====================
    # 转换颜色空间
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = hand_landmarks.landmark
        h, w = frame.shape[:2]

        # 绘制关键点（可选）
        if mp_draw is not None:
            mp_draw.draw_landmarks(
                frame, hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS
            )

        # ==================== 油门控制 ====================
        # 计算手掌中心水平位置
        palm_center_x = np.mean([lm.x for lm in landmarks])
        throttle_x_raw = (palm_center_x - 0.5) * 2  # [-1,1]
        # 计算手掌中心垂直位置（归一化到0~1）
        palm_center_y = np.mean([lm.y for lm in landmarks])
        # 映射到[-1, 1]，中心为0，上移为正，下移为负
        throttle_raw = (0.5 - palm_center_y) * 2

        # ==================== 横滚控制 ====================
        # 获取食指指尖和手腕坐标
        index_tip = landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        wrist = landmarks[mp.solutions.hands.HandLandmark.WRIST]

        # 计算食指相对于手腕的偏移量
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y

        # 计算倾斜角度并反转方向（修复左右反向问题）
        angle = np.arctan2(dy, dx)
        roll_raw = -np.sin(angle)  # 添加负号修复方向

        # ==================== 俯仰控制 ====================
        # 计算俯仰并反转方向（修复前后反向问题）
        pitch_raw = -np.cos(angle)  # 添加负号修复方向

        # ==================== 急停检测 ====================
        # 计算拇指尖端与根部的距离（握拳检测）
        thumb_tip = landmarks[mp.solutions.hands.HandLandmark.THUMB_TIP]
        thumb_mcp = landmarks[mp.solutions.hands.HandLandmark.THUMB_MCP]
        distance = np.hypot(
            thumb_tip.x - thumb_mcp.x,
            thumb_tip.y - thumb_mcp.y
        )

        # ==================== 控制逻辑 ====================
        if distance < EMERGENCY_STOP_DISTANCE:
            # 急停：所有控制量归零
            control.update({
                'throttle': 0,
                'throttle_x':0,
                'roll': 0,
                'pitch': 0,
                'emergency_stop': True
            })
        else:
            # ------------ 油门处理 ------------
            if abs(throttle_raw) > THROTTLE_DEADZONE:
                control['throttle'] = int(throttle_raw * 100)
            else:
                control['throttle'] = 0  # 死区内归零

            # -------------处理水平位置----------
            if abs(throttle_x_raw) > DEADZONE_X:
                control['throttle_x'] = int(throttle_x_raw * 100)
            else:
                control['throttle_x'] = 0

            # ------------ 横滚处理 ------------
            if abs(roll_raw) > ROLL_DEADZONE:
                control['roll'] = int(roll_raw * 50)
            else:
                control['roll'] = 0

            # ------------ 俯仰处理 ------------
            if abs(pitch_raw) > PITCH_DEADZONE:
                control['pitch'] = int(pitch_raw * 50)
            else:
                control['pitch'] = 0

            # ====== 低通滤波（抑制微小扰动） ======
            control['throttle'] = int(
                prev_throttle * (1 - SMOOTHING_FACTOR) +
                control['throttle'] * SMOOTHING_FACTOR
            )
            control['roll'] = int(
                prev_roll * (1 - SMOOTHING_FACTOR) +
                control['roll'] * SMOOTHING_FACTOR
            )
            control['pitch'] = int(
                prev_pitch * (1 - SMOOTHING_FACTOR) +
                control['pitch'] * SMOOTHING_FACTOR
            )

            control['throttle_x'] = int(
                prev_throttle_x * (1 - SMOOTHING_FACTOR) +
                control['throttle_x'] * SMOOTHING_FACTOR
            )

            # 更新历史值
            prev_throttle = control['throttle']
            prev_roll = control['roll']
            prev_pitch = control['pitch']
            prev_throttle_x = control['throttle_x']

    return control, frame


# ==================== 测试主程序 ====================
if __name__ == "__main__":

    ws_control = Quadrotor_websocket.WebSocketControl(ws_url='ws://192.168.24.136:5000')
    ws_control.init_ws_connection()

    hands, mp_draw = init_gesture_detector()
    cap = cv2.VideoCapture(0)  # 打开默认摄像头

    # 新增帧率控制参数
    TARGET_FPS = 20  # 目标帧率(每秒处理20帧)
    PROCESS_INTERVAL = 1.0 / TARGET_FPS  # 处理间隔(秒)
    last_process_time = 0  # 上次处理时间戳

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 镜像画面（更符合直觉）
        frame = cv2.flip(frame, 1)

        # 先把画面顺时针旋转 90°
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # 调用手势识别函数
        control, vis_frame = detect_gesture(frame, hands, mp_draw)

        # 在画面叠加控制信息
        cv2.putText(
            vis_frame,
            f"Throttle: {control['throttle']}",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        cv2.putText(
            vis_frame,
            f"Roll: {control['roll']}",
            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        cv2.putText(
            vis_frame,
            f"Pitch: {control['pitch']}",
            (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        cv2.putText(
            vis_frame,
            "Emergency Stop: {}".format(control['emergency_stop']),
            (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
        )
        # 显示水平位置信息
        cv2.putText(
            vis_frame,
            f"Horizontal: {control['throttle_x']}",
            (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2
        )

        # 显示画面
        cv2.imshow('Gesture Control', vis_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if (abs(control['roll']) < 20):
            x = 0
        else:
            x = control['roll'] / 50 * 2.0
        if (abs(control['pitch']) < 20):
            y = 0
        else:
            y = control['pitch'] / 50 * 2.0
        if abs(control['throttle']) < 15:
            z = 0
        else:
            z = control['throttle'] / 100 * 2.0
        if abs(control['throttle_x'])>15:
            r=y/10
        else:
            r=0
        t = 0.05

        # === 新增：时间戳控制 ===
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        if current_time - last_process_time < PROCESS_INTERVAL:
            # 未到处理时间，跳过检测
            cv2.imshow('Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        last_process_time = current_time  # 更新处理时间
        print(x,y,z,r)
        ws_control.action_palm(-x*5, -y*5, z*5, r*5)


    # 释放资源
    cap.release()
    cv2.destroyAllWindows()