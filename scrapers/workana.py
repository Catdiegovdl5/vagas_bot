import urllib.parse
import asyncio
import random
import unicodedata
from playwright.async_api import async_playwright

try:
    from playwright_stealth import stealth_async
except ImportError:
    stealth_async = None

async def scrape(keyword="Python", level="Todos", max_pages=100, location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""

    kw_str = keyword or "Python"
    lvl_str = level or "Todos"

    # 1. Normalizar e expandir termos de busca via CO_OCCURRENCE_RULES do bot
    kw_norm = "".join(
        c for c in unicodedata.normalize('NFKD', kw_str)
        if unicodedata.category(c) != 'Mn'
    ).lower()
    search_kw = kw_str

    MAPPED_KEYS = {
        "especialista ia": "especialista em ia",
        "engenheiro ia": "engenheiro de ia",
        "ai developer": "desenvolvedor de agentes ia",
        "operacoes fisicas": "operacoes fisicas",
        "operacoes": "operacoes fisicas",
        "industria": "industria",
        "logistica": "logistica",
        "administrativo": "administrativo",
        "criativos de performance": "criativos de performance",
        "criativos": "criativos de performance",
        "design": "design",
        "inteligencia de vendas": "inteligencia de vendas",
        "vendas": "vendas",
        "engenharia de ia/dados": "engenharia de ia dados",
        "engenharia de ia dados": "engenharia de ia dados",
        "engenharia de dados": "engenharia de dados",
    }

    try:
        import bot
        mapped_key = MAPPED_KEYS.get(kw_norm, kw_norm)
        if mapped_key in bot.CO_OCCURRENCE_RULES:
            # Usar apenas o PRIMEIRO termo do Grupo A como query ampla.
            # O Workana trata múltiplos termos como AND (matar resultados).
            # Nosso filtro local cuida da precisão depois.
            grupo_a = bot.CO_OCCURRENCE_RULES[mapped_key][0]
            search_kw = grupo_a[0]
    except Exception as e:
        print("Workana: Erro ao importar bot/rules:", e)

    if lvl_str != "Todos":
        search_kw += f" {lvl_str}"
    if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
        search_kw += f" {loc}"

    search_kw_encoded = urllib.parse.quote(search_kw)
    print(f"Workana: buscando por '{search_kw}'")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="pt-BR",
            )
            page = await context.new_page()

            if stealth_async:
                await stealth_async(page)

            effective_max_pages = min(max_pages, 5)
            for page_num in range(1, effective_max_pages + 1):
                if page_num > 1:
                    await asyncio.sleep(random.uniform(2.5, 5.0))

                url = (
                    f"https://www.workana.com/jobs"
                    f"?query={search_kw_encoded}&page={page_num}"
                )

                try:
                    response = await page.goto(
                        url, timeout=30000, wait_until="domcontentloaded"
                    )
                    if response and response.status == 429:
                        print("Workana: rate limit (429), parando.")
                        break
                except Exception as e:
                    print(f"Workana: erro ao navegar para {url}: {e}")
                    break

                # Aguardar os cards carregarem — seletor confirmado por inspeção real
                card_selector = ".project-item"
                try:
                    await page.wait_for_selector(card_selector, timeout=15000)
                except Exception:
                    print(f"Workana: sem cards na página {page_num}, encerrando.")
                    break

                cards = await page.query_selector_all(card_selector)
                if not cards:
                    break

                print(f"Workana: página {page_num} — {len(cards)} cards brutos")

                for card in cards:
                    # --- Título e Link ---
                    title_el = await card.query_selector(".project-title a")
                    if not title_el:
                        # fallback: qualquer <a> dentro do header
                        title_el = await card.query_selector(".project-header a")

                    title = ""
                    link = ""
                    if title_el:
                        title = (await title_el.inner_text()).strip()
                        href = await title_el.get_attribute("href")
                        if href:
                            link = href.strip()
                            if link.startswith("/"):
                                link = "https://www.workana.com" + link
                            elif not link.startswith("http"):
                                link = "https://www.workana.com/" + link

                    if not title:
                        continue
                    if not link:
                        link = url

                    # --- Clicar no botão 'Ver mais detalhes' se existir para expandir a descrição completa ---
                    try:
                        expand_btn = await card.query_selector("a.see-more, .expander, .js-show-more, a:has-text('Ver mais')")
                        if expand_btn:
                            await expand_btn.click(timeout=1000)
                            await asyncio.sleep(0.3)
                    except Exception:
                        pass

                    # --- Descrição Completa ---
                    desc_el = await card.query_selector(".project-details, .expander, .description, .js-project-details")
                    if desc_el:
                        req_text = desc_el.inner_text() if not asyncio.iscoroutinefunction(desc_el.inner_text) else await desc_el.inner_text()
                    else:
                        req_text = card.inner_text() if not asyncio.iscoroutinefunction(card.inner_text) else await card.inner_text()

                    if asyncio.iscoroutine(req_text):
                        req_text = await req_text
                    req_text = str(req_text).strip() if req_text else ""

                    # Limpar sufixos do botão "Ver mais detalhes", "Ver menos" e rodapés do HTML da Workana
                    for remove_term in ["Ver mais detalhes", "Ver mais", "... Ver mais detalhes", "... Ver mais", "Ver menos", "..."]:
                        if req_text.endswith(remove_term):
                            req_text = req_text[:-len(remove_term)].strip()
                    if "Ver menos" in req_text:
                        req_text = req_text.split("Ver menos")[0].strip()

                    # --- Habilidades (skills) como texto extra para o filtro ---
                    skills_el = await card.query_selector(".skills")
                    if skills_el:
                        skills_text = (await skills_el.inner_text()).strip()
                        req_text = req_text + " " + skills_text

                    job_obj = {
                        "platform": "Workana",
                        "title": title,
                        "company": "Cliente Workana",
                        "budget": "A Combinar",
                        "link": link,
                        "job_type": "PJ",
                        "profession": keyword,
                        "level": level,
                        "requirements": req_text,
                    }
                    try:
                        from bot import classify_job_profession
                        job_obj = classify_job_profession(job_obj)
                    except Exception:
                        pass
                    jobs.append(job_obj)

            await browser.close()

    except Exception as e:
        print("Workana: erro geral:", e)

    print(f"Workana: total vagas brutas coletadas: {len(jobs)}")
    return jobs
