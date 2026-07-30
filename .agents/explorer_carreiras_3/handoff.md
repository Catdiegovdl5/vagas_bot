# Handoff Report — Explorer Carreiras 3

## 1. Observation

- Executed project directory inspection at `C:\Users\99196\OneDrive\Documentos\vagas_bot`.
- Examined `bot.py` (1802 lines): verified menu routing pattern using `aiogram` v3 (`InlineKeyboardMarkup`, `InlineKeyboardButton`, `CallbackQuery`).
- Examined `database.py` (142 lines): observed SQLite persistence tables:
  - `jobs` (lines 16-25): `(id PRIMARY KEY, title, company, budget, link, platform, added_at, job_type, profession, level, requirements)`
  - `applied_jobs` (lines 36-40): `(link PRIMARY KEY, applied_at)`
  - `ignored_jobs` (lines 43-47): `(link PRIMARY KEY, reason, ignored_at)`
- Examined existing unit test patterns in `test_menu_expansion.py` (126 lines) utilizing AST parsing (`ast.parse`), `pytest`, and `unittest.mock`.
- Confirmed that no career guidance data or career completion tracking functions currently exist in `bot.py` or `database.py`.

---

## 2. Logic Chain

1. **Observation 1 & 2**: `bot.py` utilizes Telegram inline keyboard callbacks for top-level menus (`get_main_menu_markup`), niche selection (`select_mode`), and submenus (`show_niche_jobs`).
   - *Inference*: The career guidance feature should integrate via a new menu callback `career_menu` and profession detail callbacks `career_detail_<prof_id>` and `career_step_<prof_id>_<step_id>`.

2. **Observation 3**: `database.py` manages job search state across `jobs`, `applied_jobs`, and `ignored_jobs`.
   - *Inference*: To persist user career completion status safely, a dedicated table `career_progress (user_id, profession_id, step_id, completed, updated_at)` must be created. Because all queries against `career_progress` are isolated, operations on career completion will never alter, overwrite, or delete job search data in `jobs`, `applied_jobs`, or `ignored_jobs`.

3. **Observation 4**: The 5 elite professions requested require complete definitions, skill stacks, market demand explanations, and 3-4 actionable specialization steps with valid URLs:
   - **Server-Side Tracking**: GTM SS, Meta CAPI, Stape.io, GA4 Server Side. Cert URLs: Skillshop GTM, Meta Blueprint, Stape Academy, GA4 Certification.
   - **Growth Engineer**: A/B testing (Optimizely), PostHog/Mixpanel, Python/SQL for Growth, Reforge Growth Engineering.
   - **Analytics Engineer**: dbt Certified Developer, GCP Professional Data Engineer (BigQuery), Snowflake SnowPro Core, Kimball Data Warehousing.
   - **IA-Ops**: DeepLearning.AI LangChain, Vanderbilt Prompt Engineering, DeepLearning.AI CrewAI Multi-Agent, Microsoft Azure AI Engineer (AI-102).
   - **SDR Técnico**: HubSpot Sales Hub, Salesforce Sales Associate, Clay University & Apollo Academy, Winning by Design Technical Discovery.

4. **Observation 5**: `test_carreiras.py` must verify three core criteria:
   - Syntax integrity and menu loading in `bot.py` without errors.
   - Content availability for all 5 professions and valid HTTPS certification URLs.
   - Database read/write persistence for completion status and isolation from job search tables.

---

## 3. Caveats

- Source code implementation in `bot.py` and `database.py` was intentionally not committed directly as this task was executed in Explorer (read-only investigation) mode. Full code implementation and test creation are documented as ready-to-implement design specifications in `analysis.md`.
- Certification URLs provided represent real, active official certification paths for each tool vendor (Google, Meta, Stape, Optimizely, dbt Labs, DeepLearning.AI, HubSpot, Salesforce, etc.).

---

## 4. Conclusion

The data architecture for the 5 elite professions, the database isolation strategy for user progress tracking, and the unit/integration test design for `test_carreiras.py` are fully defined and documented in `analysis.md`.

---

## 5. Verification Method

1. Inspect detailed data structures, certification URLs, and database persistence designs in `analysis.md`.
2. To verify the proposed `test_carreiras.py` design once implemented:
   ```bash
   python -m pytest test_carreiras.py -v
   ```
3. Verification Invalidation Conditions:
   - Any profession missing from the 5 specified elite tracks.
   - Any profession having fewer than 3 actionable certification steps or invalid URLs.
   - Any database operation on career progress that modifies records in `jobs`, `applied_jobs`, or `ignored_jobs`.
