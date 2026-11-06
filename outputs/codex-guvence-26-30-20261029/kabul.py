from pathlib import Path
import sys,os,json,time,subprocess
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
OUT=Path(__file__).resolve().parent
os.environ['PAFTA_DATA']=str(OUT/'data')
from engine.lessons import Library
from engine.runners import get,for_step
MUTANTS={26:[('gradient-reversed','+eps*grad.sign()','-eps*grad.sign()'),('clipping-missing',').clamp(0,1)',')'),('lr-difference-hidden',"degisen=['lr'] if r['lr']!=base['lr'] else []","degisen=[]")],27:[('temperature-ignored','(logits/t).softmax','logits.softmax'),('all-correct','correct=(pred==labels).float()','correct=(pred==pred).float()'),('ece-unweighted','float(mask.float().mean())*abs','1.*abs')],29:[('first-secret-only',"text.replace(canary,'[MASKELI]')","text.replace(canary,'[MASKELI]',1)"),('secret-preserved',"text.replace(canary,'[MASKELI]')","text"),('hash-not-bytes','hashlib.sha256(p.read_bytes()).hexdigest()',"hashlib.sha256(p.name.encode()).hexdigest()")],30:[('always-allow','return confidence>=threshold','return True'),('strict-threshold','return confidence>=threshold','return confidence>threshold'),('hidden-false-effect',"sum(r['izin'] and not r['dogru'] for r in rs)","0")]}
allrows=[]
for n in ([int(x) for x in sys.argv[1:]] or [26,27,29,30]):
    lid=f'ai-guvence-{n}';st=next(s for s in Library().lesson('ai-guvence',lid)['steps'] if s.get('meta',{}).get('motor')=='ai-gercek');r=for_step(get('python'),st);sol=st['solution']
    import re
    funcs=re.findall(r'^def (\w+)\(',sol,re.M)
    constant='\n'.join(f'def {f}(*a): return {{}}' for f in funcs)
    cases=[('reference',sol,True),('starter',st['starter'],False),('empty','',False),('constant',constant,False)]
    for name,old,new in MUTANTS[n]:
        assert old in sol,(n,old)
        cases.append((name,sol.replace(old,new,1),False))
    for name,code,expected in cases:
        start=time.time();res=r.test(code,st);actual=res.get('status')=='pass' and any(k.get('kabul') is True for k in res.get('ai_kanit',[]));okay=actual==expected
        row=dict(lesson=lid,name=name,okay=okay,seconds=round(time.time()-start,2),result=res);allrows.append(row)
        (OUT/f'{n}-{name}.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print(n,name,res.get('status'),okay,flush=True)
    res=r.run(sol);okay=res.get('status')=='ok' and bool(res.get('ai_kanit'));allrows.append(dict(lesson=lid,name='run',okay=okay,result=res));print(n,'run',res.get('status'),okay,flush=True)
    old=os.environ.get('PAFTA_AI_PYTHON');os.environ['PAFTA_AI_PYTHON']=str(OUT/'missing-python.exe')
    try:res=r.test(sol,st)
    finally:
        if old is None:os.environ.pop('PAFTA_AI_PYTHON',None)
        else:os.environ['PAFTA_AI_PYTHON']=old
    okay=res.get('status')!='pass' and (res.get('error') or {}).get('type')=='BağımlılıkEksik';allrows.append(dict(lesson=lid,name='missing-dependency',okay=okay,result=res));print(n,'missing-dependency',res.get('status'),okay,flush=True)
(OUT/('cli-summary-'+('-'.join(sys.argv[1:]))+'.json' if sys.argv[1:] else 'cli-summary.json')).write_text(json.dumps(allrows,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(not all(x['okay'] for x in allrows))
