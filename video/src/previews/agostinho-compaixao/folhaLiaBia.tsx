import React from 'react';
import {AbsoluteFill, Composition, registerRoot} from 'remotion';
import {Host} from '@viniciuskoitin/motion-kit/host';

/**
 * Folha de escolha de Lia e Bia, recortes da fábrica do kit (mesma família da receita A do
 * apresentador azul, `apresentadorAzul.referencia.tsx`). Personagens fictícias e originais.
 * Estudo de aparência: não é o storyboard nem o episódio.
 */

import {lia, bia} from './personagens';

const GESTOS = ['rest', 'open', 'think'] as const;
const NOMES: Record<typeof GESTOS[number], string> = {rest: 'repouso', open: 'oferece a mão', think: 'pondera'};

const Folha: React.FC = () => (
  <AbsoluteFill style={{background: '#f3eee4', color: '#302f2b', fontFamily: 'Arial, sans-serif', padding: '40px 70px'}}>
    <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #c6beb0', paddingBottom: 18, fontSize: 19, letterSpacing: 3}}>
      <span>LIA E BIA / FOLHA DE ESCOLHA</span><span>createCutoutSkin · personagens fictícias e originais</span>
    </div>
    {[
      {nome: 'Lia', nota: 'bob escuro, blusa coral, triste (olhar baixo, lágrima)', skin: lia, gazeY: 0.45, tilt: -3, seed: 1},
      {nome: 'Bia', nota: 'coque ocre, blusa verde-azulada, atenta', skin: bia, gazeY: 0, tilt: 0, seed: 7},
    ].map(({nome, nota, skin, gazeY, tilt, seed}) => (
      <div key={nome} style={{display: 'flex', alignItems: 'center', marginTop: 14}}>
        <div style={{width: 380}}>
          <div style={{fontFamily: 'Georgia, serif', fontSize: 52}}>{nome}</div>
          <div style={{marginTop: 8, fontSize: 20, color: '#6a6256', maxWidth: 320}}>{nota}</div>
        </div>
        {GESTOS.map((gesture, i) => (
          <div key={gesture} style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
            <div style={{position: 'relative', height: 360, width: 300, display: 'flex', justifyContent: 'center'}}>
              <div style={{position: 'absolute', left: 50, right: 50, bottom: 6, height: 16, borderRadius: '50%', background: '#d8cdb7'}} />
              <Host identity={{skin: skin.name}} skin={skin} size={360} gesture={gesture} seed={seed + i}
                pose={{gazeX: 0, gazeY, headTilt: tilt}} />
            </div>
            <div style={{fontSize: 20, fontFamily: 'monospace', color: '#2f6fb3', marginTop: 4}}>{NOMES[gesture]}</div>
          </div>
        ))}
      </div>
    ))}
  </AbsoluteFill>
);

registerRoot(() => <Composition id="FolhaLiaBia" component={Folha} durationInFrames={30} fps={30} width={1920} height={1080} />);
