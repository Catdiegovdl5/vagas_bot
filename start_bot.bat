@echo off
title Vagas Sniper Bot - Launcher Windows
cd /d "%~dp0"

echo =======================================================================
echo              VAGAS SNIPER BOT - INICIADOR LOCAL (WINDOWS)              
echo =======================================================================
echo.

REM Liberando porta 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a > NUL 2>&1

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python launcher.py
pause
