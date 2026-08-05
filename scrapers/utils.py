import urllib.parse
from typing import Optional

def construir_termo_busca(keyword: str = "", category: str = "", seniority: str = "") -> str:
    """Combina palavras-chave, categoria e senioridade sem duplicar termos."""
    partes = []
    
    for item in [keyword, category, seniority]:
        if item and str(item).strip():
            termo = str(item).strip()
            if termo.lower() not in [p.lower() for p in partes] and termo.lower() not in ["todos", "todas", "all"]:
                partes.append(termo)
                
    return " ".join(partes).strip()

def encode_param(texto: Optional[str]) -> str:
    """Codifica parâmetros para inserção segura em URLs."""
    return urllib.parse.quote((texto or "").strip())
