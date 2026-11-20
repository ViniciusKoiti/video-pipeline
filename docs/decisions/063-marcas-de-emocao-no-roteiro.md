# 063 — Marcas de emoção no roteiro e voz MAI do Azure com estilo por trecho

- **Status:** aceita (2026-11-18). O dono aprovou o desenho e decidiu: "precisamos utilizar a voz do Caio a partir de agora para esse tipo de vídeo" (ensaios do Cena e Conceito e Shorts cortados deles).
- **Data:** 2026-11-18
- **Relaciona-se com:** ADR 015 (pausas na frase), ADR 022 (entrega por cena), ADR 041 e 049 (cache e nomes da voz),
  ADR 053 (referências por entrega), ADR 058 (voz do Azure), ADR 062 (conferência da fala)

## Contexto

O dono achou a narração "sem sentimento". A voz clonada (Chatterbox, ADR 016 e 024) tira a emoção quase só da
gravação de referência, e a maior parte das cenas usa a entrega `neutral` (ADR 022). Em 2026-11-18:

- A pesquisa de mercado (`reports/Mercado de vozes para narração.md`) mostrou que o Chatterbox foi aposentado pela
  Resemble em agosto de 2026 e que nenhum placar mede pt-BR.
- O teste em `data/benchmarks/voz-azure-mai-2026-11-18/` comparou a voz atual com as vozes MAI-Voice-2.1 do Azure,
  com estilo por trecho (`mstts:express-as`). O dono achou o **Caio** "muito legal", mas com nomes errados.
- No mesmo teste, `<sub alias="…">` corrigiu o "Kira" sem mudar o ritmo, e `<phoneme alphabet="ipa">` esticou a
  palavra para quase 2 s (`caio-pronuncia/`).
- A região do recurso (`brazilsouth`, camada F0) não lista as vozes MAI em `voices/list`, mas aceitou
  `pt-BR-Caio:MAI-Voice-2.1` pelo nome; um nome inventado dá HTTP 400.

O dono pediu que a direção de emoção entre no roteiro, por trecho, como `<raiva>…</raiva>`, e que a mesma marcação
sirva a qualquer motor de voz.

## Decisão

1. **Marcas de emoção na narração.** Lista fechada, em português e sem acento, abrindo e fechando em volta de uma
   frase ou oração: `raiva`, `sussurro`, `suspense`, `surpresa`, `tristeza`, `esperanca`, `firme`, `acolhedor`,
   `arrependimento` e `empolgacao`. O trecho sem marca usa a entrega da cena (`delivery`, ADR 022).
   - **Erro no `vp check`:** marca fora da lista, marca que não fecha, uma marca dentro da outra, marca vazia.
   - **Atenção no `vp check`:** marca com menos de três palavras (cada corte reinicia a entonação) e mais de duas
     marcas numa cena.
   - `<short pause>` continua valendo, inclusive dentro de uma marca.
2. **O texto sem marcas** vai para as legendas, a tela, a contagem de tempo dos planos e o editor e o verificador
   (a marca muda como a voz fala, não o que a fala afirma). A função que hoje tira a pausa passa a tirar as duas.
3. **Cada motor traduz a marca do seu jeito.**
   - **Azure:** a marca vira `<mstts:express-as style="…">` pela tabela `[azure_speech.styles]` do
     `config/providers.toml` (de partida: raiva→angry, sussurro→whispering, suspense→fearful, surpresa→surprised,
     tristeza→sad, esperanca→hopeful, firme→determined, acolhedor→softvoice, arrependimento→regretful,
     empolgacao→excited). Voz sem estilo (ex.: `pt-BR-AntonioNeural`) ignora a marca.
   - **Chatterbox e Kokoro:** nesta versão tiram as marcas e falam na entrega da cena. A biblioteca de referências
     por emoção (uma gravação do dono por marca) fica para uma emenda.
4. **Voz MAI no Azure.** `[azure_speech] voices` aceita `pt-BR-Caio:MAI-Voice-2.1`. Com voz MAI, o glossário
   (`voice/glossary.json`) entra pela grafia da `fala` (o texto já vai reescrito, como nas vozes sem IPA) em vez de
   `<phoneme>` (campo `pronunciation = "fala"`; `"ipa"` continua o padrão das vozes neurais). O `<sub alias>`
   testado faz o mesmo efeito e fica de reserva. A voz final do projeto (`tts_final`) continua a clonada; os
   ensaios do Cena e Conceito e seus Shorts usam `--voz azure_speech`.
5. **O resto do caminho não muda:** nivelamento (ADR 054), conferência pelo Whisper (ADR 062), legendas pela fala
   real e render.

## Consequências e riscos (decisão do dono, avisada uma vez)

- **Prévia:** o MAI-Voice-2.1 está em "public preview", "not recommended for production workloads"; a voz pode
  mudar quando sair da prévia. O cache da voz (ADR 041) já inclui a voz e o SSML, então uma mudança refaz as falas.
- **Não é a voz do dono:** o código de conduta do Azure exige avisar que a voz é sintética, e o YouTube pede o rótulo
  de conteúdo alterado ou sintético quando a voz não é a do criador. O aviso entra na descrição e no Studio
  (checklist de publicação).
- **Custo:** a conta na F0 aceitou as vozes MAI no teste; se a Microsoft cobrar, a estimativa é de US$ 2 a 4 por mês.
  O dono decide (decisão de 2026-11-18 sobre custo e risco).
- **Ritmo:** as falas com estilo saem 15% a 40% mais longas que as da voz clonada; o tempo das cenas sai do WAV real,
  como sempre.

## Fora desta decisão

A biblioteca de referências por emoção no Chatterbox, o treino do modelo com a voz do dono e outros motores com
emoção embutida (Gemini, ElevenLabs, Higgs), que poderão ler as mesmas marcas por adapter próprio.
