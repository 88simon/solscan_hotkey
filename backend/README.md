# Gun Del Sol Backend

This folder hosts every backend service that powers the Gun Del Sol action wheel:

- **Flask REST API (`api_service.py`, port 5001)** for watchlists, token analysis, CSV exports, and API settings.
- **FastAPI WebSocket server (`websocket_server.py`, port 5002)** for real-time `analysis_start` and `analysis_complete` notifications.
- **Helius integration (`helius_api.py`)** plus persistence helpers (`analyzed_tokens_db.py`, `secure_logging.py`, `debug_config.py`).

## Requirements

- Python 3.9 or later
- pip and a virtual environment (recommended)
- Valid Helius API key if you intend to run token analysis
- Redis is optional but recommended later if you distribute Socket.IO or WebSocket broadcasts

## Installation

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The root `start_backend.bat` script will create the environment automatically the first time it runs, but installing manually keeps things predictable.

## Configuration

1. Copy `config.example.json` to `config.json`.
2. Set at minimum:
   ```json
   {
     "helius_api_key": "YOUR_KEY",
     "default_threshold": 100,
     "analysis_min_usd": 50
   }
   ```
3. Override any value via environment variables when needed:
   - `HELIUS_API_KEY`
   - `API_RATE_DELAY`
   - `DEFAULT_THRESHOLD`

The Flask service also persists user-tunable API settings to `api_settings.json`; you can edit the file or call `POST /api/settings`.

## Running the Services

### From the repository root

```powershell
start_backend.bat
```

The script launches:
- Flask REST API on http://localhost:5001
- FastAPI WebSocket server on http://localhost:5002

### Manual control

```powershell
python api_service.py          # Flask REST API
python websocket_server.py     # FastAPI WebSocket server
```

Both scripts auto-reload when `debug_config.py` enables debug mode.

## REST API Overview

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/register` | Add a wallet to the monitoring list |
| `GET` | `/addresses` | List known wallets |
| `GET` | `/address/<address>` | Fetch a single wallet record |
| `PUT` | `/address/<address>/note` | Update a note/tag |
| `DELETE` | `/address/<address>` | Remove a wallet |
| `POST` | `/import` | Bulk import watchlist entries |
| `POST` | `/clear` | Delete every watchlist entry |
| `GET` | `/analysis` | List analysis jobs |
| `POST` | `/analysis` | Queue a new analysis job |
| `GET` | `/analysis/<job_id>` | Poll job status/results |
| `GET` | `/analysis/<job_id>/results` | Render results as HTML |
| `GET` | `/analysis/<job_id>/csv` | Download CSV |
| `GET` | `/api/tokens/<token_id>` | Inspect a stored token |
| `GET` | `/api/tokens/<token_id>/history` | Show historical runs |
| `DELETE` | `/api/tokens/<token_id>` | Soft-delete a token |
| `POST` | `/api/tokens/<token_id>/restore` | Restore from trash |
| `DELETE` | `/api/tokens/<token_id>/permanent` | Hard-delete |
| `GET/POST` | `/api/settings` | Read or update backend analysis defaults |
| `GET` | `/health` | Service heartbeat for launch scripts |

All responses are JSON except for the HTML and CSV exports.

## WebSocket Notifications

- Clients connect to `ws://localhost:5002/ws`.
- The Flask service posts to `/notify/analysis_start` and `/notify/analysis_complete` whenever a job transitions states.
- Sample payload:
  ```json
  {
    "event": "analysis_complete",
    "data": {
      "job_id": "b2b1de34",
      "token_name": "Example",
      "token_symbol": "EXMPL",
      "acronym": "EXMPL",
      "wallets_found": 12,
      "token_id": 42
    }
  }
  ```
- The `/health` route on the FastAPI server reports active WebSocket connections for monitoring.

## Data Storage

- `monitored_addresses.json`: primary watchlist (JSON, git-ignored)
- `analysis_results/` and `axiom_exports/`: per-job outputs and exports
- `analyzed_tokens.db` / `solscan_monitor.db`: SQLite databases holding aggregated results
- `api_settings.json`: persisted API defaults

Back up these files before reinstalling or switching machines. All sensitive paths stay on disk only; `SECURITY.md` covers safe handling.

## Logging & Debugging

- `secure_logging.py` centralizes safe log helpers (`log_info`, `log_success`, etc.).
- `debug_config.py` toggles verbose logging globally; ensure production mode keeps it disabled.
- When diagnosing issues, run the services manually so you can read stack traces directly in the console.

## Troubleshooting

- **Missing dependencies:** re-run `python -m pip install -r requirements.txt`.
- **Port already in use:** edit the host/port passed to `socketio.run` (Flask) or `uvicorn.run` (FastAPI).
- **Helius quota exceeded:** throttle via `api_settings.json` (`apiRateDelay`, `maxCreditsPerAnalysis`) or set a new API key.
- **WebSocket broadcasts never arrive:** confirm `websocket_server.py` is running and that `api_service.py` reports successful POSTs to `/notify/...`.

The backend is intentionally modular—extend it with new endpoints or queue processors as long as you keep user data local and follow the security guidance documented in `docs/`.
