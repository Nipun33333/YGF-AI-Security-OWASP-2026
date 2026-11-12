import csv,json
from pathlib import Path
from artifact_tool import Workbook, SpreadsheetFile
BASE=Path(__file__).parent
rows=list(csv.DictReader((BASE/'results'/'fixture_results.csv').open(encoding='utf-8')))
risk=json.loads((BASE/'data'/'cases.json').read_text())
wb=Workbook.create()
s=wb.worksheets.add('Overview')
s.get_range('A1:H1').merge_cells() if False else None
s.merge_cells('A1:H1')
s.get_range('A1').values=[['OWASP 2026 | YGF AI SECURITY POC']]
s.get_range('A1:H1').format={'fill':'#142941','font':{'bold':True,'color':'#FFFFFF','size':19},'row_height':40}
s.merge_cells('A2:H2')
s.get_range('A2').values=[['Offline fixtures, not a real Claude / Gemini benchmark  |  12 Nov 2026']]
s.get_range('A2:H2').format={'fill':'#E9F2FA','font':{'color':'#244F75','italic':True},'row_height':25}
s.get_range('A4:B9').values=[['Metric','Value'],['Required OWASP risk IDs',10],['Additional MCP risk group',1],['Attack scenarios',33],['Provider-label × phase rows',132],['Real provider calls',0]]
s.get_range('A4:B4').format={'fill':'#17608C','font':{'bold':True,'color':'#FFFFFF'},'row_height':27}
s.get_range('A4:A9').format.column_width=30
s.get_range('B4:B9').format.column_width=23
s.get_range('D4:H4').values=[['Provider label','Baseline markers','After markers','API calls','Evidence status']]
s.get_range('D4:H4').format={'fill':'#17608C','font':{'bold':True,'color':'#FFFFFF'},'row_height':26}
s.get_range('D5:H6').values=[['Claude',33,0,0,'FIXTURE ONLY'],['Gemini',33,0,0,'FIXTURE ONLY']]
for col,w in zip('DEFGH',[20,22,20,18,26]): s.get_range(f'{col}4:{col}6').format.column_width=w
s.get_range('A12:F12').values=[['Risk ID','2026 risk name','Cases','Before (fixture)','After (fixture)','Mitigation']]
s.get_range('A12:F12').format={'fill':'#17608C','font':{'bold':True,'color':'#FFFFFF'},'row_height':28}
summary=[[r['risk'],r['name'],3,6,0,r['mitigation']] for r in risk]
s.get_range('A13:F23').values=summary
for col,w in zip('ABCDEF',[16,35,12,20,18,66]): s.get_range(f'{col}12:{col}23').format.column_width=w
s.get_range('A13:F23').format.row_height=22
s.get_range('F13:F23').format.wrap_text=True
s.merge_cells('A26:H26')
s.get_range('A26').values=[['These fixture markers are deliberately designed outcomes: do not interpret as verified model vulnerability rates.']]
s.get_range('A26:H26').format={'fill':'#FFF4DD','font':{'color':'#814A06','bold':True},'row_height':33}
s.freeze_panes.freeze_rows(4)

r=wb.worksheets.add('Results - 132 rows')
keys=['risk_id','risk_name','case_id','model','mode','phase','prompt','result','marker','response','mitigation','evidence_type']
headers=['Risk ID','Risk name','Case ID','Model','Mode','Phase','Prompt','Result','Marker','Model or fixture response','Mitigation','Evidence']
r.get_range('A1:L1').values=[headers]
r.get_range('A1:L1').format={'fill':'#142941','font':{'color':'#FFFFFF','bold':True},'row_height':31}
r.get_range('A2:L133').values=[[row[k] for k in keys] for row in rows]
r.get_range('A2:L133').format.row_height=28
for col,width in zip('ABCDEFGHIJKL',[13,29,16,15,15,14,65,22,23,73,62,34]): r.get_range(f'{col}1:{col}133').format.column_width=width
for col in ['G','J','K']:r.get_range(f'{col}2:{col}133').format.wrap_text=True
r.freeze_panes.freeze_rows(1)
try: r.tables.add('A1:L133',True,'SecurityCases')
except Exception as e: print('Optional table creation skipped:',e)

m=wb.worksheets.add('Methodology')
method=[
['FIELD','EXPLANATION'],
['Risk ID','2026 OWASP LLM and Agentic IDs; MCP-POC is a supplementary connection-risk family.'],
['Mode: fixture','Toy application control-plane simulation; does not call LLM APIs.'],
['Model: Claude / Gemini','TARGET LABELS ONLY in fixture mode; each pair has identical outputs by construction.'],
['Phase: BEFORE','Intentionally vulnerable branch of local deterministic simulator.'],
['Phase: AFTER','Risk-specific application-level defensive check enabled.'],
['Result: OBSERVED_MARKER','Toy violation marker found in fixture response. Not a model exploit proof.'],
['Result: NO_MARKER','Toy violation marker absent. Not a universal safety guarantee.'],
['Evidence','FIXTURE_ONLY_NO_LLM_CALL for this sheet. Actual tests need --mode live.'],
['Real provider usage','Requires ANTHROPIC_API_KEY and GEMINI_API_KEY on the operator environment.'],
['Real model validation','Review live results carefully; live mode is response-only probing without real tool execution.'],
['Safe scope','Localhost / Docker/VM; fake data, no shell, no real emails or HTTP.'],
['Official LLM 2026','https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/'],
['Official Agentic 2026','https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/'],
['Date','12 November 2026']]
m.get_range('A1:B15').values=method
m.get_range('A1:B1').format={'fill':'#142941','font':{'color':'#FFFFFF','bold':True},'row_height':26}
m.get_range('A1:A15').format.column_width=28
m.get_range('B1:B15').format.column_width=115
m.get_range('A2:B15').format.row_height=25
m.get_range('B2:B15').format.wrap_text=True
m.freeze_panes.freeze_rows(1)
out=BASE/'docs'/'YGF_OWASP_2026_Results.xlsx'
SpreadsheetFile.export_xlsx(wb).save(str(out))
print(out,out.stat().st_size)
