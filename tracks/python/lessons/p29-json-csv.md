---
id: p29
title: Veri Biçimleri · JSON, CSV, SQLite
summary: json ile serileştirme, csv okuma-yazma ve parametreli SQL sorgusuyla injection'dan korunma.
---

::: anlat JSON: makinelerin ortak dili
API'ler, log toplayıcılar, yapılandırma dosyaları... Hepsi **JSON** konuşur. `json` modülü Python nesnelerini JSON metnine (**serileştirme**) ve geri (**ayrıştırma**) çevirir:

| Python | JSON |
|---|---|
| `dict` | nesne `{}` |
| `list`, `tuple` | dizi `[]` |
| `str` | metin |
| `int`, `float` | sayı |
| `True` / `False` | `true` / `false` |
| `None` | `null` |

```python
import json

olay = {"kullanici": "Ayşe", "basarili": False, "portlar": [22, 443], "not": None}
metin = json.dumps(olay)                              #! Python → JSON metni
print(metin)
print(json.dumps(olay, ensure_ascii=False, indent=2)) #! Türkçe karakterler + girinti
geri = json.loads('{"ip": "10.0.0.7", "deneme": 5}')  #! JSON metni → Python
print(geri["deneme"] + 1)

with open("olay.json", "w", encoding="utf-8") as f:   #! dump/load: dosyaya/dosyadan
    json.dump(olay, f, ensure_ascii=False)
with open("olay.json", encoding="utf-8") as f:
    print(json.load(f)["portlar"])
```

İsimlendirme: **s**'li olanlar (`dumps`, `loads`) **string** ile, s'siz olanlar dosya ile çalışır.

**JSON Lines** (`.jsonl`): her satır ayrı bir JSON nesnesidir. Log ve olay akışları için standarttır, çünkü dosyayı satır satır okuyabilirsin:

```python
import json
satirlar = ['{"tur": "giris", "k": "ali"}', '{"tur": "cikis", "k": "ali"}']
for s in satirlar:
    olay = json.loads(s)
    print(olay["tur"], olay["k"])
```

> [!TUZAK]
> JSON'da demet yoktur (listeye döner), sözlük anahtarları **her zaman metindir** (`{1: "a"}` → `{"1": "a"}`) ve `datetime` gibi nesneler doğrudan serileştirilemez (`TypeError`). Bozuk JSON `json.JSONDecodeError` verir; dışarıdan gelen veride bunu yakala.

> [!GÜVENLİK]
> Güvenilmeyen veriyi **asla `pickle` ile açma**. `pickle.loads` keyfi kod çalıştırabilir; saldırganın hazırladığı bir pickle dosyası makineni ele geçirir. Veri alışverişi için JSON güvenlidir, çünkü sadece veri taşır, kod taşımaz. Aynı uyarı `yaml.load` için de geçerlidir (`yaml.safe_load` kullan).
:::

::: tahmin
İki satır:

```python
import json
veri = {"ad": "Ayşe", "yetkiler": ["oku"], "aktif": True, "not": None}
print(json.dumps(veri, ensure_ascii=False))
print(json.loads('[1, 2.5, "x", false, null]'))
```

???

`{"ad": "Ayşe", "yetkiler": ["oku"], "aktif": true, "not": null}` ve `[1, 2.5, 'x', False, None]`. İlki **JSON metnidir** (çift tırnak, true, null). İkincisi ayrıştırılmış bir **Python listesidir** ve Python'un kendi gösterimiyle basılır.
:::

::: anlat CSV ve parametreli SQL
**CSV**: virgülle ayrılmış tablo. Elle `split(",")` yapma; değerin içinde virgül ya da tırnak olabilir. `csv` modülü bunları doğru işler:

```python
import csv

with open("kullanicilar.csv", "w", newline="", encoding="utf-8") as f:   #! newline="" şart
    w = csv.writer(f)
    w.writerow(["ad", "rol", "not"])
    w.writerow(["ali", "admin", "yetkili, dikkat"])     #! içinde virgül var
    w.writerow(["veli", "user", ""])

with open("kullanicilar.csv", newline="", encoding="utf-8") as f:
    for satir in csv.DictReader(f):                     #! başlık satırı → sözlük anahtarları
        print(satir["ad"], "|", satir["rol"], "|", satir["not"])
```

### SQL: f-string değil, parametre
P05'teki uyarının uygulaması. Python yerleşik bir veritabanıyla gelir: `sqlite3`.

```python
import sqlite3

db = sqlite3.connect(":memory:")                     #! bellekte geçici veritabanı
db.execute("CREATE TABLE k (ad TEXT, rol TEXT)")
db.executemany("INSERT INTO k VALUES (?, ?)", [("ali", "user"), ("root", "admin")])

girdi = "x' OR '1'='1"                               #! kötü niyetli kullanıcı girdisi
kotu = f"SELECT ad, rol FROM k WHERE ad = '{girdi}'"
print(kotu)                                          #! sorgunun ANLAMI değişti
print(db.execute(kotu).fetchall())                   #! bütün tablo döndü!

iyi = db.execute("SELECT ad, rol FROM k WHERE ad = ?", (girdi,)).fetchall()
print(iyi)                                           #! [] — girdi sadece VERİ olarak kaldı
```

`?` yer tutucusunda değer, sorgu metnine **hiç karışmaz**: veritabanı sürücüsü sorguyu ve veriyi ayrı kanallardan iletir. Kullanıcı ne yazarsa yazsın sorgunun yapısını değiştiremez.

> [!GÜVENLİK]
> SQL injection 25 yılı aşkın süredir en çok sömürülen açıklardan biri ve **tek bir alışkanlıkla** önlenir: sorguya değer **asla** metin birleştirme ya da f-string ile girmez. Tablo ve sütun adları parametre olamaz; onları dinamik seçmen gerekiyorsa sabit bir izin listesinden seç.
:::

::: tahmin
Çıktı tek satır:

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE k (ad TEXT, rol TEXT)")
db.executemany("INSERT INTO k VALUES (?, ?)", [("ali", "user"), ("root", "admin")])
girdi = "x' OR '1'='1"
kotu = db.execute(f"SELECT ad FROM k WHERE ad = '{girdi}'").fetchall()
iyi = db.execute("SELECT ad FROM k WHERE ad = ?", (girdi,)).fetchall()
print(len(kotu), len(iyi))
```

???

`2 0`. f-string'li sorgu `WHERE ad = 'x' OR '1'='1'` olur; `'1'='1'` her satırda doğru olduğu için iki satır da döner. Parametreli sorgu ise `x' OR '1'='1` adında bir kullanıcı arar ve bulamaz.
:::

::: gorev Olay türü sayımı
`olaylar.jsonl` dosyasında her satır bir JSON olayı. Her olayın `"tur"` alanına göre kaç olay olduğunu say ve sonucu **anahtarları sıralı** bir JSON metni olarak tek satırda yazdır (`json.dumps(..., sort_keys=True)`). Bozuk (JSON olmayan) satırları atla.

```setup
satirlar = [
    '{"tur": "giris", "k": "ali", "basarili": true}',
    '{"tur": "giris", "k": "root", "basarili": false}',
    'BOZUK SATIR {{',
    '{"tur": "dosya", "k": "ali", "yol": "/etc/shadow"}',
    '{"tur": "giris", "k": "veli", "basarili": true}',
    '',
    '{"tur": "cikis", "k": "ali"}',
]
with open("olaylar.jsonl", "w", encoding="utf-8") as f:
    f.write("\n".join(satirlar) + "\n")
```

```starter
import json

```

```test
eq(out.strip(), '{"cikis": 1, "dosya": 1, "giris": 3}', "sıralı JSON sayım")
ok(uses("try"), "bozuk satırlar için JSONDecodeError yakala")
```

```solution
import json

sayim = {}
with open("olaylar.jsonl", encoding="utf-8") as f:
    for satir in f:
        try:
            olay = json.loads(satir)
        except json.JSONDecodeError:
            continue
        sayim[olay["tur"]] = sayim.get(olay["tur"], 0) + 1
print(json.dumps(sayim, sort_keys=True))
```

```hint
Her satırı `json.loads` ile dene; `except json.JSONDecodeError: continue`. Boş satır da JSONDecodeError verir.
```
:::

::: gorev Yöneticiler
`kullanicilar.csv` dosyasında `ad,rol,son_giris` sütunları var. Rolü `admin` olanların adlarını **alfabetik sırayla** virgülle birleştirip yazdır. `csv.DictReader` kullan.

```setup
import csv
with open("kullanicilar.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["ad", "rol", "son_giris"])
    w.writerows([["zeynep", "admin", "2026-10-18"], ["ali", "user", "2026-10-19"],
                 ["Baran, Kaya", "admin", "2026-09-01"], ["ayse", "admin", "2026-10-19"],
                 ["veli", "user", ""]])
```

```starter
import csv

```

```test
eq(out.strip(), "Baran, Kaya,ayse,zeynep", "adminler alfabetik (içinde virgül olan ad dahil)")
ok(calls("DictReader"), "csv.DictReader kullan")
```

```solution
import csv

with open("kullanicilar.csv", newline="", encoding="utf-8") as f:
    adminler = sorted(s["ad"] for s in csv.DictReader(f) if s["rol"] == "admin")
print(",".join(adminler))
```

```hint
`for s in csv.DictReader(f): if s["rol"] == "admin": ...` sonra `sorted` ve `",".join`.
```

```hint
"Baran, Kaya" adında virgül var; `split(",")` ile ayrıştırsaydın bozulurdu. csv modülü tırnaklı alanı doğru okur.
```
:::

::: gorev Injection'a dayanıklı sorgu
`rol_bul(db, ad)` fonksiyonunu yaz: `k` tablosunda verilen adın rolünü döndürsün, yoksa `None` döndürsün. Sorguyu **parametreli** yaz; kötü niyetli girdiler sonuç döndürmemeli.

```starter
def rol_bul(db, ad):
    satir = db.execute(f"SELECT rol FROM k WHERE ad = '{ad}'").fetchone()
    return satir[0] if satir else None
```

```test
import sqlite3
need("rol_bul")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE k (ad TEXT, rol TEXT)")
db.executemany("INSERT INTO k VALUES (?, ?)", [("ali", "user"), ("root", "admin"), ("o'brien", "user")])
eq(rol_bul(db, "root"), "admin", "root → admin")
eq(rol_bul(db, "yok"), None, "olmayan → None")
eq(rol_bul(db, "o'brien"), "user", "adında tırnak olan kullanıcı da bulunmalı")
eq(rol_bul(db, "x' OR '1'='1"), None, "injection girdisi → None")
eq(rol_bul(db, "' UNION SELECT 'admin' --"), None, "UNION injection → None")
```

```solution
def rol_bul(db, ad):
    satir = db.execute("SELECT rol FROM k WHERE ad = ?", (ad,)).fetchone()
    return satir[0] if satir else None
```

```hint
`db.execute("SELECT rol FROM k WHERE ad = ?", (ad,))`. Parametre demeti tek elemanlıysa virgülü unutma: `(ad,)`.
```
:::
