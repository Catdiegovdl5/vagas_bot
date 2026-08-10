import os
import sys
import json
import traceback
import logging
import asyncio
from datetime import datetime
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logger = logging.getLogger("SniperBot.ErrorReporter")

async def error_reporter_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware Capturador Global de Exceções.
    Extrai o contexto completo da falha e grava relatório em logs/error_context_YYYYMMDD_HHMMSS.json.
    """
    try:
        return await call_next(request)
    except Exception as exc:
        timestamp_dt = datetime.now()
        timestamp_str = timestamp_dt.strftime("%Y%m%d_%H%M%S")
        
        # Extrai traceback detalhado
        tb_list = traceback.format_exception(type(exc), exc, exc.__traceback__)
        tb_str = "".join(tb_list)
        
        # Tenta identificar o arquivo e a linha da falha
        filepath = ""
        line_number = 0
        if exc.__traceback__:
            tb_last = traceback.extract_tb(exc.__traceback__)[-1]
            filepath = tb_last.filename
            line_number = tb_last.lineno

        # Extrai parâmetros e payload com segurança
        query_params = dict(request.query_params)
        body_payload = {}
        try:
            body_bytes = await request.body()
            if body_bytes:
                body_payload = json.loads(body_bytes.decode("utf-8", errors="ignore"))
        except Exception:
            body_payload = {"raw": "Não foi possível realizar o parse do payload"}

        error_context = {
            "timestamp": timestamp_dt.isoformat(),
            "timestamp_str": timestamp_str,
            "endpoint": request.url.path,
            "method": request.method,
            "query_params": query_params,
            "payload": body_payload,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "filepath": filepath,
            "line_number": line_number,
            "traceback": tb_str
        }

        # Salva o relatório em logs/error_context_YYYYMMDD_HHMMSS.json e .md
        logs_dir = os.path.join(PROJECT_ROOT, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        json_log = os.path.join(logs_dir, f"error_context_{timestamp_str}.json")
        md_log = os.path.join(logs_dir, f"error_context_{timestamp_str}.md")

        try:
            with open(json_log, "w", encoding="utf-8") as f:
                json.dump(error_context, f, ensure_ascii=False, indent=2)
                
            with open(md_log, "w", encoding="utf-8") as f:
                f.write(f"# 🚨 RELATÓRIO CONTEXTUAL DE ERRO DE SISTEMA\n")
                f.write(f"- **Data/Hora**: `{error_context['timestamp']}`\n")
                f.write(f"- **Endpoint**: `{request.method} {request.url.path}`\n")
                f.write(f"- **Exceção**: `{error_context['exception_type']}: {error_context['exception_message']}`\n")
                f.write(f"- **Localização**: `{filepath}:{line_number}`\n\n")
                f.write(f"### 📥 Parâmetros e Payload\n```json\n{json.dumps({'query': query_params, 'payload': body_payload}, indent=2, ensure_ascii=False)}\n```\n\n")
                f.write(f"### 📜 Traceback Completo\n```python\n{tb_str}\n```\n")
                
            logger.error(f"[ErrorReporter] Relatório salvo em {json_log}")
        except Exception as log_err:
            logger.error(f"[ErrorReporter] Erro ao gravar log de exceção: {log_err}")

        # Dispara o Agente de Diagnóstico e Autocorreção com IA em background
        try:
            from core.ai_self_healer import diagnose_and_heal_error
            asyncio.create_task(diagnose_and_heal_error(error_context))
        except Exception as heal_err:
            logger.warning(f"[ErrorReporter] Falha ao disparar self-healer: {heal_err}")

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Ocorreu um erro interno no servidor.",
                "error_id": timestamp_str
            }
        )
