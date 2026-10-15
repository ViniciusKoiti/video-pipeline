# 017 — Apresentador com a aparência do dono, em destaque na abertura do vertical

- **Status:** parte A (pele `dono`) aceita e implementada a pedido do dono em 2026-10-12; parte B (palco na
  abertura) segue proposta
- **Data:** 2026-10-11
- **Etapa do roadmap:** frente do apresentador (continuação das ADRs 013 e 014)
- **Relaciona-se com:** ADR 007 (licenças de ativos), ADR 013 (apresentador em janela), ADR 014 (perfil vertical),
  ADR 016 (voz clonada, proposta); motion-kit `<Host>` e `HostSkin`

## Contexto

O projeto reels-radar leu os primeiros quadros de 28 Reels de privacidade com um modelo de visão local
(`qwen3.5:4b`) e comparou compartilhamentos ÷ visualizações (mediana) entre quem tem e quem não tem cada
característica. Dois padrões visuais passaram no critério de lá (os dois lados com 5 Reels ou mais e diferença que
aparece em até 10% de 2.000 sorteios ao acaso):

| Característica | Com | Sem | Acaso |
|---|---|---|---|
| Pessoa falando para a câmera | 1,95% (n=21) | 0,62% (n=7) | 5% |
| Texto de alerta na tela no começo | 2,81% (n=6) | 1,23% (n=22) | 8% |

Os 7 Reels lidos do quarto superior abrem todos com pessoa falando para a câmera. Limites: é observação, não
experimento; a amostra é pequena; as respostas do modelo não foram conferidas contra os vídeos; e o dado é de
**pessoa real filmada**, não de personagem desenhado. O resumo completo fica em `briefs/privacy.json` do
reels-radar (formato `script_brief.v1`, fora do Git de lá).

Hoje o vertical tem o apresentador Notionists numa janela de 28% da largura, num canto (ADRs 013 e 014). O dono
escolheu, em 2026-10-11, testar duas mudanças juntas: o personagem em destaque na abertura e um personagem com a
**aparência dele**, feito de sprites gerados a partir de fotos suas.

O que o kit já permite (lido em `@viniciusk/motion-kit`, pin atual do `video/`): uma `HostSkin` pode devolver o
desenho como texto SVG, **URL de imagem** ou elemento React. O vocabulário é fixo: seis visemas (`rest`, `mbp`,
`ei`, `a`, `ou`, `fv`), expressões (`neutral`, `raised`, `furrow`), gestos (`rest`, `open`, `point`, `raise`,
`think`), olhar (`front`, `left`, `right`) e piscada. A pele declara o que desenha de fato; o resto cai no repouso.

## Opções consideradas

1. **Não mexer no visual** e aplicar só o que é texto e duração (falar com "você", título de alerta com o plano
   `keyword`, vídeo acima de 72 s). Custo zero; não testa o padrão visual mais forte.
2. **Notionists em destaque na abertura.** Só o palco, sem pele nova. Mais simples; o personagem continua genérico.
3. **Pele de sprites do dono, em destaque na abertura** (proposta). Mais próxima do dado, sem o dono gravar vídeo.
4. **Abertura filmada pelo dono.** A mais fiel ao dado; exige um tipo de plano novo para vídeo próprio e o dono
   diante da câmera a cada episódio. Fica como alternativa se a opção 3 não convencer.

## Decisão

Proposta, em duas partes independentes, cada uma opcional no contrato:

**Parte A — pele `dono`.**

- Uma pele do tipo imagem, com o **conjunto mínimo**: os seis visemas, de frente, expressão neutra, gesto de
  repouso, com e sem piscada (12 imagens em busto, fundo transparente, mesmo enquadramento em todas). Expressões e
  gestos entram depois, se o mínimo funcionar.
- **Estilo ilustrado, não fotorrealista.** Imagem realista de pessoa gerada por IA pede divulgação de conteúdo
  alterado (regra 4) e erra mais na consistência entre quadros.
- `HostSpec.skin` deixa de ser só `"notionists"`. Onde a pele mora (no kit ou no `video/`) e se ela é montada em
  camadas (base + boca + olhos) ou em imagens inteiras ficam para a sessão de implementação, com o MCP do kit.
- **Fotos e sprites são dado pessoal do dono:** fora do Git, em caminho local. As fotos de origem só saem da
  máquina com decisão explícita do dono sobre o provedor.

**Parte B — palco na abertura.**

- Campo opcional na cena (nome a fechar, por exemplo `host_stage: "opening"`), válido só no vertical e só na
  primeira cena: o personagem entra centralizado e grande, olhando para a câmera, com o título do plano `keyword`
  embaixo, e depois de 3 a 4 s vai para a janela de canto pelo arrasto que já existe.
- Sem o campo, nada muda: o vídeo-régua e os episódios atuais ficam como estão.

**Teste.** Pares de vídeos de privacidade iguais em roteiro, duração e voz, um com palco e pele do dono e outro com
a janela de hoje. As métricas manuais de 7 e 28 dias decidem; com poucos pares, nada se conclui.

## Consequências

- `app/pipeline/schemas.py` (`HostSpec.skin`, campo de palco na cena), `app/media/host.py` (o canto depois do
  palco), `video/src/HostWindow.tsx` e `Scene.tsx`, `tests/test_host.py`. Mudar `video/src/*.tsx` muda o
  `template_hash`: o primeiro render depois do merge refaz todas as cenas (como na ADR 013).
- O `episode.json` muda, então esta ADR é o registro exigido pelo §6. Campos novos são opcionais; `schema_version`
  não muda.
- **Licença dos sprites (regra 3).** A lista fechada da ADR 007 precisa de uma entrada para ativo de autoria do
  dono, ou os sprites entram por outra via registrada. Se forem gerados por um provedor, os termos dele entram em
  `data/benchmarks/` antes de qualquer uso, como foi feito com o Gemini e começou a ser feito com o Higgsfield.
- O roteirista passa a poder receber o `briefs/<nicho>.json` do reels-radar como orientação de **forma**, nunca
  como fonte de fato: as afirmações continuam vindo só das fichas com `source_ids` (regra 2). Isso é assunto da
  skill `roteiro-explicativo` e fica fora desta ADR.

## Decisões em aberto (do dono)

1. **Com o que gerar os sprites.** O `image_gen` atual (Workers AI) não foi conferido para entrada de imagem; o
   Higgsfield é pago e tem termos incompletos; mandar foto do dono a um provedor remoto é envio de dado pessoal.
   Alternativa sem provedor: desenhar ou decalcar à mão a partir das fotos.
2. **Consistência entre os 12 quadros.** Geradores variam o rosto de uma imagem para outra. Caminhos: gerar a
   folha inteira numa imagem só e recortar, ou gerar a base e editar só a boca e os olhos.
3. **Estilo do desenho** (traço, cores, quanto se parece com o dono) e quais fotos servem de origem.
4. **Ordem:** começar pela parte B com o Notionists (opção 2), que não depende de sprites, ou pelas duas juntas.

## Parte A implementada (2026-10-12)

- **Contrato:** `HostSpec.skin` aceita `"dono"`, sem `identity` (a pele é um desenho pronto); `notionists` continua
  exigindo as peças. `schema_version` não muda.
- **Imagens:** 12 PNGs em busto, 305×414, fundo transparente (seis visemas, olho aberto e `-piscada`), em
  `host/dono/` da pasta do episódio, que é a pasta pública do render e fica fora do Git. Imagens inteiras, não
  camadas: o `<Host>` do kit monta uma imagem por estado.
- **Origem registrada (regra 3):** `host/dono/origem.json` é obrigatório; sem ele, ou sem alguma imagem, o render
  para. O hash das imagens e do registro entra nas props da cena, então trocar o desenho refaz as cenas.
- **Template:** `video/src/donoSkin.ts` (pele de imagens escrita com o contrato do kit 0.3.0) e
  `HostWindow.tsx`, que escolhe a pele pelo `skin`. Um gesto e uma expressão; a boca e a piscada seguem o áudio.
- **Pendente:** o dono ainda não informou o gerador da folha de sprites; o `origem.json` dos dois Reels de teste
  está em `needs_review`, o que basta para prévia e não para vídeo final. A lista fechada da ADR 007 ainda não tem
  entrada para ativo de autoria do dono.
- **Kit:** a fábrica `createImageSkin` foi escrita no motion-kit (branch `feat/sprite-skin`, ainda não publicada);
  quando entrar num pin, `donoSkin.ts` passa a usá-la.
