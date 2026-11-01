# Pauta: "O que é um mod do Claude Code" (Reel tec, episódio 1 da série de mods), 2026-10-26

Reel de 60 s, vertical. Explica o conceito antes dos exemplos. Pauta para validação do dono antes da voz e do render.

## Ângulo

Um mod é texto e configuração dentro do projeto que muda o que o agente faz. Não é plugin de mágica nem código
escondido. Os três tipos que o Claude Code lê de `.claude/`: skill, agente e configuração (permissões e hooks).

## Exemplos reais (todos rastreados no Git, em `.claude/`)

- 13 skills em `.claude/skills/` (contagem de pastas).
- 5 agentes em `.claude/agents/` (um `.md` por agente, com `tools` e `model` no cabeçalho).
- 1 regra `ask` em `.claude/settings.json`: `Bash(* postiz schedule *)`, que pede confirmação antes de agendar.
- `.claude/settings.local.json` fica fora do Git: a configuração pessoal não vai para o repositório.

## Correção de termo

Os Shorts de mods anteriores chamaram a skill de "mod". Este Reel usa a definição do Claude Code: a skill é um
tipo de mod, ao lado do agente e da configuração. O primeiro vídeo da série define o termo.

## Hipótese (a registrar)

Retenção acima de 60% nos 15 s iniciais, com a definição no gancho. Medida: retenção e inscritos aos 7 e 28 dias.

## O que falta

- OK do dono na pauta.
- Narração final em pt e en (rascunhos em `data/episodes/reel-claude-mod-o-que-e/`).
- Voz, render e gates. Canal de publicação ainda por decidir.
