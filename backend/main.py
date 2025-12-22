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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
        else:
            logger.debug("WebSocket already removed from connections")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Client disconnected during broadcast: {type(e).__name__}")
                disconnected.append(connection)

        # Remove disconnected clients
        if disconnected:
            for conn in disconnected:
                self.active_connections.remove(conn)
            logger.info(f"Cleaned up {len(disconnected)} dead connections. Active: {len(self.active_connections)}")


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
# In development, allow all origins. In production, use settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.cors_origins_list,
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

        # Track last sent activity index
        last_sent_index = len(trading_agent.activity_log) if trading_agent else 0

        # Keep connection alive and send updates
        while True:
            # Send only new activities
            if trading_agent:
                current_count = len(trading_agent.activity_log)
                if current_count > last_sent_index:
                    # Send all new activities
                    new_activities = trading_agent.activity_log[last_sent_index:]
                    for activity in new_activities:
                        await websocket.send_json({
                            "type": "activity",
                            "data": activity
                        })
                    last_sent_index = current_count

            await asyncio.sleep(1)  # Check every second

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {type(e).__name__}")
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
            "activity_count": 0,
            "has_strategy": False,
            "last_discovery": None,
            "last_analysis": None,
            "last_monitoring": None
        }

    return {
        "is_running": trading_agent.is_running,
        "activity_count": len(trading_agent.activity_log),
        "has_strategy": trading_agent.current_strategy is not None,
        "strategy_style": trading_agent.current_strategy.style if trading_agent.current_strategy else None,
        "last_discovery": trading_agent.last_discovery.isoformat() if trading_agent.last_discovery else None,
        "last_analysis": trading_agent.last_analysis.isoformat() if trading_agent.last_analysis else None,
        "last_monitoring": trading_agent.last_monitoring.isoformat() if trading_agent.last_monitoring else None
    }


@app.get("/api/trading/activities")
async def get_activities(limit: int = 50):
    """Get recent activity logs."""
    global trading_agent

    if not trading_agent:
        return {"activities": []}

    return {
        "activities": trading_agent.activity_log[-limit:]
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
