from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import redis.asyncio as redis
import logging

from .config import settings

logger = logging.getLogger(__name__)

# PostgreSQL 数据库配置
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG  # 在调试模式下显示SQL语句
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# InfluxDB 客户端管理
class InfluxDBManager:
    def __init__(self):
        self._client = None
        self._write_api = None
        self._query_api = None
        self._delete_api = None
        
    def get_client(self) -> InfluxDBClient:
        """获取InfluxDB客户端实例"""
        if self._client is None:
            try:
                self._client = InfluxDBClient(
                    url=settings.INFLUXDB_URL,
                    token=settings.INFLUXDB_TOKEN,
                    org=settings.INFLUXDB_ORG,
                    timeout=30000,  # 30秒超时
                    enable_gzip=True
                )
                logger.info("InfluxDB客户端连接成功")
            except Exception as e:
                logger.error(f"InfluxDB客户端连接失败: {e}")
                raise
        return self._client
    
    def get_write_api(self):
        """获取写入API"""
        if self._write_api is None:
            client = self.get_client()
            self._write_api = client.write_api(write_options=SYNCHRONOUS)
        return self._write_api
    
    def get_query_api(self):
        """获取查询API"""
        if self._query_api is None:
            client = self.get_client()
            self._query_api = client.query_api()
        return self._query_api
    
    def get_delete_api(self):
        """获取删除API"""
        if self._delete_api is None:
            client = self.get_client()
            self._delete_api = client.delete_api()
        return self._delete_api
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            client = self.get_client()
            health = client.health()
            return health.status == "pass"
        except Exception as e:
            logger.error(f"InfluxDB健康检查失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self._client:
            try:
                self._client.close()
                logger.info("InfluxDB客户端连接已关闭")
            except Exception as e:
                logger.error(f"关闭InfluxDB客户端连接失败: {e}")
            finally:
                self._client = None
                self._write_api = None
                self._query_api = None
                self._delete_api = None

# Redis 客户端管理
class RedisManager:
    def __init__(self):
        self._client = None
        
    async def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # 测试连接
                await self._client.ping()
                logger.info("Redis客户端连接成功")
            except Exception as e:
                logger.error(f"Redis客户端连接失败: {e}")
                raise
        return self._client
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False
    
    async def close(self):
        """关闭连接"""
        if self._client:
            try:
                await self._client.close()
                logger.info("Redis客户端连接已关闭")
            except Exception as e:
                logger.error(f"关闭Redis客户端连接失败: {e}")
            finally:
                self._client = None

# 全局实例
influxdb_manager = InfluxDBManager()
redis_manager = RedisManager()

# 数据库依赖注入
def get_db():
    """获取PostgreSQL数据库会话"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_redis():
    """获取Redis客户端"""
    return await redis_manager.get_client()

def get_influx_client():
    """获取InfluxDB客户端"""
    return influxdb_manager.get_client()

def get_write_api():
    """获取InfluxDB写入API"""
    return influxdb_manager.get_write_api()

def get_query_api():
    """获取InfluxDB查询API"""
    return influxdb_manager.get_query_api()

# 数据库初始化和健康检查
async def init_db():
    """初始化数据库"""
    logger.info("开始初始化数据库连接...")
    
    # 测试PostgreSQL连接
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("PostgreSQL连接测试成功")
    except Exception as e:
        logger.error(f"PostgreSQL连接测试失败: {e}")
        raise
    
    # 创建所有表
    try:
        # 导入所有模型以确保它们被注册
        from app.models import sensor, sensor_type, gateway
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise
    
    # 测试InfluxDB连接
    try:
        if influxdb_manager.health_check():
            logger.info("InfluxDB连接测试成功")
        else:
            raise Exception("InfluxDB健康检查失败")
    except Exception as e:
        logger.error(f"InfluxDB连接测试失败: {e}")
        raise
    
    # 测试Redis连接
    try:
        if await redis_manager.health_check():
            logger.info("Redis连接测试成功")
        else:
            raise Exception("Redis健康检查失败")
    except Exception as e:
        logger.error(f"Redis连接测试失败: {e}")
        raise
    
    logger.info("所有数据库连接初始化完成")

async def close_databases():
    """关闭所有数据库连接"""
    logger.info("开始关闭数据库连接...")
    
    try:
        influxdb_manager.close()
    except Exception as e:
        logger.error(f"关闭InfluxDB连接失败: {e}")
    
    try:
        await redis_manager.close()
    except Exception as e:
        logger.error(f"关闭Redis连接失败: {e}")
    
    try:
        engine.dispose()
        logger.info("PostgreSQL连接池已关闭")
    except Exception as e:
        logger.error(f"关闭PostgreSQL连接池失败: {e}")
    
    logger.info("所有数据库连接已关闭")

async def check_databases_health() -> dict:
    """检查所有数据库的健康状态"""
    health_status = {
        "postgresql": False,
        "influxdb": False,
        "redis": False
    }
    
    # 检查PostgreSQL
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["postgresql"] = True
    except Exception as e:
        logger.error(f"PostgreSQL健康检查失败: {e}")
    
    # 检查InfluxDB
    try:
        health_status["influxdb"] = influxdb_manager.health_check()
    except Exception as e:
        logger.error(f"InfluxDB健康检查失败: {e}")
    
    # 检查Redis
    try:
        health_status["redis"] = await redis_manager.health_check()
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
    
    return health_status