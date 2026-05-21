# Consumo do Claudinho — Desktop Widget (Windows)

A floating always-on-top desktop widget for Windows that shows your Claude Code
session (5h) and weekly (7d) utilization — no ESP32 hardware needed.

Built on top of [HermannBjorgvin/Clawdmeter](https://github.com/HermannBjorgvin/Clawdmeter).
All credit for the original project goes to its creator.

![Widget preview](../assets/demo.jpeg)

## Features

- Pixel-art Clawd animations sourced from [claudepix.vercel.app](https://claudepix.vercel.app) that react to your usage rate:
  - **0–39%** → idle (blink, breathe, look around)
  - **40–69%** → work (coding, think)
  - **70–100%** → dance (bounce, sway, djmix…)
- Two progress bars: **SESSÃO · 5H** and **SEMANAL · 7D** with reset countdowns
- Color shifts green → amber → red as utilization climbs
- True transparent rounded corners (12px radius)
- System tray icon with live % badge — minimize and restore from tray
- Drag to reposition; position saved between sessions
- Auto-polls every 60 s using your existing Claude Code credentials

## Requirements

- Windows 10/11
- Python 3.9+
- Claude Code installed and signed in (credentials read from `~/.claude/.credentials.json`)

## Installation

```powershell
cd widget
.\install.ps1
```

The installer will:
1. Create a Python venv in `widget/.venv`
2. Install dependencies (`httpx`, `pystray`, `Pillow`)
3. Ask if you want a Windows Startup shortcut (auto-launch at login)
4. Optionally launch the widget immediately

## Running manually

```powershell
# From the widget/ folder
.\.venv\Scripts\pythonw.exe claude_widget.py
```

Use `pythonw.exe` (not `python.exe`) to run without a console window.

## Does it increase Claude consumption?

Technically yes, but negligibly. Every 60 seconds the widget sends one API call
to `claude-haiku-4-5-20251001` with `max_tokens: 1` — the goal is the
rate-limit headers in the response, not the reply itself. The original project
describes this as *"one token of Haiku, basically free"*.

## Credits

- Original project, firmware, BLE protocol, daemon, and animations pipeline: **Hermann Björgvin** — https://github.com/HermannBjorgvin/Clawdmeter
- Pixel-art Clawd sprites: **[@amaanbuilds](https://x.com/amaanbuilds)** — https://claudepix.vercel.app
- Desktop widget (this folder): personal fork, no commercial purpose
