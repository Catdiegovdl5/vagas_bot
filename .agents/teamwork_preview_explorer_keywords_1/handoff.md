# Handoff Report: Keyword Expansion and False Positive/Relevance Logic Refinement

This report analyzes the keyword search mapping, rules, and blacklist logic inside `bot.py` and proposes concrete expansions and bug fixes for the Brazilian job market.

---

## 1. Observation

During the read-only investigation, the following structural anomalies and bugs were observed in `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`:

### Observation A: Overwritten Keys in `search_mapping` (Lines 654-733)
The `search_mapping` dictionary contains duplicate keys, where the "LEGADOS (compatibilidade)" section at the end of the dictionary overwrites previous definitions. In Python, the last defined key in a dictionary literal overrides all previous ones.
* **Line 662 vs Line 702**: 
  ```python
  662:         "Python Scraping & Data Engineering": "Python Scraping",
  ...
  702:         "Python Scraping & Data Engineering": "Python",
  ```
  *Result*: The mapping resolves to `"Python"`, causing the scraper to execute a very broad search query, yielding massive irrelevant results.
* **Line 657 vs Line 699**: 
  ```python
  657:         "AI Coder / AI Agent Developer": "chatbot ia",
  ...
  699:         "AI Coder / AI Agent Developer": "Inteligência Artificial",
  ```
  *Result*: The mapping resolves to `"Inteligência Artificial"`, discarding the targeted `"chatbot ia"` search.
* **Line 670 vs Line 716**:
  ```python
  670:         "Analista de Dados / Data Scientist": "Analista Dados",
  ...
  716:         "Analista de Dados": "Dados",
  ```
  *Result*: The key `"Analista de Dados / Data Scientist"` is overridden by the legacy key `"Analista de Dados"` (which does not match the active menu key exactly, but is listed in legados as mapping to `"Dados"`).
* **Line 696 vs Line 728**: `"AI Coder Júnior"` maps to `"Inteligência Artificial"` instead of `"IA Developer Junior"`.
* **Line 697 vs Line 729**: `"Engenheiro de Prompt Jr"` maps to `"Inteligência Artificial"` instead of `"Prompt Engineer Junior"`.

### Observation B: Inactive Blacklist due to Key Mismatches & Normalization (Lines 417-441)
The `blacklist` dictionary in `is_job_relevant` has key mismatches with the active menu keys and fails due to accent normalization:
* **Key Mismatch**: 
  The menu keyword is `"Analista de Dados / Data Scientist"`. The blacklist key is `"analista de dados"`.
  The menu keyword is `"AI Coder / AI Agent Developer"`. The blacklist key is `"ai coder"`.
  The menu keyword is `"Gestor de Tráfego / Performance"`. The blacklist key is `"gestor de trafego"`.
  Because `kw_norm` (the lowercase normalized selected keyword) does not match the blacklist keys exactly, **these blacklist filters are never evaluated**.
* **Normalization Mismatch**:
  The blacklist key `"recepção / portaria"` contains accents. `kw_norm` for `"Recepção / Portaria"` is normalized via `normalize_str` which removes accents, resulting in `"recepcao / portaria"`. 
  Because `"recepcao / portaria" != "recepção / portaria"`, this blacklist filter is **never evaluated**.

### Observation C: Substring Matching and Lack of Word Boundaries in `has_any` (Lines 450-458)
The auxiliary function `has_any(words)` only uses regex word boundaries `\b` for a select list of short acronyms:
```python
450:     def has_any(words):
451:         for w in words:
452:             if w in ['ia', 'bi', 'jr', 'ai', 'ads', 'ux', 'ui']:
453:                 if re.search(rf'\b{w}\b', title_norm):
454:                     return True
455:             else:
456:                 if w in title_norm:
457:                     return True
458:         Return False
```
*Result*: For general terms like `"dev"`, `"back"`, `"mkt"`, `"data"`, it performs a simple substring check (`w in title_norm`). This matches:
* `"dev"` inside `"devolução"` (e.g., `"Auxiliar de Recebimento e Devolução"`).
* `"dev"` inside `"device"`.
* `"back"` inside `"feedback"`.
This leads to massive false positives.

### Observation D: Flat / Single-Group Rules in `rules` (Lines 508-510, 520-522, 526-528)
Some rule groups in `rules` consist of a single flat list of terms. Since `is_job_relevant` returns `True` if any term is found, a single match is sufficient:
* **"Python Scraping & Data Engineering"** matches any title containing `"python"`. This allows `"Professor de Python"` to match because `"python"` is in the list, even if the job has nothing to do with scraping/data engineering.
* **"Analista de Dados / Data Scientist"** matches any title containing `"dados"` or `"data"`. This allows `"Digitador de Banco de Dados"` to match because `"dados"` is in the list.

---

## 2. Logic Chain

1. **Incorrect Scraper Queries**: Due to duplicate keys in `search_mapping` (Observation A), the bot initiates searches with broad terms like `"Python"`, `"Inteligência Artificial"`, or `"Dados"`.
2. **Inundated Raw Job Lists**: These broad searches return general, low-relevance jobs (e.g., general Python developers, AI marketing copywriters, data entry typists, academic teachers, legal/pedagogy interns).
3. **Bypassed Blacklists**: When these jobs are checked for relevance, the specific blacklist rules that should filter them out (e.g., rejecting `"suporte"` for `"analista de dados"`, or `"limpeza"` for `"auxiliar administrativo"`) are bypassed because of key mismatches and character normalization issues (Observation B).
4. **Weak Relevance Checks**: The rules fail to filter the remaining jobs because:
   * Flat rules only require a single match (e.g., just matching `"python"` matches `"Professor de Python"`) (Observation D).
   * Substring matching checks without word boundaries match short words like `"dev"` in unrelated terms like `"devolução"` (Observation C).
5. **High False Positive Rate**: Consequently, highly irrelevant jobs (such as teaching, legal, heavy manual labor, and out-of-niche support roles) are successfully validated as relevant and saved to the database.

---

## 3. Caveats

* This investigation was performed in **read-only mode**. No files outside `.agents/` were modified.
* Scraper APIs and platforms may have variable search limits or behavior when querying multi-word phrases.
* The analysis assumes that Brazilian tech, marketing, and office job markets align with standard Portuguese terminology (e.g., using "Estágio", "Auxiliar", "Desenvolvedor").

---

## 4. Conclusion & Actionable Proposals

To solve these issues, the implementation agent must perform the following refactorings:

### Action 1: Re-structure the Niches & Expand Keywords
Expand the `menus` dictionary in `bot.py` to support highly relevant Brazilian market niches.

**Proposed `menus` definition:**
```python
    menus = {
        "ai": [
            "Especialista em IA", 
            "Especialista em IA Generativa", 
            "AI Coder / AI Agent Developer", 
            "Engenheiro de Prompt / RAG Specialist", 
            "Consultor de IA",
            "Engenheiro de Machine Learning / MLOps",
            "Product Manager de IA / Conversational PO"
        ],
        "dev": [
            "Python Scraping & Data Engineering", 
            "Integração de APIs & Serverless", 
            "Backend Python",
            "Desenvolvedor Frontend React",
            "Desenvolvedor Fullstack Node/React",
            "Desenvolvedor FastAPI / Django (Backend)",
            "Engenheiro de Software Python"
        ],
        "dados": [
            "Analista de BI / Analytics", 
            "Automação RPA & Workflow", 
            "Analista de Dados / Data Scientist",
            "Engenheiro de Dados (Data Engineer)",
            "Analytics Engineer",
            "Analista de Power BI"
        ],
        "mkt": [
            "Growth Engineer / Product Growth", 
            "Especialista Tracking & MarTech", 
            "Analista RevOps", 
            "SDR / BDR Técnico", 
            "Gestor de Tráfego / Performance",
            "Copywriter de Conversão",
            "Gestor de Inbound Marketing / CRM",
            "Analista de SEO & Tráfego Orgânico"
        ],
        "audio": [
            "Editor de Vídeo / Motion Designer", 
            "Video Maker / Filmmaker", 
            "Design e Social Media",
            "Designer UX/UI",
            "Editor de Vídeo para Redes Sociais",
            "Designer Gráfico / Visual Designer"
        ],
        "base": [
            "Auxiliar Administrativo", 
            "Recepção / Portaria", 
            "Assistente de Suporte Administrativo", 
            "Suporte Técnico N1 / Service Desk", 
            "SDR Técnico", 
            "Auxiliar Administrativo / Faturamento", 
            "Auxiliar de Operações / Logística",
            "Assistente Financeiro",
            "Operador de Telemarketing / SAC",
            "Auxiliar de Logística / Estoque",
            "Assistente de DP / Recursos Humanos"
        ],
        "junior": [
            "Desenvolvedor Júnior / Estagiário", 
            "Analista de Dados Jr", 
            "Assistente de Marketing", 
            "Assistente de Growth", 
            "SDR / Vendas Junior", 
            "Editor de Vídeo Júnior", 
            "AI Coder Júnior", 
            "Engenheiro de Prompt Jr",
            "Estagiário de TI / Programação",
            "Desenvolvedor Frontend Júnior",
            "Estagiário de Dados / BI",
            "Designer Júnior"
        ]
    }
```

### Action 2: Fix and Clean `search_mapping` (No duplicates)
Re-define `search_mapping` using clean, explicit mappings without duplicate overrides.

**Proposed `search_mapping` definition:**
```python
    search_mapping = {
        # --- IA ---
        "Especialista em IA": "Inteligência Artificial",
        "Especialista em IA Generativa": "IA Generativa",
        "AI Coder / AI Agent Developer": "AI Developer",
        "Engenheiro de Prompt / RAG Specialist": "Prompt Engineer",
        "Consultor de IA": "Consultor IA",
        "Engenheiro de Machine Learning / MLOps": "Machine Learning MLOps",
        "Product Manager de IA / Conversational PO": "Product Manager IA",
        
        # --- DEV ---
        "Python Scraping & Data Engineering": "Python Scraping",
        "Integração de APIs & Serverless": "API Backend",
        "Backend Python": "Python Backend",
        "Desenvolvedor Frontend React": "Frontend React",
        "Desenvolvedor Fullstack Node/React": "Fullstack React Node",
        "Desenvolvedor FastAPI / Django (Backend)": "FastAPI Django",
        "Engenheiro de Software Python": "Python Developer",
        
        # --- DADOS ---
        "Analista de BI / Analytics": "Analista BI",
        "Automação RPA & Workflow": "RPA Automação",
        "Analista de Dados / Data Scientist": "Analista de Dados",
        "Engenheiro de Dados (Data Engineer)": "Engenheiro de Dados",
        "Analytics Engineer": "Analytics Engineer",
        "Analista de Power BI": "Power BI",
        
        # --- GROWTH & MKT ---
        "Growth Engineer / Product Growth": "Growth Engineer",
        "Especialista Tracking & MarTech": "Web Analytics",
        "Analista RevOps": "RevOps",
        "SDR / BDR Técnico": "SDR",
        "Gestor de Tráfego / Performance": "Tráfego Pago",
        "Copywriter de Conversão": "Copywriter",
        "Gestor de Inbound Marketing / CRM": "Inbound Marketing CRM",
        "Analista de SEO & Tráfego Orgânico": "Analista SEO",
        
        # --- AUDIOVISUAL ---
        "Editor de Vídeo / Motion Designer": "Editor de Vídeo",
        "Video Maker / Filmmaker": "Video Maker",
        "Design e Social Media": "Social Media Designer",
        "Designer UX/UI": "UI UX Designer",
        "Editor de Vídeo para Redes Sociais": "Editor Reels TikTok",
        "Designer Gráfico / Visual Designer": "Designer Gráfico",
        
        # --- BASE ---
        "Auxiliar Administrativo": "Auxiliar Administrativo",
        "Recepção / Portaria": "Portaria Recepcionista",
        "Assistente de Suporte Administrativo": "Assistente Administrativo",
        "Suporte Técnico N1 / Service Desk": "Suporte TI Helpdesk",
        "SDR Técnico": "SDR Técnico",
        "Auxiliar Administrativo / Faturamento": "Faturamento",
        "Auxiliar de Operações / Logística": "Auxiliar Logística",
        "Assistente Financeiro": "Assistente Financeiro",
        "Operador de Telemarketing / SAC": "Telemarketing SAC",
        "Auxiliar de Logística / Estoque": "Auxiliar de Estoque",
        "Assistente de DP / Recursos Humanos": "Assistente DP RH",
        
        # --- JUNIOR ---
        "Desenvolvedor Júnior / Estagiário": "Desenvolvedor Junior",
        "Analista de Dados Jr": "Analista de Dados Junior",
        "Assistente de Marketing": "Marketing Junior",
        "Assistente de Growth": "Growth Junior",
        "SDR / Vendas Junior": "SDR Junior",
        "Editor de Vídeo Júnior": "Editor de Vídeo Junior",
        "AI Coder Júnior": "AI Developer Junior",
        "Engenheiro de Prompt Jr": "Prompt Engineer Junior",
        "Estagiário de TI / Programação": "Estágio TI Programação",
        "Desenvolvedor Frontend Júnior": "Frontend Junior",
        "Estagiário de Dados / BI": "Estágio Dados BI",
        "Designer Júnior": "Designer Junior"
    }
```

### Action 3: Refine False Positive Matching with Exact Word Boundaries & Prefix Wildcards
Refactor `has_any` inside `is_job_relevant` to support exact word boundaries and wildcard matching (using `*` for prefixes, e.g., `"desenvolv*"` to match `"desenvolvedor"`, `"desenvolvimento"`).

```python
    def has_any(words):
        for w in words:
            if w.endswith('*'):
                # Prefix matching using word boundaries for the prefix root
                pattern = rf'\b{w[:-1]}\w*'
                if re.search(pattern, title_norm):
                    return True
            else:
                # Exact word matching using boundaries
                if re.search(rf'\b{w}\b', title_norm):
                    return True
        return False
```

### Action 4: Define a Global Blacklist & Precise Keyword Blacklists
To block irrelevant industries (academic, healthcare, legal, heavy manual labor) globally, and refine key-matching:

1. **Global Blacklist (Applied to all jobs except matching menu terms):**
   ```python
   global_title_blacklist = [
       # Acadêmico / Ensino
       "professor", "professora", "docente", "tutor", "tutoria", "instrutor", "instrutora", "palestrante", 
       "academic", "academico", "lecturer", "lecionar", "ensinar", "aulas",
       # Jurídico / Legal
       "advogado", "advogada", "direito", "juridico", "paralegal", "promotor de justica",
       # Saúde / Médico
       "medico", "medica", "enfermeiro", "enfermeira", "enfermagem", "dentista", "farmaceutico", 
       "fisioterapeuta", "nutricionista", "veterinario", "psicologo", "psicologa", "psiquiatra", "biomedico",
       # Trabalho Braçal / Manutenção Física / Limpeza (geral)
       "faxineiro", "faxineira", "diarista", "domestica", "passadeira", "cozinheiro", "cozinheira", 
       "garcom", "garconete", "copa", "servente", "pedreiro", "pintor", "carpinteiro", "frentista", 
       "mecanico", "lavador", "ajudante de obras", "servicos gerais",
       # Outros
       "voluntario", "voluntary"
   ]
   ```

2. **Corrected and Expanded Niche-Specific Blacklist (keys are lowercase, accent-free normalized strings matching the menus):**
   ```python
   blacklist = {
       "gestor de trafego / performance": ["aereo", "logistica", "transporte", "rodoviario", "carga", "frota", "veiculos", "patio", "controlador"],
       "especialista em ia": ["vendas", "comercial", "atendimento", "conteudo", "social media", "criacao", "redator", "copywriter", "marketing", "video", "imagem"],
       "especialista em ia generativa": [
           "mlops", "machine learning engineer", "redes neurais", "data scientist", "engenheiro de dados",
           "rpa", "automacao", "uipath", "zapier", "n8n", "make.com",
           "backend", "desenvolvedor", "dev", "programador", "software engineer",
           "data engineer", "cloud", "devops", "kubernetes", "docker",
           "suporte", "infraestrutura", "helpdesk", "sysadmin"
       ],
       "ai coder / ai agent developer": ["vendas", "comercial", "conteudo", "social media"],
       "analista de dados / data scientist": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador"],
       "python scraping & data engineering": ["professor", "tutor", "instrutor", "curso", "vendas", "comercial"],
       "auxiliar administrativo": ["producao", "limpeza", "carga", "descarga", "pesado", "operario", "servente", "cozinha", "estoque", "repositor", "caixa", "atendente", "vendas"],
       "recepcao / portaria": ["limpeza", "zelador", "carga", "descarga", "vigilante armado", "seguranca armada"],
       "suporte tecnico n1 / service desk": ["eletricista", "mecanico", "manutencao predial", "refrigeracao", "ar condicionado", "telemarketing", "vendas"],
       "desenvolvedor junior / estagiario": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza"],
       "sdr / vendas junior": ["loja", "balcao", "caixa", "repositor", "estoque", "limpeza", "farmacia", "supermercado", "promotor", "panfleteiro", "corretor"]
   }
   ```

3. **Relevance Logic Implementation inside `is_job_relevant`:**
   ```python
   # 1. Global Title Blacklist check (excluding terms in user search keyword)
   active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm]
   if any(re.search(rf'\b{term}\b', title_norm) for term in active_global_blacklist):
       return False
       
   # 2. Local Niche-specific Blacklist check
   if kw_norm in blacklist:
       if any(re.search(rf'\b{w}\b', title_norm) for w in blacklist[kw_norm]):
           return False
   ```

### Action 5: Refine `rules` (Logic AND Grouping)
Ensure rules are partitioned into Group 1 (Niche concept) AND Group 2 (Role validation) to enforce that both the technical topic AND the engineering/analyst/support function are present, avoiding single-keyword matches.

**Example refined rule for Python Scraping & Data Engineering:**
```python
        "python scraping & data engineering": [
            # Group 1: Technical concepts
            ["python", "scraping", "crawler", "beautifulsoup", "selenium", "scrapy", "puppeteer", "playwright", "etl", "pipeline", "extracao"],
            # Group 2: Roles (Ensures it is an engineering/development job, not teaching/writing)
            ["desenvolv*", "dev*", "program*", "engineer*", "engenheir*", "analis*", "specialis*", "especialista"]
        ],
```

---

## 5. Verification Method

To verify these changes:
1. **Create `test_keywords.py`**:
   Write a lightweight test script that simulates `is_job_relevant()` with a battery of test cases (e.g., checking if `"Professor de Python"` is rejected for `"Backend Python"`, or if `"Estagiário de Direito"` is rejected for `"Desenvolvedor Júnior / Estagiário"`).
2. **Execute Python Syntax Check**:
   ```bash
   python -m py_compile bot.py
   ```
3. **Execute Test Suite**:
   Run the full project test suite using:
   ```bash
   python run_tests.py
   ```
   Or run the relevant tests directly:
   ```bash
   pytest tests/
   ```

---

## 6. Remaining Work (Handoff concrete next steps)

The next agent (implementer) should:
1. Implement the expanded `menus` and clean up duplicate/legacy keys in `search_mapping`.
2. Add `global_title_blacklist` and update the `blacklist` dictionary keys to match normalized menu options.
3. Update the `is_job_relevant` filtering logic with the global blacklist search, corrected local blacklist check, and regex boundary/wildcard logic in `has_any`.
4. Refine rule groups in `rules` to use AND-conjunction arrays where necessary (especially for scraping and analytics).
5. Create `test_keywords.py` validating that the false positives (Professor, Law internship, Cleaners) are successfully blocked and valid positions are allowed.
6. Verify python syntax and run tests.
