import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: Add higher_terms block to iniciantes_tudo
old_iniciantes_logic = '''        # Não exige a ausência de termos senior/pleno para não bloquear vagas ambíguas
        is_ganhar_exp = has_target_exp
        
        if not (is_aprendiz or is_ganhar_exp):
            return False'''

new_iniciantes_logic = '''        is_ganhar_exp = has_target_exp
        if not (is_aprendiz or is_ganhar_exp):
            return False
            
        # Bloqueia vagas claramente sênior/pleno
        higher_terms = ["pleno", "senior", "sr", "head", "lead", "gerente", "coordenador"]
        if any(match_exact_word(title_norm, w) for w in higher_terms):
            return False'''

text = text.replace(old_iniciantes_logic, new_iniciantes_logic)

# Fix 2: Require keyword match for ganhar experiencia unless it's Jovem Aprendiz
old_bypass = '''    # Para modos de iniciante, o filtro de senioridade já validou a vaga.
    # Pular a verificação de co-ocorrência de keyword para não bloquear vagas de Jovem Aprendiz
    # que não mencionam a profissão exata buscada.
    if user_level in ('ganhar experiencia', 'iniciantes tudo', 'iniciantes stuff', 'jovem aprendiz'):
        return True'''

new_bypass = '''    # Para Jovem Aprendiz explícito, pulamos o filtro de keyword pois a vaga é muito genérica
    is_jovem_aprendiz_now = any(match_exact_word(full_text, w) for w in aprendiz_terms)
    if is_jovem_aprendiz_now and user_level in ('ganhar experiencia', 'iniciantes tudo', 'iniciantes stuff', 'jovem aprendiz'):
        return True'''

text = text.replace(old_bypass, new_bypass)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated bot.py filter logic')
