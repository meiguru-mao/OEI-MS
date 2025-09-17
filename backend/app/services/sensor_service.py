from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from app.models.sensor import Sensor, SensorType, SensorData, Gateway
from app.schemas.sensor import (
    SensorCreate, SensorUpdate,
    SensorTypeCreate, SensorTypeUpdate,
    SensorDataCreate,
    GatewayCreate, GatewayUpdate
)


class SensorService:
    """传感器服务类"""
    
    @staticmethod
    def get_sensor_types(db: Session) -> List[SensorType]:
        """获取所有传感器类型"""
        return db.query(SensorType).all()
    
    @staticmethod
    def create_sensor_type(db: Session, sensor_type: SensorTypeCreate) -> SensorType:
        """创建传感器类型"""
        db_sensor_type = SensorType(**sensor_type.dict())
        db.add(db_sensor_type)
        db.commit()
        db.refresh(db_sensor_type)
        return db_sensor_type
    
    @staticmethod
    def update_sensor_type(db: Session, type_id: int, sensor_type: SensorTypeUpdate) -> SensorType:
        """更新传感器类型"""
        db_sensor_type = db.query(SensorType).filter(SensorType.id == type_id).first()
        if not db_sensor_type:
            raise ValueError("传感器类型不存在")
        
        update_data = sensor_type.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sensor_type, field, value)
        
        db.commit()
        db.refresh(db_sensor_type)
        return db_sensor_type
    
    @staticmethod
    def delete_sensor_type(db: Session, type_id: int):
        """删除传感器类型"""
        db_sensor_type = db.query(SensorType).filter(SensorType.id == type_id).first()
        if not db_sensor_type:
            raise ValueError("传感器类型不存在")
        
        db.delete(db_sensor_type)
        db.commit()
    
    @staticmethod
    def get_sensors(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> List[Sensor]:
        """获取传感器列表"""
        query = db.query(Sensor)
        
        if is_active is not None:
            query = query.filter(Sensor.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sensor(db: Session, sensor_id: int) -> Optional[Sensor]:
        """获取单个传感器"""
        return db.query(Sensor).filter(Sensor.id == sensor_id).first()
    
    @staticmethod
    def get_sensor_by_sensor_id(db: Session, sensor_id: str) -> Optional[Sensor]:
        """根据传感器标识获取传感器"""
        return db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    
    @staticmethod
    def create_sensor(db: Session, sensor: SensorCreate) -> Sensor:
        """创建传感器"""
        # 检查传感器ID是否已存在
        existing_sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor.sensor_id).first()
        if existing_sensor:
            raise ValueError("传感器ID已存在")
        
        db_sensor = Sensor(**sensor.dict())
        db.add(db_sensor)
        db.commit()
        db.refresh(db_sensor)
        return db_sensor
    
    @staticmethod
    def update_sensor(db: Session, sensor_id: int, sensor: SensorUpdate) -> Sensor:
        """更新传感器"""
        db_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if not db_sensor:
            raise ValueError("传感器不存在")
        
        update_data = sensor.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sensor, field, value)
        
        db.commit()
        db.refresh(db_sensor)
        return db_sensor
    
    @staticmethod
    def delete_sensor(db: Session, sensor_id: int):
        """删除传感器"""
        db_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if not db_sensor:
            raise ValueError("传感器不存在")
        
        db.delete(db_sensor)
        db.commit()
    
    @staticmethod
    def create_sensor_data(db: Session, data: SensorDataCreate) -> SensorData:
        """创建传感器数据"""
        db_data = SensorData(**data.dict())
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        
        # 更新传感器最后数据时间
        db_sensor = db.query(Sensor).filter(Sensor.id == data.sensor_id).first()
        if db_sensor:
            db_sensor.last_data_time = data.timestamp
            db.commit()
        
        return db_data
    
    @staticmethod
    def get_gateways(db: Session) -> List[Gateway]:
        """获取网关列表"""
        return db.query(Gateway).all()
    
    @staticmethod
    def create_gateway(db: Session, gateway: GatewayCreate) -> Gateway:
        """创建网关"""
        # 检查网关ID是否已存在
        existing_gateway = db.query(Gateway).filter(Gateway.gateway_id == gateway.gateway_id).first()
        if existing_gateway:
            raise ValueError("网关ID已存在")
        
        db_gateway = Gateway(**gateway.dict())
        db.add(db_gateway)
        db.commit()
        db.refresh(db_gateway)
        return db_gateway
    
    @staticmethod
    def update_gateway(db: Session, gateway_id: int, gateway: GatewayUpdate) -> Gateway:
        """更新网关"""
        db_gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
        if not db_gateway:
            raise ValueError("网关不存在")
        
        update_data = gateway.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_gateway, field, value)
        
        db.commit()
        db.refresh(db_gateway)
        return db_gateway
    
    @staticmethod
    def update_gateway_heartbeat(db: Session, gateway_id: int):
        """更新网关心跳"""
        db_gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
        if not db_gateway:
            raise ValueError("网关不存在")
        
        db_gateway.last_heartbeat = datetime.now()
        db_gateway.is_online = True
        db.commit()