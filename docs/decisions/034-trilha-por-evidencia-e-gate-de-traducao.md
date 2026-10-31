# 034 — Tradução em pasta própria, com gate, e trilhas por tipo de evidência

- **Status:** proposta; o gate de tradução e o `vp traducao` estão implementados e testados, os adapters de prova e
  o agente tradutor ainda não.
- **Data:** 2026-10-30
- **Relaciona-se com:** ADR 006 (portas e adapters), ADR 008 (idioma por episódio), ADR 009 (agentes escrevem
  dados, o código valida; gates por comando), ADR 016/024 (voz) e a skill `shorts-tec`.

## Contexto

O mesmo vídeo passou a sair em dois idiomas e em dois canais (`@viniciusnakahara` em português,
`@baixo.nivel.dev.s` em inglês). Os Shorts técnicos já usam um gate por idioma (`<id>-pt`, `<id>-en`), mas a
tradução em si não passa por nenhuma conferência: a narração em inglês do Short de lista ligada foi escrita junto
com a em português e só seria revista como parte da prévia.

Além disso, o pipeline único assume que a prova de um vídeo são fontes baixadas (`facts.json`). Um Short sobre uma
medição do dono tem outra prova (o arquivo do resultado). O que muda o processo é **de onde vêm os fatos**, não
a duração do vídeo.

## Decisão

1. **Uma pasta por idioma.** O original fica em `data/episodes/<id>/` (ou `<id>-<idioma-original>`); cada tradução, em
   `data/episodes/<id>-<idioma>/`, com um `traducao.json` (`derived_from`, `language`, `source_language`). O vínculo
   fica nesse arquivo, não no manifesto principal nem no `episode.json` (mudar este exige ADR).
2. **Gate de tradução** (`Step.TRANSLATION`, `vp approve <id>-<idioma> --step translation`), entre o roteiro aprovado e
   a voz. Carimba a narração traduzida, o vínculo, o `content.json` (quando existe) e a narração e o `content.json` do
   original. Se o original muda, a aprovação cai (§5). Só existe em pasta com `traducao.json`.
3. **Conferência em código antes de o dono ler** (`vp traducao <id>`, e obrigatória para aprovar o gate). Confere o que
   não depende de entender a língua: mesmo número de falas, mesmos ids de cena, mesma entrega (ADR 022), mesmo número de
   pausas (ADR 015), **mesmos números ditos** (por extenso ou em dígitos, em pt e en) e, na tela, as mesmas cenas e os
   mesmos valores numéricos. Limite: "um/uma" e "one" não entram na conta (artigo e numeral se confundem).
   O dono lê o que sobra: sentido, tom e termos.
4. **Quem traduz é um adapter de agente** (ADR 009): escreve só `narracao.json`/`content.json` na pasta nova; o código
   valida. O verificador compara os dois textos antes do dono. Um modelo local pode entrar depois como outro adapter,
   sem mudar o gate. Citações em obras traduzidas (ensaios longos) vêm de tradução registrada nas fontes, não de
   tradução automática; o gate prevê isso, e a regra vale para os longos quando houver o primeiro.
5. **Trilhas por tipo de evidência, como adapters da etapa de prova** (a implementar quando houver o terceiro Short
   no mesmo molde, para não fixar o desenho cedo):
   - adapter *fontes*: `sources.json` + `facts.json` + citação literal (`vp check` de hoje), para os longos e os Reels
     de pauta;
   - adapter *medição própria*: cada número da tela aponta para o arquivo de resultado de uma execução do dono
     (ambiente, versão e data), para os Shorts técnicos.
   O núcleo (estados, `review.json`, `vp approve`, voz, loudness, Postiz, `vp usage`) é o mesmo.

## Trade-offs

- **Um gate a mais** altera a frase "4 gates" do §2.5: passa a haver um quinto, só em pasta de tradução. Cada vídeo em
  dois idiomas pede duas aprovações do dono; a conferência em código tira a parte mecânica da leitura.
- **O código não entende sentido.** A conferência acha número, cena e pausa trocados, não uma frase mal traduzida.
  Isso fica com o verificador e com o dono.
- **A conferência de números por extenso é limitada** a pt e en e às escalas até bilhão; outro idioma pede outro
  léxico.
- **Pastas duplicadas** de `content.json` e narração; os ativos grandes do original podem ser reaproveitados por
  caminho, sem cópia, quando o primeiro longo traduzido existir.
- **A voz em inglês** segue pendente de escuta cega (skill `shorts-tec`); o gate não decide isso.

## Consequências

- Implementado: `app/pipeline/translation.py`, o passo `translation` em `app/pipeline/gates.py`, `vp traducao` e os
  testes em `tests/test_translation.py`. O `vp status` lista o gate só em pasta com `traducao.json`.
- Piloto: `short-lista-ligada-pt` e `short-lista-ligada-en`.
- Pendente: skill e agente `tradutor`, os adapters de prova, e a trilha sonora nesses Shorts: o dono acha válida, mas fora do
  primeiro (2026-10-30), para a hipótese medir só a demonstração. A ADR 030 cobre só o `explainer` com `music.json`;
  a `shorts-tec` deixa a trilha fora da v1 e o `juntar` ainda não faz ducking.
