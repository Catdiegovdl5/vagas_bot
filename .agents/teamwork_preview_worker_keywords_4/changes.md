# Changes

This document lists the code changes applied to fix the niche-specific local blacklist regex boundary bug and add corresponding test coverage.

## 1. Modify `bot.py`
- **File**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
- **Location**: Line 513
- **Details**: Changed the niche-specific local blacklist regex matching pattern from space-padded (`rf' {re.escape(w)} '`) to word boundary based (`rf'\b{re.escape(w)}\b'`). This ensures terms appearing at the start/end of a title or adjacent to punctuation are correctly filtered.

## 2. Expand tests in `test_keywords.py`
- **File**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\test_keywords.py`
- **Location**: Lines 70-71 (inside `boundary_cases`)
- **Details**: Added the 10th boundary case:
  - Job Title: `"Gestor de Tráfego Aéreo"`
  - Keyword: `"Gestor de Tráfego / Performance"`
  - Expected Result: `False` (because `"aereo"` is in the niche-specific local blacklist for the `"gestor de trafego / performance"` keyword).
