# Prompt de sessão: Reel "Thiel, dados e vigilância" (2026-10-12)

Colar numa sessão nova do Claude Code aberta em `~/projetos/auto-play`. Estado de partida: branch
`clipe-fim-dos-cortes` com alterações não commitadas em `video/src/clipe/`; `scripts/provisorio/sprites_apresentador.py`
e `tests/test_sprites_apresentador.py` novos e não commitados; ADRs 016 e 017 ainda propostas. O episódio
`thiel-dados-pt` não existe. Os dados de episódio ficam em `data/episodes/`, fora do Git, então esta frente não
precisa de branch.

---

Contexto: video-pipeline (CLAUDE.md na raiz). Fale em português simples, com calma, uma etapa por vez, perguntas
curtas e agrupadas, sem perguntar "posso seguir?". Pare só nos gates e no que estiver marcado abaixo como decisão
minha.

Frente de hoje: **levar o episódio `thiel-dados-pt` das fontes até o roteiro pronto para o gate 2.** Reel em pé
(9:16, `orientation: portrait`), em pt-BR, de 80 a 90 s.

O ângulo é escolha minha: dados e vigilância. A pergunta central, para a pesquisa responder, é: **o que as fontes
dizem que as empresas ligadas a Peter Thiel fazem com dados de pessoas, para quem, e o que isso tem a ver com quem
assiste no Brasil?** Se as fontes não sustentarem uma ligação com o espectador brasileiro, me diga isso antes do
roteiro; não force a ponte.

## 1. Fontes (autorizo o download destas oito, só delas)

Baixe com `scripts/provisorio/baixar_fonte.py` (veja o `--help` e como o `proteina-igual-pt` foi montado). Registre
`--kind`, `--authors` e `--interested` como indicado; escreva cada `--notes` só depois de abrir o texto baixado.

| # | URL | Tipo | Interessada |
|---|---|---|---|
| 1 | https://www.sec.gov/Archives/edgar/data/1321655/000132165525000022/pltr-20241231.htm | primária (relatório anual da empresa à SEC) | sim |
| 2 | https://www.defensenews.com/industry/2020/09/30/secretive-never-profitable-palantir-makes-its-market-debut/ | secundária (agência AP) | não |
| 3 | https://www.yahoo.com/news/ice-just-ordered-30-million-212445164.html | secundária (Business Insider) | não |
| 4 | https://chequeado.com/el-explicador/peter-thiel-en-argentina-el-papel-de-palantir-en-los-operativos-migratorios-de-ice/ | secundária (checagem, em espanhol) | não |
| 5 | https://theglobeandmail.com/business/article-palantir-ceo-insists-surveillance-technology-has-safeguards-as | secundária (agência Reuters) | não |
| 6 | https://digitalhealth.net/2023/11/nhs-england-awards-330m-federated-data-platform-contract-to-palantir | secundária (imprensa setorial) | não |
| 7 | https://www.businesswire.com/news/home/20210630005225/en/Palantir-and-Grupo-Globo-Extend-Digital-Transformation-Partnership | primária (comunicado da empresa) | sim |
| 8 | https://tecnoblog.net/responde/o-que-faz-a-palantir/ | secundária (explicativo em português) | não |

- Se um site recusar o robô (403) ou vier atrás de paywall, não contorne: anote e me diga, que eu salvo o PDF à
  mão (`--file`). O da SEC costuma exigir identificação no User-Agent.
- A fonte 1 é longa. Ficha só o que responde à pergunta central; não resuma o relatório inteiro.
- Fontes com a mesma origem (por exemplo, duas que reproduzem o mesmo comunicado ou a mesma agência) contam como
  uma só: confira os autores e me avise.
- Se faltar segunda fonte independente para um fato que importa, **proponha** candidatas com link e espere meu ok
  antes de baixar. Texto de opinião não entra como fonte de fato.

## 2. Fichas e gate 1

1. `vp excerpts thiel-dados-pt`.
2. Agente `pesquisador` (skill `fichamento`) escreve `facts.json`. Passe a ele a pergunta central acima e as
   perguntas neutras de `docs/pesquisa/modelo-perfil-de-poder.md` (seção "Perguntas de pesquisa genéricas"),
   adaptadas a uma pessoa. **Não ponha no prompt dele nenhum fato sobre a pessoa ou as empresas**: só perguntas, e
   os ids dos trechos quando precisar apontar algo.
3. `vp check thiel-dados-pt` até passar.
4. **Gate 1 (decisão minha):** me mostre as fichas em lista curta, cada uma com o id, a frase do fato, a fonte e se
   depende de fonte interessada. Destaque: as fichas de `impact_today` (são elas que permitem falar "você"), o que
   ficou em `open_questions` e o que só tem uma fonte. Eu escolho os fatos e aprovo com `vp approve`.

## 3. Roteiro (depois do gate 1)

Agente `roteirista` (skills `roteiro-explicativo` e `humanizer-narracao`), só com as fichas aprovadas. Além do
método da skill, valem estas orientações de **forma**, vindas do reels-radar. São observação de amostra pequena
(34 Reels de privacidade em português), nunca fonte de fato:

- Abertura que fala com o espectador ("você"), em tom de alerta, com cerca de 9 palavras, e um título de alerta na
  tela nos primeiros segundos (plano `keyword`). Arquivo: `~/projetos/radar-de-reels/briefs/privacy.json`.
- O "você" entra na abertura, na ponte com o espectador e, se houver fato, no fecho; o miolo vai em terceira
  pessoa. "Você" que afirma algo sobre a pessoa exige ficha de `impact_today` com escala e data; sem ficha, a
  abertura vira pergunta.
- Começar por algo concreto que a pessoa tem ou usa, não por ideia abstrata. Nas legendas, as palavras "celular",
  "conversas", "casa" e "tela" andaram com mais compartilhamento; "privacidade" como palavra, com menos.
- Duração acima de 72 s.
- Não copiar frase, título nem imagem dos Reels citados no resumo.

Regras do conteúdo:

- Pessoa viva e empresa ativa: controvérsia só atribuída ("segundo tal veículo, em tal ano"), com o contraponto
  da empresa quando a ficha tiver. Sem enquadramento de vilão, sem afirmar crime ou intenção.
- Perfil vertical: só os planos `photo`, `broll`, `number`, `keyword`, `stamp`, `lower_third`, `compare` e `chart`.
  Não conte com retrato da pessoa: o gate 3 ainda não foi feito e CC-BY-SA não entra.
- Apresentador: o Notionists de hoje. A pele e a voz do dono não estão no template.
- Em 80 a 90 s cabem três blocos: a ponte com o espectador, um mecanismo e uma controvérsia atribuída. O resto
  fica de fora.

Depois: `vp check`, agente `verificador` (skill `checagem`), corrigir o que ele apontar e rodar o `vp check` de novo.
Escreva também um rascunho de `legenda-post.txt` com "você", no mesmo cuidado de fatos.

## Limites desta sessão

- Rede: só os oito downloads acima. Nenhum provedor (Gemini, Pexels, Pixabay, Unsplash, Cloudflare, Apify);
  Kokoro e Ollama locais podem rodar.
- Sem voz final, sem busca de imagem, sem render, sem prévia. Isso é outra sessão, depois do gate 2.
- Custo zero (§2.1). Nada de fato de memória em roteiro, ficha, nota de fonte ou prompt de agente (§14).
- Não mexa em `video/`, `app/`, `config/` nem nas alterações não commitadas da branch. Sem commit.
- Arquivos `approved` de outros episódios ficam intactos.

Pronto quando: `sources.json` e `facts.json` passam no `vp check`, o gate 1 está aprovado por mim, `outline.md` e
`scenes.json` passam no `vp check`, o relatório do verificador não tem pendência aberta, e você me mostra o roteiro
cena a cena (narração, planos e fichas citadas) para o gate 2.

## Contexto do YouTube (não é fonte)

Coleta do reels-radar em 2026-10-12 (`niches/peter-thiel-shorts.toml` e `niches/peter-thiel.toml`): 110 Shorts
distintos e 16 vídeos longos que citam a pessoa. Quase nada em português (3 Shorts distintos, 2 longos). Palavras
de dados e vigilância aparecem em 19 dos 110 Shorts e em 6 dos 16 longos; o grupo mais comum nos Shorts é o de
origem e startups (25). Serve para saber o que já existe, não para afirmar nada no roteiro. A coleta do Instagram
não foi feita (gasta crédito da Apify e espera decisão minha).
