# Gun Del Sol

Gun Del Sol pairs an AutoHotkey action wheel with a local Solana intelligence backend. One hand stays on the mouse while the backend handles watchlists, Helius-powered analysis, CSV exports, and WebSocket notifications for the Next.js dashboard.

## Components

| Path | Purpose |
| --- | --- |
| `action_wheel.ahk` | Main AutoHotkey v2 script (radial menu, clipboard capture, Solscan helpers) |
| `action_wheel_settings.ini` | Auto-generated user settings for the wheel |
| `start.bat` | Launches the action wheel, Flask API (5001), FastAPI WebSocket server (5002), and Next.js dashboard (3000) |
| `start_backend.bat` | Starts only the backend services (Flask + WebSocket) |
| `start_frontend.bat` | Starts the dashboard located in `../gun-del-sol-web` |
| `backend/` | Flask REST API (`api_service.py`), Helius integration (`helius_api.py`), FastAPI WebSocket server (`websocket_server.py`), SQLite storage, and configs |
| `docs/` | Security guides and audits |
| `tools/` | Utilities such as `test_mouse_buttons.ahk` |
| `userscripts/` | Browser helpers (for example `defined-fi-autosearch.user.js`) |
| `Lib/` | AutoHotkey libraries bundled with the script |

## Requirements

- Windows 10 or later
- AutoHotkey v2.x
- Mouse with side buttons (XButton1/XButton2) recommended
- Python 3.9+ for the backend services
- Node.js 18+ if you run the external Next.js dashboard
- Helius API key (free tier works) for on-box token analysis

## Quick Start

### Action Wheel Only
1. Install AutoHotkey v2 from https://www.autohotkey.com/.
2. Double-click `action_wheel.ahk` (or run `start.bat` and close the backend windows you do not need).
3. Look for the green H tray icon, then press the default wheel hotkey (backtick `` ` ``) to open the radial menu.
4. Configure hotkeys or wheel slices any time via `Tray icon -> Settings`. Changes persist to `action_wheel_settings.ini`.

### Full Stack (Action Wheel + Backend + Dashboard)
1. Install Python 3.9+ and run `python -m pip install -r backend/requirements.txt`.
2. Copy `backend/config.example.json` to `backend/config.json`, set `helius_api_key`, and tune default thresholds if needed.
3. Start everything with `start.bat`, or run `start_backend.bat` and `start_frontend.bat` separately. The frontend expects the companion repo at `../gun-del-sol-web`.
4. Open http://localhost:3000 for the dashboard, http://localhost:5001 for the REST API health check, and keep http://localhost:5002 available for WebSocket clients.

## Wheel Menu

- Default hotkey: backtick `` ` `` (change via the Settings dialog).
- Mouse usage: hold the hotkey, glide toward an action, and release or click to run it.
- Keyboard usage: press number keys 1-6 while the wheel is open.
- Cancel: press Esc or select the Cancel slice.

Default slices (all configurable):
1. **Solscan** – open the hovered address in Solscan.
2. **Exclude** – add the hovered address to Solscan filters.
3. **Monitor** – register the address with the local backend.
4. **Defined.fi** – trigger the Tampermonkey helper for token pivots.
5. **Analyze** – send the token to the backend for early-bidder analysis.
6. **Cancel** – dismiss the wheel.

## Backend Monitoring and Analysis

- `backend/api_service.py` exposes JSON routes for registering wallets, launching analysis jobs, exporting CSV files, and updating API settings.
- `backend/helius_api.py` wraps Helius endpoints plus local heuristics to score buyers.
- State lives in JSON files and the SQLite database inside `backend/`. All sensitive outputs (`analysis_results/`, `axiom_exports/`, `config.json`, databases) remain git-ignored.
- Configure via environment variables (`HELIUS_API_KEY`, `API_RATE_DELAY`, etc.) or `backend/config.json`.
- REST endpoints match the ones documented in `backend/README.md`.

## Real-time Notifications

- `backend/websocket_server.py` is a FastAPI app that broadcasts `analysis_start` and `analysis_complete` events over `/ws`.
- The Flask API calls `/notify/analysis_*` to fan out updates. Clients (the dashboard or other tools) maintain a single WebSocket connection and react instantly instead of polling.

## Customization

- **Hotkeys and slices:** `Tray icon -> Settings`.
- **Wheel visuals:** edit `action_wheel.ahk` (search for `WheelConfig`).
- **Backend presets:** adjust `backend/api_settings.json` or call the `/api/settings` endpoint.
- **Tampermonkey helper:** tweak selectors in `userscripts/defined-fi-autosearch.user.js`.

## Troubleshooting

- **Mouse buttons ignored:** run `tools/test_mouse_buttons.ahk` to confirm Windows sees the buttons, then remap inside the Settings dialog.
- **Backend refuses to start:** ensure Python 3.9+ is in PATH, then run `python backend/api_service.py` for direct logs. Port 5001 must be free.
- **Helius analysis skipped:** verify `backend/config.json` has a valid `helius_api_key` or export it as `HELIUS_API_KEY`. Watch the console for quota errors.
- **Dashboard cannot connect to WebSocket:** confirm `start_backend.bat` launched the FastAPI server on port 5002 and that your browser allows `ws://localhost:5002/ws`.

## Security and Data Hygiene

- Sensitive outputs stay inside `backend/` and are already ignored by `.gitignore`. See `SECURITY.md` plus `docs/SECURITY_AUDIT.md` for the full checklist.
- Never commit `backend/config.json`, the SQLite databases, or anything under `backend/analysis_results/` or `backend/axiom_exports/`.
- Disable verbose logging before demos by toggling the flags in `backend/debug_config.py` and the helpers in `secure_logging.py`.

---

Gun Del Sol is intentionally hackable. Extend the wheel, add new API routes, or plug in different data providers—just keep the local-first security model intact.
