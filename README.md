# Solscan Mouse Hotkey

Instantly open Solscan for any Solana address by hovering and clicking your side mouse button.

## Features

- **F14/XButton2** (Forward button): Open any Solana address in Solscan with customized filters
- **F13/XButton1** (Back button): Add exclusion filters to the current Solscan page
- **Ctrl+F14/Ctrl+XButton2**: Register addresses for Telegram monitoring (requires monitor service)
- Smart text detection with multiple fallback strategies
- Validates Solana base58 addresses (32-44 characters)
- Safe clipboard handling - restores your clipboard after use
- Visual feedback with tooltip notifications
- Lightweight and non-intrusive

## Requirements

### Core Requirements
- **Windows** (10 or later)
- **AutoHotkey v2.0+** - [Download here](https://www.autohotkey.com/)
- A mouse with side buttons (or configurable gaming mouse like Logitech G502)

### Optional (for Telegram Monitoring)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Flask** - Installed automatically by the launcher script

## Installation

### Step 1: Install AutoHotkey v2

1. Download AutoHotkey v2 from [https://www.autohotkey.com/](https://www.autohotkey.com/)
2. Run the installer and follow the prompts
3. Choose "Install" (default options are fine)
4. **Important**: Make sure you install v2.0+, not v1.1

### Step 2: Configure Your Mouse (Logitech G HUB Users)

If you have a Logitech gaming mouse (G502, G Pro, etc.) with G HUB software:

1. Open Logitech G HUB
2. Select your mouse profile
3. Assign your side buttons:
   - **One side button** → Keystroke: `F14` (for opening addresses)
   - **Another side button** → Keystroke: `F13` (for exclusions)
4. Save the profile

**Why F13/F14?** G HUB can block native XButton signals. F13/F14 are unused extended function keys that work reliably with AutoHotkey.

**If you don't have G HUB or gaming mouse software:** The script works directly with XButton1/XButton2. Skip this step.

### Step 3: Run the Script

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
2. **Single-click your F14-mapped button** (or XButton2 if not using G HUB)
3. The address will be captured and validated
4. If valid, Solscan opens automatically with custom filters:
   - SOL transfers only
   - Excludes zero-amount transactions
   - Removes spam tokens
   - Minimum value: 100 SOL
5. A tooltip shows success or error message

### Exclusion Filters (Advanced)

Filter out specific addresses from a wallet's transaction list to focus on interesting counterparties.

**How it works:**

1. **Open a wallet on Solscan** (using F14 or by navigating manually)
   - Example: Open whale wallet `ABC123...`
   - Any Solscan page works - even if you opened it manually

2. **While viewing that wallet, hover over addresses you want to exclude**
   - Example: You see `Raydium DEX` appears in many transactions
   - Hover over the Raydium address
   - **Click your F13-mapped button** (or XButton1 if not using G HUB)
   - The page reloads with that address filtered out

3. **Add multiple exclusions**
   - Repeat step 2 for other addresses (exchanges, known wallets, etc.)
   - Each exclusion is added to the URL parameter: `&to_address=!Addr1,!Addr2,!Addr3`
   - The transaction list updates to hide those addresses

4. **NEW: Per-tab exclusion persistence**
   - Exclusions are stored in the browser URL, not in the script
   - Each browser tab maintains its own exclusion list independently
   - Switch between tabs freely - exclusions persist per tab
   - Reload a tab manually - exclusions remain (they're in the URL)
   - F13 reads existing exclusions from the URL and appends new ones

**Example workflow:**

You're investigating whale `7xKXt...` and want to exclude:
- `Jupiter` (aggregator)
- `Pump.fun` (token launcher)
- Your own wallet

Just hover over each and press F13 three times. The transaction list now shows only novel counterparties.

**Multi-tab workflow:**
- Tab 1: Analyze whale A with exclusions for DEXs
- Tab 2: Analyze whale B with exclusions for exchanges
- Switch between tabs freely - each maintains its own filters
- F13 always works on the currently viewed tab

**Use cases:**
- Filter out known DEXs and focus on direct wallet-to-wallet transfers
- Exclude your own addresses when analyzing trading patterns
- Remove exchange deposits/withdrawals to see OTC activity
- Analyze multiple wallets simultaneously with different exclusion sets

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
- **F14** (or XButton2 if not using G HUB) - Open Solana address in Solscan
- **F13** (or XButton1 if not using G HUB) - Add exclusion filter to current Solscan page
- **Ctrl + F14** (or Ctrl+XButton2) - Register address for Telegram monitoring

### Keyboard Shortcuts
- **Ctrl+Alt+Q** - Exit the script (with confirmation)
- **Tray icon right-click** - Reload or Exit script

## Troubleshooting

### "Nothing happens when I click the side button"

**For Logitech G HUB users:**
1. Verify G HUB button mapping:
   - Open G HUB and check your side buttons are mapped to F13/F14
   - Ensure the profile is active (not set to "Default")
2. Reload the AutoHotkey script: Right-click green "H" tray icon → Reload Script
3. Test the F13/F14 keys directly by pressing them on your keyboard - you should see a tooltip

**For non-G HUB users:**
1. Verify AutoHotkey is installed: Check for green "H" in system tray
2. Test your mouse button:
   - Open Notepad
   - Run `solscan_hotkey.ahk`
   - Click side button - you should see a tooltip
3. Check if your mouse software is intercepting the button
4. Run `test_buttons.ahk` to identify which button is which

### "G HUB button not working even after mapping to F13/F14"

1. Check G HUB profile is active (shown in the app)
2. Some G HUB versions require "Persistent Profile" to be enabled
3. Try closing and reopening G HUB
4. Restart your computer after changing G HUB settings
5. Test the key directly: Open Notepad, press your mapped button, you should see the F13/F14 key press

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
