import websocket
import json
import threading
import time

class WebSocketControl:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.ws_lock = threading.Lock()
        self.ws_connected = threading.Event()  # 用于等待连接建立完成

    def on_message(self, wsapp, message):
        try:
            data = json.loads(message)
            print(f"[WS] 收到响应: {data}")
        except Exception as e:
            print(f"[WS] 消息解析失败: {e}, 原始消息: {message}")

    def on_error(self, wsapp, error):
        print(f"[WS] 错误: {error}")

    def on_close(self, wsapp, close_status_code, close_msg):
        print(f"[WS] 连接关闭: {close_status_code}, {close_msg}")
        self.ws_connected.clear()

    def on_open(self, wsapp):
        print("[WS] 已连接到服务器")
        self.ws_connected.set()

    def init_ws_connection(self):
        """初始化 WebSocket 连接并启动线程"""
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def send_move(self, x, y, z, r, t):
        """发送控制命令，包括线速度 (x,y,z)、角速度 r（绕 Z 轴）和持续时间 t"""

        def _send():
            if not self.ws_connected.wait(timeout=5):  # 最多等待 5 秒连接
                print("[MOVE] 等待连接超时，未发送命令")
                return
            # 构造包含 r 的消息
            msg = {"x": x, "y": y, "z": z, "r": r, "t": t}
            with self.ws_lock:
                try:
                    self.ws.send(json.dumps(msg))
                    print(f"[MOVE] 已发送命令: {msg}")
                except Exception as e:frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                print(f"[MOVE] WebSocket 发送失败: {e}")

        threading.Thread(target=_send, daemon=True).start()

    def action_palm(self, X, Y, V, R=0, T=0.5):
        self.send_move(X, Y, V, R, T)

    # 各动作封装函数
    def action_Thumbs_Up(self, V=2.0, T=0.05):
        # 纯线速度，无旋转
        self.send_move(0, 0, V, 0.0, T)

    def action_Thumbs_Down(self, V=2.0, T=0.05):
        self.send_move(0, 0, -V, 0.0, T)

    def action_Forward(self, V=2.0, T=0.05):
        self.send_move(-V, 0, 0, 0.0, T)

    def action_Backward(self, V=2.0, T=0.05):
        self.send_move(V, 0, 0, 0.0, T)

    def action_Right(self, V=2.0, T=0.05):
        self.send_move(0, V, 0, 0.0, T)

    def action_Left(self, V=2.0, T=0.05):
        self.send_move(0, -V, 0, 0.0, T)

    def action_OK(self):
        print("[INFO] 电机已启用（模拟）")

    def action_Pause(self):
        # 立即停止所有运动
        self.send_move(0, 0, 0, 0.0, 0.0)

    def action_Rotate(self, R=-1.0, T=0.02):
        self.send_move(0, 0, 0, R, T)


if __name__ == '__main__':
    ws_control = WebSocketControl(ws_url='ws://vd4856bb.natappfree.cc:5000')
    ws_control.init_ws_connection()
    time.sleep(2)  # 可视作初始化缓冲（真正控制是否连接好了由事件控制）
    ws_control.action_Forward()
    time.sleep(1)
    ws_control.action_Left()
    time.sleep(1)
    ws_control.action_Thumbs_Up()
