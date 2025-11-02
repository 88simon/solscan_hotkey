# Solscan Mouse Hotkey

Instantly open Solscan for any Solana address by hovering and clicking your side mouse button.

## Features

- **XButton2** (Forward button): Open any Solana address in Solscan with customized filters
- **XButton1** (Back button): Add exclusion filters to the current Solscan page
- **Ctrl+XButton2**: Register addresses for Telegram monitoring (requires monitor service)
- Smart text detection with multiple fallback strategies
- Validates Solana base58 addresses (32-44 characters)
- Safe clipboard handling - restores your clipboard after use
- Visual feedback with tooltip notifications
- Lightweight and non-intrusive

## Requirements

### Core Requirements
- **Windows** (10 or later)
- **AutoHotkey v2.0+** - [Download here](https://www.autohotkey.com/)
- A mouse with side buttons (XButton1/XButton2)

### Optional (for Telegram Monitoring)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Flask** - Installed automatically by the launcher script

## Installation

### Step 1: Install AutoHotkey v2

1. Download AutoHotkey v2 from [https://www.autohotkey.com/](https://www.autohotkey.com/)
2. Run the installer and follow the prompts
3. Choose "Install" (default options are fine)
4. **Important**: Make sure you install v2.0+, not v1.1

### Step 2: Run the Script

**Option A: Manual Start**
1. Double-click `solscan_hotkey.ahk`
2. You'll see a green "H" icon in your system tray (bottom-right)
3. The script is now active!

**Option B: Auto-start on Windows Startup**
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create a shortcut to `solscan_hotkey.ahk` in this folder
4. The script will now run automatically when you log in

**Option C: Use the Launcher (Recommended)**
1. Double-click `start_solscan_hotkey.bat`
2. This will launch the script and minimize to tray

## Usage

### Basic Solscan Lookup

1. Hover your mouse over any Solana address (in browser, Discord, code editor, etc.)
2. **Single-click XButton2** (Forward button)
3. The address will be captured and validated
4. If valid, Solscan opens automatically with custom filters:
   - SOL transfers only
   - Excludes zero-amount transactions
   - Removes spam tokens
   - Minimum value: 100 SOL
5. A tooltip shows success or error message

### Exclusion Filters (Advanced)

When viewing a Solscan page, you can filter out specific addresses:

1. While viewing an address on Solscan, hover over an address you want to exclude
2. **Click XButton1** (Back button)
3. The current page will reload with that address added to the exclusion filter
4. Repeat to add multiple exclusions
5. The exclusion list resets when you open a new address (XButton2)

**Example use case:** Filtering out known exchange wallets or your own addresses to focus on new counterparties.

### Telegram Monitoring (Phase 1 MVP)

Register addresses to monitor for large transfers via Telegram alerts:

**Step 1: Start the Monitoring Service**
1. Install Python 3.8+ if not already installed
2. Double-click `start_monitor_service.bat`
3. The Flask service will start on `http://localhost:5001`
4. Keep this window open while monitoring

**Step 2: Register Addresses**
1. Hover over any Solana address you want to monitor
2. **Hold Ctrl + Click XButton2**
3. A tooltip confirms registration: "Monitoring registered"
4. If service is offline, you'll see: "Monitor service offline"

**Step 3: View Registered Addresses**
- Open `monitored_addresses.json` in the script folder
- Or visit `http://localhost:5001/addresses` in your browser

**Current Limitations (Phase 1):**
- Only stores addresses locally (no actual monitoring yet)
- No Telegram notifications (coming in Phase 2)
- No transaction polling (coming in Phase 2)
- Default threshold: 100 SOL (configurable in future phases)

### Examples of Valid Addresses

```
TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
So11111111111111111111111111111111111111112
EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```


## Text Capture Strategies

The script uses multiple strategies to capture text:

1. **Pre-selected text**: If you've already highlighted text, it uses that
2. **Word selection**: Double-clicks under cursor to select the word
3. **Line selection**: Selects entire line and extracts address pattern

This ensures compatibility across browsers, terminals, IDEs, and Discord.

## Validation Rules

An address is considered valid if:
- Length is between 32-44 characters
- Contains only base58 characters: `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`
- Excludes confusing characters: `0` (zero), `O` (capital o), `I` (capital i), `l` (lowercase L)

## Controls

### Mouse Hotkeys
- **XButton2** (Forward button) - Open Solana address in Solscan
- **XButton1** (Back button) - Add exclusion filter to current Solscan page
- **Ctrl + XButton2** - Register address for Telegram monitoring

### Keyboard Shortcuts
- **Ctrl+Alt+Q** - Exit the script (with confirmation)
- **Tray icon right-click** - Reload or Exit script

## Troubleshooting

### "Nothing happens when I click the side button"

1. Verify AutoHotkey is installed: Check for green "H" in system tray
2. Test your mouse button:
   - Open Notepad
   - Run `solscan_hotkey.ahk`
   - Click side button - you should see a tooltip
3. Check if your mouse software is intercepting the button
4. Run `test_mouse_buttons.ahk` to identify which button is which

### "Monitor service offline" when using Ctrl+XButton2

1. Ensure Python 3.8+ is installed: Open Command Prompt and type `python --version`
2. Start the monitoring service: Double-click `start_monitor_service.bat`
3. Verify the service is running: Visit `http://localhost:5001/health` in your browser
4. Check if port 5001 is already in use by another application
5. Look for error messages in the monitor service window

### "Says 'Not a valid Solana address'"

1. Ensure the address is fully visible (not truncated with ...)
2. Remove any quotes, brackets, or extra spaces
3. Try highlighting the address manually before clicking
4. Check the tooltip to see what text was captured

### "Clipboard is disrupted"

The script saves and restores your clipboard automatically. If issues persist:
- Increase `SELECTION_DELAY` in the script (line 17)
- Close clipboard managers temporarily

### "Works in browser but not in Terminal/IDE"

Some apps have different selection behavior:
- **Terminal**: Text must be selectable (not just hoverable)
- **VS Code**: Works best when address is on its own line
- **Discord**: Highlight the address first, then click side button

### "Opens wrong address or partial address"

Ensure the address is:
- Not mixed with other text on the same word
- Separated by spaces or punctuation
- Not split across multiple lines

## Customization

### Change Notification Duration

Edit line 16:
```ahk
NOTIFICATION_DURATION := 2000  ; milliseconds (2 seconds)
```

### Change Selection Timing

Edit line 17:
```ahk
SELECTION_DELAY := 100  ; increase if selection fails
```

### Use Different URL

To use mainnet-beta or custom RPC:
```ahk
url := "https://solscan.io/account/" . address . "?cluster=mainnet-beta"
```

## Uninstallation

1. Right-click the green "H" tray icon → Exit
2. Remove from Startup folder if you added it there
3. Delete `solscan_hotkey.ahk` and this folder
4. Optionally uninstall AutoHotkey from Control Panel

## Security & Privacy

- Runs locally - no network calls except opening Solscan in browser
- Does not log or store any data
- Only accesses clipboard temporarily (fully restored after use)
- Open source - inspect the code yourself

## Support

- **Script issues**: Check the AHK tray icon for error messages
- **AutoHotkey help**: [https://www.autohotkey.com/docs/](https://www.autohotkey.com/docs/)
- **Modify the script**: Open in any text editor

## License

Free to use and modify. No warranty provided.

---

**Enjoy instant Solscan lookups!** If you find this useful, share it with other Solana devs.
