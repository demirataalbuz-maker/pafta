---
id: ai-temel-09
title: "Eğitim Döngüsü: Loss, Gradient ve Optimizer"
summary: Sentetik MSE kaybı, gradyan ve SGD adımlarıyla tek ağırlıklı eğitim döngüsü oluştur.
timeout: 45
---

::: anlat Kayıp hatayı, gradyan yönü gösterir
Ortalama kare hata tahmin ile hedefin farkını cezalandırır. Gradyan kaybın ağırlıklara göre değişim yönünü verir; optimizer bu bilgiyi kullanarak ağırlıkları günceller. PyTorch bu işlemleri otomatik türevle yapar, ancak temel döngü aynıdır.

Bu derste PyTorch veya TensorBoard çalıştırılmaz. Üç tahminlik küçük MSE ve tek ağırlıklı lineer regresyon kullanılır. Böylece her güncellemenin kaybı nasıl değiştirdiği gerçek Python çıktısıyla izlenebilir.
:::

::: anlat Öğrenme oranı güncellemenin ölçeğidir
SGD ağırlığı gradyanın ters yönünde, öğrenme oranıyla ölçeklenmiş miktarda değiştirir. Çok büyük oran salınım veya ıraksama, çok küçük oran yavaş öğrenme yaratabilir. Kayıp düşüşü tek başına güvenlik iyileşmesi anlamına gelmez.

Eğitim kayıtlarında her adımın kaybını o adım güncellenmeden önce hesaplayacağız. Bu sözleşme, kayıp dizisiyle ağırlık dizisinin bir adım kaymasını önler.
:::

::: tahmin Gradyan ve SGD adımını tahmin et
Üç çıktı satırını yaz:

```python
tahmin, hedef = [1, 3], [0, 1]
print(round(sum((a-b)**2 for a,b in zip(tahmin,hedef))/2, 6))
print(round(2*(1-0)/2, 6))
print(round(1 - 0.1 * 2, 6))
```

???

```cikti
2.5
1.0
0.8
```

İlk satır ortalama kare hatayı, ikinci satır ilk tahminin gradyanını, üçüncü satır SGD güncellemesini gösterir.
:::

::: gorev 1 · MSE kaybını ve gradyanı hesapla
`mse(tahmin, hedef)` işlevini yaz. İki girdi de üç adet bool olmayan int/float içeren listedir; geçersiz veride `ValueError` yükselt.

Ortalama kare hatayı ve her tahmin için `2*(tahmin-hedef)/3` gradyanını hesapla. `{"kayip":K,"gradyan":G}` döndür; bütün sayıları altı ondalığa yuvarla. Girdileri değiştirme.

```starter
def mse(tahmin, hedef):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn([1, 2, 3], [1, 2, 3]) != {"kayip": 0.0, "gradyan": [0.0, 0.0, 0.0]}:
            return False
        if fn([0, 0, 0], [1, 1, 1]) != {"kayip": 1.0, "gradyan": [-0.666667, -0.666667, -0.666667]}:
            return False
        if fn([2, 0, -2], [0, 2, 0]) != {"kayip": 4.0, "gradyan": [1.333333, -1.333333, -1.333333]} or fn([0, 0, 0], [1, 0, 0]) != {"kayip": 0.333333, "gradyan": [-0.666667, 0.0, 0.0]}:
            return False
        for args in [(None, [0, 0, 0]), ([0, 0], [0, 0]), ([0, True, 0], [0, 0, 0]), ([0, 0, 0], [0, 0]), ([0, 0, 0], [0, "0", 0])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(mse), "MSE, gradyan işareti ve yuvarlama korunmalı")
def m_tahmin(t, h):
    return mse(list(reversed(t)), h)
def m_hedef(t, h):
    return mse(t, [x + 1 for x in h])
def m_boyut(t, h):
    return mse(t + [0], h + [0])
for ad, mutant in [("tahmini bozan", m_tahmin), ("hedefi bozan", m_hedef), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def mse(tahmin, hedef):
    def vektor(x):
        return isinstance(x, list) and len(x) == 3 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x)
    if not vektor(tahmin) or not vektor(hedef):
        raise ValueError("vektör geçersiz")
    farklar = [a - b for a, b in zip(tahmin, hedef)]
    return {"kayip": round(sum(x * x for x in farklar) / 3, 6), "gradyan": [round(2 * x / 3, 6) for x in farklar]}
```

```hint
Önce fark listesini çıkar. Kayıp karelerin ortalaması, gradyan ise her farkın `2/3` katıdır.
```
:::

::: gorev 2 · Üç ağırlıklı SGD güncellemesi yap
`sgd(agirliklar, gradyan, oran)` işlevini yaz. Ağırlıklar ve gradyan üç sayıdır. Oran bool olmayan, `0 < oran <= 1` koşulundaki sayıdır. Geçersiz veride `ValueError` yükselt.

Her ağırlıktan `oran * gradyan` çıkar ve sonucu altı ondalığa yuvarla. Yeni liste döndür; girdileri değiştirme.

```starter
def sgd(agirliklar, gradyan, oran):
    return []
```

```test
def sozlesme(fn):
    try:
        if fn([1, 2, 3], [0.5, -0.5, 1], 0.1) != [0.95, 2.05, 2.9] or fn([1, 1, 1], [1, 1, 1], 1) != [0.0, 0.0, 0.0]:
            return False
        if fn([1, 1, 1], [1, 2, 3], 0.3) != [0.7, 0.4, 0.1] or fn([1, 1, 1], [1, 1, 1], 1 / 3) != [0.666667, 0.666667, 0.666667]:
            return False
        for args in [(None, [0, 0, 0], 0.1), ([0, 0], [0, 0], 0.1), ([0, True, 0], [0, 0, 0], 0.1), ([0, 0, 0], [0, 0], 0.1), ([0, 0, 0], [0, 0, 0], 0), ([0, 0, 0], [0, 0, 0], 1.1), ([0, 0, 0], [0, 0, 0], True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sgd), "SGD yönü, oran ve şema korunmalı")
def m_agirlik(a, g, o):
    return sgd(list(reversed(a)), g, o)
def m_gradyan(a, g, o):
    return sgd(a, list(reversed(g)), o)
def m_oran(a, g, o):
    return sgd(a, g, o * 2)
for ad, mutant in [("ağırlığı bozan", m_agirlik), ("gradyanı bozan", m_gradyan), ("oranı bozan", m_oran)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def sgd(agirliklar, gradyan, oran):
    def vektor(x):
        return isinstance(x, list) and len(x) == 3 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x)
    if not vektor(agirliklar) or not vektor(gradyan):
        raise ValueError("vektör geçersiz")
    if not isinstance(oran, (int, float)) or isinstance(oran, bool) or not 0 < oran <= 1:
        raise ValueError("oran geçersiz")
    return [round(a - oran * g, 6) for a, g in zip(agirliklar, gradyan)]
```

```hint
Her ağırlık/gradyan çiftinde `a - oran * g` hesapla; güncellemeyi yeni listede topla.
```
:::

::: gorev 3 · Tek ağırlıklı eğitim izini üret
`egitim(x, y, baslangic, oran, adim)` işlevini yaz. x, y ve başlangıç bool olmayan sayılardır; oran ikinci görevdeki biçimdedir. Adım bool olmayan 1–8 tamsayısıdır. Geçersiz veride `ValueError` yükselt.

Model `tahmin = agirlik*x` olsun. Her adımda güncelleme öncesi MSE kaybını (`tahmin-y` karesi), ardından gradyanı `2*x*(tahmin-y)` hesapla ve SGD uygula. `{"agirlik":W,"kayiplar":L}` döndür; ağırlığı ve her kaybı altı ondalığa yuvarla.

```starter
def egitim(x, y, baslangic, oran, adim):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn(1, 2, 0, 0.1, 1) != {"agirlik": 0.4, "kayiplar": [4.0]}:
            return False
        if fn(1, 1, 0, 0.1, 3) != {"agirlik": 0.488, "kayiplar": [1.0, 0.64, 0.4096]}:
            return False
        if fn(0, 1, 2, 1, 1) != {"agirlik": 2.0, "kayiplar": [1.0]} or fn(1, 1, 0, 1 / 3, 2) != {"agirlik": 0.888889, "kayiplar": [1.0, 0.111111]} or len(fn(1, 1, 0, 0.1, 8)["kayiplar"]) != 8:
            return False
        for args in [(True, 1, 0, 0.1, 1), (1, None, 0, 0.1, 1), (1, 1, "0", 0.1, 1), (1, 1, 0, 0, 1), (1, 1, 0, 1.1, 1), (1, 1, 0, True, 1), (1, 1, 0, 0.1, 0), (1, 1, 0, 0.1, 9), (1, 1, 0, 0.1, True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(egitim), "eğitim sırası, kayıp izi ve adım sınırı korunmalı")
def m_x(x, y, b, o, a):
    return egitim(x * 2, y, b, o, a)
def m_y(x, y, b, o, a):
    return egitim(x, y + 1, b, o, a)
def m_adim(x, y, b, o, a):
    return egitim(x, y, b, o, 1)
for ad, mutant in [("x değerini bozan", m_x), ("hedefi bozan", m_y), ("adımı bozan", m_adim)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def egitim(x, y, baslangic, oran, adim):
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) for v in (x, y, baslangic)):
        raise ValueError("sayı geçersiz")
    if not isinstance(oran, (int, float)) or isinstance(oran, bool) or not 0 < oran <= 1:
        raise ValueError("oran geçersiz")
    if not isinstance(adim, int) or isinstance(adim, bool) or not 1 <= adim <= 8:
        raise ValueError("adım geçersiz")
    agirlik = float(baslangic)
    kayiplar = []
    for _ in range(adim):
        fark = agirlik * x - y
        kayiplar.append(round(fark * fark, 6))
        agirlik -= oran * 2 * x * fark
    return {"agirlik": round(agirlik, 6), "kayiplar": kayiplar}
```

```hint
Döngüde önce farkı ve kaybı kaydet; sonra aynı farkı kullanarak ağırlığı güncelle.
```
:::

::: anlat Gerçek deney: formülün yanında autograd ve optimizer çalışsın
Önceki tek ağırlıklı döngü SGD'nin matematiğini gösterdi. Bu görevde gerçek `torch.nn.Linear(2,1)` modeli, `torch.nn.functional.mse_loss`, `loss.backward()` ve `torch.optim.SGD.step()` çalıştırılır. Veri sentetik, hesap CPU ve float64'tür; önceden eğitilmiş model veya indirme gerekmez.

PyTorch gradyanları varsayılan olarak biriktirir. Her eğitim adımında optimizer gradyanlarını temizle, tahmini yap, **güncellemeden önceki** ortalama kaybı kaydet, geriye türev al ve optimizer'ı ilerlet. `zero_grad` unutulursa önceki adımın gradyanı bir sonraki güncellemeye karışır. `no_grad` eğitimde backward hesabını engeller; yalnız son ağırlıkları raporlarken veya değerlendirmede kullanılır.

Test yalnız düşen kayba bakmaz: gerçek parametre gradyan hookları ve optimizer adım hookları doğru sayıda backward/step çalıştığını gözlemler. Son ağırlıkları ayrıca autograd veya optimizer kullanmayan analitik MSE hesabıyla karşılaştırır. Eğitim kaybının düşmesi, üretimde doğruluk, genelleme veya güvenlik kanıtı değildir.
:::

::: gorev Gerçek deney · Gerçek backward ve SGD eğitim döngüsü
`torch_egit(model, optimizer, x, y, adim)` işlevini yaz. Laboratuvar sana bağımsız, CPU'da float64 `Linear(2,1,bias=True)` modeli ve onun momentum/weight-decay içermeyen SGD optimizer'ını verir. `x`, N×2; `y`, N×1 tensörüdür. Bu dört girdinin uygun kurulduğunu varsayabilirsin; bunları yeniden oluşturma veya verilen optimizer yerine başka optimizer kullanma.

`adim` bool olmayan 1–8 aralığında int olmalı; diğer değerlerde modeli değiştirmeden `ValueError` yükselt.

Her adımda sırasıyla:

1. `optimizer.zero_grad(set_to_none=True)` çağır.
2. `model(x)` tahminlerinden `torch.nn.functional.mse_loss(..., y, reduction="mean")` hesapla.
3. Güncelleme öncesi kaybı Python float olarak kaydet.
4. `loss.backward()` ve `optimizer.step()` çağır.

Tam `{"kayiplar": [...], "agirlik": [w0,w1], "bias": b}` sözlüğü döndür. Ağırlıklar ve bias **son** güncellemeden sonradır; sayılar Python float, yuvarlanmamış olsun. `x` ve `y` değiştirilmez. Verilen model gerçekten eğitilmiş kalmalı; yalnız doğru görünümlü rapor döndürmek yetmez. Başka bir modelin parametrelerini veya optimizer ayarlarını değiştirme.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 120
```

```starter
import ai_lab

def torch_egit(model, optimizer, x, y, adim):
    return {}

if ai_lab.CALISTIR:
    import torch
    model = torch.nn.Linear(2, 1, dtype=torch.float64)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    x = torch.tensor([[0.,1.],[1.,0.],[1.,1.]], dtype=torch.float64)
    y = torch.tensor([[1.],[2.],[3.]], dtype=torch.float64)
    print(torch_egit(model, optimizer, x, y, 4))
```

```test
import copy
import random
import ai_lab
sonuclar=[]
def kontrol(c,mesaj):
    sonuclar.append(bool(c))
    return ok(c,mesaj)
kontrol(not ai_lab.kod_denetimi(src),"laboratuvar yamalanmamalı")
fn=need("torch_egit")
try:
    import torch
except ImportError as e:
    kontrol(False,"GERÇEK TORCH YOK: "+str(e))
    stop()

rng=random.SystemRandom()
seed=rng.randrange(1,2**31)
r=random.Random(seed)
vakalar=[]
for n,adim,lr in [(3,1,0.03),(5,3,0.08),(6,5,0.02)]:
    x=[[r.uniform(-1,1),r.uniform(-1,1)] for _ in range(n)]
    y=[[1.5*a-0.6*b+0.4] for a,b in x]
    vakalar.append({"x":x,"y":y,"agirlik":[r.uniform(-0.7,0.7),r.uniform(-0.7,0.7)],
                    "bias":r.uniform(-0.3,0.3),"lr":lr,"adim":adim})

def kur(v):
    # Model oluştururken küresel RNG durumunu değiştirme.
    with torch.random.fork_rng(devices=[]):
        m=torch.nn.Linear(2,1,bias=True,dtype=torch.float64)
    with torch.no_grad():
        m.weight.copy_(torch.tensor([v["agirlik"]],dtype=torch.float64))
        m.bias.fill_(v["bias"])
    opt=torch.optim.SGD(m.parameters(),lr=v["lr"],momentum=0,weight_decay=0)
    return m,opt,torch.tensor(v["x"],dtype=torch.float64),torch.tensor(v["y"],dtype=torch.float64)

def analitik(v):
    x=torch.tensor(v["x"],dtype=torch.float64)
    y=torch.tensor(v["y"],dtype=torch.float64)
    w=torch.tensor(v["agirlik"],dtype=torch.float64).reshape(2,1)
    b=torch.tensor(v["bias"],dtype=torch.float64)
    losses=[]
    for _ in range(v["adim"]):
        e=x@w+b-y
        losses.append(float((e*e).mean().item()))
        dw=2*x.T@e/len(x)
        db=2*e.mean()
        w=w-v["lr"]*dw
        b=b-v["lr"]*db
    return {"kayiplar":losses,"agirlik":w.flatten().tolist(),"bias":float(b.item())}
beklenen=[analitik(v) for v in vakalar]
def ayni(a,b):
    if not isinstance(a,dict) or set(a)!=set(b) or type(a["bias"]) is not float:
        return False
    for k in ["kayiplar","agirlik"]:
        if not isinstance(a[k],list) or len(a[k])!=len(b[k]) or any(type(x) is not float for x in a[k]):
            return False
        x,y=torch.tensor(a[k],dtype=torch.float64),torch.tensor(b[k],dtype=torch.float64)
        if not bool(torch.isfinite(x).all()) or not torch.allclose(x,y,atol=1e-9,rtol=1e-8):
            return False
    return abs(a["bias"]-b["bias"])<=1e-9

def sozlesme(f):
    try:
        for v,ref in zip(vakalar,beklenen):
            m,opt,x,y=kur(v)
            eski_x,eski_y=x.clone(),y.clone()
            grad_w,grad_b,steps=[],[],[]
            hw=m.weight.register_hook(lambda g:grad_w.append(g.detach().clone()))
            hb=m.bias.register_hook(lambda g:grad_b.append(g.detach().clone()))
            hs=opt.register_step_post_hook(lambda *args:steps.append(True))
            try:
                a=f(m,opt,x,y,v["adim"])
            finally:
                hw.remove();hb.remove();hs.remove()
            if not ayni(a,ref) or len(grad_w)!=v["adim"] or len(grad_b)!=v["adim"] or len(steps)!=v["adim"]:
                return False
            if not torch.equal(x,eski_x) or not torch.equal(y,eski_y):
                return False
            if not torch.allclose(m.weight.detach().flatten(),torch.tensor(ref["agirlik"],dtype=torch.float64),atol=1e-9,rtol=1e-8) or abs(m.bias.item()-ref["bias"])>1e-9:
                return False
            if opt.param_groups[0]["lr"]!=v["lr"]:
                return False
        for n in [0,9,True,1.0,None]:
            m,opt,x,y=kur(vakalar[0])
            w,b=m.weight.detach().clone(),m.bias.detach().clone()
            try:
                f(m,opt,x,y,n)
                return False
            except ValueError:
                if not torch.equal(w,m.weight) or not torch.equal(b,m.bias):
                    return False
        return True
    except Exception:
        return False
kontrol(sozlesme(fn),"gerçek autograd gradyanları, SGD adımları, analitik ağırlık ve güncelleme öncesi kayıp doğru")

def hata(tur):
    def f(m,opt,x,y,n):
        if type(n) is not int or not 1<=n<=8:
            raise ValueError("adım")
        losses=[]
        for _ in range(n):
            if tur!="gradyan_birikimi":
                opt.zero_grad(set_to_none=True)
            loss=torch.nn.functional.mse_loss(m(x),y,reduction="sum" if tur=="toplam" else "mean")
            losses.append(float(loss.item()))
            if tur!="backward_yok":
                loss.backward()
            if tur!="step_yok":
                opt.step()
        return {"kayiplar":losses,"agirlik":m.weight.detach().flatten().tolist(),"bias":float(m.bias.item())}
    return f
for ad,mutant in [("boş kod/işlev",None),("boş sözlük",lambda *a:{}),
                  ("ezber sonuç",lambda *a:copy.deepcopy(beklenen[0])),
                  ("zero_grad unutulmuş",hata("gradyan_birikimi")),
                  ("ortalama yerine toplam kayıp",hata("toplam")),
                  ("backward çağrılmıyor",hata("backward_yok")),
                  ("optimizer adımı yok",hata("step_yok"))]:
    kontrol(not sozlesme(mutant),"hatalı çözüm reddedilmeli: "+ad)

ciktilar=[]
if all(sonuclar):
    for v in vakalar:
        m,opt,x,y=kur(v)
        ciktilar.append(fn(m,opt,x,y,v["adim"]))
ai_lab.kanit_yaz("temel-09-egitim",{
    "kaynak":"gercek","kabul":all(sonuclar),
    "model_bilgisi":{"model":"yerelde oluşturulan Linear(2,1,bias=True)","arac":"torch","surum":torch.__version__,"dtype":"float64","aygit":"cpu"},
    "ayarlar":{"veri_tohumu":seed,"vakalar":vakalar,"optimizer":"SGD momentum=0 weight_decay=0","kayip":"mean MSE"},
    "ciktilar":ciktilar,"gozlem":"parametre gradyan hookları ve gerçek optimizer step-post-hook",
    "sinir":"sentetik regresyon eğitimi; dil modeli fine-tuning veya genelleme/güvenlik kabulü değildir",
    "temizlik":"kalıcı süreç, model indirme veya dış sunucu yok"})
for v,d in zip(vakalar,ciktilar):
    print("gerçek SGD",v["adim"],"adım, lr",v["lr"],"kayıplar",d["kayiplar"],"son ağırlık",d["agirlik"],"bias",d["bias"])
```

```solution
import ai_lab
import torch

def torch_egit(model, optimizer, x, y, adim):
    if type(adim) is not int or not 1<=adim<=8:
        raise ValueError("adım 1-8 tamsayı olmalı")
    kayiplar=[]
    for _ in range(adim):
        optimizer.zero_grad(set_to_none=True)
        loss=torch.nn.functional.mse_loss(model(x),y,reduction="mean")
        kayiplar.append(float(loss.item()))
        loss.backward()
        optimizer.step()
    return {"kayiplar":kayiplar,"agirlik":model.weight.detach().flatten().tolist(),"bias":float(model.bias.item())}

if ai_lab.CALISTIR:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(2026)
        model=torch.nn.Linear(2,1,dtype=torch.float64)
    optimizer=torch.optim.SGD(model.parameters(),lr=0.05)
    x=torch.tensor([[0.,1.],[1.,0.],[1.,1.]],dtype=torch.float64)
    y=torch.tensor([[1.],[2.],[3.]],dtype=torch.float64)
    print(torch_egit(model,optimizer,x,y,4))
```

```hint
`loss.item()` kaydı `optimizer.step()` öncesinde alınır. Sonuç vektörü `model.weight.detach().flatten().tolist()` ile Python float listesine çevrilir. Gradyanları temizlemeden birkaç adım çalıştırıp neden sonucun değiştiğini Çalıştır'da gözlemleyebilirsin.
```
:::
