@echo off
chcp 65001 >nul
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Consumo do Claudinho — Instalação      ║
echo  ╚══════════════════════════════════════════╝
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado.
    echo.
    echo  Por favor instale o Python antes de continuar:
    echo  1. Acesse: https://www.python.org/downloads/
    echo  2. Clique no botão amarelo "Download Python"
    echo  3. NA TELA DE INSTALAÇÃO: marque "Add python.exe to PATH"
    echo  4. Clique em "Install Now"
    echo  5. Feche e abra este arquivo novamente após instalar
    echo.
    pause
    exit /b 1
)

echo  Python encontrado. Iniciando instalação...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0install.ps1"

echo.
pause
