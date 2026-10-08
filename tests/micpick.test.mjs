import { test } from 'node:test';
import assert from 'node:assert/strict';
import { isHandsFree, headsetName, preferredMic, handsFreeOutputFor } from '../prep/app/micpick.js';

// Device names as Chrome on Windows reports them (ticket #6's boAt, the owner's JBL, 6-7 Oct 2026).
const jblMics = [
  { deviceId: 'default', label: 'Default - Headset (JBL WAVE BEAM Hands-Free AG Audio)' },
  { deviceId: 'communications', label: 'Communications - Headset (JBL WAVE BEAM Hands-Free AG Audio)' },
  { deviceId: 'm1', label: 'Headset (JBL WAVE BEAM Hands-Free AG Audio)' },
  { deviceId: 'm2', label: 'Microphone Array (Realtek(R) Audio)' },
];
const jblOutputs = [
  { deviceId: 'default', label: 'Default - Headphones (JBL WAVE BEAM Stereo)' },
  { deviceId: 'communications', label: 'Communications - Headset (JBL WAVE BEAM Hands-Free AG Audio)' },
  { deviceId: 'o1', label: 'Headphones (JBL WAVE BEAM Stereo)' },
  { deviceId: 'o2', label: 'Headset (JBL WAVE BEAM Hands-Free AG Audio)' },
  { deviceId: 'o3', label: 'Speaker (Realtek(R) Audio)' },
];

test('a Hands-Free entry is recognised with or without Chrome\'s prefixes', () => {
  assert.equal(isHandsFree('Headset (boAt Rockerz 510 Hands-Free AG Audio)'), true);
  assert.equal(isHandsFree('Default - Headset (JBL WAVE BEAM Hands-Free AG Audio)'), true);
  assert.equal(isHandsFree('Headphones (boAt Rockerz 510 Stereo)'), false);
  assert.equal(isHandsFree('Microphone (iVOOMi Netra 1080 FHD)'), false);
  assert.equal(isHandsFree(''), false);
  assert.equal(headsetName('Headset (boAt Rockerz 510 Hands-Free AG Audio)'), 'boat rockerz 510');
  assert.equal(headsetName('Default - Headphones (boAt Rockerz 510 Stereo)'), 'boat rockerz 510');
});

test('a Hands-Free default microphone yields to a real one, so the earbuds stay in stereo', () => {
  assert.equal(preferredMic(jblMics).deviceId, 'm2');
  assert.equal(preferredMic(jblMics, 'Headset (JBL WAVE BEAM Hands-Free AG Audio)').deviceId, 'm2');
});

test('nothing changes when the default microphone is not Hands-Free, or it is the only one', () => {
  assert.equal(preferredMic([
    { deviceId: 'default', label: 'Default - Microphone Array (AMD Audio Device)' },
    { deviceId: 'm1', label: 'Microphone Array (AMD Audio Device)' },
    { deviceId: 'm3', label: 'Headset (JBL WAVE BEAM Hands-Free AG Audio)' },
  ]), null);
  assert.equal(preferredMic(jblMics.slice(0, 3)), null);
  assert.equal(preferredMic([]), null);
  assert.equal(preferredMic(undefined), null);
});

test('the Hands-Free microphone maps to its own headset\'s Hands-Free output, the plain entry first', () => {
  assert.equal(handsFreeOutputFor('Headset (JBL WAVE BEAM Hands-Free AG Audio)', jblOutputs).deviceId, 'o2');
  assert.equal(handsFreeOutputFor('Communications - Headset (JBL WAVE BEAM Hands-Free AG Audio)', jblOutputs).deviceId, 'o2');
  assert.equal(handsFreeOutputFor('Headset (boAt Rockerz 510 Hands-Free AG Audio)', jblOutputs), null, 'another headset');
  assert.equal(handsFreeOutputFor('Microphone Array (AMD Audio Device)', jblOutputs), null);
  assert.equal(handsFreeOutputFor('Headset (JBL WAVE BEAM Hands-Free AG Audio)', jblOutputs.slice(1, 2)).deviceId, 'communications', 'only the prefixed entry left');
  assert.equal(handsFreeOutputFor('Headset (JBL WAVE BEAM Hands-Free AG Audio)', []), null);
});
