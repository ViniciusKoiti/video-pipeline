# Plano de animação

## Tempos após voz

As durações da tabela de planejamento abaixo são históricas. Os arquivos finais para o parent estão em
`pronto/content.pt.voz.json` e `pronto/content.en.voz.json`; usar estes arquivos para a montagem final.
As copias anteriores nos episodios sao intermediarias. Eventos foram transformados a partir de 1,3 s, com o ultimo
movimento até `min(fala - 0,45 s, cena - 1,4 s)`, preservando a ordem e as rotas. O intervalo adicional
inclui estabilização do kit e leitura mínima; validate/inspect ficaram sem diagnósticos.

| Cena | PT final | EN final |
| --- | --- | --- |
| gancho | 4,4 s | 5,6 s |
| fechado | 5,8 s | 6,4 s |
| aberto | 4,7 s | 5,5 s |
| meio-aberto | 4,1 s | 4,0 s |
| teste | 4,4 s | 5,2 s |
| medido | 5,5 s | 4,8 s |
| limite | 6,2 s | 7,7 s |
| Total | 35,1 s | 39,2 s |

Cada fala entra no começo da cena após o trim de speech usado por `vp short juntar`. PT mantém leituras
finais de 0,769 a 0,881 s para respeitar o piso editorial de 35 s; EN usa 0,352–0,433 s. Não são pausas internas
na narração. Na concatenação dos trims, maior silêncio a -50 dB: PT 0,964562 s, EN 0,561041 s.
O MP4 final tambem foi medido: PT maximo 0,984 s; EN sem trecho >=0,8 s, a -40 dB.

As timelines finais não são iguais entre idiomas: uma timeline comum criaria vazios acima de dois segundos
em PT. Os JSONs autorais originais permanecem iguais nos campos não textuais; os derivados diferem só nos
textos localizados e campos temporais. A conferência `vp traducao` dos originais não certifica essas diferenças
temporais: a aprovação humana permanece pendente; revisao visual tecnica registrada abaixo.
Sem gasto de voz para padronizar o ritmo.

Vertical 1080 x 1920, safeArea shorts, estilo editorial. Diagramas originais com dois a quatro nós,
legend false para poupar espaço; sem host, assets externos ou Lottie. Tempos em segundos da cena, não da demo.
O esquema mostra ações selecionadas, não reproduz cada requisição da execução.

| Cena / duração inicial | Fala e regra | Estado inicial | Nós e conexões | Ação visível e estado final | Fonte |
| --- | --- | --- | --- | --- | --- |
| gancho / 5,6 s | Pagamento cai; threads esperam | Capa legível no primeiro quadro | Hook com Java explícito | Pergunta localiza a dependência; mecanismo começa na cena seguinte | F2a, D1 |
| fechado / 6,7 s | Fechado passa; cinco falhas seguidas abrem | Nó Fechado ativo | Fechado -> Pagamento; Pagamento -> Fechado (erro); Fechado -> Aberto (limiar) | Token de chamada, erro de volta, espera em Fechado, transição ao nó Aberto; não diz que só cinco chamadas chegaram | F1a, F2b, D1 |
| aberto / 5,5 s | Erro sem chamar evita espera nova | Aplicação chama breaker aberto | Pedidos Java -> Aberto; Aberto -> Pedidos Java; caminho tracejado Aberto -> Pagamento | Requisição chega e erro retorna; nenhum token ao pagamento. Aplicação recebe failed, não done | F1a/F1d, D1 |
| meio-aberto / 5 s | Após dois segundos permite teste | Aberto aguardando janela | Aberto -> Meio-aberto (2 s); Meio-aberto -> Pagamento (teste) | Token da transição e teste único; pagamento running não significa pagamento concluído | F1b, D1 |
| teste / 5,2 s | Sucesso fecha; falha reabre | Meio-aberto ativo | Meio-aberto -> Fechado (sucesso); Meio-aberto -> Aberto (falha), ambos condicionais | Primeiro ilumina ramo de sucesso, depois ramo de falha; alternativas didáticas, não dois resultados da mesma sonda | F1c, D1 testes controlados |
| medido / 7,2 s | Simulação: menos chamadas durante falha | Modos sem/com breaker | Sem breaker -> Pagamento; Com breaker -> Pagamento | Tokens 60 e 24 identificados como chamadas; todos os nós de chamada terminam failed, pois são chamadas na falha. Não são pagamentos bem-sucedidos | D1 resumos chamadas_na_falha |
| limite / 8,2 s | Proteção ainda custa recusas após retorno | Pagamento já recuperado, breaker aberto | Pedidos -> Aberto; Aberto -> Pedidos; Aberto -> Pagamento tracejado | Pagamento done sinaliza dependência saudável; requisição retorna failed sem token à dependência. Tela: 7 após retorno; 133 recusas totais, ambas medianas | F2c, D1 recusadas/recusadas_pos_falha |

## Controle de System Design

| Item | Antes da voz/render | Depois do render |
| --- | --- | --- |
| Aplicação | Pedidos Java -> breaker -> pagamento; simulação explícita | Conferido em 05/11 nos quadros pt/en e MP4s finais |
| Decisão | Recusar novas chamadas enquanto aberto, permitir sonda depois da janela | Relação dita na voz e representada pelo fluxo, conferida nos dois idiomas |
| Benefício e limite | Menos chamadas à dependência durante falha; erro ao cliente, inclusive após retorno; sem ganho de latência alegado | 60/24 chamadas e 7 recusas após retorno conferidos contra medição e quadros finais |
| Explicação visual | Passagem, bloqueio, teste, ambos os ramos e custo animados com estados/tokens | Quadros antes/durante/depois, capas, margens e folhas finais abertos |

O preenchimento complementa a pauta preservada; não altera nem aprova o texto histórico dela.
Na cena gancho, a situação é verbal; a espera aparece no nó Fechado da cena seguinte.
Estados do motor (`running`, `waiting`, `failed`, `done`) não são os estados do breaker:
closed/open/half-open aparecem nos nomes dos nós. `done` no pagamento da última cena só indica a recuperação
externa; `failed` no pedido mantém explícita a recusa. Sem equivalência entre degradação e sucesso.

## Sincronia e leitura

Primeiro evento em pelo menos 1,3 s; fim do último movimento com pelo menos 1 s até o fim da cena.
Sem silêncio interno planejado. Ajustar eventos com as falas após a voz; nunca encurtar a cena sem recalcular
os estados/tokens. Manter iguais os campos não textuais das versões pt/en, inclusive durações e IDs.
As posições e rótulos devem ser conferidos em quadros; validate/inspect não substituem revisão visual.
O planejamento inicial não autorizava voz; a continuação autorizou a síntese pontual descrita acima.
Voz, review e render executados na retomada autorizada. PT final: `final.pt.v2.mp4` (35,1 s),
EN: `final.en.mp4` (39,2 s). Sem musica, SFX ou apresentador. Quadros dos reviews pt
`1793884047821-274bcec2` e en `1793884284779-20a5120d` abertos, com antes/durante/depois.
PT v2 reduz duas caudas de leitura em 0,1 s; folhas extraidas dos MP4s finais tambem abertas:
`quadros-final.pt.v2.png` e `quadros-final.en.png`. Silencio final maximo PT 0,984 s;
EN sem trecho >=0,8 s, ambos a -40 dB. Esta conferencia tecnica nao e escuta nem aprovacao do dono.
Pacotes de gate PT/EN montados sem approve, upload ou Postiz.
