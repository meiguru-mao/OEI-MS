from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.sensor import (
    Sensor, SensorCreate, SensorUpdate,
    SensorType, SensorTypeCreate, SensorTypeUpdate,
    SensorData, SensorDataCreate, SensorDataQuery,
    Gateway, GatewayCreate, GatewayUpdate
)
from app.services.sensor_service import SensorService
from app.services.influx_service import InfluxService

router = APIRouter()


# 传感器类型相关接口
@router.get("/types", response_model=List[SensorType])
async def get_sensor_types(db: Session = Depends(get_db)):
    """获取所有传感器类型"""
    return SensorService.get_sensor_types(db)


@router.post("/types", response_model=SensorType)
async def create_sensor_type(
    sensor_type: SensorTypeCreate,
    db: Session = Depends(get_db)
):
    """创建传感器类型"""
    return SensorService.create_sensor_type(db, sensor_type)


@router.put("/types/{type_id}", response_model=SensorType)
async def update_sensor_type(
    type_id: int,
    sensor_type: SensorTypeUpdate,
    db: Session = Depends(get_db)
):
    """更新传感器类型"""
    return SensorService.update_sensor_type(db, type_id, sensor_type)


@router.delete("/types/{type_id}")
async def delete_sensor_type(type_id: int, db: Session = Depends(get_db)):
    """删除传感器类型"""
    SensorService.delete_sensor_type(db, type_id)
    return {"message": "传感器类型删除成功"}


# 传感器相关接口
@router.get("/", response_model=List[Sensor])
async def get_sensors(
    skip: int = Query(0, description="跳过条数"),
    limit: int = Query(100, description="限制条数"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: Session = Depends(get_db)
):
    """获取传感器列表"""
    return SensorService.get_sensors(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/{sensor_id}", response_model=Sensor)
async def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """获取单个传感器"""
    sensor = SensorService.get_sensor(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="传感器不存在")
    return sensor


@router.post("/", response_model=Sensor)
async def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """创建传感器"""
    return SensorService.create_sensor(db, sensor)


@router.put("/{sensor_id}", response_model=Sensor)
async def update_sensor(
    sensor_id: int,
    sensor: SensorUpdate,
    db: Session = Depends(get_db)
):
    """更新传感器"""
    return SensorService.update_sensor(db, sensor_id, sensor)


@router.delete("/{sensor_id}")
async def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """删除传感器"""
    SensorService.delete_sensor(db, sensor_id)
    return {"message": "传感器删除成功"}


# 传感器数据相关接口
@router.post("/data", response_model=SensorData)
async def create_sensor_data(
    data: SensorDataCreate,
    db: Session = Depends(get_db)
):
    """创建传感器数据"""
    # 同时写入PostgreSQL和InfluxDB
    pg_data = SensorService.create_sensor_data(db, data)
    await InfluxService.write_sensor_data(data)
    return pg_data


@router.get("/data/query")
async def query_sensor_data(query: SensorDataQuery = Depends()):
    """查询传感器时序数据"""
    return await InfluxService.query_sensor_data(query)


@router.get("/data/latest")
async def get_latest_data(
    sensor_ids: Optional[List[str]] = Query(None, description="传感器ID列表"),
    db: Session = Depends(get_db)
):
    """获取最新数据"""
    return await InfluxService.get_latest_data(sensor_ids)


@router.get("/data/statistics")
async def get_data_statistics(
    sensor_id: str = Query(..., description="传感器ID"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间")
):
    """获取数据统计信息"""
    return await InfluxService.get_data_statistics(sensor_id, start_time, end_time)


# 网关相关接口
@router.get("/gateways", response_model=List[Gateway])
async def get_gateways(db: Session = Depends(get_db)):
    """获取网关列表"""
    return SensorService.get_gateways(db)


@router.post("/gateways", response_model=Gateway)
async def create_gateway(gateway: GatewayCreate, db: Session = Depends(get_db)):
    """创建网关"""
    return SensorService.create_gateway(db, gateway)


@router.put("/gateways/{gateway_id}", response_model=Gateway)
async def update_gateway(
    gateway_id: int,
    gateway: GatewayUpdate,
    db: Session = Depends(get_db)
):
    """更新网关"""
    return SensorService.update_gateway(db, gateway_id, gateway)


@router.post("/gateways/{gateway_id}/heartbeat")
async def gateway_heartbeat(gateway_id: int, db: Session = Depends(get_db)):
    """网关心跳"""
    SensorService.update_gateway_heartbeat(db, gateway_id)
    return {"message": "心跳更新成功"}