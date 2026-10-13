# Termos do Higgsfield (consulta de 2026-10-10, INCOMPLETA)

Nada foi chamado nem testado; só leitura de páginas públicas. Não há licença registrada: o Higgsfield **não** está
na lista fechada da ADR 007 e nenhum ativo dele pode entrar no render.

## Confirmado na fonte oficial

Fonte: https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api (lida em 2026-10-10).

- API paga por saldo pré-pago em dólar: "Billing is pay-as-you-go from a US dollar balance, and the minimum top-up
  is $5". Vídeo por segundo, imagem por imagem. Sem plano nem assinatura; **sem camada gratuita citada**.
- Uso comercial: "you hold the rights to use your generated content" (base do artigo para produtos comerciais,
  anúncios e trabalho para clientes), nos Terms of Use.
- Arquivos ficam "at least 7 days" depois de criados: baixar para armazenamento próprio.
- Limite: 20 requisições simultâneas por chave.

## Não confirmado

- Termos de uso: `higgsfield.ai/terms` e `/terms-of-use` devolveram 404; o endereço correto não foi achado.
- Preços e créditos dos planos do app: a página `higgsfield.ai/pricing` veio sem conteúdo. Fontes de terceiros
  divergem (US$ 9 a US$ 129 por mês) e **não** valem como registro.
- Uso comercial no plano gratuito do app: só fontes de terceiros dizem que não há; sem confirmação oficial.
- Regras de rótulo de IA, de rosto de pessoas reais e de uso do conteúdo do usuário para treino: não lidas.

## Efeito no projeto

- Custo: qualquer uso da API exige saldo em dólar (mínimo US$ 5), o que quebra a regra de custo zero (§2.1).
  Só com decisão explícita do dono.
- Imagem ou vídeo gerado realista: ilustração, com divulgação de conteúdo alterado (§2.4).
- Para entrar no pipeline: ler os Terms oficiais, registrar licença/ADR e passar pelo gate 3.
