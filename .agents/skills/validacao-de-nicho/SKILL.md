---
name: validacao-de-nicho
description: |
  Valida se vale entrar num nicho ou formato de vídeo (ex.: recap de anime) antes de pauta ou código: quem já
  faz e com que audiência, direitos e monetização, onde publicar e que alternativas passam pelas regras do
  projeto, com ficha de canal de referência e medição de demanda verificadas. Use quando o dono trouxer um
  nicho, um formato ou um canal para avaliar.
argument-hint: "<nicho ou formato> [canal de referência]"
---

# Validação de nicho: público, risco e caminho legítimo

A pergunta é sempre a mesma: **este nicho serve a este pipeline, dentro destas regras?** Ter público não basta.
Um formato pode ter milhões de views e ainda assim ser barrado pelas regras do projeto ou pela política da
plataforma. A resposta separa **fato** (fonte com URL e data), **estimativa** (número de terceiros, como Social
Blade ou RPM) e **inferência** (raciocínio sobre os fatos).

Saída: `docs/pesquisa/reports/<Título>.md`, com as notas em `docs/pesquisa/research_notes/<Título>/`. O título tem
de 3 a 6 palavras, em pt-BR, sem pontuação, e é diferente dos que já existem nas duas pastas.

## 1. Enquadrar

- Escreva a pergunta numa frase: nicho, formato, idioma ou mercado, e o que o pipeline faria (aquisição, roteiro,
  voz, render).
- Leia antes de pesquisar:
  - CLAUDE.md §2 (licença registrada, custo zero, gates) e §12 (política de conteúdo inautêntico do YPP);
  - a lista de licenças da ADR 007;
  - o que já existe sobre o nicho em `docs/pesquisa/`.
- Pergunte ao dono só o que muda a pesquisa: o mercado ou idioma, e o canal de referência, se ele tiver um.

Pronto quando a pergunta e as restrições do projeto estão escritas e vão abrir o relatório.

## 2. Pesquisar por ângulos, em paralelo

Um subagente por ângulo, todos lançados na mesma mensagem, cada um salvando `<ângulo>.md` nas notas com quatro
partes: conclusão, fatos (URL e data de consulta), inferências e lacunas. Os ângulos padrão:

1. **Panorama de canais** por idioma: tamanho, frequência, duração, formato e sinais de produção em série com IA.
2. **Direitos e monetização:**
   - a política oficial da plataforma, citada literalmente;
   - o que os detentores de direitos fazem na prática;
   - processos e condenações;
   - táticas de evasão e se elas funcionam.
3. **Onde publicar:** plataformas, idiomas, subnichos saturados ou vazios e RPM (marcado como estimativa).
4. **Alternativas** que passam pela lista de licenças do projeto.

O prompt de cada subagente leva a pergunta do dono e as restrições do projeto. Os fatos ficam para as fontes: um
fato meu num prompt vira conclusão sem fonte. Se a skill `deep-research` estiver disponível, ela coordena a
distribuição e a escrita do relatório.

Pronto quando os quatro arquivos de notas existem e cada um tem a seção de lacunas.

## 3. Escrever o relatório

Um único subagente escreve, a partir das notas:

- a resposta na primeira frase;
- uma seção por ângulo;
- uma tabela das divergências entre as notas;
- as lacunas que pesam na decisão;
- a recomendação, com uma tabela de próximos passos e a coluna "Quem decide".

Pronto quando todo número tem fonte ou está marcado como estimativa ou inferência.

## 4. Conferir antes de apresentar

Você, coordenador, confere. O subagente não confere o próprio trabalho.

- Leia o relatório inteiro.
- Identifique os 2 ou 3 fatos que decidem a recomendação (um processo, a frase de uma política, uma regra de
  licença). Abra a fonte primária de cada um, ou marque "não conferido".
- Refaça toda mediana a partir do CSV com `python3 -I .agents/skills/validacao-de-nicho/medianas.py <csv>`.

Pronto quando cada fato decisivo está marcado como conferido ou não conferido.

## 5. Aprofundar quando a pergunta pedir

Cada aprofundamento entra no relatório como uma seção **"Adendo: …"**. Seções anteriores não são reescritas sem
aviso.

- **O dono cita um canal de referência:** siga [ficha-de-canal.md](ficha-de-canal.md).
- **"Esse formato tem público?" ou "e o formato alternativo?":** siga
  [medicao-de-demanda.md](medicao-de-demanda.md).
- **"Como o nicho faz os vídeos?" (depois da medição de demanda, ou antes de escrever o roteiro):** use a skill
  `analise-de-formato`. Ela baixa e mede uma amostra do CSV da medição com scripts determinísticos e compara
  com o nosso roteiro.
- **Programa de licença ou regra de um detentor:**
  - pesquise só páginas públicas, citando no idioma original e em tradução para pt-BR;
  - liste as perguntas que só o detentor responde;
  - deixe um rascunho de e-mail para o dono enviar.

## 6. Fechar

- **Na conversa:**
  - o veredito em uma frase;
  - de 3 a 5 números que o sustentam;
  - o que ficou sem verificar;
  - as decisões do dono, agrupadas e com a sua recomendação.
- **Na memória:** atualize o arquivo de projeto do nicho com o veredito e as decisões pendentes.

## Limites

- **O que a skill entrega:** avalia o risco e aponta caminhos licenciados. Descrever como um canal escapa do
  Content ID é evidência para o relatório. O pipeline do projeto trabalha só com material licenciado (§2.3).
  Montar a evasão (espelhar, cortar ou mascarar cena) fica fora.
- **Canais de terceiros:** são citados como caso de estudo. Denúncia a um detentor é decisão do dono, caso a
  caso, com obra, link e trecho conferidos.
- **Rede:** só leitura pública. Cadastro, formulário e envio de e-mail ficam com o dono.
- **Views não são receita.** Estimadores supõem monetização integral. Reivindicações e strikes são invisíveis de
  fora, e canal encerrado some das estatísticas (viés de sobrevivência).
