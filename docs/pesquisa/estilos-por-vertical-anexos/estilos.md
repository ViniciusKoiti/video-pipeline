# Os 50 estilos da lista do dono, com a triagem do coordenador (2026-10-07)

A lista veio colada pelo dono. A triagem é **julgamento do coordenador [I]**, exceto onde marca [F] (conferido nos arquivos do kit). O conselho pode discordar de qualquer linha.

## O que o tema e o kit têm hoje [F]

- `MotionTheme` (`/home/viniciusk/projetos/motion-kit/src/theme/MotionTheme.tsx`) guarda só: `font`, `mono`, `bg`, `surface`, `text`, `muted`, `accent`, `line` e `neon` (intensidade). **Não há tokens de forma (raio, traço), de sombra, de textura nem de movimento.** Há dois visuais no kit: o padrão neon sobre escuro e o preset sóbrio `editorial` (grafite, branco-gelo, um destaque dourado, sem neon), que é o do template.
- Template (`/home/viniciusk/projetos/auto-play/video/src/theme.ts`): fundo `#0E1116`, texto `#EDEDE8`, destaque dourado `#F2B134`, fonte Inter (OFL) carregada localmente. O kit só nomeia a família (`system-ui` por padrão); quem usa carrega o arquivo da fonte.
- Efeitos já no kit (`src/fx`, `src/motion`, `src/pixel`, `src/three`): `GlitchText` (divisão RGB e fatias), `NeonText` (brilho em camadas), `FilmGrain` (grão por `feTurbulence` e vinheta), `SceneBackground` (grade de pontos com parallax, partículas flutuando ou blobs de aurora), `SparkBurst`, `Marker` (círculo, sublinhado e seta com traço desenhado, com tremor de mão), `Focus` e `ParallaxLayer` (usam `blur`), `LightSweep` (`mix-blend-mode: screen`), módulo `pixel/` (sprites, grade, dígitos, apresentador), `three/` (`CinematicCard`, `CinematicStage`), `Hud`, `Gauge`, `TerminalWindow`, peças editoriais e de gráfico.
- **Não existe no kit:** `backdrop-filter` (vidro), padrões de meio-tom, sombra dura, tokens de forma. O `three` é dependência **opcional** do kit e **não está** no `video/package.json` do template (nova dependência exige justificativa e licença verificada, `CLAUDE.md` §2.9).

## Triagem

**A. O kit já tem a peça (ou quase) [F para as peças citadas]:** Kinetic type (`KineticHeadline`, `NeonText`), Glitch (`GlitchText`), Neon sign (`NeonText`), Particles (`SceneBackground`, `SparkBurst`), Aurora gradient (`SceneBackground`), Pixel art (`pixel/`), Infographic (gráficos e peças editoriais), Film noir (parcial: `FilmGrain` mais filtro de cor), Line art (parcial: `Marker`), Sci-fi HUD (parcial: `Hud`, `Gauge`, `TerminalWindow`), Tilt-shift (parcial: `Focus` e `ParallaxLayer` já usam `blur`), Topographic (parcial: `GeoMap` tem contornos de países, sem relevo).

**B. Preset de tema e poucas peças novas, sem ativo externo [I]:** Swiss style, Bauhaus, Mid-century, Blueprint, Bento grid, Neobrutalism, Art Deco, Flat 2D, Memphis, Op art, Pop art, Risograph, Split-flap, ASCII art, Synthwave, Vaporwave, Glassmorphism, Neumorphism, Y2K chrome, Frutiger Aero, Isometric, Cross-stitch.

**C. Dependem de ilustração, de textura, de 3D pesado ou de dependência nova [I]:** Clay 3D, Low poly, Cel shading, Paper collage, Origami, Manga, Watercolor, Woodcut, Stained glass, Art Nouveau, Surrealism, Graffiti, Psychedelic, Pencil sketch, Skeuomorphism, Grunge. Pela regra do projeto, **ilustração não é desenhada à mão**: só peças com licença aberta, imagem gerada para lacunas (com escolha humana) ou ilustrador.

## A lista completa (como colada)

Swiss style, Kinetic type, Pop art, Flat 2D, Clay 3D, Glassmorphism, Y2K chrome, Synthwave, Risograph, Paper collage, Glitch, Particles, Neobrutalism, Bauhaus, Memphis, Vaporwave, Pixel art, Isometric, Low poly, Line art, ASCII art, Frutiger Aero, Op art, Cel shading, Art Deco, Neumorphism, Stained glass, Film noir, Aurora gradient, Blueprint, Graffiti, Split-flap, Watercolor, Sci-fi HUD, Origami, Manga, Psychedelic, Infographic, Woodcut, Neon sign, Mid-century, Topographic, Cross-stitch, Skeuomorphism, Tilt-shift, Pencil sketch, Art Nouveau, Bento grid, Grunge, Surrealism.
