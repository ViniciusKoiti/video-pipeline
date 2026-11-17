# Miniatura genérica: proposta para discussão

**Estado:** proposta (2026-11-13), pedida pelo dono para pensar a skill de forma genérica. Nada aqui muda o método do
`SKILL.md` antes da decisão do dono. Hoje a skill nasceu do ensaio de anime (quadro oficial recortado sobre fundo
vermelho, no molde do Filosofatos). O piloto da capivara economista (`academia-dinheiro-pt`) mostrou que o mesmo
método precisa servir a outros formatos: personagem próprio, explicativo sem personagem, Short.

## O que é igual em todo formato

Toda miniatura do projeto é a mesma pilha de camadas, de trás para a frente:

| Camada | O que é | Exemplos |
|---|---|---|
| **Fundo** | o lugar ou a cor do tema | vermelho chapado com vinheta; foto real do tema; um fundo gerado do próprio episódio |
| **Palavra (atrás)** | uma ou duas palavras que completam o título | "TERIA VOTOS?", "NINGUÉM VAI?" |
| **Figura** | quem ou o que segura o olhar | personagem recortado, mascote do kit, objeto do tema |
| **Contorno da palavra (na frente)** | o contorno volta por cima da figura, para a figura parecer na frente sem esconder a palavra | — |
| **Acento (opcional)** | o que aponta o detalhe | seta, círculo, número grande, selo da série |

O que muda de um canal para outro é **o molde**: quais camadas aparecem, em que tamanho e com que tratamento. O que
muda de um episódio para outro é **o conteúdo** de cada camada.

## O molde de miniatura do canal de referência

Como o `molde.json` mede como os vídeos de um nicho são feitos, um molde de miniatura mede como as capas são feitas. É
medido uma vez por canal de referência, com as capas públicas (acesso externo: só com pedido do dono na sessão) e
guardado em `docs/pesquisa/miniaturas-<canal>-<data>.md`, sem as imagens de terceiros no Git.

O que anotar, de 20 a 30 capas recentes, com as visualizações ao lado:

- **Figura:** quantas; pessoa, personagem, mascote ou objeto; tamanho na tela (fração da altura); de frente ou de lado;
  expressão; olhando para a câmera ou para o objeto.
- **Fundo:** cor chapada, foto do tema ou cena desenhada; desfocado ou não; tratamento (cinza, monocromático,
  saturado).
- **Texto:** quantas palavras; fonte (grossa, esticada, com contorno); posição; cor; se repete ou completa o título.
- **Acentos:** setas, círculos, números, selos.
- **Constantes do canal:** o que se repete em quase todas (por exemplo, o mascote sempre presente, sempre à direita).

Ressalva fixa: a visualização depende do tema, do título e da idade do vídeo. O molde mostra o padrão do canal, não
prova qual capa rende mais.

## De onde vem a figura

| Fonte | Como se obtém | Licença no projeto | Cuidado |
|---|---|---|---|
| **Quadro oficial da obra** (ensaio de anime) | quadro registrado como `Citacao`, recortado com `recortar.py` | `Citacao` (emenda de citação da ADR 007) | só material oficial; a capa com quadro da obra é decisão do dono no gate 4; um strike suspende a série |
| **Mascote ou personagem do motion-kit** (capivara) | renderizado pelo próprio kit em alta resolução, com fundo transparente, na pose e expressão pedidas; não precisa recortar | `Original` | usar o mesmo desenho do vídeo; a pose da capa precisa existir no kit (hoje: frente, perfil, sentada, apontar para a direita, sete expressões) |
| **Pele do dono** (apresentador) | as imagens de `host/dono/` | conforme o `origem.json` | dado pessoal, fora do Git |
| **Foto de acervo ou de banco** | a cascata da §8; recorte por cor ou por modelo | a da lista fechada (CC-BY de órgão público é a preferida) | pessoas, marcas e texto conferidos em resolução cheia; Public Domain Mark não está na lista |
| **Imagem gerada** | o mesmo caminho dos fundos do episódio | `Generated`, com o registro da geração | ilustração, nunca "registro" do fato (§2.4); marcar conteúdo sintético |
| **Objeto ou número do kit** | uma peça do kit renderizada como quadro parado | `Original` | número na capa precisa estar numa ficha, como na tela do vídeo |

## De onde vem o fundo

- **Cor chapada com vinheta:** temas pesados (política, poder), quando o canal de referência faz assim.
- **Foto real do tema:** quando o objeto identifica o assunto (a urna no `kira-voto-brasil`).
- **Fundo do próprio episódio:** no formato de mascote em cenário, um dos fundos gerados para o vídeo (a pauta do
  piloto previa o salão vazio, fundo C). Mantém a capa coerente com o que a pessoa vai ver.
- **Desfoque:** ajuda a figura a saltar e esconde a ampliação de fundos de baixa resolução.

## Texto

- Uma palavra, no máximo duas, que **completa** o título e não o repete.
- Fonte grossa e esticada na horizontal (hoje Inter Display Black, OFL), com contorno.
- A figura na frente da palavra; o contorno da palavra volta por cima.
- Fora do canto inferior direito, onde o YouTube põe a duração do vídeo.
- Sem número que não esteja numa ficha, e sem promessa que o vídeo não cumpre.

## A composição como dado (proposta)

Hoje o `compor.py` recebe tudo por argumentos de linha de comando. A proposta é cada episódio ter um
`miniatura/miniatura.json` que declara as camadas de cada versão, para a composição ser reproduzível e comparável:

```json
{
  "molde": "docs/pesquisa/miniaturas-lucro-disfarcado-AAAA-MM-DD.md",
  "versoes": [
    {
      "id": "a",
      "fundo": { "asset_id": "fundo-c-salao-vazio", "desfoque": 4 },
      "figura": { "fonte": "kit", "personagem": "capivara", "expressao": "suspicious",
                  "enquadramento": "bust", "altura": 0.85, "x": 0.68 },
      "texto": { "palavras": "NINGUÉM VAI?", "onde": "topo", "esticar": 1.25 },
      "muda_em_relacao_a": null
    },
    {
      "id": "b",
      "muda_em_relacao_a": "a",
      "texto": { "palavras": "QUEM PAGA?" }
    }
  ]
}
```

Cada versão muda uma coisa só em relação à anterior (`muda_em_relacao_a`), como o método já pede.

## Ferramentas: o que existe e o que falta

| Peça | Situação |
|---|---|
| `recortar.py` (rembg, modelo de anime) | existe; serve ao quadro oficial |
| `compor.py` (camadas, prévia em 320 px) | existe; lê argumentos, não um JSON |
| Figura do kit com fundo transparente | falta: um quadro parado do personagem na pose pedida, em PNG com transparência (pelo `still` do Remotion ou pelo motion-video) |
| Composição a partir do `miniatura.json` | falta: o `compor.py` lendo o JSON, ou a peça `Miniatura` do kit que o `SKILL.md` já prevê |
| Análise das capas do canal (folha de capas + anotações) | feita à mão para o Filosofatos; falta um script que monte a folha a partir da lista de vídeos |

## Conferência (vale para qualquer formato)

- **320 px**, o tamanho da lista do YouTube: a palavra se lê, a figura e o objeto do tema se reconhecem.
- **A promessa bate com o título e com o vídeo:** nada que o vídeo não mostra.
- **Direitos registrados de cada camada:** a figura, o fundo e a fonte.
- **Rótulo de conteúdo sintético** quando a capa ou o vídeo usa imagem gerada ou voz sintética.
- **Nenhum resto de recorte**, nenhuma letra sobre fundo da mesma cor.

## Teste e medida

- A pauta registra a hipótese da capa antes do teste (CLAUDE.md §4; método e H01 em
  `docs/pesquisa/crescimento-youtube-embalagem-hipoteses-2026-10-23.md`).
- Se o dono quiser comparar capas, o próprio YouTube Studio tem teste de miniaturas. A decisão de usar é do dono, e o
  resultado vai para `metrics.json`.

## Como ficaria em cada formato

| Formato | Figura | Fundo | Texto |
|---|---|---|---|
| Ensaio de anime (Filosofatos) | quadro oficial recortado | vermelho chapado ou foto do tema | uma palavra que completa o título |
| Mascote em cenário (capivara, Lucro Disfarçado) | a capivara do kit, em pose e expressão da capa | um fundo do episódio, desfocado | a pergunta do título em duas palavras |
| Explicativo sem personagem (Aquário) | o objeto do tema (foto ou peça do kit) | cor ou foto | um número com ficha, ou uma palavra |
| Short | o primeiro quadro do vídeo é a capa (o vídeo começa sem fade) | — | o texto do primeiro quadro |

## Perguntas para o dono

1. Vale ter um molde de miniatura por canal de referência, medido como o `molde.json`? E, para o piloto, analisar as
   capas do Lucro Disfarçado (acesso às capas públicas no YouTube)?
2. A composição passa a ser declarada num `miniatura.json`, ou os argumentos do `compor.py` bastam por enquanto?
3. A figura do kit (capivara) sai por um quadro parado renderizado pelo próprio kit, ou o kit ganha a peça `Miniatura`?
4. O `SKILL.md` se reescreve no formato genérico agora, ou depois da primeira miniatura da capivara?
