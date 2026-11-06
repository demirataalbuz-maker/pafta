import os,sys,json,time
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab');sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/codex-ai-saldiri-08-20261029';OUT.mkdir(exist_ok=True);os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import get,for_step
st=next(v for v in Library().lesson('ai-saldiri','ai-saldiri-08')['steps'] if v.get('meta',{}).get('motor')=='ai-gercek');r=for_step(get('python'),st);sol=st['solution']
cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant','def hafiza_anahtari(*a): return ("a","b")\ndef hafiza_yaz(*a): return {}\ndef hafiza_oku(*a): return []',False)]
for name,a,b in [('merged-scope','return kullanici, oturum','return kullanici, "global"'),('role-promotion','tip="veri"','tip="system"'),('cross-session','return [dict(kayit) for kayit in hafiza.get((kullanici, oturum), [])]','return [dict(kayit) for (u,o),values in hafiza.items() if u == kullanici for kayit in values]')]:
    assert a in sol,a;cases.append((name,sol.replace(a,b),False))
rows=[]
for name,code,expected in cases:
    t=time.time();res=r.test(code,st);yes=res.get('status')=='pass' and any(v.get('kabul') is True for v in res.get('ai_kanit',[])) if expected else res.get('status')=='fail'
    row={'name':name,'okay':yes,'seconds':round(time.time()-t,2),'result':res};rows.append(row);(OUT/(name+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print(name,res.get('status'),yes,flush=True)
res=r.run(sol);good=res.get('status')=='ok' and any(v.get('kabul') is False for v in res.get('ai_kanit',[]));rows.append(dict(name='run',okay=good,result=res));print('run',res.get('status'),good,flush=True)
os.environ['PAFTA_OLLAMA_HOST']='http://127.0.0.1:9';os.environ['PAFTA_OLLAMA_EXE']=str(OUT/'eksik.exe')
res=r.test(sol,st);good=res.get('status') in ('fail','error') and not any(v.get('kabul') is True for v in res.get('ai_kanit',[]));rows.append(dict(name='missing-dependency',okay=good,result=res));print('missing-dependency',res.get('status'),good,flush=True)
(OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');raise SystemExit(not all(v['okay'] for v in rows))
