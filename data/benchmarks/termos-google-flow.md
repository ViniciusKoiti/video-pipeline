# Termos do Google Flow (vídeo e imagem gerados) — consulta de 2026-11-26

Leitura feita por agente em 2026-11-26, a pedido do dono, das páginas oficiais abaixo. É uma leitura dos termos, não
parecer jurídico. Conta usada: a conta pessoal do dono, plano Google AI **Pro** (o Flow mostra "PRO").

## Páginas lidas

- Get started with Google Flow (FAQ): https://support.google.com/flow/answer/16353333?hl=en
- Manage your data in Google Flow: https://support.google.com/flow/answer/17025472?hl=en
- Where you can use Google Flow: https://support.google.com/flow/answer/16353544?hl=en
- Google Flow models & features: https://support.google.com/flow/answer/16352836?hl=en
- Google Terms of Service (vigência 30/07/2026): https://policies.google.com/terms
- Generative AI Prohibited Use Policy: https://policies.google.com/terms/generative-ai/use-policy
- Service-specific terms: https://policies.google.com/terms/service-specific

Não lidas (redirecionam para outro domínio): a política de privacidade do Flow, o FAQ do labs.google e os termos do
Google One.

## O que dizem

1. **Dono do resultado:** "Google won't claim ownership over that content" (Termos gerais). Os mesmos termos dão ao
   Google uma licença mundial, não exclusiva e gratuita sobre "your content" protegido por propriedade intelectual,
   para operar e melhorar os serviços.
2. **Uso comercial:** o FAQ do Flow responde "posso usar comercialmente?" só com "consulte os Termos de Serviço". Os
   termos não proíbem nem liberam por escrito. Os planos diferem em créditos e recursos, não em direitos declarados.
   Canal monetizado provavelmente conta como "business user" (indenização a favor do Google, teto de
   responsabilidade).
3. **Marca d'água:** todo resultado leva SynthID invisível; a marca visível é um botão (forçada só na Índia, Coreia do
   Sul e Vietnã). Proibido contornar proteções e dizer que o conteúdo foi feito só por humano para enganar.
4. **Automação:** proibido o acesso automatizado que desrespeita instruções de máquina (robots.txt) e o abuso; o Flow
   limita a quantidade de gerações.
5. **Pessoas:** não gera vídeo de pessoas famosas; proibido imitar pessoa real (viva ou morta) sem aviso para enganar.
6. **Treino:** proibido usar o resultado para treinar modelos.
7. **Dados:** com "Ajude a deixar o Flow ainda melhor" ligado, interações e resultados podem ir para melhoria e revisão
   humana (até 18 meses). Na conta do dono ele já estava **desligado** (conferido em 2026-11-26).

## Como o projeto usa

- Ativo `license_id: Generated`, `provider: original`, `media: clip` (emenda de 2026-11-26 da ADR 007), com o
  gerador, o modelo e o projeto do Flow em `origin`, e o prompt e a conferência em `usage_notes`.
- O uso comercial sem liberação escrita é **decisão de risco do dono** (2026-11-26: "pode fazer as três").
- Divulgação de IA na descrição; rótulo de conteúdo sintético no Studio quando a cena parecer real.
- Custo observado: 30 créditos por clipe de 10 s no Omni 1.2 Flash (plano Pro: 1.000 créditos por mês).
