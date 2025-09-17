import asyncio
import json
from datetime import datetime
from typing import Optional, Callable, Dict, Any

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("警告: paho-mqtt 未安装，MQTT功能将不可用")
    mqtt = None

from app.core.config import settings
from app.core.websocket_manager import websocket_manager
from app.schemas.sensor import SensorDataPoint
from app.services.influx_service import InfluxService


class MQTTManager:
    """MQTT客户端管理器"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.reconnect_interval = 5  # 重连间隔（秒）
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
    
    async def connect(self):
        """连接到MQTT代理"""
        if not mqtt:
            print("MQTT库未安装，跳过MQTT连接")
            return
        
        try:
            self.client = mqtt.Client()
            
            # 设置回调函数
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # 设置用户名和密码（如果有）
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
            
            # 连接到MQTT代理
            self.client.connect_async(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                60
            )
            
            # 启动网络循环
            self.client.loop_start()
            
            print(f"正在连接到MQTT代理: {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            
        except Exception as e:
            print(f"MQTT连接失败: {e}")
    
    async def disconnect(self):
        """断开MQTT连接"""
        if self.client and self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            print("MQTT连接已断开")
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.is_connected = True
            self.reconnect_attempts = 0
            print("MQTT连接成功")
            
            # 订阅传感器数据主题
            topics = [
                f"{settings.MQTT_TOPIC_PREFIX}/+/data",  # 传感器数据
                f"{settings.MQTT_TOPIC_PREFIX}/+/status",  # 传感器状态
                f"{settings.MQTT_TOPIC_PREFIX}/gateway/+/heartbeat",  # 网关心跳
            ]
            
            for topic in topics:
                client.subscribe(topic)
                print(f"订阅主题: {topic}")
        else:
            print(f"MQTT连接失败，错误码: {rc}")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.is_connected = False
        print(f"MQTT连接断开，错误码: {rc}")
        
        # 自动重连
        if rc != 0 and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"尝试重连 ({self.reconnect_attempts}/{self.max_reconnect_attempts})...")
            asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """重连逻辑"""
        await asyncio.sleep(self.reconnect_interval)
        try:
            if self.client:
                self.client.reconnect()
        except Exception as e:
            print(f"重连失败: {e}")
    
    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"收到MQTT消息 - 主题: {topic}, 内容: {payload}")
            
            # 异步处理消息
            asyncio.create_task(self._handle_message(topic, payload))
            
        except Exception as e:
            print(f"处理MQTT消息失败: {e}")
    
    async def _handle_message(self, topic: str, payload: str):
        """处理接收到的消息"""
        try:
            # 解析JSON数据
            data = json.loads(payload)
            
            # 根据主题类型处理消息
            if "/data" in topic:
                await self._handle_sensor_data(topic, data)
            elif "/status" in topic:
                await self._handle_sensor_status(topic, data)
            elif "/heartbeat" in topic:
                await self._handle_gateway_heartbeat(topic, data)
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
        except Exception as e:
            print(f"消息处理失败: {e}")
    
    async def _handle_sensor_data(self, topic: str, data: dict):
        """处理传感器数据"""
        try:
            # 从主题中提取传感器ID
            topic_parts = topic.split('/')
            sensor_id = topic_parts[-2] if len(topic_parts) >= 2 else "unknown"
            
            # 创建传感器数据点
            data_point = SensorDataPoint(
                sensor_id=sensor_id,
                value=float(data.get('value', 0)),
                timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                quality=data.get('quality', 'good')
            )
            
            # 写入InfluxDB
            await InfluxService.write_sensor_data_batch([data_point])
            
            # 通过WebSocket广播数据
            await websocket_manager.broadcast_sensor_data(data_point)
            
            print(f"处理传感器数据: {sensor_id} = {data_point.value}")
            
        except Exception as e:
            print(f"处理传感器数据失败: {e}")
    
    async def _handle_sensor_status(self, topic: str, data: dict):
        """处理传感器状态"""
        try:
            topic_parts = topic.split('/')
            sensor_id = topic_parts[-2] if len(topic_parts) >= 2 else "unknown"
            
            status_message = {
                "type": "sensor_status",
                "sensor_id": sensor_id,
                "status": data.get('status', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
            
            # 广播状态更新
            await websocket_manager.broadcast_to_subscribers(status_message, sensor_id)
            
            print(f"传感器状态更新: {sensor_id} - {data.get('status')}")
            
        except Exception as e:
            print(f"处理传感器状态失败: {e}")
    
    async def _handle_gateway_heartbeat(self, topic: str, data: dict):
        """处理网关心跳"""
        try:
            topic_parts = topic.split('/')
            gateway_id = topic_parts[-2] if len(topic_parts) >= 2 else "unknown"
            
            heartbeat_message = {
                "type": "gateway_heartbeat",
                "gateway_id": gateway_id,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            # 广播心跳信息
            await websocket_manager.send_system_message("gateway_heartbeat", heartbeat_message)
            
            print(f"网关心跳: {gateway_id}")
            
        except Exception as e:
            print(f"处理网关心跳失败: {e}")
    
    async def publish(self, topic: str, payload: dict, qos: int = 0):
        """发布消息"""
        if not self.client or not self.is_connected:
            print("MQTT未连接，无法发布消息")
            return False
        
        try:
            message = json.dumps(payload, default=str)
            result = self.client.publish(topic, message, qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"消息发布成功 - 主题: {topic}")
                return True
            else:
                print(f"消息发布失败 - 主题: {topic}, 错误码: {result.rc}")
                return False
                
        except Exception as e:
            print(f"发布消息异常: {e}")
            return False
    
    async def publish_sensor_command(self, sensor_id: str, command: dict):
        """向传感器发送命令"""
        topic = f"{settings.MQTT_TOPIC_PREFIX}/{sensor_id}/command"
        return await self.publish(topic, command)
    
    def get_status(self) -> dict:
        """获取MQTT状态"""
        return {
            "connected": self.is_connected,
            "broker_host": settings.MQTT_BROKER_HOST,
            "broker_port": settings.MQTT_BROKER_PORT,
            "reconnect_attempts": self.reconnect_attempts
        }


# 全局MQTT管理器实例
mqtt_manager = MQTTManager()