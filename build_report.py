import csv, json
from pathlib import Path
from collections import Counter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

BASE=Path(__file__).parent
OUT=BASE/'docs'/'YGF_AI_Security_OWASP_2026_Report.pdf'
RISK=json.loads((BASE/'data'/'cases.json').read_text())
ROWS=list(csv.DictReader((BASE/'results'/'fixture_results.csv').open(encoding='utf-8')))
navy=HexColor('#10243C'); blue=HexColor('#1476A8'); pale=HexColor('#EAF2FA'); body=HexColor('#203344'); muted=HexColor('#617489')
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title2',fontName='DVB',fontSize=24,leading=31,textColor=navy,spaceAfter=16))
styles.add(ParagraphStyle(name='H1x',fontName='DVB',fontSize=17,leading=22,textColor=navy,spaceBefore=12,spaceAfter=9))
styles.add(ParagraphStyle(name='H2x',fontName='DVB',fontSize=11.2,leading=15,textColor=blue,spaceBefore=9,spaceAfter=6))
styles.add(ParagraphStyle(name='Bodyx',fontName='DV',fontSize=9,leading=14,textColor=body,spaceAfter=8))
styles.add(ParagraphStyle(name='Smallx',fontName='DV',fontSize=7.4,leading=10.7,textColor=body,spaceAfter=4))
styles.add(ParagraphStyle(name='Tablex',fontName='DV',fontSize=7.1,leading=10,textColor=body))
styles.add(ParagraphStyle(name='TabB',fontName='DVB',fontSize=7.1,leading=10,textColor=navy))
styles.add(ParagraphStyle(name='Note',fontName='DVB',fontSize=9,leading=14,textColor=HexColor('#9D4010'),spaceAfter=12))

def P(s,style='Bodyx'): return Paragraph(str(s).replace('&','&amp;'),styles[style])
def rich(s,style='Bodyx'): return Paragraph(s,styles[style])
def paged(canvas,doc):
    canvas.setStrokeColor(HexColor('#CBD6E5'))
    canvas.line(42,37,553,37)
    canvas.setFont('DV',7.5);canvas.setFillColor(muted)
    canvas.drawString(42,25,'YGF AI Security internship | OWASP 2026 | sandbox POC')
    canvas.drawRightString(553,25,f'{doc.page}')

def mk_table(data,widths=None,header=True):
    rows=[]
    for i,row in enumerate(data):
        rows.append([P(str(v),'TabB' if i==0 and header else 'Tablex') for v in row])
    t=Table(rows,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),0.7,blue)]
    if header:cmds.append(('BACKGROUND',(0,0),(-1,0),pale))
    for i in range(1,len(data)):
        if i%2==0:cmds.append(('BACKGROUND',(0,i),(-1,i),HexColor('#F6F9FC')))
    t.setStyle(TableStyle(cmds));return t

story=[]
def add(*elements):story.extend(elements)
add(Spacer(1,44),P('AI SECURITY LAB / 2026','H2x'),P('OWASP LLM + Agentic Risk<br/>Proof of Concept','Title2'),rich('<b>Prepared for:</b> Youth Growth Foundation (YGF NGO) — AI Security Internship, Round 2'),rich('<b>Candidate:</b> Nipun Agarwal &nbsp;&nbsp; <b>Date:</b> 12 November 2026'),Spacer(1,15),P('33 harmless attack cases  |  11 risk groups  |  132 fixture rows','H2x'))
add(mk_table([['Deliverable','Scope'],['Browser app','Localhost POC with switchable Claude / Gemini adapters'],['AI agent','Fake file read, email, HTTP and MCP manifest connection'],['Tests','At least 3 per required risk; before-and-after controls'],['Report status','Offline simulation verified; live model benchmarking pending API access']],[135,370]))
add(Spacer(1,20),P('RESEARCH INTEGRITY','H2x'),P('The results in this document are deterministic <b>application-fixture simulations</b>. The values do not represent real responses from Claude or Gemini. To compare the actual LLM services, the repository includes separate API-backed testing commands that require valid model credentials.'))
add(PageBreak())
add(P('01 / Executive summary','H1x'),P('The POC illustrates how unsafe application orchestration can expose secrets, accept injected tasks or tool definitions, generate unsafe HTML, or promote untrusted context into privileged actions. An intentionally vulnerable fixture is paired with a hardened server-side security control for each risk.'))
add(P('Key results from sandbox-fixture tests','H2x'))
add(mk_table([['Metric','Fixture result','Meaning'],['Risk families','11 (10 specified + MCP)','Required 2026 taxonomy covered'],['Distinct attack cases','33','3 per risk group'],['Model-labeled comparisons','132 rows','2 labels × before/after; not real LLM calls'],['Before mitigation','66 / 66 markers observed','By design; application vulnerability fixtures'],['After mitigation','0 / 66 markers observed','Deterministic server-side policies blocked markers'],['Unintended real side effects','0','No shell, real network calls or external mail']],[170,105,230]))
add(Spacer(1,8),P('OWASP 2026 mapping matters','H2x'),P('The 2026 LLM list was renumbered relative to 2025. For this assignment, LLM03 means Excessive Agency, LLM08 means Hidden Context Exposure, and LLM10 means Improper Output Handling. Agentic ASI05 covers unexpected code execution; ASI06 covers memory and context poisoning.'))
add(P('Evaluation limits','H2x'),P('Fixture results verify that the demonstrator differentiates vulnerable from hardened controls. They do not measure model guardrail quality, probability of a successful jailbreak, provider ranking, or real tool-use exploit rates.'))
add(PageBreak())
add(P('02 / Architecture and method','H1x'))
add(mk_table([['Component','Purpose','Trust boundary'],['User & untrusted KB','Malicious toy instructions and fake records','Must not override trusted user goal'],['Claude/Gemini adapters','Optional API-backed text inference','Model response treated as untrusted'],['Tool router','read_file; send_email; http_call; mcp_connect','Server-side target, role and approval rules'],['Fixture runner','Repeatable 33-case baseline','No external side effects'],['Hardened path','Per-risk policy checks','Unauthorized intent rejected']],[130,185,190]))
add(P('Execution protocol','H2x'))
for i,s in enumerate(['Prepare 33 toy adversarial prompts and 11 distinct mitigation rules.','For each case, execute vulnerable and hardened fixture modes under both provider-target labels.','Log Risk ID, model label, exact prompt, defense phase, observed marker and supporting response.','Apply same scenarios in real provider mode only after securely configuring local Claude and Gemini API keys.','Analyze actual model text manually; do not equate absence of a marker with complete security.'],1):
    add(P(f'{i}. {s}'))
add(P('Environment','H2x'),P('All fixture tests run with Python standard library on 127.0.0.1:8765. A minimal non-root Dockerfile is provided for additional isolation. Fake emails are only appended to an in-memory queue; HTTP entries are logged without requesting URLs; candidate code is never executed. The toy private file carries SECRET-FLAG-123.'))
add(PageBreak())
add(P('03 / Required LLM risks (2026)','H1x'))
for r in RISK[:5]:
    add(P(f'{r["risk"]}: {r["name"]}','H2x'))
    c=', '.join(x[0] for x in r['cases'])
    add(P(f'<b>Cases:</b> {c}. <b>Control:</b> {r["mitigation"]}.','Smallx'))
add(Spacer(1,12),mk_table([['2026 risk','Vulnerable (3 cases × 2 labels)','Hardened (3 × 2)']]+[[r['risk']+' — '+r['name'],'6 / 6 toy markers','0 / 6 toy markers'] for r in RISK[:5]],[240,132,133]))
add(P('Interpretation','H2x'),P('The 30/30 before and 0/30 after counts on this page are fixture outcomes only. The same scenario strings may behave differently when submitted to a real API; no empirical Claude/Gemini results were available during this preparation.'))
add(PageBreak())
add(P('04 / Required Agentic risks (2026)','H1x'))
for r in RISK[5:10]:
    add(P(f'{r["risk"]}: {r["name"]}','H2x'))
    c=', '.join(x[0] for x in r['cases'])
    add(P(f'<b>Cases:</b> {c}. <b>Control:</b> {r["mitigation"]}.','Smallx'))
add(Spacer(1,12),mk_table([['2026 risk','Vulnerable fixture','Hardened fixture']]+[[r['risk']+' — '+r['name'],'6 / 6 markers','0 / 6 markers'] for r in RISK[5:10]],[240,132,133]))
add(P('Agent safety note','H2x'),P('A secure application cannot rely on the language model alone to decide whether the caller is an admin or whether a tool action is approved. Enforced permissions, explicit side-effect approval and execution sandboxing remain the application responsibility.'))
add(PageBreak())
add(P('05 / MCP connection risk and POC','H1x'),P('The connection test simulates a rogue MCP-like tool provider that attempts to influence the local agent. The payloads are a tool-name collision, an unapproved read-write capability expansion, and adversarial tool-description instructions.'))
add(mk_table([['Step','Vulnerable simulator','Hardened simulator'],['1. Discover server','Trusts a forged manifest','Requires trusted-local-v1 identity'],['2. Parse tools','Accepts send_email / private read','Allows public_kb_search only'],['3. Honor scope','Allows read-write claim','Requires read-only scope'],['4. Execute connection','Logs accepted mock manifest','Returns BLOCKED without adding tool'],['Result (3 × 2 labels)','6 / 6 toy markers','0 / 6 toy markers']],[125,193,187]))
add(P('Boundary diagram','H2x'),mk_table([['UNTRUSTED MCP METADATA','HOST-ENFORCED POLICY','MOCK AGENT'],['Server ID / advertised tools / scope','Pin identity + allowlist capabilities','Access public KB only'],['Injected tool description','Treat as data, never instruction','No privilege elevation']],[169,169,167]))
add(Spacer(1,12),P('MCP limitation','H2x'),P('This demonstrates capability-validation logic but does not implement a live MCP transport, cryptographic attestation, or a complete interoperable MCP server-client handshake. A full protocol exercise would be a further enhancement.'))
add(PageBreak())
add(P('06 / Claude versus Gemini: status','H1x'),P('The project implements two provider adapters using the vendors’ Python SDKs. No real provider requests were made when producing the included fixture ledger. Results must therefore be treated as <b>NOT YET BENCHMARKED</b>, not as a tie or comparative security ranking.'))
add(mk_table([['Measure','Claude','Gemini'],['Adapter in code','Implemented','Implemented'],['Fixture cases labeled for model','33 × 2 phases','33 × 2 phases'],['Actual API prompts sent','0','0'],['Verified live attacks / mitigations','Not tested','Not tested'],['Fixture marker baseline','33 / 33 (synthetic)','33 / 33 (synthetic)'],['Fixture marker after defense','0 / 33 (synthetic)','0 / 33 (synthetic)']],[230,138,137]))
add(P('How to complete the genuine comparison','H2x'))
add(P('1. Add both API keys to local environment variables, never to GitHub. 2. Run <b>python run_tests.py --mode live --provider both</b> after installing dependencies. 3. Review the CSV for refusals, false positives and differences in wording. 4. Separate model-response outcomes from app-level tool effects; here live mode is text-only. 5. Rebuild the report/results sheet from observed live outcomes and describe any API or model version differences.'))
add(P('Threat and benchmark limitations','H2x'),P('As written, live probing evaluates exact toy marker appearance and does not invoke provider-native tool calling. It is inappropriate to infer that a provider is safer solely from the resulting marker count. The PoC illustrates application-layer controls rather than production-hardened defenses.'))
add(PageBreak())
add(P('07 / Evidence and next steps','H1x'))
add(P('Files delivered','H2x'),P('The submission bundle includes working Python sources, README, Dockerfile, 33 scenario prompts, unit tests, a CSV evidence log, a formatted spreadsheet, this PDF, and a local explanatory demo video.'))
add(P('Verification','H2x'),P('The Python unit test suite confirms that all 33 vulnerable fixtures expose their expected toy markers, all 33 hardened fixtures suppress those markers, the MCP guard rejects a malicious manifest, a private file is blocked, and fake email uses an in-memory queue. Test report: 6 tests, all passing.'))
add(P('Further improvements','H2x'),P('Priority 1: run both real providers under explicit authorization. Priority 2: implement provider-native structured function calling to exercise actual tool requests and separate model failures from control-plane failures. Priority 3: test official MCP transport and server verification. Priority 4: integrate a SIEM pipeline such as Wazuh for monitoring (optional extra credit).'))
add(P('References','H2x'))
refs=[('OWASP GenAI LLM Top 10 (2026)','https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/'),('OWASP Agentic Top 10 (2026)','https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/'),('Anthropic SDK','https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python'),('Google Gemini SDK','https://ai.google.dev/gemini-api/docs/get-started')]
for label,url in refs: add(P(label+': '+url,'Smallx'))
add(Spacer(1,18),P('End of report. All data and exploits are simulated; no real systems were targeted.','Note'))

pdf=SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),leftMargin=42,rightMargin=42,topMargin=50,bottomMargin=53,title='YGF AI Security OWASP 2026 POC Report',author='Nipun Agarwal')
pdf.build(story,onFirstPage=paged,onLaterPages=paged)
print(OUT)
