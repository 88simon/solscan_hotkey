# Gun Del Sol

Gun Del Sol turns your mouse buttons into a Solana intelligence desk. The AutoHotkey script provides instant Solscan lookups, defined.fi token pivots, and a configurable wheel menu, while the optional monitoring service tracks wallets and analyzes early bidders through Helius.

## Top Features
- **Radial wheel (configurable, defaults to `` ` ``)** – Choose Solscan lookup, exclusions, monitoring, defined.fi pivots, token analysis, or cancel with one gesture.
- **Configurable hotkeys/actions** – Rebind the wheel hotkey or remap actions in the built-in Settings dialog (`Tray icon → Settings`).
- **Native mouse button support** – Works directly with XButton1/XButton2 (mouse side buttons) without requiring F-key remapping.
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
- Mouse with side buttons recommended (most mice work natively via XButton1/XButton2)

Optional:
- Tampermonkey (Chrome/Edge/Firefox) for defined.fi automation
- Python 3.9+ for the monitoring service
- Helius API key (even free tier) to enable token analysis

## Quick Start
1. Install AutoHotkey v2 from <https://www.autohotkey.com/>.
2. Run `launch_gun_del_sol.bat` or double-click `gun_del_sol.ahk`. Look for the green **H** tray icon.
3. Press the backtick key (`` ` ``) to open the radial wheel menu, or open Settings from the tray icon to customize your hotkey.
4. Hover over any action and click, or press number keys 1-6 to select instantly.

## Wheel Menu
- **Default hotkey:** backtick (`` ` ``), fully customizable via `Tray icon → Settings`
- **Mouse selection** – hold the hotkey, move toward an action, release or click to execute
- **Keyboard selection** – press number keys 1–6 while the menu is open
- **Cancel** – press Esc or select option 6

Default wheel actions (configurable via Settings):
1. **Solscan** – open hovered address
2. **Exclude** – add hovered address to Solscan filters
3. **Monitor** – register address with the monitoring service
4. **defined.fi** – open token page via Tampermonkey script
5. **Analyze** – queue early-bidder analysis (Helius)
6. **Cancel** – close the wheel

## Optional Integrations
### defined.fi Token Lookup
1. Install Tampermonkey.
2. Create a new script and paste `userscripts/defined-fi-autosearch.user.js`.
3. Use the wheel menu's "Defined.fi" action to trigger automated token lookup with pre-filled filters.

### Monitoring & Analysis Service
1. Copy `monitor/config.example.json` to `monitor/config.json` and set `helius_api_key`.
2. Run `monitor/start_monitor_service.bat` (auto-installs dependencies, serves on `http://localhost:5001`).
3. Use the wheel menu's **Monitor** action to register addresses to the watchlist, or **Analyze** action to queue early-bidder analysis jobs. The dashboard lists buyers, USD volume, and CSV exports.

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
