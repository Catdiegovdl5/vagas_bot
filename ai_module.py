"""
ai_module.py — Motor de IA do Sniper Bot SaaS
Responsável por:
  - Analisar compatibilidade entre perfil de usuário e vaga (score 0-100)
  - Gerar cover letters personalizadas
  - Extrair texto de currículos em PDF
Usa a API da OpenAI (ou Groq como fallback gratuito).
"""
import os
import re
import json
import random
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Pool de Chaves de API (rotação automática para evitar rate limit) ──────
_GROQ_KEYS = [v for k, v in os.environ.items() if k.startswith('GROQ_API_KEY') and v]
_NVIDIA_KEY    = os.environ.get('NVIDIA_API_KEY', '')
_OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY', '')
_GEMINI_KEYS   = [v for k, v in os.environ.items() if k.startswith('GEMINI_API_KEY') and v]
_OPENAI_KEY    = os.environ.get('OPENAI_API_KEY', '')

def _get_groq_key() -> str:
    """Retorna uma chave Groq aleatória do pool para distribuir a carga."""
    return random.choice(_GROQ_KEYS) if _GROQ_KEYS else ''

def _call_groq(prompt: str, max_tokens: int, api_key: str) -> str | None:
    """Tenta uma chamada Groq com a chave fornecida. Retorna None em caso de falha."""
    import requests
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        logger.warning(f"[AI] Groq HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.warning(f"[AI] Groq falhou: {e}")
    return None


def _call_ai(prompt: str, max_tokens: int = 500, user_groq_key: str = "") -> str:
    """
    Chama a IA com fallback automático:
    0. Chave Groq PESSOAL do usuário (prioridade máxima)
    1. Groq pool rotativo (3 chaves gratuitas)
    2. NVIDIA NIM
    3. OpenRouter
    4. Gemini pool rotativo
    5. OpenAI
    6. Fallback local
    """
    import requests

    # 0. Chave pessoal do usuário (prioridade máxima)
    if user_groq_key:
        result = _call_groq(prompt, max_tokens, user_groq_key)
        if result:
            return result

    # 1. Groq (pool rotativo)
    groq_key = _get_groq_key()
    if groq_key:
        result = _call_groq(prompt, max_tokens, groq_key)
        if result:
            return result

    # 2. NVIDIA NIM
    if _NVIDIA_KEY:
        try:
            headers = {"Authorization": f"Bearer {_NVIDIA_KEY}", "Content-Type": "application/json"}
            payload = {"model": "meta/llama3-8b-instruct", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            resp = requests.post("https://integrate.api.nvidia.com/v1/chat/completions",
                                 json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"[AI] NVIDIA NIM falhou: {e}")

    # 3. OpenRouter
    if _OPENROUTER_KEY:
        try:
            headers = {"Authorization": f"Bearer {_OPENROUTER_KEY}", "Content-Type": "application/json",
                       "HTTP-Referer": "https://sniperbot.app", "X-Title": "Sniper Bot"}
            payload = {"model": "meta-llama/llama-3-8b-instruct:free",
                       "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"[AI] OpenRouter falhou: {e}")

    # 4. Gemini (pool rotativo)
    gemini_key = random.choice(_GEMINI_KEYS) if _GEMINI_KEYS else ''
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": max_tokens}}
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            logger.warning(f"[AI] Gemini falhou: {e}")

    # 5. OpenAI (pago)
    if _OPENAI_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=_OPENAI_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens)
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"[AI] OpenAI falhou: {e}")

    # 6. Fallback local
    return _local_fallback(prompt)


def _local_fallback(prompt: str) -> str:
    """Fallback local sem IA: retorna uma análise simplificada baseada em keywords."""
    # Extrai dados do prompt para dar uma resposta mínima funcional
    if "compatibilidade" in prompt.lower() or "score" in prompt.lower():
        return json.dumps({"score": 60, "justification": "Análise local sem IA disponível. Configure OPENAI_API_KEY ou GROQ_API_KEY para análise real."})
    elif "cover letter" in prompt.lower() or "carta" in prompt.lower():
        return "Prezados,\n\nVenho por meio desta manifestar meu interesse na vaga anunciada. Acredito que minhas habilidades e experiências estão alinhadas com os requisitos da posição.\n\nAtenciosamente."
    return "Resposta não disponível. Configure uma chave de API de IA."


# ── Extração de PDF ────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extrai texto de um arquivo PDF em bytes.
    Usa PyPDF2 se disponível, senão tenta pdfplumber.
    """
    # Tenta PyPDF2
    try:
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"[PDF] PyPDF2 falhou: {e}")

    # Tenta pdfplumber
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"[PDF] pdfplumber falhou: {e}")

    return "Não foi possível extrair texto do PDF. Instale: pip install PyPDF2 pdfplumber"


# ── Análise de Compatibilidade ─────────────────────────────

def analyze_compatibility(user_profile: dict, job: dict, user_groq_key: str = "") -> dict:
    """
    Analisa a compatibilidade entre o perfil do usuário e uma vaga.
    Retorna: {"score": int (0-100), "justification": str, "highlights": list}
    """
    profile_text = _build_profile_summary(user_profile)
    job_text = f"Cargo: {job.get('title', '')}\nEmpresa: {job.get('company', '')}\nRequisitos: {job.get('requirements', '')}"

    prompt = f"""Você é um recrutador sênior especialista em RH.
Analise a compatibilidade entre o candidato e a vaga abaixo.

PERFIL DO CANDIDATO:
{profile_text}

VAGA:
{job_text}

Responda SOMENTE com um JSON válido neste formato:
{{"score": <número 0-100>, "justification": "<1-2 frases explicando o score>", "highlights": ["<ponto forte 1>", "<ponto forte 2>"]}}

Score 0-100 onde: 0-39=incompatível, 40-69=compatível parcialmente, 70-89=bom match, 90-100=match perfeito."""

    try:
        raw = _call_ai(prompt, max_tokens=300, user_groq_key=user_groq_key)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return {
                "score": int(data.get("score", 50)),
                "justification": data.get("justification", ""),
                "highlights": data.get("highlights", [])
            }
    except Exception as e:
        logger.warning(f"[AI] Erro ao parsear compatibilidade: {e}")

    return {"score": 50, "justification": "Análise não disponível.", "highlights": []}


def score_emoji(score: int) -> str:
    """Retorna emoji representando o nível de compatibilidade."""
    if score >= 90: return "🔥"
    if score >= 70: return "✅"
    if score >= 40: return "⚠️"
    return "❌"


# ── Gerador de Cover Letter ────────────────────────────────

def generate_cover_letter(user_profile: dict, job: dict, user_groq_key: str = "") -> str:
    """
    Gera uma cover letter personalizada para a vaga.
    Retorna o texto da carta formatado.
    """
    profile_text = _build_profile_summary(user_profile)
    name = user_profile.get('full_name', 'Candidato(a)')
    company = job.get('company', 'a empresa')
    title = job.get('title', 'a vaga')
    requirements = job.get('requirements', '')[:500]

    prompt = f"""Você é um especialista em redação de cartas de apresentação profissionais para o mercado brasileiro.

Escreva uma cover letter PROFISSIONAL e PERSONALIZADA para o seguinte candidato e vaga.

CANDIDATO: {name}
PERFIL:
{profile_text}

VAGA: {title}
EMPRESA: {company}
REQUISITOS: {requirements}

Escreva uma carta em português brasileiro com:
1. Saudação profissional
2. Parágrafo de abertura mencionando o cargo e a empresa pelo nome
3. Parágrafo destacando 2-3 habilidades específicas do perfil que se encaixam nos requisitos
4. Parágrafo de encerramento com call-to-action
5. Assinatura com o nome do candidato

Tom: profissional, confiante, direto. Máximo 250 palavras."""

    return _call_ai(prompt, max_tokens=600, user_groq_key=user_groq_key)


# ── Helpers ────────────────────────────────────────────────

def _build_profile_summary(profile: dict) -> str:
    """Constrói um resumo do perfil para os prompts de IA."""
    parts = []
    if profile.get('full_name'):
        parts.append(f"Nome: {profile['full_name']}")
    if profile.get('skills'):
        parts.append(f"Habilidades: {profile['skills']}")
    if profile.get('experience'):
        parts.append(f"Experiência: {profile['experience']}")
    if profile.get('education'):
        parts.append(f"Educação: {profile['education']}")
    if profile.get('resume_text'):
        # Usa os primeiros 1000 chars do currículo
        parts.append(f"Currículo (resumo):\n{profile['resume_text'][:1000]}")
    return "\n".join(parts) if parts else "Perfil não preenchido."


def has_profile(user_profile: dict) -> bool:
    """Verifica se o usuário tem perfil mínimo preenchido para usar a IA."""
    return bool(
        user_profile.get('resume_text') or
        user_profile.get('skills') or
        user_profile.get('experience')
    )
