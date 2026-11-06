import json,os,sys
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab');sys.path.insert(0,str(ROOT))
from engine.lessons import Library
from engine.runners import get,for_step
st=next(x for x in Library().lesson('ai-saldiri','ai-saldiri-06')['steps'] if x.get('meta',{}).get('motor')=='ai-gercek')
r=for_step(get('python'),st)
rows=[]
for name,env in [('promptfoo-missing',{'PAFTA_PROMPTFOO_EXE':'C:/pafta-no-such-file/entrypoint.js'}),('ollama-missing',{'PAFTA_OLLAMA_HOST':'127.0.0.1:9','PAFTA_OLLAMA_EXE':'C:/pafta-no-such-file/ollama.exe'})]:
    old={k:os.environ.get(k) for k in env};os.environ.update(env)
    res=r.test(st['solution'],st)
    for k,v in old.items():
        if v is None:os.environ.pop(k,None)
        else:os.environ[k]=v
    okay=res.get('status')=='fail' and not any(x.get('kabul') for x in res.get('ai_kanit',[]))
    print(name,res['status'],okay)
    rows.append({'name':name,'okay':okay,'result':res})
p=ROOT/'outputs/codex-ai-saldiri-06-20261029/dependency-cases.json';p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
sys.exit(not all(x['okay'] for x in rows))

