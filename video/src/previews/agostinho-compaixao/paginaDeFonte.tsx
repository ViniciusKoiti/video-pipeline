import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Pagina, PAGINA_FRAMES} from './paginaFonteCena';

/** Entrada isolada do teste da página de fonte (a cena em si fica em paginaFonteCena.tsx). */
registerRoot(() => <Composition id="PaginaDeFonte" component={Pagina} durationInFrames={PAGINA_FRAMES} fps={30} width={1280} height={720} />);
