from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List
import json
from loguru import logger

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routes import trading
from app.services.trading_agent import TradingAgent

# Create database tables
Base.metadata.create_all(bind=engine)

# Global trading agent instance
trading_agent = None
agent_task = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Application starting...")
    yield
    logger.info("👋 Application shutting down...")
    if trading_agent:
        trading_agent.stop()


# Create FastAPI app
app = FastAPI(
    title="Trading AI Auto-Apprenant",
    description="AI Trading System with Self-Learning Capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trading.router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)

    try:
        # Send initial state
        if trading_agent:
            await websocket.send_json({
                "type": "status",
                "data": {
                    "is_running": trading_agent.is_running,
                    "activity_log": trading_agent.activity_log[-50:]  # Last 50 activities
                }
            })

        # Keep connection alive and send updates
        while True:
            # Send activity updates every 2 seconds
            if trading_agent and trading_agent.activity_log:
                await websocket.send_json({
                    "type": "activity",
                    "data": trading_agent.activity_log[-1]  # Latest activity
                })

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/trading/start")
async def start_trading():
    """Start the trading agent."""
    global trading_agent, agent_task

    if trading_agent and trading_agent.is_running:
        return {"status": "already_running"}

    # Create new agent
    db = SessionLocal()
    trading_agent = TradingAgent(db)

    # Start agent in background
    agent_task = asyncio.create_task(trading_agent.run())

    await manager.broadcast({
        "type": "status",
        "data": {"is_running": True}
    })

    return {"status": "started"}


@app.post("/api/trading/stop")
async def stop_trading():
    """Stop the trading agent."""
    global trading_agent

    if not trading_agent:
        return {"status": "not_running"}

    trading_agent.stop()

    await manager.broadcast({
        "type": "status",
        "data": {"is_running": False}
    })

    return {"status": "stopped"}


@app.get("/api/trading/status")
async def get_trading_status():
    """Get current trading status."""
    if not trading_agent:
        return {
            "is_running": False,
            "last_trade_time": None,
            "activity_count": 0
        }

    return {
        "is_running": trading_agent.is_running,
        "last_trade_time": trading_agent.last_trade_time.isoformat() if trading_agent.last_trade_time else None,
        "activity_count": len(trading_agent.activity_log)
    }


@app.get("/api/activity")
async def get_activity(limit: int = 100):
    """Get recent activity log."""
    if not trading_agent:
        return []

    return trading_agent.activity_log[-limit:]


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Trading AI Backend...")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
