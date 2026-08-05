@echo off
title Sniper Bot SaaS - Central de Controle Completa

echo ======================================================================
echo             INICIALIZANDO O SISTEMA SNIPER BOT SAAS
echo ======================================================================
echo.

REM 1. Liberar a porta 8000 caso haja algum processo antigo travado
echo [1/4] Verificando e liberando a porta 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a > NUL 2>&1

REM 2. Ativacao do Ambiente Virtual Python
if exist .venv\Scripts\activate.bat (
    echo [2/4] Ativando ambiente virtual (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [2/4] Utilizando Python do sistema...
)

REM 3. Inicializacao do Servidor FastAPI em janela visivel de log
echo [3/4] Iniciando Servidor Web FastAPI (prioriti/app.py)...
start "Sniper Bot Server (FastAPI - Porta 8000)" python prioriti/app.py

REM Aguarda 3 segundos para o servidor inicializar
timeout /t 3 /nobreak > NUL

REM 4. Abertura do Painel Web no Navegador Padrao
echo [4/4] Abrindo Painel Web (http://localhost:8000)...
start http://localhost:8000/

echo.
echo ======================================================================
echo    STATUS: SERVIDOR EM EXECUCAO NA JANELA SECUNDARIA!
echo    URL do Painel Web: http://localhost:8000/
echo ======================================================================
echo.
pause
