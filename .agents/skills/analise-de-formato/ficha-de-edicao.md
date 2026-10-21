Você vai preencher uma ficha fechada sobre como um vídeo é editado. Só leitura: não escreva nem apague arquivos no projeto (quadros extras, se precisar, só no diretório temporário da sessão). Material de terceiros, só para análise. Descreva só o que se vê e se lê; não adivinhe.

Para cada vídeo <id>, na pasta data/cache/nicho/<Título>/:
- `decupagem/<id>/cenas.tsv`: cada cena (entre dois cortes secos), com início, duração e a fala nela (legenda automática, sem pontuação, erro de ~0,5 s).
- `decupagem/<id>/cenas-*.jpg`: o quadro do meio de cada cena, com número, início e duração em amarelo (posto por nós).
- `<id>_densa_00.jpg`, `<id>_densa_50.jpg`, `<id>_densa_100.jpg`: um quadro a cada 0,1 s nos 4 s da abertura, do meio e do fim.
- `<id>.txt`: a transcrição inteira com o minuto.
O detector só conta corte seco: fusão, cartão de palavra sobre preto e movimento não viram cena; clarões e vazamento de luz podem virar cenas falsas.

Classificação imagem × fala, para TODAS as cenas dos 2 primeiros minutos e mais 10 cenas espalhadas pelo resto (conte quantas de cada):
- mostra: a imagem traz o personagem, lugar, pessoa ou evento específico da frase;
- clima: imagem sem relação direta com a frase (textura, personagem genérico enquanto a fala é abstrata);
- texto: o texto da fala (ou palavra dela) na tela é o principal;
- piada: imagem que comenta, contrasta ou faz humor com a fala (meme, reação).

Responda, para cada vídeo, com UM bloco JSON (nada além dos blocos e, no fim, até 3 linhas de observação geral):
{"video_id": "...",
 "abertura_tipo": "provocacao|confissao|pergunta|dado|apresentacao_do_tema|titulo_sem_fala|outro",
 "abertura_frase": "as primeiras palavras faladas, até 10",
 "abertura_palavra_a_palavra": true/false,
 "imagem_principal": "anime_movimento|anime_parado|manga|jogo|filme_live_action|banco|ilustracao|texto|pessoa_filmada|apresentador_desenhado|misto",
 "amostra": {"mostra": 0, "clima": 0, "texto": 0, "piada": 0},
 "imagem_reage_palavra": "nenhuma|rara|frequente",
 "pausa_visual": true/false,
 "cor_por_assunto": true/false,
 "bordao_visual": true/false,
 "palavra_destaque_cor": true/false,
 "apresentador": "nenhum|desenhado|filmado",
 "material_desleixado": true/false,
 "fecho": ["licao", "pergunta_ao_espectador", "volta_a_abertura", "opiniao_do_narrador", "pedido_inscricao", "outro"],
 "narrador_eu": "nenhum|raro|frequente",
 "notas": "até 30 palavras"}
- pausa_visual: imagem parada ou preto sem fala por 1,5 s ou mais, logo depois de uma pergunta ou frase forte.
- bordao_visual: a mesma imagem volta quando o mesmo tema volta.
- material_desleixado: marca d'água de outro programa, menu de jogo, créditos de outra obra, "Ativar o Windows".
- narrador_eu: o narrador fala de si (eu, pra mim, eu lembro), pela transcrição.
