import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createDiagnostics, measuredRequest } from '../prep/app/diagnostics.js';
import { cleanData } from '../prep/app/diagnostics-data.js';

function fixture() {
  const values = new Map(), calls = [], jobs = [];
  let down = false, time = Date.now();
  const storage = { getItem: k => values.get(k) || null, setItem: (k, v) => values.set(k, v) };
  const options = { storage, now: () => time, schedule: fn => { jobs.push(fn); }, fetcher: async (url, init) => {
    calls.push({ url, body: JSON.parse(init.body), keepalive: init.keepalive });
    if (down) throw new TypeError('Failed to fetch secret-key');
    return new Response('{}', { status: 200 });
  } };
  return { options, calls, values, setDown(v) { down = v; }, advance(v) { time += v; } };
}
test('buy has its own interview end reason in local diagnostics', () => {
  assert.deepEqual(cleanData({ reason: 'buy', elapsed: 12, email: 'private@example.com' }), { reason: 'buy', elapsed: 12 });
});

test('the Bluetooth call-mode fields survive cleanData, device names do not', () => {
  assert.deepEqual(cleanData({ deviceRate: 48000, handsFree: true, sink: 'handsfree', micPreferred: false, label: 'Headset (JBL WAVE BEAM Hands-Free AG Audio)' }),
    { deviceRate: 48000, handsFree: true, sink: 'handsfree', micPreferred: false });
  assert.deepEqual(cleanData({ sink: 'SECRET', handsFree: 'yes' }), {});
});

test('outbox strips private content before persistence and uploads ordered attempt events', async () => {
  const f = fixture(), d = createDiagnostics(f.options); d.begin({ kind: 'demo', email: 'private@example.com' });
  d.event('request_start', { stage: 'report', model: 'gemini-3.6-flash', cv: 'SECRET CV', apiKey: 'SECRET KEY' });
  d.event('socket_closed', { code: 1006, wasConnected: true, reason: 'SECRET close message' });
  d.event('SECRET unapproved event', {});
  assert.doesNotMatch([...f.values.values()].join(''), /SECRET|private@example.com/);
  await d.flush(); await d.flush();
  const events = f.calls.filter(c => c.url.endsWith('/events')).flatMap(c => c.body.events);
  assert.deepEqual(events.map(e => e.name), ['attempt_start', 'request_start', 'socket_closed']);
  assert.equal(new Set(events.map(e => e.id)).size, 3);
  assert.deepEqual(JSON.parse([...f.values.values()][0]), []);
});

test('offline events survive reload, use the same attempt ID, and retry without affecting the caller', async () => {
  const f = fixture(); f.setDown(true);
  const d = createDiagnostics(f.options); const id = d.begin(); d.event('reconnect', { reason: 'reply_timeout' });
  await d.flush();
  assert.ok([...f.values.values()].join('').includes('reply_timeout'));
  f.setDown(false); const restored = createDiagnostics(f.options); await restored.flush();
  assert.equal(f.calls.at(-1).body.id, id);
  assert.equal(f.calls.at(-1).body.events[1].data.reason, 'reply_timeout');
});

test('events arriving during an upload are preserved; multiple attempts remain separate', async () => {
  const f = fixture(); let release;
  const real = f.options.fetcher;
  f.options.fetcher = async (url, init) => {
    if (url.endsWith('/events') && !release) await new Promise(resolve => { release = resolve; });
    return real(url, init);
  };
  const d = createDiagnostics(f.options); const first = d.begin();
  await new Promise(r => setImmediate(r));
  d.event('connected'); release(); await d.flush(); await d.flush();
  const second = d.begin(); await d.flush(); await d.flush();
  assert.notEqual(first, second);
  const batches = f.calls.filter(c => c.url.endsWith('/events'));
  assert.ok(batches.some(c => c.body.id === first && c.body.events.some(e => e.name === 'connected')));
  assert.ok(batches.some(c => c.body.id === second));
});

test('bounded offline queue discloses truncation and expires after 24 hours', async () => {
  const f = fixture(); f.setDown(true); const d = createDiagnostics(f.options); d.begin(); await d.flush();
  for (let i = 0; i < 400; i++) d.event('reconnect', { reason: 'setup_timeout' });
  const saved = JSON.parse([...f.values.values()][0]); assert.equal(saved[0].events.length, 250); assert.ok(saved[0].dropped > 0);
  f.advance(86400001); const old = createDiagnostics(f.options); await old.flush();
  assert.deepEqual(JSON.parse([...f.values.values()][0]), []);
});

test('blocked storage is nonfatal; measured requests preserve response bodies and errors', async () => {
  const f = fixture(); f.options.storage = { getItem() { throw Error('blocked'); }, setItem() { throw Error('blocked'); } };
  const d = createDiagnostics(f.options); d.begin(); d.event('mic_error', { error: 'permission' }); await d.flush();
  const response = await measuredRequest('report', 'gemini-3.6-flash', async () => new Response(JSON.stringify({ candidates: [], usageMetadata: { totalTokenCount: 123 } })));
  assert.equal((await response.json()).usageMetadata.totalTokenCount, 123);
  const failure = new TypeError('Failed to fetch');
  await assert.rejects(measuredRequest('plan', 'gemini-3.1-flash-lite', async () => { throw failure; }), e => e === failure);
  assert.deepEqual(cleanData({ message: 'secret', token: 'secret', reason: 'reply_timeout' }), { reason: 'reply_timeout' });
});
