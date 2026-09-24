const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/analytics.js'), 'utf8');
function storage() { const m = new Map(); return {getItem:k=>m.get(k)||null, setItem:(k,v)=>m.set(k,v), removeItem:k=>m.delete(k)}; }
function run(url, referrer='', session=storage(), local=storage(), disabled=false) {
  const location = new URL(url), scripts = [], listeners = {};
  const window = {};
  const document = {
    referrer, head:{appendChild:s=>scripts.push(s.src)}, createElement:()=>({}),
    getElementsByTagName:()=>[{parentNode:{insertBefore:s=>scripts.push(s.src)}}],
    addEventListener:(name,fn)=>{listeners[name]=fn;}
  };
  const context = {window,document,location,URL,URLSearchParams,sessionStorage:session,localStorage:local,
    history:{replaceState:(_,__,value)=>{location.href = new URL(value, location).href;}},Date};
  vm.runInNewContext(disabled ? source.replace('G-CCFHWPJD9K','G-XXXX').replace('yb9mq7tzkq','XXXX') : source, context);
  return {get events(){return window.dataLayer.map(x=>Array.from(x));},scripts,location,listeners,window};
}
const referral = r => r.events.filter(e=>e[0]==='event' && e[1]==='ai_referral_visit');
test('known UTM and referrer sources; UTM takes precedence',()=>{
  assert.equal(referral(run('https://interviewsarthi.com/?utm_source=chatgpt.com','https://claude.ai/chat/private'))[0][2].ai_source,'chatgpt');
  assert.equal(referral(run('https://interviewsarthi.com/guides/','https://www.perplexity.ai/search/private'))[0][2].ai_source,'perplexity');
});
test('reject spoof hosts and ordinary Google traffic',()=>{
  for(const host of ['https://chatgpt.com.evil.test/','https://evilclaude.ai/','https://google.com/search?q=private']) {
    assert.equal(referral(run('https://interviewsarthi.com/',host)).length,0);
  }
});
test('one AI event per source and session; query and fragment excluded',()=>{
  const session=storage();
  const first=run('https://interviewsarthi.com/guides/?utm_source=claude&email=private#secret','',session);
  assert.equal(referral(first)[0][2].landing_page,'/guides/');
  assert.equal(referral(run('https://interviewsarthi.com/?utm_source=claude','',session)).length,0);
  assert.ok(!JSON.stringify(first.events).includes('private'));
});
test('receipt keeps purchase signal and excludes key, email and recording',()=>{
  const local=storage();
  const result=run('https://interviewsarthi.com/thanks.html?license_key=TEST-SECRET&email=private@example.test','',storage(),local);
  assert.equal(result.location.search,'');
  assert.ok(!result.scripts.some(s=>s.includes('clarity.ms')));
  assert.ok(!JSON.stringify(result.events).includes('TEST-SECRET'));
  assert.ok(!JSON.stringify(result.events).includes('private@example.test'));
  assert.equal(result.events.filter(e=>e[1]==='purchase').length,1);
  assert.equal(run('https://interviewsarthi.com/thanks.html?license_key=TEST-SECRET','',storage(),local).events.filter(e=>e[1]==='purchase').length,0);
});
test('disabled analytics and denied storage do not break navigation',()=>{
  assert.equal(referral(run('https://interviewsarthi.com/?utm_source=gemini','',storage(),storage(),true)).length,0);
  const denied={getItem:()=>{throw Error('denied')},setItem:()=>{throw Error('denied')}};
  assert.equal(referral(run('https://interviewsarthi.com/?utm_source=copilot','',denied)).length,1);
});
test('checkout still records the selected 7-day product and price',()=>{
  const local=storage(); const r=run('https://interviewsarthi.com/','',storage(),local);
  const anchor={getAttribute:()=> 'https://license.interviewsarthi.com/buy?plan=7d',closest:()=>null};
  r.listeners.click({target:{closest:()=>anchor}});
  assert.equal(JSON.parse(local.getItem('pending_pass')).value,399);
  assert.equal(r.events.find(e=>e[1]==='begin_checkout')[2].items[0].item_name,'7-Day Pass');
});
test('a Cashfree order reports the purchase once, valued by the plan label, without the key',()=>{
  const local=storage(); const r=run('https://interviewsarthi.com/thanks.html?order_id=order_123','',storage(),local);
  r.window.sarthiReportPurchase('IS-TEST-KEY','7-Day Pass');
  r.window.sarthiReportPurchase('IS-TEST-KEY','7-Day Pass');
  const purchases=r.events.filter(e=>e[1]==='purchase');
  assert.equal(purchases.length,1);
  assert.equal(purchases[0][2].value,399);
  assert.ok(!JSON.stringify(r.events).includes('IS-TEST-KEY'));
});
test('Clarity never loads inside the Prep Sarthi app, but does on its landing page',()=>{
  assert.ok(!run('https://interviewsarthi.com/prep/app/').scripts.some(s=>s.includes('clarity.ms')));
  assert.ok(run('https://interviewsarthi.com/prep/app/').scripts.some(s=>s.includes('googletagmanager')));
  assert.ok(run('https://interviewsarthi.com/prep/').scripts.some(s=>s.includes('clarity.ms')));
});
test('the old /mock/app path is still excluded from Clarity while its stub redirects',()=>{
  assert.ok(!run('https://interviewsarthi.com/mock/app/').scripts.some(s=>s.includes('clarity.ms')));
});
test('product choices are measured across guides without personal URL parameters',()=>{
  const r=run('https://interviewsarthi.com/guides/first-job-interview-guide-freshers.html');
  for (const [href,product,kind] of [
    ['../prep/','prep','product_page'],
    ['/prep/app/?email=private%40example.test&key=SECRET','prep','application'],
    ['https://apply.interviewsarthi.com/jobs?email=private','apply','application'],
    ['/live/','live','product_page'],
    ['/apply/','apply','product_page']
  ]) {
    const anchor={getAttribute:()=>href,closest:()=>null};
    r.listeners.click({target:{closest:()=>anchor}});
    const event=r.events.filter(e=>e[1]==='product_click').at(-1);
    assert.equal(event[2].product,product);assert.equal(event[2].destination_kind,kind);
  }
  assert.equal(r.events.filter(e=>e[1]==='product_click').length,5);
  assert.ok(!JSON.stringify(r.events).includes('SECRET'));
  assert.ok(!JSON.stringify(r.events).includes('private'));
});
test('unrelated and spoof product URLs are not tracked as product choices',()=>{
  const r=run('https://interviewsarthi.com/');
  for(const href of ['https://apply.interviewsarthi.com.evil.test/','https://other.test/prep/','/guides/','mailto:support@interviewsarthi.com']) {
    r.listeners.click({target:{closest:()=>({getAttribute:()=>href,closest:()=>null})}});
  }
  assert.equal(r.events.filter(e=>e[1]==='product_click').length,0);
});
test('receipt and private Prep app screens do not emit product-choice events',()=>{
  for(const url of ['https://interviewsarthi.com/thanks.html','https://interviewsarthi.com/prep/app/']) {
    const r=run(url);r.listeners.click({target:{closest:()=>({getAttribute:()=>'/live/',closest:()=>null})}});
    assert.equal(r.events.filter(e=>e[1]==='product_click').length,0);
  }
});
