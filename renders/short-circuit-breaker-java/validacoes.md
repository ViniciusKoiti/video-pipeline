# Validações e entrega ao parent

## Continuação: render-ready

Voz autorizada na continuação de 2026-11-05. CPU probe 0,077 s. Somente `medido` em inglês mudou:
"In this simulation, the breaker cut calls during the outage from sixty to twenty-four."
As cópias renders/en/ig e o roteiro receberam o mesmo texto via apply_patch. `vp short voz` completou
as sete falas inglesas, reaproveitando o cache das outras seis; novo medido nivelado em -16,75 LUFS,
pico verdadeiro -1,5 dBTP, sem alterar política/gate. O WAV bruto antigo com falha e todos os WAVs
existentes foram preservados. Nenhuma outra fala precisou de reescrita ou síntese.

### Entradas finais

- Render PT: `renders/short-circuit-breaker-java/pronto/content.pt.voz.json` (35,3 s).
- Render EN e Instagram: `renders/short-circuit-breaker-java/pronto/content.en.voz.json` (39,2 s).
- Cópias finais: `data/episodes/short-circuit-breaker-java-{pt,en}/content.voz.json`.
- Narração/registro PT: `data/episodes/short-circuit-breaker-java-pt/narracao.json` e `narracao.voz.json`.
- Narração/registro EN: `data/episodes/short-circuit-breaker-java-en/narracao.json` e `narracao.voz.json`.
- Cada `wav` do registro permanece relativo ao seu episódio, em `voice/leveled/`; NÃO usar `pronto/`
  como o argumento `pasta` da junção. Instagram pode reutilizar a montagem inglesa e seu registro EN.
- JSONs autorais de 43,4 s preservados, inclusive content.json dos episódios. NÃO usá-los no render final.
  Snapshots de conteúdo e registros em `originais/`; eles não movem nem duplicam WAVs.

### Conferências finais

- `finalizar.py audit pt en`: todos os quatorze WAVs leveled com hashes válidos, fala/registro coerentes,
  `silencedetect=noise=-50dB:d=0.5`; margem de 0,05 s em speech no início/fim. Zero pausas internas,
  zero intervalos de silêncio de pelo menos 0,5 s nos WAVs individuais. `auditoria-pausas.json` registra cada fala.
- Fala real PT 29,283 s; EN 36,488 s. Durações finais por cena no plano e em `finalizacao-tempos.json`.
- `vp short tempos` pt/en executados nos inputs de `pronto/`, sem esticar nenhuma cena além do ajuste calculado.
- `validate` e `inspect` dos dois `content.*.voz.json`: success true, diagnostics vazios, sem
  SCENE_TOO_SHORT_TO_READ. Relatórios completos em `finalizacao-{validate,inspect}.{pt,en}.json`.
- Concatenação de áudio em memória, sem gerar arquivo: trims speech exatos e padding por cena,
  maior silêncio -50 dB de 0,981438 s em PT e 0,561041 s em EN. Nenhum acima de 1 s.
  Relatórios em `finalizacao-audio.{pt,en}.json`; não substituem a conferência do MP4 misturado pelo parent.
- Sem render ou review de imagens, testes globais, app/config/demo alterados, approve, envio ou publicação.
- Medição pt/en e tradução en/ig continuam sem problemas nas entradas autorais; os quatro avisos de
  cobertura numérica conhecidos continuam documentados no registro inicial abaixo.
- EN agora tem 87 palavras, PT 81. A estimativa por palavras do registro inicial foi substituída pelos WAVs.

### Limitação temporal da tradução

PT usa leituras finais de 0,814–0,890 s para atingir 35 s sem mudar voz. EN usa 0,352–0,433 s.
Um envelope comum às duas versões deixaria até 2,323 s depois da fala PT, por isso os derivados usam
timelines diferentes. A comparação adicional confirma que só localização textual e campos de tempo
mudam: mesmas cenas, nós, rotas, estados, tokens e números. `vp traducao` lê o content.json autoral,
não o content.voz.json derivado; seu sucesso NÃO aprova as timelines diferentes. Nada foi carimbado.

### Comandos usados nesta continuação

Na raiz do auto-play:

```bash
.venv/bin/vp short voz data/episodes/short-circuit-breaker-java-en data/episodes/short-circuit-breaker-java-en/narracao.json
.venv/bin/python renders/short-circuit-breaker-java/finalizar.py audit pt en
.venv/bin/python renders/short-circuit-breaker-java/finalizar.py prepare pt en
.venv/bin/vp short tempos data/episodes/short-circuit-breaker-java-pt renders/short-circuit-breaker-java/pronto/content.pt.json data/episodes/short-circuit-breaker-java-pt/narracao.json
.venv/bin/vp short tempos data/episodes/short-circuit-breaker-java-en renders/short-circuit-breaker-java/pronto/content.en.json data/episodes/short-circuit-breaker-java-en/narracao.json
.venv/bin/python renders/short-circuit-breaker-java/finalizar.py check pt en
```

`check` chama sequencialmente o bin local já verificado no package.json, sem npx:
`node /home/viniciusk/projetos/motion-kit/packages/motion-video/dist/video.mjs validate content.pt.voz.json`
e `inspect`, depois os equivalentes en, com cwd em `pronto/`. Sem renderização ou imagens.

### Junção para o parent

Comandos ainda NÃO executados; pressupõem os MP4s silenciosos renderizados nesses caminhos:

```bash
.venv/bin/vp short juntar data/episodes/short-circuit-breaker-java-pt renders/short-circuit-breaker-java/mudo.pt.mp4 renders/short-circuit-breaker-java/pronto/content.pt.voz.json data/episodes/short-circuit-breaker-java-pt/narracao.json --saida renders/short-circuit-breaker-java/final.pt.mp4
.venv/bin/vp short juntar data/episodes/short-circuit-breaker-java-en renders/short-circuit-breaker-java/mudo.en.mp4 renders/short-circuit-breaker-java/pronto/content.en.voz.json data/episodes/short-circuit-breaker-java-en/narracao.json --saida renders/short-circuit-breaker-java/final.en.mp4
```

Sem SFX obrigatório; nenhum foi acrescentado. Escuta, revisão visual e medição final do áudio misturado,
gate humano de tradução e prévia continuam com o parent/dono. Sete recusas após retorno e 133 totais
continuam medianas de erros, nunca pagamentos bem-sucedidos.

## Registro inicial (histórico)

Preparação de texto/JSON em 2026-11-05. Não foram executados voz, render, review de quadros, approve,
Postiz, upload, commit ou push. `demo/` não foi alterado; hashes de Demo.java, BreakerTest.java e medir.sh
conferidos contra o resultado já existente. A pauta pt foi preservada sem edição.

## Arquivos

- Nesta pasta: `fontes.md`, `fontes/excertos.md`, `roteiro.md`, `plano-animacao.md`,
  `content.pt.json`, `content.en.json`, `narracao.pt.json`, `narracao.en.json`,
  `verificar_artefatos.py` e este registro.
- Nos episódios `short-circuit-breaker-java-pt`, `-en` e `-ig`: `content.json`, `narracao.json`,
  `medicao.json`, `voice/glossary.json`.
- Nos episódios en/ig: `traducao.json`, ambos `derived_from: short-circuit-breaker-java-pt`.
- Os arquivos content/narracao dos episódios são cópias byte a byte dos originais de renders;
  ig reutiliza en, sem apresentador.
- O kit gerou seus próprios relatórios em `out/production/`; não há MP4 produzido nesta preparação.

## Texto e tempo

| Idioma | Palavras por cena, separadas por espaço | Total | Estimativa a 2,2 palavras/s | Timeline inicial |
| --- | --- | --- | --- | --- |
| pt-BR | 11, 13, 10, 9, 9, 14, 15 | 81 | 36,8 s | 43,4 s |
| en / ig | 12, 13, 12, 11, 10, 12, 15 | 85 | 38,6 s | 43,4 s |

Palavras hifenizadas contam como uma nesta contagem; a pronúncia pode mudar o tempo.
Nenhuma duração de fala foi medida ou prometida: parent deve ajustar pelos WAVs.
Sete cenas, primeira hook e seis neutral, sem turn obrigatório. Humanizer revisado antes de voz,
registrado em `roteiro.md`. Fim de fluxo com pelo menos um segundo de leitura; validate considera
também a estabilização visual. A cena teste foi ampliada para 5,2 s para eliminar SCENE_TOO_SHORT_TO_READ.
A cena aberto foi ampliada para 5,5 s para caber a estimativa inglesa, mantendo pt/en estruturalmente iguais.

## CLI local usada

Bin descoberto pelo `packages/motion-video/package.json`: `dist/video.mjs`. Nenhum npx ou pacote baixado.
Executado com cwd nesta pasta, sequencialmente para evitar disputa pelo diretório `out`:

```bash
node /home/viniciusk/projetos/motion-kit/packages/motion-video/dist/video.mjs validate content.pt.json
node /home/viniciusk/projetos/motion-kit/packages/motion-video/dist/video.mjs validate content.en.json
node /home/viniciusk/projetos/motion-kit/packages/motion-video/dist/video.mjs inspect content.pt.json
node /home/viniciusk/projetos/motion-kit/packages/motion-video/dist/video.mjs inspect content.en.json
```

Saídas finais: `success: true`, `diagnostics: []` nos quatro comandos; inspect informa 43,4 s e
`reviewRequired: true`. Relatórios finais de validate:

- pt: `out/production/1793882966300-317b23ca/`
- en: `out/production/1793882980922-de5f25a6/`

Versões efetivas: Node 22.22.3, motion-video 0.3.0, motion-kit 0.9.0, Remotion 4.0.487.
Na primeira validação o kit baixou automaticamente seu navegador do Remotion, embora não tenha renderizado.
A primeira tentativa paralela de validate pt retornou EEXIST ao disputar a criação de out; a repetição
sequencial passou. As tentativas anteriores ficam preservadas no histórico local do kit.

Executado a partir da raiz do auto-play:

```bash
.venv/bin/vp medicao short-circuit-breaker-java-pt
.venv/bin/vp medicao short-circuit-breaker-java-en
.venv/bin/vp medicao short-circuit-breaker-java-ig
.venv/bin/vp traducao short-circuit-breaker-java-en
.venv/bin/vp traducao short-circuit-breaker-java-ig
.venv/bin/python -m renders.short-circuit-breaker-java.verificar_artefatos
```

Medições e traduções: `resultado: sem problemas`. Verificador adicional: PASS para cópias exatas,
todos os campos não textuais pt/en iguais (não apenas folhas numéricas), limite de palavras, entregas,
estimativa de fala por cena, quantidade de nós, eventos a partir de 1,3 s, margem final e hashes da demo.
O verificador também lê textos de sublabel/rodapé e confirma cobertura numérica no medicao.json.

## Avisos e pendências

- `vp medicao` emite quatro avisos de declarado/não usado: 1, 133, 15 e 25. Não são entradas a apagar:
  um/uma/one não entram no parser, 133 está em sublabel e 15/25 no footer, campos ignorados pelo gate.
  Estão rastreados e cobertos pela conferência adicional; falta conferir a legibilidade nos quadros.
- Os valores 5 e 2 são configuração do exemplo; 25 é versão; 15 é quantidade de rodadas.
  Resultados são 60/24 chamadas na falha, 7 recusas pós-retorno e 133 totais, medianas por rodada.
- Não chamar as recusas de sucesso. Não transformar a distribuição de latência com erros em ganho de performance.
- A pauta antiga menciona dois segundos de lentidão como proposta e contém uma linha histórica de não aprovação;
  a própria pauta registra aprovação do tema acima. Nesta demo, a falha dura três segundos e o breaker fica aberto dois.
  Esses esclarecimentos estão no roteiro/plano, sem reescrever a pauta nem trocar o resultado.
- A cena teste mostra alternativas condicionais; não a execução simultânea dos dois ramos.
- Sem revisão visual: antes/durante/depois, rodapé, retorno de erro e margens ainda devem ser abertos pelo parent.
- Não há gate humano de tradução aprovado. A aprovação continua pendente; este texto não a substitui.
- Voz, escuta, ajuste fino de sincronização, render e aprovação da prévia continuam com o parent/dono.
