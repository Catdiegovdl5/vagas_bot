# Detailed Code Review Report

## Review Summary

**Verdict**: APPROVE

The changes implemented in `bot.py` (lines 528-545) and its integration test in `tests/test_tier1.py` (lines 359-425) are correct, complete, and robust. The centralized seniority level filtering works as designed by appending the seniority level to the search keyword and passing `"Todos"` to the scrapers. This prevents duplicate level suffixes and ensures the scrapers retrieve raw jobs, while the bot overwrites the job level with the user's targeted seniority before database insertion, matching the DB schema.

We also note that the new integration test `test_bot_centralized_seniority_level_filtering` passes. However, we found minor robustness edge cases and a pre-existing test mock failure that should be addressed.

---

## Findings

### [Major] Finding 1: Glassdoor Scraper Mock Validation Failure
- **What**: Tests involving the Glassdoor scraper fail because the scraper returns an empty list `[]`.
- **Where**: `scrapers/glassdoor.py` (lines 40-49) and `tests/conftest.py` (line 178).
- **Why**: `scrapers/glassdoor.py` performs a verification check on the loaded page content:
  ```python
  if "glassdoor" in content.lower() and len(content) > 5000:
      loaded = True
  ```
  However, the Playwright Mock page in `conftest.py` returns a default page content of `"<html>Mock Page Content</html>"` which is only 30 bytes long and does not contain the word `"glassdoor"`. This causes `loaded` to remain `False`, forcing the scraper to return `[]` and causing 3 test cases to fail.
- **Suggestion**: Update the mock page content in `tests/conftest.py` to return a larger HTML page containing the word `"glassdoor"` when the URL indicates a Glassdoor scrape.

### [Minor] Finding 2: Robustness of Level Setting Fallback
- **What**: `settings.get("level", "Todos")` fails to fall back to `"Todos"` if the `"level"` key is present in the dictionary but has a value of `None`.
- **Where**: `bot.py` line 528.
- **Why**: If `settings` contains `{"level": None}`, `settings.get("level", "Todos")` will return `None`. This bypasses the `"Todos"` check (since `None != "Todos"`), resulting in `search_keyword = f"{search_keyword} None"`. The scraper will then search for the literal string `"None"` on job platforms, and the database will insert jobs with a `None` level.
- **Suggestion**: Change line 528 in `bot.py` from:
  ```python
  actual_level = settings.get("level", "Todos")
  ```
  to:
  ```python
  actual_level = settings.get("level") or "Todos"
  ```

---

## Verified Claims

- Centralized seniority level is appended to the search keyword when not `"Todos"` → verified via inspection of `bot.py` (lines 528-531) and execution of `test_bot_centralized_seniority_level_filtering` → **PASS**
- `"Todos"` is passed to all scrapers to prevent duplicate suffixes → verified via inspection of `bot.py` (lines 539-542) → **PASS**
- `job["level"]` is overwritten with the user's targeted level before database insertion → verified via inspection of `bot.py` (lines 543-545) and database schema verification in tests → **PASS**

---

## Coverage Gaps

- **Keyword Matching Accent Differences** — risk level: **Medium** — The keyword suffix is appended literally as `"Sênior"` or `"Júnior"`. Some job search engines might perform strict matches and fail to find `"Sênior"` if it is spelled without an accent (e.g. `"Senior"` or `"Junior"`).
- **Recommendation**: Accept risk or add basic search keyword normalization to try both accented and non-accented variants if search yields no results.

---

## Unverified Items

- **Real Glassdoor Scraping Output** — The Glassdoor scraper's behavior with real HTML pages is not fully verified in this local offline test environment due to mocked Playwright interfaces.

---

# Adversarial Review (Critic Perspective)

## Challenge Summary

**Overall risk assessment**: LOW

The centralized level filtering mechanism is logical and keeps the scraper modules clean. However, the system relies on the assumption that adding a text suffix like `"Sênior"` or `"Júnior"` to the keyword is universally supported and effective across all scraped platforms.

## Challenges

### [Medium] Challenge 1: Rigid Suffix Matching on Search Platforms
- **Assumption challenged**: Adding `"Sênior"` or `"Júnior"` to the search query keyword works correctly on all platforms.
- **Attack scenario**: Some platforms (like Jooble or Indeed) have specific structured filters for experience level rather than text queries. Adding `"Sênior"` to the text search query might exclude positions that do not have the word "Sênior" in the title or text but are flagged as senior by the platform's metadata. Alternatively, if a platform uses unaccented Portuguese search indexers, searching for `"Sênior"` might return zero results, whereas searching for `"Senior"` would succeed.
- **Blast radius**: Reduced search recall. Users might miss relevant positions because of strict query string matching on the search engines.
- **Mitigation**: Introduce a query normalization dictionary that maps levels to both accented and unaccented terms, or allow scrapers to translate the level into native API/query parameters where possible.

---

## Stress Test Results

- **Level value is `None`** → expected to fall back to `"Todos"` → actual behavior: appends `"None"` to search string → **FAIL** (Mitigated by suggestion in Finding 2)
- **Level is `"Todos"`** → expected to bypass keyword modification → actual behavior: keyword remains unmodified, scraper receives `level="Todos"`, DB level set to `"Todos"` → **PASS**
