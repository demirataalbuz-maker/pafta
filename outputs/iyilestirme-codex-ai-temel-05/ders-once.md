---
id: ai-temel-05
title: "Attention: Query, Key ve Value"
summary: İki boyutlu sentetik Q/K/V projeksiyonu, ölçekli dikkat skoru ve ağırlıklı bağlam hesapla.
timeout: 45
---

::: anlat Q/K/V aynı tokenın farklı rolleridir
Query bilgi arayan temsili, Key eşleşme ölçütünü, Value ise aktarılacak içeriği ifade eder. Lineer projeksiyonlar girdi vektörünü bu rollere taşır. PyTorch üzerindeki matris çarpımlarının küçük bir liste karşılığını kullanacağız; model veya kütüphane indirilmez.

Query ile her Key arasındaki nokta çarpım dikkat skorunu verir. Skor Key boyutunun kareköküne bölünür; ölçekleme büyük boyutlarda softmax doyumunu azaltır.
:::

::: anlat Attention Value içeriklerinin karışımıdır
Skorlar softmax ile ağırlığa dönüşür ve her Value bu ağırlıkla toplanır. Böylece güçlü eşleşen tokenların içeriği bağlamda daha fazla yer kaplar. Dikkat ağırlığı tek başına nedensel açıklama veya güvenlik kanıtı değildir.

Aşağıdaki görevlerde bütün boyutlar sabittir. Amaç büyük model çalıştırmak değil, projeksiyon, skor ve bağlam adımlarının birbirinden farklı olduğunu doğrulamaktır.
:::

::: tahmin Skor ve bağlamı tahmin et
Üç çıktı satırını yaz:

```python
print([1 * 2 + 0 * 1, 1 * 0 + 0 * 3])
print(round((1 * 1 + 0 * 0) / (2 ** 0.5), 6))
print([round(0.25 * 2 + 0.75 * 4, 3), round(0.25 * 1 + 0.75 * 0, 3)])
```

???

```cikti
[2, 0]
0.707107
[3.5, 0.25]
```

İlk satır Q projeksiyonunu, ikinci satır ölçekli skoru, üçüncü satır iki Value vektörünün ağırlıklı karışımını gösterir.
:::

::: gorev 1 · İki boyutlu lineer projeksiyon uygula
`projeksiyon(vektor, agirlik)` işlevini yaz. Vektör iki sayı, ağırlık iki satır ve iki sütundan oluşan sayı listesidir; bool değerler geçersizdir. Diğer geçersiz veride de `ValueError` yükselt.

Çıktının i. öğesi girdi vektörüyle ağırlığın i. satırının nokta çarpımıdır. Yeni iki öğeli liste döndür; girdileri değiştirme.

```starter
def projeksiyon(vektor, agirlik):
    return []
```

```test
W = [[2, 1], [0, 3]]
def sozlesme(fn):
    try:
        if fn([1, 0], W) != [2, 0] or fn([1, 2], W) != [4, 6] or fn([-1, 1], W) != [-1, 3]:
            return False
        for args in [(None, W), ([1], W), ([1, True], W), ([1, 2], None), ([1, 2], [[1, 0]]), ([1, 2], [[1], [0, 1]]), ([1, 2], [[1, 0], [False, 1]])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(projeksiyon), "satır nokta çarpımı ve matris şeması korunmalı")
def m_vektor(v, w):
    return projeksiyon(list(reversed(v)), w)
def m_agirlik(v, w):
    return projeksiyon(v, list(reversed(w)))
def m_boyut(v, w):
    return projeksiyon(v + [0], w)
for ad, mutant in [("vektörü bozan", m_vektor), ("ağırlığı bozan", m_agirlik), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def projeksiyon(vektor, agirlik):
    def satir(x):
        return isinstance(x, list) and len(x) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x)
    if not satir(vektor) or not isinstance(agirlik, list) or len(agirlik) != 2 or any(not satir(s) for s in agirlik):
        raise ValueError("projeksiyon geçersiz")
    return [sum(vektor[j] * satir_agirlik[j] for j in range(2)) for satir_agirlik in agirlik]
```

```hint
Her ağırlık satırı için iki çarpımın toplamını al; satırları sütunlarla karıştırma.
```
:::

::: gorev 2 · Ölçekli Q/K skorlarını hesapla
`dikkat_skorlari(query, keys)` işlevini yaz. Query iki sayıdır; keys tam üç adet iki sayılık vektör listesidir. Bool ve diğer geçersiz verilerde `ValueError` yükselt.

Her skoru Query ile Key nokta çarpımının `sqrt(2)` değerine bölünmesiyle hesapla ve altı ondalığa yuvarla. Üç skoru Key sırasıyla döndür.

```starter
def dikkat_skorlari(query, keys):
    return []
```

```test
K = [[1, 0], [0, 1], [-1, 0]]
def sozlesme(fn):
    try:
        if fn([1, 0], K) != [0.707107, 0.0, -0.707107] or fn([0, 0], K) != [0.0, 0.0, 0.0]:
            return False
        if fn([2, 1], K) != [1.414214, 0.707107, -1.414214]:
            return False
        for args in [(None, K), ([1], K), ([1, True], K), ([1, 0], None), ([1, 0], K[:2]), ([1, 0], [[1], [0, 1], [1, 0]]), ([1, 0], [[1, 0], [False, 1], [1, 0]])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dikkat_skorlari), "ölçek, skor sırası ve Q/K şeması korunmalı")
def m_query(q, k):
    return dikkat_skorlari(list(reversed(q)), k)
def m_keys(q, k):
    return dikkat_skorlari(q, list(reversed(k)))
def m_boyut(q, k):
    return dikkat_skorlari(q, k + [[0, 0]])
for ad, mutant in [("queryyi bozan", m_query), ("key sırasını bozan", m_keys), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def dikkat_skorlari(query, keys):
    import math
    def vektor(x):
        return isinstance(x, list) and len(x) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x)
    if not vektor(query) or not isinstance(keys, list) or len(keys) != 3 or any(not vektor(k) for k in keys):
        raise ValueError("Q/K geçersiz")
    return [round(sum(query[j] * k[j] for j in range(2)) / math.sqrt(2), 6) for k in keys]
```

```hint
Her Key için iki öğeli nokta çarpımı hesapla; sonucu `math.sqrt(2)` ile böl.
```
:::

::: gorev 3 · Softmax ağırlıklı Value bağlamını üret
`attention_baglam(query, keys, values)` işlevini yaz. Query ve Keys ikinci görevdeki biçimdedir; Values da üç adet iki sayılık vektördür. Geçersiz veride `ValueError` yükselt.

Ölçekli skorlara kararlı softmax uygula. Her Value satırını ilgili ağırlıkla toplayarak iki boyutlu bağlam üret ve öğeleri altı ondalığa yuvarla. Girdileri değiştirme.

```starter
def attention_baglam(query, keys, values):
    return []
```

```test
K = [[1, 0], [1, 0], [0, 1]]
V = [[1, 0], [0, 1], [2, 2]]
def sozlesme(fn):
    try:
        if fn([1, 0], K, V) != [0.796664, 0.796664]:
            return False
        if fn([0, 0], K, V) != [1.0, 1.0] or fn([0, 1], K, [[2, 0], [2, 0], [0, 4]]) != [0.99302, 2.013959]:
            return False
        for args in [(None, K, V), ([1], K, V), ([1, 0], K[:2], V), ([1, 0], K, V[:2]), ([1, 0], K, [[1], [0, 1], [1, 0]]), ([1, True], K, V)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(attention_baglam), "softmax ve Value karışımı korunmalı")
def m_query(q, k, v):
    return attention_baglam(list(reversed(q)), k, v)
def m_keys(q, k, v):
    return attention_baglam(q, list(reversed(k)), v)
def m_values(q, k, v):
    return attention_baglam(q, k, list(reversed(v)))
for ad, mutant in [("queryyi bozan", m_query), ("keyleri bozan", m_keys), ("valueları bozan", m_values)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def attention_baglam(query, keys, values):
    import math
    def vektor(x):
        return isinstance(x, list) and len(x) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x)
    if not vektor(query) or not isinstance(keys, list) or len(keys) != 3 or any(not vektor(k) for k in keys):
        raise ValueError("Q/K geçersiz")
    if not isinstance(values, list) or len(values) != 3 or any(not vektor(v) for v in values):
        raise ValueError("Value geçersiz")
    skorlar = [sum(query[j] * k[j] for j in range(2)) / math.sqrt(2) for k in keys]
    tepe = max(skorlar)
    paylar = [math.exp(x - tepe) for x in skorlar]
    agirliklar = [x / sum(paylar) for x in paylar]
    return [round(sum(agirliklar[i] * values[i][j] for i in range(3)), 6) for j in range(2)]
```

```hint
Önce üç skoru ve softmax ağırlığını hesapla. Çıktının her boyutunda üç Value satırının aynı boyutunu ağırlıklı topla.
```
:::

::: anlat Gerçek modelde dikkat: bir katman, bir kafa
Yukarıdaki görevler iki boyutlu, elle seçilmiş vektörlerle çalıştı. SmolLM2-135M'nin her katmanında 9 dikkat kafası vardır ve her kafa 64 boyutlu Query/Key/Value vektörleriyle çalışır. Laboratuvar, seçilen katman ve kafa için Q/K/V'yi modelin **kendi** projeksiyon ağırlıklarından ve konum kodlamasından (RoPE) çıkarır; senin hesabın modelin o kafada gerçekten ürettiği çıktıyla karşılaştırılır.

Dil modeli **nedenseldir**: bir token yalnız kendisine ve önceki tokenlara bakabilir. Bu yüzden skor matrisinde geleceğe denk gelen hücreler softmax'tan **önce** `-inf` yapılır; softmax sonrası sıfırlamak satırları yeniden normalize etmediği için yanlıştır. Gruplu sorgu dikkatinde (GQA) birkaç Query kafası aynı Key/Value kafasını paylaşır; laboratuvar bunu senin yerine eşler.
:::

::: gorev Gerçek deney · Gerçek bir kafada nedensel dikkat
`nedensel_dikkat(q, k, v)` işlevini yaz. `q`, `k`, `v` aynı biçimde `[T, d]` `torch.Tensor`'lardır (T token, d kafa boyutu).

- Doğrulama, aksi hâlde `ValueError`: üçü de `torch.Tensor`, 2 boyutlu, aynı biçimde, T ≥ 1, d ≥ 1, bütün değerler sonlu.
- Hesabı **float64** yap: `skor = q @ kᵀ / √d`.
- `j > i` olan hücreleri (gelecek tokenlar) softmax'tan önce `-inf` ile maskele.
- Softmax'ı her satırda (Key ekseninde) uygula; `baglam = agirliklar @ v`.
- Döndür: `{"agirliklar": [T, T] tensör, "baglam": [T, d] tensör}`.

Test rastgele bir cümlede rastgele katman ve kafa seçer, sonucunu bağımsız bir hesapla **ve modelin o kafadaki gerçek çıktısıyla** karşılaştırır. Çalıştır düğmesi bir kafanın dikkat haritasını ve katmanlara göre ilk tokena giden dikkati (attention sink) gösterir. Laboratuvardaki `referans` işlevini çağırma.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import torch
import ai_lab

def nedensel_dikkat(q, k, v):
    return {"agirliklar": None, "baglam": None}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_05 as deney
    deney.goster(nedensel_dikkat)
```

```test
import random
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "kafa_girdileri", "getattr", "scaled_dot_product_attention"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans/hazır dikkat işlevi çağrılmamalı " + ", ".join(sorun))
fn = need("nedensel_dikkat")
try:
    from sandbox import ai_gercek_ai_temel_05 as D
    tok, model, bilgi = ai_lab.dil_modeli()
    import torch
except ai_lab.GercekLabYok as e:
    kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
    stop()
rnd = random.Random()
L, H = model.config.num_hidden_layers, model.config.num_attention_heads
ozne = ["The engineer", "My sister", "The old robot", "A small bird", "Our teacher"]
eylem = ["fixed the server", "found the key", "opened the door", "read the report", "sang a song"]
rastgele = f"{rnd.choice(ozne)} {rnd.choice(eylem)} because it was {rnd.choice(['late', 'broken', 'raining', 'quiet'])}"
vakalar = [(D.DENEY_METNI, 3, 4), (D.DENEY_METNI, 0, 0), (rastgele, rnd.randrange(L), rnd.randrange(H)),
           (rastgele, rnd.randrange(L), rnd.randrange(H))]
girdiler = [D.kafa_girdileri(m, kat, kf) for m, kat, kf in vakalar]
def ayni(a, b):
    if not isinstance(a, dict) or set(a) != {"agirliklar", "baglam"}:
        return False
    for ad in ("agirliklar", "baglam"):
        x, y = a[ad], b[ad]
        if not isinstance(x, torch.Tensor) or x.shape != y.shape or not torch.isfinite(x).all():
            return False
        if (x.double() - y).abs().max().item() > 1e-9:
            return False
    return True
def sozlesme(f):
    try:
        for q, k, v, _, _ in girdiler:
            if not ayni(f(q.clone(), k.clone(), v.clone()), D.referans(q, k, v)):
                return False
        q, k, v = girdiler[0][:3]
        for arg in [(None, k, v), (q.tolist(), k, v), (q[0], k[0], v[0]), (q, k[:-1], v), (q, k, v[:, :-1]),
                    (q.unsqueeze(0), k.unsqueeze(0), v.unsqueeze(0)), (q[:0], k[:0], v[:0]),
                    (torch.full_like(q, float("nan")), k, v)]:
            try:
                f(*arg)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "gerçek Q/K/V: ölçekli skor, softmax öncesi nedensel maske, satır softmax'ı ve bağlam doğru")
def gecerli(f):
    def sarmal(q, k, v):
        if not all(isinstance(t, torch.Tensor) for t in (q, k, v)) or q.dim() != 2 or q.shape != k.shape or q.shape != v.shape \
                or q.shape[0] < 1 or q.shape[1] < 1 or not all(torch.isfinite(t).all() for t in (q, k, v)):
            raise ValueError("geçersiz")
        return f(q, k, v)
    return sarmal
sabit = D.referans(*girdiler[0][:3])
for ad, kw in [("ölçekleme yok", {"olcek": "yok"}), ("√d yerine d ile bölme", {"olcek": "d"}), ("nedensel maske yok", {"maske": False}),
               ("maske softmax'tan sonra", {"maske_sonra": True}), ("softmax yanlış eksende", {"softmax_boyutu": 0}),
               ("Value yerine Query karıştırılıyor", {"deger": False})]:
    kontrol(not sozlesme(gecerli(lambda q, k, v, kw=kw: D.referans(q, k, v, **kw))), "hatalı çözüm reddedilmeli: " + ad)
kontrol(not sozlesme(gecerli(lambda q, k, v: sabit)), "hatalı çözüm reddedilmeli: ezber tablo")
model_farki = []
if all(sonuclar):
    for q, k, v, model_c, _ in girdiler:
        model_farki.append((fn(q, k, v)["baglam"].double() - model_c.double()).abs().max().item())
    kontrol(max(model_farki) < 1e-4, f"senin bağlamın modelin o kafadaki gerçek çıktısıyla aynı (en büyük fark {max(model_farki):.1e})")
sink = D.sink_orani(fn) if all(sonuclar) else {}
yol = ai_lab.kanit_yaz("temel-dikkat", {
    "kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-temel-05", "model_bilgisi": bilgi,
    "ayarlar": {"vakalar": [list(v) for v in vakalar], "tolerans": {"referans": 1e-9, "model": 1e-4}},
    "tokenlar": [g[4] for g in girdiler], "model_farki": model_farki, "sink": sink})
if sink:
    ok(True, f"GERÇEK ÇIKTI ({bilgi['model']}@{bilgi['revizyon'][:8]}): modelle en büyük fark {max(model_farki):.1e}; "
             f"4. tokendan itibaren ilk tokena giden ortalama dikkat, katman→oran: {sink}")
```

```solution
import torch
import ai_lab

def nedensel_dikkat(q, k, v):
    if not all(isinstance(t, torch.Tensor) for t in (q, k, v)):
        raise ValueError("q, k, v tensör olmalı")
    if q.dim() != 2 or q.shape != k.shape or q.shape != v.shape or q.shape[0] < 1 or q.shape[1] < 1:
        raise ValueError("q, k, v aynı [T, d] biçiminde olmalı")
    if not all(torch.isfinite(t).all() for t in (q, k, v)):
        raise ValueError("değerler sonlu olmalı")
    q, k, v = q.double(), k.double(), v.double()
    T, d = q.shape
    skor = q @ k.T / d ** 0.5
    gelecek = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
    skor = skor.masked_fill(gelecek, float("-inf"))
    agirliklar = torch.softmax(skor, dim=-1)
    return {"agirliklar": agirliklar, "baglam": agirliklar @ v}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_05 as deney
    deney.goster(nedensel_dikkat)
```

```hint
`torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)` köşegenin üstünü, yani gelecek tokenları işaretler. `masked_fill(..., float("-inf"))` softmax'tan önce gelir; softmax `dim=-1` ile her satırda (bir Query'nin bütün Key'leri üzerinde) alınır.
```
:::
