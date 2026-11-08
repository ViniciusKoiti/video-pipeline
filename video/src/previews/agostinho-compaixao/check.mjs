import assert from 'node:assert/strict';
import {solveLimb} from '@viniciuskoitin/motion-kit/styles';
import {directionAt, handTargets, FPS, FRAMES, SCENE_FRAMES} from './timing.ts';

assert.equal(FRAMES / FPS, 24);
assert.equal(directionAt(0).scene, 0);
assert.equal(directionAt(SCENE_FRAMES).scene, 1);
assert.equal(directionAt(SCENE_FRAMES * 2).scene, 2);
assert.equal(directionAt(240 + 30).arrival, 0);
assert.equal(directionAt(240 + 100).arrival, 1);
assert.equal(directionAt(240 + 155).offer, 1);
assert.equal(directionAt(240 + 155).response, 0);
assert.equal(directionAt(240 + 195).response, 1);
assert.equal(directionAt(FRAMES - 1).offer, 1);
assert.throws(() => directionAt(FRAMES), RangeError);
for (let frame = 0; frame < FRAMES; frame++) {
  const state = directionAt(frame);
  for (const channel of ['arrival', 'offer', 'response']) assert.ok(state[channel] >= 0 && state[channel] <= 1);
  for (const who of ['lia', 'bia']) {
    const hands = handTargets(who, state.offer, state.response);
    for (const side of ['left', 'right']) {
      const shoulder = {x:side === 'left' ? 143 : 259,y:205};
      const hand = {x:hands[side][0],y:hands[side][1]};
      const limb = solveLimb(shoulder, hand, 78, 92, side === 'left' ? 1 : -1);
      assert.ok(!limb.clamped, `mão fora do alcance em ${frame}/${who}/${side}`);
      for (const point of [limb.shoulder, limb.elbow, limb.hand]) assert.ok(Number.isFinite(point.x) && Number.isFinite(point.y));
      assert.ok(Math.abs(Math.hypot(limb.elbow.x - limb.shoulder.x, limb.elbow.y - limb.shoulder.y) - 78) < .001);
      assert.ok(Math.abs(Math.hypot(limb.hand.x - limb.elbow.x, limb.hand.y - limb.elbow.y) - 92) < .001);
    }
  }
}
const regression = directionAt(275);
assert.ok(regression.arrival > 0 && regression.arrival < 1);
assert.equal(regression.offer, 0);
const lia = handTargets('lia', 1, 1).right;
const bia = handTargets('bia', 1, 1).left;
assert.ok(Math.abs((300 + lia[0] * .82) - (590 + bia[0] * .82)) < 8);
assert.equal(lia[1], bia[1]);
console.log('24s/3quadros; 720frames finitos; ossos fixos; aproximação/oferta/resposta ordenadas; encontro de mãos e regressão275 conferidos.');
