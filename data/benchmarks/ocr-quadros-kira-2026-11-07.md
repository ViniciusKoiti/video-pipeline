# OCR dos quadros do Kira (2026-11-07)

Teste do conferidor de texto na tela (a lacuna "conferir o texto na tela" do fluxo). Script:
`scripts/bench/ocr_quadros.py`. Saída (JSON e quadros) em `data/cache/ocr-kira-voto-brasil/`, fora do Git.
Vídeo: `data/episodes/kira-voto-brasil/renders/final.mp4` (1920×1080, 30 fps, 378,9 s), render de 2026-10-20.
Nada foi renderizado no teste; só se leram quadros de um vídeo que já existia.

## Ambiente

- Tesseract 5.5.0, idioma `por`, psm 11. Instalação local, sem root (`termos-tesseract.md`).
- Sonda de CPU: entre 0,065 e 0,102 s nas três rodadas (antes da v1, na v1 e na versão final). Máquina livre.
- Tempo da versão final, 1×: 61 s para 23 quadros (inclui a extração com ffmpeg). Pico de memória dos processos
  filhos: cerca de 214 MB.

## Quadros

23 planos com texto na tela: 13 `keyword`, 4 `number`, 3 `lower_third`, 1 `quote`, 2 `compare`. Um quadro por plano,
em 60% da duração do plano.

## Resultado da versão final (1×)

| Tipo de plano | Quadros | Alertas | Cobertura média |
|---|---|---|---|
| keyword | 13 | 0 | 1,00 |
| number | 4 | 0 | 1,00 |
| lower_third | 3 | 0 | 1,00 |
| quote | 1 | 0 | 1,00 |
| compare | 2 | 2 | 0,94 |

Os dois alertas são leitura errada de número, com a tela certa. Conferido a olho nas imagens:

- S20 (quadro `13-S20-compare.png`): a tela mostra "73%" e o OCR leu "13%".
- S37 (quadro `23-S37-compare.png`): a tela mostra "55%" e o OCR leu "99%".

Nenhum dos dois é defeito de render. São erros do OCR em dígitos grandes e em negrito.

## Como a versão chegou aqui

- **v1 (regras iniciais), 6 alertas.** Revisados a olho:
  - 6 `perto_da_borda`, todos de ruído: o "E," do fundo escuro (S08) e o rodapé "Fonte: …" (S02, S15, S17, S22, S29).
    Corrigido: o teste de borda só olha palavras do texto esperado.
  - 1 `faltando` na citação (S17, quadro 12). O script esperava a atribuição "Tabela 72, 10º Anuário…", que o cartão
    não mostra: o cartão traz "Fonte: Fórum Brasileiro de Segurança Pública" no rodapé. Erro do meu mapeamento, não do
    vídeo. Corrigido: a citação compara só o texto. Nesse quadro, a 60% do plano, o destaque amarelo ainda estava sendo
    desenhado, o que também derruba a leitura.
- **Versão final (1×), 2 alertas**: os dois números de comparação acima.
- **Escala 2× (`--escala 2`), 4 alertas.** Não corrige os dois números (73 e 55 continuam errados) e cria um alerta
  novo no rótulo de S22 ("crime" e "2020" não lidos). Por isso o padrão continua 1×.

## O que o teste não mede

- **Recall.** Nenhum defeito conhecido foi colocado no render (texto cortado, número trocado, erro de digitação).
  Não sabemos quantos defeitos reais o OCR pegaria. Próximo passo: injetar defeitos em quadros de teste (imagem,
  sem render de vídeo) e medir.
- **Quadro único em 60% do plano.** Não cobre a entrada nem a saída da animação, nem texto que some antes.
- **Fonte e rodapé.** Não são checados (o rodapé não entra no texto esperado).
- **Texto sobre fundo ruidoso.** Em S29, a escala 2× gerou 40 palavras fora do texto esperado (rodapé e ruído do
  fundo, entre elas). Essas palavras não entram no alerta de borda, mas pesam na confiança da leitura.

## Leitura

- O OCR lê bem texto corrido e rótulos: 4 de 4 números em cartões simples e todas as palavras de keyword, rótulo e
  citação, depois das correções.
- Erra dígito grande em negrito e em comparação: 2 de 4 números em `compare`. Essa é a parte que mais importa, porque
  é número na tela.
- Como alerta de sanidade, funcionou: achou os dois números que não batiam e custou duas olhadas. O custo é o falso
  alarme nos cartões de comparação, que precisariam de leitura própria antes de virar gate.

## Proposta (não aprovada)

- Integrar o OCR à prévia como alerta, com número e cobertura, sem bloquear o gate 4.
- Antes disso, medir o recall com defeitos injetados.
- A dependência entra só com aprovação do dono, com a licença já registrada em `termos-tesseract.md`.
