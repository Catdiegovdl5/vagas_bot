import httpx
import urllib.parse
from typing import List, Dict, Any
from scrapers.utils import encode_param

TERMOS_AI_GENERATIVA = [
    "ia generativa", "generative ai", "prompt engineer", "llm",
    "agente de ia", "comfyui", "midjourney", "stable diffusion",
    "ai content", "copywriting ia", "rag"
]

async def scrape(keyword: str = "", location: str = "", **kwargs) -> List[Dict[str, Any]]:
    """Scraper especializado para vagas de IA Generativa & IA para Conteúdo."""
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html"
    }

    termos_busca = [keyword] if keyword and keyword.strip() else TERMOS_AI_GENERATIVA[:6]

    async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
        # 1. Busca no Remotar (API JSON pública de alta qualidade para vagas tech/IA)
        for termo in termos_busca:
            try:
                query_encoded = encode_param(termo.strip())
                remotar_url = f"https://api.remotar.com.br/jobs?search={query_encoded}"
                resp = await client.get(remotar_url)
                if resp.status_code == 200:
                    r_data = resp.json()
                    r_items = r_data if isinstance(r_data, list) else r_data.get("data", [])
                    if isinstance(r_items, list):
                        for item in r_items:
                            job_id = f"aigen_remotar_{item.get('id')}"
                            job_url = item.get("url") or item.get("apply_url") or "https://remotar.com.br"
                            jobs.append({
                                "id": job_id,
                                "platform": "Portal IA Generativa",
                                "source": "Portal IA Generativa",
                                "title": item.get("title") or item.get("name", "Sem título"),
                                "company": item.get("company_name") or item.get("company", "Empresa de IA"),
                                "location": "Remoto",
                                "url": job_url,
                                "link": job_url,
                                "job_type": "CLT/PJ",
                                "profession": termo.title(),
                                "level": "Todos",
                                "category": "ai_generativa",
                                "requirements": f"Vaga de {termo} focada em IA Generativa e criação de conteúdo."
                            })
            except Exception as e:
                print(f"[AI Generativa Scraper - Remotar] Erro ao buscar '{termo}': {e}")

        # 2. Busca no Gupy
        for termo in termos_busca:
            query_encoded = encode_param(termo.strip())
            url = f"https://portal.gupy.io/api/v1/jobs?jobName={query_encoded}&limit=15"
            try:
                response = await client.get(url)
                if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
                    data = response.json()
                    items = data.get("data", [])
                    if isinstance(items, list):
                        for item in items:
                            career_page = item.get("careerPageName", "")
                            job_id = f"aigen_{item.get('id')}"
                            job_url = item.get("jobUrl") or f"https://{career_page}.gupy.io/jobs/{item.get('id')}"
                            
                            cidade = item.get("city", "")
                            estado = item.get("state", "")
                            loc_str = "Remoto" if item.get("isRemote") else f"{cidade}, {estado}".strip(", ") or "Brasil"

                            jobs.append({
                                "id": job_id,
                                "platform": "Portal IA Generativa",
                                "source": "Portal IA Generativa",
                                "title": item.get("name", "Sem título"),
                                "company": career_page or "Empresa de IA",
                                "location": loc_str,
                                "url": job_url,
                                "link": job_url,
                                "job_type": "CLT/PJ",
                                "profession": termo.title(),
                                "level": "Todos",
                                "category": "ai_generativa",
                                "requirements": str(item.get("description", "")) or f"Vaga de {termo}"
                            })
            except Exception as e:
                print(f"[AI Generativa Scraper] Erro ao buscar '{termo}': {e}")

    # Remove duplicatas por URL
    unicos = []
    urls_vistas = set()
    for job in jobs:
        target_url = job.get("url") or job.get("link")
        if target_url and target_url not in urls_vistas:
            urls_vistas.add(target_url)
            unicos.append(job)

    return unicos
