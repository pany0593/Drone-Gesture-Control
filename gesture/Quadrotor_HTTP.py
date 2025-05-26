#!/usr/bin/env python3
import requests
import json
import time
import threading

# 服务地址配置
HOST = 'http://vd4856bb.natappfree.cc'
BASE_URL = HOST

# 后台请求函数
def _async_send_move(x, y, z, t):
    url = f"{BASE_URL}/move"
    payload = {
        'x': x,
        'y': y,
        'z': z,
        't': t
    }
    headers = {'Content-Type': 'application/json'}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        print(f"[MOVE] x={x}, y={y}, z={z}, t={t} => Response: {result}")
    except Exception as e:
        print(f"[MOVE] Request failed: {e}")

# 公共非阻塞调用函数
def send_move(x, y, z, t):
    print(f"x:{x} y:{y} z:{z} t={t} => Sending" )
    thread = threading.Thread(
        target=_async_send_move,
        args=(x, y, z, t),
        daemon=True
    )
    thread.start()

# 各动作封装函数
def action_Thumbs_Up(V=1.0, T=0.5):
    """上升：增加 z"""
    send_move(0, 0, V, T)

def action_Thumbs_Down(V=1.0, T=0.5):
    """下降：减少 z"""
    send_move(0, 0, -V, T)

def action_Left(V=1.0, T=0.5):
    """左移：减少 x"""
    send_move(-V, 0, 0, T)

def action_Right(V=1.0, T=0.5):
    """右移：增加 x"""
    send_move(V, 0, 0, T)

def action_Forward(V=1.0, T=0.5):
    """前移：增加 y"""
    send_move(0, V, 0, T)

def action_Backward(V=1.0, T=0.5):
    """后移：减少 y"""
    send_move(0, -V, 0, T)

def action_OK():
    """使能电机（可选择实现为空或作为初始化）"""
    print("[INFO] Motor enabled (假设已启动)")

def action_Pause():
    """暂停动作（可以用 t=0 表示）"""
    send_move(0, 0, 0, 0)