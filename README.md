# Gun Del Sol

Gun Del Sol turns your mouse buttons into a Solana intelligence desk. The AutoHotkey script provides instant Solscan lookups, defined.fi token pivots, and a configurable wheel menu, while the optional monitoring service tracks wallets and analyzes early bidders through Helius.

## Top Features
- **Radial wheel (F13 / XButton1)** – Choose Solscan lookup, exclusions, monitoring, defined.fi pivots, token analysis, or cancel with one gesture.
- **Direct shortcuts** – F14 opens Solscan, F15 launches defined.fi, F16 queues early-bidder analysis, Ctrl+F14 registers addresses, Ctrl+Alt+Q exits.
- **Configurable hotkeys/actions** – Rebind the wheel hotkey or remap actions in the built-in Settings dialog (`Tray icon → Settings`).
- **Defined.fi automation** – Tampermonkey user script opens tokens with pre-filled filters.
- **Monitoring service (optional)** – Flask API + dashboard for watchlists, analysis jobs, CSV exports, and future Telegram alerts.

## Project Layout

| Path | Purpose |
| --- | --- |
| `gun_del_sol.ahk` | Main AutoHotkey v2 script (wheel menu, shortcuts, settings dialog) |
| `launch_gun_del_sol.bat` | Convenience launcher for the script |
| `userscripts/defined-fi-autosearch.user.js` | Tampermonkey helper for defined.fi auto-search |
| `monitor/` | Flask monitoring service (details in `monitor/README.md`) |
| `tools/` | Diagnostics (`test_mouse_buttons.ahk`) and helpers |

## Requirements
- Windows 10 or later
- AutoHotkey v2.x
- Mouse with two side buttons *or* vendor software capable of sending F13–F16

Optional:
- Tampermonkey (Chrome/Edge/Firefox) for defined.fi automation
- Python 3.9+ for the monitoring service
- Helius API key (even free tier) to enable token analysis

## Quick Start
1. Install AutoHotkey v2 from <https://www.autohotkey.com/>.
2. Map your mouse buttons (Logitech G HUB users should map to F13/F14; most mice expose XButton1/XButton2).
3. Run `launch_gun_del_sol.bat` or double-click `gun_del_sol.ahk`. Look for the green **H** tray icon.
4. Hover a Solana address and press F14 (or your mapped button). Solscan opens with high-signal filters applied.

## Wheel Menu (F13)
- **Mouse** – hold F13, slide toward an action, release/click to execute.
- **Keyboard** – press number keys 1–6 while holding F13.
- **Cancel** – press Esc or release over slice 6.

Default wheel actions (configurable via Settings):
1. **Solscan** – open hovered address
2. **Exclude** – add hovered address to Solscan filters
3. **Monitor** – register address with the monitoring service
4. **defined.fi** – open token page via Tampermonkey script
5. **Analyze** – queue early-bidder analysis (Helius)
6. **Cancel** – close the wheel

## Optional Integrations
### defined.fi Token Lookup (F15)
1. Install Tampermonkey.
2. Create a new script and paste `userscripts/defined-fi-autosearch.user.js`.
3. Hover a token mint and press F15. The script focuses defined.fi, triggers Ctrl+K, pastes the mint, and navigates to the token page with your filters.

### Monitoring & Analysis (F16 / Ctrl+F14)
1. Copy `monitor/config.example.json` to `monitor/config.json` and set `helius_api_key`.
2. Run `monitor/start_monitor_service.bat` (auto-installs dependencies, serves on `http://localhost:5001`).
3. **Ctrl+F14** registers addresses to the watchlist. **F16** queues early-bidder analysis jobs; the dashboard lists buyers, USD volume, and CSV exports.

More details, API routes, and troubleshooting live in `monitor/README.md`.

## Customization
- **Hotkeys & wheel actions** – `Tray icon → Settings` opens a GUI where you can record a new wheel hotkey and remap slices. Config is saved in `settings.ini`.
- **Solscan filters & notifications** – edit `gun_del_sol.ahk` (search for `BuildSolscanUrl` and `ShowNotification`).
- **defined.fi automation** – tweak the Tampermonkey script to pre-set filters such as minimum USD or toggle cluster.
- **Monitoring service** – extend Flask routes or adjust analysis thresholds in `monitor/config.json`.

## Troubleshooting
- **Mouse buttons ignored** – confirm AutoHotkey is running; use `tools/test_mouse_buttons.ahk` to identify button names; update mappings in vendor drivers if needed.
- **Wheel hotkey not triggering** – open Settings and re-record the hotkey. Ensure no other app is intercepting it.
- **defined.fi script fails** – verify the Tampermonkey script is enabled and refresh the page after installation. Check browser console for selector changes.
- **Monitoring service offline** – run `python --version`, start the service manually (`python monitor_service.py`), and check for port collisions on 5001.
- **Invalid address warning** – ensure a full Solana address (base58, 32–44 chars) is selected; avoid truncated UI elements.

## Directory Hygiene
- The hotkey script works without the monitoring service. All optional state (watchlist, analysis results) stays inside `monitor/` and is git-ignored.
- Keep browser automation scripts under `userscripts/` so you can share or version them.
- When exporting or backing up data, copy `monitor/monitored_addresses.json` and `monitor/analysis_results/`.

## Security / Privacy
- Script activity remains local unless you enable Helius or defined.fi features. Clipboard contents are restored after each capture.
- Monitoring service listens on `localhost` only. API keys stay in `monitor/config.json` or environment variables.
- Git ignores personal data by default; add custom ignore rules if you store extra files.

## Uninstall
1. Exit the AutoHotkey script (tray icon → Exit or press Ctrl+Alt+Q).
2. Stop the monitoring service if running.
3. Remove startup shortcuts if you created any.
4. Delete the repository; optionally uninstall AutoHotkey/Python if you no longer need them.

---

Gun Del Sol is built to be hacked on. Pull requests, issues, and feature ideas are welcome—especially around new wheel actions, defined.fi filters, and monitoring automations.
