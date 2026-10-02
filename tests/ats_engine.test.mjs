// The ATS checker's scoring and job match (assets/ats-engine.js), with the skill dictionary the page ships.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const ATS = require('../assets/ats-engine.js');
const data = JSON.parse(readFileSync(new URL('../assets/ats-skills.json', import.meta.url), 'utf8'));
const vocab = ATS.compileVocab(data);

const GOOD = `Priya Sharma
Bengaluru · priya.sharma@example.com · +91 98765 43210 · linkedin.com/in/priya-sharma
Summary
Data analyst with four years in e-commerce reporting, SQL and Power BI.
Experience
Data Analyst, Flipkart · Mar 2022 – Present
• Built 14 Power BI dashboards used by 120 category managers every week
• Cut the monthly reporting cycle from 5 days to 2 by automating SQL extracts
• Found why refunds rose 18% in Q2 using SQL on 2 million orders
• Led a pricing analysis that lifted conversion by 3.1% in two categories
Junior Analyst, Swiggy · Jun 2020 – Feb 2022
• Automated 6 Excel reports with Python, saving 10 hours a week
• Analysed delivery delays across 40 cities and presented fixes to operations
Education
B.Tech, Computer Science, VIT Vellore · Jul 2016 – May 2020
Skills
SQL, Python, Excel, Power BI, Tableau, Stakeholder management`;

const POOR = `RESUME
Rahul Kumar
Email: rahul@example.com
Career Objective
To work in a reputed organisation.
My Journey
Responsible for handling reports for the team and the manager.
Worked on many tasks given by the seniors in the office.
Involved in the preparation of monthly sales data for review.
Helped in solving customer issues over the phone and email.
Date of Birth: 01/01/1998
Marital Status: Single
Father's Name: Mr. Kumar
Declaration
I hereby declare that the above information is true.`;

const byId = (res, id) => res.groups.flatMap(g => g.checks).find(c => c.id === id);

test('skills are read exactly as ApplySarthi reads them (expected values from jobhunt/skillvocab.py)', () => {
  const cases = [
    ['We use Go, Python and k8s. React quickly to change; excel at communication.', ['Go', 'Kubernetes', 'Python']],
    ['Golang developer with Spring Boot, C# and .NET; R&D team; R, SQL.', ['C#', 'R', 'SQL', 'Spring']],
    ['Experience with React Native and ReactJS, Power BI dashboards, advanced Excel, CI/CD on Jenkins.',
     ['CI/CD', 'Excel', 'Jenkins', 'Power BI', 'React', 'React Native']],
    ['<p>Machine learning with PyTorch</p><li>LLMs and RAG pipeline</li> in the spring of 2026',
     ['LLMs', 'Machine learning', 'PyTorch', 'RAG']],
  ];
  for (const [text, want] of cases) assert.deepEqual(ATS.skillsIn(vocab, text, 15), want, text);
});

test('a clean CV scores high and every area passes', () => {
  const res = ATS.analyse({ text: GOOD, kind: 'pdf', pages: 1, columns: 0, images: false, links: [] });
  assert.ok(res.score >= 90, `score ${res.score}`);
  assert.equal(res.band, 'ready');
  for (const id of ['text', 'columns', 'junk', 'length', 'email', 'phone', 'linkedin', 'experience', 'education',
                    'skills', 'summary', 'detail', 'numbers', 'verbs', 'dates', 'personal', 'declaration', 'title'])
    assert.equal(byId(res, id).status, 'pass', id);
  const weights = res.groups.flatMap(g => g.checks).reduce((n, c) => n + c.weight, 0);
  assert.equal(weights, 100);
});

test('Indian CV habits, missing headings and weak lines are flagged, worst first', () => {
  const res = ATS.analyse({ text: POOR, kind: 'text' });
  assert.equal(byId(res, 'personal').status, 'fail');
  assert.match(byId(res, 'personal').detail, /date of birth, marital status, father’s name/);
  assert.equal(byId(res, 'declaration').status, 'warn');
  assert.equal(byId(res, 'title').status, 'warn');
  assert.equal(byId(res, 'experience').status, 'fail');      // "My Journey" is not a heading a parser knows
  assert.equal(byId(res, 'education').status, 'fail');
  assert.equal(byId(res, 'phone').status, 'fail');
  assert.equal(byId(res, 'verbs').status, 'warn');
  assert.match(byId(res, 'verbs').detail, /Responsible for/);
  assert.equal(byId(res, 'columns').status, 'na');           // pasted text has no layout to judge
  assert.ok(res.score < 55 && ['work', 'fix'].includes(res.band), `score ${res.score}`);
  // The layout check could not run on pasted text: it neither earns nor loses points.
  const ran = res.groups.flatMap(g => g.checks).filter(c => c.status !== 'na');
  const raw = ran.reduce((n, c) => n + c.earned, 0) / ran.reduce((n, c) => n + c.weight, 0);
  assert.equal(res.score, Math.round(100 * raw));
  assert.equal(res.fixes.length, 3);
  const lost = res.fixes.map(c => c.weight - c.earned);
  assert.deepEqual(lost, [...lost].sort((a, b) => b - a));
});

test('a PDF with no text is unreadable and scores zero', () => {
  const res = ATS.analyse({ text: '  \n Page 1 \n', kind: 'pdf', pages: 2 });
  assert.equal(res.unreadable, true);
  assert.equal(res.score, 0);
  assert.match(res.groups[0].checks[0].detail, /scan or an image/);
});

test('two columns, layout tables, icon characters and length are judged from what the reader saw', () => {
  const cols = ATS.analyse({ text: GOOD, kind: 'pdf', pages: 3, columns: 0.42 });
  assert.equal(byId(cols, 'columns').status, 'warn');
  // Two columns is the biggest real fix: never "Ready to send", however good the rest is.
  const twoCol = ATS.analyse({ text: GOOD, kind: 'pdf', pages: 1, columns: 0.42 });
  assert.equal(twoCol.score, 79);
  assert.equal(twoCol.band, 'good');
  assert.equal(twoCol.fixes[0].id, 'columns');
  assert.equal(byId(cols, 'length').status, 'warn');
  const docx = ATS.analyse({ text: GOOD, kind: 'docx', tables: 2 });
  assert.equal(byId(docx, 'columns').status, 'warn');
  assert.match(byId(docx, 'email').detail, /Found/);
  const junk = ATS.analyse({ text: GOOD.replace(/·/g, String.fromCharCode(0xf0b7, 32, 0xf095, 32, 0xf0e0)), kind: 'pdf', pages: 1, columns: 0 });
  assert.notEqual(byId(junk, 'junk').status, 'pass');
});

test('contact details lost to a Word header get the header hint', () => {
  const noContact = GOOD.split('\n').filter((l, i) => i !== 1).join('\n');
  const res = ATS.analyse({ text: noContact, kind: 'docx', tables: 0 });
  assert.equal(byId(res, 'email').status, 'fail');
  assert.match(byId(res, 'email').detail, /page header/);
  assert.equal(byId(res, 'linkedin').status, 'warn');
});

test('Indian phone numbers in every common grouping, and dates that are not phones', () => {
  const phone = t => byId(ATS.analyse({ text: GOOD.replace('+91 98765 43210', t), kind: 'text' }), 'phone').status;
  for (const t of ['9876543210', '98765 43210', '987-654-3210', '+919876543210', '(+91) 98765-43210', '09876543210'])
    assert.equal(phone(t), 'pass', t);
  for (const t of ['2019 - 2023', '01/2020', '12345 67890'])
    assert.equal(phone(t), 'fail', t);
});

test('dates: one format passes, two formats warn, words that start like months are not dates', () => {
  assert.equal(byId(ATS.analyse({ text: GOOD, kind: 'text' }), 'dates').status, 'pass');
  const mixed = GOOD.replace('Jun 2020 – Feb 2022', '06/2020 – 02/2022');
  assert.equal(byId(ATS.analyse({ text: mixed, kind: 'text' }), 'dates').status, 'warn');
  assert.ok(ATS.hasResultNumber('Ran marketing 10 campaigns for new users'));
  assert.ok(!ATS.hasResultNumber('Worked here from Mar 2021 to Dec 2023 on the platform team'));
});

test('letter-spaced and decorated headings are still recognised', () => {
  const h = ATS.findHeadings(['E X P E R I E N C E', 'EDUCATION:', '• Technical Skills', 'Professional Summary',
                              'Academic Projects']);
  assert.equal(h.experience, 'EXPERIENCE');
  assert.equal(h.education, 'EDUCATION');
  assert.equal(h.skills, 'Technical Skills');
  assert.equal(h.summary, 'Professional Summary');
  assert.equal(h.projects, 'Academic Projects');
  assert.deepEqual(ATS.findHeadings(['Experience in building data pipelines for retail clients across India']), {});
});

test('job match: skills the description names, then the words it repeats, never hiring boilerplate', () => {
  const jd = `Acme Retail is hiring a Data Analyst. You will build dashboards in Power BI and Tableau, write SQL,
    and work with stakeholders. Strong Excel and Python. Experience with dashboards for merchandising teams.
    You will own merchandising reporting and forecasting. Forecasting experience preferred. Acme offers hybrid work.`;
  const m = ATS.matchJob(vocab, GOOD, { jd, exclude: ['Acme', 'Retail'] });
  assert.equal(m.kind, 'jd');
  assert.ok(m.enough);
  assert.deepEqual(m.skills.missing, []);
  assert.ok(m.skills.found.includes('Tableau') && m.skills.found.includes('SQL'));
  assert.ok(m.terms.missing.includes('merchandising'));
  assert.ok(m.terms.missing.includes('forecasting'));
  assert.ok(m.terms.found.includes('dashboards'));
  for (const w of ['experience', 'hybrid', 'acme', 'work', 'strong']) {
    assert.ok(!m.terms.found.concat(m.terms.missing).includes(w), w);
  }
  assert.equal(m.percent, 100);                 // every skill it names is in the CV; words are advice only
  assert.equal(m.band, 'strong');
});

test('a description with few dictionary skills gets its repeated words and no percentage', () => {
  const jd = `Inside sales executive for our Pune branch. Call channel partners and distributors daily, grow
    distributor revenue, visit channel partners, maintain distributor records and report territory targets to
    the branch head. Territory travel required. Global company with a mission to drive complex growth.`;
  const m = ATS.matchJob(vocab, GOOD, { jd });
  assert.equal(m.enough, false);
  assert.equal(m.percent, null);
  // Shown in the form the description first used: "distributors", "partners".
  for (const w of ['distributor', 'channel', 'territory']) assert.ok(m.terms.missing.some(x => x.startsWith(w)), w);
  for (const w of ['global', 'mission', 'drive', 'complex']) assert.ok(!m.terms.missing.includes(w), w);
});

test('role match uses the skills at least one posting in ten names', () => {
  const role = data.roles['devops-engineer'];
  const m = ATS.matchJob(vocab, GOOD, { role });
  assert.equal(m.kind, 'role');
  const wanted = role.skills.filter(s => s[1] >= 10).map(s => s[0]);
  assert.deepEqual([...m.skills.found, ...m.skills.missing].sort(), wanted.slice(0, 10).sort());
  assert.ok(m.skills.found.includes('Python'));
  assert.ok(m.skills.missing.includes('Kubernetes'));
  assert.equal(m.band, 'weak');
});

test('a description too short to compare says so instead of scoring', () => {
  const m = ATS.matchJob(vocab, GOOD, { jd: 'Analyst needed in Pune. Apply now.' });
  assert.equal(m.enough, false);
});
