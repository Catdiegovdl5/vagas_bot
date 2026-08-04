import json
import os
import sys
import time
import subprocess
import requests

# Configurações do Ollama Local & Fallback
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "qwen2.5:7b"


def checar_ou_iniciar_ollama() -> bool:
    """Verifica se o servidor Ollama está ativo em localhost:11434. Se não tiver, tenta iniciar em segundo plano."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    print("[Ollama] Tentando iniciar o serviço Ollama em segundo plano...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def gerar_proposta_workana(descricao_projeto: str) -> str:
    system_prompt = (
        "Você é um especialista em vendas B2B e engenharia de software criando propostas comerciais "
        "de alta conversão na plataforma Workana.\n"
        "REGRAS DE REDAÇÃO:\n"
        "1. PROIBIDO saudações genéricas como 'Olá, espero que esteja bem' ou 'Sou o candidato ideal'.\n"
        "2. A primeira frase deve atacar diretamente a dor técnica ou o gargalo citado no projeto.\n"
        "3. Apresente uma solução direta dividida em 3 passos práticos (como será executado).\n"
        "4. Inclua uma pergunta estratégica no final para forçar a resposta do cliente.\n"
        "5. Mantenha tom direto, técnico e focado no Retorno sobre Investimento (ROI).\n"
        "6. Escreva a proposta no mesmo idioma do anúncio (Português ou Inglês)."
    )

    user_prompt = f"Crie uma proposta comercial estratégica para o seguinte projeto da Workana:\n\n{descricao_projeto}"

    # 1. Tenta primeiro via Ollama Local (Qwen 2.5 7B)
    if checar_ou_iniciar_ollama():
        payload = {
            "model": MODELO,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {"temperature": 0.4, "top_p": 0.9},
        }

        try:
            print("[Ollama Local] Gerando proposta com Qwen 2.5 7B...")
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            res = data.get("response", "").strip()
            if res:
                return res
        except Exception as e:
            print(f"[Ollama Warning] Falha na resposta local ({e}). Redirecionando para nuvem...")

    # 2. Fallback Inteligente para Nuvem (Groq / Gemini / OpenAI)
    print("[IA Nuvem] Utilizando motor de IA em nuvem (Groq / Gemini)...")
    try:
        from ai_module import _call_ai
        res_cloud = _call_ai(f"{system_prompt}\n\n{user_prompt}", max_tokens=800)
        if res_cloud:
            return res_cloud
    except Exception as e:
        print(f"[IA Nuvem Warning] {e}")

    return "Não foi possível conectar ao Ollama nem às IAs em nuvem. Verifique suas chaves no .env ou inicie o Ollama com 'ollama run qwen2.5:7b'."


def ler_entrada_multilinha() -> str:
    """Lê todas as linhas coladas pelo usuário até pressionar Enter em linha em branco ou Ctrl+Z."""
    print("\n📋 Cole a descrição completa do projeto da Workana abaixo.")
    print("(Pressione ENTER duas vezes ou ENTER em linha em branco para finalizar):\n")
    print("-" * 60)

    linhas = []
    while True:
        try:
            linha = input()
            if not linha.strip() and linhas:
                break
            linhas.append(linha)
        except EOFError:
            break

    return "\n".join(linhas).strip()


if __name__ == "__main__":
    print("==================================================")
    print("   ASSISTENTE DE PROPOSTAS WORKANA (SNIPER BOT)   ")
    print("   Modelo Principal: Qwen 2.5 7B (Ollama Local)   ")
    print("==================================================")

    if len(sys.argv) > 1:
        projeto = " ".join(sys.argv[1:])
    else:
        projeto = ler_entrada_multilinha()

    if projeto:
        print("\n" + "=" * 60)
        print("🚀 GERANDO PROPOSTA ESTRATÉGICA B2B...")
        print("=" * 60 + "\n")
        proposta = gerar_proposta_workana(projeto)
        print(proposta)
        print("\n" + "=" * 60)
    else:
        print("Nenhuma descrição colada. Encerrando.")
