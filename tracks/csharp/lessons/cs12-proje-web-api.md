---
id: cs12
title: Proje · Bir ASP.NET Core Web API Hizmetini Baştan Sona Okumak
summary: Ara katman kimlik/kota denetimi, record DTO doğrulaması ve parametreli SQLite kaydından oluşan üç katmanlı bir .NET servisini okumak.
---

::: anlat Servisin mimarisi: Ara Katman → Denetleyici Doğrulaması → Veritabanı
Bu son paftada önceki 11 derste gördüğümüz C# yapılarını tek bir ASP.NET Core iç denetim servisinde (`DenetimApi`) birleştiriyoruz. Servis üç ardışık katmandan oluşur:

1. **`AraKatmanKontrol` (Middleware):**
   - `basliklar` sözlüğünde (büyük-küçük harf duyarsız, `StringComparer.OrdinalIgnoreCase`) `"X-Api-Anahtar"` ve `"X-Kota-Kullanim"` başlıklarını arar.
   - `basliklar == null` ise `"401:BASLIK_YOK"` döndürür.
   - `"X-Api-Anahtar"` değeri `"pafta-net8-2026"` değilse `"401:GECERSIZ_ANAHTAR"` döndürür.
   - `"X-Kota-Kullanim"` başlığı yoksa `"0"` varsayılır (`?? "0"`). `int.TryParse` başarısızsa veya değer `< 0` ise `"400:HATALI_KOTA_BASLIGI"` döndürür.
   - `kota >= maksKota` ise `"429:KOTA_ASILDI"`, aksi hâlde `"OK"` döndürür.

2. **`IstekDogrula` (DTO ve Desen Eşleme):**
   - Gövde (`govde`) sözlüğünden `"servis"`, `"ortam"` ve `"sure_ms"` alanlarını okur.
   - `"servis"` bir metin (`string`) değilse veya `string.IsNullOrWhiteSpace` ise `"422:SERVIS_BOS"` döndürür; kenar boşlukları kırpılıp küçük harfe çevrildiğinde uzunluğu `3..32` aralığında değilse veya yalnızca `[a-z0-9-]` karakterlerinden oluşmuyorsa `"422:GECERSIZ_SERVIS"` döndürür.
   - `"ortam"` metin değilse veya boşluksa `"uretim"` varsayılır; küçük harfe çevrildiğinde `{"uretim", "test", "analiz"}` kümesinde değilse `"422:GECERSIZ_ORTAM"` döndürür.
   - `"sure_ms"` tam sayı (`int`, `bool` hariç!) değilse veya `0..60000` aralığı dışındaysa `"422:GECERSIZ_SURE"` döndürür.
   - Geçerliyse `$"200:{servis}|{ortam}|{sureMs}"` döndürür.

```csharp
using System;
using System.Collections.Generic;

public class DenetimApi
{
    private static readonly HashSet<string> IzinliOrtamlar =
        new(StringComparer.OrdinalIgnoreCase) { "uretim", "test", "analiz" };

    public static string AraKatmanKontrol(
        Dictionary<string, string>? basliklar, int maksKota)
    {
        if (basliklar == null)
            return "401:BASLIK_YOK";
        if (!basliklar.TryGetValue("X-Api-Anahtar", out var anahtar)
            || anahtar != "pafta-net8-2026")
            return "401:GECERSIZ_ANAHTAR";

        string kotaMetin = basliklar.TryGetValue("X-Kota-Kullanim", out var km) ? km : "0";
        if (!int.TryParse(kotaMetin.Trim(), out int kota) || kota < 0)
            return "400:HATALI_KOTA_BASLIGI";
        if (kota >= maksKota)
            return "429:KOTA_ASILDI";
        return "OK";
    }
}
```
:::

::: tahmin
```csharp
using System;
using System.Collections.Generic;

class Tahmin
{
    static string Kontrol(Dictionary<string, string>? basliklar, int maksKota)
    {
        if (basliklar == null)
            return "401:BASLIK_YOK";
        if (!basliklar.TryGetValue("X-Api-Anahtar", out var anahtar)
            || anahtar != "pafta-net8-2026")
            return "401:GECERSIZ_ANAHTAR";

        string kotaMetin = basliklar.TryGetValue("X-Kota-Kullanim", out var km) ? km : "0";
        if (!int.TryParse(kotaMetin.Trim(), out int kota) || kota < 0)
            return "400:HATALI_KOTA_BASLIGI";
        if (kota >= maksKota)
            return "429:KOTA_ASILDI";
        return $"OK:{maksKota - kota}";
    }

    static void Main()
    {
        var b1 = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["x-api-anahtar"] = "pafta-net8-2026",
            ["X-Kota-Kullanim"] = "99"
        };
        Console.WriteLine(Kontrol(b1, 100));
        Console.WriteLine(Kontrol(b1, 99));

        var b2 = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["X-Api-Anahtar"] = "pafta-net8-2026"
        };
        Console.WriteLine(Kontrol(b2, 50));
    }
}
```

```gercek
OK:1
429:KOTA_ASILDI
OK:50
```

???

`OK:1`, `429:KOTA_ASILDI`, `OK:50`. `b1` sözlüğü `StringComparer.OrdinalIgnoreCase` kullandığı için `"x-api-anahtar"` başlığı `"X-Api-Anahtar"` aramasıyla eşleşir. `maksKota = 100` iken `kota = 99 < 100` olduğu için `OK:1` döner; `maksKota = 99` iken `kota >= maksKota` (`99 >= 99`) koşulu sağlanır ve `429:KOTA_ASILDI` döner. `b2` sözlüğünde `"X-Kota-Kullanim"` başlığı olmadığı için varsayılan `"0"` kullanılır ve `OK:50` yazdırılır.
:::

::: gorev 1 · Ara katman kimlik ve kota kontrolü (`AraKatmanKontrol`)
`DenetimApi.AraKatmanKontrol(basliklar, maksKota)` metodunun davranışını Python'da `ara_katman_kontrol(basliklar, maks_kota)` fonksiyonu olarak kur. `basliklar` sözlüğündeki anahtarların C#'taki `StringComparer.OrdinalIgnoreCase` gibi **büyük-küçük harf duyarsız** aranmasına dikkat et!

```starter
def ara_katman_kontrol(basliklar, maks_kota):
    return "OK"
```

```test
need("ara_katman_kontrol")
eq(ara_katman_kontrol({"x-api-anahtar": "pafta-net8-2026", "x-kota-kullanim": "99"}, 100), "OK", "99 < 100 ve harf duyarsız başlıklar -> OK")
eq(ara_katman_kontrol({"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "100"}, 100), "429:KOTA_ASILDI", "kota == maks_kota (100 >= 100) -> 429:KOTA_ASILDI")
eq(ara_katman_kontrol({"X-Api-Anahtar": "pafta-net8-2026"}, 1), "OK", "X-Kota-Kullanim yoksa 0 varsayılır (0 < 1 -> OK)")
eq(ara_katman_kontrol({"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "0"}, 1), "OK", "alt sınır kota=0 geçerli")
eq(ara_katman_kontrol({"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "-1"}, 100), "400:HATALI_KOTA_BASLIGI", "negatif kota -> 400:HATALI_KOTA_BASLIGI")
eq(ara_katman_kontrol({"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "yuz"}, 100), "400:HATALI_KOTA_BASLIGI", "sayısal olmayan kota -> 400:HATALI_KOTA_BASLIGI")
eq(ara_katman_kontrol({"X-Api-Anahtar": "yanlis"}, 100), "401:GECERSIZ_ANAHTAR", "yanlış anahtar -> 401:GECERSIZ_ANAHTAR")
eq(ara_katman_kontrol({}, 100), "401:GECERSIZ_ANAHTAR", "eksik anahtar -> 401:GECERSIZ_ANAHTAR")
eq(ara_katman_kontrol(None, 100), "401:BASLIK_YOK", "None başlık -> 401:BASLIK_YOK")
```

```solution
import re

def ara_katman_kontrol(basliklar, maks_kota):
    if basliklar is None:
        return "401:BASLIK_YOK"
    tablo = {k.lower(): v for k, v in basliklar.items()}
    if tablo.get("x-api-anahtar") != "pafta-net8-2026":
        return "401:GECERSIZ_ANAHTAR"
    kota_metin = str(tablo.get("x-kota-kullanim", "0")).strip()
    if not re.fullmatch(r"[+-]?[0-9]+", kota_metin):
        return "400:HATALI_KOTA_BASLIGI"
    kota = int(kota_metin)
    if kota < 0:
        return "400:HATALI_KOTA_BASLIGI"
    if kota >= maks_kota:
        return "429:KOTA_ASILDI"
    return "OK"
```

```hint
Önce `basliklar` sözlüğünün anahtarlarını `.lower()` ile normalize et. `kota >= maks_kota` sınırında `kota == maks_kota` değerinin `"429:KOTA_ASILDI"` döndürdüğüne dikkat et.
```
:::

::: gorev 2 · DTO ve gövde doğrulaması (`IstekDogrula`)
Anlatımdaki kurallara göre `istek_dogrula(govde)` fonksiyonunu Python'da yaz:
- `govde` bir `dict` değilse `"400:BOZUK_GOVDE"` döndür.
- `"servis"` bir `str` değilse veya `.strip()` sonrası boşsa `"422:SERVIS_BOS"` döndür.
- `servis = govde["servis"].strip().lower()` uzunluğu `3..32` aralığında değilse veya `^[a-z0-9-]+$` desenine uymuyorsa `"422:GECERSIZ_SERVIS"` döndür.
- `"ortam"` bir `str` ise ve `.strip()` sonrası boş değilse `.strip().lower()` alınır; aksi hâlde `"uretim"` varsayılır. Değer `{"uretim", "test", "analiz"}` kümesinde değilse `"422:GECERSIZ_ORTAM"` döndür.
- `"sure_ms"` tam sayı (`type(x) is int`) değilse veya `0..60000` aralığı dışındaysa `"422:GECERSIZ_SURE"` döndür.
- Geçerliyse `f"200:{servis}|{ortam}|{sure_ms}"` döndür.

```starter
def istek_dogrula(govde):
    return "200:kimlik-api|uretim|100"
```

```test
need("istek_dogrula")
eq(istek_dogrula({"servis": "  Kimlik-API-01 ", "ortam": "TEST", "sure_ms": 0}),
   "200:kimlik-api-01|test|0", "geçerli girdi ve alt sınır sure_ms=0")
eq(istek_dogrula({"servis": "abc", "ortam": "   ", "sure_ms": 60000}),
   "200:abc|uretim|60000", "alt sınır servis uzunluğu 3, boşluklu ortamda varsayılan uretim, üst sınır sure_ms=60000")
eq(istek_dogrula({"servis": "a" * 32, "sure_ms": 250}),
   "200:" + ("a" * 32) + "|uretim|250", "üst sınır servis uzunluğu 32 ve eksik ortamda uretim")
eq(istek_dogrula(None), "400:BOZUK_GOVDE", "None gövde -> 400:BOZUK_GOVDE")
eq(istek_dogrula({"servis": "   ", "sure_ms": 10}), "422:SERVIS_BOS", "yalnızca boşluklu servis -> 422:SERVIS_BOS")
eq(istek_dogrula({"servis": 123, "sure_ms": 10}), "422:SERVIS_BOS", "sayı servis -> 422:SERVIS_BOS")
eq(istek_dogrula({"servis": "ab", "sure_ms": 10}), "422:GECERSIZ_SERVIS", "2 karakterli servis (< 3) -> 422:GECERSIZ_SERVIS")
eq(istek_dogrula({"servis": "a" * 33, "sure_ms": 10}), "422:GECERSIZ_SERVIS", "33 karakterli servis (> 32) -> 422:GECERSIZ_SERVIS")
eq(istek_dogrula({"servis": "kimlik_api", "sure_ms": 10}), "422:GECERSIZ_SERVIS", "alt çizgi içeren servis -> 422:GECERSIZ_SERVIS")
eq(istek_dogrula({"servis": "kimlik", "ortam": "staj", "sure_ms": 10}), "422:GECERSIZ_ORTAM", "izinli olmayan ortam -> 422:GECERSIZ_ORTAM")
eq(istek_dogrula({"servis": "kimlik", "sure_ms": -1}), "422:GECERSIZ_SURE", "sure_ms=-1 (< 0) -> 422:GECERSIZ_SURE")
eq(istek_dogrula({"servis": "kimlik", "sure_ms": 60001}), "422:GECERSIZ_SURE", "sure_ms=60001 (> 60000) -> 422:GECERSIZ_SURE")
eq(istek_dogrula({"servis": "kimlik", "sure_ms": True}), "422:GECERSIZ_SURE", "bool sure_ms -> 422:GECERSIZ_SURE")
eq(istek_dogrula({"servis": "kimlik", "sure_ms": "100"}), "422:GECERSIZ_SURE", "metin sure_ms -> 422:GECERSIZ_SURE")
```

```solution
import re

IZINLI_ORTAMLAR = {"uretim", "test", "analiz"}

def istek_dogrula(govde):
    if not isinstance(govde, dict):
        return "400:BOZUK_GOVDE"
    servis_obj = govde.get("servis")
    if not isinstance(servis_obj, str) or not servis_obj.strip():
        return "422:SERVIS_BOS"
    servis = servis_obj.strip().lower()
    if not (3 <= len(servis) <= 32) or not re.fullmatch(r"[a-z0-9-]+", servis):
        return "422:GECERSIZ_SERVIS"

    ortam_obj = govde.get("ortam")
    if isinstance(ortam_obj, str) and ortam_obj.strip():
        ortam = ortam_obj.strip().lower()
    else:
        ortam = "uretim"
    if ortam not in IZINLI_ORTAMLAR:
        return "422:GECERSIZ_ORTAM"

    sure_obj = govde.get("sure_ms")
    if type(sure_obj) is not int or not (0 <= sure_obj <= 60000):
        return "422:GECERSIZ_SURE"
    return f"200:{servis}|{ortam}|{sure_obj}"
```

```hint
`servis_obj` için önce `isinstance(servis_obj, str)` ve `servis_obj.strip()` kontrolü yap (`422:SERVIS_BOS`), ardından uzunluk (`3..32`) ve karakter (`[a-z0-9-]+`) kontrolüne (`422:GECERSIZ_SERVIS`) geç.
```
:::

::: gorev 3 · Uçtan uca Web API uç noktası (Ara Katman + Doğrulama + SQLite)
İlk iki görevdeki ara katman ve doğrulama adımlarını birleştirip geçerli ölçümü `olcumler (id INTEGER PRIMARY KEY, servis TEXT, ortam TEXT, sure_ms INTEGER)` tablosuna kaydeden `olcum_kaydet(db, basliklar, maks_kota, govde)` fonksiyonunu yaz:
- Ara katman `"OK"` dönmezse veritabanına dokunmadan `(durum_kodu, hata_kodu)` döndür (`(429, "KOTA_ASILDI")` gibi).
- Doğrulama `"200:..."` dönmezse veritabanına dokunmadan `(durum_kodu, hata_kodu)` döndür (`(422, "GECERSIZ_SURE")` gibi).
- Geçerliyse kaydı SQLite tablosuna ekle (`commit`) ve `(201, f"#{id}:{servis}:{ortam}:{sure_ms}")` döndür.

```starter
def olcum_kaydet(db, basliklar, maks_kota, govde):
    return 201, "#1:kimlik:uretim:100"
```

```test
import sqlite3
need("olcum_kaydet")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE olcumler (id INTEGER PRIMARY KEY, servis TEXT, ortam TEXT, sure_ms INTEGER)")
baslik = {"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "0"}

eq(olcum_kaydet(db, baslik, 1, {"servis": "abc", "ortam": "analiz", "sure_ms": 0}),
   (201, "#1:abc:analiz:0"), "ilk geçerli kayıt (kota=0 < 1, servis=3, sure_ms=0)")
eq(olcum_kaydet(db, None, 10, {"servis": "abc", "sure_ms": 10}),
   (401, "BASLIK_YOK"), "None başlık -> 401 BASLIK_YOK")
eq(olcum_kaydet(db, {"X-Api-Anahtar": "yanlis"}, 10, {"servis": "abc", "sure_ms": 10}),
   (401, "GECERSIZ_ANAHTAR"), "yanlış anahtar -> 401 GECERSIZ_ANAHTAR")
eq(olcum_kaydet(db, {"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "-1"}, 10, {"servis": "abc", "sure_ms": 10}),
   (400, "HATALI_KOTA_BASLIGI"), "negatif kota -> 400 HATALI_KOTA_BASLIGI")
eq(olcum_kaydet(db, {"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "abc"}, 10, {"servis": "abc", "sure_ms": 10}),
   (400, "HATALI_KOTA_BASLIGI"), "harf kota -> 400 HATALI_KOTA_BASLIGI")
eq(olcum_kaydet(db, {"X-Api-Anahtar": "pafta-net8-2026", "X-Kota-Kullanim": "10"}, 10, {"servis": "abc", "sure_ms": 10}),
   (429, "KOTA_ASILDI"), "kota=10 == maks_kota=10 -> 429 KOTA_ASILDI")
eq(olcum_kaydet(db, baslik, 10, None),
   (400, "BOZUK_GOVDE"), "None gövde -> 400 BOZUK_GOVDE")
eq(olcum_kaydet(db, baslik, 10, {"servis": "  ", "sure_ms": 10}),
   (422, "SERVIS_BOS"), "boş servis -> 422 SERVIS_BOS")
eq(olcum_kaydet(db, baslik, 10, {"servis": 99, "sure_ms": 10}),
   (422, "SERVIS_BOS"), "sayı servis -> 422 SERVIS_BOS")
eq(olcum_kaydet(db, baslik, 10, {"servis": "ab", "sure_ms": 10}),
   (422, "GECERSIZ_SERVIS"), "2 karakterli servis -> 422 GECERSIZ_SERVIS")
eq(olcum_kaydet(db, baslik, 10, {"servis": "a" * 33, "sure_ms": 10}),
   (422, "GECERSIZ_SERVIS"), "33 karakterli servis -> 422 GECERSIZ_SERVIS")
eq(olcum_kaydet(db, baslik, 10, {"servis": "a_b", "sure_ms": 10}),
   (422, "GECERSIZ_SERVIS"), "alt çizgili servis -> 422 GECERSIZ_SERVIS")
eq(olcum_kaydet(db, baslik, 10, {"servis": "abc", "ortam": "yok", "sure_ms": 10}),
   (422, "GECERSIZ_ORTAM"), "geçersiz ortam -> 422 GECERSIZ_ORTAM")
eq(olcum_kaydet(db, baslik, 10, {"servis": "abc", "sure_ms": -1}),
   (422, "GECERSIZ_SURE"), "sure_ms=-1 -> 422 GECERSIZ_SURE")
eq(olcum_kaydet(db, baslik, 10, {"servis": "abc", "sure_ms": 60001}),
   (422, "GECERSIZ_SURE"), "sure_ms=60001 -> 422 GECERSIZ_SURE")
eq(olcum_kaydet(db, baslik, 10, {"servis": "abc", "sure_ms": "10"}),
   (422, "GECERSIZ_SURE"), "metin sure_ms -> 422 GECERSIZ_SURE")
eq(olcum_kaydet(db, {"x-api-anahtar": "pafta-net8-2026"}, 10, {"servis": "a" * 32, "ortam": "  ", "sure_ms": 60000}),
   (201, "#2:" + ("a" * 32) + ":uretim:60000"), "ikinci geçerli kayıt (servis=32, varsayılan ortam, sure_ms=60000)")
eq(db.execute("SELECT COUNT(*) FROM olcumler").fetchone()[0], 2, "tabloda tam 2 kayıt olmalı")
```

```solution
import re

IZINLI_ORTAMLAR = {"uretim", "test", "analiz"}

def _ara_katman(basliklar, maks_kota):
    if basliklar is None:
        return "401:BASLIK_YOK"
    tablo = {k.lower(): v for k, v in basliklar.items()}
    if tablo.get("x-api-anahtar") != "pafta-net8-2026":
        return "401:GECERSIZ_ANAHTAR"
    kota_metin = str(tablo.get("x-kota-kullanim", "0")).strip()
    if not re.fullmatch(r"[+-]?[0-9]+", kota_metin):
        return "400:HATALI_KOTA_BASLIGI"
    kota = int(kota_metin)
    if kota < 0:
        return "400:HATALI_KOTA_BASLIGI"
    if kota >= maks_kota:
        return "429:KOTA_ASILDI"
    return "OK"

def _dogrula(govde):
    if not isinstance(govde, dict):
        return "400:BOZUK_GOVDE"
    servis_obj = govde.get("servis")
    if not isinstance(servis_obj, str) or not servis_obj.strip():
        return "422:SERVIS_BOS"
    servis = servis_obj.strip().lower()
    if not (3 <= len(servis) <= 32) or not re.fullmatch(r"[a-z0-9-]+", servis):
        return "422:GECERSIZ_SERVIS"
    ortam_obj = govde.get("ortam")
    if isinstance(ortam_obj, str) and ortam_obj.strip():
        ortam = ortam_obj.strip().lower()
    else:
        ortam = "uretim"
    if ortam not in IZINLI_ORTAMLAR:
        return "422:GECERSIZ_ORTAM"
    sure_obj = govde.get("sure_ms")
    if type(sure_obj) is not int or not (0 <= sure_obj <= 60000):
        return "422:GECERSIZ_SURE"
    return f"200:{servis}|{ortam}|{sure_obj}"

def olcum_kaydet(db, basliklar, maks_kota, govde):
    ak = _ara_katman(basliklar, maks_kota)
    if ak != "OK":
        kod, mesaj = ak.split(":", 1)
        return int(kod), mesaj
    d = _dogrula(govde)
    if not d.startswith("200:"):
        kod, mesaj = d.split(":", 1)
        return int(kod), mesaj
    servis, ortam, sure_str = d[4:].split("|")
    cur = db.execute(
        "INSERT INTO olcumler (servis, ortam, sure_ms) VALUES (?, ?, ?)",
        (servis, ortam, int(sure_str)),
    )
    db.commit()
    return 201, f"#{cur.lastrowid}:{servis}:{ortam}:{sure_str}"
```

```hint
İlk iki görevdeki `_ara_katman` ve `_dogrula` fonksiyonlarını sırayla çağır; yalnızca ikisi de başarılı olduğunda `INSERT INTO olcumler` sorgusunu çalıştırıp `db.commit()` yap.
```
:::
