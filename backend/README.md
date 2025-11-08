# Gun Del Sol – Monitoring & Analysis Service

This Flask app powers the “backend brain” of Gun Del Sol. It accepts addresses from the hotkey script, stores watchlists, runs token analysis through Helius, and exposes everything via a dashboard and JSON API. It only listens on `localhost`, so your data never leaves the machine unless you call external APIs.

## Highlights
- **Watchlist storage** – Use the wheel menu's "Monitor" action (or the dashboard) to add wallets, notes, and thresholds. Import/export as JSON at any time.
- **Early-bidder analysis** – Use the wheel menu's "Analyze" action to queue a job that fetches recent token activity from Helius, identifies large buyers, and surfaces CSV/PDF-ready results.
- **Web dashboard** – Browse `/addresses` and `/analysis` views, trigger exports, and check health status.
- **REST API** – Automate registrations, pull job results, or hook into other tooling.

## Requirements
- Python 3.9+ on Windows or macOS (Linux works with minor path tweaks).
- Internet access if you run Helius-powered analysis.
- Helius API key (omit to disable token analysis).

## Getting Started
1. Duplicate `monitor/config.example.json` → `monitor/config.json`. Add your Helius key if you want analysis.
2. Start the service: double-click `start_monitor_service.bat` **or** run `python monitor_service.py`. Dependencies install on first launch.
3. Visit <http://localhost:5001>. You should see the dashboard with green health status.
4. From the hotkey script, open the wheel menu and use the "Monitor" action to register addresses or "Analyze" action to queue analysis jobs. Results appear under `/analysis`.

## Configuration
`config.json` controls defaults:
```json
{
  "helius_api_key": "YOUR_KEY",
  "default_threshold": 100,
  "analysis_min_usd": 50,
  "analysis_window_hours": 24
}
```
- Omit `helius_api_key` to skip Helius calls (analysis endpoints will return a warning).
- Override from environment variables (`HELIUS_API_KEY`, etc.) when deploying elsewhere.

## Data Files
| File/Folder | Purpose |
| --- | --- |
| `monitored_addresses.json` | Primary watchlist store (git-ignored) |
| `analysis_results/` | Cached job outputs and CSV/HTML artifacts |
| `config.json` | Runtime configuration (never commit real keys) |

Back up the JSON + results folder if you migrate machines.

## REST API
| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/register` | Add a wallet (`{"address":"...","note":"..."}`) |
| `GET` | `/addresses` | List current watchlist entries |
| `GET` | `/address/<address>` | Single address details |
| `PUT` | `/address/<address>/note` | Update a note/tag |
| `DELETE` | `/address/<address>` | Remove an entry |
| `POST` | `/import` | Bulk import from JSON |
| `POST` | `/clear` | Drop all watchlist data |
| `GET` | `/analysis` | List jobs with status |
| `POST` | `/analysis` | Queue job (`{"token_address":"...","min_usd":50}`) |
| `GET` | `/analysis/<job_id>` | Fetch job metadata/results |
| `GET` | `/analysis/<job_id>/results` | Render job in HTML |
| `GET` | `/analysis/<job_id>/csv` | Download CSV |
| `GET` | `/health` | Health check used by the hotkey script |

All responses are JSON unless the route explicitly serves HTML/CSV.

## Dashboard Tips
- **Addresses tab** – add, remove, tag, and export watchlist entries.
- **Analysis tab** – review queued/completed jobs, open the results page, download CSV.
- **Health badge** – bottom-right link to `/health`; use it when debugging hotkey-to-service communication.

## Troubleshooting
- **Service won’t start** – run `python --version`. If the port is taken, edit the `app.run` port near the bottom of `monitor_service.py`.
- **Helius errors** – check that `config.json` or the `HELIUS_API_KEY` env var is set. Watch the console for rate-limit messages.
- **Hotkey fails to register** – visit `/health`. If it returns 200, ensure the address is a valid base58 string (32–44 chars). Otherwise restart the service.
- **Analysis empty/CSV blank** – ensure the token has recent activity above `analysis_min_usd` within `analysis_window_hours`.

## Development Notes
- Install dependencies manually with `pip install -r requirements.txt` if you prefer.
- Use `flask --app monitor_service.py run --debug` for hot reload while tweaking templates.
- There’s a sample-data path (`USE_SAMPLE_DATA`) for working without Helius—search the source to enable it.

## Roadmap
1. Per-address thresholds and richer tagging.
2. Telegram / Discord bot integration with push alerts.
3. Webhook support and historical analytics explorer.

---
The monitoring service is optional, but when paired with the Gun Del Sol hotkey script it becomes the long-term control room for your Solana address intelligence.
