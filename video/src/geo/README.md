# Contornos para os planos de mapa

`america-do-sul.json`: países da América do Sul e unidades da federação do Brasil, derivados do
[Natural Earth](https://www.naturalearthdata.com/) 1:50m, versão 5.1.2 (`ne_50m_admin_0_countries` e
`ne_50m_admin_1_states_provinces`, repositório `nvkelso/natural-earth-vector`, baixados em 2026-09-26).

**Licença:** domínio público ("All versions of Natural Earth raster + vector map data ... are in the public
domain"; crédito dispensado). Registro como ativo `Original` quando um mapa entrar num episódio.

Redução feita: só o contorno externo de cada polígono, coordenadas arredondadas a 0,01° (~1 km),
pontos repetidos removidos e ilhas com menos de 6 pontos descartadas. `label` é o ponto de rótulo da UF
dado pelo Natural Earth.
