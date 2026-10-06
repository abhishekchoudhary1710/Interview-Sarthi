"""Offline browser coverage for demo checkout, report recovery and trial behavior.

All APIs, audio and checkout providers are intercepted. No payment is made.
PREP_REVIEW_DIR selects the destination for desktop and phone review screenshots.
PREP_BROWSER may select an installed Chromium binary.
"""
import json
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('PREP_REVIEW_DIR', ROOT / '.seo-preview' / 'demo-buy'))
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://localhost'
CV = 'I am a backend engineer. I built reliable data processing systems and worked on customer integrations with my team.'
AUDIO = '''export class AudioIO {
  constructor() { window.__audio=this; this.sampleRate=48000; this.micLabel='Test microphone'; this.plays=0; this.clears=0; this.stopped=false; }
  async start() { this.timer=setInterval(()=>this.onChunk?.(new Int16Array(100),.04),100); }
  async stop() { clearInterval(this.timer); this.stopped=true; await new Promise(r=>setTimeout(r,400)); this.closed=true; }
  clear() { this.clears++; } play() { this.plays++; } static async listMics() { return [{id:'test',label:'Test microphone'}]; }
}'''
PLAN = {'role': 'General CV practice', 'level': 'No target seniority', 'uncertainties': [], 'deferred_requirements': [],
        'requirements': [{'label': 'Reliable pipelines', 'category': 'problem_solving', 'priority': 'inferred', 'source_quote': '',
                          'cv_evidence': 'built reliable data processing systems', 'cv_match': 'direct', 'assessment_method': 'interview',
                          'question': 'How did you make a pipeline reliable?', 'followups': [], 'next_assessment': '',
                          'criteria': {'weak': 'Names tools only.', 'adequate': 'Explains one safeguard.', 'strong': 'Explains safeguards and checks.'}}]}
REPORT = {
    'overall_score': 60, 'requirements': [{'id': 'r1', 'status': 'assessed', 'score': 6, 'evidence_turns': [2], 'explanation': 'Named retries and a row-count check.'}],
    'competencies': [{'id': 'problem_solving', 'status': 'assessed', 'score': 6, 'evidence_turns': [2], 'explanation': 'Named retries and a row-count check.'}],
    'verdict': 'A clear example. Add how you checked the result.',
    'strengths': ['You explained a specific safeguard.'],
    'weaknesses': ['Explain the result with a number or a check.'],
    'practice_next': ['Practise explaining how you verified your fix.'],
    'questions': [{'question': 'How did you make a pipeline reliable?', 'score': 6,
                   'answer_gist': 'I added retries and checked row counts after every load.',
                   'what_was_missing': 'A measurable result.',
                   'better_answer': 'I added retries, then checked row counts and failures against the previous week.'}],
    'next_focus': {'group': 'evidence', 'issue': 'Missing a result', 'drill': 'Add a check or a number.'},
}


def gemini(body):
    return {'candidates': [{'content': {'parts': [{'text': json.dumps(body)}]}}]}


class App:
    def __init__(self, p, size=(1366, 768), region='in', answer=True, trial=False, hold_plan=False):
        self.browser = p.chromium.launch(headless=True, executable_path=os.environ.get('PREP_BROWSER'))
        self.context = self.browser.new_context(viewport={'width': size[0], 'height': size[1]})
        self.region, self.answer, self.trial, self.hold_plan = region, answer, trial, hold_plan
        self.paid, self.status, self.hold_report = False, 'pending', True
        self.held, self.plans, self.calls, self.errors, self.dialogs, self.sockets = [], [], [], [], [], []
        self.mic_chunks = 0
        self.cors = {'access-control-allow-origin': BASE, 'access-control-allow-headers': 'content-type'}
        self.context.route('**/*', self.route)
        self.context.route_web_socket(re.compile(r'wss://generativelanguage\.googleapis\.com/.*'), self.live)
        self.context.add_init_script('''window.__events=[]; window.gtag=(kind,name,params)=>{
          if(kind==='event') window.__events.push({name,params});
        }; window.__PREP_TEST={retrySeconds:[20]};
        const NativeSocket=window.WebSocket;
        window.WebSocket=class extends NativeSocket {
          close(...args) { window.__socketClosed=true; return super.close(...args); }
        };''')
        self.page = self.context.new_page()
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('dialog', self.dialog)
        if trial:
            self.page.add_init_script("localStorage.setItem('ps_gemini_key','test-key')")
        self.page.goto(BASE + '/prep/app/', wait_until='networkidle')
        self.page.wait_for_function("document.getElementById('entitle').textContent !== '…'")

    def dialog(self, d):
        self.dialogs.append(d.message)
        d.accept()

    def server_entitlement(self, signed=True):
        return {
            'account': {'email': 'review@example.com', 'name': 'Reviewer'} if signed else None,
            'pass': {'valid': True, 'seconds_left': 2592000, 'expires_at': '2026-11-05T12:00:00Z'} if self.paid else None,
            'trial': {'seconds_left': 302, 'total': 1200} if self.trial else None,
        }

    def route(self, r):
        url = urlsplit(r.request.url)
        if url.hostname == 'localhost':
            path = unquote(url.path).lstrip('/')
            if path.endswith('/'): path += 'index.html'
            if path == 'assets/analytics.js':
                r.fulfill(body='', content_type='text/javascript'); return
            if path == 'prep/app/audio.js':
                r.fulfill(body=AUDIO, content_type='text/javascript'); return
            file = (ROOT / path).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file(): r.abort(); return
            r.fulfill(body=file.read_bytes(), content_type=mimetypes.guess_type(file)[0] or 'application/octet-stream'); return
        if url.hostname.endswith('workers.dev'):
            if r.request.method == 'OPTIONS':
                r.fulfill(status=204, headers=self.cors); return
            body = r.request.post_data_json or {}
            self.calls.append((url.path, body))
            result = {}
            if url.path == '/mock/config':
                result = {'demo': {'seconds': 420}, 'plans': {'m': {'amount': 99, 'days': 30, 'label': '30-Day Pass', 'usd': 999}}, 'region': self.region}
            elif url.path == '/mock/status': result = self.server_entitlement(bool(body.get('session')))
            elif url.path == '/mock/auth/google': result = {**self.server_entitlement(), 'session': 'test-session'}
            elif url.path == '/mock/demo/start': result = {'ok': True, 'demo': 'a' * 24, 'token': 'fake-token', 'seconds': 420}
            elif url.path == '/mock/trial/tick': result = {'seconds_left': 301}
            elif url.path == '/mock/demo/generate' and body.get('stage') == 'plan':
                if self.hold_plan: self.plans.append(r); return
                result = gemini(PLAN)
            elif url.path == '/mock/demo/generate':
                if self.hold_report: self.held.append(r); return
                result = gemini(REPORT)
            elif url.path == '/mock/buy':
                result = {'order_id': 'review-order', 'amount': 9.99 if self.region != 'in' else 99,
                          'currency': 'USD' if self.region != 'in' else 'INR',
                          'gateway': 'dodo' if self.region != 'in' else 'cashfree',
                          'mode': 'sandbox', 'payment_session_id': 'fake-payment-session'}
                if self.region != 'in': result['checkout_url'] = 'https://checkout.dodo.test/session'
            elif url.path == '/mock/order':
                result = {**self.server_entitlement(), 'status': self.status, 'plan': '30-Day Pass'}
            elif url.path == '/mock/invite': result = {'invite': {'code': 'ABC1234'}}
            r.fulfill(status=200, json=result, headers=self.cors); return
        if url.hostname == 'sdk.cashfree.com':
            r.fulfill(body='window.Cashfree=()=>({checkout:opts=>{sessionStorage.setItem("review_cashfree",JSON.stringify(opts));location.href="https://sandbox.cashfree.test/session";}})', content_type='text/javascript'); return
        if url.hostname in ('sandbox.cashfree.test', 'checkout.dodo.test'):
            r.fulfill(body='<h1>Simulated checkout</h1><p>No real payment was made.</p>', content_type='text/html'); return
        if url.hostname == 'generativelanguage.googleapis.com':
            if '/models?' in url.path + '?' + url.query:
                r.fulfill(json={'models': []}, headers=self.cors); return
            body = r.request.post_data_json or {}
            instructions = body.get('systemInstruction', {}).get('parts', [{}])[0].get('text', '')
            if instructions.startswith('Design a job-specific interview assessment plan'):
                r.fulfill(json=gemini(PLAN), headers=self.cors); return
            if self.hold_report: self.held.append(r); return
            r.fulfill(json=gemini(REPORT), headers=self.cors); return
        r.abort()

    def live(self, ws):
        self.sockets.append(ws)

        def message(raw):
            m = json.loads(raw)
            if 'setup' in m: ws.send(json.dumps({'setupComplete': {}}))
            elif 'clientContent' in m:
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'How did you make a pipeline reliable?'}, 'turnComplete': True}}))
                if self.answer:
                    ws.send(json.dumps({'serverContent': {'inputTranscription': {'text': 'I added retries and checked row counts after every load.'}}}))
                    ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'How did you check it worked?'}, 'turnComplete': True}}))
                self.emit_audio()
            elif 'realtimeInput' in m: self.mic_chunks += 1
        ws.on_message(message)

    def emit_audio(self):
        self.sockets[-1].send(json.dumps({'serverContent': {'modelTurn': {'parts': [{'inlineData': {'mimeType': 'audio/pcm;rate=24000', 'data': 'AAAAAA=='}}]}, 'turnComplete': True}}))

    def start(self):
        self.page.locator('#cv').fill(CV)
        self.page.locator('#practice-focus').select_option('general_cv')
        self.page.locator('#to-key').click()
        expect(self.page.locator('#line')).to_contain_text('check it worked' if self.answer else 'pipeline reliable', timeout=15000)
        self.page.wait_for_function('window.__audio.plays > 0')

    def buy(self, where='demo_call'):
        selector = '#demo-call-buy' if where == 'demo_call' else '#demo-exit-buy'
        result = self.page.locator(selector).evaluate('''button=>{
          const t=performance.now(); button.click(); return {ms:performance.now()-t,
            checkout:document.getElementById('s-pass').classList.contains('on') && document.getElementById('checkout').style.display==='block',
            saved:!!localStorage.getItem('ps_pending_report'), disabled:document.getElementById('pay').disabled,
            stopped:window.__audio.stopped};
        }''')
        assert result['ms'] < 1000 and result['checkout'], result
        assert result['stopped'] and result['disabled'], result
        assert result['saved'] == self.answer, result
        assert self.page.evaluate("localStorage.getItem('ps_demo_used')") == '1'
        self.page.wait_for_function("window.prepApp.state().phase === 'idle'")
        assert self.page.evaluate('window.__socketClosed'), 'the live socket must close before Pay is enabled'
        expect(self.page.locator('#pay')).to_be_enabled()
        return result['ms']

    def release_report(self):
        self.page.wait_for_function("localStorage.getItem('ps_pending_report') !== null")
        for _ in range(50):
            if self.held: break
            self.page.wait_for_timeout(50)
        assert self.held, ('no report request', [(path, body.get('stage')) for path, body in self.calls], self.errors)
        self.hold_report = False
        for r in self.held: r.fulfill(json=gemini(REPORT), headers=self.cors)
        self.held.clear()
        self.page.wait_for_function('window.__lastReport && window.__lastReport.report')

    def pause_report(self):
        # Both report models are busy, so the saved job remains pending without a held network route.
        for _ in range(2):
            for _ in range(50):
                if self.held: break
                self.page.wait_for_timeout(50)
            assert self.held
            self.held.pop().fulfill(status=503, json={'error': {'message': 'Service busy'}}, headers=self.cors)
        self.page.wait_for_function("document.getElementById('report-status').textContent.includes('Trying again in')")

    def pay_and_return(self, status, where):
        self.page.locator('#testlogin-email').fill('review@example.com')
        self.page.locator('#testlogin-go').click()
        expect(self.page.locator('#pass-pay')).to_be_visible()
        if self.region == 'in': self.page.locator('#phone').fill('9876543210')
        else: expect(self.page.locator('#phone')).to_be_hidden()
        self.page.locator('#pay').click()
        self.page.wait_for_url('**/*.test/session')
        self.status, self.paid = status, status == 'paid'
        self.page.goto(BASE + '/prep/app/?order_id=review-order' + ('&payment_id=review-payment' if self.region != 'in' else ''), wait_until='networkidle')
        expect(self.page.locator('#s-report')).to_be_visible(timeout=15000)
        expect(self.page.locator('#report')).to_contain_text(REPORT['verdict'], timeout=15000)
        if status == 'paid':
            expect(self.page.locator('#report-pass-active')).to_be_visible()
            expect(self.page.locator('#report-offer')).to_be_hidden()
            assert self.events('mock_offer_paid') == [{'where': where}]
            assert len(self.events('purchase')) == 1
        else:
            expect(self.page.locator('#report-offer')).to_be_visible()
            expect(self.page.locator('#report-payment-note')).to_contain_text('did not go through')
            assert not self.events('purchase') and not self.events('mock_offer_paid')

    def events(self, name):
        return self.page.evaluate('(name)=>window.__events.filter(e=>e.name===name).map(e=>e.params)', name)

    def shot(self, name, width):
        self.page.screenshot(path=str(OUT / f'{name}-{width}.png'), full_page=False, animations='disabled')
        if name.startswith(('paid-return', 'failed-return')):
            self.page.screenshot(path=str(OUT / f'{name}-full-{width}.png'), full_page=True, animations='disabled')

    def close(self):
        assert not self.errors, self.errors
        self.context.unroute_all(behavior='ignoreErrors')
        self.browser.close()


def visible_call(page, width, height):
    for selector in ('#demo-call-offer', '#demo-call-buy', '#caption', '#youline', '#clock', '#end'):
        box = page.locator(selector).bounding_box()
        assert box and box['x'] >= 0 and box['y'] >= 0 and box['x'] + box['width'] <= width + 1 and box['y'] + box['height'] <= height + 1, (selector, box, width, height)
    call, offer = page.locator('.call.big').bounding_box(), page.locator('#demo-call-offer').bounding_box()
    if width > 700: assert offer['x'] >= call['x'] + call['width'], (call, offer)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def main():
    timings = []
    with sync_playwright() as p:
        for width, height in ((1366, 768), (390, 844)):
            app = App(p, (width, height))
            app.start()
            visible_call(app.page, width, height)
            assert app.events('mock_offer_shown') == [{'where': 'demo_call'}]
            app.shot('call', width)
            app.page.evaluate('window.__audio.onMicMuted(true)')
            expect(app.page.locator('#micfix')).to_be_visible()
            visible_call(app.page, width, height)
            mic = app.page.locator('#micfix').bounding_box()
            assert mic['y'] + mic['height'] <= height, mic
            app.page.evaluate("document.getElementById('micfix').style.display='none'")
            app.page.locator('#end').click()
            expect(app.page.locator('#demo-exit-card')).to_be_visible()
            assert not app.dialogs
            plays, chunks = app.page.evaluate('window.__audio.plays'), app.mic_chunks
            app.emit_audio()
            app.page.wait_for_timeout(250)
            assert app.page.evaluate('window.__audio.plays') == plays
            assert app.mic_chunks == chunks
            app.shot('end-card', width)
            app.page.locator('#demo-exit-keep').click()
            app.emit_audio()
            app.page.wait_for_function('(plays)=>window.__audio.plays>plays', arg=plays)
            app.page.wait_for_timeout(250)
            assert app.mic_chunks > chunks, 'Keep going restores microphone input'
            where = 'demo_exit' if width == 390 else 'demo_call'
            if where == 'demo_exit': app.page.locator('#end').click()
            timings.append(app.buy(where))
            app.shot('checkout', width)
            app.release_report()
            expect(app.page.locator('#s-pass')).to_be_visible()
            expect(app.page.locator('#report-offer')).to_be_hidden()
            assert not [x for x in app.events('mock_offer_shown') if x['where'] == 'demo_report']
            app.page.locator('#pass-back').click()
            expect(app.page.locator('#s-report')).to_be_visible()
            expect(app.page.locator('#report-offer')).to_be_visible()
            assert {'choice': 'keep'} in app.events('mock_exit_card')
            if where == 'demo_exit': assert {'choice': 'buy'} in app.events('mock_exit_card')
            app.close()

            for status in ('paid', 'failed'):
                app = App(p, (width, height))
                app.start()
                where = 'demo_exit' if width == 390 else 'demo_call'
                if where == 'demo_exit': app.page.locator('#end').click()
                expect(app.page.locator('#demo-call-price')).to_have_text('Rs 99')
                app.buy(where)
                app.release_report()
                app.pay_and_return(status, where)
                app.shot(status + '-return', width)
                if status == 'paid':
                    app.page.locator('#report-key-setup').click()
                    expect(app.page.locator('#key-lede')).to_contain_text('Your pass is active. One last step')
                app.close()

        # Buy before the first answer quietly skips report generation.
        app = App(p, answer=False)
        app.start(); app.buy()
        assert not [c for c in app.calls if c[0] == '/mock/demo/generate' and c[1].get('stage') == 'report']
        expect(app.page.locator('#s-pass')).to_be_visible()
        app.close()

        # A slow plan cannot delay saved answers or unlocking Pay.
        app = App(p, hold_plan=True)
        app.start(); app.buy()
        assert app.page.evaluate("JSON.parse(localStorage.getItem('ps_pending_report')).turns.some(t=>t.who==='candidate')")
        expect(app.page.locator('#pay')).to_be_enabled()
        for r in app.plans: r.fulfill(json=gemini(PLAN), headers=app.cors)
        app.hold_plan = False
        app.release_report(); app.close()

        # Checkout interrupts an unfinished report: recovery and confirmation share the screen on both returns.
        for status in ('paid', 'failed'):
            app = App(p)
            app.start(); app.buy()
            app.pause_report()
            app.page.locator('#testlogin-go').click()
            expect(app.page.locator('#pass-pay')).to_be_visible()
            app.page.locator('#phone').fill('9876543210')
            app.page.locator('#pay').click()
            app.page.wait_for_url('**/*.test/session')
            app.hold_report = False; app.held.clear(); app.status = status; app.paid = status == 'paid'
            app.page.goto(BASE + '/prep/app/?order_id=review-order', wait_until='networkidle')
            expect(app.page.locator('#report')).to_contain_text(REPORT['verdict'], timeout=15000)
            expect(app.page.locator('#s-report')).to_be_visible()
            if status == 'paid':
                expect(app.page.locator('#report-pass-active')).to_be_visible()
                assert app.page.evaluate('window.prepApp.state().pass'), 'the report must preserve the purchased entitlement'
            else: expect(app.page.locator('#report-offer')).to_be_visible()
            app.close()

        # Closing checkout without a return URL still restores the report and the offer.
        app = App(p)
        app.start(); app.buy(); app.release_report()
        app.page.locator('#testlogin-go').click()
        expect(app.page.locator('#pass-pay')).to_be_visible()
        app.page.locator('#phone').fill('9876543210'); app.page.locator('#pay').click()
        app.page.wait_for_url('**/*.test/session')
        app.page.goto(BASE + '/prep/app/', wait_until='networkidle')
        expect(app.page.locator('#s-report')).to_be_visible(timeout=15000)
        expect(app.page.locator('#report-offer')).to_be_visible()
        expect(app.page.locator('#report-payment-note')).to_contain_text('has not been confirmed')
        app.close()

        # Trial users retain their mid-call offer, running-call lock and browser confirmation.
        app = App(p, trial=True)
        app.start()
        expect(app.page.locator('#live-offer')).to_be_visible(timeout=10000)
        expect(app.page.locator('#demo-call-offer')).to_be_hidden()
        app.page.locator('#live-offer-go').click()
        expect(app.page.locator('#buy-cta')).to_be_disabled()
        expect(app.page.locator('#pay')).to_be_disabled()
        app.page.locator('#pass-running-back').click()
        expect(app.page.locator('#livetag')).to_have_class('live on')
        app.page.locator('#end').click()
        assert len(app.dialogs) == 1
        app.release_report()
        expect(app.page.locator('#report-offer')).to_be_visible()
        app.close()

    result = {'result': 'passed', 'checkout_open_ms': timings, 'screenshots': str(OUT), 'payments': 'simulated'}
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
