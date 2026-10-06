import { test } from 'node:test';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { reportPaidOrder } from '../prep/app/purchase-analytics.js';
function storage() { const values=new Map();return {getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v)}; }
test('confirmed payment keeps actual currency/value, hashes transaction and deduplicates reloads',async()=>{
  const events=[], store=storage(), record=(...x)=>events.push(x);
  const pending={order_id:'ORDER-PRIVATE',amount:2.99,currency:'USD'};
  await reportPaidOrder(pending,{status:'paid',plan:'month'},record,store,webcrypto);
  await reportPaidOrder(pending,{status:'paid',plan:'month'},record,store,webcrypto);
  assert.equal(events.length,1);
  assert.equal(events[0][1].value,2.99);assert.equal(events[0][1].currency,'USD');
  assert.match(events[0][1].transaction_id,/^prep_[a-f0-9]{64}$/);
  assert.ok(!JSON.stringify(events).includes('ORDER-PRIVATE'));
});
test('failed/pending orders never count, unknown amounts stay absent, storage failure still has stable transaction',async()=>{
  const events=[], record=(...x)=>events.push(x), store={getItem:()=>{throw Error()},setItem:()=>{throw Error()}};
  for(const status of ['pending','failed'])await reportPaidOrder({order_id:'x'},{status},record,store,webcrypto);
  assert.equal(events.length,0);
  await reportPaidOrder({order_id:'x'},{status:'paid'},record,store,webcrypto);
  await reportPaidOrder({order_id:'x'},{status:'paid'},record,store,webcrypto);
  assert.equal(events[0][1].value,undefined);assert.equal(events[0][1].currency,undefined);
  assert.equal(events[0][1].transaction_id,events[1][1].transaction_id);
});
test('demo purchases retain their offer source and count once alongside purchase',async()=>{
  for (const where of ['demo_call','demo_exit']) {
    const events=[], store=storage(), record=(...args)=>events.push(args);
    const pending={order_id:`order-${where}`,where,amount:99,currency:'INR'};
    await reportPaidOrder(pending,{status:'paid',plan:'month'},record,store,webcrypto);
    await reportPaidOrder(pending,{status:'paid',plan:'month'},record,store,webcrypto);
    assert.deepEqual(events.map(([name])=>name),['purchase','mock_offer_paid']);
    assert.deepEqual(events[1][1],{where});
  }
});
test('ordinary purchases and unrecognized offer sources do not count as demo conversions',async()=>{
  for (const where of [undefined,'report','interview','unexpected']) {
    const events=[];
    await reportPaidOrder({order_id:'ordinary',where},{status:'paid'},(...args)=>events.push(args),storage(),webcrypto);
    assert.deepEqual(events.map(([name])=>name),['purchase']);
  }
});
