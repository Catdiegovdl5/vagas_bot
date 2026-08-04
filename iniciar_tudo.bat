@echo off
title Sniper Bot SaaS - Central de Controle Completa

echo ======================================================================
echo             INICIALIZANDO O SISTEMA SNIPER BOT SAAS
echo ======================================================================
echo.

REM 1. Ativacao do Ambiente Virtual Python
if exist .venv\Scripts\activate.bat (
    echo [1/4] Ativando ambiente virtual (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [1/4] Utilizando Python do sistema...
)

REM 2. Inicializacao do Ollama em Segundo Plano
echo [2/4] Verificando e iniciando servico de IA Ollama (Qwen 2.5)...
start /b ollama serve > NUL 2>&1

REM 3. Inicializacao do Servidor FastAPI
echo [3/4] Iniciando Servidor Web FastAPI (prioriti/app.py)...
start /b python prioriti/app.py > NUL 2>&1

REM Aguarda 3 segundos para o servidor subir
timeout /t 3 /nobreak > NUL

REM 4. Abertura do Painel Web no Navegador
echo [4/4] Abrindo Painel Web (http://localhost:8000)...
start http://localhost:8000/

echo.
echo ======================================================================
echo    STATUS: SISTEMA OPERANTE E PRONTO PARA USO NO NAVEGADOR!
echo    URL do Painel Web: http://localhost:8000/
echo ======================================================================
echo.
pause
