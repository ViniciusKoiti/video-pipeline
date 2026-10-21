# 030 — Trilha sonora no pipeline, decidida por um agente diretor musical

- **Status:** aceito pelo dono em 2026-10-21 ("ADR 030 inteira agora"), com os ajustes da seção "Implementação"
- **Data:** 2026-10-17
- **Etapa do roadmap:** voz e montagem (#16, #17); formato explicativo (#48)
- **Relaciona-se com:** ADR 007 (licenças), ADR 008 (planos ancorados na narração), ADR 009 (agentes escrevem dados,
  o código valida), ADR 022 (entrega da fala por cena, que deixou a trilha de fora), ADR 006 (portas)

## Contexto

O dono quer variar o clima dos vídeos com música de fundo que combine com o que a narração diz, e quer que um
agente decida onde a música entra. Hoje o template do explicativo não tem trilha: as ADRs 011, 014 e 022 a deixaram
de fora. O §9 do CLAUDE.md exige licença registrada por faixa. O gatilho é o ensaio de conceito com anime
(`docs/pesquisa/reports/Nicho recap de anime.md`), mas a trilha serve a qualquer episódio do explicativo.

Restrições:
- custo zero;
- a lista fechada de licenças;
- o agente não ouve áudio, então escolhe por etiquetas e pelo texto, e o dono valida na escuta;
- o tempo sai do WAV real, nunca de estimativa (§9).

## Opções consideradas

1. **Uma faixa fixa por vídeo, escolhida à mão.** Simples, mas não acompanha as viradas, e o dono pediu variação.
2. **Agente que escolhe e posiciona as faixas de um catálogo licenciado.** Segue o padrão da ADR 009: o agente
   escreve dados, o código valida e o dono decide.
3. **Música gerada sob medida para cada vídeo.** Combinaria mais, mas depende de um modelo com licença compatível
   (nenhum conferido até agora) e de avaliação na escuta. Fica como adapter futuro.

## Decisão (proposta)

1. **Catálogo** em `data/music/catalog.json`:
   - por faixa: `id`, fonte, `page_url`, licença, `sha256`, duração e etiquetas (clima, intensidade de 1 a 5, BPM,
     se tem voz cantada, se faz loop);
   - as etiquetas de clima vêm da fonte e da escuta do dono. Intensidade e BPM são medidos localmente;
   - a faixa só entra no catálogo depois de aprovada no gate 3, como qualquer ativo.
2. **Primeira fonte: YouTube Audio Library** (escolha do dono em 2026-10-17), só para vídeos publicados no YouTube.
   Os termos estão em `data/benchmarks/termos-musica.md` (página oficial lida em 2026-10-17): as faixas são
   "copyright-safe", não são reivindicadas pelo Content ID e podem ser monetizadas, mas o uso fora do YouTube não
   está coberto. O dono baixa as faixas à mão pelo Studio, porque não há API. A licença vai para a lista da ADR 007
   numa emenda. Pixabay Music e Suno ficam para uma decisão à parte: o Pixabay tem risco conhecido de
   reivindicação falsa no Content ID, e o plano do Suno ainda não foi registrado.
3. **Plano da trilha** em `data/episodes/<id>/music.json`, escrito pelo agente `diretor-musical` com a skill `trilha`:
   - cada entrada (*cue*) tem a faixa, uma âncora de entrada e outra de saída num trecho da narração (como os planos
     da ADR 008), um papel (`bed` para fundo, `sting` para transição curta, `silence` para silêncio proposital), o
     nível (`low` ou `mid`) e o fade;
   - o método fica na skill: o clima segue a `delivery` da cena (ADR 022) e o objetivo do vídeo (ADR 019), troca de
     faixa só nas viradas, poucas faixas por vídeo, silêncio antes da frase que decide e música sem voz cantada sob
     a narração.
4. **Tempo e contrato.** Uma etapa de código transforma as âncoras em milissegundos sobre a duração real dos WAVs,
   com a mesma lógica de `app/pipeline/shots.py`. O resultado vai para o `episode.json` num campo opcional `music`
   (faixa, arquivo, `start_ms`, `end_ms`, ganho e fades). Episódio sem o campo não muda.
5. **Render do explicativo.** Uma camada de áudio no template do Remotion:
   - fade de entrada e saída;
   - **ducking**: a música baixa quando a voz fala, calculado do envelope da voz, com a mesma leitura de
     `app/media/envelope.py`;
   - volume final perto de −14 LUFS, conferido nos checks automáticos, com a voz sempre acima da trilha.

   O motor ffmpeg do documentário fica fora desta ADR.
6. **Validação** no `vp check`:
   - toda faixa usada está aprovada no catálogo;
   - as âncoras existem;
   - não há `bed` sobreposto;
   - há um limite de trocas por minuto;
   - nada de voz cantada sob a narração.
7. **Lugar no fluxo:** roteiro → voz → **trilha** → render. O dono ouve a trilha na prévia, no gate 4. "Ajustar a
   música" volta só à trilha. Trocar uma faixa invalida só a montagem e a prévia (§5).
8. **Geração de música** entra depois, como adapter de uma porta `MusicSource` (ADR 006), quando houver um modelo
   com licença compatível conferida e uma escuta comparando com a biblioteca.

## Consequências

- Um agente novo (`.claude/agents/diretor-musical.md`) e uma skill (`trilha`), que só escrevem `music.json`.
- `episode.json` ganha o campo opcional `music`. Esta ADR é a autorização exigida pelo §6 do CLAUDE.md.
- **Ordem de implementação, um PR por etapa:**
  1. catálogo, schema e emenda de licença;
  2. render com uma faixa, ducking e o check de volume;
  3. agente, skill, `music.json` e as regras no `vp check`;
  4. adapter de geração, opcional.
- **Cache:** a chave do render inclui o `music` resolvido. A voz não muda com a trilha.
- **O que fica mais difícil:** cada vídeo ganha uma decisão de escuta a mais no gate 4. Um catálogo pequeno repete
  faixas entre vídeos, o que pesa no critério de variação do §12. O catálogo precisa crescer com o canal.
- **Ao aceitar:** atualizar o §9 e o §15 do CLAUDE.md no mesmo commit.

## Implementação (2026-10-21)

O dono pediu a ADR inteira para o vídeo `historia-vencedores`. A implementação segue a decisão, com três ajustes:

1. **A música entra na junção, não numa camada do Remotion.** O explicativo renderiza cada cena num segmento em
   cache, e a voz já é juntada uma vez só, no `assemble` (`app/render/ffmpeg.py`). A trilha entra ali:
   - cada trecho é cortado, ganha fade e ganho e vai para o seu lugar no tempo;
   - o ducking é o `sidechaincompress` do ffmpeg, com a voz como chave, e não um envelope calculado à parte;
   - a voz é levada ao alvo de −14 LUFS (medido antes da mistura) e um limitador segura o pico em ~−1 dBFS.

   Assim, trocar a faixa não refaz nenhum segmento de cena: refaz só a junção (§5). Vídeo sem trilha não muda,
   nem no volume.
2. **O catálogo guarda os direitos como ativo.** Cada faixa tem o ativo `data/music/<id>.json` (licença
   `YouTube-Audio-Library`, `sha256`, `usage_notes`) e uma linha no `catalog.json`, com as etiquetas.
   - A faixa entra no catálogo quando o dono a baixa (`scripts/provisorio/catalogo_musica.py adicionar`).
   - A aprovação é a do gate 3 de cada episódio que a usa: `catalogo_musica.py usar` copia o ativo para o
     `assets/` do episódio, como as imagens reaproveitadas.
3. **BPM é anotado à mão**, quando importa. A intensidade de 1 a 5 é medida pela loudness integrada da faixa.
   O clima e a voz cantada vêm da escuta do dono.

Os três PRs da ordem prevista viraram um só, porque o vídeo de quinta precisava das três partes. O adapter de
geração (etapa 4) continua fora.

**Onde está:**
- schema: `MusicTrack`, `MusicCatalog`, `MusicCue`, `MusicPlan` e `EpisodeMusic` em `app/pipeline/schemas.py`;
- tempo e regras: `app/pipeline/music.py`;
- loudness: `app/media/loudness.py`;
- mistura: `music_mix` em `app/render/ffmpeg.py`;
- `vp check`: lê `music.json` com o catálogo;
- `montar_episodio.py`: resolve a trilha e mede o volume depois do render;
- agente `diretor-musical` com a skill `trilha`;
- testes em `tests/test_music.py`, incluindo uma mistura real com ffmpeg.
