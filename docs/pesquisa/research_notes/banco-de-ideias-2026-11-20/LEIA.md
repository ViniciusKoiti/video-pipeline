# Coleta do banco de ideias, 2026-11-20

Primeira coleta da skill `vp-validacao-de-tema` (passo 1). Só páginas públicas do YouTube, lidas com `yt-dlp`
(2026.10.26), sem login, sem cookies e sem vidIQ. O passo a passo que saiu daqui está em
[coleta-publica.md](../../../../.agents/skills/vp-validacao-de-tema/coleta-publica.md).

## O que tem aqui

- **`busca.txt`:** 10 consultas na busca pública, 20 resultados cada (`yt-dlp -J --flat-playlist
  "ytsearch20:<consulta>"`), sobre o público do canal e os nichos vizinhos do palpite (psicologia,
  autoconhecimento, história, cultura pop comentada). A consulta q3 ("desânimo profundo jovem") voltou vazia. No
  fim do arquivo, os canais por número de aparições. Os títulos vêm traduzidos para o inglês quando o canal
  cadastrou tradução: confira o original pelo link. Daqui em diante a skill usa `coleta.py busca`, que traz o
  título em português.
- **`mais-vistos.txt`:** os 40 vídeos mais vistos, com 5 min ou mais, de 8 canais, cada um com as vezes que
  passou da mediana do canal. Saiu do `mais_vistos.py` da skill sobre duas leituras da aba Vídeos por canal (a
  padrão, com as views certas, e a com `lang=pt`, com o título original).
- **`aberturas.txt`:** os primeiros 40 s da legenda automática em português de 5 vídeos-modelo
  (`yt-dlp --skip-download --write-auto-subs --sub-langs pt-orig`). Tem erro de transcrição e vem sem pontuação.
- **`parecer-lote-1.md`:** o parecer do `validador-de-tema` sobre I02, I03, I04, I05 e I16, com a errata.

O bruto (JSON de cada canal) ficou em `data/cache/banco-de-ideias/bruto-2026-11-20/`, fora do Git.

## Correção da listagem, no mesmo dia

A primeira versão do `mais-vistos.txt`, a que o agente leu para o parecer do lote 1, tinha 15 vídeos por canal e
contava como zero os vídeos só para membros, que o YouTube lista sem views. Isso puxava a mediana para baixo em
três canais:

| Canal | Vídeos só para membros | Mediana antes | Mediana corrigida |
|---|---:|---:|---:|
| Filosofatos | 39 | 107 mil | 121 mil |
| Psicologia dos Animes | 18 | 71 mil | 75 mil |
| Inferno de Dante | 5 | 43 mil | 44 mil |

Nos outros cinco canais a mediana não mudou. A releitura trouxe os mesmos vídeos, com as mesmas views e os
mesmos títulos; a listagem passou de 15 para 40 por canal para que todo vídeo citado no banco apareça nela. O
efeito nos números do parecer está na errata dele.

## Limites

- Views e inscritos são da data da coleta e arredondados pelo YouTube ("1,5 mi"). São **estimativa** de interesse
  associado, não previsão de views do canal.
- Os vídeos mais vistos são os sobreviventes de cada canal: mostram o que pegou, não a taxa de acerto.
- A ordem é por views, feita aqui sobre a listagem inteira do canal. A opção "Em alta" do YouTube não foi lida.
- Nenhum vídeo foi assistido. O formato anotado no banco vem do título e, em 5 vídeos, da legenda automática.
- Crônicas Medievais tem 3 vídeos e um sucesso só (787 mil): não serve de exemplo de canal grande.
- Os títulos e as frases dos vídeos são deles. No banco entra só a pergunta e a forma (o que promete e como).
