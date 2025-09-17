from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.responses import HTMLResponse
import logging

from app.services import websocket_service
from app.core.auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None, description="用户ID"),
    room: Optional[str] = Query("default", description="房间名称")
):
    """WebSocket连接端点"""
    await websocket_service.handle_connection(websocket, user_id, room)


@router.websocket("/ws/sensor/{sensor_id}")
async def sensor_websocket_endpoint(
    websocket: WebSocket,
    sensor_id: int,
    user_id: Optional[str] = Query(None, description="用户ID")
):
    """传感器专用WebSocket连接端点"""
    room = f"sensor_{sensor_id}"
    await websocket_service.handle_connection(websocket, user_id, room)


@router.websocket("/ws/gateway/{gateway_id}")
async def gateway_websocket_endpoint(
    websocket: WebSocket,
    gateway_id: int,
    user_id: Optional[str] = Query(None, description="用户ID")
):
    """网关专用WebSocket连接端点"""
    room = f"gateway_{gateway_id}"
    await websocket_service.handle_connection(websocket, user_id, room)


@router.get("/ws/stats")
async def get_websocket_stats():
    """获取WebSocket服务统计信息"""
    return websocket_service.get_stats()


@router.get("/ws/test")
async def websocket_test_page():
    """WebSocket测试页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .message-box { 
                border: 1px solid #ccc; 
                height: 300px; 
                overflow-y: scroll; 
                padding: 10px; 
                margin: 10px 0;
                background-color: #f9f9f9;
            }
            .input-group { margin: 10px 0; }
            .input-group label { display: inline-block; width: 100px; }
            .input-group input, .input-group select { width: 200px; padding: 5px; }
            button { padding: 10px 20px; margin: 5px; }
            .connected { color: green; }
            .disconnected { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>WebSocket Test Client</h1>
            
            <div class="input-group">
                <label>Status:</label>
                <span id="status" class="disconnected">Disconnected</span>
            </div>
            
            <div class="input-group">
                <label>User ID:</label>
                <input type="text" id="userId" placeholder="Optional user ID">
            </div>
            
            <div class="input-group">
                <label>Room:</label>
                <input type="text" id="room" value="default" placeholder="Room name">
            </div>
            
            <div class="input-group">
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
                <button onclick="clearMessages()">Clear Messages</button>
            </div>
            
            <div class="message-box" id="messages"></div>
            
            <div class="input-group">
                <label>Message Type:</label>
                <select id="messageType">
                    <option value="ping">Ping</option>
                    <option value="join_room">Join Room</option>
                    <option value="leave_room">Leave Room</option>
                    <option value="get_stats">Get Stats</option>
                    <option value="custom">Custom</option>
                </select>
            </div>
            
            <div class="input-group">
                <label>Message Data:</label>
                <input type="text" id="messageData" placeholder="JSON data (optional)">
            </div>
            
            <div class="input-group">
                <button onclick="sendMessage()">Send Message</button>
            </div>
        </div>

        <script>
            let ws = null;
            const messages = document.getElementById('messages');
            const status = document.getElementById('status');

            function addMessage(message, type = 'info') {
                const div = document.createElement('div');
                div.style.color = type === 'error' ? 'red' : type === 'sent' ? 'blue' : 'black';
                div.innerHTML = `<strong>[${new Date().toLocaleTimeString()}]</strong> ${message}`;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }

            function connect() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    addMessage('Already connected', 'error');
                    return;
                }

                const userId = document.getElementById('userId').value;
                const room = document.getElementById('room').value;
                
                let url = `ws://localhost:8000/api/v1/ws?room=${encodeURIComponent(room)}`;
                if (userId) {
                    url += `&user_id=${encodeURIComponent(userId)}`;
                }

                ws = new WebSocket(url);

                ws.onopen = function(event) {
                    status.textContent = 'Connected';
                    status.className = 'connected';
                    addMessage('Connected to WebSocket server');
                };

                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        addMessage(`Received: ${JSON.stringify(data, null, 2)}`);
                    } catch (e) {
                        addMessage(`Received: ${event.data}`);
                    }
                };

                ws.onclose = function(event) {
                    status.textContent = 'Disconnected';
                    status.className = 'disconnected';
                    addMessage(`Connection closed: ${event.code} - ${event.reason}`);
                };

                ws.onerror = function(error) {
                    addMessage(`WebSocket error: ${error}`, 'error');
                };
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }

            function sendMessage() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    addMessage('Not connected', 'error');
                    return;
                }

                const messageType = document.getElementById('messageType').value;
                const messageData = document.getElementById('messageData').value;

                let message = { type: messageType };

                if (messageData) {
                    try {
                        const data = JSON.parse(messageData);
                        message = { ...message, ...data };
                    } catch (e) {
                        message.data = messageData;
                    }
                }

                if (messageType === 'join_room') {
                    const room = prompt('Enter room name:');
                    if (room) {
                        message.room = room;
                    } else {
                        return;
                    }
                }

                ws.send(JSON.stringify(message));
                addMessage(`Sent: ${JSON.stringify(message, null, 2)}`, 'sent');
            }

            function clearMessages() {
                messages.innerHTML = '';
            }

            // Auto-connect on page load
            window.onload = function() {
                // Uncomment to auto-connect
                // connect();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)