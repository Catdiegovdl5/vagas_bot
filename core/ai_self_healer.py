import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logger = logging.getLogger("SniperBot.SelfHealer")

async def diagnose_and_heal_error(error_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agente de Diagnóstico e Autocorreção com IA.
    Analisa a exceção capturada, consulta a LLM configurada e gera sugestão de patch.
    """
    timestamp_str = error_context.get("timestamp_str", datetime.now().strftime("%Y%m%d_%H%M%S"))
    endpoint = error_context.get("endpoint", "/api/vagas")
    method = error_context.get("method", "GET")
    traceback_str = error_context.get("traceback", "")
    filepath = error_context.get("filepath", "")
    line_number = error_context.get("line_number", 0)

    # Lê o trecho do código afetado se o arquivo existir
    code_snippet = ""
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            start = max(0, line_number - 15)
            end = min(len(lines), line_number + 15)
            code_snippet = "".join([f"{i+1}: {lines[i]}" for i in range(start, end)])
        except Exception as e:
            code_snippet = f"Erro ao ler arquivo {filepath}: {e}"

    prompt = f"""
Você é um Especialista em Autocorreção e Diagnóstico de Erros Python/FastAPI.
Analise a exceção não tratada capturada no servidor e forneça um diagnóstico técnico completo.

[CONTEXTO DO ERRO]
- Data/Hora: {timestamp_str}
- Endpoint: [{method}] {endpoint}
- Arquivo Afetado: {filepath} (Linha {line_number})
- Traceback Completo:
{traceback_str}

[TRECHO DO CÓDIGO FONTE AFETADO]
{code_snippet}

Responda em formato JSON estrito contendo exatamente as seguintes chaves:
1. "root_cause": Causa raiz clara e objetiva da exceção.
2. "system_impact": Impacto no sistema e usuários.
3. "refactored_code": Trecho de código Python refatorado e corrigido para eliminar o bug.
"""

    diagnosis = {
        "root_cause": "Análise técnica de exceção não tratada no servidor.",
        "system_impact": f"Falha no endpoint {endpoint} (HTTP 500).",
        "refactored_code": "# Verifique o tratamento de exceção no endpoint afetado."
    }

    try:
        from ai_module import _call_ai
        res_text = await asyncio.to_thread(_call_ai, prompt, 800)
        if res_text:
            cleaned = res_text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            if "{" in cleaned and "}" in cleaned:
                json_part = cleaned[cleaned.find("{"):cleaned.rfind("}")+1]
                try:
                    parsed = json.loads(json_part)
                    diagnosis.update(parsed)
                except Exception:
                    diagnosis["root_cause"] = res_text[:300]
                    diagnosis["refactored_code"] = cleaned
            else:
                diagnosis["root_cause"] = res_text[:300]
                diagnosis["refactored_code"] = cleaned
    except Exception as e:
        logger.warning(f"[SelfHealer] Chamada de IA falhou: {e}")

    # Salva o patch de correção em patches/ se DEBUG estiver ativado
    is_debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    if is_debug:
        patches_dir = os.path.join(PROJECT_ROOT, "patches")
        os.makedirs(patches_dir, exist_ok=True)
        patch_file = os.path.join(patches_dir, f"fix_suggested_{timestamp_str}.py")
        try:
            with open(patch_file, "w", encoding="utf-8") as f:
                f.write(f'"""\n[AUTOCORREÇÃO IA - SUGESTÃO DE PATCH]\nData: {timestamp_str}\nEndpoint: {endpoint}\nCausa Raiz: {diagnosis.get("root_cause")}\nImpacto: {diagnosis.get("system_impact")}\n"""\n\n')
                f.write(diagnosis.get("refactored_code", "# Sem código gerado."))
            logger.info(f"[SelfHealer] Patch de correção gerado com sucesso: {patch_file}")
        except Exception as e:
            logger.error(f"[SelfHealer] Erro ao gravar patch: {e}")

    return diagnosis
