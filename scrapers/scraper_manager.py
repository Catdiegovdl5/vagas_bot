import asyncio
import inspect
import importlib
from typing import List, Dict, Any

from scrapers import gupy, linkedin, infojobs, ai_generativa

import os
import glob

# Módulos principais com import direto
SCRAPER_MODULES = [
    gupy,
    linkedin,
    infojobs,
    ai_generativa,
]

# Auto-descoberta dinâmica de todos os scrapers presentes na pasta scrapers/
scrapers_dir = os.path.dirname(os.path.abspath(__file__))
module_files = glob.glob(os.path.join(scrapers_dir, "*.py"))

for file_path in module_files:
    mod_name = os.path.splitext(os.path.basename(file_path))[0]
    if mod_name in ["__init__", "utils", "ai_filter", "scraper_manager", "run_test"]:
        continue
    try:
        mod = importlib.import_module(f"scrapers.{mod_name}")
        if hasattr(mod, "scrape") and mod not in SCRAPER_MODULES:
            SCRAPER_MODULES.append(mod)
    except Exception as e:
        pass

async def executar_busca_global(
    keyword: str = "",
    location: str = "",
    category: str = "",
    seniority: str = "",
    level: str = "Todos",
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Executa todos os scrapers concorrentemente para qualquer combinacao de parametros.
    Remove duplicatas por URL/Link.
    """
    semaphore = asyncio.Semaphore(5)  # Limita requisições simultâneas para evitar bloqueios

    async def rodar_com_semaforo(modulo):
        async with semaphore:
            mod_name = getattr(modulo, "__name__", str(modulo))
            try:
                if inspect.iscoroutinefunction(modulo.scrape):
                    return await modulo.scrape(
                        keyword=keyword,
                        location=location,
                        category=category,
                        seniority=seniority,
                        level=level,
                        **kwargs
                    )
                else:
                    return await asyncio.to_thread(
                        modulo.scrape,
                        keyword=keyword,
                        location=location,
                        category=category,
                        seniority=seniority,
                        level=level,
                        **kwargs
                    )
            except Exception as err:
                print(f"[Orquestrador] Falha no scraper {mod_name}: {err}")
                return []

    tarefas = [rodar_com_semaforo(m) for m in SCRAPER_MODULES]
    resultados_brutos = await asyncio.gather(*tarefas, return_exceptions=True)

    # Consolida e remove duplicatas por URL/Link
    vagas_unicas = []
    urls_vistas = set()

    for lista in resultados_brutos:
        if isinstance(lista, list):
            for vaga in lista:
                if isinstance(vaga, dict):
                    url = vaga.get("url") or vaga.get("link")
                    if url and url not in urls_vistas:
                        urls_vistas.add(url)
                        vagas_unicas.append(vaga)

    return vagas_unicas
