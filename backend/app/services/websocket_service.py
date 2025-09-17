import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Any
from weakref import WeakSet

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 使用WeakSet自动清理断开的连接
        self.active_connections: Set[WebSocket] = WeakSet()
        self.connection_info: Dict[WebSocket, dict] = {}
        self.room_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
        # 统计信息
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_failed": 0,
            "rooms_created": 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None, room: Optional[str] = None):
        """接受WebSocket连接"""
        try:
            await websocket.accept()
            
            # 添加到活跃连接
            self.active_connections.add(websocket)
            
            # 记录连接信息
            self.connection_info[websocket] = {
                "user_id": user_id,
                "room": room,
                "connected_at": datetime.now(timezone.utc),
                "last_ping": datetime.now(timezone.utc),
                "messages_received": 0,
                "messages_sent": 0
            }
            
            # 加入房间
            if room:
                await self._join_room(websocket, room)
            
            # 关联用户
            if user_id:
                await self._associate_user(websocket, user_id)
            
            # 更新统计
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = len(self.active_connections)
            
            logger.info(f"WebSocket连接建立: 用户={user_id}, 房间={room}, 总连接数={self.stats['active_connections']}")
            
            # 发送欢迎消息
            await self.send_personal_message(websocket, {
                "type": "connection_established",
                "message": "WebSocket连接已建立",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            raise
    
    async def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        try:
            # 获取连接信息
            info = self.connection_info.get(websocket, {})
            user_id = info.get("user_id")
            room = info.get("room")
            
            # 从活跃连接中移除
            self.active_connections.discard(websocket)
            
            # 从房间中移除
            if room and room in self.room_connections:
                self.room_connections[room].discard(websocket)
                if not self.room_connections[room]:
                    del self.room_connections[room]
            
            # 从用户连接中移除
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # 清理连接信息
            if websocket in self.connection_info:
                del self.connection_info[websocket]
            
            # 更新统计
            self.stats["active_connections"] = len(self.active_connections)
            
            logger.info(f"WebSocket连接断开: 用户={user_id}, 房间={room}, 剩余连接数={self.stats['active_connections']}")
            
        except Exception as e:
            logger.error(f"断开WebSocket连接失败: {e}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """发送个人消息"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                
                # 更新统计
                if websocket in self.connection_info:
                    self.connection_info[websocket]["messages_sent"] += 1
                self.stats["messages_sent"] += 1
                
                return True
            else:
                logger.warning("WebSocket连接已断开，无法发送消息")
                return False
                
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")
            self.stats["messages_failed"] += 1
            
            # 清理断开的连接
            await self.disconnect(websocket)
            return False
    
    async def broadcast(self, message: dict, exclude: Optional[Set[WebSocket]] = None):
        """广播消息给所有连接"""
        if not self.active_connections:
            return
        
        exclude = exclude or set()
        failed_connections = set()
        success_count = 0
        
        # 并发发送消息
        tasks = []
        for connection in self.active_connections:
            if connection not in exclude:
                tasks.append(self._send_with_error_handling(connection, message))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_connections.add(list(self.active_connections)[i])
                elif result:
                    success_count += 1
        
        # 清理失败的连接
        for connection in failed_connections:
            await self.disconnect(connection)
        
        logger.debug(f"广播消息: 成功={success_count}, 失败={len(failed_connections)}")
    
    async def broadcast_to_room(self, room: str, message: dict, exclude: Optional[Set[WebSocket]] = None):
        """向房间广播消息"""
        if room not in self.room_connections:
            logger.warning(f"房间不存在: {room}")
            return
        
        exclude = exclude or set()
        room_connections = self.room_connections[room] - exclude
        
        if not room_connections:
            return
        
        failed_connections = set()
        success_count = 0
        
        # 并发发送消息
        tasks = [self._send_with_error_handling(conn, message) for conn in room_connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            connection = list(room_connections)[i]
            if isinstance(result, Exception):
                failed_connections.add(connection)
            elif result:
                success_count += 1
        
        # 清理失败的连接
        for connection in failed_connections:
            await self.disconnect(connection)
        
        logger.debug(f"房间广播 [{room}]: 成功={success_count}, 失败={len(failed_connections)}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """发送消息给特定用户的所有连接"""
        if user_id not in self.user_connections:
            logger.warning(f"用户不在线: {user_id}")
            return False
        
        user_connections = self.user_connections[user_id].copy()
        failed_connections = set()
        success_count = 0
        
        # 并发发送消息
        tasks = [self._send_with_error_handling(conn, message) for conn in user_connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            connection = list(user_connections)[i]
            if isinstance(result, Exception):
                failed_connections.add(connection)
            elif result:
                success_count += 1
        
        # 清理失败的连接
        for connection in failed_connections:
            await self.disconnect(connection)
        
        logger.debug(f"用户消息 [{user_id}]: 成功={success_count}, 失败={len(failed_connections)}")
        return success_count > 0
    
    async def _send_with_error_handling(self, websocket: WebSocket, message: dict) -> bool:
        """带错误处理的消息发送"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                
                # 更新统计
                if websocket in self.connection_info:
                    self.connection_info[websocket]["messages_sent"] += 1
                self.stats["messages_sent"] += 1
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self.stats["messages_failed"] += 1
            raise e
    
    async def _join_room(self, websocket: WebSocket, room: str):
        """加入房间"""
        if room not in self.room_connections:
            self.room_connections[room] = WeakSet()
            self.stats["rooms_created"] += 1
        
        self.room_connections[room].add(websocket)
        logger.debug(f"WebSocket加入房间: {room}")
    
    async def _associate_user(self, websocket: WebSocket, user_id: str):
        """关联用户"""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = WeakSet()
        
        self.user_connections[user_id].add(websocket)
        logger.debug(f"WebSocket关联用户: {user_id}")
    
    async def change_room(self, websocket: WebSocket, new_room: str):
        """更换房间"""
        info = self.connection_info.get(websocket, {})
        old_room = info.get("room")
        
        # 离开旧房间
        if old_room and old_room in self.room_connections:
            self.room_connections[old_room].discard(websocket)
            if not self.room_connections[old_room]:
                del self.room_connections[old_room]
        
        # 加入新房间
        await self._join_room(websocket, new_room)
        
        # 更新连接信息
        if websocket in self.connection_info:
            self.connection_info[websocket]["room"] = new_room
        
        logger.info(f"WebSocket更换房间: {old_room} -> {new_room}")
    
    async def ping_all(self):
        """向所有连接发送ping"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast(ping_message)
    
    def get_connection_info(self, websocket: WebSocket) -> dict:
        """获取连接信息"""
        return self.connection_info.get(websocket, {})
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "active_connections": len(self.active_connections),
            "active_rooms": len(self.room_connections),
            "active_users": len(self.user_connections)
        }
    
    def get_room_info(self) -> Dict[str, int]:
        """获取房间信息"""
        return {room: len(connections) for room, connections in self.room_connections.items()}
    
    def get_user_info(self) -> Dict[str, int]:
        """获取用户信息"""
        return {user: len(connections) for user, connections in self.user_connections.items()}


class WebSocketService:
    """WebSocket服务类"""
    
    def __init__(self):
        self.manager = ConnectionManager()
        self.message_handlers: Dict[str, List[callable]] = {}
        self.is_running = False
        
        # 注册默认消息处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认消息处理器"""
        self.add_message_handler("ping", self._handle_ping)
        self.add_message_handler("join_room", self._handle_join_room)
        self.add_message_handler("leave_room", self._handle_leave_room)
        self.add_message_handler("get_stats", self._handle_get_stats)
    
    async def start(self):
        """启动WebSocket服务"""
        if self.is_running:
            logger.warning("WebSocket服务已在运行")
            return
        
        self.is_running = True
        logger.info("WebSocket服务启动成功")
        
        # 启动定期ping任务
        asyncio.create_task(self._ping_loop())
    
    async def stop(self):
        """停止WebSocket服务"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 断开所有连接
        connections = list(self.manager.active_connections)
        for connection in connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"关闭WebSocket连接失败: {e}")
        
        logger.info("WebSocket服务已停止")
    
    async def handle_connection(self, websocket: WebSocket, user_id: Optional[str] = None, room: Optional[str] = None):
        """处理WebSocket连接"""
        try:
            # 建立连接
            await self.manager.connect(websocket, user_id, room)
            
            # 消息处理循环
            while True:
                try:
                    # 接收消息
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # 更新连接信息
                    if websocket in self.manager.connection_info:
                        self.manager.connection_info[websocket]["messages_received"] += 1
                        self.manager.connection_info[websocket]["last_ping"] = datetime.now(timezone.utc)
                    
                    # 处理消息
                    await self._handle_message(websocket, message)
                    
                except WebSocketDisconnect:
                    logger.info("WebSocket客户端主动断开连接")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    await self.manager.send_personal_message(websocket, {
                        "type": "error",
                        "message": "消息格式错误",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except Exception as e:
                    logger.error(f"处理WebSocket消息失败: {e}")
                    await self.manager.send_personal_message(websocket, {
                        "type": "error",
                        "message": "服务器内部错误",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
        
        except Exception as e:
            logger.error(f"WebSocket连接处理失败: {e}")
        
        finally:
            # 断开连接
            await self.manager.disconnect(websocket)
    
    async def _handle_message(self, websocket: WebSocket, message: dict):
        """处理接收到的消息"""
        message_type = message.get("type")
        if not message_type:
            await self.manager.send_personal_message(websocket, {
                "type": "error",
                "message": "消息类型不能为空",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return
        
        # 查找消息处理器
        handlers = self.message_handlers.get(message_type, [])
        if not handlers:
            logger.warning(f"未找到消息处理器: {message_type}")
            await self.manager.send_personal_message(websocket, {
                "type": "error",
                "message": f"不支持的消息类型: {message_type}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return
        
        # 执行处理器
        for handler in handlers:
            try:
                await handler(websocket, message)
            except Exception as e:
                logger.error(f"消息处理器执行失败: {e}")
    
    async def _handle_ping(self, websocket: WebSocket, message: dict):
        """处理ping消息"""
        await self.manager.send_personal_message(websocket, {
            "type": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def _handle_join_room(self, websocket: WebSocket, message: dict):
        """处理加入房间消息"""
        room = message.get("room")
        if not room:
            await self.manager.send_personal_message(websocket, {
                "type": "error",
                "message": "房间名不能为空",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return
        
        await self.manager.change_room(websocket, room)
        await self.manager.send_personal_message(websocket, {
            "type": "room_joined",
            "room": room,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def _handle_leave_room(self, websocket: WebSocket, message: dict):
        """处理离开房间消息"""
        await self.manager.change_room(websocket, "default")
        await self.manager.send_personal_message(websocket, {
            "type": "room_left",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def _handle_get_stats(self, websocket: WebSocket, message: dict):
        """处理获取统计信息消息"""
        stats = self.manager.get_stats()
        await self.manager.send_personal_message(websocket, {
            "type": "stats",
            "data": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def _ping_loop(self):
        """定期ping循环"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # 每30秒ping一次
                if self.manager.active_connections:
                    await self.manager.ping_all()
            except Exception as e:
                logger.error(f"Ping循环错误: {e}")
                await asyncio.sleep(5)
    
    async def broadcast(self, message: dict, exclude: Optional[Set[WebSocket]] = None):
        """广播消息"""
        await self.manager.broadcast(message, exclude)
    
    async def broadcast_to_room(self, room: str, message: dict, exclude: Optional[Set[WebSocket]] = None):
        """向房间广播消息"""
        await self.manager.broadcast_to_room(room, message, exclude)
    
    async def send_to_user(self, user_id: str, message: dict):
        """发送消息给用户"""
        return await self.manager.send_to_user(user_id, message)
    
    def add_message_handler(self, message_type: str, handler: callable):
        """添加消息处理器"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def remove_message_handler(self, message_type: str, handler: callable):
        """移除消息处理器"""
        if message_type in self.message_handlers:
            try:
                self.message_handlers[message_type].remove(handler)
            except ValueError:
                pass
    
    def get_stats(self) -> dict:
        """获取服务统计信息"""
        return self.manager.get_stats()
    
    def get_connection_count(self) -> int:
        """获取连接数"""
        return len(self.manager.active_connections)


# 全局WebSocket服务实例
websocket_service = WebSocketService()