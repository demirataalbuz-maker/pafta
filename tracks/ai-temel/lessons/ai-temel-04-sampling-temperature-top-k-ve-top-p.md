---
id: ai-temel-04
title: "Sampling: Temperature, Top-k ve Top-p"
summary: Sentetik logitlerde sıcaklık ölçeklemesi, top-k ve top-p aday kümelerini deterministik biçimde uygula.
timeout: 45
---

::: anlat Sıcaklık dağılımın keskinliğini değiştirir
Temperature ile logitler softmax öncesinde sıcaklığa bölünür. Birden küçük sıcaklık farkları büyütür; birden büyük sıcaklık dağılımı yumuşatır. Sıfır sıcaklık bu formülde tanımsızdır ve ayrı bir greedy üretim politikası olarak ele alınmalıdır.

Bu derste Transformers veya gerçek model gerekmez. Amaç üretim parametrelerinin aday olasılıklarını nasıl değiştirdiğini görmek ve saldırı testlerinde farklı yapılandırmaları birbirine karıştırmamaktır.
:::

::: anlat Top-k sayı, top-p kütle sınırıdır
Top-k en yüksek olasılıklı sabit sayıda adayı tutar. Top-p ise olasılığı büyükten küçüğe ekleyerek toplam kütlesi eşiğe ulaşan en küçük aday kümesini seçer. Eşiği aşan son aday da kümede kalır; aksi halde yeniden normalizasyon anlamsızlaşır.

Her iki yöntemde de eşit logitlerde küçük indeks önce gelir. Deterministik sıralama, aynı fixture üzerinde test sonuçlarının ve güvenlik ölçümlerinin tekrarlanabilmesi için gereklidir.
:::

::: tahmin Aday kümelerini tahmin et
Üç çıktı satırını yaz:

```python
print([round(x / 0.5, 3) for x in [0.0, 1.0, 2.0]])
print(sorted(range(3), key=lambda i: (-[3, 1, 2][i], i))[:2])
print([0.5, 0.5 + 0.25, 0.5 + 0.25 + 0.25])
```

???

```cikti
[0.0, 2.0, 4.0]
[0, 2]
[0.5, 0.75, 1.0]
```

İlk satır sıcaklık ölçeklemesini, ikinci satır top-2 indekslerini, üçüncü satır top-p sırasındaki kümülatif kütleyi gösterir.
:::

::: gorev 1 · Logitleri sıcaklıkla ölçekle
`sicaklik_olcekle(logitler, sicaklik)` işlevini yaz. Logitler üç adet bool olmayan int/float içeren listedir. Sıcaklık bool olmayan, 0.1–5 aralığında int/float değerdir; sınırlar dahildir. Geçersiz veride `ValueError` yükselt.

Her logiti sıcaklığa böl ve üç ondalığa yuvarlayarak yeni liste döndür. Girdiyi değiştirme.

```starter
def sicaklik_olcekle(logitler, sicaklik):
    return []
```

```test
def sozlesme(fn):
    try:
        if fn([0, 1, 2], 0.5) != [0.0, 2.0, 4.0] or fn([0, 1, 2], 2) != [0.0, 0.5, 1.0]:
            return False
        if fn([1, 1, 1], 0.1) != [10.0, 10.0, 10.0] or fn([1, 1, 1], 5) != [0.2, 0.2, 0.2] or fn([1, 1, 1], 0.3) != [3.333, 3.333, 3.333]:
            return False
        for args in [(None, 1), ([1, 2], 1), ([1, True, 2], 1), ([1, 2, 3], None), ([1, 2, 3], True), ([1, 2, 3], 0), ([1, 2, 3], 0.09), ([1, 2, 3], 5.1)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sicaklik_olcekle), "sıcaklık sınırları ve logit ölçeği korunmalı")
def m_logit(x, s):
    return sicaklik_olcekle(list(reversed(x)), s)
def m_sicaklik(x, s):
    return sicaklik_olcekle(x, s * 2)
def m_boyut(x, s):
    return sicaklik_olcekle(x + [0], s)
for ad, mutant in [("logitleri bozan", m_logit), ("sıcaklığı bozan", m_sicaklik), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def sicaklik_olcekle(logitler, sicaklik):
    if not isinstance(logitler, list) or len(logitler) != 3 or any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in logitler):
        raise ValueError("logitler geçersiz")
    if not isinstance(sicaklik, (int, float)) or isinstance(sicaklik, bool) or not 0.1 <= sicaklik <= 5:
        raise ValueError("sıcaklık geçersiz")
    return [round(x / sicaklik, 3) for x in logitler]
```

```hint
Şema kontrolünden sonra tek liste üretiminde `x / sicaklik` hesapla ve yuvarla.
```
:::

::: gorev 2 · Top-k aday indekslerini seç
`top_k(logitler, k)` işlevini yaz. Logitler üç sayıdan oluşur; k bool olmayan 1, 2 veya 3 tamsayısıdır. Geçersiz veride `ValueError` yükselt.

Adayları logit büyüklüğüne göre azalan, eşitlikte indeks artan sırala. İlk k indeksi liste olarak döndür; girdileri değiştirme.

```starter
def top_k(logitler, k):
    return []
```

```test
def sozlesme(fn):
    try:
        if fn([3, 1, 2], 2) != [0, 2] or fn([3, 1, 2], 1) != [0] or fn([3, 1, 2], 3) != [0, 2, 1]:
            return False
        if fn([2, 2, 1], 2) != [0, 1] or fn([-1, -1, -1], 3) != [0, 1, 2]:
            return False
        for args in [(None, 1), ([1, 2], 1), ([1, True, 2], 1), ([1, 2, 3], 0), ([1, 2, 3], 4), ([1, 2, 3], True), ([1, 2, 3], 1.0)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(top_k), "top-k sıralaması, eşitlik ve k sınırı korunmalı")
def m_logit(x, k):
    return top_k(list(reversed(x)), k)
def m_k(x, k):
    return top_k(x, 3 - k + 1)
def m_boyut(x, k):
    return top_k(x + [0], k)
for ad, mutant in [("logitleri bozan", m_logit), ("k değerini bozan", m_k), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def top_k(logitler, k):
    if not isinstance(logitler, list) or len(logitler) != 3 or any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in logitler):
        raise ValueError("logitler geçersiz")
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 3:
        raise ValueError("k geçersiz")
    return sorted(range(3), key=lambda i: (-logitler[i], i))[:k]
```

```hint
Sıralama anahtarında negatif logit ve indeks ikilisi kullan; sonra yalnız ilk k öğeyi al.
```
:::

::: gorev 3 · Top-p çekirdek adaylarını seç
`top_p(logitler, p)` işlevini yaz. Logitler üç sayıdır; p bool olmayan, `0 < p <= 1` koşulundaki int/float değerdir. Geçersiz veride `ValueError` yükselt.

Kararlı softmax uygula. İndeksleri olasılık azalan, eşitlikte indeks artan sırala. Kümülatif olasılık p değerine ulaşana kadar aday ekle; eşiği geçen adayı da dahil et ve seçilen indeksleri sıralama düzeninde döndür. Girdiyi değiştirme.

```starter
def top_p(logitler, p):
    return []
```

```test
import math
def sozlesme(fn):
    try:
        if fn([0, 1, 2], 0.7) != [2, 1] or fn([0, 1, 2], 0.1) != [2] or fn([0, 1, 2], 1) != [2, 1, 0]:
            return False
        esit = [0, -math.log(2), -math.log(2)]
        if fn(esit, 0.5) != [0] or fn(esit, 0.75) != [0, 1] or fn(esit, 0.8) != [0, 1, 2]:
            return False
        for args in [(None, 0.5), ([1, 2], 0.5), ([1, True, 2], 0.5), ([1, 2, 3], 0), ([1, 2, 3], -1), ([1, 2, 3], 1.1), ([1, 2, 3], True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(top_p), "top-p kütlesi, eşikteki aday ve sıralama korunmalı")
def m_logit(x, p):
    return top_p(list(reversed(x)), p)
def m_p(x, p):
    return top_p(x, min(1, p + 0.2))
def m_boyut(x, p):
    return top_p(x + [0], p)
for ad, mutant in [("logitleri bozan", m_logit), ("eşiği bozan", m_p), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def top_p(logitler, p):
    import math
    if not isinstance(logitler, list) or len(logitler) != 3 or any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in logitler):
        raise ValueError("logitler geçersiz")
    if not isinstance(p, (int, float)) or isinstance(p, bool) or not 0 < p <= 1:
        raise ValueError("p geçersiz")
    tepe = max(logitler)
    paylar = [math.exp(x - tepe) for x in logitler]
    olasiliklar = [x / sum(paylar) for x in paylar]
    sira = sorted(range(3), key=lambda i: (-olasiliklar[i], i))
    secim = []
    toplam = 0.0
    for i in sira:
        secim.append(i)
        toplam += olasiliklar[i]
        if toplam >= p:
            break
    return secim
```

```hint
Adayı kümülatif toplama ekledikten sonra `toplam >= p` ise dur; kontrolü eklemeden önce yapma.
```
:::

::: anlat Gerçek modelde örnekleme: 3 değil 49 bin aday
Yukarıdaki görevler üç logitle çalıştı. Gerçek bir dil modeli her adımda sözlüğündeki **bütün** tokenlar için logit üretir: SmolLM2-135M'de 49.152 aday. Sıcaklık, top-k ve top-p bu dev listeyi kaç adaya indirdiğini ve üretilen metni nasıl değiştirdiğini ancak gerçek dağılımda gösterir.

Üretim kütüphanelerinin (ör. transformers) sırası şöyledir: önce logitler sıcaklığa bölünür, sonra top-k en yüksek k adayı tutar, ardından top-p **top-k'dan kalan ve yeniden normalize edilmiş** dağılımda kütle eşiğini uygular. Sonunda seçilen adayların olasılıkları toplamı 1 olacak şekilde yeniden normalize edilir ve bu dağılımdan örneklenir. Sıra değişirse aday kümesi de değişir.
:::

::: gorev Gerçek deney · Gerçek logitlerde aday kümesi ve örnekleme
`ornekleme_dagilimi(logitler, sicaklik=1.0, k=None, p=1.0)` işlevini yaz. `logitler`, gerçek modelin son konumdaki logitleridir (1 boyutlu `torch.Tensor`, sözlük uzunluğunda).

- Doğrulama, aksi hâlde `ValueError`: `logitler` en az 2 öğeli, sonlu değerli, 1 boyutlu `torch.Tensor`; `sicaklik` bool olmayan int/float, 0.1–5 (sınırlar dahil); `k` `None` ya da bool olmayan int, 1 ile sözlük uzunluğu arası; `p` bool olmayan int/float, `0 < p <= 1`.
- Hesabı **float64** yap: logitleri sıcaklığa böl, softmax uygula.
- Adayları olasılık azalan, eşitlikte küçük token kimliği önce sırala. `k` verilmişse ilk k adayı tut.
- Kalan adayların olasılıklarını yeniden normalize et; bu dağılımda sırayla ekleyerek kümülatif toplam `p`'ye ulaşınca dur (eşiği geçen aday kümede kalır).
- Döndür: `{"adaylar": [token kimlikleri, sıralı], "olasiliklar": [float, toplamı 1]}`.

Test, işlevini rastgele metinlerin gerçek logitlerinde ve rastgele ayarlarda bağımsız bir hesapla ve transformers'ın kendi işlemcileriyle karşılaştırır, sonra senin işlevinle gerçek metin üretir. Çalıştır düğmesi aday kümesi boyutlarını ve dört ayarda üretilen metni gösterir. Laboratuvardaki `referans`/`hf_referans` işlevlerini çağırma.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import torch
import ai_lab

def ornekleme_dagilimi(logitler, sicaklik=1.0, k=None, p=1.0):
    return {"adaylar": [], "olasiliklar": []}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_04 as deney
    deney.goster(ornekleme_dagilimi)
```

```test
import random
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "hf_referans", "son_logitler", "getattr", "uret"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans işlevleri çağrılmamalı " + ", ".join(sorun))
fn = need("ornekleme_dagilimi")
try:
    from sandbox import ai_gercek_ai_temel_04 as D
    tok, model, bilgi = ai_lab.dil_modeli()
    import torch
except ai_lab.GercekLabYok as e:
    kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
    stop()
rnd = random.Random()
sozcuk = ["river", "music", "Ankara", "security", "garden", "data", "kedi", "model", "green", "token"]
vakalar = [("The capital of France is", 0.7, 5, 0.8), ("Once upon a time", 1.3, None, 0.9),
           ("def add(a, b):", 0.5, 20, 1.0), ("Bugün hava çok", 1.0, 8, 0.6)]
for _ in range(3):
    vakalar.append((f"The {rnd.choice(sozcuk)} and the {rnd.choice(sozcuk)} {rnd.randint(2, 999)}",
                    rnd.choice([0.6, 0.8, 1.2, 1.4]), rnd.choice([None, rnd.randint(3, 40)]), rnd.choice([0.7, 0.85, 0.95])))
logit = {}
for m, *_ in vakalar:
    if m not in logit:
        with torch.no_grad():
            logit[m] = model(torch.tensor([tok(m)["input_ids"]])).logits[0, -1].clone()
V = logit[vakalar[0][0]].shape[0]
def ayni(a, b):
    if not isinstance(a, dict) or set(a) != {"adaylar", "olasiliklar"}:
        return False
    if not isinstance(a["adaylar"], list) or not all(type(i) is int for i in a["adaylar"]) or a["adaylar"] != b["adaylar"]:
        return False
    if not isinstance(a["olasiliklar"], list) or len(a["olasiliklar"]) != len(b["olasiliklar"]):
        return False
    return all(type(x) is float and abs(x - y) < 1e-7 for x, y in zip(a["olasiliklar"], b["olasiliklar"]))
def sozlesme(f):
    try:
        if not all(ayni(f(logit[m].clone(), sicaklik=T, k=k, p=p), D.referans(logit[m], T, k, p)) for m, T, k, p in vakalar):
            return False
        t = logit[vakalar[0][0]]
        for arg, kw in [(None, {}), ([1.0, 2.0], {}), (torch.tensor([1.0]), {}), (torch.tensor([[1.0, 2.0]]), {}),
                        (torch.tensor([1.0, float("nan")]), {}), (t, {"sicaklik": 0}), (t, {"sicaklik": 5.1}),
                        (t, {"sicaklik": True}), (t, {"k": 0}), (t, {"k": V + 1}), (t, {"k": True}), (t, {"k": 2.0}),
                        (t, {"p": 0}), (t, {"p": 1.01}), (t, {"p": True})]:
            try:
                f(arg, **kw)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "gerçek logitler: sıcaklık → top-k → yeniden normalize → top-p sırası, eşikteki aday ve olasılıklar doğru")
def gecerli(f):
    def sarmal(lg, sicaklik=1.0, k=None, p=1.0):
        if not isinstance(lg, torch.Tensor) or lg.dim() != 1 or lg.shape[0] < 2 or not torch.isfinite(lg).all():
            raise ValueError("logit")
        if isinstance(sicaklik, bool) or not isinstance(sicaklik, (int, float)) or not 0.1 <= sicaklik <= 5:
            raise ValueError("sicaklik")
        if k is not None and (isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= lg.shape[0]):
            raise ValueError("k")
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not 0 < p <= 1:
            raise ValueError("p")
        return f(lg, sicaklik, k, p)
    return sarmal
sabit = D.referans(logit[vakalar[0][0]], 0.7, 5, 0.8)
for ad, kw in [("sıcaklık yok sayılıyor", {"sicaklik_kullan": False}), ("top-p top-k'dan önce, tam dağılımda", {"sira": "pk"}),
               ("eşiği geçen aday dışarıda", {"esik_dahil": False}), ("yeniden normalize yok", {"normalize": False}),
               ("k yok sayılıyor", {"k_kullan": False})]:
    kontrol(not sozlesme(gecerli(lambda lg, T, k, p, kw=kw: D.referans(lg, T, k, p, **kw))), "hatalı çözüm reddedilmeli: " + ad)
kontrol(not sozlesme(gecerli(lambda lg, T, k, p: sabit)), "hatalı çözüm reddedilmeli: ezber tablo")
hf = []
for m, T, k, p in vakalar:
    h, r = D.hf_referans(logit[m], T, k, p), D.referans(logit[m], T, k, p)
    hf.append(set(h) == set(r["adaylar"]) and max(abs(h[i] - q) for i, q in zip(r["adaylar"], r["olasiliklar"])) < 1e-6)
kontrol(all(hf), f"bağımsız karşılaştırma: transformers işlemcileri aynı aday kümesini veriyor ({sum(hf)}/{len(hf)})")
uretimler = {}
if all(sonuclar):
    for ad, ayar in D.DENEY_AYARLARI:
        uretimler[ad] = D.uret(fn, D.DENEY_METNI, ayar, seed=7)
    ref = D.uret(lambda lg, **a: D.referans(lg, **a), D.DENEY_METNI, D.DENEY_AYARLARI[1][1], seed=7)
    kontrol(uretimler[D.DENEY_AYARLARI[1][0]] == ref, "senin işlevinle gerçek üretim, aynı tohumla referans üretimle birebir aynı")
boyutlar = D.kume_boyutlari(fn) if all(sonuclar) else {}
yol = ai_lab.kanit_yaz("temel-ornekleme", {
    "kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-temel-04", "model_bilgisi": bilgi,
    "ayarlar": {"vakalar": [list(v) for v in vakalar], "tolerans": 1e-7, "uretim_tohumu": 7, "uretim_metni": D.DENEY_METNI},
    "hf_uyumu": hf, "aday_kumesi_boyutlari": boyutlar, "uretimler": uretimler})
if boyutlar:
    ok(True, f"GERÇEK ÇIKTI ({bilgi['model']}@{bilgi['revizyon'][:8]}, sözlük {V}): {D.DENEY_METNI!r} için p=0.9 aday sayısı "
             f"T=0.5'te {boyutlar['T=0.5, p=0.9']}, T=1.5'te {boyutlar['T=1.5, p=0.9']}; "
             f"T=1.5,p=0.95 üretimi: {uretimler['T=1.5, p=0.95']['metin']!r}")
```

```solution
import torch
import ai_lab

def ornekleme_dagilimi(logitler, sicaklik=1.0, k=None, p=1.0):
    if not isinstance(logitler, torch.Tensor) or logitler.dim() != 1 or logitler.shape[0] < 2 \
            or not torch.isfinite(logitler).all():
        raise ValueError("logitler 1 boyutlu, sonlu bir tensör olmalı")
    if isinstance(sicaklik, bool) or not isinstance(sicaklik, (int, float)) or not 0.1 <= sicaklik <= 5:
        raise ValueError("sıcaklık 0.1-5 arası olmalı")
    if k is not None and (isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= logitler.shape[0]):
        raise ValueError("k geçersiz")
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not 0 < p <= 1:
        raise ValueError("p geçersiz")
    olas = torch.softmax(logitler.double() / sicaklik, dim=0)
    sira = torch.argsort(-olas, stable=True)          # eşitlikte küçük kimlik önce
    if k is not None:
        sira = sira[:k]
    kalan = olas[sira] / olas[sira].sum()
    adaylar, toplam = [], 0.0
    for i, q in zip(sira.tolist(), kalan.tolist()):
        adaylar.append(i)
        toplam += q
        if toplam >= p:
            break
    secili = olas[adaylar]
    return {"adaylar": adaylar, "olasiliklar": (secili / secili.sum()).tolist()}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_04 as deney
    deney.goster(ornekleme_dagilimi)
```

```hint
`torch.argsort(-olasiliklar, stable=True)` eşit olasılıklarda küçük kimliği öne alır. Top-p'yi top-k'dan kalan adayların yeniden normalize edilmiş olasılıklarıyla uygula; kümülatif toplamı adayı ekledikten **sonra** `p` ile karşılaştır.
```
:::
