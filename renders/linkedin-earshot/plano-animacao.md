# Plano de animação: Dei ouvidos ao meu agente (LinkedIn 4:5, 2026-11-09)

Rascunho para o dono; sem voz nem render. Formato do `linkedin-motion-kit`: 1080×1350, 30 fps, legenda queimada,
composição TSX no kit (a nova, p.ex. `examples/divulgacao/ComoOuvidos.tsx`, com as peças de `pieces.tsx` e o
`<Pipeline>`), janela flutuante com a **pele do dono** (decisão de 2026-11-09), `mouthLevels` pelo `vp short boca`.
O quadro "Controle obrigatório" abaixo vale antes da voz e depois do render.

## Fio visual

Uma pipeline de blocos conectados que aparece na batida 1 sem o ouvido e ganha, na 2, o bloco `earshot` entre o
`juntar` e o gate 4. Esse bloco é onde as cenas seguintes acontecem; a seta que atravessa a pipeline leva um valor
(o volume do arquivo) e o bloco o confere.

Blocos: `JSON` → `render (mudo)` → `juntar` → **`earshot`** → `gate 4` → `Postiz`. A seta é "o arquivo".
Elemento ativo = o bloco com contorno aceso; valor em trânsito = o MP4 com seu volume.

## Cenas

| Cena (id) | Trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- | --- |
| `gancho` | "Meu agente montou um Short três decibéis mais alto do que a minha conta dizia, e ninguém nessa linha escuta o vídeo que sai" | **Abertura fria, já no quadro 0:** medidor "ffmpeg" parado em `−15,0` | Dois medidores (ffmpeg e earshot) sobre o mesmo Short; depois a pipeline pequena, com o `?` no lugar do ouvido | O medidor do earshot sobe de `−15,0` a `−12,0` em "três decibéis mais alto"; acende `+3,0 dB que a conta não via`; em "ninguém nessa linha" entra a pipeline sem o bloco de som e o MP4 passa até o gate | Os dois medidores divergem e o MP4 segue sem ninguém medir o som | `timeline` do `short-lista-ligada-pt` (2026-10-31); `vp short` (ADR 035) |
| `ouvidos` | "dei ouvidos a ele com o earshot ... sem rede" | A pipeline da cena anterior | Entra o bloco `earshot` entre `juntar` e `gate 4`, com selo "CPU · offline · MIT"; linha de terminal `earshot measure final.mp4` | O bloco encaixa, as setas se religam por ele | Pipeline com o ouvido; crédito "earshot · Leon Lin" | `termos-earshot.md` (licença, CPU, offline) |
| `medida` | "ffmpeg media ... menos quinze ... earshot ... menos doze" | Bloco `earshot` aceso; um MP4 mono (um canal) na seta | Dois medidores: `ffmpeg (ebur128)` e `earshot (BS.1770)`, ligados ao mesmo MP4 | O MP4 mono passa; o medidor ffmpeg para em `−15,0`; o do earshot, que duplica o canal nos dois alto-falantes, sobe a `−12,0`; a diferença `3,0 dB` acende | Os medidores divergem, e o valor do earshot é o que o YouTube usa | `timeline` do `short-lista-ligada-pt` (2026-10-31) |
| `decisao` | "três decibéis ... juntar passou a sair em estéreo ... o mesmo Short, refeito, mede menos quatorze vírgula dois" | Medidores divergentes (−15,0 × −12,0) | O bloco `juntar` ganha uma saída "estéreo (mesmo canal nos dois lados)" antes do `loudnorm`; o mesmo Short volta pelo `earshot` | O chip do `juntar` troca `mono` por `estéreo`; o medidor do earshot cai de `−12,0` para `−14,2`, dentro da faixa −15 a −13 | `juntar` em estéreo; o Short refeito mede `−14,2 LUFS` (pico `−1,5 dBTP`) | `final-sfx.mp4.earshot.json` (estéreo, 2 canais); decisão de 2026-10-31 |
| `cortes` | "o efeito cai no corte ... a até um quadro" | Régua de tempo do Short (38,2 s) com 4 marcas de corte | Cada corte liga ao pico do som mais próximo (seta curta) | Os 4 sons acendem sobre os cortes em 5,2 / 15,6 / 24,6 / 31,6 s, com o deslocamento de cada um (+26, −6, +27, −27 ms); chip "mediana 26,5 ms · 1 quadro = 33 ms" | Quatro cortes alinhados | `sync.cuts` do mesmo JSON (4 de 4 a até 1 quadro; acaso 31%) |
| `limite` | "em música ele erra e avisa ... fraca" | Régua de música sob a fala | O `earshot` recebe a faixa e a descrição "calm instrumental background music, no vocals" | Medidor de ajuste fica em `weak (z +2,0)`; selo "unvalidated" do próprio earshot; a palavra "veredito" é riscada e fica "segunda opinião" | A dica de que música é o ponto fraco, sem prometer mais do que a medida mostrou | `match` de `ytal-spirit-of-fire.mp3`; aviso do earshot |
| `etapa` | "volume entre −15 e −13, pico até −1, nenhum silêncio" | Pipeline completa | O bloco `earshot` vira porta com três critérios `✓ ✓ ✓` e um `✗` simulado que **bloqueia** a seta para o gate | Três verificações acendem em sequência; chip "~1× o tempo real (Short) · ~0,2× (longo)" | A porta só deixa passar o arquivo dentro do alvo; o gate 4 humano segue depois dela | Skill `short-diario`, passo 8; `termos-earshot.md` (custo) |
| `fecho` | "O link está no primeiro comentário. Que medida você poria antes de aprovar um vídeo?" | Pipeline com a porta | Cartão final: "link no 1º comentário"; linha pequena "ainda não usei: forge, fit, banco de sons" | O dono em destaque; a pergunta sobe na tela | Pergunta aberta ao público | README do earshot (só o nome das funções) |

O `✗` simulado da cena `etapa` é ilustração e deve ser rotulado como exemplo, para não parecer um resultado medido.
Todo número na tela está na tabela de `roteiro.md`; nenhum é inventado para a animação.

## Música

**Sem trilha, por decisão desta pauta** (vídeo de demonstração técnica, como o `linkedin-motion-kit`; o motivo é que a
leitura dos medidores e das réguas é o conteúdo e a voz já ocupa a faixa de atenção). A mistura de música no Short
também não existe ainda (`juntar` só mistura voz e SFX). Efeito sonoro (ADR 035) é opcional e só se o dono quiser:
sugestão de um tom curto quando o bloco `earshot` encaixa e um bloqueio na porta da cena `etapa`. Se o dono preferir
música, o plano volta ao `diretor-musical` antes da voz.

## Controle obrigatório (direção editorial)

| Item | Antes da voz/render | Depois do render |
| --- | --- | --- |
| Aplicação | Pipeline de vídeo por agente descrita na pauta e acima | **A conferir:** blocos reconhecíveis |
| Decisão de System Design | Etapa de medida entre `juntar` e gate 4; `juntar` em estéreo | **A conferir:** relação explicada na fala e no fluxo |
| Benefício e limite | Medido (−15 × −12; 4/4 cortes) e limites (música fraca, custo, não decide) com origem em `roteiro.md` | **A conferir:** nada além da medida |
| Explicação visual | Sequência acima, rastreável à fala | **A conferir:** quadros antes/durante/depois abertos |

Lacunas antes da voz: **nenhuma de conteúdo**; pendem a escuta do dono para a pronúncia, a confirmação de que os números
de 31/10 servem, e a composição TSX no kit.

## Controle depois do render (2026-11-09, `final.mp4`, 57,8 s, 1080×1350, 30 fps, AAC estéreo, −14,5 LUFS)

Quadros abertos: 0, início/meio/fim de cada transição, e o fecho. Defeitos achados na 1ª passada e corrigidos na 2ª:
janela do dono vazia nos primeiros ~20 quadros (o `Host` entrava no quadro 0; agora `at={-30}`) e rótulos `+26 ms` e `+27 ms`
sobrepostos na cena `cortes` (três linhas de rótulo). Conferido: nenhuma animação cortada antes do fim, janela à direita sem
cobrir blocos, legenda sem tocar o rodapé. O `✗` da `etapa` diz "o mono de antes (−12,0 LUFS) teria ficado de fora"
(número real, não exemplo). Não conferido: pronúncia (escuta do dono) e sincronia fina da legenda (tempo por caracteres).

| Item | Depois do render |
| --- | --- |
| Aplicação | Pipeline JSON → render → juntar → earshot → gate 4 → Postiz reconhecível |
| Decisão de System Design | Bloco `earshot` entra antes do gate 4; `juntar` troca mono por estéreo e o medidor cai de −12,0 a −14,2 |
| Benefício e limite | −15,0 × −12,0; 4 de 4 cortes a até 1 quadro; música `weak`, "segunda opinião" |
| Explicação visual | Quadros antes/durante/depois conferidos |
