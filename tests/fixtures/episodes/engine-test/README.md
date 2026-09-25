# Fixture `engine-test` — roteiro de teste do experimento de motor (etapa 6)

Trecho real de ~52 s sobre a Lady Franklin Bay Expedition (Greely, 1881–84), usado como entrada
idêntica para comparar ffmpeg puro, MoneyPrinterTurbo e Remotion (etapas 7–9). Conteúdo **real**:
fontes em domínio público, fotos com licença registrada, narração local (Kokoro, voz `am_michael`).

| Cena | Visual | Origem | Licença |
|---|---|---|---|
| S01 | Proteus no porto de Godhavn, 1881 | George W. Rice / Library of Congress, via Commons | PD-US |
| S02 | Proteus na Discovery Harbor, Fort Conger ao fundo, ago. 1881 | Rice / LoC LC-USZ62-136192, via Commons | PD-US |
| S03 | Linha do tempo 1882–1883 | tela gráfica do projeto (ffmpeg, DejaVu Serif) | Original |
| S04 | Proteus na manhã de 23/07/1883 (vertical) | U.S. Army Signal Corps 111-SC-91135, via Commons | PD-US |
| S05 | Os seis sobreviventes a bordo do Thetis, jul. 1884 (vertical) | Signal Corps 111-SC-96236, via Commons | PD-US |

## Como foi feito (2026-09-25)

1. Fontes: OCR do Internet Archive (`threeyearsofarct01gree`, `rescueofgreely00schl`); trechos numerados
   transcritos em `sources/` com hifenização desfeita e erros óbvios de OCR corrigidos.
2. Fotos: API do Commons (metadados e SHA-1 conferidos no download); descartadas duas da NOAA sem autor
   e uma da LoC cujo título não correspondia à imagem. Redimensionadas (máx. 2560 px) e reencodadas
   (JPEG q5); `sha256` de cada arquivo final no JSON do ativo. `loc.gov` bloqueia acesso automatizado.
3. Roteiro, fontes e ativos aprovados por Vinicius Koiti (`review.json`, gates 1–3).
4. Narração: `KokoroTTS` por cena; durações medidas com ffprobe. `captions.srt` é provisório:
   frases distribuídas proporcionalmente ao número de palavras (o alinhamento real é a etapa 17).

## Limites conhecidos

- Cada fato principal tem **uma** fonte (viagem: Greely; resgate: Schley). Suficiente para testar
  motor; um episódio real exige duas fontes independentes no gate 1.
- A voz **não** foi aprovada por humano (não há entrada `voice` no `review.json`).
- S04 e S05 são verticais: o motor precisa recortar/mover sem cortar o assunto (§9).
