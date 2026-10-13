# Brief comum: nichos do mercado global (língua inglesa) para vídeos curtos animados que vendem (consulta: 2026-10-07)

Você pesquisa UM nicho para o dono de um projeto de vídeos animados. O dono é brasileiro, desenvolvedor de software, não aparece em câmera e tem orçamento zero. Ele quer saber que nichos do MERCADO GLOBAL (audiência de língua inglesa: EUA, Reino Unido, Canadá, Austrália, Índia etc.) são mais vendáveis com vídeos curtos animados baseados em dados com fonte. Vender para desenvolvedores está FORA (o dono acha muito difícil), então o público do seu nicho não deve ser de programadores. Os resultados de vários pesquisadores vão para uma tabela comparativa: seja honesto sobre o que NÃO conseguiu verificar. Uma conclusão fraca e bem rotulada vale mais do que uma forte e inventada.

## 1. O que a pipeline faz hoje (lido no repositório em 2026-10-07)
- Formato `explainer` em Remotion + motion-kit. Planos tipados em `app/pipeline/schemas.py`.
- Perfil vertical 9:16 (ADR 014): só aceita os planos `photo`, `broll` (foto ou vídeo de banco de imagens), `number` (número grande, com odômetro animado), `keyword` (frase curta, no máximo 8 palavras), `stamp` (selo de data/fonte), `lower_third` (faixa de nome), `compare` (lado a lado, antes/depois, escala) e `chart` (barra, barra horizontal, linha, participação). Citação (com cartão de documento), mapa, linha do tempo, árvore e rede existem em 16:9 mas NÃO em retrato. Sem plano ainda (existem no kit): esteira de etapas (pipeline), medidor (gauge), trecho de código, janela de contexto, grafo animado, marca-texto.
- Apresentador opcional: personagem ilustrado (DiceBear Notionists, licença CC0) numa janela flutuante, boca ligada ao áudio. Não é pessoa em câmera. Legenda queimada.
- Idioma: um por episódio, `en` ou `pt-BR` (ADR 008). Voz em inglês: Kokoro local nos rascunhos; o Gemini TTS final só foi testado em pt-BR neste projeto.
- Ritmo: 2 a 4 s por plano, 25 a 40 s por Reel. Todo número, data ou citação na tela exige uma ficha com fonte (o canal só afirma o que a fonte diz); fontes oficiais de domínio público (governo dos EUA, por exemplo) são as mais fáceis de usar.
- NÃO existe: gravação de tela, demonstração real de produto ou aplicativo, pessoa em câmera, ilustração feita à mão, música e efeitos, export por plataforma, título e capa, upload (a publicação é sempre manual).
- Custo medido de um vídeo de 93 s com 5 rodadas de checagem: ~1,6 milhão de tokens e ~1 h 31 de agentes. Horas humanas não medidas.
- Pagamentos, impostos e conta do vendedor brasileiro são pesquisados à parte: NÃO pesquise esse tema.

## 2. Regras de evidência (inegociáveis)
1. Data da consulta = 2026-10-07. Registre separadamente a data de publicação. Priorize publicações dos últimos 90 dias (desde 2026-07-09); o que for mais antigo não comprova demanda atual.
2. Você NÃO assiste a vídeo. Suas ferramentas leem texto de páginas. NÃO descreva ritmo, cenas, movimento, qualidade da animação, duração nem narração de um vídeo; só o que o título, a legenda ou a página dizem. `tipo_evidencia` honesto: `descrição lida`, `trecho indexado`, `site oficial`, `estatística de terceiros`. Nunca "vídeo assistido".
3. Instagram: só páginas públicas (`https://www.instagram.com/<perfil>/`) pelo WebFetch, no máximo 8 acessos ao domínio, sem login e sem contornar bloqueio. O leitor resume a página com um modelo pequeno: copie o que ele devolveu e registre inconsistências. Seguidores, bio e legendas costumam aparecer; visualizações, curtidas e comentários por Reel geralmente NÃO. Métrica oculta = `indisponível`. NÃO estime números.
4. Mercado e país só por evidência (idioma da bio e das legendas, moeda da oferta, links). Um perfil em inglês não comprova audiência nos EUA.
5. Oferta: URL oficial, preço e moeda visíveis, data da leitura. Página de produto prova que a oferta existe; NÃO prova venda, faturamento nem conversão. Condições de afiliado só se lidas na página oficial do programa (cite URL e data); senão `não verificado`.
6. Sinais públicos de compra valem como PROXY, nunca como faturamento: "N sales" de uma loja do Etsy, alunos de um curso da Udemy, avaliações e Best Sellers Rank de um livro da Amazon, avaliações no Gumroad ou Payhip, e equivalentes. Registre o número, a página e a data. Se a página bloquear o robô (403, login), registre isso e NÃO contorne.
7. Nada de número, preço, comissão ou regra que você não tenha lido numa página (copie a frase curta e a URL). Resultado de busca sem abrir a página é `trecho indexado` e não sustenta conclusão sozinho. Marque cada afirmação com [F] fato lido, [I] inferência sua ou [H] hipótese a testar.
8. Não copie roteiros nem identidade visual de ninguém; estude mecanismos (gancho, formato, CTA).
9. Orçamento: no máximo 20 WebSearch e 25 WebFetch no total, contando os do Instagram. Prefira abrir páginas oficiais direto a buscar. Se uma ferramenta recusar por limite de uso, pare, registre e entregue o que tem.

## 3. O que pesquisar (perguntas neutras; descubra as respostas, não as presuma)
a) Quem compra: perfil, países, problema que leva à compra, o que já paga hoje. Tamanho de mercado só com fonte publicada (cite); senão `não verificado`.
b) Ofertas pagas: pelo menos 8 ofertas de vendedores DIFERENTES (e-book, planilha ou template, curso, assinatura, aplicativo, serviço) com URL oficial, preço, moeda, data da leitura, plataforma de venda (Gumroad, Etsy, Udemy, Teachable, Whop, Amazon, site próprio...) e o proxy de compra quando houver. Resuma a faixa de preço observada (mínimo, mediana, máximo, em USD ou na moeda original) dizendo que a amostra é enviesada.
c) Criadores de vídeo curto (Instagram, TikTok, YouTube Shorts) no nicho: pelo menos 4 perfis de portes variados: handle, seguidores e data, bio, o que vendem, como vendem (link, CTA, palavra-chave nos comentários) e se usam animação ou rosto.
d) Afiliado: programas oficiais relevantes: comissão, recorrência ou duração do cookie, requisitos (audiência mínima, país, empresa), pagamento mínimo, se aceita criador de fora dos EUA. Só página oficial com data.
e) Regras e riscos no mercado-alvo, com URL oficial: divulgação de afiliado e de patrocínio, alegações de saúde ou de renda, aconselhamento financeiro ou jurídico, plataformas. Diga onde fica a fronteira entre informar e aconselhar e o que pode virar problema para um canal sem credencial.
f) Fontes abertas para os números dos vídeos: órgão, URL, tipo de dado, com que frequência atualiza, licença ou condição de uso (domínio público ou não). Diga quais envelhecem rápido.
g) Produção: mapeie 6 formatos de Reel de 20 a 45 s do nicho para os planos de retrato que existem HOJE (seção 1). Aponte o que exigiria demonstração de tela, rosto ou produto (impossível hoje) e o que exigiria componente novo.
h) Concorrência e gratuitos: o que já é gratuito (oficial e de criadores) e por que alguém pagaria pelo nosso produto. Seja crítico.
i) Hipóteses para um teste de 14 dias: isca gratuita, oferta mínima, o que medir. Rotule [H].

## 4. Entrega
Grave UM arquivo `ficha` em `/tmp/claude-1000/-home-viniciusk-projetos-auto-play/7494f80d-4e24-49a2-aa6f-11dbb3bce8e8/scratchpad/globais/<id>-ficha.md`, com no máximo ~200 linhas e estes títulos, nesta ordem:
1. Resumo (5 linhas) e confiança (baixa/média/alta, com o motivo)
2. Quem compra e o que já paga
3. Ofertas pagas observadas (tabela: vendedor, oferta, URL, preço e moeda, plataforma, proxy de compra, data da leitura, rótulo)
4. Criadores de vídeo curto (tabela)
5. Afiliado (tabela)
6. Regras e riscos (tabela com URL oficial)
7. Fontes abertas para as fichas (tabela)
8. Produção: 6 formatos × planos de retrato; lacunas
9. Concorrência e gratuitos
10. Hipóteses para 14 dias
11. Não verificado
12. Notas de 1 a 5 (viabilidade comercial, facilidade de produção, ligação conteúdo-produto, interesse pelo conteúdo, espaço competitivo; 5 = melhor) com uma linha de justificativa cada. São julgamentos comparativos, não probabilidades.
Não edite nada no repositório. No fim, responda em até 250 palavras: o que encontrou, quantas ofertas, perfis e páginas realmente verificou, o que ficou indisponível e a sua confiança.
