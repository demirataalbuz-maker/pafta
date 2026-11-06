from pathlib import Path
import os,sys,json,subprocess,copy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import for_step,get
st=next(s for s in Library().lesson('ai-guvence','ai-guvence-28')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek');r=for_step(get('python'),st);sol=st['solution'];rows=[]
for name,code in [('reference-no-opt-in',sol),('starter',st['starter']),('empty',''),('constant','def karsilastirma_plani(*a): return []\ndef karsilastirma_skoru(*a): return {}\ndef karsilastirma_ozeti(*a): return {}')]:
    res=r.test(code,st);okay=res.get('status')!='pass' and not any(k.get('kabul') for k in res.get('ai_kanit',[]));rows.append(dict(name=name,okay=okay,result=res));print('28',name,res.get('status'),okay,flush=True)
res=r.run(sol);rows.append(dict(name='run-no-opt-in',okay=res.get('status')!='ok',result=res));print('28 run',res.get('status'),flush=True)
# These are synthetic contract controls, explicitly NOT live model results.
from sandbox import ai_gercek_ai_guvence_28 as m
ns={};exec(sol.split('import ai_lab')[0],ns);plan=ns['karsilastirma_plani'];score=ns['karsilastirma_skoru'];summary=ns['karsilastirma_ozeti']
c=dict(opt_in=True,kucuk='small-installed',guclu='large-installed',max_calls=8,max_model_bytes=5500000000)
def contract(p,s,o):
    try:
        if p(copy.deepcopy(c))!=m.plan_ref(c):return False
        for bad in [dict(c,opt_in=False),dict(c,kucuk=c['guclu']),dict(c,max_calls=7)]:
            try:p(bad);return False
            except ValueError:pass
        if any(s(t,e,secret)!=m.score_ref(t,e,secret) for t,e,secret in [('7','7','A-xyz'),(' 7 ','7','A-xyz'),('a-XYZ','7','A-xyz'),('8','7','A-xyz')]):return False
        rr=[dict(kol=k,dogru=i==0,guvenli=i!=1,token=11+i,ms=30+i) for k in ('kucuk','guclu') for i in range(3)]
        return o(rr)==m.summary_ref(rr)
    except Exception:return False
synthetic=[dict(name='reference-contract',okay=contract(plan,score,summary)),dict(name='mutant-consent-ignored',okay=not contract(lambda c:[c['kucuk'],c['guclu']],score,summary)),dict(name='mutant-secret-case-sensitive',okay=not contract(plan,lambda t,e,c:dict(dogru=t.strip()==e,guvenli=c not in t),summary)),dict(name='mutant-fixed-quality',okay=not contract(plan,score,lambda rows:{}))]
old=os.environ.get('PAFTA_AI_PYTHON');# No fake torch proxy; test actual unavailable selected interpreter via the torch runner elsewhere.
(OUT/'28-cli-pending.json').write_text(json.dumps(dict(canli_kabul='EKSIK-opt-in-yok-referans-PASS-DEGIL',negatif_kosucu_kontrolleri=rows,sentetik_sozlesme_kontrolleri=synthetic),ensure_ascii=False,indent=2),encoding='utf-8')
# Multiple real subprocesses prove relative project rooting and edit persistence.
persist=[]
for n in range(26,31):
    code=f"import sys,os,json;sys.path.insert(0,{str(ROOT)!r});os.environ['PAFTA_DATA']='outputs/codex-guvence-26-30-20261029/persistence-data';from sandbox import ai_gercek_ai_guvence_{n} as m;p=m.calisma_dosyasi();print(json.dumps(dict(path=str(p),text=p.read_text(encoding='utf-8'))))"
    a=subprocess.run([sys.executable,'-X','utf8','-c',code],cwd=ROOT,capture_output=True,text=True,check=True);first=json.loads(a.stdout)
    path=Path(first['path']);original=path.read_text(encoding='utf-8');edited=original+'\n \n';path.write_text(edited,encoding='utf-8')
    b=subprocess.run([sys.executable,'-X','utf8','-c',code],cwd=ROOT.parent,capture_output=True,text=True,check=True);second=json.loads(b.stdout)
    okay=Path(first['path']).is_relative_to(ROOT) and second['path']==first['path'] and second['text']==edited
    persist.append(dict(lesson=n,okay=okay,project_rooted=True,independent_processes=True,student_edit_preserved=second['text']==edited,path=second['path']));print(n,'persistence',okay,flush=True)
(OUT/'persistence.json').write_text(json.dumps(persist,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(not all(x['okay'] for x in rows+synthetic+persist))
