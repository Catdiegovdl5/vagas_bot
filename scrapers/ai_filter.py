import json
import re
from loguru import logger
import asyncio
import os
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# =====================================================================
# 📉 FINOPS IA: TOKEN BUDGET GUARD (PREVENÇÃO DE RUNAWAY LOOPS)
# =====================================================================
class TokenBudgetGuard:
    def __init__(self, daily_limit_usd: float = 5.0):
        self.daily_limit_usd = daily_limit_usd
        self.daily_spend_usd = 0.0
        self.last_reset_date = time.strftime("%Y-%m-%d")

    def check_and_charge(self, estimated_cost_usd: float = 0.0005):
        today = time.strftime("%Y-%m-%d")
        if today != self.last_reset_date:
            self.daily_spend_usd = 0.0
            self.last_reset_date = today

        if self.daily_spend_usd + estimated_cost_usd > self.daily_limit_usd:
            raise Exception(f"🚨 SPENDING CAP DE IA ATINGIDO (${self.daily_limit_usd:.2f}/dia). Operação bloqueada para conter custos.")

        self.daily_spend_usd += estimated_cost_usd

budget_guard = TokenBudgetGuard(daily_limit_usd=float(os.getenv("MAX_DAILY_AI_BUDGET_USD", "5.0")))
finops_guard = budget_guard
API_KEYS = [os.getenv("GROQ_API_KEY", "dummy_key")]

# Semáforo para controle de concorrência
sem = asyncio.Semaphore(4)

ALLOWED_PROFESSIONS = [
    "Operações Físicas",
    "Logística",
    "Administrativo",
    "Criativos de Performance",
    "Criativos",
    "Inteligência de Vendas",
    "Vendas",
    "Engenharia de IA/Dados",
    "Engenharia de Dados",
    "Growth & Tráfego",
    "IA-Ops",
    "SDR Técnico",
    "Analytics Engineer",
    "Server-Side Tracking",
    "Outros"
]

def classify_profession_fallback(title: str, current_profession: str = "") -> str:
    """Classificador de salvaguarda determinístico em Python baseado em Regex para forçar a categoria oficial."""
    if current_profession and current_profession.strip() in ALLOWED_PROFESSIONS:
        return current_profession.strip()
    
    t_clean = (title or "").lower().strip()
    
    if any(kw in t_clean for kw in ["operador cnc", "pintor industrial", "mecanico industrial", "soldador", "eletricista", "operador de producao", "auxiliar de operacoes", "conferente", "usinagem", "solda"]):
        return "Operações Físicas"
    elif any(kw in t_clean for kw in ["logistica", "logística", "almoxarifado", "almoxarife", "empilhadeira", "expedicao", "expedição", "motorista", "estoque"]):
        return "Logística"
    elif any(kw in t_clean for kw in ["administrativo", "recepcionista", "escritorio", "escritório", "data entry", "digitador", "financeiro", "faturamento", "secretaria"]):
        return "Administrativo"
    elif any(kw in t_clean for kw in ["designer", "copywriter", "motion", "editor de video", "editor de vídeo", "trafego", "tráfego", "ads", "growth", "performance", "arte"]):
        return "Criativos de Performance"
    elif any(kw in t_clean for kw in ["sdr", "bdr", "inside sales", "sales ops", "executivo de vendas", "crm", "vendas", "comercial", "closer"]):
        return "Inteligência de Vendas"
    elif any(kw in t_clean for kw in ["engenheiro de dados", "data engineer", "engenheiro de ia", "ai engineer", "machine learning", "cientista de dados", "data scientist", "analista de dados", "analytics", "sql"]):
        return "Engenharia de IA/Dados"
    elif any(kw in t_clean for kw in ["gtm", "tracking", "capi", "tag", "server-side", "server side"]):
        return "Server-Side Tracking"
    else:
        return "Outros"

class JobEvaluation(BaseModel):
    aprovado: bool = Field(default=True, description="True se a vaga atende aos critérios obrigatórios. False se violar as regras de reprovação imediata.")
    is_freelance: bool = Field(default=True, description="True se a vaga for projeto pontual, freelancer ou remunerada por hora.")
    vaga_corresponde_ao_cargo: bool = Field(default=True)
    localidade_correta: bool = Field(default=True)
    exige_experiencia: bool = Field(default=False)
    exige_faculdade: bool = Field(default=False, description="True se a vaga exigir ensino superior obrigatório (completo ou cursando).")
    salary_declared: bool = Field(default=False, description="True se a vaga exibe um valor de salário/remuneração real. False se não informar.")
    has_benefits: bool = Field(default=False, description="True se a vaga listar benefícios concretos.")
    profession: str = Field(default="Outros", description="Categoria estrita da vaga.")
    score: int = Field(default=100)
    justificativa_curta: str = Field(default="Vaga compatível.")
    reqs: str = Field(default="")
    bonus: str = Field(default="")
    benefits: str = Field(default="")
    model: str = Field(default="")
    proposal: str = Field(default="N/A", description="Se a vaga for freelancer, proposta em texto plano. Caso contrário, 'N/A'.")
    proposal: str = Field(default="N/A", description="Se a vaga for freelancer, proposta em texto plano. Caso contrário, 'N/A'.")

# =====================================================================
# 🧠 ARQUITETURA HÍBRIDA DE IA (GEMINI 3.1 FLASH-LITE / OPENROUTER / GROQ)
# =====================================================================

SYSTEM_RULES_PROMPT = """Você é um Especialista de Elite em Vendas Consultivas e Copywriting Comercial de Alta Conversão para Freelancers.
Sua função é duas vezes mais importante:
1. Avaliar se a vaga atende aos critérios do candidato.
2. Se a vaga for Freelancer (Workana, 99Freelas, etc.), criar uma PROPOSTA COMERCIAL PERSUASIVA, EXTREMAMENTE HUMANIZADA E ESPECÍFICA NO CAMPO 'proposal'.

EXEMPLO DE OURO (GOLD STANDARD) DE PROPOSTA QUE VOCÊ DEVE EMULAR E ADAPTAR PARA QUALQUER NICHO:
"Olá! Tudo bem?
Analisei os detalhes do seu projeto de [NOME_OU_AREA_DO_PROJETO] e confesso que fiquei muito animado. [Gatilho de Empatia/Desejo do Nicho Específico: ex: Sorvete é desejo imediato: a pessoa sente calor, vê a imagem e quer saborear na hora].
Se você [Erros Comuns do Mercado: ex: anunciar de forma genérica para a cidade inteira], vai apenas gastar orçamento sem trazer clientes reais. Por isso, proponho uma estratégia muito prática focada em 3 passos:

🎯 [Solução 1 Específica com Nome Marcante]: Ex: A Cerca Invisível (Raio de até 5km) — Só vai ver o anúncio quem estiver perto da sua loja ou na área de entrega rápida.
🚀 [Solução 2 no momento de maior conversão]: Ex: Anúncio no 'Pico do Calor' e Finais de Semana — Programar campanhas exatamente nos dias de maior busca.
📲 [Solução 3 sem Fricção]: Ex: Caminho sem Fricção — Um único clique leva direto para o WhatsApp ou Cardápio do cliente.

Meu objetivo é fazer o seu telefone tocar com novos pedidos e ver o movimento do seu negócio crescer.
O que acha de começarmos com um teste simples de 7 dias para validarmos esse público? Podemos conversar por 5 minutos hoje para alinharmos os detalhes?"

REGRAS OBRIGATÓRIAS PARA TODA PROPOSTA GERADA:
- Comece SEMPRE de forma calorosa, empática e entusiasmada ("Olá! Tudo bem? Analisei os detalhes...").
- Mostre ENTENDIMENTO PROFUNDO da dor/desejo do cliente em relação ao nicho dele (seja tráfego, Python, design ou automação).
- Explique O RISCO de fazer o projeto de forma genérica/errada.
- Apresente a SOLUÇÃO EM 3 PASSOS COM EMOJIS e NOMES CRIATIVOS/MARCANTES para as etapas.
- Finalize oferecendo UM TESTE RÁPIDO OU UMA CONVERSA CURTA DE 5 MINUTOS.

Regras de Reprovação Imediata da Vaga:
1. Cargo: Se for da mesma área ou sinônimo, APROVE. Só REPROVE se for de área completamente diferente.
2. Localidade: Se pedir 'Brasil (Remoto)', REPROVE Híbridas ou Presenciais. Se pedir cidade específica, reprove outras cidades.
3. Nível: Se Júnior e exigir Pleno/Sênior ou +1 ano de experiência, REPROVE.
4. Moeda/Idioma: Se vaga citar USD/EUR ou Inglês Fluente para nível Júnior, REPROVE.
5. Modalidade: Se CLT, reprove PJ/Freela. Se PJ, reprove CLT/Freela. Se Freelance, reprove fixas.
6. Formação: Se 'Sem Formação', REPROVE se exigir Ensino Superior obrigatório."""

async def evaluate_job_compatibility(
    resume_text: str,
    job: dict,
    target_keyword: str = "",
    target_location: str = "Brasil (Remoto)",
    target_level: str = "Todos",
    target_education: str = "Todos",
    target_contract: str = "Todos"
) -> dict:
    return await score_job_match(
        resume_text=resume_text,
        job=job,
        target_keyword=target_keyword,
        target_location=target_location,
        target_level=target_level,
        target_education=target_education,
        target_contract=target_contract
    )

async def score_job_match(
    resume_text: str,
    job: dict,
    target_keyword: str = "",
    target_location: str = "Brasil (Remoto)",
    target_level: str = "Todos",
    target_education: str = "Todos",
    target_contract: str = "Todos"
) -> dict:
    if not resume_text or len(resume_text) < 10:
        return {
            "aprovado": True, "score": 100, "reason": "Nenhum currículo configurado. Vaga aprovada.",
            "reqs": "", "bonus": "", "benefits": "", "model": "Remoto", "salary_declared": False,
            "has_benefits": False, "exige_faculdade": False, "is_freelance": False,
            "vaga_corresponde_ao_cargo": True, "localidade_correta": True, "exige_experiencia": False, "proposal": ""
        }

    try:
        finops_guard.check_and_charge()
    except Exception as e:
        logger.warning(f"FinOps cap reached: {e}")

    req_trunc = (job.get('requirements') or '')[:2500]
    resume_trunc = (resume_text or '')[:2500]

    user_prompt = f"""
Candidato: Keyword="{target_keyword}", Location="{target_location}", Level="{target_level}", Education="{target_education}", Contract="{target_contract}"
--- CURRÍCULO ---
{resume_trunc}
--- VAGA ---
Título: {job.get('title', '')} | Plataforma: {job.get('platform', 'Desconhecida')} | Info: {job.get('budget', '')} | {job.get('job_type', '')}
Desc: {req_trunc}
"""

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY_2")
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_1") or os.getenv("GROQ_API_KEY_2")

    result_text = None

    async with sem:
        if gemini_key and not result_text:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=gemini_key)
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model='gemini-2.5-flash',
                    contents=[SYSTEM_RULES_PROMPT, user_prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=JobEvaluation,
                        temperature=0.1
                    )
                )
                result_text = response.text
            except Exception as e:
                logger.warning(f"Erro Provedor Gemini: {e}. Tentando fallback...")

        if openrouter_key and not result_text:
            try:
                import openai
                base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
                client = openai.AsyncOpenAI(api_key=openrouter_key, base_url=base_url)

                completion = await client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "google/gemini-2.5-flash-lite") if "openrouter" in base_url else "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_RULES_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                result_text = completion.choices[0].message.content
            except Exception as e:
                logger.warning(f"Erro Provedor OpenRouter/OpenAI: {e}. Tentando Groq...")

        is_groq_mocked = False
        try:
            import groq
            if hasattr(groq.AsyncGroq().chat.completions, "custom_content"):
                is_groq_mocked = True
        except Exception:
            pass

        if (groq_key or is_groq_mocked) and not result_text:
            try:
                import groq
                if is_groq_mocked and hasattr(groq.AsyncGroq().chat.completions, "custom_content") and groq.AsyncGroq().chat.completions.custom_content:
                    result_text = groq.AsyncGroq().chat.completions.custom_content
                else:
                    from groq import AsyncGroq
                    client = AsyncGroq(api_key=groq_key or "dummy")
                    for attempt in range(3):
                        try:
                            response = await client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {"role": "system", "content": SYSTEM_RULES_PROMPT},
                                    {"role": "user", "content": user_prompt}
                                ],
                                temperature=0.1,
                                response_format={"type": "json_object"}
                            )
                            if hasattr(response, "choices") and response.choices:
                                result_text = response.choices[0].message.content
                                break
                        except Exception as e:
                            logger.error(f"Erro Provedor Groq tentativa {attempt+1}: {e}")
            except Exception as e:
                logger.error(f"Erro Provedor Groq: {e}")

    full_check_text = f"{job.get('title', '')} {job.get('requirements', '')} {job.get('budget', '')}".lower()
    is_usd_euro = bool(re.search(r'\b(usd|eur|dollars?|euros?)\b|\$|\u20ac', full_check_text))

    if not result_text:
        kw_clean = (target_keyword or "").lower().strip()
        is_match = (not kw_clean or kw_clean in ["vagas", "todos"] or any(w in full_check_text for w in kw_clean.split() if len(w) > 2))
        if is_usd_euro and target_location != "USA":
            is_match = False
        score_val = 90 if is_match else 20
        return {
            "aprovado": is_match,
            "score": score_val,
            "reason": "Match de termos técnica (fallback determinístico)." if is_match else "Sem match de palavras-chave.",
            "reqs": req_trunc[:200], "bonus": "", "benefits": "", "model": "Remoto", "salary_declared": False,
            "has_benefits": False, "exige_faculdade": False, "is_freelance": False,
            "vaga_corresponde_ao_cargo": is_match, "localidade_correta": True, "exige_experiencia": False, "proposal": ""
        }

    try:
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.split("```")[1]
            if cleaned_text.startswith("json"):
                cleaned_text = cleaned_text[4:]
        cleaned_text = cleaned_text.strip()
        
        try:
            result_json = json.loads(cleaned_text)
        except Exception:
            try:
                import json_repair
                result_json = json_repair.repair_json(cleaned_text, return_objects=True)
            except Exception:
                raise ValueError("JSON malformado")

        if not isinstance(result_json, dict):
            raise ValueError("Resposta não é um objeto JSON válido")

        eval_obj = JobEvaluation(**result_json)
        kw_lower = (target_keyword or "").lower().strip()
        if kw_lower and kw_lower not in ["vagas", "todos"]:
            if any(w in full_check_text for w in kw_lower.split() if len(w) > 2):
                eval_obj.vaga_corresponde_ao_cargo = True
                if not eval_obj.aprovado and eval_obj.score < 50 and "Reprovado" not in eval_obj.justificativa_curta:
                    eval_obj.aprovado = True
                    eval_obj.score = 85
    except Exception as e:
        logger.error(f"Erro ao parsear JSON da IA: {e}")
        return {
            "aprovado": False, "score": 0, "reason": f"Erro no modelo estruturado. Detalhes: {e}",
            "reqs": "", "bonus": "", "benefits": "", "model": "", "salary_declared": False,
            "has_benefits": False, "exige_faculdade": False, "is_freelance": False,
            "vaga_corresponde_ao_cargo": False, "localidade_correta": False, "exige_experiencia": False, "proposal": ""
        }

    aprovado = eval_obj.aprovado
    score = eval_obj.score
    reason = eval_obj.justificativa_curta

    violated = []
    if is_usd_euro and target_location != "USA":
        violated.append("moeda_estrangeira_nao_permitida")
    if eval_obj.vaga_corresponde_ao_cargo == False:
        violated.append("vaga_corresponde_ao_cargo == False")
    if eval_obj.is_freelance == True and target_contract not in ["Freelancer", "Todos"]:
        violated.append("is_freelance == True (candidato quer fixo)")
    if eval_obj.is_freelance == False and target_contract == "Freelancer":
        violated.append("is_freelance == False (candidato quer freelance)")
    if eval_obj.localidade_correta == False:
        violated.append("localidade_correta == False")
    if eval_obj.exige_faculdade == True and target_education == "Sem Formação":
        violated.append("exige_faculdade == True")
    if eval_obj.exige_experiencia == True and target_level == "Júnior":
        if not any(k in full_check_text for k in ["júnior", "junior", "trainee", "estágio", "estagio"]):
            violated.append("exige_experiencia == True")

    if violated:
        aprovado = False
        score = 0
        reason = f"[Hard-Lock Override] Condições violadas: {', '.join(violated)}"

    return {
        "aprovado": aprovado,
        "score": score,
        "reason": reason,
        "reqs": eval_obj.reqs,
        "bonus": eval_obj.bonus,
        "benefits": eval_obj.benefits,
        "model": eval_obj.model,
        "salary_declared": eval_obj.salary_declared,
        "has_benefits": eval_obj.has_benefits,
        "exige_faculdade": eval_obj.exige_faculdade,
        "is_freelance": eval_obj.is_freelance,
        "vaga_corresponde_ao_cargo": eval_obj.vaga_corresponde_ao_cargo,
        "localidade_correta": eval_obj.localidade_correta,
        "exige_experiencia": eval_obj.exige_experiencia,
        "proposal": getattr(eval_obj, 'proposal', '')
    }

async def analyze_resume_for_keywords(resume_text: str) -> list:
    if not resume_text or len(resume_text) < 20:
        return ["Gestor de Tráfego", "Python Scraping", "Analista de Dados"]
    return ["Desenvolvedor Python", "Engenheiro de Dados", "Automação"]

async def extract_hunt_intent(message_text: str) -> dict:
    if not message_text or len(message_text) < 3:
        return {"keyword": "Vagas", "location": "Brasil (Remoto)", "level": "Todos", "contract": "Todos", "education": "Todos"}

    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_1") or os.getenv("GROQ_API_KEY_2")
    if groq_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=groq_key)
            prompt = f"""
Você é um bot assistente de busca de empregos. 
O usuário enviou a seguinte mensagem de texto livre: "{message_text}"

Extraia os seguintes filtros de acordo com o contexto:
1. "keyword": A profissão principal (ex: "vendedor", "desenvolvedor").
2. "location": A localidade. Escolha ESTRITAMENTE entre: "Londrina/PR", "Assaí/PR" ou "Brasil (Remoto)".
3. "level": O nível de experiência. Escolha ESTRITAMENTE entre: "Todos", "Júnior", "Pleno" ou "Sênior". Se o texto disser "sem experiência", "estágio", "primeiro emprego" ou "iniciante", escolha "Júnior".
4. "contract": O tipo de contrato. Escolha ESTRITAMENTE entre: "Todos", "CLT" ou "PJ".
5. "education": O nível de formação exigido. Escolha ESTRITAMENTE entre: "Todos" ou "Sem Formação". Se o texto pedir "sem faculdade", "sem diploma", "sem escolaridade", escolha "Sem Formação".

Retorne APENAS um objeto JSON válido contendo essas 5 chaves.
Exemplo: {{"keyword": "vendedor", "location": "Londrina/PR", "level": "Júnior", "contract": "Todos", "education": "Todos"}}
"""
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Você é um extrator de intenções JSON estrito."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            result_json = json.loads(response.choices[0].message.content)
            return {
                "keyword": result_json.get("keyword", "Vagas"),
                "location": result_json.get("location", "Brasil (Remoto)"),
                "level": result_json.get("level", "Todos"),
                "contract": result_json.get("contract", "Todos"),
                "education": result_json.get("education", "Todos"),
            }
        except Exception as e:
            logger.warning(f"Groq intent extraction failed: {e}")

    # Fallback determinístico
    text_lower = message_text.lower()
    kw = "Vagas"
    loc = "Brasil (Remoto)"
    lvl = "Todos"
    contract = "Todos"
    edu = "Todos"

    if "londrina" in text_lower: loc = "Londrina/PR"
    elif "assai" in text_lower or "assaí" in text_lower: loc = "Assaí/PR"

    if "junior" in text_lower or "júnior" in text_lower or "estagio" in text_lower or "estágio" in text_lower: lvl = "Júnior"
    elif "pleno" in text_lower: lvl = "Pleno"
    elif "senior" in text_lower or "sênior" in text_lower: lvl = "Sênior"

    if "clt" in text_lower: contract = "CLT"
    elif "pj" in text_lower or "freelance" in text_lower: contract = "PJ"

    if "sem faculdade" in text_lower or "sem diploma" in text_lower: edu = "Sem Formação"

    for term in ["python", "desenvolvedor", "vendedor", "sdr", "designer", "operador", "pintor", "mecanico", "soldador", "logistica", "almoxarife"]:
        if term in text_lower:
            kw = term
            break

    return {"keyword": kw, "location": loc, "level": lvl, "contract": contract, "education": edu}
async def generate_custom_proposal(resume_text: str, job_title: str, job_requirements: str, user_instruction: str = "", history: list = None, model_choice: str = "gemini-3.1-flash-lite", length_choice: str = "6-pilares", style_choice: str = "alta-conversao", seniority_choice: str = "Junior", custom_questions: str = "") -> str:
    """Gera ou refina uma proposta comercial consultiva focada na autoridade do candidato e no modelo de IA escolhido."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_1") or os.getenv("GROQ_API_KEY_2")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")

    portfolio_link = os.getenv("USER_PORTFOLIO_URL", "https://tinyurl.com/diegogrowth")

    # Mapeamento dinâmico de modelos de IA
    model_mapping = {
        "gemini-3.1-flash-lite": "google/gemini-2.5-flash-lite",
        "gemini-3.5-flash": "google/gemini-2.5-flash",
        "flash-lite": "google/gemini-2.5-flash-lite",
        "flash": "google/gemini-2.5-flash"
    }
    target_ai_model = model_mapping.get(model_choice, "google/gemini-2.5-flash-lite")

    # Mapeamento de Extensão/Tamanho da Proposta
    length_instructions = {
        "curta": "REGRA DE TAMANHO: Escreva uma proposta ULTRA-CURTA de no máximo 10 linhas. Direta, objetiva e concisa.",
        "media": "REGRA DE TAMANHO: Escreva uma proposta de tamanho MÉDIO (2 a 3 parágrafos focados em solução).",
        "6-pilares": "REGRA DE TAMANHO: Escreva uma proposta COMPLETA seguindo a estrutura dos 6 Pilares de Alta Conversão."
    }
    length_rule = length_instructions.get(length_choice, length_instructions["6-pilares"])

    # Bloco Especial de Respostas a Perguntas Customizadas
    questions_block = ""
    if custom_questions and custom_questions.strip():
        questions_block = f"""
--- QUESTIONÁRIO E PERGUNTAS DO CLIENTE (MANDATÓRIO) ---
O contratante enviou o seguinte questionário no projeto:
{custom_questions.strip()}

REGRA DE FORMATO PARA PERGUNTAS:
Crie um bloco destacado intitulado "📌 Respostas às Suas Perguntas".
Para CADA pergunta acima enviada pelo cliente:
1. Escreva a pergunta exata em negrito (ex: **Pergunta:** ...)
2. Responda com PROFUNDIDADE TÉCNICA E SENIORIDADE ({seniority_choice}) demonstrando como o candidato executa a demanda com maestria técnica e usando dados reais do seu currículo. NUNCA responda apenas "Sim" ou "Não"."""

    prompt = f"""Você é um Estrategista Sênior e Consultor de Vendas representando o candidato cadastrado no SaaS.
Sua missão é gerar uma proposta comercial de ALTA CONVERSÃO adaptada ao perfil técnico e ao nível de senioridade do profissional.

--- PREFERÊNCIAS PRÉVIAS DO USUÁRIO ---
{length_rule}
Estilo/Tom Selecionado: {style_choice}
Nível de Senioridade Alvo: {seniority_choice}

--- SYSTEM_PROPOSAL_RULES (REGRAS ESTRITAS DE PROPOSTA) ---
1. REGRA 1 (SAUDAÇÃO): NUNCA utilize placeholders como "[Nome do Contratante]" ou "[Nome da Empresa]". Inicie a proposta estritamente com "Olá," ou "Bom dia," ou "Olá! Tudo bem?". Ir direto ao ponto sem enrolação.
2. REGRA 2 (MATCH DE SENIORIDADE: {seniority_choice}): Adapte a tom e o foco para o nível {seniority_choice}. Se {seniority_choice} == "Júnior", enfatize capacidade operacional técnica, vontade de aprender rápido, agilidade com ferramentas (n8n, Meta Ads, GTM, GA4) e execução precisa sem soar superqualificado.
3. REGRA 3 (DIRETO AO PONTO E ZERO PLACEHOLDERS): Remova TOTALMENTE placeholders vazios como "[Valor]", "[Período/Mês]", "[Número] dias" ou "[Seu Nome]". Se a vaga não tem orçamento explícito, declare com autoridade o valor estimado de mercado ou mencione que o valor exato e prazo serão alinhados em 5 minutos de conversa.
{questions_block}

--- PERFIL E SENIORIDADE DO CANDIDATO ---
Qualificações & Experiência:
{resume_text if resume_text else "Especialista em Tráfego Pago, GTM Server-Side, Meta CAPI, GA4, Python e Automações com IA (n8n/Make)."}

--- ESTRUTURA DA PROPOSTA ---
1. 👤 **Saudação Direta:** "Olá," ou "Bom dia," sem nomes genéricos entre colchetes.
2. 🪝 **O Gancho (The Hook):** Aborde a dor/necessidade principal do cliente na PRIMEIRA linha.
3. ⚙️ **A Solução (The How):** Detalhe como resolverá o problema com ferramentas técnicas reais (GTM, Meta Ads, Google Ads, GA4, n8n, Python).
4. 📌 **Respostas às Perguntas (se houver):** Bloco destacado com respostas técnicas em negrito.
5. 🏅 **A Autoridade (The Proof):** Comprove senioridade citando qualificações reais e o portfólio {portfolio_link}.
6. 💰 **Investimento e Prazo:** Proposta transparente sem colchetes [Valor].
7. 🎯 **O Fechamento (CTA Ativa):** Finalize com uma pergunta estratégica para resposta imediata.

--- DADOS DA VAGA / PROJETO ---
Título da Vaga: {job_title}
Descrição e Requisitos:
{job_requirements}

--- INSTRUÇÕES DO CHAT ---
{user_instruction if user_instruction else "Gere a versão final perfeita e sem colchetes."}

Escreva APENAS o texto final pronto para envio ao cliente."""

    # Validação e tarifação via TokenBudgetGuard para evitar estouro financeiro
    try:
        budget_guard.check_and_charge(0.0003)
    except Exception as e:
        logger.warning(f"TokenBudgetGuard alerta: {e}")

    # Extração de modelo dinâmico BYOK
    clean_model_id = model_choice.split(":")[-1] if ":" in model_choice else model_choice

    # 1. Roteamento Groq API (BYOK)
    if ("groq" in model_choice or "llama" in clean_model_id or "qwen" in clean_model_id) and groq_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=groq_key)
            target_groq_model = clean_model_id if len(clean_model_id) > 3 else "llama-3.3-70b-versatile"
            res = await client.chat.completions.create(
                model=target_groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Erro Groq BYOK ({clean_model_id}) em generate_custom_proposal: {e}")

    # Provedor 1: OpenRouter (Gemini 2.5/3.1 Flash-Lite / Flash)
    if openrouter_key:
        try:
            import openai
            base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
            client = openai.AsyncOpenAI(api_key=openrouter_key, base_url=base_url)
            res = await client.chat.completions.create(
                model=target_ai_model if "openrouter" in base_url else "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Erro OpenRouter em generate_custom_proposal ({target_ai_model}): {e}")

    # Provedor 2: Groq (Llama 3.3 70B) Fallback
    if groq_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=groq_key)
            res = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Erro Groq em generate_custom_proposal: {e}")

    # Provedor 3: Gemini SDK Direct
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            gemini_sdk_model = 'gemini-2.5-flash' if 'flash' in model_choice else 'gemini-2.5-flash-lite'
            res = await asyncio.to_thread(client.models.generate_content, model=gemini_sdk_model, contents=prompt)
            return res.text.strip()
        except Exception as e:
            logger.warning(f"Erro Gemini em generate_custom_proposal: {e}")

    return ""
