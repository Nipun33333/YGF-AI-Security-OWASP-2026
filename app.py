"""Offline browser UI: localhost only. Python stdlib; no dependency install needed in fixture mode."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from security_lab import all_cases, run_case

CASES=list(all_cases())
UI='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>YGF 2026 AI Security Lab</title>
<style>body{margin:0;font:15px system-ui;background:#101c30;color:#e8f0fa}header{background:#162941;padding:28px max(20px,calc((100vw - 980px)/2));border-bottom:1px solid #2d4364}h1{margin:0;font-size:29px}small{color:#9fc2e8}.wrap{max-width:980px;margin:20px auto;padding:0 20px}.panel{background:#1a2c46;border:1px solid #334969;border-radius:14px;padding:24px;margin-bottom:18px}.row{display:flex;gap:12px;flex-wrap:wrap}label{display:block;margin:10px 0;color:#b8d0ee}select,button{background:#10243d;color:white;border:1px solid #3d6689;border-radius:8px;padding:12px;min-width:140px}button{background:#35a8d7;color:#00182a;font-weight:bold;cursor:pointer}pre{white-space:pre-wrap;word-break:break-word;background:#0c182b;border-radius:9px;padding:16px;max-height:340px;overflow:auto}.note{background:#25354a;padding:12px;border-left:4px solid #ffcf5f;color:#ffdca2}</style>
<header><h1>AI Security Lab / 2026</h1><small>Claude • Gemini • OWASP LLM and Agentic • MCP attack laboratory</small></header><main class="wrap">
<div class="panel"><h2>Security scenario</h2><div class="row"><label>Provider<br><select id="provider"><option value="claude">Claude</option><option value="gemini">Gemini</option></select></label><label>Execution<br><select id="mode"><option value="fixture">Offline deterministic fixture</option><option value="live">Real provider API</option></select></label><label>Defense<br><select id="hardened"><option value="false">Vulnerable baseline</option><option value="true">Hardened</option></select></label></div><label>Attack case<br><select style="width:100%" id="case"></select></label><button id="go">Run sandbox test</button><p class="note">Fixture mode never calls Claude or Gemini. Provider names are labels for compatibility. Real API mode needs separately configured credentials; never paste API keys into the browser.</p></div>
<div class="panel"><h2>Observed behavior</h2><pre id="out">Select a scenario and run.</pre></div>
<div class="panel"><h2>Fake knowledge base and sandbox tools</h2><p>Public docs: FAQ, hours. Private: private.txt contains toy marker SECRET-FLAG-123. Mock tools: file read, fake email queue, fake HTTP log, MCP manifest connect; code execution requests are <strong>never executed</strong>.</p><p>Harness covers 5 LLM, 5 Agentic risk IDs (2026), plus 3 MCP-specific probes. Each risk has 3 cases and before/after tests across both model labels.</p></div></main><script>
(async()=>{let r=await fetch('/api/cases');let data=await r.json();document.querySelector('#case').innerHTML=data.map(c=>`<option value="${c.case_id}">${c.case_id} — ${c.case_name}</option>`).join('')})();
document.querySelector('#go').onclick=async()=>{let out=document.querySelector('#out');out.textContent='Running...';let body={provider:document.querySelector('#provider').value,mode:document.querySelector('#mode').value,hardened:document.querySelector('#hardened').value==='true',case_id:document.querySelector('#case').value};try{let r=await fetch('/api/run',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});out.textContent=JSON.stringify(await r.json(),null,2)}catch(e){out.textContent=String(e)}}
</script></html>'''
class Handler(BaseHTTPRequestHandler):
    def send(self,obj,status=200,content_type="application/json"):
        data=obj.encode() if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status);self.send_header("Content-Type",content_type+"; charset=utf-8");self.send_header("Content-Length",str(len(data)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=="/":self.send(UI,content_type="text/html")
        elif self.path=="/api/cases":self.send([{k:c[k] for k in ("case_id","risk","case_name")} for c in CASES])
        else:self.send({"error":"not found"},404)
    def do_POST(self):
        if self.path!="/api/run":return self.send({"error":"not found"},404)
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length>65536:raise ValueError("request too large")
            request=json.loads(self.rfile.read(length))
            case=next(c for c in CASES if c["case_id"]==request["case_id"])
            result=run_case(case,request["provider"],bool(request["hardened"]),request["mode"])
            self.send(result)
        except Exception as exc:self.send({"error":str(exc)},400)
if __name__=="__main__":
    print('YGF Lab: http://127.0.0.1:8765')
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
