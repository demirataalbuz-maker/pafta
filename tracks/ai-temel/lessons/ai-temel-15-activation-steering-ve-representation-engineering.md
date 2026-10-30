---
id: ai-temel-15
title: "Activation Steering ve Representation Engineering"
summary: Sentetik aktivasyonlardan davranış yönü çıkar, ağırlıkları değiştirmeden yönelt ve müdahale normunu sınırla.
timeout: 45
---

::: anlat Davranış yönü aktivasyon farklarından çıkar
Representation engineering, seçilmiş davranış örneklerinin aktivasyonları arasındaki farkları yön vektörüne dönüştürür. Bu derste pozitif ve negatif örneklerin ortalaması alınır, fark vektörü birim uzunluğa normalize edilir. Küçük fixture gerçek model aktivasyonu değildir.

TransformerLens, PyTorch veya repeng çalıştırılmaz. Amaç yön çıkarma ile üretim sonucunu değiştirme arasındaki mekanik ilişkiyi görmek; yönün nedensel veya evrensel güvenlik garantisi olmadığını kabul etmektir.
:::

::: anlat Yöneltme ağırlık güncellemesi değildir
Activation steering çalışma sırasındaki aktivasyona yön vektörünün belirli katsayıyla katlanmasını ekler. Temel model ağırlıkları değişmez. Katsayının işareti ve büyüklüğü müdahalenin yönünü ve şiddetini belirler.

Sınırsız müdahale temsili bozabilir. Son görevde müdahalenin L2 normu bir üst sınırla kısıtlanır. Norm eşiğin üzerindeyse vektör eşiğe ölçeklenir; eşitlikte kırpma yapılmaz.
:::

::: tahmin Yön ve yöneltmeyi tahmin et
Üç çıktı satırını yaz:

```python
print([2 - 1, 0 - 0, 0 - 0])
print(round((2 ** 2) ** 0.5, 6))
print([round(1 + 0.5 * 2, 6), round(2 + 0.5 * 0, 6)])
```

???

```cikti
[1, 0, 0]
2.0
[2.0, 2.0]
```

İlk satır aktivasyon farkını, ikinci satır L2 normunu, üçüncü satır katsayılı yön eklemeyi gösterir.
:::

::: gorev 1 · Ortalama aktivasyon farkından birim yön çıkar
`yon_cikar(pozitif, negatif)` işlevini yaz. İki girdi de üç adet, üç sayılık vektör içeren listedir; bool değerler geçersizdir. Geçersiz veri veya sıfır fark normunda `ValueError` yükselt.

Her gruptaki vektörlerin öğe bazında ortalamasını al, pozitif ortalama eksi negatif ortalamayı hesapla ve farkı L2 normuna böl. Üç öğeli birim yönü altı ondalığa yuvarla. Girdileri değiştirme.

```starter
def yon_cikar(pozitif, negatif):
    return []
```

```test
P = [[2, 0, 0], [2, 0, 0], [2, 0, 0]]
N = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
def sozlesme(fn):
    try:
        if fn(P, N) != [1.0, 0.0, 0.0] or fn(N, P) != [-1.0, 0.0, 0.0]:
            return False
        p = [[1, 1, 0], [0, 1, 0], [1, 0, 0]]
        if fn(p, N) != [0.707107, 0.707107, 0.0] or fn([[3, 0, 0]] * 3, [[0, 1, 0]] * 3) != [0.948683, -0.316228, 0.0]:
            return False
        for args in [(None, N), (P[:2], N), ([[1, 0]] * 3, N), ([[1, True, 0]] * 3, N), (P, None), (P, N[:2]), (N, N)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yon_cikar), "ortalama fark, normalizasyon ve yön şeması korunmalı")
def m_pozitif(p, n):
    return yon_cikar(list(reversed(p)), n)
def m_negatif(p, n):
    return yon_cikar(p, [[x[0] + 1, x[1], x[2]] for x in n])
def m_boyut(p, n):
    return yon_cikar(p + p[:1], n)
for ad, mutant in [("pozitifi bozan", m_pozitif), ("negatifi bozan", m_negatif), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yon_cikar(pozitif, negatif):
    import math
    def grup(g):
        return isinstance(g, list) and len(g) == 3 and all(isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v) for v in g)
    if not grup(pozitif) or not grup(negatif):
        raise ValueError("aktivasyon grubu geçersiz")
    p = [sum(v[j] for v in pozitif) / 3 for j in range(3)]
    n = [sum(v[j] for v in negatif) / 3 for j in range(3)]
    fark = [p[j] - n[j] for j in range(3)]
    norm = math.sqrt(sum(x * x for x in fark))
    if norm == 0:
        raise ValueError("sıfır yön")
    return [round(x / norm, 6) for x in fark]
```

```hint
İki grubun ortalamasını ayrı hesapla, farkı çıkar; norm sıfır değilse her öğeyi norma böl.
```
:::

::: gorev 2 · Aktivasyona katsayılı yön ekle
`yonelt(aktivasyon, yon, katsayi)` işlevini yaz. Aktivasyon ve yön üç sayılık vektörlerdir. Katsayı bool olmayan -2 ile 2 arasında sayıdır; sınırlar dahildir. Geçersiz veride `ValueError` yükselt.

Her öğede `aktivasyon + katsayi*yon` hesapla ve altı ondalığa yuvarla. Yeni vektör döndür; girdileri değiştirme.

```starter
def yonelt(aktivasyon, yon, katsayi):
    return []
```

```test
def sozlesme(fn):
    try:
        if fn([1, 2, 3], [1, 0, -1], 0.5) != [1.5, 2.0, 2.5] or fn([1, 1, 1], [1, 1, 1], 0) != [1.0, 1.0, 1.0]:
            return False
        if fn([0, 0, 0], [1, 1, 1], 2) != [2.0, 2.0, 2.0] or fn([0, 0, 0], [1, 1, 1], -2) != [-2.0, -2.0, -2.0]:
            return False
        if fn([0, 0, 0], [1, 0, 0], 1 / 3) != [0.333333, 0.0, 0.0]:
            return False
        for args in [(None, [1, 0, 0], 1), ([1, 0], [1, 0, 0], 1), ([1, True, 0], [1, 0, 0], 1), ([1, 0, 0], None, 1), ([1, 0, 0], [1, 0, 0], 2.1), ([1, 0, 0], [1, 0, 0], -2.1), ([1, 0, 0], [1, 0, 0], True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yonelt), "katsayı, yön işareti ve aktivasyon şeması korunmalı")
def m_aktivasyon(a, y, k):
    return yonelt(list(reversed(a)), y, k)
def m_yon(a, y, k):
    return yonelt(a, list(reversed(y)), k)
def m_katsayi(a, y, k):
    return yonelt(a, y, k * 2)
for ad, mutant in [("aktivasyonu bozan", m_aktivasyon), ("yönü bozan", m_yon), ("katsayıyı bozan", m_katsayi)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yonelt(aktivasyon, yon, katsayi):
    def vektor(v):
        return isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    if not vektor(aktivasyon) or not vektor(yon):
        raise ValueError("vektör geçersiz")
    if not isinstance(katsayi, (int, float)) or isinstance(katsayi, bool) or not -2 <= katsayi <= 2:
        raise ValueError("katsayı geçersiz")
    return [round(a + katsayi * y, 6) for a, y in zip(aktivasyon, yon)]
```

```hint
İki vektörü `zip` ile eşle; her çiftte katsayılı yönü aktivasyona ekle.
```
:::

::: gorev 3 · Müdahale normunu eşikle sınırla
`sinirli_yoneltme(aktivasyon, yon, katsayi, esik)` işlevini yaz. Vektörler ve katsayı ikinci görevdeki biçimdedir. Eşik bool olmayan 0–4 arası sayıdır; sınırlar dahildir. Geçersiz veride `ValueError` yükselt.

Müdahale `katsayi*yon` vektörünün L2 normu eşiği aşıyorsa müdahaleyi eşik/norm oranıyla ölçekle; aşmıyorsa aynen kullan. Aktivasyona ekleyip altı ondalığa yuvarla. `{"vektor":V,"kirpildi":K}` döndür; K yalnız norm eşikten büyükse True olur.

```starter
def sinirli_yoneltme(aktivasyon, yon, katsayi, esik):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn([1, 0, 0], [1, 0, 0], 2, 1) != {"vektor": [2.0, 0.0, 0.0], "kirpildi": True}:
            return False
        if fn([1, 0, 0], [1, 0, 0], 1, 1) != {"vektor": [2.0, 0.0, 0.0], "kirpildi": False} or fn([1, 0, 0], [1, 0, 0], 1, 0) != {"vektor": [1.0, 0.0, 0.0], "kirpildi": True}:
            return False
        if fn([0, 0, 0], [0, 0, 0], 2, 0) != {"vektor": [0.0, 0.0, 0.0], "kirpildi": False} or fn([0, 0, 0], [1, 1, 1], 1, 1 / 3) != {"vektor": [0.19245, 0.19245, 0.19245], "kirpildi": True}:
            return False
        if fn([0, 0, 0], [1, 0, 0], -2, 4) != {"vektor": [-2.0, 0.0, 0.0], "kirpildi": False}:
            return False
        for args in [(None, [1, 0, 0], 1, 1), ([1, 0], [1, 0, 0], 1, 1), ([1, True, 0], [1, 0, 0], 1, 1), ([1, 0, 0], [1, 0], 1, 1), ([1, 0, 0], [1, True, 0], 1, 1), ([1, 0, 0], None, 1, 1), ([1, 0, 0], [1, 0, 0], 2.1, 1), ([1, 0, 0], [1, 0, 0], True, 1), ([1, 0, 0], [1, 0, 0], "1", 1), ([1, 0, 0], [1, 0, 0], 1, -0.1), ([1, 0, 0], [1, 0, 0], 1, 4.1), ([1, 0, 0], [1, 0, 0], 1, True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sinirli_yoneltme), "norm eşiği, kırpma kararı ve sıfır yön korunmalı")
def m_yon(a, y, k, e):
    return sinirli_yoneltme(a, list(reversed(y)), k, e)
def m_katsayi(a, y, k, e):
    return sinirli_yoneltme(a, y, k * 2, e)
def m_esik(a, y, k, e):
    return sinirli_yoneltme(a, y, k, 4)
for ad, mutant in [("yönü bozan", m_yon), ("katsayıyı bozan", m_katsayi), ("eşiği bozan", m_esik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def sinirli_yoneltme(aktivasyon, yon, katsayi, esik):
    import math
    def vektor(v):
        return isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    if not vektor(aktivasyon) or not vektor(yon):
        raise ValueError("vektör geçersiz")
    if not isinstance(katsayi, (int, float)) or isinstance(katsayi, bool) or not -2 <= katsayi <= 2:
        raise ValueError("katsayı geçersiz")
    if not isinstance(esik, (int, float)) or isinstance(esik, bool) or not 0 <= esik <= 4:
        raise ValueError("eşik geçersiz")
    mudahale = [katsayi * y for y in yon]
    norm = math.sqrt(sum(x * x for x in mudahale))
    kirpildi = norm > esik
    if kirpildi:
        mudahale = [x * esik / norm for x in mudahale]
    return {"vektor": [round(a + m, 6) for a, m in zip(aktivasyon, mudahale)], "kirpildi": kirpildi}
```

```hint
Norm eşikten büyükse bütün müdahale öğelerini aynı `esik/norm` oranıyla çarp; sıfır normda bölme yapma.
```
:::

::: anlat Gerçek deney: gerçek residual aktivasyona müdahale
Önceki yönler üç boyutlu hazır vektörlerdi. Şimdi kurulu SmolLM2 modelinin iki decoder katmanında gerçek metinlerden son-token aktivasyonları yakalanır. İki sentetik metin grubunun ortalamaları arasındaki fark normalize edilerek her katman için gerçek birim yön çıkarılır. Bu hazırlığı laboratuvar yapar ve yön tensörünü sana verir; yönler sabit fixture değildir.

Sen bu yönü gerçek model çalışırken forward hook ile yalnız **son tokenın** katman çıkışına ekleyeceksin. Müdahale, katsayı×yön olup L2 sınırını aşarsa ölçeklenir. Temel ağırlıklar güncellenmez; bütün tokenlara eklemek veya modeli eğitmek farklı işlemdir. Hook `finally` içinde kaldırılmalıdır; hata sonrası sonraki deneye sızan müdahale ciddi ölçüm hatasıdır.

Bu, bir aktivasyon müdahalesinin mekanik kabulüdür. Seçilen sentetik metinler “sakin/acil” örnekleridir; ortaya çıkan yönün evrensel anlam, refusal veya güvenlik yönü olduğu iddia edilmez. Müdahale sonrası argmax aynı kalabilir; belirli bir sözcük veya saldırı başarısı test şartı değildir. TransformerLens/repeng kullanılmaz; gerçek model ve PyTorch hookları kullanılır.
:::

::: gorev Gerçek deney · Ağırlıkları değiştirmeden son-token aktivasyonunu yönelt
`gercek_yonelt(tok, model, metin, yon, katman, katsayi, esik)` işlevini yaz. Laboratuvar sana gerçek tokenizer/model ve hedef katmandan türetilmiş sonlu, birim uzunlukta 1D `yon` tensörünü verir. `model.model.layers[katman]` hedef decoder katmanıdır. Bu modelin uyumlu kurulduğunu varsayabilirsin.

- `metin` boşluk dışı karakter içeren str ve gerçek tokenizer'la 1–24 token olmalıdır. Metni değiştirme.
- `katman` bool olmayan geçerli decoder indeksi; `katsayi` bool olmayan sonlu sayı, -2..2; `esik` bool olmayan sonlu sayı, 0..1. Diğer değerlerde `ValueError` yükselt.
- Önce `use_cache=False` ve `torch.no_grad()` ile müdahalesiz gerçek son konum logitlerini hesapla.
- `delta=katsayi*yon`; normu eşikten **büyükse** `esik/norm` ile ölçekle. `kirpildi` bu karşılaştırmanın bool sonucudur. Sıfır normda bölme yapma.
- Hedef katmana forward hook tak. Katman çıktısını klonla, yalnız `[:, -1, :]` dilimine delta'yı aynı dtype/cihazda ekle. Çıktı tuple ise diğer öğeleri koru. Gerçek uygulanan son-token farkının L2 normunu kaydet.
- Aynı girdide ikinci gerçek ileri hesabı yap ve hook'u başarılı/başarısız bütün yollarda kaldır.
- Tam şu alanları döndür: `kirpildi` bool, `kayma_normu` float, `temel_logitler` ve `yeni_logitler` (her biri son konumun sözlükteki ilk 8 float logiti), `temel_en_olasi` ve `yeni_en_olasi` (tam logit argmax'ları, int).

Ağırlıkları, yön tensörünü, mevcut hookları veya önceki tokenların aktivasyonlarını değiştirme. Test, sonraki katmanın girdisini de gözler; sadece doğru görünen bir rapor yeterli değildir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 300
```

```starter
import ai_lab

def gercek_yonelt(tok, model, metin, yon, katman, katsayi, esik):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_15 as lab15
    tok,model,yonler,bilgi=lab15.hazirla()
    print(gercek_yonelt(tok,model,"A careful report about a river.",yonler[0],0,0.5,0.2))
```

```test
import copy
import math
import random
import ai_lab
from sandbox import ai_gercek_ai_temel_15 as lab15
sonuclar=[]
def kontrol(c,mesaj):
    sonuclar.append(bool(c));return ok(c,mesaj)
kontrol(not ai_lab.kod_denetimi(src,("referans_yurut",)),"laboratuvar yamalanmamalı veya test oracle'ı çağrılmamalı")
fn=need("gercek_yonelt")
try:
    import torch
    tok,model,yonler,bilgi=lab15.hazirla()
except (ImportError,ai_lab.GercekLabYok) as e:
    kontrol(False,"GERÇEK AKTİVASYON YOK: "+str(e));stop()
bas_agirlik=lab15.agirlik_ozeti(model)
layers=model.model.layers
metin="A careful report "+str(random.SystemRandom().randrange(100,999))+" about a river."
ayarlar=[(0,0.5,0.2),(2,-1.0,0.3),(0,0.0,0.4),(2,0.25,1.0),(0,0.5,0.0)]

def referans_yurut(t,m,text,d,k,a,e,hepsi=False):
    ids=t(text,add_special_tokens=False)["input_ids"]
    with torch.no_grad():
        before=m(torch.tensor([ids]),use_cache=False).logits[0,-1].double()
    delta=a*d
    norm=torch.linalg.vector_norm(delta)
    clipped=bool(norm.item()>e)
    if clipped:delta=delta*(e/norm)
    actual=[];norms=[]
    def steer(module,args,out):
        h=out[0] if isinstance(out,tuple) else out
        new=h.clone();step=delta.to(dtype=h.dtype,device=h.device)
        if hepsi:new+=step
        else:new[:,-1,:]+=step
        actual.append(new.detach().clone())
        norms.append(torch.linalg.vector_norm((new[:,-1,:]-h[:,-1,:]).double()).item())
        return (new,)+out[1:] if isinstance(out,tuple) else new
    handle=m.model.layers[k].register_forward_hook(steer)
    try:
        with torch.no_grad():after=m(torch.tensor([ids]),use_cache=False).logits[0,-1].double()
    finally:handle.remove()
    return {"kirpildi":clipped,"kayma_normu":float(norms[0]),"temel_logitler":before[:8].tolist(),
            "yeni_logitler":after[:8].tolist(),"temel_en_olasi":int(before.argmax().item()),
            "yeni_en_olasi":int(after.argmax().item())},actual[0]
beklenen=[referans_yurut(tok,model,metin,yonler[k],k,a,e) for k,a,e in ayarlar]
def ayni(a,b):
    if not isinstance(a,dict) or set(a)!=set(b) or type(a["kirpildi"]) is not bool or a["kirpildi"]!=b["kirpildi"]:
        return False
    if type(a["kayma_normu"]) is not float or not math.isfinite(a["kayma_normu"]) or abs(a["kayma_normu"]-b["kayma_normu"])>1e-6:
        return False
    for k in ["temel_en_olasi","yeni_en_olasi"]:
        if type(a[k]) is not int or a[k]!=b[k]:return False
    for k in ["temel_logitler","yeni_logitler"]:
        if not isinstance(a[k],list) or len(a[k])!=8 or any(type(v) is not float or not math.isfinite(v) for v in a[k]):return False
        if not torch.allclose(torch.tensor(a[k],dtype=torch.float64),torch.tensor(b[k],dtype=torch.float64),atol=1e-4,rtol=1e-5):return False
    return True
ids=tok(metin,add_special_tokens=False)["input_ids"]
def hook_sayilari():
    return [(len(m._forward_hooks),len(m._forward_pre_hooks)) for m in model.modules()]
def sozlesme(f):
    try:
        for (k,a,e),(ref,target) in zip(ayarlar,beklenen):
            before_hooks=hook_sayilari();before_versions=[p._version for p in model.parameters()]
            d=yonler[k].clone();d_once=d.clone();seen=[];current=[]
            def root(module,args,kwargs):
                v=args[0] if args else kwargs.get("input_ids")
                current[:]=v.detach().tolist() if isinstance(v,torch.Tensor) else []
            def downstream(module,args,kwargs):
                v=args[0] if args else kwargs.get("hidden_states")
                if current==[ids] and isinstance(v,torch.Tensor):seen.append(v.detach().clone())
            h0=model.register_forward_pre_hook(root,with_kwargs=True)
            h1=layers[k+1].register_forward_pre_hook(downstream,with_kwargs=True)
            try:r=f(tok,model,metin,d,k,a,e)
            finally:h0.remove();h1.remove()
            if not ayni(r,ref) or not any(v.shape==target.shape and torch.allclose(v,target,atol=1e-6,rtol=1e-6) for v in seen):return False
            if not torch.equal(d,d_once) or hook_sayilari()!=before_hooks or [p._version for p in model.parameters()]!=before_versions:return False
        hs=hook_sayilari();calls=[];raised=False
        def hata_enjekte(module,args,kwargs):
            calls.append(True)
            if len(calls)==2:raise RuntimeError("PAFTA_FAIL_FORWARD")
        he=model.register_forward_pre_hook(hata_enjekte,with_kwargs=True)
        try:
            try:f(tok,model,metin,yonler[0].clone(),0,0.5,0.2)
            except RuntimeError as exc:raised=str(exc)=="PAFTA_FAIL_FORWARD"
        finally:he.remove()
        if not raised or hook_sayilari()!=hs:return False
        for k,a,e,text in [(-1,1,0.5,metin),(True,1,0.5,metin),(len(layers),1,0.5,metin),
                            (0,True,0.5,metin),(0,float("nan"),0.5,metin),(0,3,0.5,metin),
                            (0,1,-1,metin),(0,1,True,metin),(0,1,float("inf"),metin),
                            (0,1,0.5,""),(0,1,0.5,None),(0,1,0.5," the"*40)]:
            hs=hook_sayilari()
            try:f(tok,model,text,yonler[0],k,a,e);return False
            except ValueError:
                if hook_sayilari()!=hs:return False
        return True
    except Exception:return False
kontrol(sozlesme(fn),"gerçek son-token müdahalesi aşağı katmana ulaşıyor; ağırlık/yön/hooklar korunuyor")
sabit=copy.deepcopy(beklenen[0][0])
def yon_degistir(t,m,text,d,k,a,e):return fn(t,m,text,d,k,-a,e)
def kirpma_yok(t,m,text,d,k,a,e):return fn(t,m,text,d,k,a,1.0)
def hepsi(t,m,text,d,k,a,e):return referans_yurut(t,m,text,d,k,a,e,hepsi=True)[0]
for ad,mutant in [("boş kod/işlev",None),("boş sözlük",lambda *a:{}),
                  ("sabit gerçek rapor",lambda *a:copy.deepcopy(sabit)),
                  ("yön işareti ters",yon_degistir),("norm sınırı yok",kirpma_yok),
                  ("bütün tokenlara müdahale",hepsi)]:
    kontrol(not sozlesme(mutant),"hatalı çözüm reddedilmeli: "+ad)
ciktilar=[fn(tok,model,metin,yonler[k],k,a,e) for k,a,e in ayarlar] if all(sonuclar) else []
kontrol(lab15.agirlik_ozeti(model)==bas_agirlik,"bütün gerçek model parametrelerinin SHA-256 özeti değişmedi")
ai_lab.kanit_yaz("temel-15-steering",{
    "kaynak":"gercek","kabul":all(sonuclar),"model_bilgisi":bilgi,
    "ayarlar":{"metin":metin,"katman_katsayi_esik":[list(a) for a in ayarlar]},"ciktilar":ciktilar,
    "agirlik_oncesi_sonrasi_sha256":bas_agirlik,"olculen":"gerçek residual forward hook, aşağı katman aktivasyonu ve logit değişimi",
    "sinir":"evrensel anlam/refusal/güvenlik veya TransformerLens/repeng kabulü değildir",
    "temizlik":"deney hookları kaldırıldı; CPU, harici süreç/sunucu/indirme yok"})
for a,r in zip(ayarlar,ciktilar):print("katman/katsayı/eşik",a,"uygulanan norm",r["kayma_normu"],"kırpıldı",r["kirpildi"],"argmax",r["temel_en_olasi"],"→",r["yeni_en_olasi"])
```

```solution
import ai_lab
import math
import torch

def gercek_yonelt(tok, model, metin, yon, katman, katsayi, esik):
    layers=model.model.layers
    if not isinstance(metin,str) or not metin.strip() or type(katman) is not int or not 0<=katman<len(layers):
        raise ValueError("metin veya katman geçersiz")
    if isinstance(katsayi,bool) or not isinstance(katsayi,(int,float)) or not math.isfinite(katsayi) or not -2<=katsayi<=2:
        raise ValueError("katsayı geçersiz")
    if isinstance(esik,bool) or not isinstance(esik,(int,float)) or not math.isfinite(esik) or not 0<=esik<=1:
        raise ValueError("eşik geçersiz")
    ids=tok(metin,add_special_tokens=False)["input_ids"]
    if not 1<=len(ids)<=24:raise ValueError("token sayısı geçersiz")
    with torch.no_grad():before=model(torch.tensor([ids]),use_cache=False).logits[0,-1].double()
    delta=katsayi*yon
    norm=torch.linalg.vector_norm(delta)
    clipped=bool(norm.item()>esik)
    if clipped:delta=delta*(esik/norm)
    norms=[]
    def steer(module,args,out):
        h=out[0] if isinstance(out,tuple) else out
        new=h.clone()
        new[:,-1,:]+=delta.to(dtype=h.dtype,device=h.device)
        norms.append(float(torch.linalg.vector_norm((new[:,-1,:]-h[:,-1,:]).double()).item()))
        return (new,)+out[1:] if isinstance(out,tuple) else new
    handle=layers[katman].register_forward_hook(steer)
    try:
        with torch.no_grad():after=model(torch.tensor([ids]),use_cache=False).logits[0,-1].double()
    finally:handle.remove()
    return {"kirpildi":clipped,"kayma_normu":norms[0],"temel_logitler":before[:8].tolist(),
            "yeni_logitler":after[:8].tolist(),"temel_en_olasi":int(before.argmax().item()),
            "yeni_en_olasi":int(after.argmax().item())}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_15 as lab15
    tok,model,yonler,bilgi=lab15.hazirla()
    print(gercek_yonelt(tok,model,"A careful report about a river.",yonler[0],0,0.5,0.2))
```

```hint
Forward hook çıktı yerine yeni bir çıktı döndürebilir. `h.clone()` üzerinde son tokenı değiştir ve handle'ı `finally` ile kaldır. Delta'nın dtype'ını katman çıktısına uydur; normu gerçekten uygulanan farktan ölç.
```
:::
