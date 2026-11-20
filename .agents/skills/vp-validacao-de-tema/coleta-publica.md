# Coleta pública para o banco de ideias

Como levantar o que rendeu nos canais de referência lendo só páginas públicas do YouTube, sem login e sem cota.
vidIQ e APIs seguem a regra do passo 1 da skill: só com pedido do dono na sessão.

## 1. Busca: achar canais e vídeos

```bash
S=.agents/skills/validacao-de-nicho
python3 -I $S/coleta.py busca "<consulta na voz do público>" - <notas>/busca.csv
```

O `coleta.py` é o da skill `validacao-de-nicho`: lê a primeira página da busca em português, com views, duração e
canal de cada vídeo, e acrescenta as linhas ao CSV. Pausa, resposta 429 e conferência de idioma estão em
[medicao-de-demanda.md](../validacao-de-nicho/medicao-de-demanda.md).

Pronto quando cada nicho do passo 1 tem ao menos uma consulta e os canais que se repetem estão anotados.

## 2. Os mais vistos de um canal

À mão, no navegador: aba Vídeos, menu de ordenação (abre em "Mais recentes"), opção **"Em alta"**.

Por script, a listagem do canal inteiro, ordenada por views aqui:

```bash
B=data/cache/banco-de-ideias/bruto-<data>          # o bruto fica fora do Git
yt-dlp --ignore-config -J --flat-playlist --sleep-requests 1 "<url do canal>/videos" > $B/<canal>.json
yt-dlp --ignore-config -J --flat-playlist --sleep-requests 1 --extractor-args "youtube:lang=pt" \
  "<url do canal>/videos" > $B/<canal>.pt.json
python3 -I .agents/skills/vp-validacao-de-tema/mais_vistos.py $B/<canal>.json >> <notas>/mais-vistos.txt
```

São duas leituras por canal porque cada uma erra uma coisa, e o `mais_vistos.py` aproveita o que cada uma acerta:

- a padrão traz as views certas, e o título traduzido para o inglês quando o canal cadastrou tradução;
- a com `lang=pt` traz o título original, e as views erradas ("312 mil" lido como 312).

O que a listagem mostra, e como ler:

- **Vezes a mediana:** views do vídeo ÷ mediana de views do canal. É a medida de quanto o vídeo passou do normal
  daquele canal, e é ela que vai para o parecer. Views soltas comparam canais de tamanhos diferentes.
- **Vídeo só para membros** vem sem contagem de views: fica fora da lista e da mediana, contado em `sem_views`.
- **Duração mínima:** 5 min por padrão (`--min-s`), para deixar fora o que não é vídeo longo.
- **Canal de um sucesso só** (poucos vídeos, um deles enorme) mostra um vídeo que pegou, e não um formato validado.
- **Canal com milhares de vídeos:** `--playlist-end 800` lê os 800 mais recentes; registre o corte nas notas.

Pronto quando cada canal de referência do banco tem o bloco dele em `mais-vistos.txt`.

## 3. Abertura dos vídeos-modelo

A listagem dá a promessa (o título) e a duração. A abertura se anota de quem viu o vídeo ou leu a legenda:

```bash
yt-dlp --ignore-config --skip-download --write-auto-subs --sub-langs pt-orig --sub-format vtt \
  -o "$B/%(id)s" "https://www.youtube.com/watch?v=<id>"
```

Leia os primeiros 40 s do `.vtt` e anote a forma (cena, pergunta, mito, relato), com as suas palavras. A legenda
automática erra nomes e vem sem pontuação. Para medir a forma de um nicho inteiro (espinha, ritmo, imagem), a
skill é a `analise-de-formato`.

## 4. Notas da coleta

Cada coleta tem uma pasta `docs/pesquisa/research_notes/banco-de-ideias-<data>/`:

- `LEIA.md`: data, consultas, canais lidos, como foi lido e os limites;
- `busca.csv` e `mais-vistos.txt`;
- `aberturas.txt`, quando houver;
- `parecer-lote-N.md`, que entra no passo 4 da skill.

Limites que o `LEIA.md` sempre escreve: views e inscritos são da data da coleta e arredondados pelo YouTube; os
mais vistos são os sobreviventes de cada canal; views de terceiros mostram interesse associado.

Pronto quando todo número do banco aparece num arquivo das notas.
