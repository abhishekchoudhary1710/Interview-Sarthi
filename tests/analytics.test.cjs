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
test('LinkedIn campaign survives URL sanitisation without unrelated query data',()=>{
  const r=run('https://interviewsarthi.com/prep/?utm_source=linkedin&utm_medium=social&utm_campaign=linkedin_product_growth&utm_content=li-20260929-prep-project&email=private@example.test');
  const c=r.events.find(e=>e[0]==='config')[2];
  assert.equal(c.campaign_source,'linkedin');
  assert.equal(c.campaign_medium,'social');
  assert.equal(c.campaign_name,'linkedin_product_growth');
  assert.equal(c.campaign_content,'li-20260929-prep-project');
  assert.equal(c.page_location,'https://interviewsarthi.com/prep/');
  assert.ok(!JSON.stringify(r.events).includes('private@example.test'));
});
test('arbitrary campaign values and receipt return parameters remain excluded',()=>{
  for(const suffix of ['li-20260929-prep-project&license_key=SECRET','private@example.test','li-20260929-prep-x%20private']) {
    const r=run('https://interviewsarthi.com/prep/?utm_source=linkedin&utm_medium=social&utm_campaign=linkedin_product_growth&utm_content='+suffix);
    assert.equal(r.events.find(e=>e[0]==='config')[2].campaign_source,undefined);
    assert.ok(!JSON.stringify(r.events).includes('SECRET'));
    assert.ok(!JSON.stringify(r.events).includes('private'));
  }
});
test('known UTM and referrer sources; UTM takes precedence',()=>{
  assert.equal(referral(run('https://interviewsarthi.com/?utm_source=chatgpt.com','https://claude.ai/chat/private'))[0][2].ai_source,'chatgpt');
  assert.equal(referral(run('https://interviewsarthi.com/guides/','https://www.perplexity.ai/search/private'))[0][2].ai_source,'perplexity');
});
test('AI assistant UTM reaches GA4 as the session source without a referrer',()=>{
  const config = r => r.events.find(e=>e[0]==='config')[2];
  let c=config(run('https://interviewsarthi.com/live/?utm_source=chatgpt.com&email=private@example.test'));
  assert.equal(c.campaign_source,'chatgpt.com');
  assert.equal(c.campaign_medium,'ai-assistant');
  assert.equal(c.page_location,'https://interviewsarthi.com/live/');
  assert.equal(config(run('https://interviewsarthi.com/?utm_source=perplexity')).campaign_source,'perplexity.ai');
  for(const url of ['https://interviewsarthi.com/?utm_source=chatgpt.com.evil.test',
                    'https://interviewsarthi.com/?utm_source=private@example.test',
                    'https://interviewsarthi.com/thanks.html?utm_source=chatgpt.com&license_key=TEST-SECRET']) {
    c=config(run(url));
    assert.equal(c.campaign_source,undefined);
    assert.equal(c.campaign_medium,undefined);
  }
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
test('checkout still records the selected 1-month product and price',()=>{
  const local=storage(); const r=run('https://interviewsarthi.com/','',storage(),local);
  const anchor={getAttribute:()=> 'https://license.interviewsarthi.com/buy?plan=30d',closest:()=>null};
  r.listeners.click({target:{closest:()=>anchor}});
  assert.equal(JSON.parse(local.getItem('pending_pass')).value,299);
  assert.equal(r.events.find(e=>e[1]==='begin_checkout')[2].items[0].item_name,'1-Month Pass');
});
test('international checkout and its receipt preserve USD amounts without exposing the key',()=>{
  for (const [plan,value] of [['2d',9.99],['30d',29.99]]) {
    const local=storage();
    const checkout=run('https://interviewsarthi.com/live/international.html','',storage(),local);
    const anchor={getAttribute:()=>`https://license.interviewsarthi.com/buy?plan=${plan}&region=intl`,closest:()=>null};
    checkout.listeners.click({target:{closest:()=>anchor}});
    const begin=checkout.events.find(e=>e[1]==='begin_checkout')[2];
    assert.equal(begin.currency,'USD');assert.equal(begin.value,value);
    assert.equal(begin.items[0].price,value);
    const receipt=run('https://interviewsarthi.com/thanks.html?license_key=PRIVATE-KEY','',storage(),local);
    const paid=receipt.events.find(e=>e[1]==='purchase')[2];
    assert.equal(paid.currency,'USD');assert.equal(paid.value,value);
    assert.ok(!JSON.stringify(receipt.events).includes('PRIVATE-KEY'));
  }
});
test('receipt with no known price leaves currency and amount absent',()=>{
  const r=run('https://interviewsarthi.com/thanks.html?license_key=PRIVATE-KEY');
  const paid=r.events.find(e=>e[1]==='purchase')[2];
  assert.equal(paid.currency,undefined);assert.equal(paid.value,undefined);
});
test('local previews suppress analytics and Clarity while retaining receipt handling',()=>{
  for (const host of ['localhost','127.0.0.1','[::1]']) {
    const r=run(`http://${host}/thanks.html?license_key=LOCAL-KEY`);
    assert.ok(!r.scripts.some(s=>s.includes('googletagmanager') || s.includes('clarity.ms')));
    assert.equal(r.events.length,0);
    assert.equal(typeof r.window.sarthiReportPurchase,'function');
    assert.equal(r.location.search,'');
  }
});
test('a Cashfree order reports the purchase once, valued by the plan label, without the key',()=>{
  const local=storage(); const r=run('https://interviewsarthi.com/thanks.html?order_id=order_123','',storage(),local);
  r.window.sarthiReportPurchase('IS-TEST-KEY','1-Month Pass');
  r.window.sarthiReportPurchase('IS-TEST-KEY','1-Month Pass');
  const purchases=r.events.filter(e=>e[1]==='purchase');
  assert.equal(purchases.length,1);
  assert.equal(purchases[0][2].value,299);
  assert.ok(!JSON.stringify(r.events).includes('IS-TEST-KEY'));
});
test('Clarity never loads inside the Prep Sarthi app, but does on its landing page',()=>{
  assert.ok(!run('https://interviewsarthi.com/prep/app/').scripts.some(s=>s.includes('clarity.ms')));
  assert.ok(run('https://interviewsarthi.com/prep/app/').scripts.some(s=>s.includes('googletagmanager')));
  assert.ok(run('https://interviewsarthi.com/prep/').scripts.some(s=>s.includes('clarity.ms')));
});
test('Clarity never records the invite page, where a licence key is typed',()=>{
  assert.ok(!run('https://interviewsarthi.com/live/invite.html?code=K7M2QXA').scripts.some(s=>s.includes('clarity.ms')));
  assert.ok(run('https://interviewsarthi.com/live/').scripts.some(s=>s.includes('clarity.ms')));
});
test('Clarity never records the ATS checker, which prints the CV on screen; GA4 still counts it',()=>{
  for(const page of ['', 'data-analyst.html', '?job=greenhouse:123'])
    assert.ok(!run('https://interviewsarthi.com/apply/ats-resume-checker/'+page).scripts.some(s=>s.includes('clarity.ms')));
  assert.ok(run('https://interviewsarthi.com/apply/ats-resume-checker/').scripts.some(s=>s.includes('googletagmanager')));
  assert.ok(run('https://interviewsarthi.com/apply/guides/ats-resume-format-india.html').scripts.some(s=>s.includes('clarity.ms')));
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
test('a guide tells its top strip apart from its bottom box and from links in the text',()=>{
  const r=run('https://interviewsarthi.com/guides/us-job-interview-tips-indians.html');
  for (const [inside,placement] of [['.app-strip','guide_strip'],['.promo','guide_box'],[null,'page']]) {
    const anchor={getAttribute:()=>'/live/',closest:sel=>(inside && sel.split(',').map(s=>s.trim()).includes(inside))?{}:null};
    r.listeners.click({target:{closest:()=>anchor}});
    assert.equal(r.events.filter(e=>e[1]==='product_click').at(-1)[2].placement,placement);
  }
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
