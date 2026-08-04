@echo off
chcp 65001 > NUL
title Sniper Bot SaaS — Central de Controle Completa

echo ======================================================================
echo             🚀 INICIALIZANDO O SISTEMA SNIPER BOT SAAS
echo ======================================================================
echo.

:: 1. Ativação do Ambiente Virtual Python (se existir)
if exist .venv\Scripts\activate.bat (
    echo [1/4] Ativando ambiente virtual (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [1/4] Utilizando Python do sistema...
)

:: 2. Inicialização do Ollama em Segundo Plano
echo [2/4] Verificando e iniciando serviço de IA Ollama (Qwen 2.5)...
start /b ollama serve > NUL 2>&1

:: 3. Inicialização do Servidor FastAPI
echo [3/4] Iniciando Servidor Web FastAPI (prioriti/app.py)...
start /b python prioriti/app.py > NUL 2>&1

:: Aguarda 3 segundos para o servidor subir
timeout /t 3 /nobreak > NUL

:: 4. Abertura do Painel Web no Navegador
echo [4/4] Abrindo Painel Web (http://localhost:8000)...
start http://localhost:8000/

echo.
echo ======================================================================
echo    STATUS: SISTEMA OPERANTE E PRONTO PARA USO NO NAVEGADOR!
echo    URL do Painel Web: http://localhost:8000/
echo ======================================================================
echo.
pause
