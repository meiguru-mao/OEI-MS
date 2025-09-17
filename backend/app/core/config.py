from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "多源多点传感器数据集成系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "sensor_data"
    POSTGRES_PORT: int = 5432
    
    # InfluxDB配置
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "your-token"
    INFLUXDB_ORG: str = "your-org"
    INFLUXDB_BUCKET: str = "sensor_data"
    
    # MQTT配置
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_KEEPALIVE: int = 60
    MQTT_TOPIC_PREFIX: str = "sensors"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # WebSocket配置
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()