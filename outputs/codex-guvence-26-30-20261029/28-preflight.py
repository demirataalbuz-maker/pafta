from pathlib import Path
import os,sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
from sandbox import ai_gercek_ai_guvence_28 as m
from engine.lessons import Library
sol=next(s for s in Library().lesson('ai-guvence','ai-guvence-28')['steps'] if s.get('meta',{}).get('motor')=='ai-gercek')['solution'];ns={};exec(sol.split('import ai_lab')[0],ns)
# Read-only local inventory, never enters a model session.
inventory=m.lab._istek(m.lab._adres(),'/api/tags',sure=5);(OUT/'28-installed-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for name,c in [('missing-installed-model',dict(opt_in=True,kucuk='pafta-nonexistent-no-download',guclu='qwen3:8b',max_calls=8,max_model_bytes=5500000000)),('model-size-budget',dict(opt_in=True,kucuk='qwen3:4b-instruct-2507-q4_K_M',guclu='qwen3:8b',max_calls=8,max_model_bytes=1))]:
    p=OUT/(name+'.json');p.write_text(json.dumps(c),encoding='utf-8')
    try:
        m.deney(ns['karsilastirma_plani'],ns['karsilastirma_skoru'],ns['karsilastirma_ozeti'],p,OUT/'never-created');rows.append(dict(name=name,okay=False))
    except m.lab.GercekLabYok as e:rows.append(dict(name=name,okay=True,error=str(e),model_calls=0))
(OUT/'28-preflight.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print(rows)
raise SystemExit(not all(r['okay'] for r in rows))
