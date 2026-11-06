import json, os, sys, time
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab'); sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs'/'codex-ai-saldiri-05-20261029'; OUT.mkdir(exist_ok=True)
os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import for_step, get
st=next(x for x in Library().lesson('ai-saldiri','ai-saldiri-05')['steps'] if x.get('meta',{}).get('motor')=='ai-gercek')
r=for_step(get('python'),st);sol=st['solution']
cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant','def set_imzala(x): return [], "x"\ndef asr_olc(*a): return {}',False)]
for name,a,b in [('noncanonical','ensure_ascii=False, sort_keys=True, separators=(",", ":")','ensure_ascii=True'),('wrong-denominator','rapor["basari"] / rapor["gecerli_saldiri"]','rapor["basari"] / rapor["deneme"]'),('silent-control','if durum == "basarisiz":','if True:')]:
    assert a in sol,a
    cases.append((name,sol.replace(a,b),False))
rows=[]
for name,code,expected in cases:
    t=time.time();res=r.test(code,st)
    actual=res.get('status')=='pass' and any(e.get('kaynak')=='gercek' and e.get('kabul') for e in res.get('ai_kanit',[]))
    okay=actual if expected else res.get('status')=='fail'
    rows.append({'name':name,'okay':okay,'seconds':round(time.time()-t,2),'result':res})
    print(name,res.get('status'),okay,flush=True)
    (OUT/(name+'.json')).write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
res=r.run(sol);rows.append({'name':'run','okay':res.get('status')=='ok' and any(e.get('kaynak')=='gercek' and not e.get('kabul') for e in res.get('ai_kanit',[])),'result':res})
(OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('run',res.get('status'),rows[-1]['okay'],flush=True)
sys.exit(0 if all(x['okay'] for x in rows) else 1)
