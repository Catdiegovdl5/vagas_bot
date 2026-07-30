@echo off
title Vagas Sniper Bot - Powered by OpenRouter
mode con: cols=95 lines=30
color 0A

:: Entra automaticamente no diretório do script, não importa como seja aberto
cd /d "%~dp0"

echo =======================================================================
echo              VAGAS SNIPER BOT - INICIADOR LOCAL (WINDOWS)              
echo                  [ MOTOR DE INTELIGENCIA: OPENROUTER ]
echo =======================================================================
echo.
echo [+] Checando o Python no seu sistema...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nao encontrado no PATH! Por favor, instale o Python.
    pause
    exit /b
)

echo [+] Validando bibliotecas obrigatorias (OpenAI, python-dotenv, etc)...
pip install -q openai python-dotenv aiogram aiohttp httpx >nul 2>&1

echo [+] Limpando processos fantasmas nas portas 8000 e 8080...
FOR /F "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
FOR /F "tokens=5" %%a in ('netstat -aon ^| find ":8080" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo.
echo =======================================================================
echo                    LOGS DO SISTEMA EM TEMPO REAL:
echo =======================================================================
python launcher.py
echo.
echo =======================================================================
echo [!] O processo foi encerrado.
pause
