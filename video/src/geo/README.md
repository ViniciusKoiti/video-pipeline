# Contornos para os planos de mapa

`america-do-sul.json`: países da América do Sul e unidades da federação do Brasil, derivados do
[Natural Earth](https://www.naturalearthdata.com/) 1:50m, versão 5.1.2 (`ne_50m_admin_0_countries` e
`ne_50m_admin_1_states_provinces`, repositório `nvkelso/natural-earth-vector`, baixados em 2026-09-26).
Usado nos mapas `scope: "region"`.

`world-110m.json`: países do mundo (sem a Antártida), do Natural Earth 1:110m (`ne_110m_admin_0_countries`,
mesmo repositório), copiado em 2026-09-28 dos exemplos do motion-kit 0.2.0 (`examples/geo/data/`, baixado lá
em 2026-09-28). Usado nos mapas `scope: "world"`, junto com os estados do Brasil do arquivo acima.

**Licença:** domínio público ("All versions of Natural Earth raster + vector map data ... are in the public
domain"; crédito dispensado). Registro como ativo `Original` quando um mapa entrar num episódio.

Redução feita: só o contorno externo de cada polígono, pontos repetidos removidos e ilhas pequenas
descartadas; coordenadas arredondadas a 0,01° (~1 km) no 1:50m e a 0,1° no 1:110m. `label` é o ponto de
rótulo da UF dado pelo Natural Earth.

**Códigos (ADR 011):** cada país e estado tem `id`, o código usado em `map.highlight`: país em ISO 3166-1
alfa-3 ("BRA"; no 1:110m é o `ADM0_A3` do Natural Earth, que coincide com o ISO na maioria dos países) e estado
em ISO 3166-2 ("BR-SP"). Os `id` do `america-do-sul.json` foram acrescentados em 2026-09-28 a partir do nome do
país e da `uf`. O `vp check` recusa código de `highlight` que não esteja nestes arquivos.
