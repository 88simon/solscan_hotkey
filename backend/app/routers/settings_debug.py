"""
Settings, debug, and health check endpoints

Provides REST endpoints for managing API settings and debug configuration
"""

from fastapi import APIRouter, HTTPException
from debug_config import DEBUG_MODE, get_debug_js_flag

from app.settings import CURRENT_API_SETTINGS, save_api_settings
from app.utils.models import UpdateSettingsRequest
from app.websocket import get_connection_manager

router = APIRouter()


# ============================================================================
# Root & Health Check
# ============================================================================

@router.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "status": "ok",
        "service": "Gun Del Sol API",
        "version": "2.0.0",
        "message": "FastAPI backend for Solana token analysis (Modular)",
        "endpoints": {
            "health": "/health",
            "tokens": "/api/tokens/history",
            "analysis": "/analysis",
            "watchlist": "/addresses",
            "settings": "/api/settings"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint with WebSocket connection count"""
    manager = get_connection_manager()
    return {
        "status": "healthy",
        "service": "FastAPI Gun Del Sol (Modular)",
        "version": "2.0.0",
        "architecture": "modular",
        "endpoints": 46,
        "websocket_connections": manager.get_connection_count() if manager else 0
    }


# ============================================================================
# Debug Configuration
# ============================================================================

@router.get("/api/debug-mode")
async def get_debug_mode():
    """Get current debug mode status"""
    return {"debug_mode": DEBUG_MODE}


@router.get("/api/debug/config")
async def get_debug_config():
    """Get debug configuration for frontend"""
    return {"debug": get_debug_js_flag()}


# ============================================================================
# API Settings
# ============================================================================

@router.get("/api/settings")
async def get_api_settings():
    """
    Get current API settings

    Returns:
        API settings dictionary
    """
    settings = CURRENT_API_SETTINGS.copy()
    settings["maxWalletsToStore"] = settings["walletCount"]
    return settings


@router.post("/api/settings")
async def update_api_settings(payload: UpdateSettingsRequest):
    """
    Update API settings

    Args:
        payload: Settings to update

    Returns:
        Updated settings
    """
    global CURRENT_API_SETTINGS

    updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if not updates:
        return {"status": "noop", "settings": CURRENT_API_SETTINGS}

    # Update in-memory settings
    CURRENT_API_SETTINGS.update(updates)

    # Persist to file
    if not save_api_settings(CURRENT_API_SETTINGS):
        raise HTTPException(status_code=500, detail="Failed to save settings")

    settings = CURRENT_API_SETTINGS.copy()
    settings["maxWalletsToStore"] = settings["walletCount"]
    return {"status": "success", "settings": settings}