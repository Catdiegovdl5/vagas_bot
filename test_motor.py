"""
test_motor.py - Teste Automático do Motor de Busca de Vagas
Executa: python test_motor.py
"""
import sys
import unicodedata
import re

# ─────────────────────────────────────────────
# Copiar as funções relevantes do bot para cá
# ─────────────────────────────────────────────
def normalize_str(s):
    if not s: return ""
    s = unicodedata.normalize('NFD', str(s))
    return s.encode('ascii', 'ignore').decode('utf-8').lower()

def match_exact_word(text, word):
    pattern = rf'(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])'
    return bool(re.search(pattern, text))

CO_OCCURRENCE_RULES = {
    "python": [
        ["python", "django", "fastapi", "flask", "scraping"],
        ["desenvolvedor", "developer", "programador", "software", "engineer", "dev",
         "backend", "junior", "estagiario", "pleno", "senior", "assistente", "analista",
         "engenheiro", "dados", "data", "fullstack", "web", "api"]
    ],
    "ia generativa": [
        ["chatgpt", "midjourney", "ia", "ai", "inteligencia artificial", "llm",
         "generative", "generativa", "copilot", "claude", "gemini", "prompt"],
        ["copywriter", "designer", "editor", "gestor", "analista", "marketing",
         "content", "redator", "video", "trafego", "digital", "especialista",
         "desenvolvedor", "developer", "criador"]
    ],
    "ia": [
        ["ia", "ai", "inteligencia artificial", "machine learning", "deep learning",
         "llm", "generativa", "chatgpt", "gemini", "claude", "copilot", "agente", "agent"],
        ["desenvolvedor", "developer", "engenheiro", "engineer", "analista", "analyst",
         "especialista", "specialist", "cientista", "scientist", "pesquisador",
         "arquiteto", "architect", "consultor", "consultant", "gestor", "manager",
         "programador", "programmer", "dev", "tech", "software"]
    ],
    "machine learning": [
        ["machine learning", "ml", "mlops", "deep learning", "redes neurais",
         "tensorflow", "pytorch", "sklearn", "xgboost", "transformers"],
        ["desenvolvedor", "developer", "engenheiro", "engineer", "analista", "analyst",
         "especialista", "specialist", "cientista", "scientist", "pesquisador",
         "arquiteto", "architect", "consultor", "consultant", "dev", "software"]
    ],
    "react": [
        ["react", "reactjs", "nextjs", "frontend", "javascript", "typescript"],
        ["desenvolvedor", "developer", "programador", "software", "engineer", "dev",
         "frontend", "fullstack", "junior", "pleno", "senior"]
    ],
    "rpa": [
        ["rpa", "automacao", "automation", "uipath", "power automate", "blue prism",
         "n8n", "make", "zapier"],
        ["desenvolvedor", "developer", "analista", "engineer", "especialista"]
    ],
    "power bi": [
        ["power bi", "powerbi", "bi", "business intelligence", "tableau", "looker"],
        ["analista", "analyst", "desenvolvedor", "especialista", "consultor"]
    ],
    "administrativo": [
        ["auxiliar", "assistente", "suporte"],
        ["administrativo", "administracao", "adm", "escritorio", "office"]
    ],
}

def check_co_occurrence(text_norm, kw_norm):
    if kw_norm in CO_OCCURRENCE_RULES:
        groups = CO_OCCURRENCE_RULES[kw_norm]
        for group in groups:
            matched_group = False
            for word in group:
                if match_exact_word(text_norm, word):
                    matched_group = True
                    break
            if not matched_group:
                return False
        return True
    # Generic fallback: all significant words present
    words = [w for w in re.split(r'\W+', kw_norm) if len(w) > 2]
    stopwords = {"de","em","com","para","por","sem","sob","sobre","the","and","with","for"}
    significant_words = [w for w in words if w not in stopwords]
    if not significant_words:
        return match_exact_word(text_norm, kw_norm)
    for word in significant_words:
        if not match_exact_word(text_norm, word):
            return False
    return True

def simulate_filter(vaga, keyword):
    title_norm = normalize_str(vaga.get('title', ''))
    reqs_norm = normalize_str(vaga.get('requirements', ''))
    full_text = title_norm + " " + reqs_norm
    kw_norm = normalize_str(keyword)
    return check_co_occurrence(full_text, kw_norm)

# ─────────────────────────────────────────────
# CASOS DE TESTE
# ─────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

# (vaga, keyword, esperado, descricao)
test_cases = [
    # ===== VERDADEIROS POSITIVOS (devem PASSAR) =====
    ({"title": "Desenvolvedor Python Backend", "requirements": "Precisa saber Django e FastAPI"},
     "python", True, "[OK] VP: Dev Python Backend com Django"),

    ({"title": "Analista de Dados Python", "requirements": "SQL, pandas, python, engenharia de dados"},
     "python", True, "[OK] VP: Analista de Dados Python"),

    ({"title": "Especialista em IA Generativa", "requirements": "Experiência com Midjourney, ChatGPT, geração de conteúdo com LLM"},
     "ia generativa", True, "[OK] VP: Especialista IA Generativa"),

    ({"title": "Desenvolvedor React Frontend", "requirements": "Vaga para desenvolvedor react, nextjs, typescript"},
     "react", True, "[OK] VP: Dev React Frontend"),

    ({"title": "Desenvolvedor RPA Automação", "requirements": "UiPath, Power Automate, automação de processos, developer"},
     "rpa", True, "[OK] VP: Desenvolvedor RPA"),

    # ===== FALSOS POSITIVOS - devem ser BLOQUEADOS =====
    ({"title": "Enfermeira com conhecimento em TI", "requirements": "Buscamos enfermeira que saiba python para análises"},
     "python", False, "[BLOQUEAR] FP: Enfermeira com python - DEVE BLOQUEAR"),

    ({"title": "Médico Veterinário Autônomo", "requirements": "Clínica veterinária, atendimento, python para controle de estoque"},
     "python", False, "[BLOQUEAR] FP: Médico vet com python no estoque - DEVE BLOQUEAR"),

    ({"title": "Motorista de Aplicativo Python", "requirements": "Motorista parceiro, CNH categoria B, conhecimento básico em python"},
     "python", False, "[BLOQUEAR] FP: Motorista com python - DEVE BLOQUEAR"),

    ({"title": "Atendente de Lanchonete IA", "requirements": "Funcionário para atendimento ao balcão, IA é nossa empresa"},
     "ia", False, "[BLOQUEAR] FP: Atendente onde 'IA' é nome da empresa - DEVE BLOQUEAR"),

    ({"title": "Costureira para Confecção", "requirements": "Máquina de costura, ia para agulha (incluindo IA na sigla irrelevante)"},
     "ia generativa", False, "[BLOQUEAR] FP: Costureira sem IA generativa - DEVE BLOQUEAR"),

    ({"title": "Balconista de Farmácia React", "requirements": "Atendimento ao cliente, caixa registradora, nosso sistema chama React"},
     "react", False, "[BLOQUEAR] FP: Balconista onde 'React' é nome do sistema - DEVE BLOQUEAR"),

    ({"title": "Repositor de Estoque com PowerBI", "requirements": "Repositor para supermercado, organização de gôndolas, relatórios em Power BI"},
     "power bi", False, "[BLOQUEAR] FP: Repositor com Power BI - DEVE BLOQUEAR"),

    ({"title": "Recepcionista Machine Learning Center", "requirements": "Atendimento presencial na recepção do Machine Learning Center (nome da empresa)"},
     "machine learning", False, "[BLOQUEAR] FP: Recepcionista em empresa cujo nome é ML - DEVE BLOQUEAR"),

    ({"title": "Professor de Ensino Médio", "requirements": "Aulas de matemática e física, python mencionado apenas como exemplos de linguagem"},
     "python", False, "[BLOQUEAR] FP: Professor sem vaga de TI - DEVE BLOQUEAR"),

    ({"title": "Auxiliar de Limpeza RPA Clean", "requirements": "Limpeza de ambientes, empresa chamada RPA Clean, sem automação"},
     "rpa", False, "[BLOQUEAR] FP: Auxiliar limpeza da empresa RPA Clean - DEVE BLOQUEAR"),

    ({"title": "Corretor de Imóveis", "requirements": "Vendas de imóveis, captação de clientes, experiência com React (sistema interno)"},
     "react", False, "[BLOQUEAR] FP: Corretor de imóveis - DEVE BLOQUEAR"),
]

# ─────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("   VAGAS SNIPER BOT — TESTE DO MOTOR DE BUSCA")
print("="*65)

passed = 0
failed = 0
failures = []

for (vaga, keyword, expected, desc) in test_cases:
    result = simulate_filter(vaga, keyword)
    ok = (result == expected)
    if ok:
        passed += 1
        print(f"  {GREEN}PASS{RESET}  {desc}")
    else:
        failed += 1
        label = "LIBEROU (devia BLOQUEAR)" if result else "BLOQUEOU (devia LIBERAR)"
        print(f"  {RED}FAIL{RESET}  {desc}  -> {label}")
        failures.append(desc)

total = passed + failed
fp_cases = [c for c in test_cases if not c[2]]  # esperado=False
fp_blocked = sum(1 for c in fp_cases if not simulate_filter(c[0], c[1]))

print("\n" + "="*65)
print(f"  Resultado: {passed}/{total} testes passaram")
print(f"  Falsos-Positivos bloqueados: {fp_blocked}/{len(fp_cases)} ({100*fp_blocked//len(fp_cases)}%)")

if failed == 0:
    print(f"\n  {GREEN}>> MOTOR APROVADO! 100% dos falsos-positivos bloqueados.{RESET}")
    sys.exit(0)
else:
    print(f"\n  {RED}!!  MOTOR REPROVADO! {failed} teste(s) falharam:{RESET}")
    for f in failures:
        print(f"    -> {f}")
    sys.exit(1)
