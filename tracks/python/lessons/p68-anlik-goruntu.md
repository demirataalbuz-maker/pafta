---
id: p68
title: Proje · Klasör Anlık Görüntüsü
summary: Bir klasörün özet tabanlı anlık görüntüsünü alıp imzalı saklayan ve sonradan değişiklikleri raporlayan araç.
---

::: anlat Proje tanımı
Bir sunucuya uygulama dağıttın ya da önemli bir klasörün yedeğini aldın. Sonra şu soruyu sorman gerekiyor: **bu klasördeki dosyalar hâlâ bıraktığım gibi mi?** Bir güncelleme bir dosyayı değiştirmiş, bir betik yeni dosya bırakmış ya da yanlışlıkla bir şey silinmiş olabilir.

Bu projede bir **anlık görüntü** (snapshot) aracı yazacaksın:

1. Klasördeki her dosyanın SHA-256 özetini çıkar (P49)
2. Görüntüyü JSON olarak kaydet ve **HMAC ile imzala**, böylece görüntü dosyasının kendisi sonradan değiştirilirse fark edilsin (P49)
3. Daha sonra klasörü yeniden tara ve eklenen, silinen ve değişen dosyaları raporla

| Aşama | Kullandığın paftalar |
|---|---|
| Klasörü gezmek, desenle hariç tutmak | P28 pathlib, `fnmatch` |
| Parça parça özet | P49 hashlib |
| İmzalı JSON | P29 json, P49 hmac |
| Fark raporu | P17 kümeler |

Görüntü, göreli yol (`/` ayraçlı) → onaltılık özet sözlüğüdür:

```python norun
{"config/app.ini": "9f2c…", "bin/servis": "e3b0…", "README.md": "4a1d…"}
```

> [!NOT]
> Bu fikrin profesyonel karşılıkları: Git (her dosya özetiyle adreslenir), `rsync` ve yedekleme araçlarının değişiklik tespiti, paket yöneticilerinin bütünlük doğrulaması ve sistem yöneticilerinin dosya bütünlüğü izleme araçları (AIDE, Tripwire). Hepsinin özünde aynı üçlü var: **özetle, sakla, karşılaştır**.

> [!DERİN]
> Görüntüyü neden imzalıyoruz? Görüntü dosyası klasörün yanında duruyorsa, dosyaları değiştirebilen biri görüntüyü de yeni özetlerle güncelleyip değişikliği gizleyebilir. HMAC anahtarı başka bir yerde (ör. bir parola kasasında) tutulursa, görüntüyü anahtarsız yeniden imzalamak mümkün olmaz. Kanonik JSON (`sort_keys=True`) imzalamak önemlidir: aynı veri her zaman aynı baytlara dönüşmeli.
:::

::: gorev 1 · Anlık görüntü
`anlik_goruntu(kok, haric=())` fonksiyonu `kok` altındaki **bütün dosyaları** (alt klasörler dahil) gezsin ve `{göreli_yol: sha256_hex}` sözlüğünü döndürsün:

- Göreli yollar `/` ayraçlı olsun (`as_posix()`)
- Dosyaları ikilik kipte, parça parça özetle
- `haric` içindeki `fnmatch` desenlerinden biri göreli yola **ya da** dosya adına uyuyorsa o dosyayı atla (ör. `"*.tmp"`, `"cache/*"`)

```setup
from pathlib import Path
dosyalar = {"uygulama/README.md": b"# Uygulama\n", "uygulama/config/app.ini": b"[db]\nport=5432\n",
            "uygulama/bin/servis": bytes(range(256)) * 50, "uygulama/gecici.tmp": b"silinecek",
            "uygulama/cache/a.bin": b"onbellek"}
for yol, icerik in dosyalar.items():
    p = Path(yol)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(icerik)
```

```starter
import hashlib, fnmatch
from pathlib import Path

def anlik_goruntu(kok, haric=()):
    pass
```

```test
import hashlib
from pathlib import Path
need("anlik_goruntu")
g = anlik_goruntu("uygulama", haric=("*.tmp", "cache/*"))
eq(sorted(g), ["README.md", "bin/servis", "config/app.ini"], "hariç tutulanlar dışındaki dosyalar")
eq(g["config/app.ini"], hashlib.sha256(b"[db]\nport=5432\n").hexdigest(), "doğru özet")
eq(g["bin/servis"], hashlib.sha256(bytes(range(256)) * 50).hexdigest(), "büyük dosyanın özeti")
eq(len(anlik_goruntu("uygulama")), 5, "hariç yoksa beş dosya")
ok(calls("fnmatch"), "fnmatch kullan")
```

```solution
import hashlib, fnmatch
from pathlib import Path

def _ozet(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(65536), b""):
            h.update(parca)
    return h.hexdigest()

def anlik_goruntu(kok, haric=()):
    kok = Path(kok)
    goruntu = {}
    for p in sorted(kok.rglob("*")):
        if not p.is_file():
            continue
        goreli = p.relative_to(kok).as_posix()
        if any(fnmatch.fnmatch(goreli, d) or fnmatch.fnmatch(p.name, d) for d in haric):
            continue
        goruntu[goreli] = _ozet(p)
    return goruntu
```

```hint
`Path(kok).rglob("*")` + `is_file()`. Göreli yol: `p.relative_to(kok).as_posix()`.
```

```hint
Hariç tutma: `any(fnmatch.fnmatch(goreli, d) or fnmatch.fnmatch(p.name, d) for d in haric)`.
```
:::

::: gorev 2 · İmzalı kayıt
İki fonksiyon yaz:

- `kaydet(goruntu, yol, anahtar)`: dosyaya şu JSON'u yazsın: `{"surum": 1, "dosyalar": goruntu, "imza": ...}`. İmza, `json.dumps(goruntu, sort_keys=True)` metninin (UTF-8) `anahtar` ile alınmış HMAC-SHA256'sıdır (onaltılık). `anahtar` bir metindir.
- `yukle(yol, anahtar)`: dosyayı okusun; `surum` 1 değilse `ValueError("sürüm desteklenmiyor")`, imza tutmuyorsa `ValueError("imza geçersiz")` yükseltsin; geçerliyse `dosyalar` sözlüğünü döndürsün. Karşılaştırmayı sabit süreli yap.

```starter
import json, hmac, hashlib

def kaydet(goruntu, yol, anahtar):
    pass

def yukle(yol, anahtar):
    pass
```

```test
import json
need("kaydet"); need("yukle")
g = {"a.txt": "11" * 32, "alt/b.bin": "22" * 32}
kaydet(g, "goruntu.json", "gizli-anahtar")
eq(yukle("goruntu.json", "gizli-anahtar"), g, "kaydet → yukle gidiş-dönüş")
v = json.load(open("goruntu.json", encoding="utf-8"))
eq(v["surum"], 1, "sürüm alanı")
ok(isinstance(v["imza"], str) and len(v["imza"]) == 64, "64 karakterlik imza")
raises(ValueError, yukle, "goruntu.json", "yanlis-anahtar", msg="yanlış anahtar → ValueError")
v["dosyalar"]["a.txt"] = "33" * 32
json.dump(v, open("oynanmis.json", "w", encoding="utf-8"))
try:
    yukle("oynanmis.json", "gizli-anahtar")
    ok(False, "oynanmış görüntü reddedilmeli")
except ValueError as e:
    eq(str(e), "imza geçersiz", "mesaj: imza geçersiz")
v2 = json.load(open("goruntu.json", encoding="utf-8")); v2["surum"] = 2
json.dump(v2, open("yeni.json", "w", encoding="utf-8"))
try:
    yukle("yeni.json", "gizli-anahtar")
    ok(False, "bilinmeyen sürüm reddedilmeli")
except ValueError as e:
    eq(str(e), "sürüm desteklenmiyor", "mesaj: sürüm desteklenmiyor")
ok(calls("compare_digest"), "hmac.compare_digest kullan")
kaydet({"b.txt": "44" * 32, "a.txt": "55" * 32}, "s1.json", "gizli-anahtar")
kaydet({"a.txt": "55" * 32, "b.txt": "44" * 32}, "s2.json", "gizli-anahtar")
eq(json.load(open("s1.json", encoding="utf-8"))["imza"], json.load(open("s2.json", encoding="utf-8"))["imza"],
   "anahtar ekleme sırası imzayı değiştirmemeli")
```

```solution
import json, hmac, hashlib

def _imza(goruntu, anahtar):
    kanonik = json.dumps(goruntu, sort_keys=True).encode("utf-8")
    return hmac.new(anahtar.encode("utf-8"), kanonik, hashlib.sha256).hexdigest()

def kaydet(goruntu, yol, anahtar):
    veri = {"surum": 1, "dosyalar": goruntu, "imza": _imza(goruntu, anahtar)}
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1)

def yukle(yol, anahtar):
    with open(yol, encoding="utf-8") as f:
        veri = json.load(f)
    if veri.get("surum") != 1:
        raise ValueError("sürüm desteklenmiyor")
    if not hmac.compare_digest(_imza(veri["dosyalar"], anahtar), veri.get("imza", "")):
        raise ValueError("imza geçersiz")
    return veri["dosyalar"]
```

```hint
İmzayı hesaplayan küçük bir yardımcı yaz ve hem `kaydet` hem `yukle` onu kullansın. Kanonik biçim: `json.dumps(goruntu, sort_keys=True)`.
```
:::

::: gorev 3 · Fark raporu
`karsilastir(eski, yeni)` iki görüntüyü karşılaştırıp şu sözlüğü döndürsün (listeler alfabetik):

```python
{"eklenen": [...], "silinen": [...], "degisen": [...], "temiz": True/False}
```

`temiz`, hiçbir fark yoksa `True` olsun. Sonra kısa bir program bölümü yaz: `surum1` ve `surum2` klasörlerinin görüntülerini al (yardımcı fonksiyon hazır), karşılaştır ve her farkı `+ yol`, `- yol`, `~ yol` biçiminde (önce eklenenler, sonra silinenler, sonra değişenler) yazdır.

```setup
from pathlib import Path
icerik1 = {"README.md": b"v1", "config/app.ini": b"port=80", "bin/servis": b"\x00\x01", "eski.log": b"x"}
icerik2 = {"README.md": b"v1", "config/app.ini": b"port=8080", "bin/servis": b"\x00\x01", "yeni/eklenti.py": b"print(1)"}
for klasor, icerik in (("surum1", icerik1), ("surum2", icerik2)):
    for yol, veri in icerik.items():
        p = Path(klasor) / yol
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(veri)
```

```starter
import hashlib
from pathlib import Path

def anlik_goruntu(kok):
    kok = Path(kok)
    return {p.relative_to(kok).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in kok.rglob("*") if p.is_file()}

def karsilastir(eski, yeni):
    pass

# surum1 ile surum2'yi karşılaştır ve farkları yazdır

```

```test
need("karsilastir")
r = karsilastir({"a": "1", "b": "2", "c": "3"}, {"a": "1", "b": "9", "d": "4"})
eq(r, {"eklenen": ["d"], "silinen": ["c"], "degisen": ["b"], "temiz": False}, "fark raporu")
eq(karsilastir({"a": "1"}, {"a": "1"}), {"eklenen": [], "silinen": [], "degisen": [], "temiz": True}, "fark yok → temiz")
eq(lines, ["+ yeni/eklenti.py", "- eski.log", "~ config/app.ini"], "surum1 → surum2 farkları yazdırılmalı")
```

```solution
import hashlib
from pathlib import Path

def anlik_goruntu(kok):
    kok = Path(kok)
    return {p.relative_to(kok).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in kok.rglob("*") if p.is_file()}

def karsilastir(eski, yeni):
    e, y = set(eski), set(yeni)
    rapor = {
        "eklenen": sorted(y - e),
        "silinen": sorted(e - y),
        "degisen": sorted(k for k in e & y if eski[k] != yeni[k]),
    }
    rapor["temiz"] = not (rapor["eklenen"] or rapor["silinen"] or rapor["degisen"])
    return rapor

r = karsilastir(anlik_goruntu("surum1"), anlik_goruntu("surum2"))
for isaret, anahtar in (("+", "eklenen"), ("-", "silinen"), ("~", "degisen")):
    for yol in r[anahtar]:
        print(isaret, yol)
```

```hint
P49'daki `degisenler` görevinin aynısı, artı bir `temiz` alanı. Yazdırırken üç listeyi sırayla dolaş.
```
:::
