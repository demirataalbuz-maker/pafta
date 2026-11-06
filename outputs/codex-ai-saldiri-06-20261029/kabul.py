import json,os,sys,time
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab');sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/codex-ai-saldiri-06-20261029';OUT.mkdir(exist_ok=True)
os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import get,for_step
st=next(s for s in Library().lesson('ai-saldiri','ai-saldiri-06')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek')
r=for_step(get('python'),st);sol=st['solution']
cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant','def sizinti_sinyalleri(*a): return []\ndef guvenli_kayit(x,*a): return x\ndef cikarim_raporu(*a): return {}',False)]
for name,a,b in [('normal-missing','if normal_gizli in normal_yanit:','if False:'),('casefold-base64','if kod in yanit or kod.rstrip("=") in yanit:','if kod.casefold() in yanit.casefold() or kod.rstrip("=").casefold() in yanit.casefold():'),('shallow-redaction','return [temizle(x) for x in deger]','return list(deger)'),('count-signals','rapor[yontem]["sizinti"] += 1','rapor[yontem]["sizinti"] += len(sinyaller)')]:
    assert a in sol,a
    cases.append((name,sol.replace(a,b),False))
rows=[]
for name,code,expected in cases:
    start=time.time();res=r.test(code,st)
    actual=res.get('status')=='pass' and any(e.get('kaynak')=='gercek' and e.get('kabul') is True for e in res.get('ai_kanit',[]))
    okay=actual if expected else res.get('status')=='fail'
    row={'name':name,'okay':okay,'seconds':round(time.time()-start,2),'result':res};rows.append(row)
    (OUT/(name+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,res.get('status'),okay,flush=True)
    if not okay:print(json.dumps(res,ensure_ascii=False)[:2000],flush=True)
res=r.run(sol);okay=res.get('status')=='ok' and any(e.get('kaynak')=='gercek' and e.get('kabul') is False for e in res.get('ai_kanit',[]))
rows.append({'name':'run','okay':okay,'result':res})
print('run',res.get('status'),okay,flush=True)
(OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(not all(x['okay'] for x in rows))
