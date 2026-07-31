import asyncio
import traceback
import datetime
from scrapers import catho, linkedin, gupy, indeed, infojobs, jooble

SCRAPERS = {
    "Catho": catho,
    "LinkedIn": linkedin,
    "Gupy": gupy,
    "Indeed": indeed,
    "InfoJobs": infojobs,
    "Jooble": jooble,
}

async def rodar_qa():
    relatorio_nome = f"relatorio_erros_qa_{datetime.date.today()}.txt"
    with open(relatorio_nome, "w", encoding="utf-8") as f:
        f.write(f"=== RELATÓRIO DE TESTES E ERROS QA - {datetime.datetime.now()} ===\n\n")
        for nome, modulo in SCRAPERS.items():
            f.write(f"[*] Testando Scraper: {nome}...\n")
            try:
                if hasattr(modulo, "scrape"):
                    if asyncio.iscoroutinefunction(modulo.scrape):
                        vagas = await modulo.scrape(keyword="Python", location="Brasil")
                    else:
                        vagas = modulo.scrape("Python", "Brasil")
                    f.write(f"  [SUCESSO] Vagas encontradas: {len(vagas or [])}\n\n")
            except Exception as e:
                f.write(f"  [FALHA / ERRO DETECTADO]: {e}\n")
                f.write(f"  Traceback:\n{traceback.format_exc()}\n")
            f.write("-" * 60 + "\n\n")
    print(f"Relatório de QA gerado com sucesso em: {relatorio_nome}")

if __name__ == "__main__":
    asyncio.run(rodar_qa())
