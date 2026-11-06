import os,sys,json,urllib.request,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/codex-guvence-21-25-20261029'
os.environ['PAFTA_DATA']=str(OUT/'cli-data')
from engine.lessons import Library
from engine.runners import AiGercekRunner
lib=Library();result={}
for n in range(21,26):
    module=__import__('sandbox.ai_gercek_ai_guvence_'+str(n),fromlist=['calisma_dosyasi'])
    p=module.calisma_dosyasi();p.write_text(json.dumps(dict(seed=1234+n,adim=31)),encoding='utf-8');before=p.read_bytes()
    s=next(s for s in lib.lesson('ai-guvence',f'ai-guvence-{n}')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek')
    r=AiGercekRunner('torch').run(s['solution'],timeout=180)
    (OUT/f'g{n}-run-edited.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    evidence=[k for k in r.get('ai_kanit',[]) if k.get('kabul') is False and k.get('dosya')]
    raw=json.loads(Path(evidence[0]['dosya']).read_text(encoding='utf-8')) if evidence else {}
    try:
        data=urllib.request.urlopen(f'http://127.0.0.1:18800/data/ai-guvence-{n}-deney.txt',timeout=20).read()
        visible=dict(served=True,matches=data==(ROOT/f'web/data/ai-guvence-{n}-deney.txt').read_bytes(),sha256=hashlib.sha256(data).hexdigest())
    except Exception as e:visible=dict(served=False,error=str(e))
    ok=r.get('status') not in ('fail','error') and raw.get('egitim',{}).get('seed')==1234+n and raw.get('egitim',{}).get('adim')==31 and p.read_bytes()==before
    result[str(n)]=dict(correct=ok,student_path=str(p),seed=1234+n,adim=31,ai_kanit=evidence,visible=visible)
    (OUT/'edited-run-and-visible.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(n,'EDITED RUN',ok,'VISIBLE',visible,flush=True)
assert all(r['correct'] for r in result.values())
