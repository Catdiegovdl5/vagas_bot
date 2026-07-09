# Scope: Scrapers Restore

## Architecture
- **Data Flow**:
  - The 9 scrapers (Jsearch, Workana, Remotar, Glassdoor, Gupy, Vagas Com, Programathor, Coodesh, Geekhunter) scrape jobs for a given keyword (default "Desenvolvedor" or "Desenvolvedor" with level) and return a list of dictionaries representing jobs.
  - The scraper modules reside under `scrapers/`.
  - A verification script `test_scrapers.py` at the root imports and runs all 9 scrapers, asserting that they each return more than 0 results without throwing exceptions.
  
## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Investigation | Analyze all 9 scrapers to find reasons they are returning 0 results or failing. | None | DONE |
| 2 | Restoration | Apply fixes to the 9 scrapers so they return valid jobs. | M1 | DONE |
| 3 | Verification Script | Create `test_scrapers.py` and run it to verify results. | M2 | DONE |
| 4 | Final Verification & Audit | Perform final verification and run Forensic Auditor for integrity check. | M3 | DONE |

## Interface Contracts
### Scraper interface
- Each scraper module must expose a function `scrape(keyword: str, **kwargs) -> List[dict]` or `scrape(keyword: str) -> List[dict]` (we should check the exact signature).
- Returns list of dictionaries with keys like `title`, `company`, `link`, etc.
- No exception should escape the `scrape()` function or the main test script.
