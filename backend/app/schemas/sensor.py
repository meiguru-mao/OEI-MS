from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SensorTypeBase(BaseModel):
    name: str = Field(..., description="传感器类型名称")
    description: Optional[str] = Field(None, description="描述")
    unit: Optional[str] = Field(None, description="单位")
    min_value: Optional[float] = Field(None, description="最小值")
    max_value: Optional[float] = Field(None, description="最大值")


class SensorTypeCreate(SensorTypeBase):
    pass


class SensorTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class SensorType(SensorTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SensorBase(BaseModel):
    sensor_id: str = Field(..., description="传感器唯一标识")
    name: str = Field(..., description="传感器名称")
    location: Optional[str] = Field(None, description="安装位置")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(True, description="是否激活")
    ip_address: Optional[str] = Field(None, description="IP地址")
    port: Optional[int] = Field(None, description="端口")
    protocol: Optional[str] = Field(None, description="通信协议")
    sampling_interval: int = Field(60, description="采样间隔(秒)")


class SensorCreate(SensorBase):
    sensor_type_id: int = Field(..., description="传感器类型ID")


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    sampling_interval: Optional[int] = None
    sensor_type_id: Optional[int] = None


class Sensor(SensorBase):
    id: int
    sensor_type_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_data_time: Optional[datetime] = None
    sensor_type: Optional[SensorType] = None
    
    class Config:
        from_attributes = True


class SensorDataBase(BaseModel):
    value: float = Field(..., description="数值")
    quality: str = Field("good", description="数据质量")
    status: Optional[str] = Field(None, description="传感器状态")
    timestamp: datetime = Field(..., description="数据时间戳")


class SensorDataCreate(SensorDataBase):
    sensor_id: int = Field(..., description="传感器ID")


class SensorData(SensorDataBase):
    id: int
    sensor_id: int
    created_at: datetime
    sensor: Optional[Sensor] = None
    
    class Config:
        from_attributes = True


class SensorDataPoint(BaseModel):
    """时序数据点"""
    timestamp: datetime
    value: float
    sensor_id: str
    quality: str = "good"


class SensorDataQuery(BaseModel):
    """传感器数据查询参数"""
    sensor_ids: Optional[List[str]] = Field(None, description="传感器ID列表")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    limit: int = Field(1000, description="限制条数")
    aggregation: Optional[str] = Field(None, description="聚合方式: mean, max, min, sum")
    interval: Optional[str] = Field(None, description="聚合间隔: 1m, 5m, 1h, 1d")


class GatewayBase(BaseModel):
    gateway_id: str = Field(..., description="网关唯一标识")
    name: str = Field(..., description="网关名称")
    location: Optional[str] = Field(None, description="安装位置")
    ip_address: Optional[str] = Field(None, description="IP地址")


class GatewayCreate(GatewayBase):
    pass


class GatewayUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    is_online: Optional[bool] = None


class Gateway(GatewayBase):
    id: int
    is_online: bool
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True