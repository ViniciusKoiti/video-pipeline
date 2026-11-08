# Versão em inglês do fluxo de concorrência em C

Tradução da versão portuguesa publicada: `../final.pt.fluxo.mp4`.
Produção independente em `data/episodes/short-concorrencia-fluxo-en/`;
os arquivos aprovados em português permanecem preservados.

Sete cenas, com voz clonada em inglês, abertura/fecho e textos dos diagramas traduzidos.
Os tempos foram ajustados à fala inglesa: 47,6 s no total. Os resultados da medição
e as afirmações técnicas são os mesmos do original; não houve novo benchmark.
Fontes e limites: `../explicacao/fontes.md` e `../demo/resultado.txt`.

## Plano das animações

| Cena | Estado e transição | Fonte |
| --- | --- | --- |
| codigo | Contador compartilhado 10; ambos leem 10; cada um soma e grava 11; resultado 11, uma atualização perdida. Exemplo ilustrativo; a fala e a tela explicitam comportamento indefinido em C. | C11/DEMO, plano português |
| mutex | A entra no trecho protegido; B espera a mesma trava; A libera e B entra. | MUTEX/DEMO |
| atomic | READ, ADD e WRITE numa operação indivisível; contador passa de 10 para 11 e 12. | C11/DEMO |

O plano completo e os trechos de evidência estão em `../fluxo/plano-animacao.md`.
O gerador inglês traduz textos sem alterar geometria; a sincronização escala somente
os keyframes, mantendo o frame rate. Fontes Noto Sans locais e desenhos originais.
Hashes dos ativos efetivamente renderizados: `licencas.render.en.json`.

Os sete quadros de leitura e as três faixas de movimento foram abertos e conferidos:
textos legíveis, setas e estados coerentes, animações concluídas antes do corte,
sem conteúdo sobre o rodapé. Os valores didáticos 10/11/12 também foram conferidos
dentro do Lottie, pois o `vp medicao` não lê seu texto interno.

Limite de localização: os componentes numéricos do kit conservam a formatação pt-BR
(pontos nos milhares e vírgula decimal); o contrato JSON atual não expõe locale.
Textos e voz estão em inglês, e os valores não mudam.

## Revisão e publicação

Esta entrega traduz o vídeo de C que o dono acabou de aprovar e publicar. A direção
editorial de explicar o impacto visual em System Design será aplicada à próxima pauta
Java/CompletableFuture; não foi acrescentada uma cena nova somente nesta tradução.

Os checks e dados do MP4 final ficam em `verificacao.en.json` e `audio.en.json`.
Primeira mistura preservada em `../final.en.fluxo.v1.mp4`, com `audio.en.v1.json`
e `sfx.en.v1.json`: o pop da entrada do atomic ficou encoberto pela fala
(ataque detectado a −41 ms, limite de 40 ms). Esse efeito opcional foi removido;
a versão final tem sete falas e seis efeitos. O visual não mudou nessa revisão.
O dono aprovou a versão em inglês na conversa: "Acho que esta adequado pode esta ok nesse caos".
Tradução aprovada via `vp approve short-concorrencia-fluxo-en --step translation`;
a aprovação do vídeo foi vinculada ao hash do MP4 nas notas do gate e no relatório.
Depois, o dono autorizou "Pode publicar por favor". O pacote com descrição foi
preparado, o gate 4 aprovado e a dúvida cega registrada com parecer "segue".
O Postiz confirmou **PUBLISHED** no canal inglês `@baixo.nivel.dev.s`:
https://www.youtube.com/watch?v=ubt9aMaDaMs . Registro e pendências manuais em
`../posts/publicacao-en.md`; o MP4 aprovado foi preservado.
