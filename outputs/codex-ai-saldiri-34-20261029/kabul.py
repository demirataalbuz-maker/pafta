import os,sys,json,time
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab');sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/codex-ai-saldiri-34-20261029';OUT.mkdir(exist_ok=True);os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import get,for_step
st=next(v for v in Library().lesson('ai-saldiri','ai-saldiri-34')['steps'] if v.get('meta',{}).get('motor')=='ai-gercek');r=for_step(get('python'),st);sol=st['solution']
cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant','def mesaj_akis_ozeti(*a): return {}\ndef chat_sablonu_render(*a,**kw): return ""\ndef sablon_regresyon_raporu(*a): return []',False)]
for name,a,b in [('late-system-allowed','if rol == "system" and (indeks != 0 or "system" in roller):','if False:'),('start-marker-unescaped','.replace("<|im_start|>", "< |im_start|>")',''),('hash-from-wrong-template','"chatml_sha256": hashlib.sha256(chatml).hexdigest()','"chatml_sha256": hashlib.sha256(kose).hexdigest()')]:
    assert a in sol,a;cases.append((name,sol.replace(a,b),False))

rows=[]
for name,code,expected in cases:
    t=time.time();res=r.test(code,st);yes=res.get('status')=='pass' and any(v.get('kabul') is True for v in res.get('ai_kanit',[])) if expected else res.get('status')=='fail'
    row={'name':name,'okay':yes,'seconds':round(time.time()-t,2),'result':res};rows.append(row);(OUT/(name+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print(name,res.get('status'),yes,flush=True)
res=r.run(sol);good=res.get('status')=='ok' and any(v.get('kabul') is False for v in res.get('ai_kanit',[]));rows.append(dict(name='run',okay=good,result=res));print('run',res.get('status'),good,flush=True)
os.environ['PAFTA_OLLAMA_HOST']='http://127.0.0.1:9';os.environ['PAFTA_OLLAMA_EXE']=str(OUT/'eksik.exe')
res=r.test(sol,st);good=res.get('status') in ('fail','error') and not any(v.get('kabul') is True for v in res.get('ai_kanit',[]));rows.append(dict(name='missing-dependency',okay=good,result=res));print('missing-dependency',res.get('status'),good,flush=True)
(OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');raise SystemExit(not all(v['okay'] for v in rows))
