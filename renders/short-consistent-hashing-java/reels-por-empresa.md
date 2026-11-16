# Consistent hashing: três Reels, um por empresa (proposta de texto, 2026-11-08)

**Pedido do dono (2026-11-08):** três Reels diferentes, cada um abrindo com uma pergunta sobre uma empresa; o Short
passa a citar só uma (Amazon). **Estado: só texto.** Nada de `content.json`, voz, render nem pacote até o dono
aprovar as falas abaixo (a skill pede o texto fechado antes da primeira voz, porque cada fala refeita custa uma chamada
ao Modal). Fontes e aspas literais: `fontes.md`, seções 1, 4 e 5. Números próprios: `demo/resultado.txt`.

**Regra de cada Reel:** o primeiro quadro é a pergunta; a fala não cita fonte (o rodapé mostra); o nome da empresa é
dito porque é o assunto; opinião e número de empresa nunca se misturam com a medição do dono; o que é de 2015 ou de
2017 é dito como tal.

**Pendente do dono (uma decisão, antes do `content.json`):** idioma e saída dos Reels. A série decidiu Instagram em
inglês com a pele do dono na janela (2026-10-31), mas a pele segue em `needs_review`. As falas abaixo estão em pt-BR;
a versão en vai para pasta própria com `traducao.json` e gate (ADR 034).

## Reel 1: Amazon

- **Pergunta de abertura (capa):** "Como a Amazon adiciona um servidor sem esvaziar o cache?"
- **Aplicação / decisão / benefício e limite:** cache distribuído de sessões; escolher resto do hash ou anel, e quantos
  pontos por servidor; benefício medido (80,18% → 20,13% das chaves mudam), limite medido (251,5% da carga com 1 ponto).
- **Animação:** chaves coloridas por servidor; no resto do hash quase todas trocam de cor ao entrar o 5º servidor; no
  anel só um arco muda e todas as trocadas vão para o novo; o anel com 1 ponto desigual e com muitos pontos parelho.

| Cena | Fala | Entrega | Origem |
| --- | --- | --- | --- |
| `pergunta` | Como a Amazon adiciona um servidor sem esvaziar o cache? | hook | pauta |
| `anel` | No Dynamo, chaves e servidores ficam num anel, e cada chave vai para o primeiro servidor no sentido horário. | neutral | F-D1 |
| `vizinhos` | Quando um servidor entra, só os vizinhos sentem a mudança. | neutral | F-D2 |
| `medicao` | Na minha medição, o resto do hash mexeu em oitenta por cento das chaves, e o anel com cem pontos por servidor, em vinte. | turn | medição |
| `pontos` | Com um ponto só a carga fica torta, e por isso o Dynamo usa vários pontos por servidor: os nós virtuais. | neutral | F-D3, F-D4, medição |
| `fecho` | Quantos pontos virtuais você daria para cada servidor? | invite | pergunta ao público |

~84 palavras, ~38 s a 2,2 palavras/s. Entregas: 1 hook, 1 turn, 1 invite, 3 neutral (50% neutras: abaixo dos 60% da
skill; trocar `vizinhos` e `medicao` para neutral se o dono preferir um único `turn`).

## Reel 2: Discord

- **Pergunta de abertura (capa):** "Como o Discord descobre em qual nó está cada comunidade?"
- **Aplicação / decisão / benefício e limite:** consulta ao anel a cada conexão de sessão; decisão de onde mora o anel
  (num processo dono ou em memória compartilhada de leitura); benefício e limite são **do Discord, 2017** (12 μs →
  0,3 μs por consulta; o anel custa até um segundo para ser reconstruído, mas muda raramente).
- **Animação:** sessões reconectando em bloco contra um único processo que guarda o anel (fila crescendo); depois o
  anel como bloco compartilhado, lido por todos sem passar pelo processo. Esta é a decisão de System Design do Reel.

| Cena | Fala | Entrega | Origem |
| --- | --- | --- | --- |
| `pergunta` | Como o Discord descobre em qual nó está cada comunidade? | hook | pauta |
| `anel` | Em dois mil e dezessete, eles usavam um anel de consistent hashing para achar o nó de cada entidade. | neutral | F-Di1 |
| `gargalo` | Mas quando muitos usuários reconectavam juntos, o processo dono do anel não dava conta e o sistema sobrecarregava. | turn | F-Di3 |
| `solucao` | A saída foi pôr o anel numa memória compartilhada só de leitura, e cada consulta caiu de doze microssegundos para zero vírgula três. | neutral | F-Di2, F-Di4 |
| `fecho` | O seu anel fica na memória de quem consulta, ou atrás de um processo só? | invite | pergunta ao público |

~80 palavras, ~36 s. Só números do post do Discord, ditos como deles; nada do Java do dono entra. O 30 s de consulta
de uma reinicialização e os 750 ms ficam fora (cabem num segundo plano do rodapé, se o dono quiser).
Glossário de voz: "consistent hashing" ("consistent rrráshin" a conferir na escuta), "μs" por extenso.

## Reel 3: Akamai

- **Pergunta de abertura (capa):** "Como a Akamai decide qual servidor entrega cada arquivo?"
- **Aplicação / decisão / benefício e limite:** CDN com vários servidores por cluster; decisão de mapear arquivo e
  servidor no mesmo círculo; benefício medido pelo dono (80,18% → 20,13%) e descrito pelo artigo (só os arquivos do
  servidor novo se movem); limite: o escopo do artigo é um cluster e é de 2015.
- **Animação:** arquivos e servidores como pontos no círculo; cada arquivo liga ao próximo servidor no sentido horário;
  entra um servidor e só os arquivos do seu arco trocam de ligação (as setas mudam).

| Cena | Fala | Entrega | Origem |
| --- | --- | --- | --- |
| `pergunta` | Como a Akamai decide qual servidor entrega cada arquivo? | hook | pauta |
| `circulo` | Arquivos e servidores vão para o mesmo círculo, e cada arquivo fica com o próximo servidor no sentido horário. | neutral | F-A2 |
| `origem` | Foi a primeira inovação algorítmica da rede de entrega da Akamai, e serve para dividir a carga dentro de um cluster. | turn | F-A1 |
| `servidor-novo` | Quando entra um servidor, só os arquivos que caem nele precisam mudar, e na minha medição foram vinte por cento, contra oitenta no resto do hash. | neutral | F-A3, medição |
| `fecho` | O seu sistema aguenta mover oitenta por cento do cache de uma vez? | invite | pergunta ao público |

~85 palavras, ~39 s. Fonte interessada (autores da Akamai): a fala atribui o uso à Akamai porque o artigo diz, e fica
em "dentro de um cluster", sem estender à empresa toda.

## O que falta para cada Reel virar vídeo (nada disto foi feito)

1. Dono aprova as falas e decide o idioma e a saída (acima).
2. `plano-animacao.md` de cada Reel com estados, blocos e setas (e a seção "Música": só YouTube; Instagram sem trilha).
3. `narracao.pt.json` (humanizer antes da voz), glossário de pronúncia (Dynamo, Akamai, Discord, consistent hashing).
4. `medicao.json` com 80,18 / 20,13 / 251,5 / 140,2 / 111,2 por Reel; `vp medicao` limpo. Os números das empresas não
   entram no `medicao.json` (são de fonte, não de medição) e o `vp check` os confere pelas aspas de `fontes.md`.
5. `content.json`, `validate`/`inspect`/`review` do kit, voz no Modal (só com o pedido do dono), `tempos`, render,
   SFX, `vp audio`, gate 4 por saída, Postiz.
6. O Short (Amazon) ganha a mesma refação em `content.pt.json` e `content.en.json` (cena `anel`).
