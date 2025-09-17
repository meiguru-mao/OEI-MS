from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SensorType(Base):
    """传感器类型模型"""
    __tablename__ = "sensor_types"
    
    id = Column(Integer, primary_key=True, index=True, comment="传感器类型ID")
    name = Column(String(100), unique=True, nullable=False, index=True, comment="传感器类型名称")
    description = Column(Text, comment="传感器类型描述")
    unit = Column(String(20), comment="测量单位")
    data_type = Column(String(20), nullable=False, default="float", comment="数据类型")
    min_value = Column(String(50), comment="最小值")
    max_value = Column(String(50), comment="最大值")
    precision = Column(Integer, default=2, comment="数据精度")
    
    # 传感器配置参数（JSON格式存储）
    config_schema = Column(JSON, comment="配置参数模式")
    default_config = Column(JSON, comment="默认配置参数")
    
    # 数据采集配置
    default_interval = Column(Integer, default=60, comment="默认采集间隔（秒）")
    retention_days = Column(Integer, default=30, comment="数据保留天数")
    
    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    sensors = relationship("Sensor", back_populates="sensor_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SensorType(id={self.id}, name='{self.name}', unit='{self.unit}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "data_type": self.data_type,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "precision": self.precision,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
            "default_interval": self.default_interval,
            "retention_days": self.retention_days,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_common_types(cls):
        """获取常见传感器类型配置"""
        return [
            {
                "name": "温度传感器",
                "description": "测量环境温度",
                "unit": "°C",
                "data_type": "float",
                "min_value": "-50",
                "max_value": "100",
                "precision": 1,
                "default_interval": 60,
                "config_schema": {
                    "calibration_offset": {"type": "float", "default": 0.0, "description": "校准偏移量"},
                    "alarm_high": {"type": "float", "default": 35.0, "description": "高温报警阈值"},
                    "alarm_low": {"type": "float", "default": 5.0, "description": "低温报警阈值"}
                }
            },
            {
                "name": "湿度传感器",
                "description": "测量环境湿度",
                "unit": "%RH",
                "data_type": "float",
                "min_value": "0",
                "max_value": "100",
                "precision": 1,
                "default_interval": 60,
                "config_schema": {
                    "calibration_offset": {"type": "float", "default": 0.0, "description": "校准偏移量"},
                    "alarm_high": {"type": "float", "default": 80.0, "description": "高湿报警阈值"},
                    "alarm_low": {"type": "float", "default": 20.0, "description": "低湿报警阈值"}
                }
            },
            {
                "name": "压力传感器",
                "description": "测量压力值",
                "unit": "Pa",
                "data_type": "float",
                "min_value": "0",
                "max_value": "1000000",
                "precision": 0,
                "default_interval": 30,
                "config_schema": {
                    "calibration_factor": {"type": "float", "default": 1.0, "description": "校准系数"},
                    "alarm_high": {"type": "float", "default": 101325.0, "description": "高压报警阈值"}
                }
            },
            {
                "name": "光照传感器",
                "description": "测量光照强度",
                "unit": "lux",
                "data_type": "float",
                "min_value": "0",
                "max_value": "100000",
                "precision": 0,
                "default_interval": 300,
                "config_schema": {
                    "sensitivity": {"type": "float", "default": 1.0, "description": "灵敏度系数"},
                    "night_threshold": {"type": "float", "default": 10.0, "description": "夜间阈值"}
                }
            },
            {
                "name": "电流传感器",
                "description": "测量电流值",
                "unit": "A",
                "data_type": "float",
                "min_value": "0",
                "max_value": "100",
                "precision": 3,
                "default_interval": 10,
                "config_schema": {
                    "ct_ratio": {"type": "float", "default": 1.0, "description": "电流互感器变比"},
                    "alarm_high": {"type": "float", "default": 10.0, "description": "过流报警阈值"}
                }
            },
            {
                "name": "电压传感器",
                "description": "测量电压值",
                "unit": "V",
                "data_type": "float",
                "min_value": "0",
                "max_value": "500",
                "precision": 2,
                "default_interval": 10,
                "config_schema": {
                    "voltage_divider": {"type": "float", "default": 1.0, "description": "分压比"},
                    "alarm_high": {"type": "float", "default": 250.0, "description": "过压报警阈值"},
                    "alarm_low": {"type": "float", "default": 200.0, "description": "欠压报警阈值"}
                }
            }
        ]