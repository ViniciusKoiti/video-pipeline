# Posts de circuit breaker: rascunhos locais

Nenhum upload, gate, pacote, aprovação, consulta remota ou publicação foi executado nesta preparação.
Os JSONs seguem a estrutura dos posts de `short-virtual-threads-java/posts/` e `docs/postiz.md`,
mas contêm lacunas deliberadas e NÃO estão prontos para envio. `type: schedule` e a visibilidade
`public` são campos do molde, não autorização nem decisão de agendamento.

## Saídas e mídia candidata

| Rascunho | Episódio / legenda local | Mídia candidata, ainda sujeita à revisão |
| --- | --- | --- |
| post-youtube-pt.json | short-circuit-breaker-java-pt/legenda-post.txt | renders/short-circuit-breaker-java/final.pt.v2.mp4; 35,1 s, em geração segundo o parent |
| post-youtube-en.json | short-circuit-breaker-java-en/legenda-post.txt | renders/short-circuit-breaker-java/final.en.mp4; 39,2 s, informado pelo parent |
| post-instagram-en.json | short-circuit-breaker-java-ig/legenda-post.txt | Reutiliza final.en.mp4, sem host; conferir adequação final ao Reel |

NÃO usar `final.pt.mp4` antigo de 35,3 s. Os caminhos acima são candidatos locais, não IDs nem URLs
de upload. Existência, integridade, áudio e aprovação da mídia continuam com o parent.
Datas e horários não foram escolhidos. A menção histórica a 11/11/2026 era apenas previsão,
não confirmação de agenda ou publicação, e não foi copiada para os campos date.

## Proveniência

- Nenhum ID de integração, mídia ou postagem foi copiado dos posts de virtual threads.
- Todos os campos de canal e mídia ficam explicitamente pendentes de verificação/autorização.
- Nenhuma consulta a Postiz, vidIQ ou GitHub foi feita. O link público de baixo-nivel-demos não foi
  verificado, portanto só existe uma lacuna editorial para código, sem URL inventada ou promessa na fala.
  Antes de publicar, inserir apenas URL pública verificada, ou remover a linha inteira das três legendas.
- As URLs de Fowler e Azure vêm das fontes primárias já registradas em `../fontes.md` e `../fontes/excertos.md`.
- Os números vêm de `../demo/resultado.txt`, não dos exemplos de virtual threads.
- Não havia `review.json` nem `legenda-post.txt` nos três episódios ao conferir esta preparação;
  as legendas foram criadas sem registrar gates ou aprovações.

## Conteúdo e limites

A descrição distingue configuração de resultado. Configuração: 300 requisições a 50 por segundo,
20 threads, timeout de um segundo, falha simulada por três segundos, cinco falhas consecutivas
na ordem de conclusão para abrir e janela aberta de dois segundos. O teste meio-aberto é único.

Resultados: medianas por rodada de quinze rodadas por modo, chamadas na falha de 60 sem breaker
para 24 com breaker, 133 recusas totais e 7 depois do retorno, pela chegada programada dos pedidos.
Os sete pedidos são parte das recusas totais; não se somam aos 133. Recusa continua sendo erro.
JDK é identificação do ambiente, não resultado. Não alegar ganho de latência, sucesso de pagamento,
disponibilidade em produção ou que o breaker recupera o serviço. Fila ilimitada e Thread.sleep são
limitações da simulação local. Voz clonada por IA declarada, sem apresentador em imagem.

## Hipótese editorial

Rascunho de hipótese, sem promessa de resultado: abrir com o custo de falhar rápido e mostrar
o pagamento recuperado ainda recebendo bloqueio pode ajudar o público Java a entender o limite do padrão.
Variável proposta: enquadramento de benefício e custo no título/abertura. Depois de uma publicação
autorizada, registrar retenção/completude e comentários que identifiquem o trade-off aos sete e vinte e oito
dias. Sem baseline ou comparação controlada, essas leituras são descritivas, não prova causal.

## Pendências antes de qualquer envio

1. Parent concluir PT v2 e revisar áudio e quadros das duas versões, sem usar o render PT antigo.
2. Dono revisar título e legenda, resolver/remover a lacuna de código e confirmar os canais corretos.
3. Escolher data futura com fuso; não inferir o horário da previsão histórica de novembro.
4. Executar o fluxo de gate e obter aprovações humanas aplicáveis, incluindo tradução e prévia;
   esta preparação não executou `vp short gate`.
5. Só com autorização, verificar integrações/settings e fazer upload da mídia aprovada; preencher
   IDs e paths com a resposta daquele upload, sem reutilizar mídia antiga por nome parecido.
6. Atualizar a legenda-post.txt correspondente se o texto do JSON mudar, mantendo o gate coerente.
7. Seguir a cadeia de pacote, dúvida cega e autorização de agendamento de `docs/postiz.md`.
8. Conferir no Studio/perfil após a publicação e marcar a divulgação de conteúdo alterado/sintético
   quando aplicável à voz clonada. Nada aqui afirma que o vídeo já foi publicado.
