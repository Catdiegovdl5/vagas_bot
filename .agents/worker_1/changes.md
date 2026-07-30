# Changes Report - Iniciantes Tudo Filter Implementation

## Overview
Implemented the unified seniority filter 'Iniciantes Tudo' (combining 'Jovem Aprendiz' and 'Ganhar Experiência') across the UI (`static/index.html`), Backend (`bot.py`), and test harness (`test_iniciantes.py`).

## File Modifications

### 1. `static/index.html`
- **Location**: Radio container inside `#screen-settings` (Orquestração / Nível de Senioridade).
- **Modification**: Added radio input option:
  `<label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="iniciantes tudo"> Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)</label>`
- **Rationale**: Allows users in the web GUI to select the combined beginner level filter.

### 2. `bot.py`
- **Location**: `is_job_relevant(job, keyword, settings)` and `change_level` callback.
- **Modifications**:
  1. Updated `change_level` levels tuple to include `"Iniciantes Tudo"` for Telegram menu toggles.
  2. Added condition for normalized `user_level in ('iniciantes stuff', 'iniciantes tudo')`:
     - Evaluates whether job satisfies `is_aprendiz` criteria (matches `aprendiz_terms` in `full_text`).
     - Evaluates whether job satisfies `is_ganhar_exp` criteria (matches `target_exp_terms` and does NOT match `higher_terms`).
     - Returns `False` if neither criteria is met.
  3. Updated `active_global_blacklist` filtering to allow terms `"voluntario"` and `"voluntary"` when `user_level in ("ganhar experiencia", "iniciantes tudo", "iniciantes stuff")`.
- **Rationale**: Genuine, unified evaluation combining 'jovem aprendiz' and 'ganhar experiência' filter logic while unblocking volunteer jobs.

### 3. `test_iniciantes.py` (New File)
- **Location**: Root directory `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_iniciantes.py`
- **Tests Added**:
  - `test_iniciantes_voluntario`: Validates "Dev Voluntário" under `user_level = 'iniciantes tudo'` returns `True`.
  - `test_iniciantes_aprendiz`: Validates "Jovem Aprendiz de TI" under `user_level = 'iniciantes tudo'` returns `True`.
  - `test_iniciantes_junior_blocked`: Validates "Dev Júnior 1 ano de experiência" under `user_level = 'iniciantes tudo'` returns `False`.
- **Execution**: Can be executed directly via Python (`python test_iniciantes.py`) or Pytest (`pytest test_iniciantes.py`).

## Test Execution Results

1. **`test_iniciantes.py`**:
   - Status: PASS (3/3 test cases passed)
2. **`test_experience.py`**:
   - Status: PASS (10/10 test cases passed)
3. **`test_motor.py`**:
   - Status: PASS (16/16 test cases passed)
4. **`test_keywords.py`**:
   - Status: PASS (20/20 test cases passed)
5. **`run_tests.py` / Pytest suite**:
   - Status: PASS (69/69 test cases passed)
