# Original User Request

## Follow-up — 2026-07-08T13:30:12Z

O objetivo é expandir os filtros do Vagas Bot para capturar vagas voltadas ao uso de ferramentas de IA (ChatGPT, Midjourney, Claude, etc.) em áreas menos técnicas e mais focadas em criatividade, marketing, redação, design, animação e geração de imagens/vídeos.

Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot
Integrity mode: benchmark

## Requirements

### R1. Expandir a Lógica de Filtragem (IA Criativa e Operacional)
Você deve modificar a lógica de filtragem (`rules` no arquivo `bot.py` or os dicionários de busca, e qualquer outra parte relevante) para que o bot passe a aprovar vagas para profissionais que **usam** a IA para gerar textos, imagens, vídeos ou campanhas (ex: Copywriter com IA, Designer Midjourney, Videomaker com IA Generativa). A decisão da arquitetura (criar um novo nicho específico no menu ou integrar isso ao nicho de "Especialista em IA Generativa") cabe inteiramente à equipe de agentes.

### R2. Script de Validação Rigorosa
Você deve criar um script de testes independente na raiz do projeto chamado `verify_ai_creative_jobs.py`. O script deve importar a função de validação de vagas do `bot.py` (ou simular a lógica caso ela não possa ser importada diretamente).

## Acceptance Criteria

### Teste de Falsos Positivos e Falsos Negativos
- [ ] O script `verify_ai_creative_jobs.py` deve criar um mock de pelo menos 5 títulos de vagas "criativas com IA" (ex: "Copywriter ChatGPT", "Designer Midjourney", "Editor de Vídeo - IA", etc.) e afirmar matematicamente que o bot **APROVA** todas elas.
- [ ] O script também deve criar um mock de pelo menos 5 títulos de vagas "comuns não relacionadas à IA" (ex: "Desenvolvedor Java", "Analista de RH", "Vendedor", etc.) e afirmar matematicamente que o bot sob esta categoria **REJEITA** todas elas.
- [ ] O script de teste deve rodar com saída 100% verde sem gerar exceções.
