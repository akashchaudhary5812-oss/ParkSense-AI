from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.core.config import settings
from app.core.database import engine, Base
from app.api import violations, hotspots, forecast, patrol, gis, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="ParkSense AI",
    description="AI-Driven Parking Intelligence for Smart City Enforcement",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,       prefix="/api/v1/auth",       tags=["auth"])
app.include_router(violations.router, prefix="/api/v1/violations",  tags=["violations"])
app.include_router(hotspots.router,   prefix="/api/v1/hotspots",    tags=["hotspots"])
app.include_router(forecast.router,   prefix="/api/v1/forecast",    tags=["forecast"])
app.include_router(patrol.router,     prefix="/api/v1/patrol",      tags=["patrol"])
app.include_router(gis.router,        prefix="/api/v1/gis",         tags=["gis"])

# WebSocket: live alert feed
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(30)  # heartbeat
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "ParkSense AI"}
