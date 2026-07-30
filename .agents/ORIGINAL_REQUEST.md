# Original User Request

## 2026-07-29T11:27:45Z

# Teamwork Project Prompt — Draft

> Status: Launched 🚀
> Goal: Get user approval → delegate to teamwork_preview

**Project Description**: Refatorar os scrapers na pasta `scrapers/` (Gupy, LinkedIn, Workana, Infojobs, etc.) para garantir que eles pesquisem ativamente as vagas das 6 novas categorias profissionais com precisão máxima. Os agentes devem focar em injetar as palavras-chave diretamente nas buscas das plataformas para otimizar requisições.

Working directory: `C:\Users\99196\OneDrive\Documentos\vagas_bot`
Integrity mode: demo

## Verification Resources
The project has existing tests in the `tests/` directory which you can adapt to verify your changes.

## Requirements

### R1. Native Scraper Search Parameterization
All relevant python scrapers in the `scrapers/` directory must be refactored to explicitly support querying the 6 new profession categories (Operações Físicas, Logística, Administrativo, Criativos de Performance, Inteligência de Vendas, Engenharia de IA/Dados). Wherever possible, map these new taxonomies directly into the platform's API/search parameters to prevent generic bulk scraping.

### R2. Downstream Payload Compatibility
Ensure that the output returned by the updated scrapers maintains compatibility with the existing database schema and insertion flows. The `profession` or `category` fields in the returned job objects must accurately reflect the new taxonomy mappings.

## Acceptance Criteria

### Objective Verification
- [ ] At least three individual platform scrapers in `scrapers/` are updated to support the new categories natively.
- [ ] A programmatic test (adapting an existing test from `tests/`) runs against at least 3 updated scrapers using one of the new categories (e.g., "Operador CNC" ou "Pintor Industrial").
- [ ] The test executes successfully without API errors and returns valid job objects (or a clean empty list if no jobs are found).
- [ ] The returned job objects correctly contain the appropriate classification fields matching the internal database structure.
