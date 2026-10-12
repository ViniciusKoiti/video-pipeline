# Termos do Chatterbox (Resemble AI), voz clonada local (ADR 016)

Modelo local, sem conta, sem chave e sem chamada a serviço: nada é enviado para fora da máquina. Usado pelo
adapter `app/providers/tts/chatterbox.py`, num ambiente Python próprio.

## Conferido na fonte

- **Licença do modelo geral:** MIT. Cartão `https://huggingface.co/ResembleAI/chatterbox`, lido em 2026-10-12:
  metadado `License: mit` e, no texto, "Licensed under MIT". O cartão cobre o "Chatterbox Multilingual V3".
- **Licença do repositório e do ajuste de português do Brasil:** MIT, conferidas em 2026-10-11 (ADR 016):
  `resemble-ai/chatterbox` e `ResembleAI/Chatterbox-Multilingual-pt-br`.
- **Marca d'água:** o cartão tem a seção "Built-in PerTh Watermarking for Responsible AI" e lista "Watermarked
  outputs": todo áudio gerado sai marcado como sintético.
- **Português:** o cartão lista "Brazilian Portuguese" e "Portugal Portuguese" entre os ajustes de um idioma só.
  O adapter usa o modelo geral (`v3`) com o idioma `pt`; o ajuste de pt-BR não foi testado.

## Efeito no projeto

- Custo zero e sem cota (§2.1). A voz é sintética: a divulgação no upload (§12) não muda.
- A gravação de referência é dado pessoal do dono: fora do Git, em `CHATTERBOX_REFERENCE`, nunca enviada a
  provedor remoto.

## Medido (2026-10-12, CPU, 12 threads, sonda de 0,05 s)

| Fala | Áudio | Tempo |
|---|---|---|
| Primeira fala depois de carregar o modelo | 3,4 s | 180 s |
| Segunda fala | 6,8 s | 194 s |

Ritmo: 12,9 e 14,4 caracteres por segundo. Falta medir um episódio inteiro.
