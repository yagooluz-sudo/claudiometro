#Requires -Version 5.1
<#
.SYNOPSIS
    Install and optionally auto-start the Claude Usage Widget.
.DESCRIPTION
    Creates a Python venv, installs dependencies, and (optionally) adds a
    shortcut to the Windows Startup folder so the widget launches at login.
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "=== Claude Usage Widget installer ===" -ForegroundColor Cyan
Write-Host ""

# ── 1. Python check ───────────────────────────────────────────────────────────

$python = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 9) {
                $python = $candidate
                Write-Host "Found: $ver" -ForegroundColor Green
                break
            }
        }
    } catch { }
}

if (-not $python) {
    Write-Host "Python 3.9+ not found. Install it from https://python.org and re-run." `
        -ForegroundColor Red
    exit 1
}

# ── 2. Create venv ────────────────────────────────────────────────────────────

$venvDir = Join-Path $ScriptDir ".venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $python -m venv $venvDir
} else {
    Write-Host "Virtual environment already exists, skipping." -ForegroundColor DarkGray
}

$pip    = Join-Path $venvDir "Scripts\pip.exe"
$pythonExe = Join-Path $venvDir "Scripts\pythonw.exe"   # pythonw = no console window
$script = Join-Path $ScriptDir "claude_widget.py"

# ── 3. Install dependencies ───────────────────────────────────────────────────

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $pip install -q -r (Join-Path $ScriptDir "requirements.txt")
Write-Host "Dependencies installed." -ForegroundColor Green

# ── 4. Quick smoke-test (import check) ───────────────────────────────────────

$check = Join-Path $venvDir "Scripts\python.exe"
$ok = & $check -c "import httpx, pystray, PIL, tkinter; print('ok')" 2>&1
if ($ok -ne "ok") {
    Write-Host "Import check failed: $ok" -ForegroundColor Red
    exit 1
}
Write-Host "Import check passed." -ForegroundColor Green

# ── 5. Startup shortcut (optional) ───────────────────────────────────────────

Write-Host ""
$addStartup = Read-Host "Add to Windows Startup so the widget launches at login? [y/N]"
if ($addStartup -match "^[yY]") {
    $startupDir = [Environment]::GetFolderPath("Startup")
    $lnkPath    = Join-Path $startupDir "Claude Usage Widget.lnk"

    $wsh  = New-Object -ComObject WScript.Shell
    $link = $wsh.CreateShortcut($lnkPath)
    $link.TargetPath       = $pythonExe
    $link.Arguments        = "`"$script`""
    $link.WorkingDirectory = $ScriptDir
    $link.WindowStyle      = 7          # minimised (goes straight to tray)
    $link.Description      = "Claude Code usage floating widget"
    $link.Save()

    Write-Host "Startup shortcut created: $lnkPath" -ForegroundColor Green
} else {
    Write-Host "Skipped startup shortcut." -ForegroundColor DarkGray
}

# ── 6. Launch now ────────────────────────────────────────────────────────────

Write-Host ""
$runNow = Read-Host "Launch the widget now? [Y/n]"
if ($runNow -notmatch "^[nN]") {
    Write-Host "Launching widget..." -ForegroundColor Cyan
    Start-Process $pythonExe -ArgumentList "`"$script`"" -WorkingDirectory $ScriptDir
    Write-Host "Widget started. Look for the ● icon in the system tray." -ForegroundColor Green
}

Write-Host ""
Write-Host "Done. To run manually:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\pythonw.exe claude_widget.py" -ForegroundColor White
Write-Host ""
