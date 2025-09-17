from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import init_db
from app.core.mqtt_client import mqtt_manager
from app.core.websocket_manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await init_db()
    await mqtt_manager.connect()
    yield
    # 关闭时执行
    await mqtt_manager.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="多源多点传感器数据集成系统",
    lifespan=lifespan
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# WebSocket管理器
app.state.websocket_manager = websocket_manager


@app.get("/")
async def root():
    return {"message": "多源多点传感器数据集成系统 API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )