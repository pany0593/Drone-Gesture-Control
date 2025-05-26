#!/usr/bin/env python3
"""
ROS Python 节点：通过标准 WebSocket 接收线速度、角速度与持续时间，并通过 /cmd_vel 控制 Hector Quadrotor
"""
import asyncio
import json
import threading
import rospy
from geometry_msgs.msg import Twist
import websockets

controller = None

class QuadrotorController:
    def __init__(self):
        rospy.init_node('quadrotor_controller_ws')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.rate = rospy.Rate(20)
        self.lock = threading.Lock()
        self.current_cmd = Twist()
        self.end_time = rospy.Time.now()
        thread = threading.Thread(target=self._publish_loop)
        thread.daemon = True
        thread.start()

    def _publish_loop(self):
        while not rospy.is_shutdown():
            with self.lock:
                now = rospy.Time.now()
                # 如果当前时间早于结束时间，则发布命令，否则发布零速度命令
                cmd = self.current_cmd if now < self.end_time else Twist()
                self.pub.publish(cmd)
            self.rate.sleep()

    def set_command(self, x=0.0, y=0.0, z=0.0, r=0.0, t=0.0):
        """
        设置线速度 (x,y,z)、角速度 r（绕 Z 轴，r<0 逆时针，r>0 顺时针）
        并持续 t 秒
        """
        with self.lock:
            # 线速度
            self.current_cmd.linear.x = x
            self.current_cmd.linear.y = y
            self.current_cmd.linear.z = z
            # 角速度（绕 Z 轴）
            self.current_cmd.angular.z = r
            # 设置结束时间
            self.end_time = rospy.Time.now() + rospy.Duration(t)
            rospy.loginfo(
                f"[COMMAND] 设置速度 x={x}, y={y}, z={z}, r={r}, 持续 {t}s, 截止 {self.end_time.to_sec():.2f}"
            )

async def handle_client(websocket, path):
    """
    接收客户端发送的 JSON 格式控制命令: {"x": float, "y": float, "z": float, "r": float, "t": float}
    r: 角速度，r<0 逆时针，r>0 顺时针
    """
    client_ip = websocket.remote_address[0]
    rospy.loginfo(f"[WebSocket] 客户端已连接：{client_ip}")

    async for message in websocket:
        try:
            data = json.loads(message)
            x = float(data.get("x", 0.0))
            y = float(data.get("y", 0.0))
            z = float(data.get("z", 0.0))
            r = float(data.get("r", 0.0))
            t = float(data.get("t", 0.0))
            controller.set_command(x, y, z, r, t)
            # 回传已设置的命令状态
            await websocket.send(json.dumps({
                "status": "ok", "x": x, "y": y, "z": z, "r": r, "t": t
            }))
        except Exception as e:
            rospy.logerr(f"[WebSocket] 指令解析或执行失败: {e}")
            await websocket.send(json.dumps({"error": str(e)}))


def start_websocket_server():
    rospy.loginfo("[STARTUP] WebSocket 服务已启动，监听端口 5000")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(handle_client, "0.0.0.0", 5000)
    loop.run_until_complete(server)
    loop.run_forever()


if __name__ == '__main__':
    try:
        controller = QuadrotorController()
        server_thread = threading.Thread(target=start_websocket_server)
        server_thread.daemon = True
        server_thread.start()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
