import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any

import paho.mqtt.client as mqtt
from influxdb_client import Point
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, get_write_api, get_redis
from app.models import Sensor, Gateway
from .websocket_service import WebSocketService

logger = logging.getLogger(__name__)


class MQTTService:
    """MQTT服务类，处理设备数据接收和转发"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.is_running = False
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.websocket_service = WebSocketService()
        self.reconnect_interval = 5  # 重连间隔（秒）
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        # 统计信息
        self.stats = {
            "messages_received": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            "last_message_time": None,
            "connected_since": None
        }
    
    async def start(self):
        """启动MQTT服务"""
        if self.is_running:
            logger.warning("MQTT服务已在运行")
            return
        
        logger.info("启动MQTT服务...")
        self.is_running = True
        
        try:
            await self._setup_client()
            await self._connect()
            
            # 启动消息处理循环
            asyncio.create_task(self._message_loop())
            
            logger.info("MQTT服务启动成功")
        except Exception as e:
            logger.error(f"启动MQTT服务失败: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """停止MQTT服务"""
        if not self.is_running:
            return
        
        logger.info("停止MQTT服务...")
        self.is_running = False
        
        if self.client and self.is_connected:
            try:
                self.client.disconnect()
                self.client.loop_stop()
            except Exception as e:
                logger.error(f"断开MQTT连接失败: {e}")
        
        self.is_connected = False
        logger.info("MQTT服务已停止")
    
    async def _setup_client(self):
        """设置MQTT客户端"""
        self.client = mqtt.Client(
            client_id=f"oei_ms_server_{datetime.now().timestamp()}",
            protocol=mqtt.MQTTv311
        )
        
        # 设置认证
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        
        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_unsubscribe = self._on_unsubscribe
        
        # 设置连接选项
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        logger.info(f"MQTT客户端配置完成，服务器: {settings.MQTT_HOST}:{settings.MQTT_PORT}")
    
    async def _connect(self):
        """连接到MQTT代理"""
        try:
            logger.info(f"连接到MQTT代理 {settings.MQTT_HOST}:{settings.MQTT_PORT}")
            
            # 异步连接
            result = self.client.connect_async(
                settings.MQTT_HOST,
                settings.MQTT_PORT,
                keepalive=settings.MQTT_KEEPALIVE
            )
            
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"MQTT连接失败，错误码: {result}")
            
            # 启动网络循环
            self.client.loop_start()
            
            # 等待连接建立
            for _ in range(30):  # 最多等待30秒
                if self.is_connected:
                    break
                await asyncio.sleep(1)
            
            if not self.is_connected:
                raise Exception("MQTT连接超时")
            
            self.reconnect_attempts = 0
            
        except Exception as e:
            logger.error(f"MQTT连接失败: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.is_connected = True
            self.stats["connected_since"] = datetime.now(timezone.utc)
            logger.info("MQTT连接成功")
            
            # 订阅主题
            asyncio.create_task(self._subscribe_topics())
            
        else:
            self.is_connected = False
            error_messages = {
                1: "协议版本不正确",
                2: "客户端标识符无效",
                3: "服务器不可用",
                4: "用户名或密码错误",
                5: "未授权"
            }
            error_msg = error_messages.get(rc, f"未知错误 ({rc})")
            logger.error(f"MQTT连接失败: {error_msg}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.is_connected = False
        
        if rc != 0:
            logger.warning(f"MQTT意外断开连接，错误码: {rc}")
            
            # 自动重连
            if self.is_running and self.reconnect_attempts < self.max_reconnect_attempts:
                self.reconnect_attempts += 1
                logger.info(f"尝试重连 ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
                asyncio.create_task(self._reconnect())
            else:
                logger.error("达到最大重连次数，停止重连")
        else:
            logger.info("MQTT正常断开连接")
    
    async def _reconnect(self):
        """重连逻辑"""
        await asyncio.sleep(self.reconnect_interval)
        
        if self.is_running and not self.is_connected:
            try:
                await self._connect()
            except Exception as e:
                logger.error(f"重连失败: {e}")
    
    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            self.stats["messages_received"] += 1
            self.stats["last_message_time"] = datetime.now(timezone.utc)
            
            # 异步处理消息
            asyncio.create_task(self._process_message(msg.topic, msg.payload))
            
        except Exception as e:
            logger.error(f"处理MQTT消息失败: {e}")
            self.stats["messages_failed"] += 1
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """订阅成功回调"""
        logger.info(f"订阅成功，消息ID: {mid}, QoS: {granted_qos}")
    
    def _on_unsubscribe(self, client, userdata, mid):
        """取消订阅回调"""
        logger.info(f"取消订阅成功，消息ID: {mid}")
    
    async def _subscribe_topics(self):
        """订阅主题"""
        try:
            # 订阅所有传感器数据主题
            topics = [
                ("sensors/+/data", 1),  # 传感器数据
                ("sensors/+/status", 1),  # 传感器状态
                ("gateways/+/heartbeat", 1),  # 网关心跳
                ("gateways/+/status", 1),  # 网关状态
                ("system/+/alert", 1),  # 系统告警
            ]
            
            for topic, qos in topics:
                result, mid = self.client.subscribe(topic, qos)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"订阅主题: {topic} (QoS: {qos})")
                else:
                    logger.error(f"订阅主题失败: {topic}, 错误码: {result}")
            
        except Exception as e:
            logger.error(f"订阅主题失败: {e}")
    
    async def _process_message(self, topic: str, payload: bytes):
        """处理接收到的消息"""
        try:
            # 解析消息
            message_str = payload.decode('utf-8')
            message_data = json.loads(message_str)
            
            logger.debug(f"收到消息 - 主题: {topic}, 数据: {message_data}")
            
            # 根据主题类型处理消息
            if "/data" in topic:
                await self._handle_sensor_data(topic, message_data)
            elif "/status" in topic:
                await self._handle_status_message(topic, message_data)
            elif "/heartbeat" in topic:
                await self._handle_heartbeat(topic, message_data)
            elif "/alert" in topic:
                await self._handle_alert(topic, message_data)
            else:
                logger.warning(f"未知主题类型: {topic}")
            
            self.stats["messages_processed"] += 1
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始数据: {payload}")
            self.stats["messages_failed"] += 1
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            self.stats["messages_failed"] += 1
    
    async def _handle_sensor_data(self, topic: str, data: dict):
        """处理传感器数据"""
        try:
            # 从主题中提取设备ID
            device_id = topic.split('/')[1]
            
            # 获取数据库会话
            db = next(get_db())
            
            try:
                # 查找传感器
                sensor = db.query(Sensor).filter(Sensor.device_id == device_id).first()
                if not sensor:
                    logger.warning(f"未找到传感器: {device_id}")
                    return
                
                # 提取数据字段
                value = data.get('value')
                timestamp = data.get('timestamp')
                quality = data.get('quality', 'good')
                
                if value is None:
                    logger.warning(f"传感器数据缺少value字段: {device_id}")
                    return
                
                # 解析时间戳
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        else:
                            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    except Exception as e:
                        logger.warning(f"时间戳解析失败: {e}, 使用当前时间")
                        dt = datetime.now(timezone.utc)
                else:
                    dt = datetime.now(timezone.utc)
                
                # 更新传感器状态
                sensor.update_data_stats(str(value))
                sensor.status = "online"
                db.commit()
                
                # 写入InfluxDB
                await self._write_to_influxdb(sensor, value, dt, quality)
                
                # 缓存到Redis
                await self._cache_sensor_data(sensor, value, dt)
                
                # 检查报警条件
                if isinstance(value, (int, float)):
                    alarms = sensor.check_alarm_conditions(float(value))
                    if alarms:
                        await self._handle_alarms(alarms)
                
                # 通过WebSocket广播数据
                await self._broadcast_sensor_data(sensor, value, dt)
                
                logger.debug(f"处理传感器数据成功: {device_id} = {value}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"处理传感器数据失败: {e}")
    
    async def _handle_status_message(self, topic: str, data: dict):
        """处理状态消息"""
        try:
            device_id = topic.split('/')[1]
            status = data.get('status', 'unknown')
            
            db = next(get_db())
            try:
                if 'sensors' in topic:
                    # 传感器状态
                    sensor = db.query(Sensor).filter(Sensor.device_id == device_id).first()
                    if sensor:
                        error_message = data.get('error')
                        sensor.update_status(status, error_message)
                        db.commit()
                        
                        # 广播状态更新
                        await self.websocket_service.broadcast({
                            "type": "sensor_status",
                            "sensor_id": sensor.id,
                            "device_id": device_id,
                            "status": status,
                            "error": error_message,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                
                elif 'gateways' in topic:
                    # 网关状态
                    gateway = db.query(Gateway).filter(Gateway.device_id == device_id).first()
                    if gateway:
                        gateway.update_status(status)
                        db.commit()
                        
                        # 广播状态更新
                        await self.websocket_service.broadcast({
                            "type": "gateway_status",
                            "gateway_id": gateway.id,
                            "device_id": device_id,
                            "status": status,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
            
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"处理状态消息失败: {e}")
    
    async def _handle_heartbeat(self, topic: str, data: dict):
        """处理心跳消息"""
        try:
            device_id = topic.split('/')[1]
            
            db = next(get_db())
            try:
                gateway = db.query(Gateway).filter(Gateway.device_id == device_id).first()
                if gateway:
                    gateway.status = "online"
                    gateway.last_seen = datetime.now(timezone.utc)
                    
                    # 更新运行时间
                    if 'uptime' in data:
                        gateway.uptime = data['uptime']
                    
                    # 更新统计信息
                    gateway.update_statistics()
                    db.commit()
                    
                    logger.debug(f"处理网关心跳: {device_id}")
            
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"处理心跳消息失败: {e}")
    
    async def _handle_alert(self, topic: str, data: dict):
        """处理告警消息"""
        try:
            # 广播告警信息
            await self.websocket_service.broadcast({
                "type": "alert",
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"处理告警消息: {data}")
            
        except Exception as e:
            logger.error(f"处理告警消息失败: {e}")
    
    async def _write_to_influxdb(self, sensor: Sensor, value: Any, timestamp: datetime, quality: str):
        """写入InfluxDB"""
        try:
            write_api = get_write_api()
            
            # 创建数据点
            point = Point("sensor_data") \
                .tag("sensor_id", str(sensor.id)) \
                .tag("device_id", sensor.device_id) \
                .tag("sensor_type", sensor.sensor_type.name if sensor.sensor_type else "unknown") \
                .tag("gateway_id", str(sensor.gateway_id)) \
                .tag("location", sensor.location or "unknown") \
                .field("value", float(value) if isinstance(value, (int, float)) else str(value)) \
                .field("quality", quality) \
                .time(timestamp)
            
            # 添加额外字段
            if sensor.sensor_type and sensor.sensor_type.unit:
                point = point.tag("unit", sensor.sensor_type.unit)
            
            # 写入数据
            write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                record=point
            )
            
            logger.debug(f"数据写入InfluxDB成功: {sensor.device_id} = {value}")
            
        except Exception as e:
            logger.error(f"写入InfluxDB失败: {e}")
    
    async def _cache_sensor_data(self, sensor: Sensor, value: Any, timestamp: datetime):
        """缓存传感器数据到Redis"""
        try:
            redis_client = await get_redis()
            
            # 缓存最新数据
            cache_key = f"sensor:{sensor.id}:latest"
            cache_data = {
                "value": value,
                "timestamp": timestamp.isoformat(),
                "sensor_id": sensor.id,
                "device_id": sensor.device_id
            }
            
            await redis_client.setex(
                cache_key,
                3600,  # 1小时过期
                json.dumps(cache_data)
            )
            
            # 添加到时间序列（保留最近100个数据点）
            series_key = f"sensor:{sensor.id}:series"
            await redis_client.lpush(series_key, json.dumps(cache_data))
            await redis_client.ltrim(series_key, 0, 99)  # 只保留最近100个
            await redis_client.expire(series_key, 86400)  # 24小时过期
            
        except Exception as e:
            logger.error(f"缓存传感器数据失败: {e}")
    
    async def _handle_alarms(self, alarms: List[dict]):
        """处理报警"""
        try:
            for alarm in alarms:
                # 广播报警信息
                await self.websocket_service.broadcast({
                    "type": "alarm",
                    "data": alarm,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                logger.warning(f"传感器报警: {alarm['message']}")
        
        except Exception as e:
            logger.error(f"处理报警失败: {e}")
    
    async def _broadcast_sensor_data(self, sensor: Sensor, value: Any, timestamp: datetime):
        """广播传感器数据"""
        try:
            await self.websocket_service.broadcast({
                "type": "sensor_data",
                "sensor_id": sensor.id,
                "device_id": sensor.device_id,
                "value": value,
                "timestamp": timestamp.isoformat(),
                "sensor_name": sensor.name,
                "unit": sensor.sensor_type.unit if sensor.sensor_type else None
            })
            
        except Exception as e:
            logger.error(f"广播传感器数据失败: {e}")
    
    async def _message_loop(self):
        """消息处理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(1)
                
                # 定期检查连接状态
                if not self.is_connected and self.is_running:
                    logger.warning("MQTT连接断开，尝试重连...")
                    await self._reconnect()
                
            except Exception as e:
                logger.error(f"消息循环错误: {e}")
                await asyncio.sleep(5)
    
    async def publish(self, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        """发布消息"""
        if not self.is_connected:
            logger.error("MQTT未连接，无法发布消息")
            return False
        
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"消息发布成功: {topic}")
                return True
            else:
                logger.error(f"消息发布失败: {topic}, 错误码: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"发布消息失败: {e}")
            return False
    
    def get_stats(self) -> dict:
        """获取服务统计信息"""
        return {
            **self.stats,
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "reconnect_attempts": self.reconnect_attempts
        }
    
    def add_message_handler(self, topic_pattern: str, handler: Callable):
        """添加消息处理器"""
        if topic_pattern not in self.message_handlers:
            self.message_handlers[topic_pattern] = []
        self.message_handlers[topic_pattern].append(handler)
    
    def remove_message_handler(self, topic_pattern: str, handler: Callable):
        """移除消息处理器"""
        if topic_pattern in self.message_handlers:
            try:
                self.message_handlers[topic_pattern].remove(handler)
            except ValueError:
                pass


# 全局MQTT服务实例
mqtt_service = MQTTService()