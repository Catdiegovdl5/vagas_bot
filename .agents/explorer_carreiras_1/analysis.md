# Análise Técnica & Design de Integração: Módulo 'Guia de Profissionalização e Trilha de Carreira'

## 1. Visão Geral e Contexto
O objetivo desta análise é estruturar a inclusão do novo módulo interativo **'Guia de Profissionalização e Trilha de Carreira'** no bot do Telegram (`bot.py`), focando nas **5 profissões de elite e alta demanda no mercado digital/tech**:
1. **Server-Side Tracking** (GTM Server, Stape.io, Meta CAPI, GA4, Cookie First-Party, Privacy Shield)
2. **Growth Engineer** (Engenharia de Conversão, Testes A/B, Webhooks, Automação de Funil, CRO, Integrador MarTech)
3. **Analytics Engineer** (dbt, SQL Avançado, Data Warehousing, BigQuery/Snowflake, Modelagem Dimensional, Looker/PowerBI)
4. **IA-Ops** (Automação de Workflows com IA, n8n/Make, Integração de APIs LLM, Deployment de Agentes, IA Empresarial)
5. **SDR Técnico** (Vendas B2B SaaS Tech, Prospecção Qualificada, Mapeamento Técnico de Soluções, Outbound Automatizado)

---

## 2. Arquitetura Atual do `bot.py`
A análise do arquivo `bot.py` (1.802 linhas, biblioteca `aiogram 3.x`) revelou os seguintes pontos principais:

### 2.1. Handlers de Comando Existentes
- **`/start`** (linha 110-112): Executa `@dp.message(Command("start"))` chamando `show_main_menu(message)`.
- **`/logs`** (linha 114-131): Exibe os últimos logs de erro.

### 2.2. Estrutura dos Menus Principais
- **Menu Persistente (ReplyKeyboardMarkup)** (linha 140-144):
  ```python
  persistent_markup = ReplyKeyboardMarkup(
      keyboard=[[KeyboardButton(text="🎯 Caçar Vagas"), KeyboardButton(text="🛠 Configurações")]],
      resize_keyboard=True,
      is_persistent=True
  )
  ```
- **Menu Inline Principal (`get_main_menu_markup()`)** (linha 150-155):
  ```python
  def get_main_menu_markup():
      return InlineKeyboardMarkup(inline_keyboard=[
          [InlineKeyboardButton(text="🎯 Caçar Vagas", callback_data="hunt_menu")],
          [InlineKeyboardButton(text="🎓 Caçar Tudo para Iniciantes", callback_data="mega_iniciantes")],
          [InlineKeyboardButton(text="🛠 Configurações", callback_data="settings_menu")]
      ])
  ```

### 2.3. Roteamento de Mensagens e Callbacks
- **Handlers de Texto Relacionados a Botões**:
  - `@dp.message(F.text == "🎯 Caçar Vagas")` (linha 1633)
  - `@dp.message(F.text == "🛠 Configurações")` (linha 1649)
  - `@dp.message(F.text)` (linha 1656) captura texto livre e executa busca genérica.
- **CallbackQueryHandler**:
  - Utiliza `F.data == "main_menu"`, `F.data == "hunt_menu"`, `F.data.startswith("modo_")`, `F.data.startswith("nicho_")`, `F.data.startswith("hunt_")`, etc.

---

## 3. Plano de Integração Sem Restrições / Sem Quebras
Para integrar a **Trilha de Carreiras** perfeitamente sem afetar o fluxo de busca de vagas existente:

### 3.1. Comando `/carreiras`
Adicionar handler nativo com decorator `@dp.message(Command("carreiras"))` que renderiza o menu de carreiras.

### 3.2. Atualização do `ReplyKeyboardMarkup` (`show_main_menu`)
Adicionar o botão `"🎓 Trilha de Carreiras"` mantendo layout limpo de 2 linhas:
```python
persistent_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Caçar Vagas"), KeyboardButton(text="🎓 Trilha de Carreiras")],
        [KeyboardButton(text="🛠 Configurações")]
    ],
    resize_keyboard=True,
    is_persistent=True
)
```

### 3.3. Atualização do Inline Keyboard Principal (`get_main_menu_markup`)
Incluir a nova opção mantendo limite de 15 botões por tela:
```python
def get_main_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Caçar Vagas", callback_data="hunt_menu")],
        [InlineKeyboardButton(text="🎓 Trilha de Carreiras", callback_data="car:main")],
        [InlineKeyboardButton(text="🎓 Caçar Tudo para Iniciantes", callback_data="mega_iniciantes")],
        [InlineKeyboardButton(text="🛠 Configurações", callback_data="settings_menu")]
    ])
```

### 3.4. Handler para Botão de Texto
Adicionar `@dp.message(F.text == "🎓 Trilha de Carreiras")` antes do handler genérico `@dp.message(F.text)` para garantir a captura imediata sem cair na busca de vagas NLP.

---

## 4. Especificação do `callback_data` (Limite do Telegram: Max 64 Bytes)

### 4.1. Regra da API do Telegram
O Telegram limita estritamente o parâmetro `callback_data` a **64 bytes (UTF-8)**. Exceder esse limite resulta em exceção `BadRequest: BUTTON_DATA_INVALID`.

### 4.2. Padrão Recomendado (`car:*`)
Para garantir concisão, extensibilidade e margem ampla de segurança (máximo de 12 bytes utilizados), adota-se o prefixo `car:`:

| Ação | Formato `callback_data` | Exemplo | Bytes | Descrição |
|---|---|---|---|---|
| Menu Principal de Carreiras | `car:main` | `car:main` | 8 bytes | Abre menu com as 5 profissões de elite |
| Detalhes da Profissão | `car:p:<pid>` | `car:p:1` | 7 bytes | Exibe visão geral, salário, ferramentas e botão de trilha da profissão 1 |
| Trilha / Checklist | `car:r:<pid>` | `car:r:1` | 7 bytes | Exibe o mapa de desenvolvimento/etapas da profissão 1 |
| Toggle de Etapa na Trilha | `car:t:<pid>:<step>` | `car:t:1:2` | 9 bytes | Alterna status (concluído/pendente) da etapa 2 da profissão 1 |
| Disparar Busca de Vagas | `car:j:<pid>` | `car:j:1` | 7 bytes | Executa `_do_hunt` com a keyword otimizada da profissão |
| Cursos & Recursos | `car:c:<pid>` | `car:c:1` | 7 bytes | Lista recursos, documentações e guias recomendados |

**IDs das Profissões (`<pid>`):**
- `1`: Server-Side Tracking
- `2`: Growth Engineer
- `3`: Analytics Engineer
- `4`: IA-Ops
- `5`: SDR Técnico

---

## 5. Dicionário de Dados das 5 Profissões de Elite

```python
CAREER_PROFILES = {
    "1": {
        "title": "Server-Side Tracking Specialist",
        "subtitle": "Especialista em Coleta de Dados & Privacidade First-Party",
        "salary_br": "R$ 6.000,00 a R$ 14.000,00 / mês",
        "salary_usd": "$ 3,000 to $ 6,500 / month",
        "summary": "Profissional responsável por configurar rastreamento de dados no servidor (GTM Server-Side, Stape, CAPI) contornando bloqueios de iOS 14+ e adblockers.",
        "search_kw": "Especialista Tracking & MarTech",
        "tools": ["Google Tag Manager (Server)", "Stape.io", "Meta Conversions API", "GA4 BigQuery Export", "Cookie First-Party"],
        "steps": [
            "1. Dominar Web GTM, GA4 e Conceitos de Cookies First-Party vs Third-Party",
            "2. Configurar Servidor de Rastreamento (Stape.io / Google Cloud / AWS Container)",
            "3. Implementar Meta CAPI, Google Ads Server-Side e TikTok Events API",
            "4. Criar Portfólio com Validação via HTTP Request e BigQuery Logs"
        ]
    },
    "2": {
        "title": "Growth Engineer",
        "subtitle": "Engenheiro de Crescimento & Automação de Funil",
        "salary_br": "R$ 7.500,00 a R$ 16.000,00 / mês",
        "salary_usd": "$ 3,500 to $ 8,000 / month",
        "summary": "Une código, análise de dados e marketing para criar experimentos rápidos, testes A/B complexos, automações de produto e engenharia de conversão.",
        "search_kw": "Growth Engineer / Product Growth",
        "tools": ["Python/JS", "PostHog / Mixpanel", "VMO / Optimizely (A/B)", "n8n / Webhooks", "SQL / Segment"],
        "steps": [
            "1. Fundamentos de CRO, Métricas de Funil (AARRR) e Testes A/B",
            "2. Domínio de Scripting (JavaScript/Python) para Instrumentação de Produtos",
            "3. Automação de Workflows com Webhooks, APIs e Ferramentas No-Code/Low-Code",
            "4. Construção de Experimento Real com Relatório de Aumento de Conversão"
        ]
    },
    "3": {
        "title": "Analytics Engineer",
        "subtitle": "Transformador de Dados Brutos em Modelos de Negócio",
        "salary_br": "R$ 8.000,00 a R$ 18.000,00 / mês",
        "salary_usd": "$ 4,000 to $ 9,000 / month",
        "summary": "Fica na ponte entre Data Engineer e Data Analyst. Utiliza dbt e SQL moderno para transformar dados no Data Warehouse de forma testada e documentada.",
        "search_kw": "Analytics Engineer",
        "tools": ["dbt (data build tool)", "SQL Avançado", "BigQuery / Snowflake", "Git / GitHub", "Looker Studio / Power BI"],
        "steps": [
            "1. Domínio Avançado de SQL (CTEs, Window Functions, Analytics Functions)",
            "2. Aprender Engenharia de Transformação com dbt (Models, Tests, Docs, Jinja)",
            "3. Arquitetura de Data Warehouse (Kimball, Modelagem Dimensional, Star Schema)",
            "4. Criar Projeto dbt Público no GitHub com CI/CD e Visualização no BI"
        ]
    },
    "4": {
        "title": "IA-Ops (AI Workflow Specialist)",
        "subtitle": "Engenheiro de Operações e Automações com IA",
        "salary_br": "R$ 7.000,00 a R$ 15.000,00 / mês",
        "salary_usd": "$ 3,500 to $ 7,500 / month",
        "summary": "Especialista em integrar Inteligência Artificial nos processos operacionais da empresa usando orquestradores (n8n, Make), LLMs e agentes autônomos.",
        "search_kw": "AI Coder / AI Agent Developer",
        "tools": ["n8n / Make.com", "OpenAI / Anthropic APIs", "LangChain / CrewAI", "Vector DBs (Pinecone/Qdrant)", "Python / FastApi"],
        "steps": [
            "1. Compreensão de Arquiteturas de LLM, Prompt Engineering e Structuring JSON Output",
            "2. Construção de Workflows no n8n conectando APIs, Webhooks e Bancos SQL",
            "3. Implementação de RAG (Retrieval-Augmented Generation) com Vector DBs",
            "4. Deploy de Agente de IA Funcional para Atendimento ou Processamento de Documentos"
        ]
    },
    "5": {
        "title": "SDR Técnico",
        "subtitle": "Pré-Vendedor Especializado em Soluções Tech / SaaS B2B",
        "salary_br": "R$ 4.500,00 a R$ 9.000,00 + Comissões",
        "salary_usd": "$ 2,500 to $ 5,000 / month",
        "summary": "Profissional de pré-vendas com background técnico para dialogar com CTOs, Tech Leads e Devs, qualificando leads complexos para vendas SaaS.",
        "search_kw": "SDR Técnico",
        "tools": ["HubSpot / Salesforce", "Apollo.io / Clay", "LinkedIn Sales Navigator", "Cold Email Automation", "Tech Stack Scraper"],
        "steps": [
            "1. Metodologias de Qualificação B2B (SPIN Selling, BANT, MEDDIC)",
            "2. Domínio da Linguagem Técnica (APIs, Cloud, SaaS, Métricas Financeiras/Tech)",
            "3. Automação de Prospecção Outbound com Cadência Personalizada",
            "4. Simulação de Call de Qualificação Técnica gravada com Objeções Reais"
        ]
    }
}
```

---

## 6. Proposta de Código de Integração para `bot.py`

### 6.1. Função de Visualização do Menu Principal de Carreiras
```python
@dp.message(Command("carreiras"))
@dp.message(F.text == "🎓 Trilha de Carreiras")
async def cmd_carreiras(message: types.Message):
    await show_carreiras_menu(message)

@dp.callback_query(F.data == "car:main")
async def callback_carreiras_main(callback: CallbackQuery):
    await callback.answer()
    markup = get_carreiras_menu_markup()
    await callback.message.edit_text(
        "🎓 *Guia de Profissionalização & Trilha de Carreira*\n\n"
        "Selecione uma das 5 profissões de elite com alta demanda e altos salários para ver o guia, roadmap e vagas abertas:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def show_carreiras_menu(message: types.Message):
    markup = get_carreiras_menu_markup()
    await message.answer(
        "🎓 *Guia de Profissionalização & Trilha de Carreira*\n\n"
        "Selecione uma das 5 profissões de elite com alta demanda e altos salários para ver o guia, roadmap e vagas abertas:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

def get_carreiras_menu_markup():
    buttons = [
        [InlineKeyboardButton(text="⚡ Server-Side Tracking", callback_data="car:p:1")],
        [InlineKeyboardButton(text="🚀 Growth Engineer", callback_data="car:p:2")],
        [InlineKeyboardButton(text="📊 Analytics Engineer", callback_data="car:p:3")],
        [InlineKeyboardButton(text="🧠 IA-Ops Specialist", callback_data="car:p:4")],
        [InlineKeyboardButton(text="🎯 SDR Técnico B2B", callback_data="car:p:5")],
        [InlineKeyboardButton(text="🔙 Voltar ao Menu Principal", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
```

### 6.2. Visualização dos Detalhes da Profissão (`car:p:<pid>`)
```python
@dp.callback_query(F.data.startswith("car:p:"))
async def callback_carreira_profile(callback: CallbackQuery):
    await callback.answer()
    pid = callback.data.split(":")[-1]
    prof = CAREER_PROFILES.get(pid)
    if not prof:
        return
        
    tools_str = ", ".join(prof["tools"])
    msg = (
        f"🎓 *{prof['title']}*\n"
        f"_{prof['subtitle']}_\n\n"
        f"📝 *Sobre a Profissão:*\n{prof['summary']}\n\n"
        f"💰 *Média Salarial:*\n• 🇧🇷 Brasil: `{prof['salary_br']}`\n• 🌎 Gringo/Remoto: `{prof['salary_usd']}`\n\n"
        f"🛠️ *Ferramentas Chave:*\n_{tools_str}_\n\n"
        f"O que deseja fazer agora?"
    )
    
    buttons = [
        [InlineKeyboardButton(text="🗺️ Ver Trilha & Roadmap", callback_data=f"car:r:{pid}")],
        [InlineKeyboardButton(text="🔍 Buscar Vagas Desta Carreira", callback_data=f"car:j:{pid}")],
        [InlineKeyboardButton(text="🔙 Voltar às Carreiras", callback_data="car:main")]
    ]
    await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")
```

### 6.3. Visualização e Toggle da Trilha / Checklist (`car:r:<pid>` e `car:t:<pid>:<step>`)
```python
# Armazenamento simples em memória para estado de progresso por usuário
user_career_progress = {} # { chat_id: { pid: [step_indices] } }

@dp.callback_query(F.data.startswith("car:r:"))
async def callback_carreira_roadmap(callback: CallbackQuery):
    await callback.answer()
    pid = callback.data.split(":")[-1]
    chat_id = str(callback.message.chat.id)
    await render_roadmap_view(callback.message, chat_id, pid, is_edit=True)

@dp.callback_query(F.data.startswith("car:t:"))
async def callback_carreira_toggle(callback: CallbackQuery):
    _, _, pid, step_idx = callback.data.split(":")
    step_idx = int(step_idx)
    chat_id = str(callback.message.chat.id)
    
    if chat_id not in user_career_progress:
        user_career_progress[chat_id] = {}
    if pid not in user_career_progress[chat_id]:
        user_career_progress[chat_id][pid] = set()
        
    if step_idx in user_career_progress[chat_id][pid]:
        user_career_progress[chat_id][pid].remove(step_idx)
        await callback.answer("Etapa desmarcada!")
    else:
        user_career_progress[chat_id][pid].add(step_idx)
        await callback.answer("Etapa concluída! 🎉")
        
    await render_roadmap_view(callback.message, chat_id, pid, is_edit=True)

async def render_roadmap_view(message: types.Message, chat_id: str, pid: str, is_edit: bool = False):
    prof = CAREER_PROFILES.get(pid)
    if not prof: return
    
    user_done = user_career_progress.get(chat_id, {}).get(pid, set())
    total_steps = len(prof["steps"])
    done_count = len(user_done)
    percent = int((done_count / total_steps) * 100) if total_steps > 0 else 0
    
    msg = (
        f"🗺️ *Roadmap: {prof['title']}*\n"
        f"Progresso: *{percent}%* ({done_count}/{total_steps} etapas concluidas)\n\n"
        f"Clique nos botões abaixo para marcar/desmarcar as etapas conforme avança na sua formação:"
    )
    
    buttons = []
    for idx, step_text in enumerate(prof["steps"]):
        is_done = idx in user_done
        icon = "✅" if is_done else "⬜"
        # Garante texto curto no botão
        btn_text = f"{icon} {step_text[:35]}..." if len(step_text) > 35 else f"{icon} {step_text}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"car:t:{pid}:{idx}")])
        
    buttons.append([InlineKeyboardButton(text="🔍 Buscar Vagas Desta Carreira", callback_data=f"car:j:{pid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Voltar aos Detalhes", callback_data=f"car:p:{pid}")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    if is_edit:
        await message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")
    else:
        await message.answer(msg, reply_markup=markup, parse_mode="Markdown")
```

### 6.4. Execução da Busca Direta de Vagas (`car:j:<pid>`)
```python
@dp.callback_query(F.data.startswith("car:j:"))
async def callback_carreira_job_search(callback: CallbackQuery):
    await callback.answer()
    pid = callback.data.split(":")[-1]
    prof = CAREER_PROFILES.get(pid)
    if not prof: return
    
    kw = prof["search_kw"]
    await callback.message.answer(f"🚀 *Disparando caçada de vagas para: {prof['title']} ({kw})*...", parse_mode="Markdown")
    await _do_hunt(kw, callback.message, callback=callback)
```

---

## 7. Matriz de Verificação & Validação
Para garantir que a integração atenda a todos os requisitos sem gerar efeitos colaterais:

1. **Validação de Tamanho do `callback_data`**:
   - `car:main` (8B), `car:p:1` (7B), `car:r:1` (7B), `car:t:1:3` (9B), `car:j:1` (7B).
   - Todos estão drasticamente abaixo do limite de 64 bytes.

2. **Validação de Limite de Botões por Tela**:
   - Menu Principal de Carreiras: 6 botões.
   - Detalhes da Profissão: 3 botões.
   - Roadmap Interativo: 6 botões (4 etapas + 2 de navegação).
   - Nenhuma tela excede o limite máximo de 15 botões.

3. **Validação de Retrocompatibilidade**:
   - O fluxo de caça de vagas (`hunt_menu`, `modo_*`, `nicho_*`, `mega_iniciantes`) e as opções de configurações permanecem inalterados.
   - `show_main_menu` e `get_main_menu_markup()` preservam todas as opções anteriores.

---

## 8. Conclusão
A arquitetura proposta para a **Trilha de Carreiras** é altamente escalável, 100% compatível com as regras de `callback_data` e botões do Telegram, e entrega valor educacional e prático imediato para os usuários do bot.
