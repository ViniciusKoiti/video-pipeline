# Revisão das ADRs 001–059 (2026-11-14)

Revisão só de leitura, a pedido do dono: cada ADR ainda serve à situação de hoje? Hoje o projeto tem 4 semanas de
publicação em vários canais, e as ADRs foram escritas para uma fase de validação com 4 vídeos e um piloto
documentário. Três leitores leram as 55 ADRs inteiras, em lotes (001–016, 017–033, 034–059), e conferiram no código o
que era barato conferir. Os achados de maior peso foram reconferidos na sessão principal (marcados ✔). Nenhum arquivo
foi alterado.

## Resumo

- **Adequadas (≈25):** quase todas as decisões de código (portas, modelos, constantes, erros, fontes, ativos, voz por
  cena, pacote do gate 4) e algumas editoriais (objetivo, conta na tela, entrega da fala, Postiz).
- **O problema não está nelas.** Está em três lugares:
  1. **Decisões editoriais que nunca viraram ADR** e hoje guiam o trabalho sem motivo registrado: a miniatura pelo
     canal de referência, as métricas manuais sem a API do YouTube, os Shorts cortados do longo, a trilha
     obrigatória e a direção dos vídeos técnicos.
  2. **ADRs da fase de Reels e da validação** que continuam valendo no papel, mas não se aplicam mais: radar,
     funil, planos dos Reels, legenda palavra a palavra, "MVP só documentário".
  3. **Status e texto desatualizados:** ADRs "propostas" já em uso, emendas sem referência cruzada e scripts
     citados que já foram apagados.

## Urgente (afeta vídeo publicado ou roda sozinho hoje)

| # | Achado | Evidência |
|---|---|---|
| U1 ✔ | **A condição da ADR 058 (voz do Azure) não foi cumprida.** A ADR diz que a voz não entra em vídeo publicado antes de o dono ler os Microsoft Product Terms sobre uso comercial. Mesmo assim, o `academia-dinheiro-pt` e dois Shorts saíram como não listados em 14/11 com essa voz. A Microsoft também exige avisar que a voz é sintética. | `058-voz-azure-speech.md:64-70`; `data/benchmarks/termos-azure-speech.md` ("A confirmar"); 70 WAVs `azure_speech` em `academia-dinheiro-pt/voice/` |
| U2 ✔ | **A rotina diária de Shorts (ADR 036) roda todo dia às 06:00 e está parada há 7 dias** no passo das fontes primárias: a sessão sem ninguém para aprovar não tem permissão de baixar a fonte. Gasta cota e não produz nada. A ADR e a descrição do timer ainda dizem "desligado". | `systemctl --user list-timers` (próxima execução 15/11 06:00); `data/rotina/2026-11-14.md` |
| U3 | **Permissão mais larga do que a ADR 036 prevê:** `settings.local.json` libera `.venv/bin/vp postiz *` (inclui `postiz duvida`, que a ADR proíbe à rotina). Depende da precedência entre as regras `ask` e `allow`; não foi testado. | relatório do lote 034–059 |
| U4 ✔ | **Shorts sem legenda queimada.** As ADRs 014 e 021 mandam queimar a legenda no vertical, mas os Shorts técnicos saem pelo `motion-video`, que não tem legenda ("fora da v1"). Os Shorts somam 61% das views do Cena e Conceito, com 11 s por view. | `.claude/skills/shorts-tec/SKILL.md:150` |
| U5 ✔ | **Duas regras opostas sobre anime em movimento.** A ADR 031 (l.51–52) diz que a "cena do anime em movimento continua fora"; a emenda de 03/11 da ADR 007 liberou clipes em B-roll. Quem lê a 031 (roteirista, plano de imagens) restringe mais do que o dono decidiu. | `031-perfil-de-formato-do-nicho.md:51-52`; CLAUDE.md §6 |

## Regras em uso sem ADR (onde as escolhas ruins se escondem)

- **Miniatura pelo canal de referência** (pintura ou busto e uma palavra; skill `miniatura`): nenhuma ADR. Esse estilo
  teve de 0,9% a 2,2% de CTR; o vídeo que fugiu dele teve 4,2% (`studio-export-cena-e-conceito-2026-11-14.md`).
- **§12: métricas manuais, "sem API do YouTube nesta fase", 4 vídeos no mesmo recorte:** vem da spec v0.4 (primeiro
  commit, 24/09), sem motivo nem critério de saída da fase. A emenda de métricas da ADR 007 (l.204) só repete o §12.
  Resultado: 17 leituras vencidas e nenhuma feita.
- **Imagem gerada pelo gerador do dono** (`Generated` com `provider original`, "decisão do dono de 2026-10-27"): a
  ADR 007 (l.25) e o §8 definem `Generated` como Workers AI. Foi o caminho do vídeo com 4,2%.
- **Shorts cortados de um longo** (personagem pergunta na abertura e chama para o canal no fecho; frase fixa na
  descrição), **trilha obrigatória nos longos**, **direção dos vídeos técnicos** (System Design, Java, quadro de
  controle), **vídeo-régua** (citado em 12 ADRs, sem nenhuma que o estabeleça), **gate de qualidade** (mypy, limite
  de tamanho por arquivo), **exceção de código do `diretor-animacao`** e o **ambiente** posterior à ADR 004
  (nvm, temporários do Remotion, sonda de CPU).
- **ADRs fantasmas:** 002, 003 e 010 são citadas (007, 009, CLAUDE.md §13.7), mas nunca existiram no Git ✔.

## Conflitos com o código

- **ADR 055 × ADR 008 e schema ✔:** a ficção histórica dispensa claims, mas o código exige claims em todo plano
  com dado na tela (`_schemas_factual_shot.py:10`, `min_length=1`). Por enquanto passa porque o `idade-media-ser-rico`
  usa só `photo` e `keyword`; um número ou carimbo nesse formato seria recusado.
- **ADR 039:** o passo `translation` pode ser reaberto, mas os arquivos da tradução não ficam protegidos
  (`gates_constants.py:14-28`).
- **ADR 040:** `run_scenes` só é chamado nos testes; o CLAUDE.md descreve como se estivesse em uso.
- **"Só no YouTube"** (música, ADR 030; clipes, emenda da ADR 007): não há trava no `vp postiz`.
- **ADR 034** cria um quinto gate (`translation`), mas o CLAUDE.md ainda fala em 4.
- **ADR 033** proíbe um segundo caminho de render, mas os Shorts saem pelo `motion-video` (ADRs 048 e 050), sem
  emenda.

## Tabela por ADR

Vereditos: **ok** = adequada; **status** = o status declarado não bate com a prática; **parcial** = superada em parte
sem marcação; **vencida** = a premissa mudou; **texto** = cita arquivo ou nome que já não existe.

| ADR | Veredito | Motivo |
|---|---|---|
| 001 Motor por formato | vencida, texto | "MVP só documentário"; os 44 `episode.json` são `explainer` v2; o `format_decision.py` não é chamado; o item 3 foi superado |
| 004 Ambiente WSL | ok | `.wslconfig` bate com a ADR |
| 006 Portas e adaptadores | ok (pequena deriva) | "uma implementação por função" não vale para a voz (`tts`, `tts_final`, `--voz`) |
| 007 Contratos e licenças | parcial, status | item 1 trocado pela 008 e o 16:9 ampliado pela 014, sem marca; emenda Holder-Program "proposta" numa linha encerrada; cita `metricas.py` (agora `vp metricas`); `Generated` só Workers AI |
| 008 Cena com planos | ok | falta citar a 055; o tempo por palavra nunca foi ligado |
| 009 Agentes criativos | parcial | modelo do `roteirista` diferente do arquivo do agente; `diretor-animacao` fora da tabela; cita 002/003 |
| 011 Planos editoriais | status | emenda de 07/10 "proposta", mas já implementada; o kit já tem `locale`, mas o template não passa |
| 012 Voz Gemini | vencida, status | não é mais a voz final (`tts_final = chatterbox_modal`); segue só como voz do vídeo-régua |
| 013 Apresentador em janela | ok | só uma referência velha ao `montar_episodio` |
| 014 Perfil vertical | ok | os Shorts técnicos saem por outro caminho (`motion-video`) |
| 015 Pausas e tom | status | pausas ok; o tom do Gemini perdeu o objeto |
| 016 Voz clonada | parcial | a 024 a emendou (Modal), mas a 016 não aponta de volta e ainda diz "nunca enviada a provedor" |
| 017 Apresentador do dono | status | a parte B nunca foi feita e a premissa dela acabou; o gerador da pele já tem registro |
| 018 Radar de Reels | vencida, texto | último `radar-brief.json` de 17/10; cita `radar_resumo.py`, que foi apagado |
| 019 Objetivo | ok | os 22 episódios recentes declaram o objetivo |
| 020 Conta na tela | ok | só a confeitaria usou |
| 021 Legenda por frase | parcial, texto | os longos usam; os Shorts saem sem legenda; cita `montar_episodio.py` |
| 022 Entrega da fala | ok | |
| 023 Legenda palavra a palavra | vencida | último uso em 14/10 |
| 024 Voz no Modal | ok | depende do crédito gratuito do Modal |
| 025 Postiz | ok | |
| 026 Funil | vencida | 21 de 22 longos são `topo`; o estágio não está no `metrics.json`; contexto MEI e planilha |
| 027 Kit por tarball | texto | o pacote virou `@viniciuskoitin` 0.9.0; a ADR, o CLAUDE.md e a skill dizem `@viniciusk` |
| 028 Planos dos Reels | vencida | só um Reel usou (17/10); a régua exigida nunca foi feita |
| 029 Pele em sprites | status | as decisões 1 e 2 já se resolveram na prática; a régua exigida nunca foi feita |
| 030 Trilha | status, parcial | "Decisão (proposta)" no corpo; a regra "trilha obrigatória" entrou sem emenda; cita scripts apagados |
| 031 Perfil de formato | status, parcial | a parte E está parada desde 18/10; "anime em movimento fora" foi superado; "a métrica própria decide" nunca rodou |
| 032 SQLite | ok | |
| 033 Montagem por JSON | parcial | os Shorts passaram ao `motion-video` sem a avaliação que a ADR pedia |
| 034 Tradução e provas | status | "proposta", mas em uso (13 `traducao.json`) |
| 035 SFX | status | "proposta", mas em uso (22 `sfx*.json`) |
| 036 Rotina diária | vencida, texto | roda todo dia e está parada há 7 dias; o texto diz "desligado"; cita `conferir_audio.py` |
| 037 Modelos por área | ok | o teste-gate passa |
| 038 Constantes | ok | o teste-gate passa |
| 039 Proteção pelo review | ok, com lacuna | `translation` não protege os arquivos |
| 040 Etapa por cena | parcial | o código existe, mas só os testes o usam |
| 041 Porta de voz | ok | |
| 042 Contexto e fronteiras | status | as operações propostas não existem; a guarda testa módulos inexistentes |
| 043 Fontes | ok | |
| 044 Ativos | ok | |
| 045 Erros | texto | cita `montar_episodio.py` e `shorts_tec.py`, que foram apagados |
| 046 Entradas do SFX | ok | |
| 047 Briefs e música | ok | |
| 048 Entradas do Short | ok | |
| 049 VoiceKey | ok | texto datado |
| 050 Pacote do gate 4 | ok | |
| 051 Render por porta | ok | cita script apagado |
| 052 Estado da voz | ok | idem |
| 053 Referências de voz | ok | |
| 054 Nivelamento | ok, com lacuna | `voice_polish` desligado à espera da escuta; o limite de 4–5 s não está na ADR |
| 055 Ficção histórica | parcial | aceita a opção C, mas o título e o corpo ainda descrevem a B; o marcador de ficção não existe; o schema exige claims |
| 056 Host por cena | status | "proposta, nenhum vídeo", mas usada no Nietzsche (agendado) e no Jin-woo |
| 057 Preto e branco no B-roll | status | "proposta", mas usada; não está no CLAUDE.md |
| 058 Azure Speech | **condição violada** | ver U1 |
| 059 Plano `cast` | ok | nada implementado; pede o kit 0.12.0 e o template está no 0.9.0; o nome coincide com a cena `cast` do `motion-video` |

## Proposta de arrumação (uma etapa por PR)

1. **Decisões do dono, sem código:** a ADR 058 (ler os termos ou manter os vídeos não listados), a rotina diária
   (pausar o timer ou liberar o download de fontes) e a permissão do `vp postiz *`.
2. **Uma ADR de "fase de crescimento"** que substitua as premissas do §12 e da validação: métricas (API só de
   leitura ou não), recorte, cadência e miniatura escolhida por teste A/B, não pelo canal de referência. Ela
   aposenta, total ou parcialmente, as ADRs 018, 023, 026, 028 e a parte E da 031, e acerta o anime da 031 com a 007.
3. **Limpeza mecânica, sem mudar decisão:** linhas de status, referências cruzadas (016↔024, 008↔055, 031↔007),
   scripts apagados, nome do kit, ADRs fantasmas e o formato do status a partir da 037.
