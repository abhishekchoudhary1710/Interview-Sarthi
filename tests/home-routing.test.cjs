const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const routing = fs.readFileSync(path.join(__dirname, '../assets/home-routing.js'), 'utf8');
const analytics = fs.readFileSync(path.join(__dirname, '../assets/analytics.js'), 'utf8');

function run(url) {
  const location = new URL(url), redirects = [], listeners = {}, window = {};
  location.replace = target => redirects.push(target);
  const context = { window, location, URLSearchParams, addEventListener: (name, fn) => { listeners[name] = fn; } };
  vm.runInNewContext(routing, context);
  return { location, redirects, listeners, window, context };
}

test('legacy Live sections retain their destination and campaign parameters', () => {
  for (const section of ['pricing', 'hidden', 'why', 'features', 'how', 'install', 'faq', 'proof', 'promo', 'tools']) {
    const result = run(`https://interviewsarthi.com/?utm_source=old_link#${section}`);
    assert.deepEqual(result.redirects, [`/live/?utm_source=old_link#${section}`]);
  }
});

test('new homepage sections stay on the product hub', () => {
  for (const section of ['', '#products', '#plans', '#questions', '#see-inside']) {
    const result = run(`https://interviewsarthi.com/${section}`);
    assert.deepEqual(result.redirects, []);
    assert.equal(result.window.sarthiHomeRedirecting, undefined);
  }
});

test('hash changes and existing mobile handoff links still open Live', () => {
  const result = run('https://interviewsarthi.com/');
  result.location.hash = '#install';
  result.listeners.hashchange();
  assert.deepEqual(result.redirects, ['/live/#install']);
  assert.deepEqual(run('https://interviewsarthi.com/?utm_source=self_share&utm_medium=mobile_handoff').redirects,
    ['/live/?utm_source=self_share&utm_medium=mobile_handoff']);
});

test('payment returns reach the receipt before Live fragment routing or analytics', () => {
  for (const query of ['license_key=TEST-ONLY&email=test%40example.invalid', 'order_id=TEST-ORDER']) {
    const result = run(`https://interviewsarthi.com/?${query}#pricing`);
    assert.deepEqual(result.redirects, [`/thanks.html?${query}#pricing`]);
    assert.equal(result.window.sarthiHomeRedirecting, true);
    // Any analytics DOM/network access would throw: receipt navigation must stop it.
    assert.doesNotThrow(() => vm.runInNewContext(analytics, result.context));
    assert.equal(result.window.dataLayer, undefined);
    assert.equal(result.window.clarity, undefined);
  }
});

test('HTTPS upgrade preserves paths and queries and leaves localhost alone', () => {
  assert.deepEqual(run('http://interviewsarthi.com/?order_id=TEST-ORDER#pricing').redirects,
    ['https://interviewsarthi.com/?order_id=TEST-ORDER#pricing']);
  assert.deepEqual(run('http://www.interviewsarthi.com/').redirects, ['https://www.interviewsarthi.com/']);
  assert.deepEqual(run('http://localhost:8938/').redirects, []);
  assert.deepEqual(run('http://interviewsarthi.com.example.invalid/').redirects, []);
});
