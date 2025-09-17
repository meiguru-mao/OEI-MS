from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sensor(Base):
    """传感器模型"""
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True, comment="传感器ID")
    name = Column(String(100), nullable=False, index=True, comment="传感器名称")
    device_id = Column(String(100), unique=True, nullable=False, index=True, comment="设备唯一标识")
    description = Column(Text, comment="传感器描述")
    
    # 外键关系
    sensor_type_id = Column(Integer, ForeignKey("sensor_types.id"), nullable=False, comment="传感器类型ID")
    gateway_id = Column(Integer, ForeignKey("gateways.id"), nullable=False, comment="所属网关ID")
    
    # 位置信息
    location = Column(String(200), comment="安装位置")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    altitude = Column(Float, comment="海拔高度")
    
    # 配置参数
    config = Column(JSON, comment="传感器配置参数")
    calibration = Column(JSON, comment="校准参数")
    
    # 数据采集配置
    sampling_interval = Column(Integer, default=60, comment="采样间隔（秒）")
    data_retention_days = Column(Integer, default=30, comment="数据保留天数")
    
    # 报警配置
    alarm_enabled = Column(Boolean, default=True, comment="是否启用报警")
    alarm_rules = Column(JSON, comment="报警规则")
    
    # 状态信息
    status = Column(String(20), default="offline", comment="在线状态")
    last_data_time = Column(DateTime(timezone=True), comment="最后数据时间")
    last_value = Column(String(100), comment="最后读数")
    
    # 统计信息
    data_points_count = Column(Integer, default=0, comment="数据点总数")
    error_count = Column(Integer, default=0, comment="错误次数")
    last_error = Column(Text, comment="最后错误信息")
    last_error_time = Column(DateTime(timezone=True), comment="最后错误时间")
    
    # 系统字段
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    sensor_type = relationship("SensorType", back_populates="sensors")
    gateway = relationship("Gateway", back_populates="sensors")
    
    def __repr__(self):
        return f"<Sensor(id={self.id}, name='{self.name}', device_id='{self.device_id}', status='{self.status}')>"
    
    def to_dict(self, include_relations=False):
        """转换为字典格式"""
        data = {
            "id": self.id,
            "name": self.name,
            "device_id": self.device_id,
            "description": self.description,
            "sensor_type_id": self.sensor_type_id,
            "gateway_id": self.gateway_id,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "config": self.config,
            "calibration": self.calibration,
            "sampling_interval": self.sampling_interval,
            "data_retention_days": self.data_retention_days,
            "alarm_enabled": self.alarm_enabled,
            "alarm_rules": self.alarm_rules,
            "status": self.status,
            "last_data_time": self.last_data_time.isoformat() if self.last_data_time else None,
            "last_value": self.last_value,
            "data_points_count": self.data_points_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            if self.sensor_type:
                data["sensor_type"] = self.sensor_type.to_dict()
            if self.gateway:
                data["gateway"] = {
                    "id": self.gateway.id,
                    "name": self.gateway.name,
                    "device_id": self.gateway.device_id,
                    "status": self.gateway.status
                }
        
        return data
    
    def update_status(self, status: str, error_message: str = None):
        """更新传感器状态"""
        self.status = status
        self.updated_at = func.now()
        
        if error_message:
            self.error_count += 1
            self.last_error = error_message
            self.last_error_time = func.now()
    
    def update_data_stats(self, value: str = None):
        """更新数据统计"""
        self.data_points_count += 1
        self.last_data_time = func.now()
        if value is not None:
            self.last_value = str(value)
        self.updated_at = func.now()
    
    @property
    def is_online(self) -> bool:
        """检查传感器是否在线"""
        return self.status == "online"
    
    @property
    def has_recent_data(self) -> bool:
        """检查是否有最近的数据"""
        if not self.last_data_time:
            return False
        
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        last_data_dt = self.last_data_time.replace(tzinfo=datetime.timezone.utc) if self.last_data_time.tzinfo is None else self.last_data_time
        
        # 如果超过采样间隔的3倍时间没有数据，认为没有最近数据
        threshold_seconds = self.sampling_interval * 3
        return (now - last_data_dt).total_seconds() <= threshold_seconds
    
    def get_health_status(self) -> dict:
        """获取传感器健康状态"""
        import datetime
        
        health = {
            "status": self.status,
            "is_healthy": False,
            "has_recent_data": self.has_recent_data,
            "last_data_minutes_ago": None,
            "error_rate": 0,
            "issues": []
        }
        
        # 计算最后数据时间
        if self.last_data_time:
            now = datetime.datetime.now(datetime.timezone.utc)
            last_data_dt = self.last_data_time.replace(tzinfo=datetime.timezone.utc) if self.last_data_time.tzinfo is None else self.last_data_time
            minutes_ago = (now - last_data_dt).total_seconds() / 60
            health["last_data_minutes_ago"] = int(minutes_ago)
        
        # 计算错误率
        if self.data_points_count > 0:
            health["error_rate"] = (self.error_count / self.data_points_count) * 100
        
        # 判断健康状态
        health["is_healthy"] = (
            self.is_online and 
            self.has_recent_data and 
            health["error_rate"] < 10  # 错误率小于10%
        )
        
        # 收集问题
        if not self.is_online:
            health["issues"].append("传感器离线")
        if not self.has_recent_data:
            health["issues"].append("数据更新延迟")
        if health["error_rate"] >= 10:
            health["issues"].append(f"错误率过高 ({health['error_rate']:.1f}%)")
        if self.last_error:
            health["issues"].append(f"最近错误: {self.last_error}")
        
        return health
    
    def get_default_alarm_rules(self) -> dict:
        """获取默认报警规则"""
        if not self.sensor_type:
            return {}
        
        rules = {
            "enabled": True,
            "rules": []
        }
        
        # 根据传感器类型设置默认报警规则
        if self.sensor_type.name == "温度传感器":
            rules["rules"] = [
                {
                    "name": "高温报警",
                    "condition": ">",
                    "threshold": 35.0,
                    "severity": "warning",
                    "enabled": True
                },
                {
                    "name": "低温报警",
                    "condition": "<",
                    "threshold": 5.0,
                    "severity": "warning",
                    "enabled": True
                }
            ]
        elif self.sensor_type.name == "湿度传感器":
            rules["rules"] = [
                {
                    "name": "高湿报警",
                    "condition": ">",
                    "threshold": 80.0,
                    "severity": "warning",
                    "enabled": True
                },
                {
                    "name": "低湿报警",
                    "condition": "<",
                    "threshold": 20.0,
                    "severity": "info",
                    "enabled": True
                }
            ]
        
        return rules
    
    def check_alarm_conditions(self, value: float) -> list:
        """检查报警条件"""
        if not self.alarm_enabled or not self.alarm_rules:
            return []
        
        triggered_alarms = []
        rules = self.alarm_rules.get("rules", [])
        
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            
            condition = rule.get("condition")
            threshold = rule.get("threshold")
            
            if condition and threshold is not None:
                triggered = False
                
                if condition == ">" and value > threshold:
                    triggered = True
                elif condition == "<" and value < threshold:
                    triggered = True
                elif condition == ">=" and value >= threshold:
                    triggered = True
                elif condition == "<=" and value <= threshold:
                    triggered = True
                elif condition == "==" and value == threshold:
                    triggered = True
                elif condition == "!=" and value != threshold:
                    triggered = True
                
                if triggered:
                    triggered_alarms.append({
                        "rule_name": rule.get("name", "未命名规则"),
                        "condition": f"{value} {condition} {threshold}",
                        "severity": rule.get("severity", "info"),
                        "message": rule.get("message", f"传感器 {self.name} 触发报警条件"),
                        "sensor_id": self.id,
                        "sensor_name": self.name,
                        "value": value,
                        "threshold": threshold
                    })
        
        return triggered_alarms


class SensorData(Base):
    """传感器数据表（用于PostgreSQL存储元数据）"""
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    value = Column(Float, nullable=False, comment="数值")
    quality = Column(String(20), default="good", comment="数据质量")
    status = Column(String(50), comment="传感器状态")
    timestamp = Column(DateTime(timezone=True), nullable=False, comment="数据时间戳")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    sensor = relationship("Sensor")