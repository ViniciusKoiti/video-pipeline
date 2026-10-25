# 033 — Evoluir primeiro a montagem por JSON no auto-play

- **Status:** aceita pelo dono; melhorias de montagem ainda não implementadas por esta decisão.
- **Data:** 2026-10-24
- **Relaciona-se com:** ADR 008 (cena com planos), ADR 011 (planos editoriais) e ADR 027 (motion-kit versionado).

## Contexto

O auto-play já monta o explicativo a partir de dados: `scenes.json` descreve narração,
planos e âncoras; a produção resolve mídia e tempos em `episode.json`; o adapter
Remotion gera props JSON que o template React interpreta usando o motion-kit.

O JSON não oferece a liberdade de qualquer composição React: só expressa os tipos,
campos e combinações integrados nos contratos e no template. Um componente disponível
na biblioteca não fica automaticamente disponível no roteiro JSON.

O pacote vizinho `@viniciusk/motion-video` tem outro contrato de montagem, documentado
atualmente para vídeos verticais e silenciosos. Ele não é a entrada do explicativo
narrado do auto-play, nem um substituto direto do fluxo atual.

## Decisão

**Primeiro facilitar a montagem por JSON no auto-play, com o motion-kit já integrado.
Depois avaliar o motion-video, sem migração ou segundo caminho de render nesta etapa.**

1. Reutilizar os planos e componentes existentes antes de criar recursos novos.
2. Quando uma cena necessária não puder ser descrita, identificar o limite concreto
   do contrato ou do template. Validar uma prova curta antes de ampliar o vocabulário JSON.
3. Integrar somente os campos necessários nos schemas Python, tipos TypeScript,
   adapter e template, com testes de contrato e revisão visual. O código implementa
   o comportamento reutilizável; o JSON escolhe conteúdo e opções suportadas.
4. Manter no auto-play as decisões editoriais, evidências, ativos, resolução dos tempos,
   gates e produção. Extrair para o motion-kit apenas composições ou comportamentos
   genéricos cuja reutilização tenha sido demonstrada.
5. Não mudar episódios aprovados nem a aparência de planos existentes por consequência
   incidental de uma melhoria. Mudanças visuais seguem a revisão pelo vídeo-régua.

## Sequência de avaliação

O próximo piloto deve usar poucos planos representativos do Cena e Conceito, como
apresentação do pensador, imagem comentada e comparação de conceitos. Esses exemplos
são candidatos de teste, não novos tipos de plano aprovados por esta ADR.

Conferir se trocar conteúdo dispensa editar TSX, se legenda e fonte permanecem legíveis
e se o tempo de montagem e as correções manuais diminuem. Registrar os limites encontrados;
não presumir ganho nem paridade completa entre React e JSON.

Na sequência, avaliar o motion-video com esses aprendizados: comparar contratos,
formatos, áudio, tempos, revisão e custo de manutenção. Decidir separadamente se vale
reutilizar recursos, contribuir com o pacote ou integrar algum caminho. Esta ADR não
autoriza migração, não unifica os contratos e não promete compatibilidade entre eles.

## Consequências

- O caminho vigente continua sendo `scenes.json` → produção → `episode.json` →
  adapter → template React/motion-kit → Remotion e montagem ffmpeg.
- Não criar um interpretador genérico de React em JSON, editor visual ou renderizador
  paralelo para atender esta decisão.
- Este registro orienta trabalhos futuros; não adiciona comandos, campos ou componentes.
