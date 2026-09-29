"""Offline browser integration tests for the real Prep app and progress UI.
No payments, Gemini calls, or account writes leave this process.
Run with a Python environment containing playwright; PREP_BROWSER can override Chromium.
"""
import copy
import json
import mimetypes
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.seo-preview'
OUT.mkdir(exist_ok=True)
NOW = datetime.now(timezone.utc)
iso = lambda d: d.isoformat().replace('+00:00', 'Z')
PERIOD = {'start': iso(NOW-timedelta(days=17)), 'end': iso(NOW+timedelta(days=13)), 'current': True}
GROUPS = ['communication','ownership','role_knowledge','problem_solving','quality_risk','collaboration','judgment_learning','leadership']

def interview(n, score):
    at = iso(NOW-timedelta(days=16-n*2))
    ident = f'iv-ui-{n}'
    summary = dict(id=ident,kind='interview',sv=1,at=at,minutes=15,language='English',model='gemini-main',writer='main',rubric='v1',mode='job_description',role='Backend engineer',level='Mid-level',track='job_description|backend engineer|mid-level',score=score,coverage={'scored':6,'total':8},groups={g:{'score':(score-i*2)/10,'n':1,'limited':False} for i,g in enumerate(GROUPS[:6])},planned={g:1 for g in GROUPS},delivery={'wpm':140+n,'pause':3.5-n*.2,'fillers_pm':3-n*.3,'answer_seconds':70,'talk_share':.65},focus={'group':'ownership','issue':'Make your own contribution clear.','drill':'Describe one decision you made and explain why it mattered.'},focus_check={'status':'improved','note':'Your latest answer named a decision and its outcome.'},questions=[{'q':'Walk me through your project.','score':score/10}])
    body = dict(id=ident,at=at,elapsed=900,language='English',model='gemini-main',rubric='v1',metrics={'avgResponseDelay':2,'avgWpm':140,'fillersTotal':3,'longestPause':2},transcript=[{'who':'interviewer','text':'Walk me through your project.'},{'who':'candidate','text':'I designed the retry queue. <img src=x onerror="window.uiInjected=true"> We cut failures by half.'}],report={'overall_score':score,'verdict':'Your answers are getting more specific.','strengths':['Clear explanation'],'weaknesses':['Explain the trade-off'],'questions':[{'question':'Walk me through your project.','score':score/10,'answer_gist':'I designed a queue.','what_was_missing':'The trade-off.','better_answer':'I chose retries with backoff.','answer_turns':[2]}],'competencies':[],'requirements':[{'id':'r1','label':'Backend APIs','category':'role_knowledge','priority':'essential','weight':2,'score':6,'status':'assessed','outcome':'Partially demonstrated','evidence_turns':[2],'explanation':'Explained the queue.'}],'delivery':{},'practice_next':['Explain your decision.'],'next_focus':summary['focus'],'focus_check':{'status':'improved','note':'You named your decision.','evidence_turns':[2]}},changes={'comparable':True,'score':{'since_last':4,'since_first':18,'same_role_as_last':True,'same_role_as_first':True},'groups':[]})
    return {'id':ident,'kind':'interview','at':at,'summary':summary,'body':body}

class Backend:
    def __init__(self):
        self.items = [interview(i,s) for i,s in enumerate([51,55,63,60,69,72,77])]
        self.enabled = True
        self.signed_in = True
        self.live = True
        self.offline = False
        self.save_attempts = 0
        self.writes = []
        self.fail_delete = False
        # Match analysisId's period tag, populated below after importing the production module.
        self.analysis = dict(enough=True,scope='latest',window={'from':PERIOD['start'],'to':PERIOD['end']},based_on=[i['id'] for i in self.items],model='gemini-main',summary='Your explanations are clearer. The next step is showing your own decisions.',patterns=[{'type':'recurring_weakness','group':'ownership','group_label':'Ownership','title':'Show the decision behind the work.','detail':'Your project answers name tools, but sometimes omit your personal trade-off.','evidence':[{'interview_id':'iv-ui-0','turn':2},{'interview_id':'iv-ui-6','turn':2}],'interviews':2,'drill':'Compare two approaches in one sentence.'}],strong_answers=[{'interview_id':'iv-ui-6','turn':2,'why':'A concrete contribution.'}],next_priorities=['Explain your decision.','Name the outcome.'],facts={})
        self.analysis_id = None
        self.redrill = {'id':'rd-ui','kind':'redrill','at':iso(NOW),'summary':{'interview_id':'iv-ui-0','question_index':0,'question':'Walk me through your project.','score_before':5.1,'score_after':8,'change':2.9,'verdict':'A more specific answer.','improved':['You explained the decision.'],'still_missing':['Quantify the outcome if you know it.']},'body':{'source':{'before':{'text':'We built retries.','better':'I chose retries with backoff.'}},'after':{'text':'I designed retry backoff after comparing two options.'}}}
        self.items.append(self.redrill)
    def prefs(self):
        return {'enabled':self.enabled,'consent_version':1,'current_consent_version':1,'retention_days':365,'pass':{'live':self.live,'expires_at':PERIOD['end']}}
    def route(self, route):
        u=urlsplit(route.request.url)
        if u.hostname=='localhost':
            path=unquote(u.path).lstrip('/') or 'index.html'
            if path.endswith('/'): path+='index.html'
            f=(ROOT/path).resolve()
            if f.is_relative_to(ROOT) and f.is_file(): route.fulfill(body=f.read_bytes(),content_type=mimetypes.guess_type(str(f))[0] or 'application/octet-stream')
            else: route.fulfill(status=404,body='Not found')
            return
        if not u.path.startswith('/mock/'):
            route.abort(); return
        body=route.request.post_data_json or {}
        def reply(d,status=200): route.fulfill(status=status,json=d)
        path=u.path
        if path=='/mock/config': reply({'google_client_id':'','plans':{'m':{'amount':99,'days':30,'usd':999,'label':'30-Day Pass'}},'region':'in','demo':{'seconds':420}})
        elif path=='/mock/status': reply({'now':iso(NOW),'account':{'name':'Riya','email':'ui@example.invalid'} if self.signed_in else None,'pass':{'valid':self.live and self.signed_in,'seconds_left':100000,'expires_at':PERIOD['end']},'trial':None})
        elif path=='/mock/history/prefs':
            if 'enabled' in body: self.enabled=body['enabled']; self.writes.append(('prefs',self.enabled))
            reply(self.prefs())
        elif path=='/mock/history/list':
            if self.offline: route.abort(); return
            items=copy.deepcopy(self.items)
            if self.analysis_id: items.append({'id':self.analysis_id,'kind':'analysis','at':iso(NOW),'summary':self.analysis,'body':None})
            items.sort(key=lambda i:i['at'],reverse=True)
            reply({'items':items,'periods':[PERIOD],'prefs':self.prefs(),'more':False})
        elif path=='/mock/history/get': reply({'items':[i for i in self.items if i['id'] in body['ids']]})
        elif path=='/mock/history/delete':
            if self.fail_delete: reply({'error':'Could not delete. Please try again.'},500); return
            self.writes.append(('delete',body))
            self.items=[] if body.get('all') else [i for i in self.items if i['id']!=body['id']]
            if body.get('all'): self.analysis_id=None
            reply({'deleted':1})
        elif path=='/mock/history/save':
            self.save_attempts+=1
            if self.offline: reply({'error':'Temporarily unavailable'},503); return
            item=body['item']; self.items=[i for i in self.items if i['id']!=item['id']]+[item]; reply({'saved':True})
        else: reply({})

with sync_playwright() as pw:
    opts={'headless':True}
    if os.environ.get('PREP_BROWSER'): opts['executable_path']=os.environ['PREP_BROWSER']
    browser=pw.chromium.launch(**opts)
    backend=Backend()
    ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    ctx.route('**/*',backend.route)
    ctx.add_init_script("localStorage.setItem('ps_session','ui-fixture');")
    page=ctx.new_page(); page.set_default_timeout(8000); errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://localhost/prep/app/',wait_until='networkidle')
    backend.analysis_id=page.evaluate("async p => (await import('/prep/app/insights.js')).analysisId(p,'latest')",PERIOD)
    page.click('#open-progress')
    expect(page.locator('.pg-chart')).to_be_visible()
    expect(page.get_by_text('Make your own contribution clear.',exact=True)).to_be_visible()
    expect(page.locator('#pg-title')).to_be_focused()
    assert page.locator('#pg-title').evaluate("el => getComputedStyle(el).outlineStyle") == 'none'
    page.keyboard.press('Tab')
    expect(page.locator('#s-progress [data-pg="settings"]')).to_be_focused()
    assert page.locator('#s-progress [data-pg="settings"]').evaluate("el => getComputedStyle(el).outlineStyle") == 'solid'
    page.locator('#pg-title').focus()
    assert not backend.writes, 'Opening progress must not opt in or write data'
    page.screenshot(path=str(OUT/'prep-progress-desktop.png'),full_page=True)
    for width in [390,320,768,1440]:
        page.set_viewport_size({'width':width,'height':900})
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+1'), f'Overflow at {width}'
        if width==390: page.screenshot(path=str(OUT/'prep-progress-mobile.png'),full_page=True)
    # A practiced day selects only that day's interviews.
    page.locator('.pg-day.practised').first.click()
    expect(page.locator('.pg-history-row')).to_have_count(1)
    page.click('[data-pg="clear-day"]')
    # Select a role before comparing: unrelated roles stay out of the score line.
    other=interview(7,20)
    other['summary'].update(role='Product manager',track='job_description|product manager|senior',level='Senior')
    backend.items.append(other)
    page.click('#open-progress'); page.click('[data-tab="overview"]')
    page.select_option('#pg-track','job_description|product manager|senior')
    expect(page.locator('.pg-chart')).to_have_count(0)
    page.select_option('#pg-track','job_description|backend engineer|mid-level')
    expect(page.locator('.pg-chart')).to_be_visible()
    backend.items.remove(other)
    page.click('[data-tab="reviews"]')
    page.screenshot(path=str(OUT/'prep-progress-reviews.png'),full_page=True)
    expect(page.get_by_text('Show the decision behind the work.',exact=True)).to_be_visible()
    page.locator('[data-pg="evidence"]').first.click()
    expect(page.locator('#pg-turn-2')).to_be_focused()
    assert not page.evaluate('!!window.uiInjected'), 'Transcript must be escaped'
    expect(page.locator('#pg-turn-2 img')).to_have_count(0)
    expect(page.locator('#pg-report-tools')).to_be_visible()
    page.screenshot(path=str(OUT/'prep-progress-report.png'),full_page=True)
    # Real reports draw requirement rows with the same .q class above the questions: one retake button per
    # question, on the question card, never on a requirement row.
    expect(page.locator('#report [data-pg="redrill"]')).to_have_count(1)
    assert page.evaluate("document.querySelector('#report [data-pg=redrill]').closest('.q').dataset.qi")=='0'
    # Start a retake without a key: should open the existing key setup screen, not a fake UI.
    page.locator('[data-pg="redrill"]').first.click()
    expect(page.locator('#s-key')).to_have_class('screen on')
    assert page.evaluate('prepApp.state().redrill.question')=='Walk me through your project.'
    page.click('#open-progress'); page.click('[data-tab="history"]')
    page.locator('[data-pg="comparison"]').click()
    expect(page.get_by_text('We built retries.',exact=True)).to_be_visible()
    expect(page.get_by_text('I designed retry backoff after comparing two options.',exact=True)).to_be_visible()
    page.screenshot(path=str(OUT/'prep-progress-comparison.png'),full_page=True)
    page.click('#open-progress'); page.click('#s-progress [data-pg="settings"]')
    expect(page.locator('#pg-saving')).to_be_checked()
    page.screenshot(path=str(OUT/'prep-progress-settings.png'),full_page=True)
    page.uncheck('#pg-saving'); assert backend.enabled is False
    expect(page.locator('#pg-saving')).not_to_be_checked()
    page.check('#pg-saving'); assert backend.enabled is True
    page.click('#pg-dialog [data-pg="close"]')
    # Export returns a real browser download.
    page.click('[data-tab="history"]'); page.click('[data-pg="export"]')
    with page.expect_download() as d: page.click('[data-pg="export-json"]')
    exported=json.loads(Path(d.value.path()).read_text())
    assert len(exported['items'])==len(backend.items)+1
    page.click('#pg-dialog [data-pg="close"]')
    # Deletion is explicit, cancelable, and failures keep history visible.
    count=len(backend.items)
    page.locator('[data-pg="delete"]').first.click(); page.click('#pg-dialog [data-pg="close"]'); assert len(backend.items)==count
    backend.fail_delete=True
    page.locator('[data-pg="delete"]').first.click(); page.click('[data-pg="confirm-delete"]')
    expect(page.locator('#pg-dialog-error')).to_contain_text('Could not delete')
    assert len(backend.items)==count
    backend.fail_delete=False; page.click('[data-pg="confirm-delete"]')
    expect(page.locator('#pg-dialog')).not_to_be_visible(); assert len(backend.items)==count-1
    # Browser-only import requires its own affirmative click.
    local=interview(9,81); local['id']='iv-local'; local['body']['id']='iv-local'; local['summary']['id']='iv-local'
    page.evaluate('r=>localStorage.setItem("ps_last_report",JSON.stringify(r))',local['body'])
    page.click('#s-progress [data-pg="settings"]')
    expect(page.locator('[data-pg="import"]')).to_be_enabled()
    assert not any(i['id']=='iv-local' for i in backend.items)
    page.click('[data-pg="import"]'); expect(page.locator('#pg-dialog')).not_to_be_visible()
    assert any(i['id']=='iv-local' for i in backend.items)
    # Save failure is visible and retry uses the actual history outbox.
    backend.offline=True
    local['body']['id']='iv-retry'
    page.evaluate("async r => { window.dispatchEvent(new CustomEvent('prep:report-rendered',{detail:{record:r}})); await (await import('/prep/app/history.js')).saveInterview(r); }",local['body'])
    expect(page.locator('#pg-save-state')).to_contain_text('Save pending')
    backend.offline=False
    await_count=backend.save_attempts
    page.evaluate("async () => await (await import('/prep/app/history.js')).flushOutbox()")
    expect(page.locator('#pg-save-state')).to_contain_text('Saved to your account')
    assert backend.save_attempts>await_count
    # One interview: never draw a fabricated trend.
    backend.items=[interview(0,50)]; backend.analysis_id=None
    page.evaluate("localStorage.removeItem('ps_history'); localStorage.removeItem('ps_last_report')")
    page.click('#open-progress'); page.click('[data-tab="overview"]')
    expect(page.locator('.pg-chart')).to_have_count(0)
    expect(page.get_by_text('One full interview so far. Your trend starts with the next one.')).to_be_visible()
    # Expired pass: saved reports remain usable and saving cannot be enabled.
    backend.live=False; backend.enabled=False
    page.reload(wait_until='networkidle'); page.click('#open-progress')
    page.click('#s-progress [data-pg="settings"]'); expect(page.locator('#pg-saving')).to_be_disabled(); page.click('#pg-dialog [data-pg="close"]')
    page.click('[data-tab="history"]'); page.locator('#s-progress [data-pg="interview"]').first.click()
    expect(page.locator('#s-report')).to_have_class('screen on')
    expect(page.locator('[data-pg="redrill"]')).to_be_disabled()
    # Signed out: private dashboard contents are not presented.
    backend.signed_in=False
    page.reload(wait_until='networkidle'); page.click('#open-progress')
    expect(page.get_by_text('Sign in to see the interviews saved to your account.')).to_be_visible()
    expect(page.locator('.pg-chart')).to_have_count(0)
    expect(page.locator('.pg-history-row')).to_have_count(0)
    # Demo preview never exposes the locked report's transcript or private feedback.
    locked=interview(0,50)['body']; locked['locked']=True
    page.evaluate("r=>{prepApp.navigate('s-cv');window.dispatchEvent(new CustomEvent('prep:report-rendered',{detail:{record:r,locked:true}}));}",locked)
    expect(page.locator('#pg-report-tools .pg-preview')).to_have_count(1)
    expect(page.locator('#pg-report-tools .pg-turn')).to_have_count(0)
    # Marketing preview links to the same app view, with no made-up user scores.
    page.goto('http://localhost/prep/',wait_until='networkidle')
    expect(page.locator('#progress a[href="app/#progress"]')).to_be_visible()
    page.set_viewport_size({'width':390,'height':900})
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+1')
    page.locator('#progress').screenshot(path=str(OUT/'prep-progress-landing.png'))
    assert not errors, errors
    browser.close()
    print(json.dumps({'result':'passed','browser_errors':errors,'viewports':[320,390,768,1440],'screenshots':str(OUT)}))
