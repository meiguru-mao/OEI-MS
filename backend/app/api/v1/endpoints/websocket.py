from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
import json
import asyncio
from datetime import datetime

from app.core.websocket_manager import websocket_manager
from app.schemas.sensor import SensorDataPoint

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接端点"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            if message.get("type") == "subscribe":
                # 订阅特定传感器数据
                sensor_ids = message.get("sensor_ids", [])
                await websocket_manager.subscribe_sensors(client_id, sensor_ids)
                await websocket_manager.send_personal_message(
                    {"type": "subscription_confirmed", "sensor_ids": sensor_ids},
                    client_id
                )
            
            elif message.get("type") == "unsubscribe":
                # 取消订阅
                sensor_ids = message.get("sensor_ids", [])
                await websocket_manager.unsubscribe_sensors(client_id, sensor_ids)
                await websocket_manager.send_personal_message(
                    {"type": "unsubscription_confirmed", "sensor_ids": sensor_ids},
                    client_id
                )
            
            elif message.get("type") == "ping":
                # 心跳检测
                await websocket_manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    client_id
                )
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        print(f"客户端 {client_id} 断开连接")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        websocket_manager.disconnect(client_id)


@router.websocket("/ws/broadcast")
async def broadcast_websocket(websocket: WebSocket):
    """广播WebSocket连接（接收所有传感器数据）"""
    await websocket.accept()
    client_id = f"broadcast_{id(websocket)}"
    websocket_manager.active_connections[client_id] = websocket
    
    try:
        while True:
            # 保持连接活跃
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }))
    
    except WebSocketDisconnect:
        if client_id in websocket_manager.active_connections:
            del websocket_manager.active_connections[client_id]
        print(f"广播客户端 {client_id} 断开连接")
    except Exception as e:
        print(f"广播WebSocket错误: {e}")
        if client_id in websocket_manager.active_connections:
            del websocket_manager.active_connections[client_id]


# 用于测试的数据推送接口
@router.post("/test/push")
async def test_push_data(data: SensorDataPoint):
    """测试数据推送"""
    await websocket_manager.broadcast_sensor_data(data)
    return {"message": "数据推送成功"}


@router.get("/connections")
async def get_active_connections():
    """获取活跃连接数"""
    return {
        "active_connections": len(websocket_manager.active_connections),
        "client_ids": list(websocket_manager.active_connections.keys())
    }