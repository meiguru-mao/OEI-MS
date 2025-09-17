import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db, health_check
from app.services import mqtt_service, websocket_service
from app.api import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动OEI监控系统...")
    
    try:
        # 初始化数据库
        logger.info("初始化数据库连接...")
        await init_db()
        
        # 启动WebSocket服务
        logger.info("启动WebSocket服务...")
        await websocket_service.start()
        
        # 启动MQTT服务
        logger.info("启动MQTT服务...")
        await mqtt_service.start()
        
        logger.info("OEI监控系统启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise
    
    finally:
        # 关闭服务
        logger.info("关闭OEI监控系统...")
        
        try:
            # 停止MQTT服务
            await mqtt_service.stop()
            
            # 停止WebSocket服务
            await websocket_service.stop()
            
            # 关闭数据库连接
            await close_db()
            
            logger.info("OEI监控系统已关闭")
            
        except Exception as e:
            logger.error(f"关闭服务时出错: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="OEI监控系统",
    description="工业设备监控系统API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "OEI监控系统API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    try:
        # 检查数据库连接
        db_status = await health_check()
        
        # 检查服务状态
        mqtt_stats = mqtt_service.get_stats()
        websocket_stats = websocket_service.get_stats()
        
        return {
            "status": "healthy",
            "database": db_status,
            "mqtt": {
                "connected": mqtt_stats.get("is_connected", False),
                "running": mqtt_stats.get("is_running", False),
                "messages_processed": mqtt_stats.get("messages_processed", 0)
            },
            "websocket": {
                "active_connections": websocket_stats.get("active_connections", 0),
                "messages_sent": websocket_stats.get("messages_sent", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    try:
        mqtt_stats = mqtt_service.get_stats()
        websocket_stats = websocket_service.get_stats()
        
        return {
            "mqtt": mqtt_stats,
            "websocket": websocket_stats
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )