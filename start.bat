@echo off
title Sniper Bot - Inicializador Unificado
cd /d "%~dp0"

echo ========================================================
echo        SNIPER BOT - INICIALIZADOR UNIFICADO
echo ========================================================
echo.

REM 1. Liberando porta 8000
echo [1/3] Liberando a porta 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a > NUL 2>&1

REM 2. Ativando ambiente virtual
echo [2/3] Ativando ambiente virtual (.venv)...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Utilizando Python do sistema...
)

REM 3. Iniciando Launcher Hot-Reload
echo [3/3] Iniciando Servidor Web FastAPI (http://localhost:8000)...
python launcher.py

pause
