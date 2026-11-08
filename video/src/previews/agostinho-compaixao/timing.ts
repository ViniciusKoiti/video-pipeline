export const FPS = 30;
export const SCENE_FRAMES = 240;
export const FRAMES = SCENE_FRAMES * 3;

export function handTargets(who: 'lia' | 'bia', offer: number, response: number) {
  const left: [number, number] = who === 'lia' ? [116, 355] : [92 - 88 * offer, 355 - 55 * offer];
  const right: [number, number] = who === 'lia' ? [290 + 60 * response, 355 - 55 * response] : [290, 355];
  return {left, right};
}

export function directionAt(frame: number) {
  if (!Number.isInteger(frame) || frame < 0 || frame >= FRAMES) {
    throw new RangeError('Quadro fora da prévia');
  }
  const scene = Math.floor(frame / SCENE_FRAMES);
  const local = frame % SCENE_FRAMES;
  const ease = (start: number, end: number) => {
    const t = Math.max(0, Math.min(1, (local - start) / (end - start)));
    return t * t * (3 - 2 * t);
  };
  return {
    scene,
    local,
    arrival: scene === 1 ? ease(30, 100) : scene === 2 ? 1 : 0,
    offer: scene === 1 ? ease(110, 155) : scene === 2 ? 1 : 0,
    response: scene === 1 ? ease(155, 195) : scene === 2 ? 1 : 0,
  };
}
