# Context - AI Creative Job Filtering

## Files and Lines of Interest
- **`C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`**:
  - `rules` dict in `is_job_relevant` (lines 419-525). Specifically, the entry `"especialista em ia generativa"` at lines 424-427.
- **`C:/Users/99196/OneDrive/Documentos/vagas_bot/scrapers/ai_filter.py`**:
  - `score_job_match` function (lines 43-108). Specifically, prompt line 77 containing the "Regra de Ouro IA" (Rule 8).

## Planned Changes
1. Modify `bot.py` `"especialista em ia generativa"` rule:
   - Expand the list of creative/content terms (group 2) to include marketing, traffic, ads, copywriter, redator, video/audio-maker, and other creative/marketing terms.
2. Modify `scrapers/ai_filter.py` "Regra de Ouro IA":
   - Update prompt instruction to allow performance marketing and content creation jobs that explicitly integrate generative AI tools.
3. Add a verification script `verify_ai_creative_jobs.py` in the project root.
