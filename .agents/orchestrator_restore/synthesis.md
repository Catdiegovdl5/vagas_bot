# Synthesis of Scraper Investigation Reports

## Catalog of Inputs
- **Explorer 1** (Conv ID: `45c9e703-af3f-4caa-a18d-db12bc01f906`):
  - Investigated all 9 scrapers empirically using custom test scripts.
  - Key findings:
    - Jsearch: RapidAPI 404 endpoint/auth error.
    - Workana & Vagas.com: Fully operational.
    - Remotar: CSR Next.js. Suggests Playwright navigation.
    - Glassdoor: Validation logic evaluates to True on Cloudflare challenge pages due to brand name check.
    - Gupy: Legacy API `/api/job-search` deprecated. Suggests new API `employability-portal.gupy.io/api/v1/jobs`.
    - Programathor: Case-sensitivity bug (uppercase keyword redirects to 404). Lowercase fixes it.
    - Coodesh: CSR shell. Suggests direct API call using key `x-csh-key: coodesh-experts`.
    - Geekhunter: Domain change to `geekhunter.com/pt`, dynamic rendering. Suggests parsing `/jobs/` links directly from HTML.
- **Explorer 2** (Conv ID: `f2396696-0aac-4f03-9332-8f6346191fc9`):
  - Investigated the 9 scrapers and identified system logic gaps in `bot.py`.
  - Key findings:
    - Jsearch: Default API key expired.
    - Workana: Cloudflare blocks request, Vue results-initials tag.
    - Remotar: Defunct route returning 404. Correct route is `/search?q={search_kw}`.
    - Glassdoor: Cloudflare Turnstile blocks, suggests standard query URL.
    - Gupy: Cloudflare block on API portal.
    - Vagas.com: SEO landing page format `/vagas-de-{kw}` returns 404 for custom keywords. Suggests dynamic search `/vagas/?q={kw}`.
    - Programathor: SEO landing page format `/jobs-{kw}` returns 404.
    - Coodesh: Next.js/React SPA skeleton. Suggests API or Playwright.
    - Geekhunter: Mandatory authentication barrier/login redirect.
    - `bot.py`: Identification of unlisted scrapers in country/location filtering block.
- **Explorer 3** (Conv ID: `ca06b449-7090-4bd1-be1a-7193f7733c8e`):
  - In progress. Noted JSearch (404/auth), Workana (works but subject to blocks), Remotar (Next.js SPA using `https://api.remotar.com.br/jobs` backend).

## Consensus vs Dissent & Resolution

### JSearch
- **Consensus**: Default key is expired/invalid. Must require valid `JSEARCH_API_KEY` in `.env` or fix error handling to not fail silently.

### Workana
- **Consensus**: Workana has some Cloudflare protections, but the core Vue parsing logic (`:results-initials`) is intact and currently works.
- **Resolution**: Keep Vue selector logic. Ensure standard request headers are correct, or fallback to `curl_cffi` if Cloudflare blocks.

### Remotar
- **Dissent**: Explorer 1 suggests Playwright for CSR Next.js. Explorer 2 suggests updating search route to `/search?q={kw}`. Explorer 3 notes Next.js SPA using `https://api.remotar.com.br/jobs` backend.
- **Resolution**: Querying the backend API `https://api.remotar.com.br/jobs` or dynamic route `/search?q={kw}` is much faster and cleaner than Playwright. We should first inspect if the backend API or simple headers on the search route works. If not, fallback to Playwright.

### Glassdoor
- **Consensus**: Headless Playwright gets stuck on Cloudflare Turnstile. The validator incorrectly thinks it succeeded because "glassdoor" is on the Cloudflare challenge page.
- **Resolution**: Update success validator to check for real job cards or exclude Cloudflare challenge keywords. Use standard query parameter search `https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={kw}`.

### Gupy
- **Consensus**: Legacy `/api/job-search` endpoint is decommissioned.
- **Resolution**: Explorer 1 found the new API endpoint `https://employability-portal.gupy.io/api/v1/jobs?jobName={encoded_kw}&limit=30`. This is the perfect fix.

### Vagas.com
- **Dissent**: Explorer 1 says Vagas.com is working. Explorer 2 points out that the URL `/vagas-de-{kw}` returns 404 for custom/complex keywords and suggests `/vagas/?q={kw}`.
- **Resolution**: Implement the dynamic query endpoint `/vagas/?q={kw}` to support arbitrary search queries and prevent 404 redirects.

### Programathor
- **Consensus**: The `/jobs-{kw}` URL redirects or 404s for custom keywords.
- **Resolution**: Force lowercase of the keyword (e.g., `/jobs-python`) as discovered by Explorer 1, or use the dynamic endpoint `/jobs?text={kw}` as suggested by Explorer 2. Lowercase query is very simple and works well.

### Coodesh
- **Consensus**: Static HTML is empty due to SPA rendering.
- **Resolution**: Query Coodesh's public API `https://api.coodesh.com/v2/jobs?search={encoded_kw}&pageSize=30` using header `x-csh-key: coodesh-experts` and `referer: https://coodesh.com/` as discovered by Explorer 1.

### Geekhunter
- **Consensus**: Obsolete selectors/domain.
- **Resolution**: Update URL to `https://www.geekhunter.com/pt/vagas?q={encoded_kw}`. Extract the job URLs directly from `/jobs/` links in the HTML, split by `/` to get company name, and pull skill tags.

### bot.py (Systemic Logic Gap)
- **Consensus**: Gupy, Vagas.com, Programathor, Coodesh, and Geekhunter are excluded from the location-aware call block in `bot.py`, defaulting to remote/national search.
- **Resolution**: Add these platforms to the location-aware `if` block, or ensure location parameters are correctly formatted for them.

## Gaps
- None. The findings cover all 9 scrapers and bot.py logic.
