# Monitoring and Analysis Service

Local Flask service that complements the AutoHotkey script. It stores wallet addresses for future alerts, powers the F16 token analysis flow, and surfaces results through a dashboard and REST API.

## Feature Snapshot

- **Address watchlist**: register wallets from `Ctrl + F14` or the web UI, add notes, export to JSON.
- **Token analysis jobs**: queue mint addresses from F16, collect earliest buyers and large transfers (Helius API).
- **Dashboard**: manage addresses, review analysis output, download CSVs, verify service health.
- **REST/JSON API**: integrate with other tooling or scripted workflows.

## Requirements

- Windows or macOS with Python 3.9 or newer.
- Internet access when Helius data is requested.
- Helius API key (free tier works) if you intend to run analysis jobs.

The service binds to `localhost` only, so nothing is exposed externally by default.

## Quick Start

1. Copy `config.example.json` to `config.json` and add your Helius API key if you have one.
2. Double-click `start_monitor_service.bat` (or run `python monitor_service.py`). Dependencies install automatically the first time.
3. Visit http://localhost:5001 and confirm the dashboard loads.

## Integrating With the Hotkey Script

- **Register address (Ctrl + F14)**: hover a wallet, hold `Ctrl`, press F14. The address shows up in the dashboard immediately.
- **Token analysis (F16)**: hover a token mint and press F16. A job is queued and the dashboard opens to `/analysis` once the Helius call completes.

## Configuration

`config.json` accepts the following keys:

```json
{
  "helius_api_key": "YOUR_KEY",
  "default_threshold": 100,
  "analysis_min_usd": 50,
  "analysis_window_hours": 24
}
```

- Leave out `helius_api_key` to disable analysis jobs.
- Override values with environment variables such as `HELIUS_API_KEY` when needed.

## Data Storage

- `monitored_addresses.json` holds the watchlist (git-ignored).
- `analysis_results/` caches job outputs for later review and CSV export.

Back up these files if you want to migrate the service.

## REST API Reference

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/register` | Register a wallet (`{"address": "...", "note": "..."}`) |
| `GET` | `/addresses` | List watchlist entries |
| `GET` | `/address/<address>` | Retrieve details |
| `PUT` | `/address/<address>/note` | Update the note or tag |
| `DELETE` | `/address/<address>` | Remove an entry |
| `POST` | `/import` | Import addresses from JSON |
| `POST` | `/clear` | Clear the watchlist |
| `GET` | `/analysis` | List analysis jobs |
| `POST` | `/analysis` | Queue a job (`{"token_address": "...", "min_usd": 50}`) |
| `GET` | `/analysis/<job_id>` | Job metadata and summary |
| `GET` | `/analysis/<job_id>/results` | Render results in HTML |
| `GET` | `/analysis/<job_id>/csv` | Download CSV export |
| `GET` | `/health` | Health check endpoint |

All routes return JSON unless noted.

## Dashboard Highlights

- **Home**: add wallets, search, import/export, edit notes.
- **Analysis**: earliest buyers, USD spent, transaction counts, CSV download.
- **Navigation**: quick links to watchlist, job list, and health page.

## Troubleshooting

- **Service will not start**: verify Python 3.9+ is on PATH by running `python --version`. If port 5001 is busy, edit the `app.run` call near the end of `monitor_service.py`.
- **Helius errors**: confirm the API key is present in `config.json` or provided via `HELIUS_API_KEY`. Watch the console for rate limit messages.
- **Hotkey cannot register addresses**: visit http://localhost:5001/health. If the check passes, ensure the address is valid base58 (32-44 characters). If the check fails, restart the service.
- **CSV export empty**: ensure the token actually has transfers within the configured USD threshold and time window.

## Development Tips

- Run `pip install -r requirements.txt` to mirror the batch script manually.
- Use `flask --app monitor_service.py run --debug` for live reload while adjusting the UI.
- Mock Helius by setting `HELIUS_API_KEY=dummy` and enabling the sample-data path in the source (search for `USE_SAMPLE_DATA`).

## Roadmap

1. Phase 2: richer config, per-address thresholds, better tagging.
2. Phase 3: Telegram bot integration and push notifications.
3. Phase 4: webhook support (Discord, custom) and historical analytics.

---

The monitoring service is optional but unlocks the longer-term wallet tracking workflow envisioned for the control room.
