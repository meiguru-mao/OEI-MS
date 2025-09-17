from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Gateway(Base):
    """网关设备模型"""
    __tablename__ = "gateways"
    
    id = Column(Integer, primary_key=True, index=True, comment="网关ID")
    name = Column(String(100), nullable=False, index=True, comment="网关名称")
    device_id = Column(String(100), unique=True, nullable=False, index=True, comment="设备唯一标识")
    description = Column(Text, comment="网关描述")
    
    # 网络配置
    ip_address = Column(String(45), comment="IP地址")
    mac_address = Column(String(17), comment="MAC地址")
    port = Column(Integer, comment="通信端口")
    protocol = Column(String(20), default="MQTT", comment="通信协议")
    
    # 位置信息
    location = Column(String(200), comment="安装位置")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    altitude = Column(Float, comment="海拔高度")
    
    # 设备信息
    model = Column(String(100), comment="设备型号")
    firmware_version = Column(String(50), comment="固件版本")
    hardware_version = Column(String(50), comment="硬件版本")
    manufacturer = Column(String(100), comment="制造商")
    
    # 配置参数
    config = Column(JSON, comment="网关配置参数")
    mqtt_config = Column(JSON, comment="MQTT配置")
    
    # 状态信息
    status = Column(String(20), default="offline", comment="在线状态")
    last_seen = Column(DateTime(timezone=True), comment="最后在线时间")
    uptime = Column(Integer, default=0, comment="运行时间（秒）")
    
    # 统计信息
    total_sensors = Column(Integer, default=0, comment="传感器总数")
    active_sensors = Column(Integer, default=0, comment="活跃传感器数")
    data_points_today = Column(Integer, default=0, comment="今日数据点数")
    
    # 系统字段
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    sensors = relationship("Sensor", back_populates="gateway", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Gateway(id={self.id}, name='{self.name}', device_id='{self.device_id}', status='{self.status}')>"
    
    def to_dict(self, include_sensors=False):
        """转换为字典格式"""
        data = {
            "id": self.id,
            "name": self.name,
            "device_id": self.device_id,
            "description": self.description,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "port": self.port,
            "protocol": self.protocol,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "model": self.model,
            "firmware_version": self.firmware_version,
            "hardware_version": self.hardware_version,
            "manufacturer": self.manufacturer,
            "config": self.config,
            "mqtt_config": self.mqtt_config,
            "status": self.status,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "uptime": self.uptime,
            "total_sensors": self.total_sensors,
            "active_sensors": self.active_sensors,
            "data_points_today": self.data_points_today,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensors and self.sensors:
            data["sensors"] = [sensor.to_dict() for sensor in self.sensors]
        
        return data
    
    def update_status(self, status: str):
        """更新网关状态"""
        self.status = status
        if status == "online":
            self.last_seen = func.now()
        self.updated_at = func.now()
    
    def update_statistics(self):
        """更新统计信息"""
        if self.sensors:
            self.total_sensors = len(self.sensors)
            self.active_sensors = len([s for s in self.sensors if s.is_active and s.status == "online"])
        else:
            self.total_sensors = 0
            self.active_sensors = 0
        self.updated_at = func.now()
    
    @property
    def is_online(self) -> bool:
        """检查网关是否在线"""
        return self.status == "online"
    
    @property
    def uptime_formatted(self) -> str:
        """格式化运行时间"""
        if not self.uptime:
            return "0秒"
        
        days = self.uptime // 86400
        hours = (self.uptime % 86400) // 3600
        minutes = (self.uptime % 3600) // 60
        seconds = self.uptime % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}秒")
        
        return "".join(parts)
    
    def get_default_mqtt_config(self):
        """获取默认MQTT配置"""
        return {
            "broker_host": "localhost",
            "broker_port": 1883,
            "username": "",
            "password": "",
            "client_id": f"gateway_{self.device_id}",
            "keepalive": 60,
            "qos": 1,
            "retain": False,
            "topics": {
                "data": f"sensors/{self.device_id}/data",
                "status": f"sensors/{self.device_id}/status",
                "command": f"sensors/{self.device_id}/command",
                "response": f"sensors/{self.device_id}/response"
            }
        }
    
    def get_health_status(self) -> dict:
        """获取网关健康状态"""
        import datetime
        
        health = {
            "status": self.status,
            "is_healthy": False,
            "last_seen_minutes_ago": None,
            "sensor_health": {
                "total": self.total_sensors,
                "active": self.active_sensors,
                "inactive": self.total_sensors - self.active_sensors,
                "health_percentage": 0
            }
        }
        
        # 计算最后在线时间
        if self.last_seen:
            now = datetime.datetime.now(datetime.timezone.utc)
            last_seen_dt = self.last_seen.replace(tzinfo=datetime.timezone.utc) if self.last_seen.tzinfo is None else self.last_seen
            minutes_ago = (now - last_seen_dt).total_seconds() / 60
            health["last_seen_minutes_ago"] = int(minutes_ago)
            
            # 5分钟内在线认为健康
            health["is_healthy"] = self.status == "online" and minutes_ago <= 5
        
        # 计算传感器健康百分比
        if self.total_sensors > 0:
            health["sensor_health"]["health_percentage"] = int((self.active_sensors / self.total_sensors) * 100)
        
        return health