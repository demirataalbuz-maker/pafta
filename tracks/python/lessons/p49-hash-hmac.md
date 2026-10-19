---
id: p49
title: Özet Fonksiyonları ve HMAC
summary: hashlib ile bütünlük kontrolü, büyük dosyaları parça parça özetlemek, HMAC ile mesaj doğrulama.
---

::: anlat Parmak izi: özet fonksiyonu
Bir **kriptografik özet fonksiyonu** (hash), herhangi uzunluktaki veriyi sabit uzunlukta bir "parmak izine" çevirir. İyi bir özet fonksiyonunun dört özelliği vardır:

1. **Belirlenimci**: aynı girdi, her zaman aynı çıktı
2. **Sabit uzunluk**: 1 bayt da 10 GB da olsa SHA-256 çıktısı 32 bayttır
3. **Çığ etkisi**: girdide tek bir bit değişse çıktının yaklaşık yarısı değişir
4. **Tek yönlü ve çakışmaya dayanıklı**: çıktıdan girdiyi bulmak ya da aynı çıktıyı veren iki girdi bulmak pratikte imkânsızdır

```python
import hashlib

print(hashlib.sha256(b"pafta").hexdigest())
print(hashlib.sha256(b"Pafta").hexdigest())          #! tek harf → bambaşka özet
h = hashlib.sha256()
h.update(b"paf")                                     #! parça parça beslenebilir
h.update(b"ta")
print(h.hexdigest() == hashlib.sha256(b"pafta").hexdigest())
print(hashlib.sha256(b"x").digest_size, "bayt")
print(sorted(hashlib.algorithms_guaranteed)[:6])
```

### Büyük dosyaları özetlemek
Dosyayı belleğe tümüyle yüklemeden, sabit boyutlu bloklar halinde besle:

```python
import hashlib

with open("arsiv.bin", "wb") as f:
    f.write(b"\x00" * 3_000_000)

def dosya_ozeti(yol, blok=65536):
    h = hashlib.sha256()
    with open(yol, "rb") as f:                       #! ikilik kip!
        for parca in iter(lambda: f.read(blok), b""):  #! P42'deki iki argümanlı iter
            h.update(parca)
    return h.hexdigest()

print(dosya_ozeti("arsiv.bin")[:16], "…")
```

> [!GÜVENLİK]
> **Bütünlük doğrulaması**: indirdiğin bir yazılımın yayıncının sitesindeki SHA-256 değeriyle aynı olması, dosyanın yolda değişmediğini gösterir. Olay müdahalesinde şüpheli dosyaların özetleri VirusTotal gibi tehdit istihbaratı kaynaklarında aranır ve kanıt zincirinde delillerin değişmediği özetlerle belgelenir. **MD5 ve SHA-1** artık güvenlik için kullanılmaz (çakışma üretmek pratiktir); sadece eski sistemlerle uyum ya da yinelenen dosya tespiti gibi güvenlik dışı işler için kalmıştır.
:::

::: tahmin
Çıktı tek satır:

```python
import hashlib
a = hashlib.sha256(b"pafta").hexdigest()
b = hashlib.sha256(b"Pafta").hexdigest()
print(len(a), a == b, a == hashlib.sha256(b"pafta").hexdigest())
```

???

`64 False True`. SHA-256 32 bayttır, yani 64 onaltılık karakter. Tek harf farkı tamamen farklı bir özet üretir. Aynı girdi ise her zaman aynı özeti verir.
:::

::: anlat HMAC: anahtarlı doğrulama
Düz bir özet bütünlüğü kanıtlamaz: saldırgan mesajı değiştirip özeti **yeniden hesaplayabilir**. Mesajın gerçekten anahtara sahip birinden geldiğini kanıtlamak için **HMAC** (anahtarlı özet) kullanılır:

```python
import hmac, hashlib

ANAHTAR = b"sunucu-gizli-anahtari"

def imzala(mesaj: bytes) -> str:
    return hmac.new(ANAHTAR, mesaj, hashlib.sha256).hexdigest()

def dogrula(mesaj: bytes, imza: str) -> bool:
    return hmac.compare_digest(imzala(mesaj), imza)  #! sabit süreli karşılaştırma

m = b"kullanici=ali&rol=user"
imza = imzala(m)
print(dogrula(m, imza))
print(dogrula(b"kullanici=ali&rol=admin", imza))     #! değiştirilmiş mesaj reddedilir
```

Webhook doğrulama, API istek imzaları ve oturum çerezleri bu kalıbı kullanır: sunucu veriyi imzalar, geri geldiğinde imzayı yeniden hesaplayıp karşılaştırır.

> [!TUZAK]
> İmzaları `==` ile karşılaştırma, **`hmac.compare_digest`** kullan. `==` ilk farklı karakterde durur; yanıt süresindeki mikrosaniyelik farklar, saldırganın imzayı karakter karakter tahmin etmesine yarayabilir (zamanlama yan kanalı). `compare_digest` her zaman tüm metni karşılaştırır.

> [!NOT]
> **Parola saklamak** ayrı bir problemdir: düz SHA-256 hızlı olduğu için uygun değildir. Parolalar için bilerek **yavaş** ve **tuzlu** fonksiyonlar kullanılır: `hashlib.scrypt`, `hashlib.pbkdf2_hmac` ya da argon2/bcrypt kütüphaneleri. Her kullanıcıya ayrı bir rastgele tuz verilir ve tuz özetle birlikte saklanır.
:::

::: tahmin
Çıktı tek satır:

```python
import hmac, hashlib
anahtar = b"gizli"
m1 = hmac.new(anahtar, b"tutar=100", hashlib.sha256).hexdigest()
m2 = hmac.new(anahtar, b"tutar=900", hashlib.sha256).hexdigest()
print(m1 == m2, hmac.compare_digest(m1, m1), len(m1))
```

???

`False True 64`. Farklı mesajlar farklı imzalar üretir. HMAC-SHA256 çıktısı da 32 bayt, yani 64 onaltılık karakterdir.
:::

::: gorev Dosya özeti
`dosya_ozeti(yol)` fonksiyonu dosyanın SHA-256 özetini onaltılık metin olarak döndürsün. Dosyayı **ikilik kipte** ve **parça parça** (ör. 8192 baytlık bloklar) oku; `read()` ile tamamını tek seferde okuma.

```setup
import os
with open("kucuk.txt", "wb") as f:
    f.write(b"merhaba\n")
with open("buyuk.bin", "wb") as f:
    f.write(bytes(range(256)) * 20000)
open("bos.dat", "wb").close()
```

```starter
import hashlib

def dosya_ozeti(yol):
    pass
```

```test
import hashlib
need("dosya_ozeti")
for ad in ("kucuk.txt", "buyuk.bin", "bos.dat"):
    beklenen = hashlib.sha256(open(ad, "rb").read()).hexdigest()
    eq(dosya_ozeti(ad), beklenen, f"{ad} özeti")
ok("read()" not in src.replace(" ", ""), "dosyayı tek seferde read() ile okuma, parça parça oku")
```

```solution
import hashlib

def dosya_ozeti(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(8192), b""):
            h.update(parca)
    return h.hexdigest()
```

```hint
`h = hashlib.sha256()`, sonra döngüde `h.update(parca)`. Parçalar için `iter(lambda: f.read(8192), b"")` ya da `while True` + boş parçada `break`.
```
:::

::: gorev İmzala ve doğrula
İki fonksiyon yaz:

- `imzala(anahtar, mesaj)`: HMAC-SHA256 imzasını onaltılık metin olarak döndürür. `anahtar` ve `mesaj` metin (`str`) olarak gelir; UTF-8 ile bayta çevir.
- `dogrula(anahtar, mesaj, imza)`: imza doğruysa `True`. Karşılaştırmayı `hmac.compare_digest` ile yap.

```starter
import hmac, hashlib

def imzala(anahtar, mesaj):
    pass

def dogrula(anahtar, mesaj, imza):
    pass
```

```test
import hmac, hashlib
need("imzala"); need("dogrula")
beklenen = hmac.new(b"k3y", "olay=giris&kullanici=ayşe".encode(), hashlib.sha256).hexdigest()
eq(imzala("k3y", "olay=giris&kullanici=ayşe"), beklenen, "doğru HMAC-SHA256")
i = imzala("anahtar", "tutar=100")
eq(dogrula("anahtar", "tutar=100", i), True, "doğru imza → True")
eq(dogrula("anahtar", "tutar=900", i), False, "değişmiş mesaj → False")
eq(dogrula("baska", "tutar=100", i), False, "yanlış anahtar → False")
ok(calls("compare_digest"), "compare_digest kullan")
```

```solution
import hmac, hashlib

def imzala(anahtar, mesaj):
    return hmac.new(anahtar.encode("utf-8"), mesaj.encode("utf-8"), hashlib.sha256).hexdigest()

def dogrula(anahtar, mesaj, imza):
    return hmac.compare_digest(imzala(anahtar, mesaj), imza)
```

```hint
`hmac.new(anahtar_bayt, mesaj_bayt, hashlib.sha256).hexdigest()`
```
:::

::: gorev Değişiklik raporu
Bir dosya bütünlük izleyicisinin çekirdeği: `degisenler(onceki, simdiki)` iki `{yol: özet}` sözlüğünü karşılaştırıp şu sözlüğü döndürsün (her liste **alfabetik**):

```python
{"eklenen": [...], "silinen": [...], "degisen": [...]}
```

- `eklenen`: sadece `simdiki`'de olan yollar
- `silinen`: sadece `onceki`'de olan yollar
- `degisen`: ikisinde de olan ama özeti farklı yollar

```starter
def degisenler(onceki, simdiki):
    pass
```

```test
need("degisenler")
once = {"/etc/passwd": "a1", "/etc/hosts": "b2", "/usr/bin/ls": "c3", "/tmp/x": "d4"}
simdi = {"/etc/passwd": "a1", "/etc/hosts": "ff", "/usr/bin/ls": "99", "/etc/cron.d/yeni": "e5"}
eq(degisenler(once, simdi), {"eklenen": ["/etc/cron.d/yeni"], "silinen": ["/tmp/x"],
                             "degisen": ["/etc/hosts", "/usr/bin/ls"]}, "örnek rapor")
eq(degisenler({}, {}), {"eklenen": [], "silinen": [], "degisen": []}, "boş")
eq(degisenler({"a": "1"}, {"a": "1"})["degisen"], [], "değişiklik yok")
```

```solution
def degisenler(onceki, simdiki):
    o, s = set(onceki), set(simdiki)
    return {
        "eklenen": sorted(s - o),
        "silinen": sorted(o - s),
        "degisen": sorted(y for y in o & s if onceki[y] != simdiki[y]),
    }
```

```hint
Anahtar kümeleriyle çalış: `set(simdiki) - set(onceki)` eklenenleri verir. Değişenler için ortak anahtarlarda özetleri karşılaştır.
```
:::
