# Original User Request

## Initial Request — 2026-07-04T13:30:56Z

O projeto visa transformar o bot atual em uma máquina autônoma de recrutamento end-to-end com quatro pilares: (1) Adição de Scrapers S-Tier (LinkedIn, Glassdoor, InfoJobs); (2) Web Scraping profundo para resolver a limitação de snippets (Jooble/Indeed); (3) Novo modelo de pontuação IA (priorizando Salário e Benefícios); e (4) Sistema de Auto-Apply para disparo automatizado de currículos.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Scrapers S-Tier
Implementar scrapers para LinkedIn, Glassdoor e InfoJobs. Eles devem ser capazes de puxar o texto completo das vagas. O LinkedIn deve focar em vagas de Full-time e ignorar o restante.

### R2. Bypass de Snippets (Deep Scrape)
Para plataformas que enviam apenas resumos (Jooble e Indeed), construir um mecanismo que acesse a URL da vaga e extraia a descrição completa em HTML/Texto.

### R3. IA Ranking por Remuneração
Modificar a estrutura de dados avaliativa (`JobEvaluation`) para que a IA não apenas "aprove", mas ranqueie as vagas priorizando aquelas que exibem valores salariais e benefícios como VR/VA.

### R4. Motor de Auto-Apply
Criar um módulo capaz de preencher formulários simples de candidatura (Easy Apply) usando os dados do currículo do usuário fornecidos na pasta local.

## Acceptance Criteria

### Scrapers S-Tier & Bypass
- [ ] O script `scrapers/linkedin.py` retorna pelo menos 10 vagas com a chave `requirements` contendo mais de 500 caracteres, rodando um teste unitário programático.
- [ ] O scraper do Indeed resolve e extrai o texto do DOM ao invés de retornar o snippet da API.

### IA Ranking
- [ ] Ao rodar o pipeline do Groq em um dataset de 5 vagas controladas, a vaga com maior salário declarado sempre fica no topo (`ai_score` mais alto).

### Auto-Apply
- [ ] Existe um script `test_apply.py` que demonstra submissão bem sucedida (status 200 OK) para uma URL de mockup local representando um ATS.

## Follow-up — 2026-07-04T15:34:26Z

O projeto visa refinar a inteligência de filtragem da IA (Groq) no `Sniper_bot`, eliminando o problema de "alucinação" onde o modelo reprova a vaga em texto, mas a aprova no booleano. O objetivo é alcançar 110% de precisão usando travas via código (hard-locks), troca de modelo e validação massiva automatizada.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: benchmark

## Requirements

### R1. Python Hard-Locks (Trava de Segurança)
Modificar o fluxo de avaliação em `scrapers/ai_filter.py`. Mesmo que a IA retorne `aprovado = True`, o Python deve interceptar a resposta e forçar `aprovado = False` se qualquer uma das regras de quebra for ativada (ex: `vaga_corresponde_ao_cargo == False`, `is_freelance == True`, `localidade_correta == False`, `exige_faculdade == True`, `exige_experiencia == True`).

### R2. Upgrade de Modelo
Alterar o modelo padrão instanciado no `AsyncGroq` (dentro de `ai_filter.py`) para um modelo de maior capacidade de raciocínio (ex: `llama3-70b-8192` or `mixtral-8x7b-32768`) para minimizar as alucinações de inconsistência lógica.

### R3. Bateria de Testes de Sanidade (50 Vagas)
Criar um script de teste e um dataset (JSON ou CSV) com 50 vagas projetadas especificamente como "pegadinhas" (vagas em dólar, vagas que exigem inglês fluente, vagas de estágio quando a configuração é sem formação, projetos Workana, etc). O script deve submeter as 50 vagas ao `ai_filter.py` e gerar um relatório.

## Acceptance Criteria

### Precisão e Blindagem
- [ ] O código Python sobrepõe a decisão da IA quando as regras booleanas falham.
- [ ] O modelo configurado no Groq é de alta capacidade (70B+).
- [ ] O script de teste com 50 vagas executa com sucesso.
- [ ] A taxa de aprovação para as vagas criadas como "pegadinha" no dataset é estritamente 0% (gabarito perfeito de bloqueio).

## Follow-up — 2026-07-06T18:39:50Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview

An extensive audit and optimization of the `vagas_bot` codebase to fix remaining bugs, remove unused/obsolete code, and implement architectural improvements for a 100% stable production release.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Aggressive Codebase Audit and Cleanup
Analyze all Python files in the repository. Identify and aggressively remove any dead code, unused imports, or logic that no longer makes sense given the current architecture. Rewrite inefficient logic.

### R2. Bug Fixing and Stability
Identify any edge cases, unhandled exceptions, or logical errors that could crash the Telegram bot or the web server. Implement robust fixes.

### R3. Performance and Architecture Improvements
Propose and implement optimizations for better performance, such as optimizing async tasks, improving the Groq AI API rate-limiting strategy, or enhancing the scraper reliability.

## Acceptance Criteria

### Verification
- [ ] The codebase runs without syntax or import errors.
- [ ] No regression is introduced to the core functionality (scraping, AI filtering, Telegram UI).
- [ ] A detailed report of all changes, removed code, and improvements is provided to the user.

## Follow-up — 2026-07-07T18:03:24Z

O projeto consiste em duas correções pontuais no Vagas Bot: (1) corrigir um bug lógico onde a plataforma Indeed continua aparecendo como "⏳ Buscando..." na Dashboard do Telegram mesmo após o terminal acusar sua finalização e o scraper terminar, e (2) desativar permanentemente o scraper do 99freelas nas configurações de caça.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Corrigir o Bug da Dashboard Viva (Telegram)
O laço assíncrono `status_updater()` que atualiza a mensagem no Telegram precisa garantir que uma última atualização seja enviada após o término de **todos** os scrapers. Atualmente, o último scraper a terminar não tem seu status final renderizado no Telegram porque o laço encerra imediatamente.

### R2. Desativar a Plataforma 99Freelas (Novenove)
O 99freelas está sem "conexões" disponíveis. Você deve remover o módulo/plataforma correspondente (chamado `novenove`) das listas de plataformas ativas no arquivo principal, de modo que ele nunca seja acionado nas caçadas "Freelance", sem deletar o arquivo do scraper em si.

## Acceptance Criteria

### Bug do Dashboard (Indeed) Resolvido
- [ ] Uma análise independente do código modificado em `bot.py` deve confirmar que, após `is_hunting = False` (ou ao término do bloco de scrapers concorrentes), há um comando explícito para enviar a mensagem de status final para o Telegram.

### 99freelas Desativado
- [ ] Uma busca literal pela string "novenove" na definição das plataformas de Freelance em `bot.py` não deve retornar nenhum resultado como ativo.

## Follow-up — 2026-07-07T18:31:10Z

# Teamwork Project Prompt — Draft

O projeto consiste em implementar o suporte real ao filtro de nível de senioridade (Júnior, Pleno, Sênior) em todos os scrapers do Vagas Bot. Atualmente, a interface permite a escolha do nível, mas as plataformas buscam a palavra-chave genérica. A solução escolhida pelo usuário é anexar o nível diretamente à string de busca (ex: "Consultor de IA Júnior") de forma centralizada.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Centralizar a Lógica de Senioridade no bot.py
Você deve alterar a lógica no arquivo `bot.py` (preferencialmente antes das chamadas aos scrapers na função `fetch_plat` ou no laço principal de busca) para que, se a variável `settings["level"]` for diferente de "Todos", o seu valor seja concatenado à palavra-chave (`keyword` ou `search_keyword`).
Dessa forma, ao invés de buscar "Consultor de IA", o bot passará "Consultor de IA Pleno" para todos os módulos de scraping simultaneamente, sem precisar reescrever cada scraper individual.

## Acceptance Criteria

### Implementação Universal e Segura
- [ ] O código em `bot.py` garante que o `search_keyword` tenha o nível concatenado (ex: `f"{search_keyword} {settings['level']}"`) apenas quando o nível não for "Todos".
- [ ] Os módulos da pasta `scrapers/` não precisam ser profundamente alterados, já que a string que eles recebem no argumento `keyword` já chegará mastigada e formatada do `bot.py`.


## Follow-up — 2026-07-07T19:17:34Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview

Realizar uma auditoria completa de leitura no código do Vagas Bot para gerar um relatório de bugs e erros residuais. O código **não** deve ser modificado pela equipe.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Auditoria e Identificação de Bugs (Somente Leitura)
A equipe deve analisar todos os arquivos Python (bot.py, scrapers, etc) em busca de bugs lógicos, erros de sintaxe, exceções não tratadas, loops infinitos, ou gargalos de performance (como chamadas síncronas bloqueando o loop assíncrono). A equipe **NÃO** deve modificar nenhum arquivo.

### R2. Relatório Detalhado
Gerar um relatório em formato Markdown listando todos os problemas encontrados, incluindo o nome do arquivo, a linha exata e a explicação do porquê ser um problema e como resolvê-lo. Se não houver problemas, o relatório deve confirmar que o código está limpo.

## Acceptance Criteria

### Verificação do Relatório
- [ ] Um arquivo `bug_report.md` (ou similar) é criado no diretório de artefatos contendo os resultados da auditoria.
- [ ] O relatório aponta arquivos e linhas específicas para qualquer problema encontrado.
- [ ] Nenhum arquivo de código original `.py` foi modificado durante a execução.

## Follow-up — 2026-07-07T20:16:45Z

# Teamwork Project Prompt — Draft

> Status: Launched

Realizar uma auditoria rápida (Fast Audit) apenas nos 6 novos arquivos criados (`scrapers/catho.py`, `gupy.py`, `vagas_com.py`, `programathor.py`, `coodesh.py`, `geekhunter.py`) e nas integrações do `bot.py`/`app.py` para garantir que não haja erros impeditivos, exceções fatais ou gargalos óbvios. Focar estritamente no essencial para economizar tokens e tempo.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Auditoria Rápida (Somente Leitura)
A equipe deve focar apenas em erros sintáticos, chamadas bloqueantes acidentais, ou falhas de dicionário sem fallback (`.get()`) nos 6 novos scrapers. Ignorar questões de estilo, formatação, ou code-smells não críticos.

### R2. Relatório Enxuto
Gerar um relatório direto e minimalista listando apenas problemas reais que vão causar crash. Se o código estiver seguro, retornar apenas "Tudo Seguro".

## Acceptance Criteria

### Verificação
- [ ] O relatório aponta apenas erros de severidade ALTA (ex: crashes, loops infinitos, exceptions sem try/catch em áreas críticas).
- [ ] A equipe NÃO modifica nenhum arquivo, apenas lê e reporta.

## Follow-up — 2026-07-07T23:24:18Z

# Teamwork Project Prompt — Draft

> Status: Launched

Realizar uma varredura completa e minuciosa (Deep Audit) em toda a base de código do `vagas_bot` para encontrar e corrigir qualquer bug restante, garantindo 100% de estabilidade. O foco é resolver condições de corrida, falhas de extração, erros de UI no Telegram e vazamentos de exceções.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Auditoria Profunda e Correção
A equipe deve analisar ativamente todos os arquivos (`bot.py`, `app.py`, `auto_apply.py`, `database.py` e todos os `scrapers/`) em busca de bugs lógicos, erros de sintaxe ou gargalos de performance, e aplicar as correções necessárias no código.

### R2. Estabilidade Assíncrona
Garantir que todas as chamadas bloqueantes (I/O, rede, leitura de disco) estejam devidamente isoladas do event loop do Telegram para evitar travamentos.

## Acceptance Criteria

### Validação de Qualidade
- [ ] O código passa em testes de sintaxe (nenhum erro de compilação).
- [ ] Nenhum scraper possui exceções não tratadas no nível de extração de itens.
- [ ] A equipe de auditoria reporta as correções feitas de forma clara.

## Follow-up — 2026-07-07T23:46:54Z

Diagnosticar e corrigir scrapers do `vagas_bot` que retornam 0 vagas ou falham com erros de rede/DNS, com base nos logs reais de execução capturados pelo usuário. O objetivo é maximizar o número de vagas reais retornadas por execução.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Context (Logs Reais)

Os seguintes problemas foram identificados num ciclo real de execução:

```
GUPY       → 0 vagas (sem erro aparente)
COODESH    → 0 vagas (sem erro aparente)  
PROGRATHOR → 0 vagas (sem erro aparente)
JSEARCH    → 0 vagas (sem erro aparente)
REMOTAR    → Timeout (connect timeout=5s muito curto)
GEEKHUNTER → DNS não resolve via curl_cffi
INDEED     → Muito lento (~116s por execução, puxando páginas de detalhe individualmente)
META_ADS   → "Authentication token was not provided" (token Apify ausente)
```

## Requirements

### R1. Corrigir Scrapers com 0 Resultados
Para `scrapers/gupy.py`, `scrapers/coodesh.py`, `scrapers/programathor.py` e `scrapers/jsearch.py`: investigar o HTML ou JSON atual de cada plataforma, identificar se os seletores ou endpoints mudaram, e atualizar o código para extrair vagas reais. Se a plataforma bloquear scrapers de forma definitiva, documentar no relatório e retornar `[]` com log claro.

### R2. Corrigir Falhas de Conexão
Para `scrapers/remotar.py`: aumentar o `connect timeout` de 5s para pelo menos 15s. Para `scrapers/geekhunter.py`: testar alternativa de conexão (requests padrão ou headers alterados) para resolver o problema de DNS com `curl_cffi`.

### R3. Otimizar Performance do INDEED
O scraper `scrapers/indeed.py` está demorando ~116 segundos porque busca páginas de detalhe individualmente com `curl_cffi`. Reduzir o número de requisições de detalhe por execução (ex: limitar a 5 vagas com detalhe) ou extrair dados suficientes da listagem sem precisar acessar cada vaga individualmente.

### R4. Tratar META_ADS com Graciosidade
O `scrapers/meta_ads.py` falha silenciosamente sem o token Apify. Garantir que o erro seja capturado com `try/except` e logado adequadamente, sem afetar os outros scrapers.

## Acceptance Criteria

### Qualidade
- [ ] O código de todos os arquivos modificados compila sem erros de sintaxe (`py_compile`).
- [ ] `scrapers/remotar.py` tem timeout >= 15s.
- [ ] `scrapers/indeed.py` completa em menos de 30s (redução de ~75% no tempo atual).
- [ ] Scrapers com 0 resultados foram investigados e ou retornam vagas reais ou retornam `[]` com log explicativo claro.
- [ ] Nenhum scraper lança exceção não capturada.

## Follow-up — 2026-07-08T12:08:33Z

O objetivo é investigar e consertar 9 scrapers específicos do Vagas Bot que estão atualmente retornando 0 vagas nas caçadas. Os scrapers são: Jsearch, Workana, Remotar, Glassdoor, Gupy, Vagas Com, Programathor, Coodesh e Geekhunter. Eles devem voltar a extrair vagas corretamente com os novos termos de busca.

Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot
Integrity mode: benchmark

## Requirements

### R1. Restabelecer a Extração
Você deve investigar, debugar e corrigir os arquivos em `scrapers/` referentes aos 9 sites listados acima. Descubra o porquê de cada um estar retornando `0` (mudança no HTML, bloqueio de rede, seletores desatualizados, etc) e implemente as correções para que eles voltem a retornar listas de dicionários de vagas válidas.

### R2. Script de Verificação
Você deve criar um script autônomo na pasta do projeto chamado `test_scrapers.py`. Este script deve importar e rodar a função `scrape()` de cada um dos 9 scrapers individualmente passando `keyword="Desenvolvedor"`.

## Acceptance Criteria

### Teste de Validação Programática
- [ ] O script `test_scrapers.py` deve rodar do início ao fim sem lançar exceções.
- [ ] Para **cada um** dos 9 scrapers testados pelo script, a afirmação `len(vagas) > 0` deve ser verdadeira (ou seja, capturar pelo menos 1 vaga real de "Desenvolvedor").

## Follow-up — 2026-07-08T13:30:12Z

O objetivo é expandir os filtros do Vagas Bot para capturar vagas voltadas ao uso de ferramentas de IA (ChatGPT, Midjourney, Claude, etc.) em áreas menos técnicas e mais focadas em criatividade, marketing, redação, design, animação e geração de imagens/vídeos.

Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot
Integrity mode: benchmark

## Requirements

### R1. Expandir a Lógica de Filtragem (IA Criativa e Operacional)
Você deve modificar a lógica de filtragem (`rules` no arquivo `bot.py` ou os dicionários de busca, e qualquer outra parte relevante) para que o bot passe a aprovar vagas para profissionais que **usam** a IA para gerar textos, imagens, vídeos ou campanhas (ex: Copywriter com IA, Designer Midjourney, Videomaker com IA Generativa). A decisão da arquitetura (criar um novo nicho específico no menu ou integrar isso ao nicho de "Especialista em IA Generativa") cabe inteiramente à equipe de agentes.

### R2. Script de Validação Rigorosa
Você deve criar um script de testes independente na raiz do projeto chamado `verify_ai_creative_jobs.py`. O script deve importar a função de validação de vagas do `bot.py` (ou simular a lógica caso ela não possa ser importada diretamente).

## Acceptance Criteria

### Teste de Falsos Positivos e Falsos Negativos
- [ ] O script `verify_ai_creative_jobs.py` deve criar um mock de pelo menos 5 títulos de vagas "criativas com IA" (ex: "Copywriter ChatGPT", "Designer Midjourney", "Editor de Vídeo - IA", etc.) e afirmar matematicamente que o bot **APROVA** todas elas.
- [ ] O script também deve criar um mock de pelo menos 5 títulos de vagas "comuns não relacionadas à IA" (ex: "Desenvolvedor Java", "Analista de RH", "Vendedor", etc.) e afirmar matematicamente que o bot sob esta categoria **REJEITA** todas elas.
- [ ] O script de teste deve rodar com saída 100% verde sem gerar exceções.

