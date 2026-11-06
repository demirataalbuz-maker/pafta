---
id: ai-temel-11
title: "Tercih Verisi ve Hizalama"
summary: Tercih çiftlerini temizle, sentetik DPO kaybı hesapla ve hizalama ölçütlerini raporla.
timeout: 45
---

::: anlat Tercih verisi iki yanıtı karşılaştırır
DPO gibi yöntemler aynı istem için seçilen ve reddedilen yanıt çiftlerini kullanır. Boş istem, aynı iki yanıt veya yanlış alan adları eğitim sinyalini bozar. Veri temizliği modelden önce açık bir sözleşmeyle yapılmalıdır.

Bu derste TRL, Transformers veya Datasets çalıştırılmaz. Küçük kayıtlar ve önceden hesaplanmış log olasılıklar kullanılır. Böylece tercih verisinin biçimi ile modelin öğrenme hedefi ayrı ayrı test edilebilir.
:::

::: anlat DPO tercih farkını büyütmeye çalışır
Sentetik fixture'da seçilen ve reddedilen yanıt için politika/referans log olasılık farkları verilir. DPO bu iki farkın arasındaki marjı artırır; kayıp marj azaldıkça büyür. Beta marjın etkisini ölçekler.

Kayıp ve tercih doğruluğu güvenliğin tamamını ölçmez. Seçilen yanıtın gerçekten güvenli olup olmadığı ayrıca etiketlenmelidir. Bu nedenle son görevde doğruluk ve güvenli seçim oranı ayrı raporlanır.
:::

::: tahmin Tercih marjını tahmin et
Üç çıktı satırını yaz:

```python
print({"prompt": "  soru  ".strip(), "chosen": " A ".strip()})
print((-1 - (-2)) - (-3 - (-2)))
print(round(2 / 4, 6))
```

???

```cikti
{'prompt': 'soru', 'chosen': 'A'}
2
0.5
```

İlk satır metin temizliğini, ikinci satır politika/referans farkları arasındaki marjı, üçüncü satır tercih oranını gösterir.
:::

::: gorev 1 · Tercih çiftlerini doğrula ve temizle
`tercih_temizle(kayitlar)` işlevini yaz. Kayıtlar 1–8 öğeli listedir; her kayıt tam `prompt`, `chosen`, `rejected` anahtarlı string sözlüğüdür. Boşlukları atıldıktan sonra alanlar boş olamaz ve chosen ile rejected aynı olamaz. Geçersiz veride `ValueError` yükselt.

Her alanın baş/son boşluğunu at, kayıt sırasını koru ve bağımsız sözlükler döndür. Girdileri değiştirme.

```starter
def tercih_temizle(kayitlar):
    return []
```

```test
R = [{"prompt": "  soru ", "chosen": " A ", "rejected": " B "}]
def sozlesme(fn):
    try:
        beklenen = [{"prompt": "soru", "chosen": "A", "rejected": "B"}]
        sonuc = fn(R)
        if sonuc != beklenen or sonuc[0] is R[0] or R[0]["prompt"] != "  soru ":
            return False
        sekiz = [dict(R[0], prompt=str(i)) for i in range(8)]
        if len(fn(sekiz)) != 8:
            return False
        for deger in [None, [], sekiz + [dict(R[0], prompt="9")], [dict(R[0], ek=1)], [dict(R[0], prompt=" ")], [dict(R[0], chosen=1)], [dict(R[0], chosen=" ")], [dict(R[0], rejected=" ")], [dict(R[0], chosen=" B ")], [dict(R[0], rejected=" A ")]]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(tercih_temizle), "tercih şeması, temizlik ve farklı yanıtlar korunmalı")
def m_prompt(r):
    return tercih_temizle([dict(x, prompt="x") for x in r])
def m_secim(r):
    return tercih_temizle([dict(x, chosen=x["rejected"]) for x in r])
def m_boyut(r):
    return tercih_temizle(r + r)
for ad, mutant in [("istemi bozan", m_prompt), ("tercihi bozan", m_secim), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def tercih_temizle(kayitlar):
    if not isinstance(kayitlar, list) or not 1 <= len(kayitlar) <= 8:
        raise ValueError("kayıt listesi geçersiz")
    if any(not isinstance(x, dict) or set(x) != {"prompt", "chosen", "rejected"} for x in kayitlar):
        raise ValueError("kayıt şeması geçersiz")
    if any(any(not isinstance(x[a], str) for a in ("prompt", "chosen", "rejected")) for x in kayitlar):
        raise ValueError("metin geçersiz")
    sonuc = [{a: x[a].strip() for a in ("prompt", "chosen", "rejected")} for x in kayitlar]
    if any(not x["prompt"] or not x["chosen"] or not x["rejected"] or x["chosen"] == x["rejected"] for x in sonuc):
        raise ValueError("tercih içeriği geçersiz")
    return sonuc
```

```hint
Alanları önce `strip` ile yeni sözlüklere kopyala; boşluk ve eşitlik kontrollerini temizlenmiş değerlerde yap.
```
:::

::: gorev 2 · Kararlı sentetik DPO kaybı hesapla
`dpo_kaybi(secilen, reddedilen, beta)` işlevini yaz. İki girdi de `[politika_logp, referans_logp]` biçiminde iki sayılık listedir. Beta bool olmayan 0.1–2 aralığında sayıdır; sınırlar dahildir. Geçersiz veride `ValueError` yükselt.

Marj `(secilen[0]-secilen[1]) - (reddedilen[0]-reddedilen[1])`, `z=-beta*marj` olsun. `log(1+exp(z))` kaybını taşmaya dayanıklı biçimde hesapla ve altı ondalığa yuvarla. Girdileri değiştirme.

```starter
def dpo_kaybi(secilen, reddedilen, beta):
    return 0.0
```

```test
def sozlesme(fn):
    try:
        if fn([-1, -2], [-3, -2], 1) != 0.126928 or fn([-1, -2], [-3, -2], 0.5) != 0.313262:
            return False
        if fn([-1, -2], [-3, -2], 0.1) != 0.598139 or fn([-1, -2], [-3, -2], 2) != 0.01815:
            return False
        if fn([-1000, -1000], [-1000, -1000], 1) != 0.693147 or fn([1000, 0], [0, 0], 1) != 0.0:
            return False
        for args in [(None, [-3, -2], 1), ([-1], [-3, -2], 1), ([-1, True], [-3, -2], 1), ([-1, -2], [-3], 1), ([-1, -2], [-3, -2], 0), ([-1, -2], [-3, -2], 0.09), ([-1, -2], [-3, -2], 2.1), ([-1, -2], [-3, -2], True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dpo_kaybi), "DPO marjı, beta ve kararlı softplus korunmalı")
def m_secilen(s, r, b):
    return dpo_kaybi(list(reversed(s)), r, b)
def m_reddedilen(s, r, b):
    return dpo_kaybi(s, list(reversed(r)), b)
def m_beta(s, r, b):
    return dpo_kaybi(s, r, b * 2)
for ad, mutant in [("seçileni bozan", m_secilen), ("reddedileni bozan", m_reddedilen), ("betayı bozan", m_beta)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def dpo_kaybi(secilen, reddedilen, beta):
    import math
    def cift(x):
        return isinstance(x, list) and len(x) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x)
    if not cift(secilen) or not cift(reddedilen):
        raise ValueError("logp çifti geçersiz")
    if not isinstance(beta, (int, float)) or isinstance(beta, bool) or not 0.1 <= beta <= 2:
        raise ValueError("beta geçersiz")
    marj = (secilen[0] - secilen[1]) - (reddedilen[0] - reddedilen[1])
    z = -beta * marj
    kayip = max(z, 0) + math.log1p(math.exp(-abs(z)))
    return round(kayip, 6)
```

```hint
Kararlı softplus için `max(z,0) + log1p(exp(-abs(z)))` kullan; büyük pozitif z'de doğrudan `exp(z)` alma.
```
:::

::: gorev 3 · Tercih doğruluğu ve güvenliği ayrı raporla
`hizalama_raporu(kayitlar)` işlevini yaz. Kayıtlar 1–8 öğeli listedir; her kayıt tam `dogru`, `guvenli` anahtarlı iki bool değer içerir. Geçersiz veride `ValueError` yükselt.

`dogru` tercihin beklenen yanıtı, `guvenli` seçilen yanıtın güvenlik kontrolünü geçmesini gösterir. `{"dogruluk":D,"guvenli_oran":G,"adet":N}` döndür; oranlar altı ondalığa yuvarlanır. Girdileri değiştirme.

```starter
def hizalama_raporu(kayitlar):
    return {}
```

```test
R = [{"dogru": True, "guvenli": True}, {"dogru": True, "guvenli": False}, {"dogru": False, "guvenli": True}, {"dogru": False, "guvenli": False}]
def sozlesme(fn):
    try:
        if fn(R) != {"dogruluk": 0.5, "guvenli_oran": 0.5, "adet": 4} or fn(R[:1]) != {"dogruluk": 1.0, "guvenli_oran": 1.0, "adet": 1} or fn(R[:3]) != {"dogruluk": 0.666667, "guvenli_oran": 0.666667, "adet": 3}:
            return False
        sekiz = R + R
        if fn(sekiz)["adet"] != 8:
            return False
        for deger in [None, [], sekiz + R[:1], [dict(R[0], ek=1)], [dict(R[0], dogru=1)], [dict(R[0], guvenli=None)]]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(hizalama_raporu), "doğruluk, güvenli oran ve bool şema korunmalı")
def m_dogru(r):
    return hizalama_raporu([dict(x, dogru=False) for x in r])
def m_guvenli(r):
    return hizalama_raporu([dict(x, guvenli=True) for x in r])
def m_boyut(r):
    return hizalama_raporu(r + r)
for ad, mutant in [("doğruluğu bozan", m_dogru), ("güvenliği bozan", m_guvenli), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def hizalama_raporu(kayitlar):
    if not isinstance(kayitlar, list) or not 1 <= len(kayitlar) <= 8:
        raise ValueError("kayıt listesi geçersiz")
    if any(not isinstance(x, dict) or set(x) != {"dogru", "guvenli"} or any(not isinstance(x[a], bool) for a in ("dogru", "guvenli")) for x in kayitlar):
        raise ValueError("kayıt geçersiz")
    adet = len(kayitlar)
    return {"dogruluk": round(sum(x["dogru"] for x in kayitlar) / adet, 6), "guvenli_oran": round(sum(x["guvenli"] for x in kayitlar) / adet, 6), "adet": adet}
```

```hint
Bool değerlerin toplamı True sayısını verir; iki alanın toplamını ayrı ayrı kayıt sayısına böl.
```
:::

::: anlat Gerçek deney: gerçek LM olasılıklarından küçük bir DPO eğitimi
Önceki DPO kaybında log olasılıklar hazır sayılardı. Şimdi kurulu SmolLM2-135M gerçek istemlerle çalıştırılır. Son konumun tüm sözlük logitleri alınır; aynı dondurulmuş tabanın üzerine eklenen `token_bias` parametresi gerçek autograd ve SGD ile eğitilir. Referans politika tabandır; eğitim politikası `taban_logit + token_bias` döndürür.

Taban sabit olduğundan her istemin gerçek LM ileri hesabı Kontrol başına bir kez yapılıp eğitim adımlarında yeniden kullanılır. Bunlar elle yazılmış logitler değildir; gerçek model kimliği, ağırlık özeti, girdiler ve logit özetleri kanıta yazılır. Deney **tek tokenlık** seçilen/reddedilen tamamlamaları kullanır; ekranda gerçek token metinlerini görürsün. Çok tokenlı yanıtların toplam log olasılığı ve tam model fine-tuning'i bu görevin kabulü değildir. TRL çalıştırıldığı da iddia edilmez.

Her çift için `marj = (logπ(chosen)-logπ(rejected)) - (logref(chosen)-logref(rejected))`. Kararlı DPO kaybı `softplus(-beta*marj)` ve bütün çiftlerin ortalamasıdır. Referans eğitilmez. Etiketler bu sentetik görev için verilmiştir; tercih kaybının düşmesi, modelin güvenli veya etik hâle geldiğini kanıtlamaz.
:::

::: gorev Gerçek deney · Gerçek dil modeli tabanında token-bias DPO eğitimi
`dpo_egit(politika, referans, optimizer, vakalar, beta, adim)` işlevini yaz. Laboratuvar sana gerçek LM çıktısına dayanan iki torch modülü ve yalnız `politika.token_bias` parametresini güncelleyen SGD optimizer'ını verir. Her vaka tam `prompt`, `chosen`, `rejected` alanlarını taşır; chosen/rejected gerçek tek-token kimlikleridir. Bu girdilerin doğru kurulduğunu varsayabilirsin; modülleri veya optimizer'ı yeniden oluşturma.

- `beta` bool olmayan, sonlu, `0 < beta <= 2` sayısı; `adim` bool olmayan 1–6 int olmalı. Aksi hâlde politika değişmeden `ValueError` yükselt.
- Her adımda gradyanı temizle. Her istem için `torch.log_softmax(politika(prompt),dim=-1)` hesapla; referansın log-softmax'ını `torch.no_grad()` içinde hesapla. Yukarıdaki düzeltilmiş marjı kullanarak `softplus(-beta*marj)` kayıplarının ortalamasını al.
- Güncelleme **öncesi** kaybı kaydet, `loss.backward()` ve `optimizer.step()` uygula.
- Son güncellemeden **sonra** aynı vakaların beta ile çarpılmamış düzeltilmiş marjlarını yeniden hesapla.
- Tam `{"kayiplar": [float,...], "son_marjlar": [float,...]}` döndür. Sayılar yuvarlanmaz. Verilen politika gerçekten değişmeli; referans ve vaka listesi değişmemeli.

Yalnız seçilen yanıtın negatif log olasılığını en aza indirmek, referans farkını atlamak, beta'yı yok saymak veya seçilen/reddedilen yönünü ters almak DPO çözümü değildir. Tamamlamalar tek token olduğundan bu görevin log olasılığı o tokenın gerçek dağılımdaki değeridir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import ai_lab

def dpo_egit(politika, referans, optimizer, vakalar, beta, adim):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_11 as lab11
    bases, vakalar, bilgi = lab11.hazirla()
    politika, referans, optimizer = lab11.modeller(bases, 0.1)
    print(dpo_egit(politika, referans, optimizer, vakalar, 0.4, 3))
```

```test
import copy
import math
import ai_lab
from sandbox import ai_gercek_ai_temel_11 as lab11
sonuclar=[]
def kontrol(c,mesaj):
    sonuclar.append(bool(c))
    return ok(c,mesaj)
kontrol(not ai_lab.kod_denetimi(src,("analitik",)),"çözüm laboratuvarı yamalamamalı veya test oracle'ını çağırmamalı")
fn=need("dpo_egit")
try:
    import torch
    bases,vakalar,bilgi=lab11.hazirla()
except (ImportError,ai_lab.GercekLabYok) as e:
    kontrol(False,"GERÇEK MODEL YOK: "+str(e))
    stop()

# Bu tek-token additive-bias politikasında normalizer farkları iptal olur.
# Bağımsız oracle autograd/optimizer kullanmaz: dL/dz=-sigmoid(-z).
def analitik(beta,adim,lr):
    bias=torch.zeros_like(next(iter(bases.values())))
    losses=[]
    for _ in range(adim):
        grad=torch.zeros_like(bias)
        total=0.0
        for v in vakalar:
            c,r=v["chosen"],v["rejected"]
            margin=float((bias[c]-bias[r]).item())
            z=beta*margin
            total+=max(-z,0)+math.log1p(math.exp(-abs(z)))
            g=-beta/(1+math.exp(z))/len(vakalar)
            grad[c]+=g;grad[r]-=g
        losses.append(total/len(vakalar))
        bias=bias-lr*grad
    return {"kayiplar":losses,"son_marjlar":[float((bias[v["chosen"]]-bias[v["rejected"]]).item()) for v in vakalar]},bias
ayarlar=[(0.2,1,0.05),(1.4,3,0.08),(0.6,4,0.03)]
beklenen=[analitik(*a) for a in ayarlar]
def ayni(a,b):
    if not isinstance(a,dict) or set(a)!=set(b):
        return False
    for k in b:
        if not isinstance(a[k],list) or len(a[k])!=len(b[k]) or any(type(x) is not float or not math.isfinite(x) for x in a[k]):
            return False
        if not torch.allclose(torch.tensor(a[k],dtype=torch.float64),torch.tensor(b[k],dtype=torch.float64),atol=1e-8,rtol=1e-7):
            return False
    return True
def sozlesme(f):
    try:
        for (beta,n,lr),(ref,ref_bias) in zip(ayarlar,beklenen):
            p,r,opt=lab11.modeller(bases,lr)
            once={k:t.clone() for k,t in bases.items()};v_once=copy.deepcopy(vakalar)
            grads,steps,referans_cagrilari=[],[],[]
            hg=p.token_bias.register_hook(lambda g:grads.append(g.detach().clone()))
            hs=opt.register_step_post_hook(lambda *a:steps.append(True))
            hr=r.register_forward_hook(lambda *a:referans_cagrilari.append(True))
            try:
                a=f(p,r,opt,vakalar,beta,n)
            finally:
                hg.remove();hs.remove();hr.remove()
            if not ayni(a,ref) or len(grads)!=n or len(steps)!=n or len(referans_cagrilari)<len(vakalar):
                return False
            if not torch.allclose(p.token_bias.detach(),ref_bias,atol=1e-8,rtol=1e-7) or vakalar!=v_once or opt.param_groups[0]["lr"]!=lr:
                return False
            if any(not torch.equal(t,once[k]) for k,t in bases.items()):
                return False
        for beta,n in [(0,1),(-1,1),(True,1),(float("nan"),1),(float("inf"),1),(3,1),(0.5,0),(0.5,7),(0.5,True)]:
            p,r,opt=lab11.modeller(bases,0.1)
            try:
                f(p,r,opt,vakalar,beta,n)
                return False
            except ValueError:
                if bool((p.token_bias.detach()!=0).any()):
                    return False
        return True
    except Exception:
        return False
kontrol(sozlesme(fn),"gerçek LM tabanlı DPO: referans farkı, beta, autograd, SGD ve son marjlar doğru")

def hatali(tur):
    def f(p,r,opt,vs,beta,n):
        if isinstance(beta,bool) or not isinstance(beta,(int,float)) or not math.isfinite(beta) or not 0<beta<=2 or type(n) is not int or not 1<=n<=6:
            raise ValueError("ayar")
        losses=[]
        for _ in range(n):
            opt.zero_grad(set_to_none=True)
            ls=[]
            for v in vs:
                c,j=v["chosen"],v["rejected"]
                lp=torch.log_softmax(p(v["prompt"]),dim=-1)
                with torch.no_grad():
                    lr=torch.log_softmax(r(v["prompt"]),dim=-1)
                m=lp[c]-lp[j]-(0 if tur=="referans_yok" else lr[c]-lr[j])
                if tur=="ters":m=-m
                ls.append(torch.nn.functional.softplus(-(1 if tur=="beta_yok" else beta)*m))
            loss=torch.stack(ls).mean()
            losses.append(float(loss.item()));loss.backward();opt.step()
        with torch.no_grad():
            margins=[]
            for v in vs:
                lp=torch.log_softmax(p(v["prompt"]),dim=-1);lr=torch.log_softmax(r(v["prompt"]),dim=-1)
                margins.append(float((lp[v["chosen"]]-lp[v["rejected"]]-lr[v["chosen"]]+lr[v["rejected"]]).item()))
        return {"kayiplar":losses,"son_marjlar":margins}
    return f
for ad,mutant in [("boş kod/işlev",None),("boş sözlük",lambda *a:{}),
                  ("sabit gerçek rapor",lambda *a:copy.deepcopy(beklenen[0][0])),
                  ("referans farkı yok",hatali("referans_yok")),
                  ("beta yok sayılıyor",hatali("beta_yok")),
                  ("tercih yönü ters",hatali("ters"))]:
    kontrol(not sozlesme(mutant),"hatalı çözüm reddedilmeli: "+ad)
ciktilar=[]
if all(sonuclar):
    for beta,n,lr in ayarlar:
        p,r,opt=lab11.modeller(bases,lr)
        d=fn(p,r,opt,vakalar,beta,n)
        ids=sorted({v[k] for v in vakalar for k in ["chosen","rejected"]})
        ciktilar.append(dict(d,bias_ozeti={str(i):p.token_bias[i].item() for i in ids}))
ai_lab.kanit_yaz("temel-11-dpo",{
    "kaynak":"gercek","kabul":all(sonuclar),"model_bilgisi":bilgi,
    "ayarlar":{"beta_adim_lr":[list(a) for a in ayarlar],"vakalar":vakalar},"ciktilar":ciktilar,
    "gozlem":"gerçek LM ileri hesabı + token-bias gradyan hooku + optimizer step hooku",
    "sinir":"tek-token additive-bias DPO; tüm LM ağırlıkları fine-tuning, TRL veya güvenlik kabulü değildir",
    "temizlik":"CPU işlemi; harici sunucu ve süreç yok"})
for v in bilgi["gercek_cagrilar"]:
    print("gerçek tercih tokenları:",repr(v["chosen_metin"]),repr(v["rejected_metin"]),"istem:",v["prompt"])
for a,d in zip(ayarlar,ciktilar):
    print("beta/adım/lr",a,"DPO kayıpları",d["kayiplar"],"son marjlar",d["son_marjlar"])
```

```solution
import ai_lab
import math
import torch

def dpo_egit(politika, referans, optimizer, vakalar, beta, adim):
    if isinstance(beta,bool) or not isinstance(beta,(int,float)) or not math.isfinite(beta) or not 0<beta<=2 or type(adim) is not int or not 1<=adim<=6:
        raise ValueError("beta veya adım geçersiz")
    kayiplar=[]
    for _ in range(adim):
        optimizer.zero_grad(set_to_none=True)
        losses=[]
        for v in vakalar:
            lp=torch.log_softmax(politika(v["prompt"]),dim=-1)
            with torch.no_grad():
                lr=torch.log_softmax(referans(v["prompt"]),dim=-1)
            marj=lp[v["chosen"]]-lp[v["rejected"]]-lr[v["chosen"]]+lr[v["rejected"]]
            losses.append(torch.nn.functional.softplus(-beta*marj))
        loss=torch.stack(losses).mean()
        kayiplar.append(float(loss.item()))
        loss.backward()
        optimizer.step()
    son_marjlar=[]
    with torch.no_grad():
        for v in vakalar:
            lp=torch.log_softmax(politika(v["prompt"]),dim=-1)
            lr=torch.log_softmax(referans(v["prompt"]),dim=-1)
            son_marjlar.append(float((lp[v["chosen"]]-lp[v["rejected"]]-lr[v["chosen"]]+lr[v["rejected"]]).item()))
    return {"kayiplar":kayiplar,"son_marjlar":son_marjlar}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_11 as lab11
    bases,vakalar,bilgi=lab11.hazirla()
    p,r,opt=lab11.modeller(bases,0.1)
    print(dpo_egit(p,r,opt,vakalar,0.4,3))
```

```hint
Politika log-softmax'ı autograd grafiğinde kalmalı; yalnız referans hesaplarını `no_grad` içine al. Kayıp `softplus(-beta*marj)` biçimindedir. Son marjlar optimizer'ın son adımından sonra yeniden hesaplanır.
```
:::
