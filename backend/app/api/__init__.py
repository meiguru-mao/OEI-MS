"""API模块

包含所有API路由和WebSocket端点。
"""

from fastapi import APIRouter
from .websocket import router as websocket_router

# 创建主路由
api_router = APIRouter()

# 注册WebSocket路由
api_router.include_router(websocket_router, tags=["websocket"])

__all__ = ["api_router"]