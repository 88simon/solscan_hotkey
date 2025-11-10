"""
FastAPI WebSocket Server for Real-time Analysis Notifications
Runs on port 5002 alongside Flask backend (port 5001)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analysis Notifications WebSocket Server")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WebSocket] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"[WebSocket] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                logger.info(f"[WebSocket] Sent message to client: {message.get('event')}")
            except Exception as e:
                logger.error(f"[WebSocket] Error sending to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Pydantic models for notification payloads
class AnalysisCompleteNotification(BaseModel):
    job_id: str
    token_name: str
    token_symbol: str
    acronym: str
    wallets_found: int
    token_id: int

class AnalysisStartNotification(BaseModel):
    job_id: str
    token_name: str
    token_symbol: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(websocket)
    try:
        # Keep connection alive and handle any incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for heartbeat/testing
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"[WebSocket] Error: {e}")
        manager.disconnect(websocket)

@app.post("/notify/analysis_complete")
async def notify_analysis_complete(notification: AnalysisCompleteNotification):
    """HTTP endpoint for Flask to trigger analysis complete notifications"""
    logger.info(f"[Notify] Analysis complete: {notification.token_name} ({notification.wallets_found} wallets)")

    message = {
        "event": "analysis_complete",
        "data": notification.dict()
    }

    await manager.broadcast(message)

    return {"status": "broadcasted", "connections": len(manager.active_connections)}

@app.post("/notify/analysis_start")
async def notify_analysis_start(notification: AnalysisStartNotification):
    """HTTP endpoint for Flask to trigger analysis start notifications"""
    logger.info(f"[Notify] Analysis started: {notification.token_name}")

    message = {
        "event": "analysis_start",
        "data": notification.dict()
    }

    await manager.broadcast(message)

    return {"status": "broadcasted", "connections": len(manager.active_connections)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections)
    }

if __name__ == "__main__":
    logger.info("[FastAPI] Starting WebSocket server on port 5002")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5002,
        log_level="info"
    )
