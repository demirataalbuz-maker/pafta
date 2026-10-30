---
id: ai-temel-02
title: "Embeddingler: Tokenlerin Vektör Uzayına Taşınması"
summary: Token kimliklerini iki boyutlu sentetik embedding satırlarına eşle; kosinüs benzerliğini ve en yakın temsil seçimini uygula.
timeout: 45
---

::: anlat Embedding bir arama tablosudur
PyTorch embedding katmanı her token kimliği için öğrenilmiş bir vektör saklar. Kimlik doğrudan anlam taşımaz; anlam ilişkileri eğitim sırasında vektörlerin konumlarına yansır. Bu derste model veya PyTorch indirilmez; üç tokenlık, iki boyutlu sabit bir matris kullanılır.

Token kimlikleri matrisin satır indeksleridir. Aynı kimlik yinelendiğinde aynı vektör kopyalanır. Geçersiz kimliği sessizce başka satıra yöneltmek, üretim hattında yanlış temsili ve hatalı güvenlik kararını gizleyebilir.
:::

::: anlat Yakınlık yararlıdır ama anlam kanıtı değildir
Kosinüs benzerliği iki vektörün açısını ölçer ve büyüklüklerinin etkisini azaltır. Birden büyük değer veya sıfır normu geçerli sonuç değildir. En yakın vektörü seçerken eşitlikte küçük indeksin kazanması deterministik sonuç sağlar.

Benzer temsiller çoğu zaman ilişkili kavramları yakalar; ancak sentetik matriste olduğu gibi yakınlık tek başına doğruluk, güvenlik veya nedensellik kanıtı değildir. Retrieval ve sınıflandırma kararları ayrıca veriyle sınanmalıdır.
:::

::: tahmin Satır seçimini ve benzerliği tahmin et
Üç çıktı satırını yaz:

```python
m = [[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]]
print(m[2] + m[0])
print(round((1 * 1 + 1 * 0) / ((2 ** 0.5) * 1), 6))
print(max(range(3), key=lambda i: [0.0, 1.0, 0.7][i]))
```

???

```cikti
[1.0, 1.0, 1.0, 0.0]
0.707107
1
```

İlk satır bağımsız liste birleştirmeyi, ikinci satır `[1,1]` ile `[1,0]` arasındaki kosinüsü, üçüncü satır en yüksek benzerliğin indeksini gösterir.
:::

::: gorev 1 · Token kimliklerini embedding satırlarına çevir
`embedding_bak(matris, kimlikler)` işlevini yaz. Matris tam üç satırlı listedir; her satır iki adet, bool olmayan int/float değer içerir. Kimlikler 1–8 öğeli listedir; her öğe bool olmayan 0, 1 veya 2 tamsayısıdır. Geçersiz veride `ValueError` yükselt.

Kimlik sırasındaki satırları yeni iki öğeli listeler olarak döndür. Yinelenen kimliklere izin ver; matrisi ve kimlik listesini değiştirme.

```starter
def embedding_bak(matris, kimlikler):
    return []
```

```test
import copy
M = [[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]]
def sozlesme(fn):
    try:
        once = copy.deepcopy(M)
        if fn(M, [2, 0, 2]) != [[1.0, 1.0], [1.0, 0.0], [1.0, 1.0]] or M != once:
            return False
        sonuc = fn(M, [1] * 8)
        if len(sonuc) != 8 or any(x is M[1] for x in sonuc) or fn(M, [0]) != [[1.0, 0.0]]:
            return False
        for args in [(None, [0]), ([[0, 0]] * 2, [0]), ([[0, 0], [0], [0, 0]], [0]), ([[0], [0, 0], [0, 0]], [0]), ([[True, 0], [0, 0], [0, 0]], [0]), (M, None), (M, []), (M, [0] * 9), (M, [-1]), (M, [3]), (M, [True]), (M, [0.0])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(embedding_bak), "satır eşleme ve embedding şeması korunmalı")
def m_matris(m, k):
    return embedding_bak(list(reversed(m)), k)
def m_kimlik(m, k):
    return embedding_bak(m, [0] * len(k))
def m_uzun(m, k):
    return embedding_bak(m, k + k)
for ad, mutant in [("satırları değiştiren", m_matris), ("kimlikleri silen", m_kimlik), ("uzunluğu bozan", m_uzun)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def embedding_bak(matris, kimlikler):
    def sayi(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool)
    if not isinstance(matris, list) or len(matris) != 3:
        raise ValueError("matris geçersiz")
    if any(not isinstance(s, list) or len(s) != 2 or any(not sayi(x) for x in s) for s in matris):
        raise ValueError("satır geçersiz")
    if not isinstance(kimlikler, list) or not 1 <= len(kimlikler) <= 8:
        raise ValueError("kimlik listesi geçersiz")
    if any(not isinstance(k, int) or isinstance(k, bool) or not 0 <= k < 3 for k in kimlikler):
        raise ValueError("kimlik geçersiz")
    return [list(matris[k]) for k in kimlikler]
```

```hint
Önce bütün şemayı doğrula. Sonra liste üretiminde her kimlik için `list(matris[k])` kopyası oluştur.
```
:::

::: gorev 2 · Kosinüs benzerliğini hesapla
`kosinus(a, b)` işlevini yaz. İki girdi de iki adet bool olmayan int/float içeren listedir. Sıfır normlu vektör ve diğer geçersiz verilerde `ValueError` yükselt.

İki vektörün kosinüs benzerliğini hesapla, altı ondalığa yuvarla ve float döndür. Girdileri değiştirme.

```starter
def kosinus(a, b):
    return 0.0
```

```test
def sozlesme(fn):
    try:
        if fn([1, 0], [1, 0]) != 1.0 or fn([1, 0], [0, 2]) != 0.0:
            return False
        if fn([1, 1], [1, 0]) != 0.707107 or fn([1, 0], [-2, 0]) != -1.0:
            return False
        for args in [(None, [1, 0]), ([1], [1, 0]), ([1, 0, 0], [1, 0]), ([True, 0], [1, 0]), ([0, 0], [1, 0]), ([1, 0], [0, 0]), ("10", [1, 0])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kosinus), "kosinüs, yuvarlama ve sıfır norm reddi korunmalı")
def m_a(a, b):
    return kosinus(list(reversed(a)), b)
def m_b(a, b):
    return kosinus(a, [-x for x in b])
def m_boyut(a, b):
    return kosinus(a + [0], b + [0])
for ad, mutant in [("vektörü bozan", m_a), ("işareti bozan", m_b), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kosinus(a, b):
    import math
    def gecerli(v):
        return isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    if not gecerli(a) or not gecerli(b):
        raise ValueError("vektör geçersiz")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        raise ValueError("sıfır norm")
    return round(sum(x * y for x, y in zip(a, b)) / (na * nb), 6)
```

```hint
Nokta çarpımını iki normun çarpımına böl. Normlardan biri sıfırsa bölme yapmadan hata ver.
```
:::

::: gorev 3 · En yakın embedding satırını seç
`en_yakin_satir(vektor, matris)` işlevini yaz. Vektör ikinci görevdeki biçimde, matris ilk görevdeki üç satırlı biçimdedir; vektörlerden hiçbiri sıfır normlu olamaz. Geçersiz veride `ValueError` yükselt.

Vektörün her satırla kosinüs benzerliğini hesapla. En yüksek benzerlikli satırın indeksini döndür; eşitlikte küçük indeks kazanır. Girdileri değiştirme.

```starter
def en_yakin_satir(vektor, matris):
    return -1
```

```test
M = [[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]]
def sozlesme(fn):
    try:
        if fn([1, 0], M) != 0 or fn([0, 3], M) != 1 or fn([2, 2], M) != 2:
            return False
        esit = [[1, 0], [2, 0], [0, 1]]
        if fn([3, 0], esit) != 0:
            return False
        for args in [(None, M), ([0, 0], M), ([1], M), ([1, 0], None), ([1, 0], M[:2]), ([1, 0], [[0, 0], [1, 0], [0, 1]]), ([1, 0], [[True, 0], [1, 0], [0, 1]])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(en_yakin_satir), "en yakın satır ve eşitlik kuralı korunmalı")
def m_vektor(v, m):
    return en_yakin_satir(list(reversed(v)), m)
def m_matris(v, m):
    return en_yakin_satir(v, list(reversed(m)))
def m_secim(v, m):
    return 2
for ad, mutant in [("sorguyu bozan", m_vektor), ("satır sırasını bozan", m_matris), ("sabit seçim", m_secim)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def en_yakin_satir(vektor, matris):
    import math
    def gecerli(v):
        return isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    if not gecerli(vektor) or not isinstance(matris, list) or len(matris) != 3 or any(not gecerli(s) for s in matris):
        raise ValueError("girdi geçersiz")
    if math.sqrt(sum(x * x for x in vektor)) == 0 or any(math.sqrt(sum(x * x for x in s)) == 0 for s in matris):
        raise ValueError("sıfır norm")
    def benzerlik(s):
        return sum(x * y for x, y in zip(vektor, s)) / (math.sqrt(sum(x * x for x in vektor)) * math.sqrt(sum(x * x for x in s)))
    return max(range(3), key=lambda i: benzerlik(matris[i]))
```

```hint
`max(range(3), key=...)` küçük indeksten başlar ve yalnız daha büyük değerde seçimi değiştirir; böylece eşitlikte ilk satır kalır.
```
:::

::: anlat Gerçek deney: öğrenilmiş embedding tablosunu aç
Önceki üç satırlık matris öğretim içindi. Şimdi kurulu `SmolLM2-135M` modelinin **gerçek giriş embedding katmanını** kullanacağız. `ai_lab.dil_modeli()` yalnız yerel önbelleği okur; model yoksa görev geçmez. `model.get_input_embeddings()` her token kimliğinin öğrenilmiş vektörünü verir. Burada transformer ileri hesabı yapılmaz; elde ettiğimiz giriş embedding'i bağlama göre oluşan son katman gizli durumu değildir.

Metindeki aynı token kimliği hangi konumda olursa olsun aynı tablo satırını seçer. Farklı kimliklerin vektörleri arasındaki kosinüs, açısal yakınlıktır; metinlerin anlamını, doğruluğunu veya güvenliğini tek başına kanıtlamaz. Bu katman otomatik olarak bir cümle embedding modeli sayılmaz. Türkçe kelimeler birden fazla token olabilir; kelimeyle tokenı karıştırma.

Gerçek vektörler iki boyutlu değildir. Boyutu modelin embedding ağırlığının ikinci ekseninden öğren. Kosinüs matrisi için her satırı kendi L2 normuna bölüp normalize edilmiş matrisin transpozuyla çarp. Ham nokta çarpımı kosinüs değildir. Burada sıfır normlu bir satır çıkarsa sessizce bölmek yerine hata ver.
:::

::: gorev Gerçek deney · Gerçek embedding vektörleri ve kosinüs matrisi
`gercek_embedding_raporu(metin)` işlevini yaz:

- `metin`, boşluk dışı karakter içeren bir `str` olsun. Gerçek tokenizer'ın özel token eklemeden ürettiği token sayısı 1–16 aralığında olmalı. Geçersiz girdide `ValueError` yükselt. Metni kırpma; token sınırını aşan metni sessizce kesme.
- `tok, model, bilgi = ai_lab.dil_modeli()` ile kurulu gerçek modeli al. `tok(metin, add_special_tokens=False)["input_ids"]` kimliklerini sırayla kullan.
- `torch.no_grad()` içinde `model.get_input_embeddings()` katmanını gerçek kimlik tensörüyle çağır. Ham satırları `float64` hesapla kullan; kosinüs için normalize et ama döndüreceğin ham vektörleri değiştirme.
- Tam şu alanları döndür: `token_idleri` (int listesi), `boyut` (embedding boyutu int), `vektorler` (N×D float listesi), `kosinus` (N×N float listesi).

Sıra ve yinelenen kimlikler korunmalı. Modelin çıkış logitlerini, rastgele vektörleri veya yalnız normları döndürmek çözüm değildir. Sonuçlar yuvarlanmaz. Deneyin bütçesi kısa metindir; model eğitilmez ve GPU gerektirmez.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import ai_lab

def gercek_embedding_raporu(metin):
    return {}

if ai_lab.CALISTIR:
    d = gercek_embedding_raporu(" the the river")
    print(d)
```

```test
import copy
import random
import ai_lab

sonuclar = []
def kontrol(c, mesaj):
    sonuclar.append(bool(c))
    return ok(c, mesaj)

kontrol(not ai_lab.kod_denetimi(src), "laboratuvar yamalanmamalı")
fn = need("gercek_embedding_raporu")
try:
    import torch
    tok, model, bilgi = ai_lab.dil_modeli()
except (ImportError, ai_lab.GercekLabYok) as e:
    kontrol(False, "GERÇEK MODEL YOK: " + str(e))
    stop()

rng = random.SystemRandom()
metinler = ["hello", " the the river", " river the the", "İstanbul", "  model",
            rng.choice(["green", "blue", "red"]) + " " + rng.choice(["data", "music", "river"]) + " " + str(rng.randrange(100, 999))]

def referans(m):
    ids = tok(m, add_special_tokens=False)["input_ids"]
    if not 1 <= len(ids) <= 16:
        raise ValueError("token sayısı")
    with torch.no_grad():
        # Katman çağrısından bağımsız, gerçek ağırlık tablosundan satır seçimi.
        v = model.get_input_embeddings().weight.detach().index_select(0, torch.tensor(ids)).double()
        norm = torch.linalg.vector_norm(v, dim=1, keepdim=True)
        if bool((norm == 0).any()):
            raise ValueError("sıfır norm")
        birim = v / norm
        cos = birim @ birim.T
    return {"token_idleri": ids, "boyut": v.shape[1], "vektorler": v.tolist(), "kosinus": cos.tolist()}

beklenen = [referans(m) for m in metinler]
def ayni(a, b):
    try:
        if not isinstance(a, dict) or set(a) != set(b) or a["token_idleri"] != b["token_idleri"]:
            return False
        if type(a["boyut"]) is not int or a["boyut"] != b["boyut"] or any(type(i) is not int for i in a["token_idleri"]):
            return False
        for alan in ["vektorler", "kosinus"]:
            if not isinstance(a[alan], list) or any(not isinstance(row, list) or any(type(x) is not float for x in row) for row in a[alan]):
                return False
            x, y = torch.tensor(a[alan], dtype=torch.float64), torch.tensor(b[alan], dtype=torch.float64)
            if x.shape != y.shape or not bool(torch.isfinite(x).all()) or not torch.allclose(x, y, atol=1e-7, rtol=1e-6):
                return False
        return True
    except Exception:
        return False

uzun = " the" * 40
kontrol(len(tok(uzun, add_special_tokens=False)["input_ids"]) > 16, "sınır testi gerçekten token bütçesini aşıyor")
def sozlesme(f):
    try:
        for m, b in zip(metinler, beklenen):
            a = f(m)
            if not ayni(a, b):
                return False
            once = copy.deepcopy(a)
            f("a different word")
            if a != once:
                return False
        for m in ["", "   ", None, 42, True, [], b"hello", uzun]:
            try:
                f(m)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

kontrol(sozlesme(fn), "gerçek giriş embedding satırları, boyut, sıra ve kosinüs doğru")

def degistir(f):
    def s(m):
        if not isinstance(m, str) or not m.strip():
            raise ValueError("metin")
        return f(copy.deepcopy(referans(m)))
    return s
def ters(a):
    a["vektorler"].reverse()
    return a
def nokta(a):
    v = torch.tensor(a["vektorler"], dtype=torch.float64)
    a["kosinus"] = (v @ v.T).tolist()
    return a
def birim(a):
    v = torch.tensor(a["vektorler"], dtype=torch.float64)
    a["vektorler"] = (v / torch.linalg.vector_norm(v, dim=1, keepdim=True)).tolist()
    return a
sabit = beklenen[0]
for ad, mutant in [("boş kod/işlev", None), ("boş sözlük", lambda m: {}),
                   ("ezber vektörler", lambda m: copy.deepcopy(sabit)),
                   ("satır sırası ters", degistir(ters)),
                   ("kosinüs yerine nokta çarpımı", degistir(nokta)),
                   ("ham vektör yerine birim vektör", degistir(birim))]:
    kontrol(not sozlesme(mutant), "hatalı çözüm reddedilmeli: " + ad)

ciktilar = [fn(m) for m in metinler] if all(sonuclar) else []
for d in ciktilar:
    cos = torch.tensor(d["kosinus"], dtype=torch.float64)
    kontrol(torch.allclose(cos, cos.T, atol=1e-7) and torch.allclose(cos.diag(), torch.ones(len(cos), dtype=torch.float64), atol=1e-7), "kosinüs simetrik ve köşegeni bir")

# Herhangi bir konumda yinelenen kimlik varsa aynı tablo satırını verdiğini ayrıca göster.
tekrarlar = 0
for d in ciktilar:
    for i in range(len(d["token_idleri"])):
        for j in range(i):
            if d["token_idleri"][i] == d["token_idleri"][j]:
                tekrarlar += 1
                kontrol(d["vektorler"][i] == d["vektorler"][j], "aynı kimlik aynı giriş embedding satırını seçer")
kontrol(tekrarlar > 0, "gerçek metinler içinde yinelenen kimlik sınandı")

ai_lab.kanit_yaz("temel-02-embedding", {
    "kaynak": "gercek", "kabul": all(sonuclar), "model_bilgisi": bilgi,
    "islem": "gerçek öğrenilmiş giriş embedding tablosu; transformer ileri hesabı yok",
    "ayarlar": {"girdiler": metinler, "max_token": 16, "atol": 1e-7, "rtol": 1e-6},
    "ciktilar": ciktilar, "tekrarlanan_kimlik_ciftleri": tekrarlar,
    "temizlik": "CPU işlemi; dış sunucu veya kalıcı süreç açılmadı"})
for m, d in zip(metinler, ciktilar):
    print(repr(m), "→", len(d["token_idleri"]), "token ×", d["boyut"], "boyut; kimlikler", d["token_idleri"])
    print("ilk vektörün ilk 6 bileşeni:", d["vektorler"][0][:6], "kosinüs:", d["kosinus"])
```

```solution
import ai_lab
import torch

def gercek_embedding_raporu(metin):
    if not isinstance(metin, str) or not metin.strip():
        raise ValueError("boş olmayan metin gerekli")
    tok, model, _ = ai_lab.dil_modeli()
    ids = tok(metin, add_special_tokens=False)["input_ids"]
    if not 1 <= len(ids) <= 16:
        raise ValueError("1-16 token gerekli")
    with torch.no_grad():
        v = model.get_input_embeddings()(torch.tensor(ids)).double()
        norm = torch.linalg.vector_norm(v, dim=1, keepdim=True)
        if bool((norm == 0).any()):
            raise ValueError("sıfır norm")
        birim = v / norm
        cos = birim @ birim.T
    return {"token_idleri": ids, "boyut": v.shape[1], "vektorler": v.tolist(), "kosinus": cos.tolist()}

if ai_lab.CALISTIR:
    d = gercek_embedding_raporu(" the the river")
    print("Token kimlikleri:", d["token_idleri"], "boyut:", d["boyut"])
    print("İlk vektörün ilk 6 bileşeni:", d["vektorler"][0][:6])
    print("Kosinüs matrisi:", d["kosinus"])
```

```hint
`get_input_embeddings()` bir katmandır: kimlik tensörüyle çağır. `v / norm` ayrı hesap olsun; ham `v` döndürülecek. Boşlukları yalnız girdinin geçerliliğini kontrol ederken incele, tokenizer'a özgün metni ver.
```
:::
