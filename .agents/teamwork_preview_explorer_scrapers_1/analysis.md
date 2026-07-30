# Detailed Technical Analysis: Scraper Architecture, Category Mappings, and Refactoring Strategy

## 1. Executive Summary

This report provides a thorough analysis of the 19 active scrapers in `scrapers/` and the dispatcher/relevance filtering logic in `bot.py`. The objective is to design the architectural refactoring needed to transition from legacy tech/support job categories (`ti`, `sdr`, `adm`, `dev`, `log`) to **6 new canonical categories**:
1. **Operações Físicas**
2. **Logística**
3. **Administrativo**
4. **Criativos de Performance**
5. **Inteligência de Vendas**
6. **Engenharia de IA/Dados**

Our investigation reveals that job boards use wildly varying query parameter formats, URL slug mappings, API endpoints, and search semantics (e.g. strict `AND` matching vs broad keyword searching). Injecting raw meta-category strings like `"Operações Físicas"` into platform search queries results in zero job hits. Native title-based term sets must be dispatched to native search interfaces.

---

## 2. Inventory of Scrapers & Query Parameter Handling

Below is the complete analysis of all 19 scrapers in `scrapers/`:

| Scraper Module | Invocation Signature | Transport / Protocol | Search Parameter Formulation & URL Structure | Category / Keyword Quirks |
|---|---|---|---|---|
| `catho.py` | `async def scrape(keyword="Python", level="Todos", max_pages=10, location="", country="", **kwargs)` | Async HTTP via `curl_cffi` (impersonate chrome110) | Formats search query `search_kw` (appending level/location if non-default) and URL encodes it via `urllib.parse.quote(search_kw)`. URL: `https://www.catho.com.br/vagas/{encoded_kw}/?page={page}`. | Broad general board. Handles operational, administrative, and technical search terms well. |
| `coodesh.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTTP via `curl_cffi` | Query parameters passed via URL query string. | Tech-focused job board (Software, Data, DevOps). Irrelevant/empty for non-tech categories. |
| `freelancer.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | REST API (`requests`) | Endpoint: `https://www.freelancer.com/api/projects/0.1/projects/active/?query={encoded_kw}&limit=15`. | Freelance project board. Best suited for remote, design, writing, sales, and dev projects. |
| `geekhunter.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTML Scraping via `curl_cffi` / `BeautifulSoup` | Endpoint: `https://www.geekhunter.com/pt/vagas?q={encoded_kw}`. | Tech-focused talent platform (Developers, Data, DevOps). |
| `github_vagas.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | GitHub Search API (`requests`) | Endpoint: `https://api.github.com/search/issues?q={encoded_q}` targeting repos `frontendbr/vagas`, `backend-br/vagas`, `react-brasil/vagas`, `qa-brasil/vagas`. | Developer issue repository scraper. Fails with 0 results for non-tech roles (e.g. Operações Físicas or Admin). |
| `glassdoor.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTTP Scraping | Encodes search terms in Glassdoor search URL parameters. | Corporate job board. Requires clean job title queries. |
| `gmail.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | Google Gmail API | Searches user inbox messages for job alert emails containing `keyword`. | Searches raw email text. |
| `gupy.py` | `async def scrape(keyword="Python", level="Todos", max_pages=10, location="", country="", **kwargs)` | Public REST API (`curl_cffi` / `httpx`) | Endpoint: `https://portal.api.gupy.io/api/v1/jobs?name={encoded_kw}&limit=100&offset={offset}`. | Gupy filters by `name` substring. Works exceptionally well when supplied with exact job title keywords. |
| `indeed.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTML Scraping via `curl_cffi` | Endpoint: `https://br.indeed.com/jobs?q={encoded_kw}&l={loc_param}`. | Broad general board. High volume across all 6 categories. |
| `infojobs.py` | `async def scrape(keyword="Python", level="Todos", max_pages=10, location="", country="", **kwargs)` | Playwright Stealth + `curl_cffi` | Endpoint: `https://www.infojobs.com.br/vagas-de-emprego-{encoded_kw}.aspx`. | Leading operational and administrative job portal in BR. High sensitivity to keyword slugs. |
| `jooble.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTML Scraping via `curl_cffi` | Endpoint: `https://br.jooble.org/SearchResult?p=1&rgns={loc}&kw={encoded_kw}`. | Aggregator covering operational, administrative, sales, and tech positions. |
| `jsearch.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | RapidAPI REST API | Endpoint: `https://jsearch.p.rapidapi.com/search?query={encoded_kw}&page=1&num_pages=3`. | Aggregator API. Requires standard job title strings. |
| `linkedin.py` | `def scrape(keyword="Python", level="Todos", location="", country="", contract="Todos", **kwargs)` | Guest Job Search API / HTML via `curl_cffi` | Endpoint: `https://www.linkedin.com/jobs/search?keywords={encoded_kw}&location={target_loc}`. | Professional corporate network. Performs best with corporate, creative, sales, admin, and tech titles. |
| `meta_ads.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | Apify Actor (`facebook-ads-library-scraper`) | URL: `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BR&q={urllib.parse.quote(search_term)}`. | Searches active job recruitment ads on Facebook/Instagram. |
| `novenove.py` (99Freelas) | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTML Scraping via `requests` / `BeautifulSoup` | Endpoint: `https://www.99freelas.com.br/projects?q={encoded_kw}`. | Freelance project portal in Brazil. High density of creative, video, copywriting, sales, and dev tasks. |
| `programathor.py` | `def scrape(keyword="Python", level="Todos", location="", country="", **kwargs)` | HTML Scraping via `curl_cffi` | Endpoint: `https://programathor.com.br/jobs-{encoded_kw}`. | Niche IT/Developer job board in Brazil. |
| `remotar.py` | `def scrape(keyword="Python", level="Todos", contract="Todos", location="", country="", **kwargs)` | HTML Scraping via `curl_cffi` | Endpoint: `https://remotar.com.br/search?q={encoded_kw}`. | Remote-only job board. Best for remote administrative, sales, creative, and tech roles. |
| `vagas_com.py` | `async def scrape(keyword="Python", level="Todos", max_pages=1, location="", country="", **kwargs)` | Async HTTP via `curl_cffi` / `httpx` | Endpoint: `https://www.vagas.com.br/vagas-de-{encoded_kw}?pagina={page}`. Internal dictionary `vagas_com_mapping` maps normalized keywords to URL slugs (e.g. `"especialista em ia"` -> `"inteligencia-artificial"`). Fallback: `kw_str.replace(' ', '-')`. | Hardcoded URL slug dictionary requires explicit mapping for new category titles. |
| `workana.py` | `async def scrape(keyword="Python", level="Todos", max_pages=100, location="", country="", **kwargs)` | Playwright Async + Stealth | Endpoint: `https://www.workana.com/jobs?query={search_kw_encoded}&page={page_num}`. Uses `bot.CO_OCCURRENCE_RULES` or `MAPPED_KEYS` to pick the 1st term of Grupo A. | Workana's search engine treats space-separated words as strict `AND`. Multi-word queries often return 0 results. |

---

## 3. Dataflow of Keywords & Categories

```
[ Telegram User Button / Command ]
              │
              ▼
    [ process_mega_category / process_hunt in bot.py ]
              │
              ├─► Looks up category in MAGIC_CATEGORIES (e.g., 'adm', 'log', 'ti', 'sdr', 'dev')
              ├─► Maps user title via SEARCH_MAPPING
              │
              ▼
       [ _do_hunt(keyword, ...) ]
              │
              ├─► Checks settings["platforms"] (active scrapers)
              ├─► Formats level logic (appends level to string EXCEPT for freelance platforms)
              ├─► Calls module.scrape(**kwargs) concurrently via asyncio.gather()
              │
              ▼
   [ Scrapers execute search HTTP/API requests ]
              │
              ▼
   [ Raw Job Results returned to _do_hunt ]
              │
              ▼
  [ Local Filtering: is_job_relevant() in bot.py ]
              │
              ├─► Normalizes title & text via normalize_str()
              ├─► Checks global_title_blacklist & BLACKLIST_PROFILES
              ├─► Checks CO_OCCURRENCE_RULES (Grupo A mandatory match & Grupo B co-occurrence)
              │
              ▼
  [ Deduplicated & Saved to DB / Displayed to User ]
```

---

## 4. Platform Refactoring Strategy for 6 Canonical Categories

To ensure all scrapers seamlessly support the 6 new categories without breakage or empty responses, the following architectural updates are required:

### 4.1. Category Routing in `bot.py`
1. **Update `MAGIC_CATEGORIES`**: Replace legacy categories (`ti`, `sdr`, `adm`, `dev`, `log`) with the 6 new canonical categories:
   - `operacoes_fisicas`
   - `logistica`
   - `administrativo`
   - `criativos_performance`
   - `inteligencia_vendas`
   - `engenharia_ia_dados`
2. **Update `SEARCH_MAPPING`**: Ensure every individual term in the 6 category term sets maps to a normalized search keyword string.
3. **Update `CO_OCCURRENCE_RULES`**: Add rule definitions for all new term keywords so `is_job_relevant()` correctly validates scraped job descriptions.
4. **Update `BLACKLIST_PROFILES`**: Adjust title blacklists to prevent false positive exclusions (for instance, ensuring logistics or physical operations terms like `"ajudante de estoque"` or `"operador"` are NOT prematurely blocked by generic manual labor blacklists).

### 4.2. Scraper-Specific Adjustments
- **`vagas_com.py`**: Update `vagas_com_mapping` dictionary with URL slugs for all newly introduced terms:
  - `"operador de producao"` -> `"operador-de-producao"`
  - `"auxiliar de deposito"` -> `"auxiliar-de-deposito"`
  - `"assistente de logistica"` -> `"assistente-logistica"`
  - `"auxiliar de almoxarifado"` -> `"auxiliar-de-almoxarifado"`
  - `"editor de video"` -> `"editor-de-video"`
  - `"analista de sales ops"` -> `"analista-sales-ops"`
  - `"engenheiro de dados"` -> `"engenheiro-de-dados"`
  - etc.
- **`workana.py`**: Update `MAPPED_KEYS` and integration with `CO_OCCURRENCE_RULES` so that any search keyword from the 6 categories extracts a clean 1-word or 2-word root term from Grupo A for Workana's search bar, preventing zero-result failures caused by multi-word `AND` logic.
- **Niche/Tech-Only Scrapers (`github_vagas.py`, `programathor.py`, `geekhunter.py`, `coodesh.py`)**:
  - Add a early guard or category filter check: if the search query belongs to non-tech categories (`operacoes_fisicas`, `logistica`, `administrativo`), return `[]` immediately without executing network calls.
  - This saves execution budget, speeds up Telegram bot responsiveness, and prevents rate-limiting.

---

## 5. Native Keyword Term Sets per Category

To avoid generic bulk searches (e.g. searching `"Logística"` or `"Operações Físicas"` directly), each category will dispatch specific, platform-indexed job titles:

### 1. Operações Físicas (`operacoes_fisicas`)
- `"Operador de Produção"`
- `"Auxiliar de Operações"`
- `"Conferente"`
- `"Operador de Empilhadeira"`
- `"Auxiliar de Serviços Gerais"`
- `"Mecanico de Manutenção"`
- `"Operador de Maquinas"`

### 2. Logística (`logistica`)
- `"Assistente de Logística"`
- `"Auxiliar de Logística"`
- `"Auxiliar de Almoxarifado"`
- `"Auxiliar de Expedição"`
- `"Analista de Logística"`
- `"Controlador de Estoque"`
- `"Operador Logístico"`

### 3. Administrativo (`administrativo`)
- `"Assistente Administrativo"`
- `"Auxiliar Administrativo"`
- `"Assistente Financeiro"`
- `"Assistente de Faturamento"`
- `"Recepcionista"`
- `"Analista Administrativo"`
- `"Auxiliar de Escritório"`
- `"Data Entry"`

### 4. Criativos de Performance (`criativos_performance`)
- `"Editor de Vídeo"`
- `"Motion Designer"`
- `"Designer Gráfico"`
- `"Copywriter"`
- `"Video Maker"`
- `"Gestor de Tráfego"`
- `"Criador de Conteúdo"`
- `"Social Media"`

### 5. Inteligência de Vendas (`inteligencia_vendas`)
- `"SDR"`
- `"BDR"`
- `"Inside Sales"`
- `"Analista de Sales Ops"`
- `"Analista de CRM"`
- `"Executivo de Vendas"`
- `"Analista de Inteligência de Mercado"`
- `"Growth Hacker"`

### 6. Engenharia de IA/Dados (`engenharia_ia_dados`)
- `"Engenheiro de IA"`
- `"Engenheiro de Dados"`
- `"Cientista de Dados"`
- `"Analista de Dados"`
- `"Analista de Power BI"`
- `"Desenvolvedor de Agentes IA"`
- `"Prompt Engineer"`
- `"Machine Learning Engineer"`
- `"Desenvolvedor Python"`
