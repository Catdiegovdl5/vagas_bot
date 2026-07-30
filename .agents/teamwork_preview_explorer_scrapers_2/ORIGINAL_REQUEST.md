## 2026-07-29T11:28:24Z
You are teamwork_preview_explorer_scrapers_2.
Your working directory is `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_scrapers_2`.
Please create your working directory if it does not exist, initialize `progress.md`, and perform code exploration.

Objective:
Inspect backend job models, database schemas, and payload handlers (e.g. `database.py`, `models.py`, `bot.py`, `app.py`, `scrapers/`).
Determine:
1. What fields are required in job dictionary/object payloads returned by scrapers (e.g. `title`, `company`, `url`, `source`/`platform`, `profession`/`category`, `location`, `description`, etc.).
2. How downstream database insertion flows validate or store `profession` and `category` fields.
3. Verify if `profession` or `category` or both need to be populated with the exact name of the 6 new categories, or if there is a normalization/mapping dictionary.
4. Specify exact requirements to ensure 100% downstream payload compatibility.

Write your findings to `analysis.md` and `handoff.md` in `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_scrapers_2\`. Send a completion message to parent when done.
