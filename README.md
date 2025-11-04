# Solscan Hotkey Toolkit

Automate Solana wallet and token digging directly from your mouse side buttons. The toolkit couples a fast AutoHotkey script with optional browser automation and a local monitoring service.

## Project Layout

| Path | Purpose |
| --- | --- |
| `solscan_hotkey.ahk` | Primary AutoHotkey script (F13, F14, F15, F16 bindings) |
| `start_solscan_hotkey.bat` | Helper launcher for the hotkey script |
| `userscripts/defined-fi-autosearch.user.js` | Tampermonkey helper for defined.fi token lookup |
| `monitor/` | Flask monitoring and analysis service (see `monitor/README.md`) |
| `test_buttons.ahk`, `test_mouse_buttons.ahk` | Diagnostics for mapping mouse buttons |

## Core Hotkey Actions

### Wheel Menu (F13 or XButton1)
Press F13 to open a radial wheel menu with all available actions. Select by:
- **Mouse gesture**: Move mouse toward desired action and click
- **Keyboard**: Press number keys 1-6 to instantly select
- **Cancel**: Press Esc or select option 6

Available wheel menu actions:
1. Open Solscan - look up the hovered address on Solscan
2. Add Exclusion - filter out hovered address from current Solscan page
3. Monitor Address - register address with monitoring service
4. Defined.fi Lookup - analyze token on defined.fi
5. Analyze Token - queue early bidder analysis via Helius API
6. Cancel - close menu without action

### Direct Hotkeys
- `F14` or `XButton2`: open the selected Solana address on Solscan with opinionated filters.
- `F15`: launch defined.fi and auto-search the hovered token mint (requires the Tampermonkey userscript).
- `F16`: queue an "early bidder" analysis job through the monitoring service (Helius API key required).
- `Ctrl + F14`: register an address with the monitoring service for future alerts.
- `Ctrl + Alt + Q`: exit the AutoHotkey script.

## Requirements

- Windows 10 or later.
- AutoHotkey v2.0 or newer.
- Mouse with two side buttons or vendor software that can emit F13-F16.

Optional components:

- Tampermonkey (Chrome, Edge, or Firefox) for the defined.fi automation.
- Python 3.9+ for the monitoring service.
- Helius API key (free tier works for light use) for token analysis.

## Quick Start (Hotkey Only)

1. Install AutoHotkey v2 from https://www.autohotkey.com/.
2. Logitech G HUB users: map side buttons to F13 and F14. Other mice can rely on native `XButton1` and `XButton2`.
3. Double-click `start_solscan_hotkey.bat` (or the `.ahk` file directly). Look for the green "H" tray icon.
4. Hover over a Solana address and press F14 or XButton2. Solscan opens with large-transfer filters already applied.

## Optional Integrations

### Defined.fi Token Lookup (F15)

1. Install Tampermonkey and create a new userscript.
2. Paste the contents of `userscripts/defined-fi-autosearch.user.js`.
3. Hover over a token mint and press F15. Defined.fi opens, triggers its Ctrl+K search, inserts the mint, and navigates to the token.

### Token Early-Bidder Analysis (F16)

1. Copy `monitor/config.example.json` to `monitor/config.json`.
2. Add your Helius API key: `{"helius_api_key": "YOUR_KEY"}`.
3. Launch `monitor/start_monitor_service.bat`. Dependencies install automatically and a Flask app starts on http://localhost:5001.
4. Hover any token mint and press F16. A job is queued; the browser opens to the job dashboard with earliest buyers, USD spent, and CSV export.

### Address Watchlist (Ctrl + F14)

1. Make sure the monitoring service is running.
2. Hover a wallet address, hold Ctrl, and press F14. The address is stored in `monitor/monitored_addresses.json`.
3. Visit http://localhost:5001 to review, tag, or export the watchlist. Telegram notifications are planned for later phases; see `monitor/README.md` for the roadmap.

## Directory Tips

- You can run the hotkey script on its own. The monitoring service is optional and lives entirely inside `monitor/`.
- Local state such as watchlists and analysis artifacts is git-ignored.
- Keep browser helpers like Tampermonkey scripts under `userscripts/` so they are easy to version and share.

## Troubleshooting

- **Mouse buttons not triggering:** confirm AutoHotkey is running, then use `test_mouse_buttons.ahk` to verify which button maps to which key. Rebind keys in vendor software if needed.
- **Defined.fi search fails:** ensure the userscript is enabled and the site has finished loading. Refresh the page after installing or editing the script.
- **Monitoring service unavailable:** verify `python --version` works inside the `monitor` folder and that the console prints `Running on http://localhost:5001`. Check that port 5001 is free.
- **Invalid address pop-up:** only base58 addresses 32-44 characters long are accepted. Highlight the clean address without quotes or punctuation.

Additional troubleshooting, API endpoints, and configuration details are in `monitor/README.md`.

## Customization Hints

- Tweak Solscan filters, notification timing, and hotkey bindings directly in `solscan_hotkey.ahk`.
- Modify the defined.fi userscript to apply extra filters (for example a minimum USD size) once you inspect the page in DevTools.
- Extend the monitoring service with new endpoints or schedulers; it already exposes `/analysis`, `/addresses`, and CSV exports.

## Uninstall

1. Exit the AutoHotkey script (tray icon -> Exit or Ctrl + Alt + Q).
2. Remove any shortcuts from the Windows Startup folder.
3. Delete the repository directory. Optionally uninstall AutoHotkey or Python if you no longer need them.

## Security Notes

- All scripts run locally. The hotkey opens Solscan and defined.fi in your browser; the monitoring service only reaches out to Helius when configured.
- Clipboard contents are restored after each hotkey run.
- Watchlist data stays in `monitor/monitored_addresses.json`, which is ignored by git.

---

Enjoy faster Solana due diligence. Contributions, feedback, and new hotkey ideas are welcome.
