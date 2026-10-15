# 023 — Legenda palavra a palavra no vertical, com o tempo do Whisper da Groq

- **Status:** aceito pelo dono em 2026-10-14 (três decisões na sessão: alinhador, onde mora o tempo, estilo)
- **Data:** 2026-10-14
- **Etapa do roadmap:** legendas (#17, parte P1), item V1 da qualidade visual do SPEC-WORKFLOW
- **Relaciona-se com:** ADR 014 (legenda queimada no vertical), ADR 016 (voz final), ADR 021 (legenda por frase),
  guia de animação de texto §3

## Contexto

A ADR 021 pôs a legenda por frase no vertical, com o tempo das fronteiras tirado dos silêncios do WAV. O guia de
animação de texto pede a palavra falada acesa (prioridade do dono desde 2026-10-07) e proíbe fingir esse destaque
com o modelo proporcional: precisa de tempo por palavra vindo do áudio. O Kokoro só dá esse tempo no inglês, o
Chatterbox e o Gemini não dão. Três pontos estavam em aberto no guia (§9): quem alinha, onde mora o tempo por
palavra e a identidade visual da legenda.

## Decisão

1. **Quem alinha: o Whisper da Groq, na camada gratuita** (`app/providers/alignment/groq.py`, porta `WordAligner`,
   `word_aligner = "groq"` em `config/providers.toml`). O dono escolheu o remoto ao Whisper local. O WAV de cada
   cena sai da máquina: por isso a chamada só acontece com `--legenda-palavra` no `montar_episodio.py`, pedido na
   sessão (§14). A gravação de referência da voz clonada continua sem sair (ADR 016); o que vai é a narração gerada.
   Custo zero (camada gratuita, `usd_per_call = 0`); cota esgotada para o script e guarda o que já veio.
2. **Onde mora o tempo: `captions.words.json`, ao lado do SRT** (`app/media/word_captions.py`). Por cena: o
   caminho do WAV, as palavras reconhecidas e as palavras do roteiro com tempo, em ms da cena. A cena só é
   reconhecida de novo quando o WAV muda (o nome já leva o hash do texto e da voz). O `episode.json` não muda; o
   adapter do Remotion converte ms em quadros e passa `words` só na cena vertical que tem palavras.
3. **A tela mostra o texto do roteiro, não o do reconhecedor.** As duas listas são casadas sem acento, caixa nem
   pontuação. Palavra do roteiro que não casou (número por extenso que o Whisper escreveu em algarismos, nome
   grafado de outro jeito) divide, pelo tamanho, o tempo entre as vizinhas que casaram, e o script conta quantas
   ficaram assim. Nenhum fato da tela sai do reconhecedor.
4. **Estilo enérgico, só na legenda:** caixa alta, contorno preto grosso, palavra falada em amarelo, blocos de até
   três palavras, troca seca. É a "segunda identidade visual" do guia (§9, item 4), restrita à legenda; o resto do
   template segue o tema `editorial`. A peça é o `WordCaption` do motion-kit (MK-01), consumida pelo SHA fixado.
5. **Sem palavras, legenda por frase.** Cena sem reconhecimento (WAV novo sem `--legenda-palavra`) mostra a legenda
   da ADR 021. A paisagem segue só com a legenda por frase.

## Consequências

- Trocar a voz (rascunho → voz final) pede rodar `--legenda-palavra` de novo: as cenas com WAV novo voltam para a
  legenda por frase até lá, e o script avisa quais.
- Os números aparecem por extenso, como a narração; trocar por algarismos na tela seria tirar texto do
  reconhecedor e fica fora desta decisão.
- O SRT por frase continua sendo o arquivo editável e o que vai no pacote de publicação.
- Uma dependência remota nova na montagem (Groq), opcional e sem custo; nenhuma biblioteca nova.
