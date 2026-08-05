import asyncio
import inspect
import importlib
from typing import List, Dict, Any

from scrapers import gupy, linkedin, infojobs

# Modulos de scrapers disponiveis
SCRAPER_MODULES = [
    gupy,
    linkedin,
    infojobs,
]

# Tenta importar scrapers adicionais se disponiveis no ambiente
for mod_name in ["catho", "remotar", "vagas_com", "workana", "programathor", "jooble"]:
    try:
        mod = importlib.import_module(f"scrapers.{mod_name}")
        if hasattr(mod, "scrape"):
            SCRAPER_MODULES.append(mod)
    except Exception:
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
