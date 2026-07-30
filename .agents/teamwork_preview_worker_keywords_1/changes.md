# Changes Report

## Modified Files
### `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
- **Expanded `menus` dictionary**: Added more fine-grained Brazilian job market options for AI, Dev, Dados, Growth & Mkt, Audiovisual, Base, and Junior niches.
- **Cleaned `search_mapping` dictionary**: Removed all duplicate legados (compatibility) overrides so that keys map directly to clean search query keywords.
- **Module-level variables**: Added `global_title_blacklist` and `blacklist` to support clean imports and reuse.
- **Refactored `is_job_relevant`**:
  - Sequence order correction: Checked location, contract, and level, then global blacklist, then niche-specific local blacklist, then finally `rules` dictionary.
  - Regex-based word boundary validation in both blacklists.
- **Refactored `has_any`**:
  - Implemented exact word boundary matches (`\bword\b`) instead of broad substring checks.
  - Implemented prefix wildcard matching (`word*` maps to `\bword\w*`) to accurately handle word derivations (e.g. `desenvolv*` matching `desenvolvedor`).
- **Refactored `rules`**:
  - Restructured rules to use multiple logical groups acting as AND conjunctions (Group 1: Niche technical concept, Group 2: Role/Job function, e.g., requiring both `python` AND `dev*`).

## Created Files
### `C:\Users\99196\OneDrive\Documentos\vagas_bot\test_keywords.py`
- A standalone test suite that imports `is_job_relevant` and `normalize_str` from `bot.py`.
- Validates 5 approved cases (e.g., "Desenvolvedor Python" under "Backend Python") and 5 rejected cases (e.g., "Professor de Python" under "Backend Python").
- Prints clear, formatted output of all test evaluations.
