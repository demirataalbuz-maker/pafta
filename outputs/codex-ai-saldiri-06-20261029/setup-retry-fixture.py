import json,sys,urllib.error
from unittest.mock import patch
from pathlib import Path
ROOT=Path(r'C:\Users\demo12\Documents\Pafta-AI-GercekLab');sys.path.insert(0,str(ROOT))
import sandbox.ai_gercek_lab as L;sys.modules['ai_lab']=L
from sandbox.ai_gercek_ai_saldiri_06 import ExtractionSession,OzelCpuOturumu
rows=[]
for name,errors,want_calls,want_ok in [('transient-then-ready',[urllib.error.URLError('fixture timeout'),None],2,True),('persistent',[urllib.error.URLError('fixture timeout')]*2,2,False),('http404',[urllib.error.HTTPError('http://127.0.0.1',404,'fixture',{},None)],1,False)]:
    count=[0]
    def fake(self):
        index=count[0];count[0]+=1;e=errors[index]
        if e:raise e
        return 'ready'
    session=ExtractionSession();okay=True;ready=False
    with patch.object(OzelCpuOturumu,'_model_sec',fake):
        try:ready=session._model_sec()=='ready'
        except L.GercekLabYok:pass
    okay=ready==want_ok and count[0]==want_calls and len(session.kayit.get('hazirlik_yeniden_denemeleri',[]))==sum(e is not None for e in errors)
    rows.append({'case':name,'okay':okay,'calls':count[0],'recorded':session.kayit.get('hazirlik_yeniden_denemeleri',[])})
print(json.dumps({'kaynak':'fixture','realModelAcceptance':False,'results':rows},ensure_ascii=False))
raise SystemExit(not all(x['okay'] for x in rows))
