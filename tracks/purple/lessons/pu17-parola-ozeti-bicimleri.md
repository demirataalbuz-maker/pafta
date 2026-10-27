---
id: pu17
title: Parola Özeti Biçimleri · NTLM, crypt ve Araç Modları
summary: NTLM'nin 32 hex MD4(UTF-16LE) ilişkisini doğrulamak; /etc/shadow alanlarını, bcrypt/sha512crypt/yescrypt modular crypt bileşenlerini ayrıştırmak; salt tekrarı ve work factor risklerini ayırmak; John/Hashcat modlarını sürüm bağımlılığıyla eşlemek.
timeout: 60
---

::: anlat Özet parola değildir; önce biçimi tanı
CPTS kapsamında parola özetiyle karşılaşınca ilk iş onu kırmaya çalışmak değil, **biçimini ve kanıt sınırını** doğru okumaktır. Hash metni parola veya plaintext değildir; 32 hexadecimal karakter de kendiliğinden NTLM anlamına gelmez. Bağlam yoksa MD4, MD5, NTLM veya başka bir 128-bit özet arasında ayrım yapılamaz.

NTLM bağlamı doğrulanmışsa NT özeti, parolanın UTF-16LE baytlarına MD4 uygulanmasıdır ve 16 bayt = 32 hex karakterdir. Salt içermez. Bu dersteki yardımcı küçük bir RFC 1320 MD4 implementasyonuyla yalnız bilinen test girdisini doğrular; parola kırma yapmaz.

Linux `/etc/shadow` satırı ise dokuz `:` ayrımlı alandır:

| No | Alan | Anlam |
|---|---|---|
| 1 | kullanıcı | Hesap adı |
| 2 | parola alanı | Modular crypt özeti, kilit işareti veya boş alan |
| 3 | son değişim | 1 Ocak 1970'ten beri gün |
| 4 | minimum gün | Değişiklikler arası asgari süre |
| 5 | maksimum gün | Parola geçerlilik üst sınırı |
| 6 | uyarı günü | Süre dolmadan uyarı |
| 7 | pasifleştirme günü | Süre sonrası ek tolerans |
| 8 | hesap bitişi | 1 Ocak 1970'ten beri gün |
| 9 | rezerve | Ayrılmış alan |

Boş sayısal alanlar “ayar yok” olarak `None` okunur. `*` veya `!` ile başlayan parola alanı modular crypt özeti değildir. Dosya yalnız yetkili hesaplarca okunmalı, erişim kısıtlanmalı, yedekler ve raporlar da aynı hassasiyetle korunmalıdır; özetleri genel loglara veya sohbetlere kopyalamak güvenli saklama değildir.

> [!GÜVENLİK]
> Bu pafta gerçek `/etc/shadow` okumaz, parola kırmaz, wordlist/GPU/online lookup kullanmaz ve paket kurmaz. Bütün veriler sentetik veya yayımlanmış test vektörüdür; iş yalnız MD4 vektör doğrulaması ve biçim ayrıştırmadır.
:::

::: anlat Modular crypt: aynı `$` işareti, farklı alanlar
`crypt(3)` ailesinin modular biçiminde `$` ayraçlarının anlamı algoritma kimliğine göre değişir. Her dolarlı metni aynı şemaya bastırma.

| Tür | Biçim | Ayrışacak bileşenler |
|---|---|---|
| bcrypt | `$2a$05$<22 salt><31 digest>` | `$2a$`, `$2b$`, `$2y$`; iki basamaklı cost, 22 salt, 31 digest |
| sha512crypt | `$6$<salt>$<86 digest>` | Varsayılan `rounds=5000`; isteğe bağlı `$6$rounds=N$...` |
| yescrypt | `$y$<parametreler>$<salt>$<digest>` | `j9T` gibi kodlanmış parametre bloğu, salt ve digest |

bcrypt'te `05` doğrudan beş tur değil, logaritmik work factor'dür: iş `2^5` ölçeğindedir. Geçerli sözdizimi aralığı 04–31'dir; güvenlik politikasında istenen asgari cost ayrı bir karardır. `$2a$`, `$2b$` ve `$2y$` aynı ailedeki farklı sürüm etiketleridir; birbirinin ön ekini değiştirerek yeni geçerli özet üretilmez.

sha512crypt, tek başına hızlı `SHA-512(parola)` değildir. `$6$` tuzlu ve tekrarlı crypt şemasıdır. yescrypt'in `j9T` bloğu tek bir ondalık cost değildir; birden çok çalışma parametresini kodlar. Bu nedenle bcrypt cost'u, sha512crypt rounds'u ve yescrypt parametre metni aynı sütunda sayısal karşılaştırılmaz. yescrypt'in bellek maliyeti de salt veya digest uzunluğundan tahmin edilmez.

Salt her hesapta benzersiz olmalıdır. Salt gizli değildir ama tekrarı, aynı parolanın hesaplar arasında aynı çıktıyı üretip üretmediğini göstermeyi ve işin paylaşılmasını kolaylaştırır. Uygun cost/work factor doğrulama maliyetini yükseltir; zayıf parolayı güçlü yapmaz. Parser yalnız **biçim geçerliliği** denetler: digest'in belirli bir parolayla eşleştiğini kanıtlamaz.
:::

::: tahmin UTF-16LE kodlaması neden önemli?
```python
from hash_formats_lab import md4, ntlm_test_ozeti
print(md4(b"abc"))
print(ntlm_test_ozeti("password"))
print(ntlm_test_ozeti("password") == md4("password".encode("utf-8")))
```

???

```text
a448017aaf21d8525fc10ae87aa6729d
8846f7eaee8fb117ad06bdd830b7586c
False
```

İlk satır RFC 1320 `abc` MD4 vektörüdür. NT özeti UTF-16LE baytlarından hesaplanır; UTF-8 baytları farklı bir MD4 girdisidir. Bu doğrulama yalnız bilinen test vektörü içindir, bir kırma işlemi değildir.

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
```

:::

::: gorev 1 · Biçimi katı kurallarla ayrıştır
`ozet_ayristir(metin)` işlevini yaz. Baş/son boşlukları kabul etme; yalnız aşağıdaki tam eşleşmeleri döndür, diğer her metinde `ValueError` yükselt.

- Tam 32 hex için `{"tur": "ntlm", "digest": <küçük harf>}`. Bu etiket yalnız bu görevin **verilmiş NTLM bağlamı** içindir; genel 32 hex tanıma kuralı değildir.
- `$2a$`, `$2b$`, `$2y$` bcrypt için `{"tur":"bcrypt", "surum":"2a|2b|2y", "cost":int, "salt":..., "digest":...}`. Cost 04–31; salt 22 ve digest 31 bcrypt-base64 karakteri (`A–Z a–z 0–9 . /`) olmalı.
- `$6$` sha512crypt için `{"tur":"sha512crypt", "rounds":5000 veya int, "salt":..., "digest":...}`. Salt 1–16 crypt-base64 karakteri, digest tam 86 karakterdir. `rounds=` varsa 1000–999999999 aralığını denetle.
- `$y$` yescrypt için `{"tur":"yescrypt", "parametreler":..., "salt":..., "digest":...}`. Üç bileşen de boş olmayan crypt-base64 metnidir. Parametreyi ondalığa çevirme.

`$5$`, `$2x$`, eksik digest, yanlış bcrypt cost, uzun sha512crypt salt'ı, ekstra alan ve belirsiz metin reddedilmelidir. Kaynak özet metnini parola olarak döndürme.

```starter
import json
kayitlar = json.load(open("hash_formats/hashes.json", encoding="utf-8"))["kayitlar"]

def ozet_ayristir(metin):
    return {"tur": "bilinmiyor", "digest": metin}

print(ozet_ayristir(kayitlar[0]["hash"]))
```

```test
need("ozet_ayristir")
by_id = {k["id"]: k["hash"] for k in kayitlar}
eq(ozet_ayristir(by_id["ntlm-rfc-test"]), {"tur":"ntlm", "digest":"8846f7eaee8fb117ad06bdd830b7586c"}, "NTLM 32 hex")
eq(ozet_ayristir(by_id["ntlm-rfc-test"].upper()), {"tur":"ntlm", "digest":"8846f7eaee8fb117ad06bdd830b7586c"}, "hex normalize edilir")
eq(ozet_ayristir(by_id["bcrypt-openwall-2a"]),
   {"tur":"bcrypt", "surum":"2a", "cost":5, "salt":"CCCCCCCCCCCCCCCCCCCCC.", "digest":"E5YPO9kmyuRGyh0XouQYb4YMJKvyOeW"}, "bcrypt 22 salt + 31 digest")
eq((ozet_ayristir(by_id["bcrypt-openwall-2y"])["surum"], ozet_ayristir(by_id["bcrypt-openwall-2y"])["cost"]), ("2y", 5), "2y sürümü korunur")
eq((ozet_ayristir(by_id["bcrypt-2b-test"])["surum"], ozet_ayristir(by_id["bcrypt-2b-test"])["cost"]), ("2b", 12), "2b ve cost 12")
s = ozet_ayristir(by_id["sha512crypt-yerel-test"])
eq((s["tur"], s["rounds"], s["salt"], len(s["digest"])), ("sha512crypt", 5000, "pu17testsalt", 86), "sha512crypt varsayılan rounds")
y = ozet_ayristir(by_id["yescrypt-belgelenmis-test"])
eq((y["tur"], y["parametreler"], y["salt"]), ("yescrypt", "j9T", "SALT"), "yescrypt parametre bloğu sayı değildir")
r = ozet_ayristir("$6$rounds=10000$abc$" + "A" * 86)
eq(r["rounds"], 10000, "açık rounds okunur")
for metin, alan, deger in (("$2a$04$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31, "cost", 4),
                           ("$2y$20$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31, "cost", 20),
                           ("$2b$31$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31, "cost", 31),
                           ("$6$a$" + "A" * 86, "salt", "a"),
                           ("$6$" + "B" * 16 + "$" + "A" * 86, "salt", "B" * 16),
                           ("$6$rounds=1000$abc$" + "A" * 86, "rounds", 1000),
                           ("$6$rounds=999999999$abc$" + "A" * 86, "rounds", 999999999)):
    eq(ozet_ayristir(metin)[alan], deger, "sınırdaki geçerli biçim kabul edilir: " + metin[:26])
for kotu in ("", "8846f7ea", by_id["ntlm-rfc-test"] + "00", " " + by_id["ntlm-rfc-test"],
             "$5$abc$" + "A" * 43, "$2x$05$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31,
             "$2a$03$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31,
             "$2a$32$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31,
             "$2a$5$CCCCCCCCCCCCCCCCCCCCC." + "A" * 31,
             "$2a$05$CCCCCCCCCCCCCCCCCCCCC." + "A" * 30,
             "$6$" + "A" * 17 + "$" + "A" * 86,
             "$6$rounds=999$abc$" + "A" * 86,
             "$6$rounds=1000000000$abc$" + "A" * 86,
             "$6$abc$" + "A" * 85,
             "$y$j9T$$" + "A" * 43,
             "$y$j9T$SALT$" + "A" * 43 + "$ek"):
    raises(ValueError, ozet_ayristir, kotu, msg="yanlış/belirsiz biçim reddedilir: " + repr(kotu))
```

```solution
import json
import re
kayitlar = json.load(open("hash_formats/hashes.json", encoding="utf-8"))["kayitlar"]
BCRYPT = re.compile(r"^\$(2[aby])\$(0[4-9]|[12][0-9]|3[01])\$([./A-Za-z0-9]{22})([./A-Za-z0-9]{31})$")
SHA512 = re.compile(r"^\$6\$(?:rounds=([0-9]+)\$)?([./A-Za-z0-9]{1,16})\$([./A-Za-z0-9]{86})$")
YESCRYPT = re.compile(r"^\$y\$([./A-Za-z0-9]+)\$([./A-Za-z0-9]+)\$([./A-Za-z0-9]+)$")

def ozet_ayristir(metin):
    if not isinstance(metin, str):
        raise ValueError("Özet metin olmalı")
    if re.fullmatch(r"[0-9A-Fa-f]{32}", metin):
        return {"tur": "ntlm", "digest": metin.lower()}
    m = BCRYPT.fullmatch(metin)
    if m:
        surum, cost, salt, digest = m.groups()
        return {"tur":"bcrypt", "surum":surum, "cost":int(cost), "salt":salt, "digest":digest}
    m = SHA512.fullmatch(metin)
    if m:
        rounds, salt, digest = m.groups()
        rounds = int(rounds) if rounds else 5000
        if not 1000 <= rounds <= 999999999:
            raise ValueError("sha512crypt rounds aralık dışı")
        return {"tur":"sha512crypt", "rounds":rounds, "salt":salt, "digest":digest}
    m = YESCRYPT.fullmatch(metin)
    if m:
        parametreler, salt, digest = m.groups()
        return {"tur":"yescrypt", "parametreler":parametreler, "salt":salt, "digest":digest}
    raise ValueError("Desteklenmeyen veya belirsiz özet biçimi")

print(ozet_ayristir(kayitlar[0]["hash"]))
```

```hint
Dört ayrı `fullmatch` kullan. bcrypt sürümünü, cost'u, salt'ı ve digest'i ayrı gruplarla yakala; yescrypt parametrelerini metin olarak bırak.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from hash_formats_lab import hazirla
hazirla()
```
:::

::: gorev 2 · Shadow alanlarından salt ve cost bulgusu üret
Görev 1'deki `ozet_ayristir` işlevini kopyala ve `shadow_raporu(satirlar, minimum_bcrypt_cost=12)` işlevini yaz. Boş satırları atla; diğer her satır tam dokuz alan olmalı, değilse `ValueError` yükselt. Boş ya da kilitli olmayan her parola alanını (modular `$...$` biçimleri ve bu derste NTLM bağlamındaki 32 hex) Görev 1 parser'ından geçir; bilinmeyen biçimi sessizce kabul etme.

Dönüş:

```text
{"kayitlar": [...], "tekrarlanan_saltlar": [...], "dusuk_bcrypt_cost": [...]}
```

Her kayıt `kullanici`, `parola_alani`, `durum`, `son_degisim`, `min_gun`, `max_gun`, `uyari_gun`, `pasif_gun`, `bitis`, `rezerve`, `ozet` alanlarını taşır. Sayısal alanlar `int`, boşsa `None`; `rezerve` metindir. `durum`: boş parola alanında `parolasiz`, `*` veya `!` ile başlayanda `kilitli`, aksi hâlde `ozet`. `ozet` ayrıştırılmış sözlük veya kilitli/parolasız kayıtta `None`.

Yalnız ayrıştırılan ve salt taşıyan özetlerde, aynı salt'ı kullanan birden fazla hesabı `{"salt":..., "kullanicilar":[...]}` olarak raporla; salt'a ve kullanıcı adlarına göre sırala. bcrypt cost değeri eşikten düşükse kullanıcıyı `dusuk_bcrypt_cost` listesine ekle. yescrypt parametresini veya sha512crypt rounds'u bcrypt eşiğiyle karşılaştırma. NTLM salt taşımaz; salt tekrarı analizine katılmaz.

```starter
def shadow_raporu(satirlar, minimum_bcrypt_cost=12):
    kayitlar = []
    for satir in satirlar:
        if satir.strip():
            alanlar = satir.rstrip("\n").split(":")
            kayitlar.append({"kullanici":alanlar[0], "parola_alani":alanlar[1]})
    return {"kayitlar":kayitlar, "tekrarlanan_saltlar":[], "dusuk_bcrypt_cost":[]}

satirlar = open("hash_formats/shadow.txt", encoding="utf-8").readlines()
print(shadow_raporu(satirlar))
```

```test
import copy
need("ozet_ayristir"); need("shadow_raporu")
r = shadow_raporu(satirlar)
eq(len(r["kayitlar"]), 6, "altı sentetik shadow kaydı")
a = r["kayitlar"][0]
eq((a["kullanici"], a["durum"], a["son_degisim"], a["min_gun"], a["max_gun"], a["uyari_gun"]),
   ("pu17a", "ozet", 20000, 0, 99999, 7), "shadow alanları doğru sırayla")
eq((a["pasif_gun"], a["bitis"], a["rezerve"]), (None, None, ""), "boş sayısal alan None")
eq(a["ozet"]["tur"], "yescrypt", "parola alanı yescrypt olarak ayrıştırılır")
eq(r["kayitlar"][1]["pasif_gun"], 30, "yedinci alan pasifleştirme günü")
eq(r["kayitlar"][1]["bitis"], 21000, "sekizinci alan hesap bitişi")
eq(r["kayitlar"][4]["durum"], "kilitli", "kilit alanı hash değildir")
eq(r["kayitlar"][4]["ozet"], None, "kilitli kayıtta özet yok")
eq(r["kayitlar"][5]["durum"], "parolasiz", "boş parola alanı ayrı durum")
eq(r["tekrarlanan_saltlar"], [{"salt":"pu17testsalt", "kullanicilar":["pu17b", "pu17d"]}], "salt tekrarı hesaplarla raporlanır")
eq(r["dusuk_bcrypt_cost"], ["pu17c"], "cost 05 eşik 12 altında")
eq(shadow_raporu(satirlar, minimum_bcrypt_cost=4)["dusuk_bcrypt_cost"], [], "eşik bcrypt cost'a uygulanır")
raises(ValueError, shadow_raporu, ["a::"], msg="dokuzdan az alan reddedilir")
raises(ValueError, shadow_raporu, ["a:$5$abc$def:1:2:3:4:5:6:"], msg="bilinmeyen modular biçim reddedilir")
x = list(satirlar); x[1] = x[1].replace("$6$pu17testsalt$", "$6$baskasalt$")
eq(shadow_raporu(x)["tekrarlanan_saltlar"], [], "farklı salt tekrar değildir")
x = list(satirlar); x[2] = x[2].replace("$2a$05$", "$2a$12$")
eq(shadow_raporu(x)["dusuk_bcrypt_cost"], [], "cost 12 eşikte düşük değildir")
x = list(satirlar); x[0] = x[0].replace("$y$j9T$", "$y$AAAA$")
eq(shadow_raporu(x)["dusuk_bcrypt_cost"], ["pu17c"], "yescrypt parametresi bcrypt cost değildir")
eq(r["kayitlar"][1]["ozet"]["rounds"], 5000, "rounds= yoksa sha512crypt varsayılanı 5000")
ek = [k + ":" + p + ":20000:0:99999:7:::" for k, p in (
    ("sinir4", "$2a$04$" + "a" * 22 + "A" * 31), ("orta20", "$2y$20$" + "b" * 22 + "A" * 31),
    ("sinir31", "$2b$31$" + "c" * 22 + "A" * 31), ("tek", "$6$rounds=1000$a$" + "A" * 86),
    ("ust", "$6$rounds=999999999$" + "B" * 16 + "$" + "A" * 86),
    ("nt1", "8846f7eaee8fb117ad06bdd830b7586c"), ("nt2", "8846f7eaee8fb117ad06bdd830b7586c"))]
s = shadow_raporu(ek)
eq([(k["ozet"]["tur"], k["ozet"].get("cost"), k["ozet"].get("rounds")) for k in s["kayitlar"]],
   [("bcrypt", 4, None), ("bcrypt", 20, None), ("bcrypt", 31, None), ("sha512crypt", None, 1000),
    ("sha512crypt", None, 999999999), ("ntlm", None, None), ("ntlm", None, None)],
   "kopyalanan parser sınırdaki biçimleri shadow'da da kabul eder")
eq(s["dusuk_bcrypt_cost"], ["sinir4"], "cost 04 eşik altında, 20 ve 31 değil")
eq(s["tekrarlanan_saltlar"], [], "NTLM salt taşımaz; aynı NT özeti salt tekrarı sayılmaz")
raises(ValueError, shadow_raporu, ["uzun:$6$" + "A" * 17 + "$" + "A" * 86 + ":1:2:3:4:5:6:"],
       msg="16 karakterden uzun salt shadow'da da reddedilir")
```

```solution
import re
BCRYPT = re.compile(r"^\$(2[aby])\$(0[4-9]|[12][0-9]|3[01])\$([./A-Za-z0-9]{22})([./A-Za-z0-9]{31})$")
SHA512 = re.compile(r"^\$6\$(?:rounds=([0-9]+)\$)?([./A-Za-z0-9]{1,16})\$([./A-Za-z0-9]{86})$")
YESCRYPT = re.compile(r"^\$y\$([./A-Za-z0-9]+)\$([./A-Za-z0-9]+)\$([./A-Za-z0-9]+)$")

def ozet_ayristir(metin):
    if not isinstance(metin, str):
        raise ValueError("Özet metin olmalı")
    if re.fullmatch(r"[0-9A-Fa-f]{32}", metin):
        return {"tur":"ntlm", "digest":metin.lower()}
    m = BCRYPT.fullmatch(metin)
    if m:
        surum, cost, salt, digest = m.groups()
        return {"tur":"bcrypt", "surum":surum, "cost":int(cost), "salt":salt, "digest":digest}
    m = SHA512.fullmatch(metin)
    if m:
        rounds, salt, digest = m.groups()
        rounds = int(rounds) if rounds else 5000
        if not 1000 <= rounds <= 999999999:
            raise ValueError("sha512crypt rounds aralık dışı")
        return {"tur":"sha512crypt", "rounds":rounds, "salt":salt, "digest":digest}
    m = YESCRYPT.fullmatch(metin)
    if m:
        parametreler, salt, digest = m.groups()
        return {"tur":"yescrypt", "parametreler":parametreler, "salt":salt, "digest":digest}
    raise ValueError("Desteklenmeyen veya belirsiz özet biçimi")

def shadow_raporu(satirlar, minimum_bcrypt_cost=12):
    kayitlar = []
    salt_gruplari = {}
    dusuk = []
    adlar = ("kullanici", "parola_alani", "son_degisim", "min_gun", "max_gun",
             "uyari_gun", "pasif_gun", "bitis", "rezerve")
    for satir in satirlar:
        if not satir.strip():
            continue
        alanlar = satir.rstrip("\n").split(":")
        if len(alanlar) != 9:
            raise ValueError("Shadow satırı dokuz alan olmalı")
        kayit = dict(zip(adlar, alanlar))
        for ad in adlar[2:8]:
            deger = kayit[ad]
            if deger == "":
                kayit[ad] = None
            elif not deger.isdecimal():
                raise ValueError("Shadow gün alanı sayısal olmalı")
            else:
                kayit[ad] = int(deger)
        parola_alani = kayit["parola_alani"]
        if parola_alani == "":
            kayit["durum"] = "parolasiz"
            kayit["ozet"] = None
        elif parola_alani.startswith(("!", "*")):
            kayit["durum"] = "kilitli"
            kayit["ozet"] = None
        else:
            kayit["durum"] = "ozet"
            kayit["ozet"] = ozet_ayristir(parola_alani)
        if kayit["ozet"] and "salt" in kayit["ozet"]:
            salt_gruplari.setdefault(kayit["ozet"]["salt"], []).append(kayit["kullanici"])
        if kayit["ozet"] and kayit["ozet"]["tur"] == "bcrypt" and kayit["ozet"]["cost"] < minimum_bcrypt_cost:
            dusuk.append(kayit["kullanici"])
        kayitlar.append(kayit)
    tekrarlar = [{"salt":salt, "kullanicilar":sorted(kullanicilar)}
                 for salt, kullanicilar in salt_gruplari.items() if len(kullanicilar) > 1]
    return {"kayitlar":kayitlar,
            "tekrarlanan_saltlar":sorted(tekrarlar, key=lambda x:x["salt"]),
            "dusuk_bcrypt_cost":sorted(dusuk)}

satirlar = open("hash_formats/shadow.txt", encoding="utf-8").readlines()
print(shadow_raporu(satirlar))
```

```hint
Önce `split(":")` sonucunun uzunluğunu denetle. Salt gruplarını `{salt:[kullanici...]}` sözlüğünde topla; düşük cost koşulunda önce türün tam `bcrypt` olduğunu sına.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from hash_formats_lab import hazirla
hazirla()
```
:::

::: anlat Araç modu biçimden seçilir; sürüm notu saklanır
Bu derste komut çalıştırılmayacak; yalnız biçim → mod eşlemesi öğrenilecek. Yaygın başlangıç eşlemesi:

| Biçim | Hashcat `-m` | John Jumbo `--format` |
|---|---|---|
| NTLM | `1000` | `nt` |
| bcrypt `$2a/$2b/$2y$` | `3200` | `bcrypt` |
| sha512crypt `$6$` | `1800` | `sha512crypt` |
| yescrypt `$y$` | `30600` | `yescrypt` |

Bunlar çalıştırma talimatı değil, sınavda ve raporda kullanılan tanımlayıcılardır. Kurulu araçta `john --list=formats` veya Hashcat'in kendi yardım/sürüm çıktısıyla destek doğrulanır. Özellikle yescrypt desteği sürüme ve derlemeye bağlıdır. John'daki genel `crypt` modu, desteği **çalıştıran sistemin crypt(3) kitaplığına** bırakabilir; her yerde yescrypt anlamına gelmez ve bu görevde otomatik eşdeğer sayılmaz. John core/Jumbo farkı da göz ardı edilmez. Mod numarasını bilmek özetin parolasını vermez.
:::

::: gorev 3 · Aracın doğru modunu seç
`arac_modu(arac, tur)` işlevini yaz. `arac` yalnız `hashcat` veya `john-jumbo`; `tur` yalnız `ntlm`, `bcrypt`, `sha512crypt`, `yescrypt` olabilir. Yukarıdaki tablonun mod metnini döndür. Bilinmeyen araç/tür, genel `john`, `crypt`, `$6$` gibi normalize edilmemiş tür veya büyük/küçük harf değişimi için tahmin yapma; `ValueError` yükselt.

Ayrıca `surum_dogrulanmali(arac, tur)` işlevini yaz: bütün geçerli çağrılarda `True`, geçersizlerde `ValueError` döndürsün. Böylece raporlayan kod, özellikle yescrypt ve John desteğini kurulu sürümle doğrulama yükümlülüğünü atlayamaz.

```starter
def arac_modu(arac, tur):
    return "crypt"

def surum_dogrulanmali(arac, tur):
    return False

print(arac_modu("hashcat", "ntlm"))
```

```test
need("arac_modu"); need("surum_dogrulanmali")
beklenen = {
    ("hashcat", "ntlm"):"1000", ("hashcat", "bcrypt"):"3200",
    ("hashcat", "sha512crypt"):"1800", ("hashcat", "yescrypt"):"30600",
    ("john-jumbo", "ntlm"):"nt", ("john-jumbo", "bcrypt"):"bcrypt",
    ("john-jumbo", "sha512crypt"):"sha512crypt", ("john-jumbo", "yescrypt"):"yescrypt"
}
for anahtar, mod in beklenen.items():
    eq(arac_modu(*anahtar), mod, "araç ve biçim modu: " + repr(anahtar))
    eq(surum_dogrulanmali(*anahtar), True, "kurulu sürüm/derleme desteği doğrulanır")
for arac, tur in (("john", "yescrypt"), ("hashcat", "crypt"), ("hashcat", "$6$"),
                  ("Hashcat", "ntlm"), ("john-jumbo", "NTLM"), ("", "ntlm")):
    raises(ValueError, arac_modu, arac, tur, msg="belirsiz araç/tür reddedilir")
    raises(ValueError, surum_dogrulanmali, arac, tur, msg="geçersiz çağrı sessizce doğrulanmaz")
```

```solution
MODLAR = {
    "hashcat": {"ntlm":"1000", "bcrypt":"3200", "sha512crypt":"1800", "yescrypt":"30600"},
    "john-jumbo": {"ntlm":"nt", "bcrypt":"bcrypt", "sha512crypt":"sha512crypt", "yescrypt":"yescrypt"}
}

def arac_modu(arac, tur):
    try:
        return MODLAR[arac][tur]
    except (KeyError, TypeError) as e:
        raise ValueError("Bilinmeyen araç veya özet türü") from e

def surum_dogrulanmali(arac, tur):
    arac_modu(arac, tur)
    return True

print(arac_modu("hashcat", "ntlm"))
```

```hint
İki katmanlı sabit sözlük kullan. Önce `MODLAR[arac][tur]` erişimini yap; `KeyError` ve `TypeError` durumunda aynı `ValueError` hatasını yükselt.
```
:::

::: anlat Bulguyu güvenli ve dürüst raporla
İyi bir CPTS notu “hash buldum, parola bu” demez. Kaynağı ve erişim yetkisini, kullanıcı/hesap bağlamını, tam biçim kimliğini, salt ve work factor ayrımını, kullanılan araç sürümünü ve doğrulama sınırını kaydeder. 32 hex değeri bağlamsız NTLM diye etiketlemez; `$6$` ile `$y$` biçimini karıştırmaz; bcrypt cost'u ile yescrypt `j9T` metnini aynı sayı gibi kıyaslamaz.

Salt tekrarı ve düşük cost, iyileştirilmesi gereken depolama politikası bulgularıdır; parolanın kendisi değildir. Testte parser'ı bozuk biçim, yanlış cost ve eksik alanlarla mutasyona uğratmak, yanlış pozitifleri engeller. Gerçek kanıtı yalnız yetkili ve kısıtlı depoda tut; rapora gerekiyorsa maskele, çalışma dosyalarını ve yedekleri koru. Araç desteği belirsizse modu tahmin etmek yerine “kurulu sürümde doğrulanmadı” yaz.
:::
