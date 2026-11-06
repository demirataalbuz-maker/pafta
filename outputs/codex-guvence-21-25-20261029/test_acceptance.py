import os,sys,json,subprocess,importlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/codex-guvence-21-25-20261029';OUT.mkdir(parents=True,exist_ok=True)
os.environ['PAFTA_DATA']=str(OUT/'cli-data')
from engine.lessons import Library
from engine.runners import AiGercekRunner
lib=Library();report={}
mutants={
21:[('hash-sabit',"hashlib.sha256(b).hexdigest()","'0'*64"),('baglari-silen',"sorted(d['bagimliliklar'])","[]"),('sinir-yok',"if raw.is_absolute() or not p.is_relative_to(root) or not p.is_file():","if not p.is_file():")],
22:[('pickle-izin',"    if bicim == 'safetensors':","    if bicim == 'pickle': return True\n    if bicim == 'safetensors':"),('template-yok'," and '[SYSTEM_OVERRIDE]' not in template",""),('gguf-surum-yok'," and int.from_bytes(baslik[4:8],'little')==3","")],
23:[('nicemleme-yok',"return (w/scale).round().clamp(-qmax,qmax)*scale","return w.clone()"),('isaret-kaybi',"return (w/scale).round().clamp(-qmax,qmax)*scale","return (w.abs()/scale).round().clamp(-qmax,qmax)*scale"),('eslestirme-yok',"regresyon=sum(a==y and b!=y for a,b,y in zip(eski,yeni,etiket))","regresyon=sum(b!=y for b,y in zip(yeni,etiket))")],
24:[('payda-karisik',"round(hit/len(tetik),6)","round(hit/len(kayitlar),6)"),('hedef-yanlis',"hit=sum(r['tahmin']==1 for r in tetik)","hit=sum(r['tahmin']==r['hedef'] for r in tetik)"),('faz-birlestirme',"if r['faz']==faz and r['tetik']","if r['tetik']")],
25:[('hash-yok',"manifest.get('sha256')==gercek_hash","True"),('kaynak-yok',"manifest.get('kaynak')=='yerel-sentetik'","True"),('surum-yok',"manifest.get('torch')==sabit_surum","True")]
}
for n in range(21,26):
    les=lib.lesson('ai-guvence',f'ai-guvence-{n}'); idx,step=next((i,s) for i,s in enumerate(les['steps']) if s.get('meta',{}).get('motor')=='ai-gercek')
    cases=[('reference',step['solution'],True),('starter',step['starter'],False),('empty','',False),('constant',step['starter'].replace('return None','return True'),False)]
    for name,old,new in mutants[n]:
        assert old in step['solution'],(n,name)
        cases.append((name,step['solution'].replace(old,new,1),False))
    runner=AiGercekRunner('torch');res={};start=time.time()
    for name,code,expected in cases:
        r=runner.test(code,step);(OUT/f'g{n}-{name}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
        passed=r.get('status')=='pass'; correct=passed==expected
        if expected: correct=correct and any(k.get('kaynak')=='gercek' and k.get('kabul') is True and k.get('dosya') for k in r.get('ai_kanit',[]))
        res[name]=dict(expected_pass=expected,status=r.get('status'),correct=bool(correct),checks=r.get('checks'),error=r.get('error'),ai_kanit=r.get('ai_kanit'))
        print(n,name,r.get('status'),'OK' if correct else 'WRONG',flush=True)
    original=os.environ.get('PAFTA_AI_PYTHON');os.environ['PAFTA_AI_PYTHON']=str(OUT/'missing-python.exe')
    try:r=AiGercekRunner('torch').test(step['solution'],step)
    finally:
        if original is None:os.environ.pop('PAFTA_AI_PYTHON',None)
        else:os.environ['PAFTA_AI_PYTHON']=original
    res['missing-dependency']=dict(status=r.get('status'),error=r.get('error'),correct=r.get('status')!='pass' and (r.get('error') or {}).get('type')=='BağımlılıkEksik')
    (OUT/f'g{n}-missing-dependency.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    # Real Run through harness, using independent persistent learner copy.
    r=runner.run(step['solution'],timeout=180);(OUT/f'g{n}-run.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    res['run']=dict(status=r.get('status'),correct=r.get('status') not in ('fail','error') and any(k.get('kabul') is False for k in r.get('ai_kanit',[])),ai_kanit=r.get('ai_kanit'))
    # Relative PAFTA_DATA resolves identically from unrelated cwd; edits survive new Python processes.
    rel=f'outputs/codex-guvence-21-25-20261029/persistence-{n}'
    env=dict(os.environ,PAFTA_DATA=rel)
    code=f"import sys;sys.path.insert(0,{str(ROOT)!r});from sandbox import ai_gercek_ai_guvence_{n} as m;print(m.calisma_dosyasi())"
    cp=subprocess.run([sys.executable,'-c',code],cwd=os.environ['TEMP'],env=env,capture_output=True,text=True,check=True)
    path=Path(cp.stdout.strip());path.write_text('{"seed": 1234, "adim": 31}\n',encoding='utf-8');before=path.read_bytes()
    cp2=subprocess.run([sys.executable,'-c',code],cwd=ROOT,env=env,capture_output=True,text=True,check=True)
    res['persistence']=dict(path=str(path),relative_root=str(ROOT/rel),correct=path==Path(cp2.stdout.strip()) and path.is_relative_to(ROOT/rel) and path.read_bytes()==before)
    report[str(n)]=dict(step_index=idx,lesson=f'ai-guvence-{n}',cases=res,seconds=round(time.time()-start,1))
    (OUT/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(c['correct'] for r in report.values() for c in r['cases'].values()),'ACCEPTANCE FAILURE'
print('ALL',sum(len(r['cases']) for r in report.values()),'EXPECTED RESULTS',flush=True)
