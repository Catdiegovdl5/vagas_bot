# Handoff Report - explorer_m1

This report analyzes how job eligibility is determined in `vagas_bot` and details a strategy to support creative/marketing jobs that utilize AI (ChatGPT, Midjourney, Claude, etc.) without directly editing the code.

---

## 1. Observation

### A. Bot Menu Niches and Professions
In `C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`, the user-facing job categories and professions are defined in the `menus` dictionary inside the `show_niche_jobs` function (lines 302-309):
```python
302:     menus = {
303:         "ai": ["Especialista em IA", "Especialista em IA Generativa", "AI Coder / AI Agent Developer", "Engenheiro de Prompt / RAG Specialist", "Consultor de IA"],
304:         "dev": ["Python Scraping & Data Engineering", "Integração de APIs & Serverless", "Backend Python"],
305:         "dados": ["Analista de BI / Analytics", "Automação RPA & Workflow", "Analista de Dados / Data Scientist"],
306:         "mkt": ["Growth Engineer / Product Growth", "Especialista Tracking & MarTech", "Analista RevOps", "SDR / BDR Técnico", "Gestor de Tráfego / Performance"],
307:         "junior": ["Desenvolvedor Júnior / Estagiário", "Analista de Dados Jr", "Assistente de Marketing", "Assistente de Growth", "SDR / Vendas Junior", "Editor de Vídeo Júnior", "AI Coder Júnior", "Engenheiro de Prompt Jr"],
308:         "audio": ["Editor de Vídeo / Motion Designer", "Video Maker / Filmmaker", "Design e Social Media"]
309:     }
```

### B. Search Keyword Mapping
When the user triggers a search, the selected option is mapped to a search term queried against the platform scrapers. This mapping is defined in the `search_mapping` dictionary in `bot.py` (lines 587-624):
```python
587:     search_mapping = {
588:         "Especialista em IA Generativa": "Inteligência Artificial",
...
612:         "Gestor de Tráfego": "Tráfego Pago",
...
623:         "Design e Social Media": "Social Media"
624:     }
```

### C. Local Relevance Rules
Job relevance is checked locally inside `is_job_relevant(job, keyword, settings)` in `bot.py` (lines 347-535). Inside this function, specific keyword rules are evaluated via the `rules` dictionary (lines 419-525):
```python
419:     rules = {
420:         # === IA E MACHINE LEARNING ===
...
424:         "especialista em ia generativa": [
425:             ["ia", "ai", "artificial", "chatgpt", "midjourney", "generativa", "prompt", "dall-e", "stable diffusion", "llm", "claude", "gemini", "sora", "deepseek", "flux", "genai", "gpt", "anthropic"], 
426:             ["imagem", "video", "audiovisual", "criacao", "design", "arte", "conteudo", "generativa", "multimodal", "synthetic", "avatar", "texto", "copy", "redacao", "solucoes"]
427:         ],
...
```
The rule structure expects a list of list groups: `all(has_any(group) for group in groups)`. The job must contain at least one term from each inner list in its title.

### D. AI Filter "Regra de Ouro IA" (Rule of Gold)
In `C:/Users/99196/OneDrive/Documentos/vagas_bot/scrapers/ai_filter.py`, the LLM prompt evaluates the job description under strict guidelines. The eighth rule ("Regra de Ouro IA") in `score_job_match` (line 77) dictates:
```python
77: 8. Regra de Ouro IA: Se a busca ({target_keyword}) for relacionada a Inteligência Artificial (ex: "Especialista em IA", "AI Coder", "Engenheiro de Prompt", "Consultor de IA"), a vaga DEVE ser OBRIGATORIAMENTE técnica (Desenvolvimento, Engenharia de Dados, Python, LLMs, Machine Learning) OU de Criação de Conteúdo Avançada exigindo explicitamente ferramentas de IA (Midjourney, Runway, Stable Diffusion, IA para vídeo/áudio/imagem). REPROVE SUMARIAMENTE vagas de Marketing de Performance (Google Ads, Meta Ads) e Chatbots simples (ManyChat). Se for "Criação de Conteúdo", SÓ APROVE se citar o uso direto de Inteligência Artificial generativa, senão REPROVE (vaga_corresponde_ao_cargo=false, aprovado=false).
```

---

## 2. Logic Chain

1. **Menu Triggering & Search**: If a user selects an option such as `"Design e Social Media"` or `"Gestor de Tráfego / Performance"`, the bot initiates a search using `"Social Media"` or `"Tráfego Pago"` as the query for the scrapers (based on `search_mapping`).
2. **Local Relevance Evaluation**:
   - For a general creative/marketing search (e.g. `"Design e Social Media"`), the local rule `rules["design e social media"]` checks if the title contains terms like `["design", "designer", "social media", "arte", ...]` (lines 487-489). Since it only requires one of these terms to pass, any job titled `"Designer de Social Media com IA (ChatGPT/Midjourney)"` will pass this stage.
   - However, if the user performs a search targeting AI (e.g., `"Especialista em IA Generativa"`), the rule requires at least one term from the AI/LLM tools list (Group 1) AND at least one term from the Content/Design list (Group 2) (lines 424-427).
   - If a performance marketing job utilizing AI (e.g. `"Gestor de Tráfego com IA"`) is scraped during an AI-related search, it will be **rejected** by `is_job_relevant` because `"Gestor de Tráfego"` does not match any of the creative content keywords defined in Group 2 of `"especialista em ia generativa"` rules.
3. **AI Filter Rejection**:
   - If the AI filter (Groq LLM) is triggered (specifically for freelance jobs or when `settings["ai_filter"]` is checked), the prompt instructions in `scrapers/ai_filter.py` under the "Regra de Ouro IA" (Rule 8) will **summarily reject** performance marketing jobs (`REPROVE SUMARIAMENTE vagas de Marketing de Performance (Google Ads, Meta Ads)`).
   - Additionally, creative copy/content jobs are only approved if they explicitly require generative AI tools.
4. **Strategy for Supporting AI Creative/Mkt Jobs**:
   - To properly support and surface these jobs, we must introduce dedicated menu categories, search queries, local matching groups (combining creative/marketing terms with AI terms), and adjust the Groq prompt rule so that performance marketing jobs utilizing AI are not summarily rejected.

---

## 3. Caveats

- **Scraper Limits**: Scrapers themselves perform generic platform searches. If the API queries are too specific (e.g., `"Design IA"`), they might return very few raw jobs. The search terms must balance precision and recall.
- **AI Filtering Overhead**: The Groq evaluation is only run automatically for freelance platforms (Workana, 99Freelas, Freelancer) in the default setup, unless the user changes it. For standard corporate jobs, the heuristic filter in `bot.py` is the primary gatekeeper.

---

## 4. Conclusion & Recommendations

To configure the bot to accept and search for creative/marketing jobs that utilize AI (ChatGPT, Midjourney, Claude, etc.), apply the following non-intrusive modifications:

### Step 1: Add User-Facing Menu Options in `bot.py`
Add options for AI-assisted creative/marketing roles in `menus` (lines 302-309):
- Add `"Design e Social Media com IA"` under `"audio"` or `"ai"`.
- Add `"Gestor de Tráfego com IA"` under `"mkt"` or `"ai"`.
- Add `"Especialista em IA (Criação & Marketing)"` under `"ai"`.

### Step 2: Configure API Search Queries in `bot.py`
In `search_mapping` (lines 587-624), map the new options to broad but relevant queries to feed the scrapers:
```python
"Design e Social Media com IA": "Design Inteligência Artificial",
"Gestor de Tráfego com IA": "Tráfego Pago IA",
"Especialista em IA (Criação & Marketing)": "Marketing Inteligência Artificial"
```

### Step 3: Add Local Match Heuristics in `bot.py`
Define matching rules in the `rules` dictionary (lines 419-525) to require both the core professional domain term and at least one generative AI term:
```python
"design e social media com ia": [
    ["design", "designer", "social media", "arte", "criacao", "grafico", "figma", "photoshop", "illustrator"],
    ["ia", "ai", "chatgpt", "midjourney", "generativa", "dall-e", "stable diffusion", "claude", "gemini", "flux", "inteligencia artificial"]
],
"gestor de trafego com ia": [
    ["trafego", "ads", "performance", "midia", "media", "paid media", "meta ads", "google ads", "tiktok ads"],
    ["ia", "ai", "chatgpt", "generativa", "llm", "claude", "gemini", "gpt", "inteligencia artificial"]
],
"especialista em ia (criacao & marketing)": [
    ["ia", "ai", "artificial", "chatgpt", "midjourney", "generativa", "prompt", "dall-e", "stable diffusion", "llm", "claude", "gemini", "sora", "deepseek", "flux", "genai", "gpt", "anthropic"],
    ["imagem", "video", "audiovisual", "criacao", "design", "arte", "conteudo", "generativa", "copy", "redacao", "solucoes", "marketing", "trafego", "ads", "performance", "midia", "media"]
]
```

### Step 4: Relax AI Filter Constraints in `scrapers/ai_filter.py`
Rewrite Rule 8 ("Regra de Ouro IA") in `scrapers/ai_filter.py` (line 77) to permit performance marketing and content creation jobs that explicitly integrate generative AI tools:
- **Change from**:
  `REPROVE SUMARIAMENTE vagas de Marketing de Performance (Google Ads, Meta Ads) e Chatbots simples (ManyChat).`
- **Change to**:
  `SÓ REPROVE vagas de Marketing de Performance (Google Ads, Meta Ads) e Chatbots se elas NÃO exigirem ou fizerem uso direto de ferramentas de Inteligência Artificial generativa (como ChatGPT, Claude, Midjourney, etc.) para automação, copy ou geração de criativos.`

---

## 5. Verification Method

To verify these changes after implementation:
1. **Mock Test Cases**:
   Add test jobs to `tests/sanity_battery.json` mimicking creative/marketing AI positions. E.g.:
   - Title: `"Gestor de Tráfego com IA (ChatGPT & Claude)"`, Requirements: `"Criar campanhas no Meta Ads utilizando ChatGPT para copies."`
   - Title: `"Designer Gráfico & Midjourney Specialist"`, Requirements: `"Geração de artes e mockups utilizando Midjourney."`
2. **Execute Pytest Suite**:
   Run the test runner to ensure no regressions are introduced and that the new mock jobs pass successfully:
   ```powershell
   python run_tests.py
   ```
3. **Manual Bot Verification**:
   Trigger a search inside the Telegram bot using the newly added options (e.g. `/start` -> `Caçar Vagas` -> Select Niche -> Select AI Option) and verify that the scraper statuses update and output relevant listings.
