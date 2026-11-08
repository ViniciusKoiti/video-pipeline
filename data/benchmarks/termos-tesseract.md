# Termos do Tesseract (OCR local, consulta de 2026-11-07)

Motor de OCR que roda na máquina: sem conta, sem chave e sem chamada a serviço. Usado só pelo teste
`scripts/bench/ocr_quadros.py` (conferência de texto na tela). Nada foi enviado para fora da máquina.

## Conferido na fonte

- **Licença do Tesseract:** Apache License 2.0. Lido em
  https://raw.githubusercontent.com/tesseract-ocr/tesseract/main/LICENSE em 2026-11-07 ("Apache License, Version 2.0,
  January 2004").
- **Dados de idioma em português** (`por.traineddata`, pacote Ubuntu `tesseract-ocr-por`): Apache License 2.0. Lido em
  https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/LICENSE em 2026-11-07.

## Instalação usada no teste

- Sem root e sem mexer no sistema: os pacotes do arquivo do Ubuntu foram baixados com `apt-get download` e extraídos
  com `dpkg -x` em `data/cache/ocr-kira/root/` (fora do Git).
- Pacotes: `tesseract-ocr` 5.5.0-1build1, `tesseract-ocr-por` 4.1.0-2build1, `libtesseract5`, `libleptonica6`,
  `libarchive13t64` (versões do arquivo na época da consulta).
- Não há instalação no sistema. Para rodar:
  `LD_LIBRARY_PATH=<raiz>/usr/lib/x86_64-linux-gnu TESSDATA_PREFIX=<raiz>/usr/share/tesseract-ocr/5/tessdata`.

## Efeito no projeto

- Só entra como dependência se a medição (`data/benchmarks/ocr-quadros-kira-2026-11-07.md`) justificar, com a licença
  acima registrada e a justificativa no commit (CLAUDE.md §2.9).
- Roda na CPU: só com a sonda `cpu_probe()` abaixo de 0,3 s (CLAUDE.md §3).
