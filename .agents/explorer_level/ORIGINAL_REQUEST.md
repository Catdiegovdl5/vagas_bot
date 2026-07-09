## 2026-07-07T18:32:07Z

Please analyze the codebase, specifically bot.py, to understand how the search keyword and the seniority level filter (settings["level"]) are used. 

Your objectives:
1. Locate where settings["level"] is defined, loaded, or read.
2. Locate where scrapers are invoked (e.g. search loops, fetch_plat, etc.) and where the search keyword is passed to them.
3. Recommend how to implement the requirement: if settings["level"] is different from "Todos", append the level to the search keyword (e.g. f"{search_keyword} {settings['level']}") before passing it to the scraper modules.
4. Write your detailed analysis report to C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\explorer_level\analysis.md.

Note: You are a read-only exploration agent. Do NOT modify any files in the repository. Save your results in your analysis.md file and send a message back to me (conversation ID: 5cb4152d-4810-4c8d-8709-f0d9655e30c6) when you are done, citing the path to the report.
