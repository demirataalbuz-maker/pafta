from pathlib import Path
import sys,os,json,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
# Only this acceptance directory opts in. Never touches a real student/UI directory.
os.environ['PAFTA_DATA']=str(OUT/'28-optin-data')
from engine.lessons import Library
from engine.runners import for_step,get
from sandbox import ai_gercek_ai_guvence_28 as m
p=m.calisma_dosyasi();c=m.izin_config(p);c['opt_in']=True;p.write_text(json.dumps(c,indent=2),encoding='utf-8')
st=next(s for s in Library().lesson('ai-guvence','ai-guvence-28')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek');r=for_step(get('python'),st);sol=st['solution']
cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant','def karsilastirma_plani(*a): return []\ndef karsilastirma_skoru(*a): return {}\ndef karsilastirma_ozeti(*a): return {}',False)]
for name,a,b in [('consent-ignored',"if c['opt_in'] is not True:raise ValueError('Acik model calistirma onayi yok')",'if False:raise ValueError()'),('secret-case-sensitive','canary.lower() not in text.lower()','canary not in text'),('token-count-hidden',"token=sum(r['token'] for r in rs)",'token=0')]:
    assert a in sol;cases.append((name,sol.replace(a,b,1),False))
rows=[]
for name,code,expected in cases:
    t=time.time();res=r.test(code,st);actual=res.get('status')=='pass' and any(k.get('kabul') for k in res.get('ai_kanit',[]));row=dict(name=name,okay=actual==expected,seconds=round(time.time()-t,2),result=res);rows.append(row);(OUT/f'28-live-{name}.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print('28',name,res.get('status'),row['okay'],flush=True)
res=r.run(sol);rows.append(dict(name='run',okay=res.get('status')=='ok' and bool(res.get('ai_kanit')),result=res));print('28 run',res.get('status'),rows[-1]['okay'],flush=True)
# Installed model absent is tested independently in 28-preflight.py, no downloads.
(OUT/'28-live-cli-summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(not all(x['okay'] for x in rows))
