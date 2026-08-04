import json
import requests
import sys

# Configurações do Ollama Local
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "qwen2.5:7b"


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

    payload = {
        "model": MODELO,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False,
        "options": {
            "temperature": 0.4,  # Baixa temperatura para evitar alucinações técnicas
            "top_p": 0.9,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"Erro ao conectar ao Ollama local (localhost:11434): {str(e)}\nCertifique-se de que o Ollama está rodando ('ollama run qwen2.5:7b')."


if __name__ == "__main__":
    print("==================================================")
    print("   ASSISTENTE DE PROPOSTAS WORKANA (OLLAMA LOCAL) ")
    print("   Modelo: Qwen 2.5 7B Instruct (qwen2.5:7b)      ")
    print("==================================================")
    
    if len(sys.argv) > 1:
        projeto = " ".join(sys.argv[1:])
    else:
        projeto = input("\nCole a descrição completa do projeto da Workana aqui:\n\n")

    if projeto.strip():
        print("\nGerando proposta estratégica B2B com Qwen 2.5...\n" + "-" * 50)
        proposta = gerar_proposta_workana(projeto)
        print(proposta)
        print("-" * 50)
    else:
        print("Descrição vazia. Encerrando.")
