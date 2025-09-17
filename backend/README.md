# OEI-MS Backend

基于 FastAPI 的工业设备监控系统后端服务

## 🏗️ 技术栈

- **框架**: FastAPI 0.104+
- **Python**: 3.11+
- **数据库**: PostgreSQL + SQLAlchemy 2.0
- **缓存**: Redis
- **消息队列**: MQTT (paho-mqtt)
- **认证**: JWT (python-jose)
- **验证**: Pydantic v2
- **异步**: asyncio + asyncpg
- **测试**: pytest + httpx

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── deps.py         # 依赖注入
│   │   ├── auth.py         # 认证路由
│   │   ├── sensors.py      # 传感器API
│   │   ├── data.py         # 数据API
│   │   ├── alarms.py       # 报警API
│   │   ├── gateways.py     # 网关API
│   │   └── websocket.py    # WebSocket处理
│   ├── core/               # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py       # 应用配置
│   │   ├── security.py     # 安全相关
│   │   └── database.py     # 数据库配置
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py         # 基础模型
│   │   ├── user.py         # 用户模型
│   │   ├── sensor.py       # 传感器模型
│   │   ├── gateway.py      # 网关模型
│   │   ├── data.py         # 数据模型
│   │   └── alarm.py        # 报警模型
│   ├── schemas/            # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模式
│   │   ├── sensor.py       # 传感器模式
│   │   ├── gateway.py      # 网关模式
│   │   ├── data.py         # 数据模式
│   │   └── alarm.py        # 报警模式
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证服务
│   │   ├── sensor.py       # 传感器服务
│   │   ├── data.py         # 数据服务
│   │   ├── alarm.py        # 报警服务
│   │   ├── mqtt.py         # MQTT服务
│   │   └── websocket.py    # WebSocket服务
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── logger.py       # 日志工具
│       ├── redis.py        # Redis工具
│       └── helpers.py      # 辅助函数
├── tests/                  # 测试文件
│   ├── __init__.py
│   ├── conftest.py         # pytest配置
│   ├── test_auth.py        # 认证测试
│   ├── test_sensors.py     # 传感器测试
│   └── test_data.py        # 数据测试
├── alembic/                # 数据库迁移
│   ├── versions/           # 迁移版本
│   ├── env.py             # Alembic环境
│   └── script.py.mako     # 迁移模板
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── alembic.ini            # Alembic配置
├── Dockerfile             # Docker配置
├── .dockerignore          # Docker忽略文件
└── README.md              # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- MQTT Broker (Mosquitto)

### 本地开发

1. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **安装依赖**

```bash
pip install -r requirements-dev.txt
```

3. **环境配置**

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/oei_ms
REDIS_URL=redis://localhost:6379/0

# MQTT配置
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# JWT配置
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 日志配置
LOG_LEVEL=INFO
```

4. **数据库迁移**

```bash
# 初始化迁移
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

5. **启动服务**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 开发

```bash
# 构建镜像
docker build -t oei-ms-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env oei-ms-backend
```

## 📚 API 文档

### 自动生成文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 主要端点

#### 认证相关

```http
POST /api/auth/login          # 用户登录
POST /api/auth/refresh        # 刷新Token
POST /api/auth/logout         # 用户登出
GET  /api/auth/me             # 获取当前用户信息
```

#### 传感器管理

```http
GET    /api/sensors           # 获取传感器列表
POST   /api/sensors           # 创建传感器
GET    /api/sensors/{id}      # 获取传感器详情
PUT    /api/sensors/{id}      # 更新传感器
DELETE /api/sensors/{id}      # 删除传感器
```

#### 数据查询

```http
GET /api/data                 # 获取传感器数据
GET /api/data/latest          # 获取最新数据
GET /api/data/history         # 获取历史数据
GET /api/data/statistics      # 获取统计数据
```

#### 报警管理

```http
GET    /api/alarms            # 获取报警列表
POST   /api/alarms            # 创建报警规则
GET    /api/alarms/{id}       # 获取报警详情
PUT    /api/alarms/{id}       # 更新报警规则
DELETE /api/alarms/{id}       # 删除报警规则
POST   /api/alarms/{id}/ack   # 确认报警
```

#### 网关管理

```http
GET    /api/gateways          # 获取网关列表
POST   /api/gateways          # 注册网关
GET    /api/gateways/{id}     # 获取网关详情
PUT    /api/gateways/{id}     # 更新网关
DELETE /api/gateways/{id}     # 删除网关
```

#### WebSocket

```http
WS /ws                        # WebSocket连接
WS /ws/sensors/{id}           # 传感器数据流
WS /ws/alarms                 # 报警通知流
```

#### 系统监控

```http
GET /health                   # 健康检查
GET /metrics                  # 系统指标
GET /version                  # 版本信息
```

## 🔧 配置说明

### 环境变量

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | string | - | PostgreSQL连接字符串 |
| `REDIS_URL` | string | - | Redis连接字符串 |
| `MQTT_HOST` | string | localhost | MQTT服务器地址 |
| `MQTT_PORT` | int | 1883 | MQTT服务器端口 |
| `MQTT_USERNAME` | string | - | MQTT用户名 |
| `MQTT_PASSWORD` | string | - | MQTT密码 |
| `SECRET_KEY` | string | - | JWT密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 30 | Token过期时间 |
| `HOST` | string | 0.0.0.0 | 服务器地址 |
| `PORT` | int | 8000 | 服务器端口 |
| `DEBUG` | bool | false | 调试模式 |
| `LOG_LEVEL` | string | INFO | 日志级别 |

### 数据库配置

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### Redis 配置

```python
# app/utils/redis.py
import redis.asyncio as redis

redis_client = redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
)
```

## 🏛️ 数据模型

### 用户模型

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 传感器模型

```python
class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # temperature, humidity, pressure, etc.
    unit = Column(String(20), nullable=False)
    gateway_id = Column(Integer, ForeignKey("gateways.id"))
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    min_value = Column(Float)
    max_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    gateway = relationship("Gateway", back_populates="sensors")
    data_points = relationship("SensorData", back_populates="sensor")
```

### 数据模型

```python
class SensorData(Base):
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    quality = Column(String(20), default="good")  # good, bad, uncertain
    
    # 关系
    sensor = relationship("Sensor", back_populates="data_points")
    
    # 索引
    __table_args__ = (
        Index('ix_sensor_data_sensor_timestamp', 'sensor_id', 'timestamp'),
        Index('ix_sensor_data_timestamp', 'timestamp'),
    )
```

## 🔐 认证和授权

### JWT 认证

```python
# app/core/security.py
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### 权限装饰器

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
```

## 📡 MQTT 集成

### MQTT 客户端

```python
# app/services/mqtt.py
import paho.mqtt.client as mqtt
from app.core.config import settings

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # 订阅传感器数据主题
            client.subscribe("sensors/+/+/data")
            client.subscribe("gateways/+/status")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    async def on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            payload = json.loads(msg.payload.decode())
            
            if topic_parts[0] == "sensors":
                await self.handle_sensor_data(topic_parts, payload)
            elif topic_parts[0] == "gateways":
                await self.handle_gateway_status(topic_parts, payload)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    async def handle_sensor_data(self, topic_parts, payload):
        gateway_id = topic_parts[1]
        sensor_id = topic_parts[2]
        
        # 保存数据到数据库
        await save_sensor_data(sensor_id, payload)
        
        # 发送WebSocket通知
        await websocket_manager.broadcast_sensor_data(sensor_id, payload)
```

## 🌐 WebSocket 支持

### WebSocket 管理器

```python
# app/services/websocket.py
from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sensor_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # 清理订阅
        for sensor_id, connections in self.sensor_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
    
    async def broadcast_sensor_data(self, sensor_id: str, data: dict):
        if sensor_id in self.sensor_subscriptions:
            for connection in self.sensor_subscriptions[sensor_id]:
                try:
                    await connection.send_json({
                        "type": "sensor_data",
                        "sensor_id": sensor_id,
                        "data": data
                    })
                except:
                    await self.disconnect(connection)

manager = ConnectionManager()
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_sensors.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行测试并显示详细输出
pytest -v
```

### 测试示例

```python
# tests/test_sensors.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_sensor():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/sensors",
            json={
                "name": "Test Sensor",
                "type": "temperature",
                "unit": "°C",
                "gateway_id": 1
            },
            headers={"Authorization": "Bearer test-token"}
        )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Sensor"

@pytest.mark.asyncio
async def test_get_sensors():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/sensors",
            headers={"Authorization": "Bearer test-token"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 📊 性能优化

### 数据库优化

1. **连接池配置**
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=0,        # 最大溢出连接
    pool_pre_ping=True,    # 连接预检
    pool_recycle=3600,     # 连接回收时间
)
```

2. **查询优化**
```python
# 使用索引
class SensorData(Base):
    __table_args__ = (
        Index('ix_sensor_data_sensor_timestamp', 'sensor_id', 'timestamp'),
    )

# 批量插入
async def bulk_insert_sensor_data(db: AsyncSession, data_list: List[dict]):
    stmt = insert(SensorData).values(data_list)
    await db.execute(stmt)
    await db.commit()
```

### 缓存策略

```python
# app/services/cache.py
import json
from app.utils.redis import redis_client

class CacheService:
    @staticmethod
    async def get_sensor_data_cache(sensor_id: int, hours: int = 1):
        key = f"sensor_data:{sensor_id}:{hours}h"
        cached_data = await redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    @staticmethod
    async def set_sensor_data_cache(sensor_id: int, hours: int, data: list):
        key = f"sensor_data:{sensor_id}:{hours}h"
        await redis_client.setex(
            key, 
            3600,  # 1小时过期
            json.dumps(data, default=str)
        )
```

## 🚀 部署

### 生产环境配置

```python
# app/core/config.py
class Settings(BaseSettings):
    # 生产环境配置
    debug: bool = False
    log_level: str = "INFO"
    
    # 数据库配置
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 0
    
    # Redis配置
    redis_url: str
    redis_max_connections: int = 20
    
    # 安全配置
    secret_key: str
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
```

### Docker 部署

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 开发指南

### 代码规范

- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 使用 **flake8** 进行代码检查
- 使用 **mypy** 进行类型检查

```bash
# 格式化代码
black app/
isort app/

# 检查代码
flake8 app/
mypy app/
```

### 提交规范

使用 **Conventional Commits** 规范：

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```

### 开发流程

1. 创建功能分支
2. 编写代码和测试
3. 运行测试和代码检查
4. 提交代码
5. 创建Pull Request
6. 代码审查
7. 合并到主分支

## 🔍 故障排除

### 常见问题

**Q: 数据库连接失败**
```bash
# 检查数据库连接
psql -h localhost -U postgres -d oei_ms

# 检查环境变量
echo $DATABASE_URL
```

**Q: MQTT连接失败**
```bash
# 测试MQTT连接
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test
```

**Q: Redis连接失败**
```bash
# 测试Redis连接
redis-cli ping
```

### 日志分析

```python
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看性能日志
grep "slow query" logs/app.log
```

## 📈 监控和指标

### 健康检查

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "mqtt": await check_mqtt_health(),
    }
```

### 性能指标

```python
# 使用 Prometheus 指标
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_connections = Gauge('websocket_connections_active', 'Active WebSocket connections')
```

---

更多详细信息请参考主项目 [README](../README.md) 或访问 [API文档](http://localhost:8000/docs)。