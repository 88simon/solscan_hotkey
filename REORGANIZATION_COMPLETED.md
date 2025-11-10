# Gun Del Sol – Codebase Status

**Last updated:** 2025-11-10  
**Scope:** Desktop automation (AutoHotkey) + local monitoring backend

---

## What Changed

- Removed duplicate AutoHotkey libraries and obsolete batch files.
- Promoted documentation into `/docs` and added security-specific guides.
- Renamed the legacy `monitor/` service to `/backend/` and updated imports (`analyzed_tokens_db.py`, `secure_logging.py`, `debug_config.py`).
- Split launchers:
  - `start.bat` orchestrates the wheel, Flask API, WebSocket server, and dashboard.
  - `start_backend.bat` and `start_frontend.bat` run services independently.
- Added FastAPI WebSocket server (`backend/websocket_server.py`) for New UI notifications.

---

## Current Layout (abridged)

```
solscan_hotkey/
├─ action_wheel.ahk
├─ action_wheel_settings.ini
├─ start.bat
├─ start_backend.bat
├─ start_frontend.bat
├─ README.md
├─ SECURITY.md
├─ backend/
│  ├─ api_service.py
│  ├─ helius_api.py
│  ├─ websocket_server.py
│  ├─ analyzed_tokens_db.py
│  ├─ secure_logging.py
│  ├─ debug_config.py
│  ├─ config.example.json
│  ├─ config.json          (git-ignored)
│  ├─ analysis_results/    (git-ignored)
│  ├─ axiom_exports/       (git-ignored)
│  └─ *.db                 (git-ignored)
├─ docs/
│  ├─ SECURITY_AUDIT.md
│  └─ SECURITY_QUICKFIX.md
├─ tools/
│  └─ test_mouse_buttons.ahk
└─ userscripts/
   └─ defined-fi-autosearch.user.js
```

All sensitive data lives under `backend/` and is ignored by git.

---

## Testing Checklist

- [ ] `start_backend.bat` launches both the Flask API (http://localhost:5001) and FastAPI WebSocket server (http://localhost:5002).
- [ ] `python backend/api_service.py` loads without import errors.
- [ ] Registering a wallet via `/register` persists to `backend/monitored_addresses.json`.
- [ ] Analysis jobs populate `backend/analysis_results/` and `analyzed_tokens.db`.
- [ ] WebSocket `/notify/analysis_complete` triggers the dashboard.
- [ ] AutoHotkey wheel can reach the backend over `http://localhost:5001`.

---

## Recommended Follow-ups

1. Finish the security fixes listed in `docs/SECURITY_AUDIT.md`.
2. Add architectural documentation (`docs/ARCHITECTURE.md`, `docs/API_REFERENCE.md`).
3. Ship a formal CHANGELOG once the backend authentication work lands.
4. Add automated tests for `backend/helius_api.py` and `backend/api_service.py`.
5. Publish a LICENSE when you are ready to share binaries.

The repository is now tidy enough for daily work—keep README.md and SECURITY.md in sync whenever you move files or rename services.
