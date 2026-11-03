---
name: short-diario
description: Rotina de um Short da série "eu medi" até o pacote do Postiz, sem gates (ADR 036). Use quando o timer chamar ou quando o dono pedir "roda a rotina".
---
# Short diário
O pedido em pé do dono está na ADR 036: tudo abaixo roda sem perguntar; nada fora disto. Nunca `vp approve`, nunca `vp postiz duvida` nem `schedule`, nunca vidIQ, nunca push, nunca baixar ativo. Em dúvida, pare e registre.
## Entrada
- Ler `renders/serie-conceitos/direcao-editorial.md` e `fila.md` antes de escolher a pauta. A fila atual tem prioridade sobre o calendário histórico de `serie.md`: Java é a próxima frente. Produzir somente pauta aprovada; sem ela, registrar a pendência em `data/rotina/AAAA-MM-DD.md`, sem escolher um item adiado do lote antigo.
- `cpu_probe()` acima de 0,3 s: registre "máquina limitada" e pare.
- Referência visual atual: `data/episodes/short-concorrencia-fluxo-pt/` e `renders/short-concorrencia/fluxo/`. Os exemplos em C orientam a forma, não os fatos nem os números de Java.
- Abrir `renders/short-concorrencia/final.pt.fluxo.mp4` ou seus quadros como referência de blocos conectados e consultar `fluxo/plano-animacao.md` e `fluxo/gerar_animacoes.py` nessa pasta. Adaptar os estados à aplicação do tema, incluindo sua decisão de System Design.
## Método (pare no primeiro passo que falhar; registre tudo)
1. Pastas: `renders/short-<conceito>/demo/`, `data/episodes/short-<conceito>-pt`, `-en` (com `traducao.json`) e `-ig`.
2. Medição: o programa da pauta em `demo/`, `medir.sh` gravando `demo/resultado.txt` com ambiente, versão, data, 15 rodadas, mediana e extremos.
3. `roteiro.md` com a origem de cada número e fontes primárias registradas para explicar o mecanismo. Em todo vídeo técnico, ligar o conceito a uma decisão de System Design de uma aplicação concreta, com benefícios e limites. Responder a pergunta central no próprio vídeo; o fecho pode pedir outra linguagem ou continuação.
   **A lição em uma frase:** o `roteiro.md` declara, antes da narração, a regra que o espectador leva
   (ex.: "a latência do caminho composto é a da chamada mais lenta, não a soma"). Cada cena de explicação
   diz na **fala** uma regra ou consequência, não só o número; a tela repete a lição, nunca a substitui.
   Mostrar 501 contra 310 sem dizer o porquê não ensina. Sem a lição dita na fala, não gerar voz.
4. `plano-animacao.md` com trecho da fala, estado inicial/final, blocos, conexões, ação visível e fonte por cena de explicação, incluindo o impacto no fluxo e nos recursos da aplicação (System Design). Conferir na pauta o quadro obrigatório da direção editorial: aplicação, decisão, benefício/limite e sequência animada. Lacuna impede voz/render e deve ser registrada. Depois `narracao.pt.json` (humanizer-narracao) e `narracao.en.json`, na duração planejada na pauta, sem prender a história a cinco cenas. Copiar como `narracao.json` nas pastas de episódio.
   **Porta do texto, antes da primeira voz** (cada fala refeita custa uma chamada ao Modal; fechar o texto primeiro):
   - humanizer **antes** da primeira `vp short voz`, nunca depois; frases ligadas por "e/ou/mas", sem série de frases curtas (cada ponto vira pausa na voz clonada);
   - `voice/glossary.json` para toda sigla dita (API → "á pi", JSON → "jêison"); sigla nova sem entrada no glossário não vai à voz;
   - conferir a lição do passo 3 presente na fala de cada cena de explicação;
   - estimar a duração: a voz clonada fala ~2,2 palavras/s (a referência `turn` é mais lenta); fala estimada maior que a cena planejada = encurtar o texto agora, não depois da escuta.
5. `content.pt.json` e `content.en.json` seguindo o plano (`safeArea: shorts`, `footer` com o ambiente, `showRatio: false`); linguagem explícita na abertura. Usar animação de fluxo para o mecanismo, com passos e mudanças de estado, não só cartões de texto. `validate` e `inspect` do kit com cwd na pasta do JSON; `review` e abrir os quadros de antes/durante/depois das transições, conferindo valores e margens. Números internos de Lottie exigem rastreio e conferência próprios.
6. `medicao.json` com todos os números; `vp medicao <id>-pt` e `-en` limpos; `vp traducao <id>-en` limpo. Corrija a narração ou o `medicao.json`, nunca o resultado.
7. Definir `delivery` de cada cena pela intenção: `hook`, `turn`, `neutral`, `calm` ou `invite`.
   **Proporção:** `hook` só na primeira cena, `invite` só na última, no máximo um `turn` (a virada), e o resto
   `neutral` (ou `calm` na conta): pelo menos 60% das falas neutras. As entregas fortes (config de 2026-11-02) só
   contrastam se forem raras; mais de uma cena forte seguida soa forçada. `vp short voz` seleciona a referência por idioma/entrega em `[chatterbox.references]` (ADR 053); conferir arquivo e hash em `narracao.voz.json` e identidade no manifest. Com o banco ativo, o comando também nivela cada fala a −16 LUFS em `voice/leveled/` (ADR 054); conferir `level` e usar os caminhos `wav` do registro. Arquivo configurado ausente, divergente no Modal ou falha de nivelamento deixa a cena pendente: registrar, sem trocar tom ou enviar gravação pessoal.
   **Pausas dentro da fala, antes do `tempos`:** em cada WAV de `voice/leveled/`, `ffmpeg -af
   silencedetect=noise=-50dB:d=0.5`. Silêncio de 0,5 s ou mais **dentro** da fala (entre o início e o fim de
   `speech` no registro) que não esteja planejado no `plano-animacao.md` = reescrever a frase (ligar as orações com
   "e/ou/mas", como no passo 4) e refazer só aquela fala. Corrigir aqui custa uma chamada ao Modal; depois do render
   custa reabrir o gate 4, renderizar e reenviar ao Postiz. Registrar cada pausa encontrada no log do dia.
   Depois `tempos` e `render` do kit nas duas pastas; o Reel usa o `content.en.json` com `host` só se a pele estiver `approved`.
   **Sem vazios:** depois do `tempos`, encolher o `durationSec` das cenas com sobra (alvo: fala + a leitura mínima
   que o `validate` pedir; `SCENE_TOO_SHORT_TO_READ` diz o piso). Depois do `juntar`, medir com
   `ffmpeg -af silencedetect=noise=-40dB:d=0.8`: vazio acima de 1 s só se for pausa de leitura planejada no
   `plano-animacao.md`; o resto é corte. Registrar a medição no log do dia.
8. `sfx.pt.json` e `sfx.en.json` no molde; `vp short sfx`; `vp short juntar --sfx` em `renders/final.mp4`; `vp audio --content --sfx` sem problema.
   **Conferência de áudio, em cada saída e antes do passo 9** (nada vai a `vp short gate` nem ao Postiz sem ela):
   `vp audio <final.mp4> --content content.<idioma>.voz.json --sfx sfx.<idioma>.json --saida <log do dia>`.
   Critérios: volume integrado entre −15 e −13 LUFS; pico real até −1,0 dBTP; nenhum silêncio de 0,5 s ou mais no
   meio de uma fala (o JSON traz o volume momentâneo a cada 0,1 s; −60 LUFS ou menos conta como silêncio). Fora do
   critério = corrigir antes do gate e registrar.
   **Como ler os cortes:** o "ataque a 40 ms" só vale para efeito que está no `sfx.json`. Sem efeito planejado no
   corte, o ataque que o earshot acha é o início da fala; a voz começar até ~150 ms depois da troca de cena é normal
   e não é defeito. Os rótulos do classificador ("chat message pop", "piano", "speech synthesizer") são pistas, não
   veredito: não chamar de efeito o que não está no plano.
   Se `uv run` tentar sincronizar o ambiente e falhar sem rede, usar `uv run --no-sync` (ou `.venv/bin/vp`).
9. `post.json` por saída (título provisório da pauta, origem dos números, divulgação da voz clonada, link do baixo-nivel-demos); `vp short gate` por saída; `vp postiz upload` e `vp postiz pacote --episode` por saída; confira os ids em `vp postiz integrations`.
10. Conferir novamente o quadro obrigatório de System Design e animação no render final; item não conferido impede apresentar a versão como pronta. `data/rotina/AAAA-MM-DD.md`: o que foi feito, os avisos, os quadros para olhar e os comandos que faltam ao dono (`vp approve ... --step translation`, `--step preview` ×3, push, `vp postiz duvida` e `schedule` ×3).
## Regras
Tudo da skill `shorts-tec` vale. Resultados saem da medição; explicações, das fontes registradas. Java exige fontes e medições próprias do ambiente Java. Não refazer o que existe com o mesmo hash; não apagar saídas. Uma execução por dia.
