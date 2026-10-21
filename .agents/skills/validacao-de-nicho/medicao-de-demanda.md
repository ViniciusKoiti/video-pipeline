# Medição de demanda por formato

Use quando a dúvida é "esse formato tem público?" ou "o formato que as regras permitem compete com o que o
mercado faz?". A comparação é entre **grupos de formato** do mesmo nicho e idioma, nunca entre um canal e outro.

## Desenho

- **Grupos:** de 2 a 4, definidos pela duração e pelo título. Exemplo do recap de anime:
  - A: recap longo, ≥ 60 min;
  - B: episódio comentado, 8–25 min;
  - C: react;
  - D: ensaio sobre a obra.

  Mantenha o formato que as regras do projeto permitem como um grupo próprio.
- **Amostra:** de 8 a 15 canais por grupo, achados pela busca e pela pesquisa anterior.
- **Demanda de um título específico:** quando a pergunta é sobre títulos (os liberados por um programa de licença,
  por exemplo), busque vídeos sobre cada um e classifique por formato.
- **Métrica por canal:** mediana de views dos vídeos com **14 a 180 dias**, porque os recém-publicados puxam para
  baixo. Também: inscritos, vídeos nos últimos 90 dias e duração mediana.
- **Métrica por grupo:** mediana das medianas dos canais, com p25 e p90. Use a mediana, não a média.
- **Horas assistidas:** compare a frequência e a duração entre os grupos. A diferença em horas assistidas é
  *inferência*: a receita não aparece nos dados públicos.

## Coleta

- **Amostra pequena:** use `coleta.py`, que fica nesta pasta. Ele lê as páginas públicas, sem login nem cookies,
  pausa 2,5 s entre requisições e sai com código 3 na primeira resposta 429 (pare e registre). Cada chamada
  acrescenta linhas ao mesmo CSV:
  ```bash
  S=.agents/skills/validacao-de-nicho
  python3 -I $S/coleta.py busca "resumo de anime" - <scratchpad>/achados.csv  # achar canais (grupo "-")
  python3 -I $S/coleta.py canal @Canal A <notas>/demanda.csv --bruto <scratchpad>/bruto
  python3 -I $S/coleta.py idioma <notas>/demanda.csv                     # título original × coletado
  python3 -I $S/medianas.py <notas>/demanda.csv
  ```
  O modo `canal` segue as páginas seguintes até passar de 180 dias ou chegar a 4 páginas (`--paginas`). Um canal
  que publica todo dia pode precisar de mais.
- **Coleta grande ou recorrente:** proponha a YouTube Data API, com chave do dono e cota gratuita. É serviço novo,
  então a decisão é do dono.
- **Idioma:** com `hl=pt`, o YouTube traduz títulos em inglês e espanhol. Rode o modo `idioma` e tire do CSV os
  canais cujo título original não está no idioma medido.
- **Idade:** "há 2 meses" vira 60 dias, então registre o texto original ao lado do número.
- **CSV** com as colunas `canal, grupo, video_id, titulo, duracao_s, views, idade_texto, idade_dias_aprox,
  data_coleta, fonte, inscritos_canal`, que o `coleta.py` já escreve. O CSV fica nas notas da pesquisa, onde o
  dono pode abrir numa planilha. O HTML bruto fica no scratchpad (`--bruto`), citado pelo caminho nas notas.

## Verificação

1. **Recoleta.** Colete de novo de 3 a 4 canais sorteados, um por grupo, com a semente registrada. As medianas devem
   bater, salvo pelos vídeos recém-publicados.
2. **Conta do coordenador.** Refaça os números com
   `python3 -I .agents/skills/validacao-de-nicho/medianas.py <csv>`. Diferença pequena por critério de corte se
   registra; diferença grande volta para quem coletou.
3. **Limites, sempre escritos:**
   - busca personalizada pela região do IP;
   - viés de sobrevivência;
   - views não são receita;
   - idade aproximada;
   - formato e uso de cenas inferidos pelo título e pela miniatura.

O resultado entra no relatório como "Adendo: demanda de …". O adendo traz a tabela dos grupos, os números
refeitos, a demanda por título e a inferência sobre o que isso muda na recomendação.
