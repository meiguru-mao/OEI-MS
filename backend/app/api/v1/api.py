from fastapi import APIRouter

from app.api.v1.endpoints import sensors, websocket

api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])