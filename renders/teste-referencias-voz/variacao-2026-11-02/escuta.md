# Variação de entrega: atual × forte (2026-11-02)

Pedido do dono: variar mais as entregas e deixar a maioria no tom atual. Mesma frase e mesma referência por entrega da
comparação anterior; só mudam `exaggeration` e `cfg_weight` de hook, turn e invite. A config (`[chatterbox.delivery]`)
não foi alterada. Três falas novas no Modal (script fora do repositório); todas niveladas a −16 LUFS e −1,5 dBTP.

[Ouvir comparação](comparacao.mp3)

| # | Fala | Início |
|---|---|---|
| 1 | neutral 0,5/0,5 (fica como está) | 0,00 s |
| 2 | hook atual 0,8/0,3 | 5,63 s |
| 3 | hook forte 1,0/0,3 | 12,30 s |
| 4 | turn atual 0,7/0,4 | 19,45 s |
| 5 | turn forte 0,9/0,35 | 27,80 s |
| 6 | invite atual 0,6/0,4 | 36,19 s |
| 7 | invite forte 0,8/0,35 | 43,46 s |

Medidas (ebur128): todas entre −16,3 e −15,7 LUFS, pico −1,4 a −1,5 dBFS. A faixa de volume dentro da fala (LRA)
subiu no invite (1,9 → 2,7 LU), caiu no hook (1,7 → 1,2) e ficou quase igual no turn (2,6 → 2,4); a neutra tem 1,2.
É só uma pista, porque a LRA não mede entonação; quem decide é a escuta.

**Escuta do dono (2026-11-02):** "Gostei das fortes, pode aplicar na config e na skill". Os três valores fortes foram
para `[chatterbox.delivery]` em `config/providers.toml`, e a skill `short-diario` (passo 7) ganhou a regra da proporção
(gancho só na primeira cena, convite só na última, no máximo uma virada, ≥ 60% neutras).
