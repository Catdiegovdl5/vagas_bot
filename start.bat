@echo off
title Sniper Bot - Inicializador Unificado
echo ========================================================
echo        SNIPER BOT - INICIALIZADOR UNIFICADO 🚀
echo ========================================================
echo.
echo [1/3] Encerrando instancias antigas do Bot e Servidor Web...
taskkill /FI "WINDOWTITLE eq Sniper Telegram Bot*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sniper Web Server*" /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Ativando ambiente virtual (.venv)...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [ERRO] Ambiente virtual .venv nao encontrado!
    pause
    exit /b
)

echo [3/3] Iniciando Servidor Web (FastAPI) e Bot Telegram...
start "Sniper Web Server" cmd /k "uvicorn app:app --reload --log-level debug --port 8000"
start "Sniper Telegram Bot" cmd /k "python -u bot.py"

echo.
echo ========================================================
echo   ✅ Tudo Pronto! 
echo   - Painel Web: http://localhost:8000
echo   - Bot do Telegram: Conectado e Operativo
echo ========================================================
echo.
pause
