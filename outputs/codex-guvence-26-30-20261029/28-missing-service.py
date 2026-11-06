from pathlib import Path
import sys,os,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
os.environ['PAFTA_DATA']=str(OUT/'28-optin-data');os.environ['PAFTA_OLLAMA_HOST']='http://127.0.0.1:9';os.environ['PAFTA_OLLAMA_EXE']=str(OUT/'not-installed.exe')
from engine.lessons import Library
from engine.runners import for_step,get
st=next(s for s in Library().lesson('ai-guvence','ai-guvence-28')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek');r=for_step(get('python'),st);res=r.test(st['solution'],st);good=res.get('status')!='pass' and not any(v.get('kabul') for v in res.get('ai_kanit',[]));(OUT/'28-missing-service.json').write_text(json.dumps(dict(okay=good,result=res),ensure_ascii=False,indent=2),encoding='utf-8');print('missing-service',res.get('status'),good);raise SystemExit(not good)
