@echo off
title Bot Cacador de Vagas & Servidor Web
color 0B
echo.
echo    [ PREPARANDO O ECOSSISTEMA DO SNIPER BOT ]
echo.
cd /d "C:\Users\99196\OneDrive\Documentos\vagas_bot"

echo [+] Encerrando instancias antigas na porta 8000...
FOR /F "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo [+] Iniciando Servidor Web e Bot de Telegram...
python launcher.py
pause
