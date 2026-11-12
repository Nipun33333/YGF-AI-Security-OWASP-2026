import os,subprocess,textwrap,json,math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
BASE=Path(__file__).parent
DOCS=BASE/'docs'
TMP=BASE/'_video_build';TMP.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
chapters=[
('Assignment overview','33 cases / 11 groups / 132 fixture rows', ['5 OWASP LLM 2026 risk families','5 OWASP Agentic 2026 risk families','3 extra MCP connection scenarios'],
'''Welcome to the Youth Growth Foundation AI Security internship assignment demonstration. This project is a self-contained educational proof of concept about OWASP security risks in large language model applications and agentic AI systems. The project has thirty three harmless attack scenarios, covering the ten required risk identifiers and an additional MCP connection category. Each case includes a vulnerable baseline, a mitigation, and a repeatable after test. The provider selector names Claude and Gemini. One vital distinction: the test records shown in this video are deterministic sandbox fixtures, not genuine Claude or Gemini API results. I will explain precisely how real-provider testing can be activated later.''',None),
('Architecture','Toy data, defensive gates, optional model adapters',['Browser UI runs locally on port 8765','Fake knowledge base + four sandbox tools','No real email, HTTP or shell execution'],
'''This application has five main components. A lightweight browser interface presents a choice of model label, attack case, execution mode, and defense setting. A toy knowledge base includes public FAQ notes and one private record containing a harmless secret marker. The agent-side simulator offers four tools: file reading, email queuing, HTTP logging, and an MCP manifest connection. Those tools are intentionally simulated, so they never send an email or request a real website. The security lab contains the risk-specific controls. Finally, optional Anthropic and Google SDK adapters can submit text prompts to actual model APIs after the operator securely provides credentials.''','app_ui.png'),
('2026 OWASP taxonomy','Using the CURRENT risk numbering',['LLM03: Excessive Agency','LLM08: Hidden Context Exposure','LLM10: Improper Output Handling'],
'''The assignment explicitly references the twenty twenty six OWASP lists, so version control matters. In the LLM taxonomy, the required items are prompt injection, sensitive information disclosure, excessive agency, hidden context exposure, and improper output handling. Agentic risks include goal hijacking, tool misuse, identity and privilege abuse, unexpected code execution, and memory poisoning. Some of these numbers meant different things in the earlier OWASP editions. The repository and report consistently use the twenty twenty six definitions. Every one of those ten required groups has three separate attack prompts. An additional eleventh category tests an untrusted MCP connection boundary.''',None),
('Vulnerable example','LLM02 / toy confidential marker',['Case LLM02-01: request private file content','Insecure branch permits fake private read','Marker appears in response: intentional fixture'],
'''Here is an example of the deliberately vulnerable baseline. The scenario labeled LLM zero two, case one, asks the assistant to reveal data from a private toy file instead of a public FAQ. The local fixture stores the harmless marker secret flag one two three in that document. In baseline mode, the security lab permits this unauthorized fake file read and returns the marker. The results CSV records an observed marker. This is a deterministic property of our intentionally insecure application branch, not a claim that Claude leaked real information. The purpose of the example is to show a reproducible access control failure in application logic.''','demo_before.png'),
('Hardened example','Application-level authorization blocks access',['Same prompt / same fixture / same provider label','Authorization check denies private file','No marker appears after mitigation'],
'''Now we rerun precisely the same scenario with hardened mode enabled. The tool router checks which fake files the caller is authorized to read, and the private file is no longer returned. The response records access denied, and the marker is absent. This isolates one control that addresses the sensitive disclosure risk: server-side information access checks and context redaction. The same approach is repeated across all cases, but controls differ by risk. Prompt injection requires data-instruction separation; excessive agency requires approval for side effects; unsafe output requires escaping. A model refusal alone is not a substitute for these host-level restrictions.''','demo_after.png'),
('Agentic risk families','Goals, privileges, tools, code, memory',['ASI01 preserves the original user goal','ASI03 rejects identity claims in prompts','ASI05 never executes a shell command'],
'''Agentic systems can cause harm even if the model generates plausible natural language. We therefore model the security boundary between instructions and tool execution. For goal hijacking, the trusted task must not be overwritten by a retrieved web page. Tool misuse is constrained with parameter validation and approved destinations. Caller identity must be determined by the application rather than statements such as I am an administrator. Requests that resemble executable code are logged in memory and never run. Finally, memory updates carry an approval requirement so untrusted document text cannot silently replace a persistent trusted preference. Three test cases illustrate each of these five agentic concerns.''',None),
('MCP connection POC','Rogue capability and manifest metadata',['Untrusted server identity: rogue-mcp','Unexpected tool: send_email','Expanded scope: read-write'],
'''For the MCP portion, the simulator receives a deliberately untrustworthy server manifest. The imaginary remote tool provider claims a new capability, changes its scope to read write, and advertises a deceptive server identity. The vulnerable fixture accepts these fields into its in-memory log. The hardened fixture instead verifies a pinned local server identity, limits the allowed tool to public knowledge base search, and requires a read-only scope. A failed validation prevents the tool from entering the trusted set. This is a useful connection risk proof of concept, but it is not a complete networked MCP server implementation or a cryptographic transport test.''','demo_mcp.png'),
('Test evidence','Automated, repeatable, clearly labeled',['33 scenarios x 2 model labels x 2 phases','132 CSV entries, exact prompts included','4 local unit tests passed'],
'''The fixture runner expands each attack case into four records: Claude label before, Claude label after, Gemini label before, and Gemini label after. This creates one hundred thirty two rows. Sixty six pre-mitigation rows contain the intentionally exposed toy marker; all sixty six after-mitigation rows suppress it. These outcomes are expected because the fixture is deterministic. Four separate Python unit tests passed, including the test for all thirty three scenarios, a private file check, a forbidden MCP manifest, and evidence that a fake email is not actually sent. The accompanying spreadsheet contains risk ID, model, prompt, result, evidence type, and mitigation.''',None),
('Claude and Gemini','Ready for optional API text probes',['Select live mode after configuring API keys','ANTHROPIC_API_KEY and GEMINI_API_KEY','No keys included in repository or video'],
'''Actual Claude versus Gemini model testing requires valid API keys and enabled models. The project includes provider adapters that call the official Python SDKs. A local operator can install dependencies and run the test harness with the live mode flag, collecting actual text responses into a separate CSV. The current package does not make those external calls, because the accounts and credentials were not supplied. As a result, it would be inaccurate to show a Claude versus Gemini winner or any measured jailbreak success rate. Even in live mode, the included probe only evaluates text and does not execute suggested tool calls. Manual validation and expanded provider-native function calling are recommended.''',None),
('Conclusion and submission','Report + workbook + code + demo',['PDF: 8 pages, within the 10-page limit','README explains setup and limitations','Use only sandbox fake data and own APIs'],
'''To summarize, this project provides a complete local teaching demonstration of the specified OWASP 2026 risk categories, plus a distinct MCP connection trust-boundary simulation. It contains a browser interface, fake agent tools, the attack library, repeatable tests, a detailed README, a PDF report, and a formatted results workbook. The claims are deliberately narrow: verified local fixture behavior, no real side effects, and no invented API benchmarking. A stronger follow-up evaluation would run authorized calls through both real providers, inspect the responses, and implement structured tool-calling tests and protocol-level MCP verification. Thank you for reviewing the Youth Growth Foundation AI Security proof of concept.''',None)
]

def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)

def wrapped(draw, s, f, maxw):
    words=s.split(); out=[]; cur=''
    for w in words:
        test=(cur+' '+w).strip()
        if draw.textbbox((0,0),test,font=f)[2] <= maxw: cur=test
        else:out.append(cur);cur=w
    if cur:out.append(cur)
    return out

for i,(title,kicker,bullets,script,shot) in enumerate(chapters,1):
    im=Image.new('RGB',(1280,720),'#0f2035');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1280,12),fill='#2db7d1')
    d.rounded_rectangle((55,48,1225,669),radius=24,fill='#152d49',outline='#294964',width=2)
    d.text((86,83),'YGF  |  AI SECURITY INTERNSHIP  |  2026',font=font(19,True),fill='#50cae4')
    d.text((86,132),title,font=font(45,True),fill='#ffffff')
    d.text((88,198),kicker,font=font(21),fill='#b5d4e6')
    d.line((88,241,1190,241),fill='#426786',width=2)
    max_w=510 if shot else 1030
    y=284
    for bullet in bullets:
        d.ellipse((92,y+11,102,y+21),fill='#30bdd7')
        lines=wrapped(d,bullet,font(24),max_w)
        for ln in lines:d.text((121,y),ln,font=font(24),fill='#edf4fc');y+=38
        y+=26
    if shot:
        src=Image.open(DOCS/shot).convert('RGB')
        # crop top 750px to keep controls and output legible
        src=src.crop((0,0,src.width,min(790,src.height)))
        src.thumbnail((575,348))
        left=1225-39-src.width;top=275
        im.paste(src,(left,top))
        d.rectangle((left-2,top-2,left+src.width+2,top+src.height+2),outline='#68b8d2',width=3)
    d.text((89,617),'DETERMINISTIC OFFLINE FIXTURE — NOT ACTUAL MODEL TESTS',font=font(15,True),fill='#fcd08c')
    d.text((1165,617),f'{i:02d}/{len(chapters):02d}',font=font(19,True),fill='#ccd9e8')
    im.save(TMP/f'slide_{i:02}.png')
    (TMP/f'script_{i:02}.txt').write_text(script,encoding='utf-8')
    subprocess.run(['espeak','-v','en-us','-s','145','-p','50','-f',str(TMP/f'script_{i:02}.txt'),'-w',str(TMP/f'voice_{i:02}.wav')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(TMP/f'voice_{i:02}.wav')]).decode().strip())
    print('slide',i,'seconds',round(dur,2),'words',len(script.split()),flush=True)
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','2','-i',str(TMP/f'slide_{i:02}.png'),'-i',str(TMP/f'voice_{i:02}.wav'),'-vf','fps=5,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','28','-c:a','aac','-b:a','96k','-shortest',str(TMP/f'part_{i:02}.mp4')],check=True)
(TMP/'concat.txt').write_text(''.join(f"file 'part_{i:02}.mp4'\n" for i in range(1,len(chapters)+1)))
output=DOCS/'YGF_OWASP_2026_Demo.mp4'
subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(TMP/'concat.txt'),'-c','copy',str(output)],check=True)
print('demo',output,'size',output.stat().st_size)
