# Comparação das referências de voz por cena

Foram geradas 12 falas reais no Modal pelo mesmo fluxo de voz dos Shorts. Em cada idioma, todos os trechos dizem a mesma frase. A referência antiga usa a entrega neutra; os demais usam as referências e os parâmetros de produção de cada delivery. A comparação não isola somente o efeito da gravação.

Os arquivos foram concatenados com pausas de 0,75 s, preservando os WAVs gerados, sem normalizar ou alterar sua velocidade. A escuta do dono continua pendente. Não é um vídeo aprovado para publicação.

**Aprovação posterior:** o dono aprovou a comparação nivelada dos dois idiomas na
conversa: "Gostei, me parece adequado agora". A pendência de escuta acima descreve
o estado inicial, anterior ao nivelamento. Registro em `nivelamento.verificacao.json`;
isso não aprova vídeos novos ou publicação.

**Versão preferida para escuta: comparação nivelada.** Após o dono apontar a voz neutra
baixa, foram medidas as 12 falas. A neutra em pt-BR estava em −28,14 LUFS e a referência
antiga em −13,45 LUFS. Cada trecho agora foi nivelado separadamente, com alvo de
−16 LUFS e teto de pico de −1,5 dBTP, antes de montar uma nova comparação. Os resultados
ficaram entre −15,83 e −16,53 LUFS. Nenhuma fala foi regenerada e os originais permanecem
intactos. Medições e arquivos em `nivelamento.verificacao.json`.

Após o relato de áudio quebrado, foram criadas cópias em MP3 (160 kb/s, 48 kHz,
estéreo) para testar a reprodução. WAVs, MP3s e as 12 falas individuais passaram
na decodificação completa; a concatenação preserva exatamente as amostras de cada
fala. Isso não confirma a qualidade perceptiva nem corrige possíveis defeitos da
síntese. Registro técnico: `reproducao.json`.

## pt-BR

[Ouvir MP3 nivelado](comparacao.nivelada.pt.mp3) · [WAV nivelado](comparacao.nivelada.pt.wav) · [WAV original](comparacao.pt.wav)

| Posição | Tom / referência | Início | Fim |
| --- | --- | --- | --- |
| 1 | referência antiga | 0.00 s | 6.48 s |
| 2 | neutral | 7.23 s | 12.11 s |
| 3 | hook | 12.86 s | 18.78 s |
| 4 | calm | 19.53 s | 25.89 s |
| 5 | turn | 26.64 s | 34.24 s |
| 6 | invite | 34.99 s | 41.51 s |

## en

[Ouvir MP3 nivelado](comparacao.nivelada.en.mp3) · [WAV nivelado](comparacao.nivelada.en.wav) · [WAV original](comparacao.en.wav)

| Posição | Tom / referência | Início | Fim |
| --- | --- | --- | --- |
| 1 | referência antiga | 0.00 s | 4.60 s |
| 2 | neutral | 5.35 s | 10.39 s |
| 3 | hook | 11.14 s | 16.82 s |
| 4 | calm | 17.57 s | 24.05 s |
| 5 | turn | 24.80 s | 32.96 s |
| 6 | invite | 33.71 s | 38.91 s |

As referências foram sincronizadas no volume privado e seus hashes conferidos. A reexecução de `vp short voz` reutilizou todos os WAVs dos dois idiomas, sem alterar bytes ou datas dos arquivos. Os vídeos publicados continuam com seus hashes originais.

Configuração: `config/providers.toml`, tabelas `[chatterbox.references]`. Cadastro e uso: `docs/guia-gravacao-referencias-voz.md`. Decisão técnica: ADR 053.

Verificação técnica: 1.487 testes passaram (8 desmarcados), Mypy passou em 467 módulos e Ruff passou. A última correção foi apenas de espaçamento no bloco de imports; os resultados de testes e tipagem permanecem válidos.
