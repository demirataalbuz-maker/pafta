import os,sys,json,time,copy,tempfile
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab');sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/codex-ai-saldiri-04-20261029';OUT.mkdir(exist_ok=True)
os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import get,for_step
st=next(s for s in Library().lesson('ai-saldiri','ai-saldiri-04')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek')
r=for_step(get('python'),st);sol=st['solution']
cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant','def taktikleri_bul(x): return []\ndef vakalari_siniflandir(x): return []\ndef siniflandirma_olc(*a): return {}\ndef vaka_dosyasini_oku(*a): return []',False)]
for name,a,b in [('single-label','"etiketler":sorted(etiketler)','"etiketler":sorted(etiketler)[:1]'),('zero-instead-none','if tp + fp else None','if tp + fp else 0.0'),('skip-lines','for satir in Path(yol).read_text(encoding="utf-8").splitlines():','for satir in Path(yol).read_text(encoding="utf-8").splitlines()[:1]:'),('ignore-unknown','or e not in etiketler','or False')]:
    assert a in sol,a
    cases.append((name,sol.replace(a,b),False))
rows=[]
for name,code,expected in cases:
    start=time.time();res=r.test(code,st)
    good=res.get('status')=='pass' and any(v.get('kaynak')=='gercek' and v.get('kabul') is True for v in res.get('ai_kanit',[])) if expected else res.get('status')=='fail'
    row={'name':name,'okay':good,'seconds':round(time.time()-start,2),'result':res};rows.append(row)
    (OUT/(name+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,res.get('status'),good,flush=True)
    if not good:print(json.dumps(res,ensure_ascii=False)[:1600],flush=True)
# Kalıcılık doğrulaması gerçek dosya ile; canlı model kabulü değildir.
from sandbox import ai_gercek_ai_saldiri_04 as lab
p=lab.calisma_dosyasi();original=p.read_text(encoding='utf-8');edited=original+'\n'
p.write_text(edited,encoding='utf-8');again=lab.calisma_dosyasi()
assert again==p and again.read_text(encoding='utf-8')==edited
p.write_text(original,encoding='utf-8')
(OUT/'file-contract.json').write_text(json.dumps({'kaynak':'fixture','kalicilik':True,'ogrenci_kopyasi':str(p),'sablon_degismedi':lab.ORNEK.read_text(encoding='utf-8')==original},ensure_ascii=False,indent=2),encoding='utf-8')
res=r.run(sol);good=res.get('status')=='ok' and any(v.get('kabul') is False for v in res.get('ai_kanit',[]))
rows.append({'name':'run','okay':good,'result':res});print('run',res.get('status'),good,flush=True)
# Eksik gerçek bağımlılık kabul sayılmamalı.
os.environ['PAFTA_OLLAMA_EXE']=str(OUT/'olmayan-ollama.exe')
os.environ['PAFTA_OLLAMA_HOST']='http://127.0.0.1:9'
res=r.test(sol,st);good=res.get('status') in ('fail','error') and not any(v.get('kabul') is True for v in res.get('ai_kanit',[]))
rows.append({'name':'dependency-missing','okay':good,'result':res});print('dependency-missing',res.get('status'),good,flush=True)
(OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(not all(x['okay'] for x in rows))
