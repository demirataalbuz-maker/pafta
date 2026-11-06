---
id: ai-temel-12
title: "Fine-Tune Sonrası Güvenlik Değerlendirmesi"
summary: Temel ve ince ayarlı sonuçları aynı kayıtlarda karşılaştır, regresyonları bul ve yayın kapısı uygula.
timeout: 45
---

::: anlat Aynı test seti olmadan karşılaştırma zayıftır
Fine-tune sonrası değerlendirme, temel ve yeni modelin aynı girdilerdeki sonuçlarını karşılaştırmalıdır. Toplam başarı artarken bazı vakalarda güvenlik gerileyebilir. Bu kayıplar vaka kimlikleriyle raporlanmalıdır.

Bu derste Promptfoo, garak veya LM Evaluation Harness çalıştırılmaz. Önceden etiketlenmiş sentetik sonuçlar kullanılır. Amaç araç çıktısını yorumlamak için gereken kazanç, regresyon ve yayın kararı mantığını doğrulamaktır.
:::

::: anlat Ortalama kazanç regresyonu gizleyebilir
Güvenlik oranı yükselse bile önceden güvenli olan bir vakanın artık güvensiz olması ayrı bir risktir. Regresyon sayısını sıfıra yakın izlemek ve kritik vakalarda sıfır istemek, tek ortalamaya göre daha güçlü bir yayın politikasıdır.

Yayın kapısı sabit eşikleri açıkça uygular. Eşikteki değerler kabul edilir; eksik veya türü bozuk metrik reddedilmek yerine hata üretir ki hatalı rapor sessizce dağıtılmasın.
:::

::: tahmin Regresyon ve kapıyı tahmin et
Üç çıktı satırını yaz:

```python
temel = [True, False, True]
yeni = [True, True, False]
print([i for i in range(3) if temel[i] and not yeni[i]])
print(round(sum(yeni) / 3, 6))
print(0.9 >= 0.8 and 0.95 >= 0.95 and 0 == 0)
```

???

```cikti
[2]
0.666667
True
```

İlk satır gerileyen vaka indeksini, ikinci satır yeni güvenlik oranını, üçüncü satır eşikteki yayın kararını gösterir.
:::

::: gorev 1 · Güvenlik kazancını ve regresyonu karşılaştır
`guvenlik_karsilastir(temel, yeni)` işlevini yaz. İki girdi de dört bool değerli listedir; geçersiz veride `ValueError` yükselt.

`{"temel_oran":T,"yeni_oran":Y,"kazanc":K,"regresyonlar":R}` döndür. Kazanç yeni eksi temel orandır. Regresyonlar temelde True, yenide False olan indekslerin artan listesidir. Girdileri değiştirme.

```starter
def guvenlik_karsilastir(temel, yeni):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn([True, False, True, False], [True, True, False, False]) != {"temel_oran": 0.5, "yeni_oran": 0.5, "kazanc": 0.0, "regresyonlar": [2]}:
            return False
        if fn([False, False, False, False], [True, True, True, True]) != {"temel_oran": 0.0, "yeni_oran": 1.0, "kazanc": 1.0, "regresyonlar": []}:
            return False
        if fn([True] * 4, [False] * 4)["regresyonlar"] != [0, 1, 2, 3]:
            return False
        for args in [(None, [True] * 4), ([True] * 3, [True] * 4), ([True, 1, True, False], [True] * 4), ([True] * 4, None), ([True] * 4, [True, False, 0, True])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(guvenlik_karsilastir), "oran, kazanç ve vaka regresyonu korunmalı")
def m_temel(t, y):
    return guvenlik_karsilastir([False] * 4, y)
def m_yeni(t, y):
    return guvenlik_karsilastir(t, [True] * 4)
def m_boyut(t, y):
    return guvenlik_karsilastir(t + [True], y + [True])
for ad, mutant in [("temeli bozan", m_temel), ("yeniyi bozan", m_yeni), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def guvenlik_karsilastir(temel, yeni):
    if any(not isinstance(x, list) or len(x) != 4 or any(not isinstance(v, bool) for v in x) for x in (temel, yeni)):
        raise ValueError("sonuç listesi geçersiz")
    t = sum(temel) / 4
    y = sum(yeni) / 4
    return {"temel_oran": t, "yeni_oran": y, "kazanc": y - t, "regresyonlar": [i for i in range(4) if temel[i] and not yeni[i]]}
```

```hint
İki oranı ayrı hesapla. Regresyon listesinde aynı indeksin temel değeri True ve yeni değeri False olmalı.
```
:::

::: gorev 2 · Vaka kimlikleriyle regresyon raporu üret
`regresyon_raporu(kayitlar)` işlevini yaz. Kayıtlar 1–8 öğeli listedir; her kayıt tam `id`, `temel`, `yeni` anahtarlarını içerir. Kimlikler farklı, boş olmayan stringler; sonuçlar bool değerdir. Geçersiz veride `ValueError` yükselt.

`{"iyilesen":[...],"gerileyen":[...],"sabit":[...]}` döndür. İyileşen temelde False/yenide True, gerileyen tersi, sabit iki sonucu aynı olan kimliklerdir. Her liste özgün kayıt sırasındadır.

```starter
def regresyon_raporu(kayitlar):
    return {}
```

```test
R = [{"id": "a", "temel": False, "yeni": True}, {"id": "b", "temel": True, "yeni": False}, {"id": "c", "temel": True, "yeni": True}]
def sozlesme(fn):
    try:
        if fn(R) != {"iyilesen": ["a"], "gerileyen": ["b"], "sabit": ["c"]} or fn(R[:1]) != {"iyilesen": ["a"], "gerileyen": [], "sabit": []}:
            return False
        sekiz = R + [dict(x, id=x["id"] + str(i)) for i, x in enumerate(R)] + R[:2]
        sekiz = [dict(x, id=str(i)) for i, x in enumerate(sekiz)]
        if sum(len(v) for v in fn(sekiz).values()) != 8:
            return False
        for deger in [None, [], sekiz + [dict(R[0], id="9")], [dict(R[0], ek=1)], [dict(R[0], id="")], [dict(R[0], temel=1)], [R[0], R[0]]]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(regresyon_raporu), "vaka sınıfları, kimlik sırası ve şema korunmalı")
def m_temel(r):
    return regresyon_raporu([dict(x, temel=False) for x in r])
def m_yeni(r):
    return regresyon_raporu([dict(x, yeni=True) for x in r])
def m_boyut(r):
    return regresyon_raporu(r + [dict(r[0], id="x")])
for ad, mutant in [("temeli bozan", m_temel), ("yeniyi bozan", m_yeni), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def regresyon_raporu(kayitlar):
    if not isinstance(kayitlar, list) or not 1 <= len(kayitlar) <= 8:
        raise ValueError("kayıt listesi geçersiz")
    if any(not isinstance(x, dict) or set(x) != {"id", "temel", "yeni"} for x in kayitlar):
        raise ValueError("kayıt şeması geçersiz")
    if any(not isinstance(x["id"], str) or not x["id"] or any(not isinstance(x[a], bool) for a in ("temel", "yeni")) for x in kayitlar):
        raise ValueError("kayıt değeri geçersiz")
    if len({x["id"] for x in kayitlar}) != len(kayitlar):
        raise ValueError("kimlikler yinelenemez")
    return {"iyilesen": [x["id"] for x in kayitlar if not x["temel"] and x["yeni"]], "gerileyen": [x["id"] for x in kayitlar if x["temel"] and not x["yeni"]], "sabit": [x["id"] for x in kayitlar if x["temel"] == x["yeni"]]}
```

```hint
Üç listeyi ayrı üret; sabit sınıf iki bool değerin eşitliğidir.
```
:::

::: gorev 3 · Sabit eşikli yayın kapısı uygula
`yayin_kapisi(metrik)` işlevini yaz. Metrik tam `dogruluk`, `guvenlik`, `regresyon` anahtarlı sözlüktür. İlk iki alan bool olmayan 0–1 arası sayı, regresyon bool olmayan 0–8 arası tamsayıdır. Geçersiz veride `ValueError` yükselt.

Doğruluk en az 0.8, güvenlik en az 0.95 ve regresyon tam 0 ise True, aksi halde False döndür. Eşikler dahildir; girdiyi değiştirme.

```starter
def yayin_kapisi(metrik):
    return False
```

```test
M = {"dogruluk": 0.9, "guvenlik": 1.0, "regresyon": 0}
def sozlesme(fn):
    try:
        if not fn(M) or not fn({"dogruluk": 0.8, "guvenlik": 0.95, "regresyon": 0}) or not fn(dict(M, dogruluk=1)):
            return False
        if fn(dict(M, dogruluk=0)) or fn(dict(M, guvenlik=0)) or fn(dict(M, dogruluk=0.79)) or fn(dict(M, guvenlik=0.94)) or fn(dict(M, regresyon=1)) or fn(dict(M, regresyon=8)):
            return False
        for deger in [None, {}, dict(M, ek=1), dict(M, dogruluk=True), dict(M, dogruluk=-0.1), dict(M, dogruluk=1.1), dict(M, guvenlik=-0.1), dict(M, guvenlik=1.1), dict(M, regresyon=True), dict(M, regresyon=-1), dict(M, regresyon=9), dict(M, regresyon=0.0)]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yayin_kapisi), "yayın eşikleri, regresyon ve metrik şeması korunmalı")
def m_dogruluk(m):
    return yayin_kapisi(dict(m, dogruluk=0))
def m_guvenlik(m):
    return yayin_kapisi(dict(m, guvenlik=0))
def m_regresyon(m):
    return yayin_kapisi(dict(m, regresyon=1))
for ad, mutant in [("doğruluğu bozan", m_dogruluk), ("güvenliği bozan", m_guvenlik), ("regresyonu bozan", m_regresyon)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yayin_kapisi(metrik):
    if not isinstance(metrik, dict) or set(metrik) != {"dogruluk", "guvenlik", "regresyon"}:
        raise ValueError("metrik şeması geçersiz")
    if any(not isinstance(metrik[a], (int, float)) or isinstance(metrik[a], bool) or not 0 <= metrik[a] <= 1 for a in ("dogruluk", "guvenlik")):
        raise ValueError("oran geçersiz")
    if not isinstance(metrik["regresyon"], int) or isinstance(metrik["regresyon"], bool) or not 0 <= metrik["regresyon"] <= 8:
        raise ValueError("regresyon geçersiz")
    return metrik["dogruluk"] >= 0.8 and metrik["guvenlik"] >= 0.95 and metrik["regresyon"] == 0
```

```hint
Son ifadede üç koşulu `and` ile birleştir; oranlarda `>=`, regresyonda `== 0` kullan.
```
:::

::: anlat Gerçek deney: önce/sonra kararlarını modelden yeniden ölç
Önceki görevde güvenli/güvensiz sonuçları hazır bool dizileriydi. Burada SmolLM2'nin gerçek son-token logitleri üzerine eklenen küçük bir token-bias katmanı **gerçek SGD ile** eğitilir. Aynı tabandan biri olumlu kontrol, diğeri ilk kritik vaka için bilerek yanlış etikete eğitilmiş iki uyarlayıcı çıkarılır. Gerçek LM hesabı çalışma başına yapılır; dondurulmuş taban tekrar kullanılır. Hazır etiketlenmiş model sonuçları verilmez: güvenli-etiket olasılığını modellerden sen hesaplayacaksın.

Her vakanın karar uzayı iki gerçek tokenla sınırlıdır. `chosen` bu sentetik görevde güvenli etiketi, `rejected` ihlal etiketini temsil eder; bunlar genel “iyi/kötü kelime” listesi değildir. Yalnız bu iki logit üzerinde softmax uygula. Bu ölçüm, modelin serbest metinle sır sızdırdığını veya gerçek bir jailbreak yaşandığını göstermez; kontrollü uyarlama sonrası regresyon ölçümünü öğretir. Tam dil modeli fine-tuning, Promptfoo veya garak kabulü yapılmış sayılmaz.

Değerlendirme `torch.no_grad()` içinde olmalı. Eğitim bitmiştir; değerlendirmede ağırlık, vaka veya eşik değiştirilmez. Aynı kimlikli vakaları karşılaştır; ortalama oran aynı kalsa bile temelde güvenli olup yenide güvensiz olan vaka regresyondur. Kritik regresyon ayrıca listelenir. İyi kontrol modeli de yayın kapısının her şeyi körlemesine engellemediğini sınar.
:::

::: gorev Gerçek deney · Gerçek uyarlayıcılarda eşlenmiş regresyon ve yayın kapısı
`gercek_regresyon_raporu(temel, yeni, vakalar, esik=0.5)` işlevini yaz. `temel` ve `yeni`, her `prompt` için gerçek LM tabanı + eğitilmiş bias logitlerini döndüren torch modülleridir. Modeller ve vakaların uygun kurulduğunu varsayabilirsin; yeniden model oluşturma veya eğitme.

`esik`, bool olmayan sonlu bir sayı ve `0 < esik <= 1` olmalıdır; aksi durumda `ValueError` yükselt.

Her vaka `id`, `prompt`, `chosen`, `rejected`, `kritik` alanlarını taşır. `torch.no_grad()` içinde her iki modeli aynı istemde çağır. `[chosen,rejected]` sırasındaki iki logite softmax uygula; ilk öğe güvenli etiket olasılığıdır. Olasılık `>= esik` ise vaka güvenli sayılır. Eşitlikte kabul et.

Tam şu alanları döndür:

- `vakalar`: özgün sırayla `{"id":..., "temel_p":float, "yeni_p":float, "temel_guvenli":bool, "yeni_guvenli":bool}` kayıtları.
- `temel_oran`, `yeni_oran`, `kazanc`: float; güvenli vaka oranları ve yeni eksi temel oran.
- `regresyonlar`: temelde güvenli, yenide güvensiz vaka kimlikleri.
- `kritik_regresyonlar`: bunların `kritik=True` olanları.
- `yayin_izin`: yalnız yeni güvenli oranı `>= 0.95` ve kritik regresyon sayısı sıfır ise True.

Girdiler değişmez. Sayılar yuvarlanmaz. “Her zaman yayınla” ve “her zaman engelle” çözüm değildir. Kapı kararı yalnız bu sentetik deneyin ölçütüdür; üretim dağıtımı yapılmaz.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import ai_lab

def gercek_regresyon_raporu(temel, yeni, vakalar, esik=0.5):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_12 as lab12
    temel, iyi, bozuk, vakalar, bilgi = lab12.hazirla()
    print(gercek_regresyon_raporu(temel, bozuk, vakalar))
```

```test
import copy
import math
import ai_lab
from sandbox import ai_gercek_ai_temel_12 as lab12
sonuclar=[]
def kontrol(c,mesaj):
    sonuclar.append(bool(c))
    return ok(c,mesaj)
kontrol(not ai_lab.kod_denetimi(src,("referans_rapor",)),"laboratuvar yamalanmamalı veya test oracle'ı çağrılmamalı")
fn=need("gercek_regresyon_raporu")
try:
    import torch
    temel,iyi,bozuk,vakalar,bilgi=lab12.hazirla()
except (ImportError,ai_lab.GercekLabYok) as e:
    kontrol(False,"GERÇEK MODEL/EĞİTİM YOK: "+str(e))
    stop()

def referans_rapor(a,b,vs,e):
    rows=[]
    with torch.no_grad():
        for v in vs:
            ids=[v["chosen"],v["rejected"]]
            ap=float(torch.softmax(a(v["prompt"])[ids],dim=-1)[0].item())
            bp=float(torch.softmax(b(v["prompt"])[ids],dim=-1)[0].item())
            rows.append({"id":v["id"],"temel_p":ap,"yeni_p":bp,"temel_guvenli":ap>=e,"yeni_guvenli":bp>=e})
    t=sum(x["temel_guvenli"] for x in rows)/len(rows)
    y=sum(x["yeni_guvenli"] for x in rows)/len(rows)
    regress=[x["id"] for x in rows if x["temel_guvenli"] and not x["yeni_guvenli"]]
    critical=[v["id"] for v in vs if v["id"] in regress and v["kritik"]]
    return {"vakalar":rows,"temel_oran":float(t),"yeni_oran":float(y),"kazanc":float(y-t),
            "regresyonlar":regress,"kritik_regresyonlar":critical,"yayin_izin":y>=0.95 and not critical}
normal=referans_rapor(temel,iyi,vakalar,0.5)
bozuk_rapor=referans_rapor(temel,bozuk,vakalar,0.5)
kontrol(normal["yayin_izin"] is True and bozuk_rapor["yayin_izin"] is False and bool(bozuk_rapor["kritik_regresyonlar"]),"gerçek eğitim olumlu kontrol ve kritik regresyon üretti")

# Aynı modelin gerçek olasılığını eşik olarak kullan: >= sınırını sınar.
sinir=normal["vakalar"][0]["temel_p"]
senaryolar=[(temel,iyi,vakalar,0.5),(temel,bozuk,vakalar,0.5),
            (bozuk,temel,vakalar,0.7),(temel,temel,vakalar[:1],sinir),
            (temel,bozuk,list(reversed(vakalar)),0.5)]
beklenen=[referans_rapor(*a) for a in senaryolar]
def ayni(a,b):
    if not isinstance(a,dict) or set(a)!=set(b):
        return False
    if any(type(a[k]) is not float or not math.isfinite(a[k]) or abs(a[k]-b[k])>1e-10 for k in ["temel_oran","yeni_oran","kazanc"]):
        return False
    if type(a["yayin_izin"]) is not bool or a["yayin_izin"]!=b["yayin_izin"] or a["regresyonlar"]!=b["regresyonlar"] or a["kritik_regresyonlar"]!=b["kritik_regresyonlar"]:
        return False
    if not isinstance(a["vakalar"],list) or len(a["vakalar"])!=len(b["vakalar"]):
        return False
    for x,y in zip(a["vakalar"],b["vakalar"]):
        if not isinstance(x,dict) or set(x)!=set(y) or x["id"]!=y["id"]:
            return False
        if any(type(x[k]) is not bool or x[k]!=y[k] for k in ["temel_guvenli","yeni_guvenli"]):
            return False
        if any(type(x[k]) is not float or not math.isfinite(x[k]) or abs(x[k]-y[k])>1e-10 for k in ["temel_p","yeni_p"]):
            return False
    return True
def sozlesme(f):
    try:
        for args,ref in zip(senaryolar,beklenen):
            a,b,vs,e=args
            once_a,once_b=a.token_bias.detach().clone(),b.token_bias.detach().clone()
            v_once=copy.deepcopy(vs);seen_a=[];seen_b=[]
            ha=a.register_forward_hook(lambda *x:seen_a.append(torch.is_grad_enabled()))
            hb=b.register_forward_hook(lambda *x:seen_b.append(torch.is_grad_enabled()))
            try:
                result=f(a,b,vs,e)
            finally:
                ha.remove();hb.remove()
            if not ayni(result,ref) or len(seen_a)<len(vs) or len(seen_b)<len(vs) or any(seen_a+seen_b):
                return False
            if vs!=v_once or not torch.equal(once_a,a.token_bias) or not torch.equal(once_b,b.token_bias):
                return False
        for e in [0,-1,1.01,True,None,float("nan"),float("inf")]:
            try:
                f(temel,iyi,vakalar,e)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn),"gerçek önce/sonra olasılıkları, kritik regresyonlar ve iki yönlü yayın kapısı doğru")
def degistir(tur):
    def f(a,b,vs,e=0.5):
        if isinstance(e,bool) or not isinstance(e,(int,float)) or not math.isfinite(e) or not 0<e<=1:
            raise ValueError("eşik")
        out=referans_rapor(a,b,vs,e)
        if tur=="hep_izin":out["yayin_izin"]=True
        if tur=="hep_red":out["yayin_izin"]=False
        if tur=="kritik_yok":out["kritik_regresyonlar"]=[]
        if tur=="ters":out=referans_rapor(b,a,vs,e)
        return out
    return f
for ad,mutant in [("boş kod/işlev",None),("boş sözlük",lambda *a:{}),
                  ("sabit gerçek rapor",lambda *a:copy.deepcopy(normal)),
                  ("her zaman yayınla",degistir("hep_izin")),
                  ("her zaman engelle",degistir("hep_red")),
                  ("kritik regresyonu gizle",degistir("kritik_yok")),
                  ("önce ve sonrayı değiştir",degistir("ters"))]:
    kontrol(not sozlesme(mutant),"hatalı çözüm reddedilmeli: "+ad)
ciktilar=[fn(*a) for a in senaryolar] if all(sonuclar) else []
ai_lab.kanit_yaz("temel-12-regresyon",{
    "kaynak":"gercek","kabul":all(sonuclar),"model_bilgisi":bilgi,
    "ayarlar":{"vakalar":vakalar,"esikler":[s[3] for s in senaryolar]},"ciktilar":ciktilar,
    "sinir":"iki-token sentetik karar uzayında eğitilmiş bias regresyonu; genel LLM güvenlik kabulü değildir",
    "temizlik":"CPU; dış süreç/sunucu/indirme yok; kalıcı LM ağırlıkları değişmedi"})
for tag,d in zip(["olumlu kontrol","kontrollü bozulma","geri kazanım","eşik sınırı","ters vaka sırası"],ciktilar):
    print(tag,"temel",d["temel_oran"],"yeni",d["yeni_oran"],"kritik",d["kritik_regresyonlar"],"yayın",d["yayin_izin"])
```

```solution
import ai_lab
import math
import torch

def gercek_regresyon_raporu(temel, yeni, vakalar, esik=0.5):
    if isinstance(esik,bool) or not isinstance(esik,(int,float)) or not math.isfinite(esik) or not 0<esik<=1:
        raise ValueError("eşik geçersiz")
    rows=[]
    with torch.no_grad():
        for v in vakalar:
            ids=[v["chosen"],v["rejected"]]
            p0=float(torch.softmax(temel(v["prompt"])[ids],dim=-1)[0].item())
            p1=float(torch.softmax(yeni(v["prompt"])[ids],dim=-1)[0].item())
            rows.append({"id":v["id"],"temel_p":p0,"yeni_p":p1,"temel_guvenli":p0>=esik,"yeni_guvenli":p1>=esik})
    t=float(sum(x["temel_guvenli"] for x in rows)/len(rows))
    y=float(sum(x["yeni_guvenli"] for x in rows)/len(rows))
    regress=[x["id"] for x in rows if x["temel_guvenli"] and not x["yeni_guvenli"]]
    critical=[v["id"] for v in vakalar if v["id"] in regress and v["kritik"]]
    return {"vakalar":rows,"temel_oran":t,"yeni_oran":y,"kazanc":float(y-t),
            "regresyonlar":regress,"kritik_regresyonlar":critical,"yayin_izin":y>=0.95 and not critical}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_12 as lab12
    temel,iyi,bozuk,vakalar,bilgi=lab12.hazirla()
    print(gercek_regresyon_raporu(temel,bozuk,vakalar))
```

```hint
Softmax yalnız `[chosen,rejected]` iki logiti üzerinde hesaplanır. Önce bütün vaka kayıtlarını üret, sonra bu aynı kayıtlardan oranları ve regresyon kimliklerini çıkar. Sadece yayın kapısını doğru döndürmek yeterli değildir; olasılıklar da gerçek modele uymalı.
```
:::
