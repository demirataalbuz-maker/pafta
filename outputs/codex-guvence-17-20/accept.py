import os,sys,json,time,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));os.chdir(ROOT)
os.environ['PAFTA_DATA']=str(ROOT/'outputs/codex-guvence-17-20/cli-data')
from engine.lessons import Library
from engine.runners import for_step,get
from sandbox import ai_gercek_ai_guvence_17_20 as lab
out=ROOT/'outputs/codex-guvence-17-20';report={}
spec=json.loads((out/'mutation-spec.json').read_text(encoding='utf-8'))
for n in range(17,21):
    lid=f'ai-guvence-{n}';lesson=Library().lesson('ai-guvence',lid);st=lesson['steps'][7];runner=for_step(get('python'),st)
    cases=[('reference',st['solution'],True),('starter',st['starter'],False),('empty','',False),('constant',st['solution'].split('def olc')[0]+'def olc(*args):\n    return {}\ndef butce(*args):\n    return 0\n',False)]
    for i,(old,new) in enumerate(spec[str(n)]):
        assert old in st['solution'];cases.append((f'mutant-{i+1}',st['solution'].replace(old,new,1),False))
    rr=[]
    for name,code,want in cases:
        start=time.time();res=runner.test(code,st);good=(res['status']=='pass')==want
        if want:good=good and any(k.get('kabul') and k.get('kaynak')=='gercek' for k in res.get('ai_kanit',[]))
        row=dict(case=name,expected_pass=want,ok=good,seconds=round(time.time()-start,2),result=res);rr.append(row);print(lid,name,res['status'],'OK' if good else 'BAD',flush=True)
    saved=os.environ.get('PAFTA_AI_PYTHON');os.environ['PAFTA_AI_PYTHON']=str(out/'missing-python.exe')
    res=runner.test(st['solution'],st)
    rr.append(dict(case='missing-dependency',ok=res['status']!='pass' and res.get('error',{}).get('type')=='BağımlılıkEksik',result=res))
    if saved is None:os.environ.pop('PAFTA_AI_PYTHON')
    else:os.environ['PAFTA_AI_PYTHON']=saved
    # Relative PAFTA_DATA belongs to project, never temp runner cwd; edited copy must survive.
    saved_data=os.environ['PAFTA_DATA'];os.environ['PAFTA_DATA']='outputs/codex-guvence-17-20/persistence'
    p=lab.calisma_dosyasi(n);p.write_text('{"seed": 991, "ornek": 11, "sigma": 3}',encoding='utf-8');before=p.read_bytes()
    again=lab.calisma_dosyasi(n)
    rr.append(dict(case='persistent-edited-copy-relative-root',ok=p==again and p.is_relative_to(ROOT) and before==again.read_bytes(),path=str(p)))
    os.environ['PAFTA_DATA']=saved_data
    report[lid]=rr
    (out/'cli-acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL',sum(r['ok'] for rows in report.values() for r in rows),'/',sum(len(rows) for rows in report.values()),flush=True)
sys.exit(0 if all(r['ok'] for rows in report.values() for r in rows) else 1)
