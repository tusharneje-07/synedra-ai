"""
FastAPI Backend for AI Multi-Agent Council
==========================================

Main entry point for the backend API server.
Provides REST APIs, WebSocket support for real-time agent communication.

Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database.base import init_db
from routes import agents, brand_config, chat, websocket, council

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup/shutdown events."""
    # Startup
    logger.info("🚀 Starting AI Council Backend...")
    await init_db()
    logger.info("✓ Database initialized")
    yield
    # Shutdown
    logger.info("👋 Shutting down AI Council Backend...")


# Create FastAPI app
app = FastAPI(
    title="AI Multi-Agent Council API",
    description="Backend API for autonomous AI marketing council with real-time debate streaming",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative
        "http://localhost:8080",  # Frontend from screenshot
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(brand_config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])
app.include_router(council.router, prefix="/api/council", tags=["Council"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "running",
        "service": "AI Multi-Agent Council API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
