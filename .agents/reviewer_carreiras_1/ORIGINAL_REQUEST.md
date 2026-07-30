## 2026-07-21T17:15:32Z

<USER_REQUEST>
Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\reviewer_carreiras_1

You are a Reviewer specialist for the vagas_bot project.

Task:
Perform code review and verification of the new Career Guidance & Gamified Progress Track module ('Guia de Profissionalização e Trilha de Carreira') implemented in `bot.py`, `database.py`, and `test_carreiras.py`.

Requirements to verify:
- R1. Interactive Career Guidance Module: InlineKeyboardMarkup menus for navigating the 5 elite professions (Server-Side Tracking, Growth Engineer, Analytics Engineer, IA-Ops, SDR Técnico), explaining what each profession is, market demand, and listing certification/specialization steps with valid URLs.
- R2. Gamified Progress Track: Persistently mark/unmark completed steps/certifications in SQLite database (`user_career_progress` table in `database.py`), updating interface status (e.g. ✅ Concluído vs ⬜ Pendente).
- R3. Seamless Integration: Integrated into current `bot.py`, accessible via main menu button ('🎓 Trilha de Carreiras') in `/start` and command `/carreiras`, without breaking existing job search code.

Instructions:
1. Examine code changes in `bot.py`, `database.py`, and `test_carreiras.py`.
2. Run pytest suite on `test_carreiras.py` and `test_menu_expansion.py`.
3. Check for correctness, error handling, thread safety in SQLite connection handling, Telegram 64-byte callback_data limits, button limits (<15 per markup), and valid HTTPS certification links.
4. Write your detailed review report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\reviewer_carreiras_1\review.md` and handoff report to `handoff.md`. Send completion message when done.
</USER_REQUEST>
