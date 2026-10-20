---
id: p53
title: Serileştirme · pickle ve shelve
summary: Python nesnelerini olduğu gibi saklamak; pickle.dumps/loads ve dosyaya dump/load, paylaşılan başvuruların korunması, protokoller, nelerin serileştirilemediği, __getstate__/__setstate__, shelve ile kalıcı sözlük ve writeback tuzağı, güvenilmeyen veriyi açmamak, HMAC imzası ve find_class ile kısıtlı okuyucu.
---

::: anlat pickle: nesneyi olduğu gibi saklamak
JSON (P29) yalnızca sözlük, liste, metin, sayı, bool ve `None` taşır. Demet listeye döner, küme hiç yazılamaz, kendi sınıfların ise `TypeError` verir. **pickle** ise hemen her Python nesnesini, aralarındaki başvurularla birlikte **bayt dizisine** çevirir ve geri kurar:

```python
import pickle

veri = {"ad": "web01", "portlar": (80, 443), "etiketler": {"prod", "eu"}}
baytlar = pickle.dumps(veri)                 #! nesne → bayt
geri = pickle.loads(baytlar)                 #! bayt → nesne
print(type(baytlar).__name__, geri == veri, type(geri["portlar"]).__name__)

with open("veri.pkl", "wb") as f:            #! dosyaya: ikili kip ("wb")
    pickle.dump(veri, f)
with open("veri.pkl", "rb") as f:
    print(pickle.load(f)["ad"])
```

| | JSON | pickle |
|---|---|---|
| Biçim | metin, dilden bağımsız | ikili, yalnızca Python |
| Türler | temel türler | hemen her şey: demet, küme, kendi sınıfların |
| Paylaşılan başvuru | kopyalanır | korunur |
| Güvenlik | yalnızca veri taşır | **açılırken kod çalıştırabilir** |
| Kullanım | veri alışverişi, API | kendi programının kendi verisi: önbellek, ara sonuç |

Aynı nesneye iki yerden işaret eden yapılar (P14) korunur: geri kurulan nesnede de iki işaretçi **aynı** nesneyi gösterir.

### Protokoller ve sınırlar
`pickle.dumps(nesne, protocol=...)` bayt biçiminin sürümünü seçer: Python 3.8'den beri varsayılan 4, en yüksek 5. Eski bir Python'un okuyacağı veriyi yazarken düşük bir protokol seçilir.

Serileştirilemeyenler: `lambda`'lar ve iç içe tanımlanmış fonksiyonlar, açık dosyalar, soketler, kilitler, üreteçler. Sınıflar ve fonksiyonlar **adlarıyla** (modül + ad) kaydedilir, kodlarıyla değil: veriyi açan programda aynı sınıf aynı adla içe aktarılabilir olmalıdır.

### Ne saklanacağını seçmek: __getstate__ ve __setstate__
Bir nesne serileştirilemeyen bir alan taşıyorsa (bağlantı, kilit) ya da bazı alanların saklanmasını istemiyorsan:

```python
import pickle, threading

class Istemci:
    def __init__(self, ad):
        self.ad = ad
        self.kilit = threading.Lock()        #! serileştirilemez

    def __getstate__(self):                  #! pickle'a ne verilecek
        durum = self.__dict__.copy()
        del durum["kilit"]
        return durum

    def __setstate__(self, durum):           #! açılırken nasıl kurulacak
        self.__dict__.update(durum)
        self.kilit = threading.Lock()        #! yenisini oluştur

i = pickle.loads(pickle.dumps(Istemci("web01")))
print(i.ad, type(i.kilit).__name__)
```
:::

::: anlat shelve ve güvenlik
**shelve**, pickle'ın üstüne kurulmuş, diskte duran bir **sözlüktür**: anahtarlar metin, değerler pickle'lanabilen herhangi bir nesne:

```python
import shelve

with shelve.open("envanter") as db:          #! dosya yoksa oluşturur
    db["web01"] = {"cpu": 72, "etiketler": ["prod"]}
with shelve.open("envanter") as db:          #! sonraki çalıştırmada veri yerinde
    print(db["web01"]["cpu"], "web01" in db, len(db))
```

> [!TUZAK]
> `db["web01"]["etiketler"].append("eu")` **kalıcı olmaz**: `db["web01"]` diskteki verinin bir **kopyasını** döndürür, ekleme o kopyaya yapılır ve kopya atılır. Ya değeri al, değiştir ve **yeniden ata** (`kayit = db["web01"]; kayit["etiketler"].append("eu"); db["web01"] = kayit`), ya da `shelve.open(..., writeback=True)` kullan; o zaman okunan her şey bellekte tutulur ve kapanışta yazılır (bellek ve süre bedeliyle).

### Güvenilmeyen pickle'ı açma
pickle bir veri biçimi değil, küçük bir **komut dilidir**: açılırken nesneleri kurmak için fonksiyon çağırabilir. Bu yüzden Python belgeleri açıkça uyarır: **güvenmediğin bir kaynaktan gelen pickle'ı asla açma.** Ağdan, kullanıcıdan ya da paylaşılan bir klasörden gelen veri için JSON kullan.

Kendi programının yazdığı pickle'ı başka bir yerde saklaman gerekiyorsa iki savunma vardır:

1. **İmzala** (P52): baytların bir HMAC'ini sakla, açmadan önce doğrula. Anahtarı bilmeyen biri veriyi değiştiremez.
2. **Kısıtla**: `pickle.Unpickler`'ın `find_class` metodu, veride adı geçen her sınıf ve fonksiyon için çağrılır; yalnızca izin listesindekileri ver:

```python
import pickle, io, datetime

class KisitliOkuyucu(pickle.Unpickler):
    IZINLI = {("builtins", "set"), ("builtins", "frozenset")}

    def find_class(self, modul, ad):
        if (modul, ad) in self.IZINLI:
            return super().find_class(modul, ad)
        raise pickle.UnpicklingError(f"izin verilmeyen tür: {modul}.{ad}")

def guvenli_ac(baytlar):
    return KisitliOkuyucu(io.BytesIO(baytlar)).load()

print(guvenli_ac(pickle.dumps({"a": [1, 2]})))
try:
    guvenli_ac(pickle.dumps(datetime.date(2026, 10, 19)))
except pickle.UnpicklingError as e:
    print(e)
```
:::

::: tahmin
Üç satır yazar:

```python
import pickle
veri = {"ad": "web01", "portlar": (80, 443), "etiketler": {"prod"}}
geri = pickle.loads(pickle.dumps(veri))
print(geri == veri, geri is veri)
print(type(geri["portlar"]).__name__, type(geri["etiketler"]).__name__)
a = [1, 2]
b = [a, a]
c = pickle.loads(pickle.dumps(b))
c[0].append(3)
print(c[1])
```

???

`True False`, `tuple set`, `[1, 2, 3]`. Geri kurulan sözlük eşittir ama yeni bir nesnedir. pickle demeti demet, kümeyi küme olarak korur (JSON ikisini de bozardı). `b`'nin iki elemanı aynı listeydi; pickle bu paylaşımı korur, bu yüzden `c[0]`'a ekleme `c[1]`'de de görünür.
:::

::: gorev Bağlantıyı dışarıda bırak
`Oturum` sınıfını yaz: `ad` ve `ayarlar` (sözlük) alanları ile serileştirilemeyen bir `kilit` (`threading.Lock()`) alanı olsun. `__getstate__` ve `__setstate__` ile pickle'a **yalnızca** `ad` ve `ayarlar` gitsin; açılan nesnede `kilit` yeni bir kilit olsun.

```starter
import threading


class Oturum:
    def __init__(self, ad, ayarlar):
        self.ad = ad
        self.ayarlar = ayarlar
        self.kilit = threading.Lock()
```

```test
import pickle
need("Oturum", "sınıf")
o = Oturum("web01", {"port": 8443})
durum = o.__getstate__()
eq(durum, {"ad": "web01", "ayarlar": {"port": 8443}}, "__getstate__ yalnızca ad ve ayarları verir")
baytlar = pickle.dumps(o)
ok(b"kilit" not in baytlar, "kilit pickle'a hiç girmemeli")
g = pickle.loads(baytlar)
ok(isinstance(g, Oturum), "açılan nesne bir Oturum")
eq((g.ad, g.ayarlar), ("web01", {"port": 8443}), "veri korunur")
ok(hasattr(g, "kilit") and hasattr(g.kilit, "acquire"), "kurulan nesnede yeni bir kilit var")
ok(g.kilit is not o.kilit, "kilit yeni oluşturulmuş")
```

```solution
import threading


class Oturum:
    def __init__(self, ad, ayarlar):
        self.ad = ad
        self.ayarlar = ayarlar
        self.kilit = threading.Lock()

    def __getstate__(self):
        durum = self.__dict__.copy()
        del durum["kilit"]
        return durum

    def __setstate__(self, durum):
        self.__dict__.update(durum)
        self.kilit = threading.Lock()
```

```hint
Başlangıç kodunu pickle'lamak `TypeError: cannot pickle '_thread.lock' object` verir. `__getstate__` kilitsiz bir sözlük döndürsün.
```

```hint
`__setstate__(self, durum)`: `self.__dict__.update(durum)`, sonra `self.kilit = threading.Lock()`.
```
:::

::: gorev shelve ile kalıcı kayıt
İki fonksiyon yaz; ikisi de her çağrıda shelve dosyasını açıp kapatsın:

- `ziyaret(dosya, sayfa)`: sayfanın ziyaret sayısını bir artırıp yeni değeri döndürsün (ilk ziyarette 1).
- `etiket_ekle(dosya, sunucu, etiket)`: `sunucu` anahtarındaki **listeye** etiketi eklesin (anahtar yoksa yeni liste) ve güncel listeyi döndürsün. Ekleme diske **gerçekten** yazılmalı.

```starter
import shelve


def ziyaret(dosya, sayfa):
    with shelve.open(dosya) as db:
        db[sayfa] = 1
        return db[sayfa]


def etiket_ekle(dosya, sunucu, etiket):
    with shelve.open(dosya) as db:
        if sunucu not in db:
            db[sunucu] = []
        db[sunucu].append(etiket)
        return db[sunucu]
```

```test
import shelve
need("ziyaret")
need("etiket_ekle")
eq([ziyaret("sayac", "/rapor") for _ in range(3)], [1, 2, 3], "sayaç kalıcı artar")
eq(ziyaret("sayac", "/giris"), 1, "başka sayfa ayrı sayılır")
etiket_ekle("etiket", "web01", "prod")
eq(etiket_ekle("etiket", "web01", "eu"), ["prod", "eu"], "güncel liste")
with shelve.open("etiket") as db:
    eq(db["web01"], ["prod", "eu"], "diske yazılmış olmalı")
```

```solution
import shelve


def ziyaret(dosya, sayfa):
    with shelve.open(dosya) as db:
        db[sayfa] = db.get(sayfa, 0) + 1
        return db[sayfa]


def etiket_ekle(dosya, sunucu, etiket):
    with shelve.open(dosya) as db:
        liste = db.get(sunucu, [])
        liste.append(etiket)
        db[sunucu] = liste
        return liste
```

```hint
Sayaç: `db[sayfa] = db.get(sayfa, 0) + 1`.
```

```hint
`db[sunucu].append(...)` diskteki listenin bir kopyasını değiştirir. Listeyi al, değiştir, `db[sunucu] = liste` ile geri yaz.
```
:::

::: gorev İmzalı pickle
Kendi programının yazdığı veriyi değiştirilmeye karşı korumak için iki fonksiyon yaz:

- `imzala(nesne, anahtar)`: nesneyi pickle'la ve başına baytların HMAC-SHA256 özetini (32 bayt) ekleyerek döndürsün.
- `ac(veri, anahtar)`: ilk 32 baytı imza olarak ayır, geri kalanın imzasını yeniden hesaplayıp **sabit süreli** karşılaştır; tutmazsa `ValueError("imza geçersiz")` fırlatsın, tutarsa **ancak o zaman** `pickle.loads` ile açsın.

```starter
import pickle


def imzala(nesne, anahtar):
    return pickle.dumps(nesne)


def ac(veri, anahtar):
    return pickle.loads(veri)
```

```test
need("imzala")
need("ac")
anahtar = b"gizli-anahtar"
paket = imzala({"ad": "web01", "cpu": 72}, anahtar)
eq(len(paket) > 32, True, "imza + veri")
eq(ac(paket, anahtar), {"ad": "web01", "cpu": 72}, "doğru anahtarla açılır")
bozuk = paket[:-1] + bytes([paket[-1] ^ 1])
raises(ValueError, ac, bozuk, anahtar, msg="değiştirilmiş veri reddedilir")
raises(ValueError, ac, paket, b"baska-anahtar", msg="yanlış anahtar reddedilir")
raises(ValueError, ac, b"kisa", anahtar, msg="imzadan kısa veri reddedilir")
ok("compare_digest" in src, "hmac.compare_digest kullan")
```

```solution
import hashlib
import hmac
import pickle


def imzala(nesne, anahtar):
    govde = pickle.dumps(nesne)
    imza = hmac.new(anahtar, govde, hashlib.sha256).digest()
    return imza + govde


def ac(veri, anahtar):
    imza, govde = veri[:32], veri[32:]
    beklenen = hmac.new(anahtar, govde, hashlib.sha256).digest()
    if len(imza) != 32 or not hmac.compare_digest(imza, beklenen):
        raise ValueError("imza geçersiz")
    return pickle.loads(govde)
```

```hint
İmza: `hmac.new(anahtar, govde, hashlib.sha256).digest()` (32 bayt). Paket: `imza + govde`.
```

```hint
Açarken önce doğrula, sonra yükle; doğrulanmamış baytlar `pickle.loads`'a hiç ulaşmamalı. Kısa veride dilimlenen imza 32 bayttan kısa olur; onu da reddet.
```
:::
