import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bot import is_job_relevant

def test_seniority():
    keyword = 'desenvolvedor'

    # Caso 1: Título genérico, descrição crava que é sênior
    # Deve ser REJEITADA se o nível for Júnior.
    job1 = {
        'title': 'Desenvolvedor',
        'requirements': 'Buscamos um dev com experiencia senior.',
        'platform': 'GeekHunter',
        'location': 'Remoto'
    }

    # Caso 2: Título Júnior, descrição menciona sênior casualmente
    # Deve ser APROVADA se o nível for Júnior.
    job2 = {
        'title': 'Desenvolvedor Junior',
        'requirements': 'Você será mentorado por um engenheiro senior.',
        'platform': 'GeekHunter',
        'location': 'Remoto'
    }

    # Caso 3: Título genérico, descrição crava que é Pleno
    # Deve ser APROVADA se o nível for Pleno.
    job3 = {
        'title': 'Analista de Dados',
        'requirements': 'Nivel pleno.',
        'platform': 'GeekHunter',
        'location': 'Remoto'
    }

    print("Testando Caso 1 (esperado: False)...")
    res1 = is_job_relevant(job1, keyword, {'level': 'junior', 'location': 'Remoto', 'contract': 'Todos'})
    print(f"Resultado: {res1} {'[OK]' if not res1 else '[FAIL]'}")

    print("Testando Caso 2 (esperado: True)...")
    res2 = is_job_relevant(job2, keyword, {'level': 'junior', 'location': 'Remoto', 'contract': 'Todos'})
    print(f"Resultado: {res2} {'[OK]' if res2 else '[FAIL]'}")

    print("Testando Caso 3 (esperado: True)...")
    res3 = is_job_relevant(job3, 'analista de dados', {'level': 'pleno', 'location': 'Remoto', 'contract': 'Todos'})
    print(f"Resultado: {res3} {'[OK]' if res3 else '[FAIL]'}")

if __name__ == '__main__':
    test_seniority()
