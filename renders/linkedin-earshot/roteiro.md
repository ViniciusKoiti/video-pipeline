# Roteiro: Dei ouvidos ao meu agente (LinkedIn, pt, 2026-11-09)

Pauta: `data/episodes/linkedin-earshot-pt/pauta.md`. Falas: `data/episodes/linkedin-earshot-pt/narracao.pt.json`
(8 falas, ~79 s a 2,2 palavras/s; 5 de 8 neutras = 62%: 1 `hook`, 1 `turn`, 1 `invite`). Rascunho: sem voz nem render.

## A lição em uma frase (dita na fala das cenas `medida`, `decisao` e `etapa`)

Quem monta o vídeo por código só sabe o que o código calcula: uma medida independente do arquivo final acha o que a
conta não vê (3 dB), e ainda assim só mede, quem aprova é quem ouve.

## Origem de cada número e afirmação

Todos vêm de `data/benchmarks/termos-earshot.md` ("Primeira medida", 2026-10-31, `cpu_probe` 0,045, earshot v0.4.0,
modelos offline), feita pelo dono. Nenhum número é novo e nada foi medido hoje.

| Fala | Afirmação | Origem |
| --- | --- | --- |
| `gancho` | O Short que o agente montou estava 3 dB mais alto do que a conta dizia (−15,0 × −12,0); ninguém na linha escuta o resultado | Mesmo `timeline` de `medida` (−15,0 ffmpeg; −12,0 earshot mono) e `vp short` (`tempos`, `render`, `juntar`; ADR 035). Abertura fria trocada em 2026-11-09 a pedido do dono (antes: "Meu agente escreve o JSON, o código renderiza e junta a voz…") |
| `ouvidos` | earshot é aberto, do Leon Lin, roda na máquina, sem rede | `termos-earshot.md`: MIT, © 2026 Leon Lin, só CPU, offline depois do cache; o único comando de rede (`llm`) não está instalado |
| `medida` | O ffmpeg media o Short em −15 LUFS; o earshot conta o mono nos dois alto-falantes, como o YouTube, e deu −12 | `timeline` do `short-lista-ligada-pt/renders/final-sfx.mp4` (38 s, mono): ebur128 −15,0; earshot −12,0 (BS.1770, mono nos dois alto-falantes) |
| `decisao` | 3 dB que a conta não via; o `juntar` passou a sair em estéreo; o mesmo Short, refeito, mede −14,2 | −15,0 → −12,0 = 3,0; decisão do dono de 2026-10-31 (estéreo antes do `loudnorm`); `data/episodes/short-lista-ligada-pt/renders/final-sfx.mp4.earshot.json` (2026-10-31 17:54, `ffprobe`: aac, 48 kHz, **2 canais**): `loudness.integrated_lufs` −14,2, `true_peak_dbtp` −1,5, `lra_lu` 4,4. Montaigne (estéreo, 702 s) já dava −14,1 nos dois medidores |
| `cortes` | O som entra a até um quadro nos quatro cortes do Short | Mesmo JSON, `sync.cuts`: 4 cortes (5,2 / 15,6 / 24,6 / 31,6 s), deslocamento do ataque +26, −6, +27 e −27 ms, `hit_within_1_frame` 1,0 (acaso 0,308), mediana 26,5 ms, 1 quadro a 30 fps = 33,3 ms; sons: "chat message pop", "short swish", "glockenspiel note" (o 4º sem rótulo) |
| `limite` | Em música ele erra e avisa; a trilha calma deu `weak`; uso como segunda opinião | `match` de `ytal-spirit-of-fire.mp3` × "calm instrumental background music without vocals": **weak** (z +2,0); o earshot marca descrição de música como "unvalidated"; "Julgar música é o ponto fraco dele, e ele mesmo diz" |
| `etapa` | Critérios: −15 a −13 LUFS, pico real até −1,0 dBTP, sem silêncio de 0,5 s no meio da fala | Skill `short-diario`, passo 8 (`vp audio`); a fala diz "pico até menos um" (−1,0 dBTP) |
| tela, `etapa` | ~1× o tempo real num Short, ~0,2× num longo | `termos-earshot.md`: 37 s para 38 s de Short; 146 s para 702 s de longo |
| tela, `fecho` | Cartão "ainda não usei: forge, fit, banco de sons" | README do earshot (`forge`, `fit`, `sfx`); o dono não os usou, e não há medida dele |

Cuidado de redação: o **−14,2** é o do mesmo Short `lista-ligada` refeito em estéreo (31/10); a fala não diz que
todos os Shorts publicados medem isso (os anteriores a 31/10 ficaram como estavam, mono). O `−12,0` do antes está só
em `termos-earshot.md` (o arquivo mono foi substituído). A mediana dos cortes na primeira rodada (mono) foi 20 ms; o
vídeo usa a do arquivo estéreo final, **26,5 ms**.

## Pronúncia a conferir na escuta (glossário em `voice/glossary.json`)

`earshot` → "írshót", `Leon Lin` → "Líon Lin", `Short` → "xórt", `YouTube`, `ffmpeg`, `LUFS`, `JSON`, `pipeline`,
`mono`. O dono ouve antes do render (sem chamada ao Modal até ele pedir).

## Link e crédito

O repositório `github.com/Leonxlnx/earshot` é público: o link vai no primeiro comentário, não na fala. O texto do post
credita o autor e a licença (MIT) e diz que a voz é clonada e que a janela é um desenho a partir de fotos do dono
(divulgação de conteúdo sintético; marcação no Studio/LinkedIn é do dono).
