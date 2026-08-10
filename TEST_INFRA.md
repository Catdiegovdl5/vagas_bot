# E2E Test Infra: vagas_bot

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design.
- Methodology: Category-Partition + BVA + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Launcher & FastAPI Port 8000 Launch | ORIGINAL_REQUEST § R1 | 5 | 5 | ✓ |
| 2 | Batch Scripts Invocation | ORIGINAL_REQUEST § R1 | 5 | 5 | ✓ |
| 3 | SEO & Schema.org Endpoints | ORIGINAL_REQUEST § R2 | 5 | 5 | ✓ |
| 4 | Category Search & NOT LIKE Exclusions | ORIGINAL_REQUEST § R3 | 5 | 5 | ✓ |
| 5 | Frontend SPA & DOM Cleanliness | ORIGINAL_REQUEST § R4 | 5 | 5 | ✓ |
| 6 | Error Reporter & Self-Healer Logging | ORIGINAL_REQUEST § R5 | 5 | 5 | ✓ |

## Test Architecture
- Test runner: Python `pytest` and empirical verification scripts (`scripts/verify_category_integrity_qa.py`).
- Pass/fail semantics: Exit code 0, 100% test pass.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full system startup via launcher without Telegram token | F1, F2, F5 | High |
| 2 | SEO indexing crawl on /sitemap.xml and schema API | F3 | Medium |
| 3 | Category filtering with zero leakage and exact DB count | F4 | High |
| 4 | Error capture and auto-patch generation under 500 error | F6 | High |
| 5 | Git branch verification on refactor/organizacao-e-limpeza | F1..F6 | Medium |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 per feature
- Tier 3: Pairwise coverage of major feature interactions
- Tier 4: ≥5 realistic application scenarios
