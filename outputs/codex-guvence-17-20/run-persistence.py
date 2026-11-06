from pathlib import Path
import os,sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));os.chdir(ROOT)
os.environ['PAFTA_DATA']='outputs/codex-guvence-17-20/persistence'
from engine.lessons import Library
from engine.runners import for_step,get
out=ROOT/'outputs/codex-guvence-17-20';report={}
for n in range(17,21):
    st=Library().lesson('ai-guvence',f'ai-guvence-{n}')['steps'][7]
    p=ROOT/os.environ['PAFTA_DATA']/'calisma'/f'ai-guvence-{n}'/'ayarlar.json'
    p.parent.mkdir(parents=True,exist_ok=True)
    try:
        with p.open('x',encoding='utf-8') as f:f.write('{"seed": 991, "ornek": 11, "sigma": 3}')
    except FileExistsError:pass
    before=p.read_bytes();res=for_step(get('python'),st).run(st['solution'],timeout=180)
    evidence=[json.loads(Path(e['dosya']).read_text(encoding='utf-8')) for e in res.get('ai_kanit',[]) if e.get('dosya')]
    good=not res.get('error') and len(evidence)==1 and evidence[0]['kaynak']=='gercek' and evidence[0]['mod']=='run' and evidence[0]['kabul'] is False and evidence[0]['ayarlar']==json.loads(before) and p.read_bytes()==before
    report[str(n)]=dict(ok=good,persistent_path=str(p),result=res)
    (out/'cli-run-persistence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(n,res['status'],good,flush=True)
sys.exit(0 if all(x['ok'] for x in report.values()) else 1)
