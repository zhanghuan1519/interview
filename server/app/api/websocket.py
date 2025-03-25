from typing import List, Dict
import cv2
import mediapipe as mp
import time
import asyncio
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# 初始化 MediaPipe Pose 和 Face Detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/video/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    data = None
    alarm_triggered = False
    last_face_detected_time = time.time()
    await manager.connect(websocket, client_id)
    
    async def send_heartbeat():
        while True:
            await asyncio.sleep(30)  # 每30秒发送一次心跳消息
            await manager.send_message(client_id, "heartbeat")

    heartbeat_task = asyncio.create_task(send_heartbeat())
    
    try:
        while True:
            data = await websocket.receive()
            if data["type"] == "websocket.receive":
                if "bytes" in data:
                    data = data["bytes"]  # 处理二进制数据
                elif "text" in data:
                    data = data["text"]   # 处理文本数据
                    continue
            elif data["type"] == "websocket.disconnect":
                manager.disconnect(client_id)
                return
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 转换为RGB格式并检测
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = face_detection.process(rgb_frame)
            
            # 检测人脸
            if face_results.detections:
                last_face_detected_time = time.time()
                alarm_triggered = False
            else:
                # 如果超过2秒没有检测到人脸，则触发报警
                if time.time() - last_face_detected_time > 2:
                    if not alarm_triggered:
                        await manager.send_message(client_id, "报警：屏幕内没有检测到人脸！")
                        alarm_triggered = True
    except WebSocketDisconnect as ee:
        print(f"ERROR: {ee}")
        manager.disconnect(client_id)
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(client_id)
    finally:
        heartbeat_task.cancel()