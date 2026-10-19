---
id: p67
title: Proje · Kural Motoru
summary: Olaylara bildirimsel kurallar uygulayan motor; alan değiştiricileri, seçimler ve eval'siz ifade ayrıştırıcı.
---

::: anlat Proje tanımı
İzleme sistemleri saniyede binlerce **olay** üretir: servis logları, metrikler, uygulama hataları. Her olay için elle `if` yazmak yerine **bildirimsel kurallar** tanımlanır ve bir **motor** bu kuralları olaylara uygular. Kural yazan kişi Python bilmek zorunda kalmaz; kural bir veri yapısıdır.

Bu projede böyle bir motoru sıfırdan yazacaksın. Olaylar düz sözlüklerdir:

```python norun
{"servis": "odeme", "seviye": "ERROR", "mesaj": "Veritabanı zaman aşımı (5 sn)", "cpu": 93, "ortam": "prod"}
```

Bir kural şöyle görünür:

```python norun
{
    "ad": "Üretimde zaman aşımı",
    "secimler": {
        "hata": {"seviye": ["ERROR", "CRITICAL"], "mesaj|contains": "zaman aşımı"},
        "yuk":  {"cpu|gt": 90},
        "test": {"ortam": "test"},
    },
    "ifade": "(hata or yuk) and not test",
}
```

Okuma kuralları:

- Bir **seçimin** içindeki alanlar **VE** ile bağlanır: hepsi tutmalı
- Bir alanın değeri **liste** ise **VEYA** demektir: herhangi biri tutarsa yeter
- Alan adındaki `|` sonrası bir **değiştiricidir**: `contains`, `startswith`, `endswith`, `re`, `gt`, `lt`
- Metin karşılaştırmaları büyük-küçük harfe **duyarsızdır** (`re` hariç)
- `ifade` seçim adlarını `and`, `or`, `not` ve parantezlerle birleştirir

| Aşama | İş | Kullandığın paftalar |
|---|---|---|
| 1 | Tek alan eşleştirme + değiştiriciler | P05, P33, P23 dağıtım sözlüğü |
| 2 | Seçim eşleştirme (VE / VEYA) | P18 any/all |
| 3 | İfade ayrıştırıcı ve değerlendirici | P24 özyineleme, P62 |
| 4 | Motoru birleştirmek | hepsi |

> [!GÜVENLİK]
> 3. adımda ifadeyi `eval()` ile değerlendirmek cazip gelebilir: `eval("(hata or yuk) and not test", {}, sonuclar)` tek satırda çalışır. Ama kural dosyası dışarıdan geliyorsa `eval` o dosyayı yazan herkese **kod çalıştırma** yetkisi verir (P06, P62). Bu yüzden kendi küçük ayrıştırıcını yazacaksın: sadece izin verdiğin dilbilgisini anlar, başka hiçbir şeyi değil. Yol haritasındaki **Sigma** yolunda, SIEM'lerin tespit kurallarının aynı fikri nasıl kullandığını göreceksin.
:::

::: gorev 1 · Alan eşleştirme
`alan_eslesir(olay, anahtar, deger)` fonksiyonunu yaz. `anahtar` `"alan"` ya da `"alan|degistirici"` biçiminde olabilir:

| Değiştirici | Anlam |
|---|---|
| (yok) | eşitlik (metinlerde büyük-küçük harf duyarsız) |
| `contains` / `startswith` / `endswith` | metin içeriyor / ile başlıyor / ile bitiyor (duyarsız) |
| `re` | `re.search` (duyarlı) |
| `gt` / `lt` | sayısal büyüktür / küçüktür |

- `deger` bir liste ise elemanlardan **herhangi biri** tutması yeter
- Olayda alan yoksa `False`
- Bilinmeyen değiştiricide `ValueError`

> [!TUZAK]
> Türkçe metinde büyük-küçük harf dönüşümü tuzaklıdır: Python'un `lower()`'ı dilden bağımsızdır ve `"AŞIMI".lower()` → `"aşimi"` verir (noktasız ı değil, noktalı i). Yani `"ZAMAN AŞIMI"` ile `"zaman aşımı"` `lower()` sonrası **eşleşmez**. Türkçe için önce `"I"` → `"ı"` ve `"İ"` → `"i"` dönüşümü yapmak gerekir. Bu görevde testler bu duruma girmiyor, ama gerçek bir araçta mutlaka ele al.

```starter
import re

def alan_eslesir(olay, anahtar, deger):
    pass
```

```test
need("alan_eslesir")
o = {"servis": "odeme", "seviye": "ERROR", "mesaj": "Veritabanı zaman aşımı (5 sn)", "cpu": 93, "kod": 504}
eq(alan_eslesir(o, "servis", "odeme"), True, "eşitlik")
eq(alan_eslesir(o, "seviye", "error"), True, "büyük-küçük harf duyarsız eşitlik")
eq(alan_eslesir(o, "seviye", ["WARN", "ERROR"]), True, "liste = VEYA")
eq(alan_eslesir(o, "mesaj|contains", "ZAMAN"), True, "contains (duyarsız)")
eq(alan_eslesir(o, "mesaj|startswith", "veri"), True, "startswith")
eq(alan_eslesir(o, "mesaj|endswith", ["ms)", "sn)"]), True, "endswith + liste")
eq(alan_eslesir(o, "mesaj|re", r"\(\d+ sn\)"), True, "re")
eq(alan_eslesir(o, "mesaj|re", r"veritabanı"), False, "re büyük-küçük harfe duyarlı")
eq(alan_eslesir(o, "cpu|gt", 90), True, "gt")
eq(alan_eslesir(o, "cpu|lt", 90), False, "lt")
eq(alan_eslesir(o, "kod", 504), True, "sayı eşitliği")
eq(alan_eslesir(o, "olmayan", "x"), False, "eksik alan → False")
raises(ValueError, alan_eslesir, o, "mesaj|tersten", "x", msg="bilinmeyen değiştirici → ValueError")
```

```solution
import re

def _metin(x):
    return str(x).lower()

DEGISTIRICILER = {
    None: lambda a, b: _metin(a) == _metin(b) if isinstance(a, str) or isinstance(b, str) else a == b,
    "contains": lambda a, b: _metin(b) in _metin(a),
    "startswith": lambda a, b: _metin(a).startswith(_metin(b)),
    "endswith": lambda a, b: _metin(a).endswith(_metin(b)),
    "re": lambda a, b: re.search(b, str(a)) is not None,
    "gt": lambda a, b: a > b,
    "lt": lambda a, b: a < b,
}

def alan_eslesir(olay, anahtar, deger):
    alan, _, degistirici = anahtar.partition("|")
    karsilastir = DEGISTIRICILER.get(degistirici or None)
    if karsilastir is None:
        raise ValueError(f"bilinmeyen değiştirici: {degistirici}")
    if alan not in olay:
        return False
    degerler = deger if isinstance(deger, list) else [deger]
    return any(karsilastir(olay[alan], d) for d in degerler)
```

```hint
`anahtar.partition("|")` alan adını ve değiştiriciyi ayırır. Değiştiricileri bir **dağıtım sözlüğünde** (P23) lambda'larla tut.
```

```hint
Liste ya da tek değer farkını ortadan kaldır: `degerler = deger if isinstance(deger, list) else [deger]`, sonra `any(...)`.
```
:::

::: gorev 2 · Seçim eşleştirme
`secim_eslesir(olay, secim)` fonksiyonunu yaz:

- `secim` bir **sözlükse**: bütün alanlar tutmalı (VE)
- `secim` bir **sözlük listesiyse**: listedeki sözlüklerden **herhangi biri** tamamen tutmalı (VEYA)
- Boş sözlük her olayla eşleşir

Aşağıda 1. görevin bir çözümü hazır.

```starter
import re

def alan_eslesir(olay, anahtar, deger):
    alan, _, d = anahtar.partition("|")
    if alan not in olay:
        return False
    a = olay[alan]
    k = {"": lambda x, y: str(x).lower() == str(y).lower(), "contains": lambda x, y: str(y).lower() in str(x).lower(),
         "startswith": lambda x, y: str(x).lower().startswith(str(y).lower()),
         "endswith": lambda x, y: str(x).lower().endswith(str(y).lower()),
         "re": lambda x, y: re.search(y, str(x)) is not None, "gt": lambda x, y: x > y, "lt": lambda x, y: x < y}[d]
    return any(k(a, v) for v in (deger if isinstance(deger, list) else [deger]))

def secim_eslesir(olay, secim):
    pass
```

```test
need("secim_eslesir")
o = {"servis": "odeme", "seviye": "ERROR", "mesaj": "Veritabanı zaman aşımı", "cpu": 93}
eq(secim_eslesir(o, {"seviye": "ERROR", "mesaj|contains": "zaman"}), True, "iki alan da tutuyor")
eq(secim_eslesir(o, {"seviye": "ERROR", "servis": "sepet"}), False, "biri tutmuyor → False")
eq(secim_eslesir(o, [{"servis": "sepet"}, {"cpu|gt": 90}]), True, "listede biri tutuyor")
eq(secim_eslesir(o, [{"servis": "sepet"}, {"cpu|lt": 50}]), False, "listede hiçbiri tutmuyor")
eq(secim_eslesir(o, {}), True, "boş seçim her şeyle eşleşir")
```

```solution
import re

def alan_eslesir(olay, anahtar, deger):
    alan, _, d = anahtar.partition("|")
    if alan not in olay:
        return False
    a = olay[alan]
    k = {"": lambda x, y: str(x).lower() == str(y).lower(), "contains": lambda x, y: str(y).lower() in str(x).lower(),
         "startswith": lambda x, y: str(x).lower().startswith(str(y).lower()),
         "endswith": lambda x, y: str(x).lower().endswith(str(y).lower()),
         "re": lambda x, y: re.search(y, str(x)) is not None, "gt": lambda x, y: x > y, "lt": lambda x, y: x < y}[d]
    return any(k(a, v) for v in (deger if isinstance(deger, list) else [deger]))

def secim_eslesir(olay, secim):
    if isinstance(secim, list):
        return any(secim_eslesir(olay, s) for s in secim)
    return all(alan_eslesir(olay, anahtar, deger) for anahtar, deger in secim.items())
```

```hint
Sözlük için `all(...)`, liste için kendini her sözlükle çağırıp `any(...)`. `all([])` True döner: boş seçim kendiliğinden doğru olur.
```
:::

::: gorev 3 · İfade ayrıştırıcı
`ifade_degerlendir(ifade, sonuclar)` fonksiyonunu **`eval` kullanmadan** yaz. `sonuclar`, seçim adı → bool sözlüğüdür. Dilbilgisi (öncelik: `not` > `and` > `or`):

```text
ifade  := terim ("or" terim)*
terim  := faktor ("and" faktor)*
faktor := "not" faktor | "(" ifade ")" | AD
```

- `sonuclar`'da olmayan bir ad → `NameError`
- Sözdizimi bozuksa (eşleşmeyen parantez, eksik işlenen, fazla sözcük) → `SyntaxError`

```starter
import re

def ifade_degerlendir(ifade, sonuclar):
    pass
```

```test
need("ifade_degerlendir")
s = {"a": True, "b": False, "c": True}
eq(ifade_degerlendir("a", s), True, "tek ad")
eq(ifade_degerlendir("a and b", s), False, "and")
eq(ifade_degerlendir("a and not b", s), True, "and not")
eq(ifade_degerlendir("b or c", s), True, "or")
eq(ifade_degerlendir("not a or c", s), True, "not önceliği: (not a) or c")
eq(ifade_degerlendir("b and c or a", s), True, "and önce: (b and c) or a")
eq(ifade_degerlendir("b and (c or a)", s), False, "parantez")
eq(ifade_degerlendir("not (a and (b or not c))", s), True, "iç içe parantez")
raises(NameError, ifade_degerlendir, "a and x", s, msg="bilinmeyen ad → NameError")
raises(SyntaxError, ifade_degerlendir, "(a and b", s, msg="kapanmamış parantez → SyntaxError")
raises(SyntaxError, ifade_degerlendir, "a and", s, msg="eksik işlenen → SyntaxError")
raises(SyntaxError, ifade_degerlendir, "a b", s, msg="fazla sözcük → SyntaxError")
ok(not calls("eval") and not calls("exec") and not calls("compile"), "eval/exec/compile kullanmadan")
```

```solution
import re

def ifade_degerlendir(ifade, sonuclar):
    jetonlar = re.findall(r"\(|\)|[A-Za-z_]\w*|\S", ifade)
    konum = 0

    def bak():
        return jetonlar[konum] if konum < len(jetonlar) else None

    def al(beklenen=None):
        nonlocal konum
        j = bak()
        if j is None or (beklenen is not None and j != beklenen):
            raise SyntaxError(f"beklenen {beklenen or 'ifade'}, gelen {j!r}")
        konum += 1
        return j

    def ifade_():
        deger = terim()
        while bak() == "or":
            al("or")
            sag = terim()
            deger = deger or sag
        return deger

    def terim():
        deger = faktor()
        while bak() == "and":
            al("and")
            sag = faktor()
            deger = deger and sag
        return deger

    def faktor():
        j = bak()
        if j == "not":
            al("not")
            return not faktor()
        if j == "(":
            al("(")
            deger = ifade_()
            al(")")
            return deger
        if j is None or not re.fullmatch(r"[A-Za-z_]\w*", j) or j in ("and", "or"):
            raise SyntaxError(f"beklenmeyen {j!r}")
        al()
        if j not in sonuclar:
            raise NameError(f"bilinmeyen seçim: {j}")
        return bool(sonuclar[j])

    sonuc = ifade_()
    if konum != len(jetonlar):
        raise SyntaxError(f"fazla sözcük: {bak()!r}")
    return sonuc
```

```hint
Önce metni jetonlara böl: `re.findall(r"\(|\)|[A-Za-z_]\w*|\S", ifade)`. Sonra dilbilgisindeki her kural için bir fonksiyon yaz (özyinelemeli iniş: `ifade_ → terim → faktor`), ortak bir konum değişkeniyle ilerle.
```

```hint
Sağ tarafı mutlaka ayrıştır, kısa devreyle atlama: `deger = deger or terim()` yazarsan `deger` doğruyken `terim()` hiç çağrılmaz ve jetonlar tüketilmez. Önce `sag = terim()`, sonra birleştir.
```
:::

::: gorev 4 · Motor
`motor(kurallar, olaylar)` fonksiyonu her kuralı her olaya uygulasın ve eşleşmeleri `(kural_adı, olay_indeksi)` demetleri olarak döndürsün: önce olay sırasına, sonra kuralların sırasına göre. Bir kuralın değerlendirmesi: her seçimi `secim_eslesir` ile hesapla, sonuçları `ifade_degerlendir`'e ver.

Önceki görevlerin çözümleri aşağıda hazır.

```starter
import re

def alan_eslesir(olay, anahtar, deger):
    alan, _, d = anahtar.partition("|")
    if alan not in olay:
        return False
    a = olay[alan]
    k = {"": lambda x, y: str(x).lower() == str(y).lower(), "contains": lambda x, y: str(y).lower() in str(x).lower(),
         "startswith": lambda x, y: str(x).lower().startswith(str(y).lower()),
         "endswith": lambda x, y: str(x).lower().endswith(str(y).lower()),
         "re": lambda x, y: re.search(y, str(x)) is not None, "gt": lambda x, y: x > y, "lt": lambda x, y: x < y}[d]
    return any(k(a, v) for v in (deger if isinstance(deger, list) else [deger]))

def secim_eslesir(olay, secim):
    if isinstance(secim, list):
        return any(secim_eslesir(olay, s) for s in secim)
    return all(alan_eslesir(olay, a, d) for a, d in secim.items())

def ifade_degerlendir(ifade, sonuclar):
    j = re.findall(r"\(|\)|[A-Za-z_]\w*|\S", ifade)
    i = 0
    def bak():
        return j[i] if i < len(j) else None
    def al(b=None):
        nonlocal i
        if bak() is None or (b and bak() != b):
            raise SyntaxError(bak())
        i += 1
        return j[i - 1]
    def ifd():
        v = trm()
        while bak() == "or":
            al(); s = trm(); v = v or s
        return v
    def trm():
        v = fkt()
        while bak() == "and":
            al(); s = fkt(); v = v and s
        return v
    def fkt():
        if bak() == "not":
            al(); return not fkt()
        if bak() == "(":
            al(); v = ifd(); al(")"); return v
        ad = al()
        if ad not in sonuclar:
            raise NameError(ad)
        return bool(sonuclar[ad])
    v = ifd()
    if i != len(j):
        raise SyntaxError(bak())
    return v

def motor(kurallar, olaylar):
    pass
```

```test
need("motor")
kurallar = [
    {"ad": "Üretimde zaman aşımı",
     "secimler": {"hata": {"seviye": ["ERROR", "CRITICAL"], "mesaj|contains": "zaman aşımı"},
                  "yuk": {"cpu|gt": 90}, "test": {"ortam": "test"}},
     "ifade": "(hata or yuk) and not test"},
    {"ad": "Disk dolmak üzere",
     "secimler": {"disk": {"metrik": "disk", "deger|gt": 85}},
     "ifade": "disk"},
]
olaylar = [
    {"servis": "odeme", "seviye": "ERROR", "mesaj": "Veritabanı zaman aşımı", "cpu": 40, "ortam": "prod"},
    {"servis": "odeme", "seviye": "INFO", "mesaj": "ok", "cpu": 95, "ortam": "test"},
    {"metrik": "disk", "deger": 91, "ortam": "prod"},
    {"servis": "sepet", "seviye": "WARN", "mesaj": "yavaş", "cpu": 97, "ortam": "prod"},
    {"metrik": "disk", "deger": 40},
]
eq(motor(kurallar, olaylar), [("Üretimde zaman aşımı", 0), ("Disk dolmak üzere", 2), ("Üretimde zaman aşımı", 3)], "eşleşmeler")
eq(motor([], olaylar), [], "kural yok")
eq(motor(kurallar, []), [], "olay yok")
```

```solution
import re

def alan_eslesir(olay, anahtar, deger):
    alan, _, d = anahtar.partition("|")
    if alan not in olay:
        return False
    a = olay[alan]
    k = {"": lambda x, y: str(x).lower() == str(y).lower(), "contains": lambda x, y: str(y).lower() in str(x).lower(),
         "startswith": lambda x, y: str(x).lower().startswith(str(y).lower()),
         "endswith": lambda x, y: str(x).lower().endswith(str(y).lower()),
         "re": lambda x, y: re.search(y, str(x)) is not None, "gt": lambda x, y: x > y, "lt": lambda x, y: x < y}[d]
    return any(k(a, v) for v in (deger if isinstance(deger, list) else [deger]))

def secim_eslesir(olay, secim):
    if isinstance(secim, list):
        return any(secim_eslesir(olay, s) for s in secim)
    return all(alan_eslesir(olay, a, d) for a, d in secim.items())

def ifade_degerlendir(ifade, sonuclar):
    j = re.findall(r"\(|\)|[A-Za-z_]\w*|\S", ifade)
    i = 0
    def bak():
        return j[i] if i < len(j) else None
    def al(b=None):
        nonlocal i
        if bak() is None or (b and bak() != b):
            raise SyntaxError(bak())
        i += 1
        return j[i - 1]
    def ifd():
        v = trm()
        while bak() == "or":
            al(); s = trm(); v = v or s
        return v
    def trm():
        v = fkt()
        while bak() == "and":
            al(); s = fkt(); v = v and s
        return v
    def fkt():
        if bak() == "not":
            al(); return not fkt()
        if bak() == "(":
            al(); v = ifd(); al(")"); return v
        ad = al()
        if ad not in sonuclar:
            raise NameError(ad)
        return bool(sonuclar[ad])
    v = ifd()
    if i != len(j):
        raise SyntaxError(bak())
    return v

def motor(kurallar, olaylar):
    eslesmeler = []
    for i, olay in enumerate(olaylar):
        for kural in kurallar:
            sonuclar = {ad: secim_eslesir(olay, secim) for ad, secim in kural["secimler"].items()}
            if ifade_degerlendir(kural["ifade"], sonuclar):
                eslesmeler.append((kural["ad"], i))
    return eslesmeler
```

```hint
Dış döngü olaylar (`enumerate`), iç döngü kurallar. Her kural için `{ad: secim_eslesir(olay, secim) ...}` sözlüğünü üret ve ifadeye ver.
```
:::
