# earshot: termos, instalação e primeira medida (2026-10-31)

Ferramenta local que dá "ouvidos" a um agente: descreve áudio, julga se um som bate com uma descrição, mede
eventos, loudness, grade de batidas e sincronia com os cortes de um vídeo, e sintetiza efeitos em código. Decisão
do dono em 2026-10-31: instalar **para os vídeos longos** (trilha do `diretor-musical`, que hoje escolhe sem ouvir,
ADR 030; e cortes na batida quando a música entrar nos Shorts, ADR 035). Não decide nada: é medida e conferência;
o dono continua ouvindo a prévia.

## Licenças (conferidas no repositório)

| Peça | Licença | Onde |
|---|---|---|
| earshot (código) | MIT, © 2026 Leon Lin | `LICENSE` do repositório |
| CLAP `laion/larger_clap_general` @ `16c8cc3` | Apache-2.0 | ficha do modelo no Hub |
| AST `MIT/ast-finetuned-audioset-10-10-0.4593` @ `f826b80` | BSD-3-Clause | ficha do modelo no Hub |

- Repositório: https://github.com/Leonxlnx/earshot, versão `v0.4.0` (commit `591fa3e`, 2026-10-22). Não está no PyPI:
  instala do clone.
- Custo: zero. Roda só em CPU, offline depois do cache; o único comando que sai da máquina é o `llm` (envia
  áudio ao Gemini, só com `GEMINI_API_KEY` e `--yes-upload`), que **não** instalamos (extra `llm` fora).
- Dado pessoal: a voz clonada do dono passa pelos modelos **localmente**; nada é enviado.

## Instalação (ambiente próprio, fora do `auto-play`)

```
~/projetos/earshot/.venv            Python 3.12, torch só-CPU, `pip install -e ".[mcp]"`
~/projetos/earshot/.cache/hf        os dois modelos (~1,1 GB), revisões fixas, safetensors
```

- `.venv/bin/python -m earshot doctor --fetch` baixa os modelos uma vez; depois `EARSHOT_OFFLINE=1`.
- **Origem dos pacotes (2026-10-31):** o PyPI (`pypi.org` e `files.pythonhosted.org`) não respondia desta máquina
  (timeout em IPv4 e IPv6, sem incidente na página de status), e o uv não tinha o `soxr` no cache. Com a
  autorização do dono, a instalação veio do espelho `mirrors.aliyun.com/pypi/simple` (mesmos wheels) mais o
  índice só-CPU do pytorch.org. Quando o PyPI voltar, o `.venv` pode ser refeito pela fonte oficial; os modelos
  vêm do Hugging Face em qualquer caso.
- Cada chamada da CLI carrega os modelos (20–40 s); o servidor MCP (`python -m earshot mcp`) os mantém na memória.
  Registro no Claude Code, quando o dono quiser: `claude mcp add earshot --scope user -e EARSHOT_THREADS=3 --
  ~/projetos/earshot/.venv/bin/python -m earshot mcp`.
- `EARSHOT_THREADS` limita os threads do torch (padrão min(4, núcleos/2)). Na máquina limitada: sonda de CPU antes
  (`cpu_probe()` acima de 0,3 s = medida inválida), como para render e benchmark.

## No pipeline (2026-10-31)

Registrado como servidor MCP do usuário (`claude mcp add earshot --scope user`, offline, 3 threads) e como passo de
conferência: `scripts/provisorio/conferir_audio.py` chama o `timeline` por subprocesso (`app/media/earshot.py`),
com os cortes do `episode.json` (longo) ou do `content.voz.json` (Short, e o `sfx.json` para saber onde havia
efeito), e grava o JSON ao lado do vídeo. `EARSHOT_PYTHON` no `.env` aponta o ambiente.

## Primeira medida (2026-10-31, máquina livre: `cpu_probe` 0,045 s; `EARSHOT_THREADS=4`, bf16, offline)

Cada comando é um processo novo (carrega os modelos, ~30 s dos tempos abaixo). JSONs completos ficaram no
scratchpad da sessão; os números aqui são os do resumo de cada comando.

| Comando | Entrada | Tempo | O que devolveu |
|---|---|---|---|
| `describe` | `ytal-spirit-of-fire.mp3` (608 s, a trilha do Montaigne) | 99 s | "ambient synth pad music" (z +3,2); clima "dreamy and ethereal" (z +3,3) e "dark and tense" (z +2,2), que o próprio comando marca como **não validado** ("errado em ~1 de 5 faixas no teste"); AudioSet Music 0,83, Ambient 0,69. −19,0 LUFS, pico −4,4 dBFS. No catálogo o dono etiquetou `calmo, inspirador`, intensidade 3. |
| `match` | mesma faixa × "calm instrumental background music without vocals", alternativas "energetic rock with vocals" e "ambient drone" | 8,6 s | **weak** (z +2,0, cosseno 0,30, #9 entre 322 descrições); na escolha forçada, "ambient drone" ganha (p 0,92, z +3,1) e "energetic rock" perde (z +0,7). Descrição de música é "unvalidated" para o próprio earshot. |
| `timeline` | `montaigne-desapego/renders/final.mp4` (702 s, estéreo) com os 13 cortes de cena como `--cues` | 146 s (0,21× o tempo real; cortes de vídeo 45 s, loudness 24 s, seções 25 s) | −14,1 LUFS integrado (igual ao nosso ebur128), pico real −0,7 dBTP (o encoder AAC passa do −1,5 do loudnorm; "fine for a delivered file"). **Sem grade de batidas** (clareza de pulso 0,01 < 0,15): a faixa é ambiente, não dá para cortar na batida com ela. 204 quedas de nível = as pausas da fala. 92 cortes detectados por diferença de quadro (os planos dentro das cenas) contra os 13 de cena. Sincronia com os 13 cortes de cena: 54% têm um ataque a até 40 ms (acaso 42%), mediana 33 ms; 2 sem som nenhum (6:13,66 e 10:47,83). Etiquetas das seções erradas ("funk music, vocal chop" num pad ambiente com narração): o earshot avisa que as etiquetas "são frequentemente erradas em música e voz". |
| `timeline` | `short-lista-ligada-pt/renders/final-sfx.mp4` (38 s, **mono**, 13 efeitos da ADR 035) com os 4 cortes | 37 s (~1× o tempo real) | **Os 4 cortes têm um ataque a até 1 quadro (mediana 20 ms) e um acento forte (≥ 29 dB sobre o fundo), onde o acaso daria 31% e 7%.** Os efeitos do plano caíram onde o `juntar --sfx` os pôs. Loudness **−12,0 LUFS** integrado, pico real −1,5 dBTP. |

### O que a medida mostrou

1. **A loudness dos Shorts mono está 3 dB acima do que o nosso check diz.** O `juntar` grava um canal só e o
   `ebur128` do ffmpeg mede esse canal (−15,0). O earshot mede o mono "como se tocado nos dois alto-falantes"
   (BS.1770), que é o que o YouTube faz, e dá −12,0. No vídeo estéreo (Montaigne) os dois concordam (−14,1).
   Proposta: o `juntar` sair em estéreo (o mesmo canal nos dois lados) ou o alvo do mono descer 3 dB. Os Shorts
   já publicados estão a −12 efetivos; o YouTube abaixa, não há dano, mas a medida do pipeline estava errada.
2. **Sincronia dos efeitos confirmada por medida**, não só pela conta: no Short, 100% dos cortes com ataque a
   1 quadro. É o check que a ADR 035 previa para o earshot; o custo foi 37 s por Short.
3. **Cortar na batida pede faixa com batida.** `Spirit of Fire` não tem pulso; para o passo "cortes na batida" o
   catálogo precisa de faixa com `bpm` (o `catalog.json` já tem o campo), e o earshot entrega a grade.
4. **Julgar música é o ponto fraco dele**, e ele mesmo diz. Serve como segunda opinião ao lado das etiquetas do
   dono (aqui, "calmo" não foi contradito; "inspirador" não encontrou eco), não como decisor.
5. **Custo por vídeo:** ~0,2× o tempo real num longo de 12 min (2,5 min), ~1× num Short, com a máquina livre.
   Viável como check depois do `juntar`; não como coisa a rodar a cada iteração.
