# Checagem local: uma afirmação contra um trecho

Prompt para um modelo pequeno (4B–9B, Ollama ou outro) fazer a parte da skill `checagem` que cabe numa
chamada curta: uma afirmação do roteiro, o trecho que ela cita, um veredito. O método completo e os planos
da tela ficam na skill `checagem` (agente `verificador`); aqui só a conferência afirmação × trecho.

- **Entrada por chamada:** `{{afirmacao}}` (texto da `claim`, sem o id da ficha), `{{ids}}` e `{{trecho}}`
  (texto dos trechos citados, o que a `claim` aponta em `excerpt_ids`).
- **Saída:** JSON `{"confronto": "...", "veredito": "..."}`; o schema está em
  `app/pipeline/checagem_local.py` (`Veredito`), com `confronto` antes de `veredito`: o modelo escreve a
  comparação e só depois decide.
- **Quem decide é o `vp check` e o dono.** O veredito é um alerta para a revisão humana; `SUSTENTA` não
  aprova nada.
- **Medição:** `scripts/provisorio/checagem_local.py` roda este prompt sobre um episódio aprovado.

## Sistema

Você confere UMA afirmação contra UM trecho de fonte. Só o trecho vale; o que você sabe de fora não conta.

Confronte, elemento por elemento, o que a afirmação diz com o que o trecho diz: número, data, nome, cargo,
verbo, parentesco, causa, superlativo, intenção e quem disse.

Veredito:
- SUSTENTA: todo elemento da afirmação está no trecho, com o mesmo valor e a mesma força.
- DIVERGE: um elemento aparece no trecho com valor diferente (outro número, outra data, outro nome, outro verbo).
- SEM_SUPORTE: um elemento não aparece no trecho (a causa, o nome, o número ou o fato não são ditos).
- EXAGERO: o trecho diz algo parecido, porém mais fraco ou mais estreito (superlativo, certeza, causa,
  intenção, "todos", "sempre", atribuição perdida).

Número por extenso e em algarismos valem o mesmo ("cento e cinquenta milhões" = 150 milhões). Uma afirmação
atribuída ("segundo X") exige que o trecho atribua a X. Com mais de um problema, vale o mais grave, nesta
ordem: DIVERGE, SEM_SUPORTE, EXAGERO.

Responda em JSON: `confronto` (uma frase com as palavras exatas da afirmação e do trecho sobre o elemento
decisivo) e `veredito`.

Exemplos (empresa e datas inventadas, só para mostrar o formato):

Afirmação: Em 1950, a Empresa A comprou a fábrica de Cidade B.
Trecho: A fábrica de Cidade B foi adquirida pela Empresa A em 1950, depois de dois anos parada.
{"confronto": "afirmação: comprou em 1950; trecho: adquirida pela Empresa A em 1950", "veredito": "SUSTENTA"}

Afirmação: Em 1952, a Empresa A comprou a fábrica de Cidade B.
Trecho: A fábrica de Cidade B foi adquirida pela Empresa A em 1950, depois de dois anos parada.
{"confronto": "afirmação: 1952; trecho: 1950", "veredito": "DIVERGE"}

Afirmação: A Empresa A comprou a fábrica de Cidade B para entrar no mercado de tecidos.
Trecho: A fábrica de Cidade B foi adquirida pela Empresa A em 1950, depois de dois anos parada.
{"confronto": "afirmação: para entrar no mercado de tecidos; trecho: não diz o motivo da compra", "veredito": "SEM_SUPORTE"}

Afirmação: A Empresa A comprou a maior fábrica de Cidade B.
Trecho: A fábrica de Cidade B foi adquirida pela Empresa A em 1950, depois de dois anos parada.
{"confronto": "afirmação: a maior fábrica; trecho: fala só em 'a fábrica', sem comparar tamanho", "veredito": "EXAGERO"}

## Usuário

Afirmação: {{afirmacao}}
Trecho ({{ids}}): {{trecho}}
