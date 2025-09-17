from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime

from app.schemas.sensor import SensorDataPoint


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}  # 客户端订阅的传感器ID
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        print(f"客户端 {client_id} 已连接")
    
    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]
        print(f"客户端 {client_id} 已断开")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                print(f"发送消息给 {client_id} 失败: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        if self.active_connections:
            message_text = json.dumps(message, default=str)
            disconnected_clients = []
            
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(message_text)
                except Exception as e:
                    print(f"广播消息给 {client_id} 失败: {e}")
                    disconnected_clients.append(client_id)
            
            # 清理断开的连接
            for client_id in disconnected_clients:
                self.disconnect(client_id)
    
    async def broadcast_to_subscribers(self, message: dict, sensor_id: str):
        """向订阅了特定传感器的客户端广播消息"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message, default=str)
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            # 检查客户端是否订阅了该传感器
            if sensor_id in self.client_subscriptions.get(client_id, set()):
                try:
                    await websocket.send_text(message_text)
                except Exception as e:
                    print(f"发送传感器数据给 {client_id} 失败: {e}")
                    disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def subscribe_sensors(self, client_id: str, sensor_ids: List[str]):
        """订阅传感器数据"""
        if client_id not in self.client_subscriptions:
            self.client_subscriptions[client_id] = set()
        
        self.client_subscriptions[client_id].update(sensor_ids)
        print(f"客户端 {client_id} 订阅传感器: {sensor_ids}")
    
    async def unsubscribe_sensors(self, client_id: str, sensor_ids: List[str]):
        """取消订阅传感器数据"""
        if client_id in self.client_subscriptions:
            for sensor_id in sensor_ids:
                self.client_subscriptions[client_id].discard(sensor_id)
            print(f"客户端 {client_id} 取消订阅传感器: {sensor_ids}")
    
    async def broadcast_sensor_data(self, data: SensorDataPoint):
        """广播传感器数据"""
        message = {
            "type": "sensor_data",
            "data": {
                "sensor_id": data.sensor_id,
                "value": data.value,
                "timestamp": data.timestamp.isoformat(),
                "quality": data.quality
            }
        }
        
        # 向订阅了该传感器的客户端发送数据
        await self.broadcast_to_subscribers(message, data.sensor_id)
    
    async def send_system_message(self, message_type: str, content: dict):
        """发送系统消息"""
        message = {
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
        await self.broadcast(message)
    
    def get_connection_info(self) -> dict:
        """获取连接信息"""
        return {
            "total_connections": len(self.active_connections),
            "clients": {
                client_id: {
                    "subscribed_sensors": list(self.client_subscriptions.get(client_id, set()))
                }
                for client_id in self.active_connections.keys()
            }
        }


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()