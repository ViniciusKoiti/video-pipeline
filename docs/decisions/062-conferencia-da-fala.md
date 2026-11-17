# 062 — Conferência da fala depois da voz: Whisper local, folha de escuta e nova tomada por cena

- **Status:** aceito pelo dono em 2026-11-16 ("vamos alterar para seguir esse padrão"; recomendação (a): Whisper
  local). Falta a primeira rodada real, que precisa do modelo no cache (download de ~1 GB, uma vez).
- **Data:** 2026-11-16
- **Pedido do dono:** os erros de fala do `vazio-de-ter-tudo` (publicado em 15/11): "Empty Man saiu como 'em Man'",
  "Oath saiu como 'Wolf'", Thorfinn e Einar oscilando, e "sem curso de ligação", "não tira a care".
- **Relaciona-se com:** ADR 016 e 024 (voz clonada), ADR 023 (palavras com tempo), ADR 041 e 049 (porta de voz e
  nomes dos WAVs), ADR 052 (estado da voz por cena), ADR 054 (cópia nivelada), ADR 058 (Azure, `ipa`).

## Contexto

O glossário do episódio existia e foi aplicado: o hash de cada WAV confere com o texto já trocado ("Tórfin",
"Êinar", "ôuf", "én émpti mén") nas 9 cenas com esses termos. A falha não foi falta de trava antes da síntese, e
sim duas coisas depois dela:

1. a voz clonada (Chatterbox) não segue a grafia de forma estável, e ainda troca palavras comuns; e uma grafia do
   glossário ("ôuf") já soa como "Wolf";
2. ninguém ouviu as cenas com nomes antes de montar.

A transcrição usada na crítica também é reconhecimento automático, que erra nome estrangeiro; por isso a conferência
aponta trechos para ouvir, não aprova nem reprova sozinha.

## Decisão

1. **Reconhecedor local.** Adaptador `whisper_local` da porta `WordAligner` (`app/providers/alignment/whisper_local.py`),
   pelo `transformers` na CPU, com o modelo `openai/whisper-small` (apache-2.0, `model.safetensors` de ~967 MB,
   conferido no cartão do modelo em 2026-11-16). Escolhido em `providers.toml` por `speech_check`. O modelo vem do
   cache do Hugging Face: `uv run hf download openai/whisper-small` uma vez; sem ele, o adaptador para com esse
   comando e não baixa nada sozinho (`vp voice` roda com `HF_HUB_OFFLINE=1`). O áudio não sai da máquina.
2. **Sem o texto esperado.** A conferência chama o reconhecedor sem `prompt`: o texto do roteiro levaria o Whisper a
   escrever o nome certo mesmo quando a voz o disse errado.
3. **Comparação** (`app/pipeline/speech_review.py`), cena a cena, contra o roteiro sem as marcas de pausa:
   - termo do glossário: o ouvido no lugar dele precisa lembrar a grafia ou a `fala` (sem acento, sem "h" e sem
     letra dobrada; semelhança de pelo menos 0,75), senão é diferença do tipo `termo`;
   - palavra comum trocada ou faltando com quatro letras ou mais é diferença do tipo `palavra`; as curtas e os
     números escritos com algarismo são ruído do reconhecedor.
4. **`vp voice <id> --conferir`** ouve o WAV que vai ao vídeo (a cópia nivelada, já na velocidade de
   `voice/ritmo.json`), grava `voice/conferencia.json` e, se houver diferença, a folha de escuta
   `voice/conferencia-escuta.wav`: os trechos na ordem da lista, com folga de 0,7 s e 0,9 s de silêncio entre eles.
   Sozinho, não gera fala.
5. **`vp voice <id> --voz-final --refazer S06 S43`** guarda a fala atual dessas cenas, nesta voz, com as cópias
   nivelada e com pausas, em `voice/tomadas-recusadas/<data>/` (nada é apagado) e gera outra tomada. A cópia
   nivelada nova tem outro nome, e a legenda é refeita no próximo render.

## Fora desta decisão (propostas)

- **Melhor de N** nas vozes generativas (Chatterbox, Gemini): gerar 2 ou 3 tomadas só das cenas com termo do
  glossário e ficar com a que a conferência entende melhor. Gasta tempo de GPU no Modal do dono: decisão dele.
- **Velocidade 0,75:** comparar a conferência do WAV bruto com a da cópia lenta, para saber se a desaceleração
  borra consoantes ("custo" → "curso").
- Por voz: no Azure, `ipa` obrigatório em todo termo (fonema exato, saída determinística); grafia testada na
  conferência para a voz clonada; título estrangeiro dito uma vez ou em português na narração, com o original na
  tela (vale para qualquer voz). Vão para a etapa seguinte, com o aviso de termo sem glossário no `vp check`.

## Consequências

- `transformers>=5.17,<6` declarado no extra `tts` (Apache-2.0; já vinha instalado com o Kokoro).
- `Context.speech_checker`, `ProviderChoice.speech_check`, `Settings.whisper_local`, registro `whisper_local` em
  `word_aligner`; `tests/test_speech_review.py` e `tests/test_voice_conferir.py` usam reconhecedor e pipeline falsos.
- `app/pipeline/voice_timeline.py` ganha `voiced_paths`; `app/media/listening_sheet.py` monta a folha com o ffmpeg.
- O adaptador também serve à porta da legenda palavra a palavra, mas ignora o `prompt`; trocar `word_aligner` para
  ele é outra decisão.

## Emenda (2026-11-16): a trava antes da voz

Mesma decisão do dono. O `vp check` ganha a trava fonética do `CLAUDE.md` §6 (`app/pipeline/glossary_check.py`):

- **Termo de fora sem glossário** (narração em pt-BR): sigla, `w`/`y`/`k`, `th`/`sh`/`ph`/`ck`/`tz`/`gh`, letra
  dobrada fora de `rr` e `ss`, ou fim de palavra que o português não tem. Entrada de várias palavras cobre cada
  uma. Sai como ponto de `atenção`. No `vazio-de-ter-tudo` sem glossário, acha Vinland, Empty, Thorfinn, Oath e
  CVV, sem falso positivo nas 57 cenas; Einar, sem traço, escapa (a conferência depois da voz pega). Na
  varredura dos 48 roteiros de `data/episodes` (2026-11-17), os falsos positivos foram letra solta ("opção C"),
  ordinal ("1º"), palavra entre aspas simples ("'bom'"), CAIXA ALTA de ênfase ("SIM", com "sim" no mesmo
  roteiro) e "sob"/"pizzaria"; saíram. O que sobra é nome e palavra de fora (Kira, Marcovitch, software,
  holding) ou sigla brasileira (PIB, IBGE), que a regra do §6 também manda pôr no glossário.
- **Voz final do Azure:** termo com letra e sem `ipa` é ponto de `atenção` (o `vp check` recebe a voz final da
  configuração).
- **Dois-pontos que abrem pergunta** sem `<short pause>` logo depois: alerta (S31, S35 e S57 do episódio; S35 é
  o "pensea como é que é" da crítica).
- **Título estrangeiro dito uma vez**, ou em português na narração com o original na tela: regra da skill
  `roteiro-explicativo`, sem conferência em código (nome de personagem se repete com razão; título, não).
