---
name: short-diario
description: Rotina de um Short da série "eu medi" até o pacote do Postiz, sem gates (ADR 036). Use quando o timer chamar ou quando o dono pedir "roda a rotina".
---
# Short diário
O pedido em pé do dono está na ADR 036: tudo abaixo roda sem perguntar; nada fora disto. Nunca `vp approve`, nunca `vp postiz duvida` nem `schedule`, nunca vidIQ, nunca push, nunca baixar ativo. Em dúvida, pare e registre.
## Entrada
- `renders/serie-conceitos/serie.md` (ou `fila.md`): a próxima pauta aprovada sem pasta `renders/short-<conceito>/` é a de hoje. Sem pauta: registre "sem pauta" em `data/rotina/AAAA-MM-DD.md` e pare.
- `cpu_probe()` acima de 0,3 s: registre "máquina limitada" e pare.
- Molde: `renders/short-lista-ligada/` e `renders/short-memory-leak/`.
## Método (pare no primeiro passo que falhar; registre tudo)
1. Pastas: `renders/short-<conceito>/demo/`, `data/episodes/short-<conceito>-pt`, `-en` (com `traducao.json`) e `-ig`.
2. Medição: o programa da pauta em `demo/`, `medir.sh` gravando `demo/resultado.txt` com ambiente, versão, data, 15 rodadas, mediana e extremos.
3. `roteiro.md` com a origem de cada número; o "porquê" vai para a pergunta do fecho.
4. `narracao.pt.json` (pela skill humanizer-narracao) e `narracao.en.json`, cinco cenas, 35 a 45 s; copiar como `narracao.json` nas pastas de episódio.
5. `content.pt.json` e `content.en.json` no molde (`safeArea: shorts`, `footer` com o ambiente, `showRatio: false`); `validate` e `inspect` do kit com cwd na pasta do JSON; corrigir rótulos longos; `review` e listar os quadros.
6. `medicao.json` com todos os números; `vp medicao <id>-pt` e `-en` limpos; `vp traducao <id>-en` limpo. Corrija a narração ou o `medicao.json`, nunca o resultado.
7. `shorts_tec.py voz` (Modal), `tempos`, `render` do kit nas duas pastas; o Reel usa o `content.en.json` com `host` só se a pele estiver `approved`.
8. `sfx.pt.json` e `sfx.en.json` no molde; `shorts_tec.py sfx`; `juntar --sfx` em `renders/final.mp4`; `conferir_audio.py --content --sfx` sem problema.
9. `post.json` por saída (título provisório da pauta, origem dos números, divulgação da voz clonada, link do baixo-nivel-demos); `shorts_tec.py gate` por saída; `vp postiz upload` e `vp postiz pacote --episode` por saída; confira os ids em `vp postiz integrations`.
10. `data/rotina/AAAA-MM-DD.md`: o que foi feito, os avisos, os quadros para olhar e os comandos que faltam ao dono (`vp approve ... --step translation`, `--step preview` ×3, push, `vp postiz duvida` e `schedule` ×3).
## Regras
Tudo da skill `shorts-tec` vale. Só o que a medição mostra. Não refazer o que existe com o mesmo hash; não apagar saídas. Uma execução por dia.
