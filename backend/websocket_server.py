"""
FastAPI WebSocket Server for Real-time Analysis Notifications
Runs on port 5002 alongside Flask backend (port 5001)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import asyncio
import logging
import os
import json
import re
from datetime import datetime
import aiofiles

# Import async versions of our modules
from helius_api_async import TokenAnalyzerAsync, generate_token_acronym, generate_axiom_export
from analyzed_tokens_db_async import save_analyzed_token

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

# ============================================================================
# TOKEN ANALYSIS ENDPOINT (Migrated from Flask)
# ============================================================================

# Load Helius API key from config
HELIUS_API_KEY = os.getenv('HELIUS_API_KEY', '')
if not HELIUS_API_KEY:
    # Try to load from backend/config.json
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            HELIUS_API_KEY = config.get('helius_api_key', '')

# Store for analysis jobs (in-memory, simple tracking)
analysis_jobs: Dict[str, Dict] = {}

class AnalyzeTokenRequest(BaseModel):
    address: str
    api_settings: Optional[Dict] = None
    min_usd: Optional[float] = None
    time_window_hours: Optional[int] = 999999

def is_valid_solana_address(address: str) -> bool:
    """Validate Solana address format (base58, 32-44 chars)"""
    if not address or not isinstance(address, str):
        return False

    # Length check
    if len(address) < 32 or len(address) > 44:
        return False

    # Base58 pattern check (excludes 0, O, I, l)
    if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address):
        return False

    return True

async def run_token_analysis_async(
    job_id: str,
    token_address: str,
    min_usd: float,
    time_window_hours: int,
    transaction_limit: int,
    max_credits: int,
    max_wallets: int
):
    """Run token analysis in background (async version)"""
    try:
        logger.info(f"[Job {job_id}] Starting analysis for token: {token_address}")
        analysis_jobs[job_id]['status'] = 'running'

        # Create analyzer
        analyzer = TokenAnalyzerAsync(HELIUS_API_KEY)

        # Run analysis
        result = await analyzer.analyze_token(
            mint_address=token_address,
            min_usd=min_usd,
            time_window_hours=time_window_hours,
            max_transactions=transaction_limit,
            max_credits=max_credits,
            max_wallets_to_store=max_wallets
        )

        # Check if analysis succeeded
        if 'error' in result:
            analysis_jobs[job_id]['status'] = 'failed'
            analysis_jobs[job_id]['error'] = result['error']
            logger.error(f"[Job {job_id}] Analysis failed: {result['error']}")
            return

        # Extract token info
        token_info = result.get('token_info', {})
        token_name = token_info.get('onChainMetadata', {}).get('metadata', {}).get('name', 'Unknown')
        token_symbol = token_info.get('onChainMetadata', {}).get('metadata', {}).get('symbol', 'UNK')

        # Generate acronym
        acronym = generate_token_acronym(token_name, token_symbol)

        # Generate Axiom export
        early_bidders = result.get('early_bidders', [])
        axiom_json = generate_axiom_export(early_bidders, token_name, token_symbol, max_wallets)

        # Save to database
        token_id = await save_analyzed_token(
            token_address=token_address,
            token_name=token_name,
            token_symbol=token_symbol,
            acronym=acronym,
            early_bidders=early_bidders,
            axiom_json=axiom_json,
            first_buy_timestamp=result.get('first_transaction_time'),
            credits_used=result.get('api_credits_used', 0),
            max_wallets=max_wallets
        )

        # Save full analysis results to file (async)
        analysis_results_dir = os.path.join(os.path.dirname(__file__), 'analysis_results')
        os.makedirs(analysis_results_dir, exist_ok=True)

        # Use token_id in filename for unique identification
        from analyzed_tokens_db_async import sanitize_filename
        sanitized_name = sanitize_filename(token_name)
        analysis_file = os.path.join(analysis_results_dir, f"{token_id}_{sanitized_name}.json")

        async with aiofiles.open(analysis_file, 'w') as f:
            await f.write(json.dumps(result, indent=2, default=str))

        # Save Axiom export to file (async)
        axiom_exports_dir = os.path.join(os.path.dirname(__file__), 'axiom_exports')
        os.makedirs(axiom_exports_dir, exist_ok=True)

        sanitized_acronym = sanitize_filename(acronym, max_length=10)
        axiom_file = os.path.join(axiom_exports_dir, f"{token_id}_{sanitized_acronym}.json")

        async with aiofiles.open(axiom_file, 'w') as f:
            await f.write(json.dumps(axiom_json, indent=2))

        # Update job status
        analysis_jobs[job_id]['status'] = 'complete'
        analysis_jobs[job_id]['result'] = {
            'token_id': token_id,
            'token_name': token_name,
            'token_symbol': token_symbol,
            'acronym': acronym,
            'wallets_found': len(early_bidders),
            'credits_used': result.get('api_credits_used', 0),
            'analysis_file': analysis_file,
            'axiom_file': axiom_file
        }

        logger.info(f"[Job {job_id}] Analysis complete: {token_name} ({len(early_bidders)} wallets)")

        # Broadcast completion notification via WebSocket
        await manager.broadcast({
            "event": "analysis_complete",
            "data": {
                "job_id": job_id,
                "token_name": token_name,
                "token_symbol": token_symbol,
                "acronym": acronym,
                "wallets_found": len(early_bidders),
                "token_id": token_id
            }
        })

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"[Job {job_id}] Analysis failed: {str(e)}")
        logger.error(f"[Job {job_id}] Full traceback:\n{error_trace}")
        analysis_jobs[job_id]['status'] = 'failed'
        analysis_jobs[job_id]['error'] = str(e)
        analysis_jobs[job_id]['error_trace'] = error_trace

@app.post("/analyze/token")
async def analyze_token(request: AnalyzeTokenRequest):
    """
    Analyze a token to find early bidders (async FastAPI version)

    Expected JSON payload:
    {
        "address": "TokenMintAddress...",
        "api_settings": {  # optional - API request settings from frontend
            "transactionLimit": 500,
            "minUsdFilter": 50,
            "walletCount": 10,
            "apiRateDelay": 100,
            "maxCreditsPerAnalysis": 1000,
            "maxRetries": 3
        }
    }
    """
    if not HELIUS_API_KEY:
        raise HTTPException(status_code=503, detail="Helius API not configured")

    token_address = request.address.strip()

    if not is_valid_solana_address(token_address):
        raise HTTPException(status_code=400, detail="Invalid Solana address format")

    # Get API settings from request (with defaults)
    api_settings = request.api_settings or {}
    transaction_limit = int(api_settings.get('transactionLimit', 500))
    min_usd = float(api_settings.get('minUsdFilter', 50))
    # Support both old and new parameter names for backward compatibility
    max_wallets = int(api_settings.get('walletCount', api_settings.get('maxWalletsToStore', 10)))
    max_credits = int(api_settings.get('maxCreditsPerAnalysis', 1000))

    # For backwards compatibility, also accept old parameter names
    if request.min_usd is not None:
        min_usd = float(request.min_usd)
    time_window_hours = int(request.time_window_hours)

    # Create analysis job
    import uuid
    job_id = str(uuid.uuid4())[:8]
    analysis_jobs[job_id] = {
        'job_id': job_id,
        'token_address': token_address,
        'status': 'queued',
        'min_usd': min_usd,
        'time_window_hours': time_window_hours,
        'transaction_limit': transaction_limit,
        'max_wallets': max_wallets,
        'max_credits': max_credits,
        'api_settings': api_settings,
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None
    }

    # Start background analysis using asyncio.create_task()
    asyncio.create_task(run_token_analysis_async(
        job_id, token_address, min_usd, time_window_hours,
        transaction_limit, max_credits, max_wallets
    ))

    # OPSEC: Only show first/last 4 chars of token address
    token_display = f"{token_address[:4]}...{token_address[-4:]}" if len(token_address) >= 12 else "****"
    logger.info(f"[OK] Queued token analysis: {token_display} (Job ID: {job_id})")
    logger.info(f"[OK] Settings: ${min_usd} min, {transaction_limit} transactions, {max_wallets} wallets max")

    return {
        'status': 'queued',
        'job_id': job_id,
        'token_address': token_address,
        'api_settings': {
            'min_usd': min_usd,
            'transaction_limit': transaction_limit,
            'max_wallets': max_wallets,
            'time_window_hours': time_window_hours
        },
        'results_url': f'/analysis/{job_id}'
    }

@app.get("/analysis/{job_id}")
async def get_analysis_status(job_id: str):
    """Get status of an analysis job"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return analysis_jobs[job_id]

@app.get("/api/settings")
async def get_api_settings():
    """Get API settings (for backward compatibility with AutoHotkey script)"""
    # Load settings from config file if available
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    default_settings = {
        "transactionLimit": 500,
        "minUsdFilter": 50,
        "walletCount": 10,
        "apiRateDelay": 100,
        "maxCreditsPerAnalysis": 1000,
        "maxRetries": 3
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                if 'api_settings' in config:
                    default_settings.update(config['api_settings'])
        except Exception as e:
            logger.warning(f"Could not load settings from config: {e}")

    return default_settings

if __name__ == "__main__":
    logger.info("[FastAPI] Starting WebSocket server on port 5002")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5002,
        log_level="info"
    )
