---
id: p47
title: Dekoratörler II
summary: Parametreli dekoratörler, kayıt (registry) kalıbı, yeniden deneme, sınıf tabanlı dekoratörler.
---

::: anlat Parametreli dekoratör: üç kat
`@tekrar(3)` gibi argüman alan bir dekoratör istiyorsan bir kat daha gerekir. `tekrar(3)` çağrısı önce **asıl dekoratörü** üretmeli, o da fonksiyonu sarmalı:

```python
from functools import wraps

def tekrar(n):                         #! 1. kat: parametreyi alır
    def dekorator(fonk):               #! 2. kat: fonksiyonu alır
        @wraps(fonk)
        def sarmal(*args, **kwargs):   #! 3. kat: çağrıyı yakalar
            return [fonk(*args, **kwargs) for _ in range(n)]
        return sarmal
    return dekorator

@tekrar(3)                             #! = selam = tekrar(3)(selam)
def selam(ad):
    return f"merhaba {ad}"

print(selam("ali"))
```

Okuma kılavuzu: `@ifade` satırında Python önce **ifadeyi değerlendirir** (`tekrar(3)` → `dekorator`), sonra sonucu fonksiyona uygular. `@tekrar` (parantezsiz) yazarsan `tekrar(selam)` olur ve n'e fonksiyon geçer; klasik bir hatadır.

### Yetki kontrolü
Erişim kontrolünü iş mantığından ayırmanın en temiz yolu dekoratördür. Web çatılarındaki `@login_required` böyle çalışır:

```python
from functools import wraps

def rol_gerekli(rol):
    def dekorator(fonk):
        @wraps(fonk)
        def sarmal(kullanici, *args, **kwargs):
            if rol not in kullanici.get("roller", []):
                raise PermissionError(f"{kullanici['ad']}: '{rol}' rolü gerekli")
            return fonk(kullanici, *args, **kwargs)
        return sarmal
    return dekorator

@rol_gerekli("admin")
def kullanici_sil(kullanici, hedef):
    return f"{hedef} silindi"

print(kullanici_sil({"ad": "ayse", "roller": ["admin"]}, "test01"))
try:
    kullanici_sil({"ad": "ali", "roller": ["user"]}, "test01")
except PermissionError as e:
    print("engellendi:", e)
```

> [!GÜVENLİK]
> Kontrolü her fonksiyonun başına elle yazmak yerine tek bir dekoratörde toplamak **unutulma riskini** azaltır. Yetki açıklarının (OWASP'ta "Broken Access Control", 1 numara) çoğu, kontrolün bir uç noktada **eksik kalmasıdır**. Ama dekoratörün kendisi de test edilmeli: kontrolü yanlış argümana bakarak yapan bir dekoratör, her yeri birden açar.
:::

::: tahmin
Ne yazdırır?

```python
def tekrar(n):
    def dekor(f):
        def sar(*a, **k):
            return [f(*a, **k) for _ in range(n)]
        return sar
    return dekor

@tekrar(3)
def ping():
    return "pong"

print(ping())
```

???

`['pong', 'pong', 'pong']`. `tekrar(3)` dekoratörü üretir, o da `ping`'i sarar. Sarmal fonksiyonu 3 kez çağırıp sonuçları listeler.
:::

::: anlat Kayıt kalıbı ve sınıf tabanlı dekoratör
Dekoratör fonksiyonu **sarmak zorunda değildir**: sadece bir yere kaydedip aynen geri verebilir. Komut sistemleri, eklentiler, olay işleyicileri böyle kurulur:

```python
KOMUTLAR = {}

def komut(ad):
    def kaydet(fonk):
        KOMUTLAR[ad] = fonk
        return fonk                    #! fonksiyonu değiştirmeden geri ver
    return kaydet

@komut("durum")
def durum():
    return "çalışıyor"

@komut("surum")
def surum():
    return "1.4.2"

for ad in sorted(KOMUTLAR):
    print(ad, "→", KOMUTLAR[ad]())
```

**Durum tutan** dekoratörler için sınıf da kullanılabilir: `__init__` fonksiyonu alır, `__call__` çağrıyı yakalar:

```python
import functools

class HizSiniri:
    def __init__(self, fonk):
        functools.update_wrapper(self, fonk)   #! wraps'in sınıf versiyonu
        self.fonk = fonk
        self.cagri = 0

    def __call__(self, *args, **kwargs):
        self.cagri += 1
        if self.cagri > 3:
            raise RuntimeError("çok fazla istek")
        return self.fonk(*args, **kwargs)

@HizSiniri
def api():
    return "tamam"

print([api() for _ in range(3)], api.cagri)
```

> [!DERİN]
> Dekoratörler sınıflara da uygulanabilir: `@dataclass` sınıfı alır, değiştirir ve geri verir. Ama sınıf tabanlı bir dekoratörü bir **metoda** uygularsan dikkat: sınıf örneği bir fonksiyon değildir, bu yüzden `self` otomatik bağlanmaz. Bunu düzeltmek için dekoratör sınıfına `__get__` yazmak gerekir, yani tanımlayıcı olmak. P64'ta bu bağlantıyı kuracağız.
:::

::: tahmin
Çıktı tek satır:

```python
KOMUTLAR = {}

def komut(ad):
    def kaydet(f):
        KOMUTLAR[ad] = f
        return f
    return kaydet

@komut("selam")
def s():
    return "merhaba"

@komut("saat")
def t():
    return "12:00"

print(sorted(KOMUTLAR), KOMUTLAR["selam"](), s())
```

???

`['saat', 'selam'] merhaba merhaba`. Dekoratör fonksiyonları sözlüğe kaydedip **değiştirmeden** geri verdiği için `s()` de normal çalışır.
:::

::: gorev Rol kontrolü
`rol_gerekli(*roller)` adında parametreli bir dekoratör yaz. Sarmalanan fonksiyonun **ilk argümanı** bir kullanıcı sözlüğüdür (`{"ad": ..., "roller": [...]}`). Kullanıcının rollerinden **en az biri** istenen rollerdeyse fonksiyon çalışsın, değilse `PermissionError` yükseltsin. `"roller"` anahtarı hiç yoksa da reddet.

```starter
from functools import wraps

def rol_gerekli(*roller):
    pass
```

```test
need("rol_gerekli")
@rol_gerekli("admin", "denetci")
def rapor(kullanici, ay):
    """aylık rapor"""
    return f"{ay} raporu"
eq(rapor({"ad": "ayse", "roller": ["admin"]}, "ekim"), "ekim raporu", "admin geçer")
eq(rapor({"ad": "deniz", "roller": ["user", "denetci"]}, "kasim"), "kasim raporu", "denetçi geçer")
raises(PermissionError, rapor, {"ad": "ali", "roller": ["user"]}, "ekim", msg="user → PermissionError")
raises(PermissionError, rapor, {"ad": "x"}, "ekim", msg="roller yok → PermissionError")
eq(rapor.__name__, "rapor", "wraps")
```

```solution
from functools import wraps

def rol_gerekli(*roller):
    def dekorator(fonk):
        @wraps(fonk)
        def sarmal(kullanici, *args, **kwargs):
            if not set(kullanici.get("roller", [])) & set(roller):
                raise PermissionError(f"{kullanici.get('ad')}: yetki yok")
            return fonk(kullanici, *args, **kwargs)
        return sarmal
    return dekorator
```

```hint
Üç kat: `rol_gerekli(*roller)` → `dekorator(fonk)` → `sarmal(kullanici, *args, **kwargs)`.
```

```hint
"En az biri" = kesişim boş değil: `set(kullanici.get("roller", [])) & set(roller)`.
```
:::

::: gorev Yeniden dene
`yeniden_dene(deneme=3, hatalar=(ConnectionError,))` dekoratörünü yaz: fonksiyon `hatalar`'dan biriyle başarısız olursa toplam `deneme` kez denesin. Son denemede de başarısız olursa istisnayı yükseltsin. **Başka türdeki** hatalar hemen yükselsin (tekrar denenmesin).

```starter
from functools import wraps

def yeniden_dene(deneme=3, hatalar=(ConnectionError,)):
    pass
```

```test
need("yeniden_dene")
sayac = {"n": 0}
@yeniden_dene(deneme=3)
def kararsiz():
    sayac["n"] += 1
    if sayac["n"] < 3:
        raise ConnectionError("bağlantı koptu")
    return "tamam"
eq(kararsiz(), "tamam", "3. denemede başarılı")
eq(sayac["n"], 3, "toplam 3 çağrı")
sayac["n"] = 0
@yeniden_dene(deneme=2)
def hep_bozuk():
    sayac["n"] += 1
    raise ConnectionError("yok")
raises(ConnectionError, hep_bozuk, msg="2 denemeden sonra yükselt")
eq(sayac["n"], 2, "tam 2 çağrı")
sayac["n"] = 0
@yeniden_dene(deneme=5, hatalar=(TimeoutError,))
def baska_hata():
    sayac["n"] += 1
    raise ValueError("kötü girdi")
raises(ValueError, baska_hata, msg="başka tür hemen yükselir")
eq(sayac["n"], 1, "ValueError tekrar denenmez")
```

```solution
from functools import wraps

def yeniden_dene(deneme=3, hatalar=(ConnectionError,)):
    def dekorator(fonk):
        @wraps(fonk)
        def sarmal(*args, **kwargs):
            for i in range(1, deneme + 1):
                try:
                    return fonk(*args, **kwargs)
                except hatalar:
                    if i == deneme:
                        raise
        return sarmal
    return dekorator
```

```hint
`for i in range(1, deneme + 1):` içinde `try: return fonk(...)`. `except hatalar:` (demet verilebilir) son denemedeyse `raise`.
```
:::

::: gorev Temizlenebilir önbellek
`onbellek` adında bir dekoratör yaz (`lru_cache` kullanmadan): konumsal argümanları anahtar olarak bir sözlükte sonuçları saklasın. Sarmalın iki niteliği olsun:

- `temizle()`: önbelleği boşaltır
- `isabet`: önbellekten kaç kez cevap verildiği

```starter
from functools import wraps

def onbellek(fonk):
    pass
```

```test
need("onbellek")
cagri = []
@onbellek
def pahali(x, y):
    cagri.append((x, y))
    return x * y
eq(pahali(3, 4), 12, "ilk hesap")
eq(pahali(3, 4), 12, "önbellekten")
eq(pahali(2, 5), 10, "yeni argüman")
eq(cagri, [(3, 4), (2, 5)], "asıl fonksiyon 2 kez çalıştı")
eq(pahali.isabet, 1, "1 isabet")
pahali.temizle()
pahali(3, 4)
eq(len(cagri), 3, "temizledikten sonra yeniden hesaplar")
ok(not calls("lru_cache") and not calls("cache"), "lru_cache kullanmadan")
```

```solution
from functools import wraps

def onbellek(fonk):
    depo = {}

    @wraps(fonk)
    def sarmal(*args):
        if args in depo:
            sarmal.isabet += 1
            return depo[args]
        sonuc = fonk(*args)
        depo[args] = sonuc
        return sonuc

    def temizle():
        depo.clear()

    sarmal.isabet = 0
    sarmal.temizle = temizle
    return sarmal
```

```hint
Dekoratörün içinde bir `depo = {}` sözlüğü; anahtar `args` demeti. `temizle` iç fonksiyonunu sarmalın niteliği yap: `sarmal.temizle = temizle`.
```
:::
