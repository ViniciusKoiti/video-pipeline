// Linha do tempo da S17 do mec-fechadura-pt (chave errada na vista lateral): frame → estado do desenho. Função pura.
// A duração é a da voz final (tempos-errada.json, conferido por check-errada.mjs). Dentro da cena, os instantes são frações da duração
// (estimativa pela posição das palavras); o tempo exato por palavra só sai do `vp render`. A entrada da chave é compartilhada (entrada.ts).
import {SHEAR} from './geometria.ts';
import {FPS} from './linhaDoTempo.ts';
import {estadoEntrada} from './entrada.ts';
import type {EstadoEntrada} from './entrada.ts';

export const DURACAO_ERRADA = 14.36;
export const TOTAL_ERRADA = Math.round(DURACAO_ERRADA * FPS);

/** Fundos dos cortes da chave errada (um y por coluna). Coluna 1 coincide com a chave certa (alinhada); 2, 4 e 5 ficam fundos demais
 *  (o pino superior atravessa a linha) e a 3 rasa demais (o pino de chave passa da linha). Valores ilustrativos. */
export const FUNDOS_ERRADA: readonly number[] = [SHEAR + 105, SHEAR + 85 + 30, SHEAR + 125 - 25, SHEAR + 95 + 45, SHEAR + 115 + 15];

export type EstadoErrada = EstadoEntrada;

export const estadoErradaEm = (frame: number): EstadoErrada => estadoEntrada(frame, TOTAL_ERRADA, {alerta: true, juncoes: true});
