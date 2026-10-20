---
id: p39
title: Kapsülleme ve @property
summary: _ ve __ gelenekleri, isim bozma, doğrulayan nitelikler, salt okunur ve hesaplanan alanlar.
---

::: anlat Python'da "private" yok, gelenek var
Java ya da C++'taki `private` anahtar kelimesi Python'da yoktur. Onun yerine bir **gelenek** vardır:

- `ad`: herkese açık
- `_ad`: "iç kullanım, dokunma". Teknik olarak erişilebilir ama dokunursan sonuçtan sen sorumlusun
- `__ad`: **isim bozma** (name mangling). Python bunu sınıf içinde `_SinifAdi__ad`'a çevirir; alt sınıflarla isim çakışmasını önlemek içindir, gizlilik için değil

```python
class Hesap:
    def __init__(self):
        self.sahip = "ali"
        self._bakiye = 100        #! iç kullanım
        self.__pin = "1234"       #! isim bozulur

h = Hesap()
print(h._bakiye)                  #! erişilebilir, sadece "kibarca" gizli
print(hasattr(h, "__pin"))        #! False
print(h._Hesap__pin)              #! bozulmuş adla hâlâ erişilebilir
print(list(vars(h)))
```

> [!ZEN]
> Python topluluğunun deyişiyle: "Hepimiz yetişkiniz" (*we are all consenting adults*). Dil seni zorla engellemez, sadece işaret koyar.

> [!GÜVENLİK]
> `__pin` gibi bir isim **gizlilik sağlamaz**: aynı süreçte çalışan her kod onu okuyabilir, `vars()` onu listeler. Python'da hassas veriyi korumanın yolu erişim belirteci değil; **hiç saklamamak** (parolanın kendisi yerine hash'ini tutmak) ya da işletim sistemi düzeyinde ayırmaktır (ayrı süreç, ayrı kullanıcı).
:::

::: tahmin
Çıktı tek satır:

```python
class K:
    def __init__(self):
        self.__gizli = 1
        self._yari = 2

k = K()
print(k._yari, hasattr(k, "__gizli"), k._K__gizli)
```

???

`2 False 1`. `_yari` sıradan bir niteliktir. `__gizli` sınıf içinde `_K__gizli` olarak saklanır; o yüzden `__gizli` adıyla bulunamaz ama bozulmuş adıyla erişilebilir.
:::

::: anlat @property: nitelik gibi görünen metot
Bir niteliğe değer atanırken **doğrulama** yapmak ya da değeri her okunuşta **hesaplamak** istediğini düşün. Java'da `getX()/setX()` yazılır. Python'da ise önce düz nitelikle başlarsın, ihtiyaç doğunca **arayüzü bozmadan** `@property`'ye geçersin:

```python
class Hedef:
    def __init__(self, host, port):
        self.host = host
        self.port = port               #! bu satır bile setter'dan geçer

    @property
    def port(self):                    #! okuma: h.port
        return self._port

    @port.setter
    def port(self, deger):             #! yazma: h.port = 443
        if not isinstance(deger, int) or not 0 < deger < 65536:
            raise ValueError(f"geçersiz port: {deger!r}")
        self._port = deger

    @property
    def adres(self):                   #! setter yok → salt okunur, hesaplanan alan
        return f"{self.host}:{self.port}"

h = Hedef("web01", 443)
h.port = 8443                          #! düz atama gibi görünür ama doğrulama çalışır
print(h.adres)
try:
    h.port = 70000
except ValueError as e:
    print("reddedildi:", e)
try:
    h.adres = "x"
except AttributeError as e:
    print("salt okunur:", e)
```

Kullanan kod hep `h.port` yazar; içeride basit bir nitelik mi, doğrulayan bir fonksiyon mu olduğunu bilmez. Bu sayede sınıfın içini değiştirdiğinde dışarıdaki kodu değiştirmen gerekmez.

> [!TUZAK]
> Property içinde aynı ada yazarsan sonsuz özyineleme olur: `self.port = deger` setter'ı yeniden çağırır, o da yine kendini... Gerçek değeri **başka bir adda** sakla: `self._port`.

> [!DERİN]
> `property` bir **tanımlayıcıdır** (descriptor): `__get__`, `__set__` ve `__delete__` metotları olan bir nesne. Sınıf niteliği olarak durur ve nesne niteliği erişimini araya girip yakalar. `@port.setter` aynı property nesnesinin setter'ı eklenmiş bir kopyasını döndürür, bu yüzden üç fonksiyonun da adı aynı olmalıdır. P60'ta kendi `property`'ni sıfırdan yazacaksın.
:::

::: tahmin
Ne yazdırır?

```python
class Sicaklik:
    def __init__(self, c):
        self.c = c
    @property
    def f(self):
        return self.c * 9 / 5 + 32

s = Sicaklik(100)
s.c = 0
print(s.f)
```

???

`32.0`. `f` saklanmaz, her okunuşta `c`'den **yeniden hesaplanır**. c 0 yapıldıktan sonra f de ona göre değişir. Bölme `/` olduğu için sonuç float'tır.
:::

::: gorev Doğrulayan e-posta
`Kullanici(ad, eposta)` sınıfında `eposta` bir property olsun:

- Atanırken kenar boşlukları temizlensin ve küçük harfe çevrilsin
- İçinde tam bir `@` yoksa ya da `@`'den önce veya sonra boşsa `ValueError` yükseltsin
- Kurucudaki atama da aynı kontrolden geçsin

```starter
class Kullanici:
    def __init__(self, ad, eposta):
        self.ad = ad
        self.eposta = eposta
```

```test
K = need("Kullanici", "sınıf")
k = K("ali", "  Ali.Veli@Ornek.COM ")
eq(k.eposta, "ali.veli@ornek.com", "temizlenmiş ve küçük harf")
k.eposta = "YENI@x.io"
eq(k.eposta, "yeni@x.io", "sonraki atama da temizlenir")
raises(ValueError, K, "a", "gecersiz", msg="@ yok → ValueError")
raises(ValueError, setattr, k, "eposta", "a@b@c", msg="iki @ → ValueError")
raises(ValueError, setattr, k, "eposta", "@x.io", msg="@ öncesi boş → ValueError")
raises(ValueError, setattr, k, "eposta", "ali@", msg="@ sonrası boş → ValueError")
ok(isinstance(type(k).__dict__.get("eposta"), property), "eposta bir property olmalı")
```

```solution
class Kullanici:
    def __init__(self, ad, eposta):
        self.ad = ad
        self.eposta = eposta

    @property
    def eposta(self):
        return self._eposta

    @eposta.setter
    def eposta(self, deger):
        deger = deger.strip().lower()
        parcalar = deger.split("@")
        if len(parcalar) != 2 or not parcalar[0] or not parcalar[1]:
            raise ValueError(f"geçersiz e-posta: {deger!r}")
        self._eposta = deger
```

```hint
Gerçek değeri `self._eposta`'da sakla. `split("@")` tam 2 parça ve ikisi de dolu olmalı.
```
:::

::: gorev Termostat
`Termostat` sınıfı:

- `hedef` property: 5–30 arası olmalı; dışındaysa `ValueError`
- `olcum` düz nitelik (dışarıdan güncellenir)
- `durum` **salt okunur** property: ölçüm hedeften 0.5'ten fazla düşükse `"ısıt"`, 0.5'ten fazla yüksekse `"soğut"`, değilse `"bekle"`
- `Termostat(hedef=21, olcum=20)`

```starter
class Termostat:
    def __init__(self, hedef=21, olcum=20):
        self.hedef = hedef
        self.olcum = olcum
```

```test
T = need("Termostat", "sınıf")
t = T()
eq(t.durum, "ısıt", "20 < 21-0.5 → ısıt")
t.olcum = 21.3
eq(t.durum, "bekle", "21.3 → bekle")
t.olcum = 22
eq(t.durum, "soğut", "22 → soğut")
t.hedef = 25
eq(t.durum, "ısıt", "hedef 25 → ısıt")
raises(ValueError, setattr, t, "hedef", 40, msg="40 → ValueError")
raises(ValueError, T, 2, 20, msg="kurucuda 2 → ValueError")
raises(AttributeError, setattr, t, "durum", "x", msg="durum salt okunur")
t.hedef = 21
t.olcum = 20.5
eq(t.durum, "bekle", "tam 0.5 düşük → bekle")
t.olcum = 21.5
eq(t.durum, "bekle", "tam 0.5 yüksek → bekle")
eq((T(5).hedef, T(30).hedef), (5, 30), "5 ve 30 sınırları geçerli")
```

```solution
class Termostat:
    def __init__(self, hedef=21, olcum=20):
        self.hedef = hedef
        self.olcum = olcum

    @property
    def hedef(self):
        return self._hedef

    @hedef.setter
    def hedef(self, deger):
        if not 5 <= deger <= 30:
            raise ValueError(f"hedef 5-30 arası olmalı: {deger}")
        self._hedef = deger

    @property
    def durum(self):
        if self.olcum < self.hedef - 0.5:
            return "ısıt"
        if self.olcum > self.hedef + 0.5:
            return "soğut"
        return "bekle"
```

```hint
`durum` için sadece getter yaz; setter yoksa atama `AttributeError` verir.
```
:::

::: gorev Hesaplanan boyut
`Dosya(ad, bayt)` sınıfında:

- `bayt` düz nitelik
- `kb` ve `mb` salt okunur property'ler: 1024 tabanında, 2 ondalığa yuvarlanmış
- `okunakli` property: 1024'ten küçükse `"N B"`, 1024² 'den küçükse `"X KB"`, değilse `"X MB"` (X 1 ondalıklı)

```starter
class Dosya:
    def __init__(self, ad, bayt):
        self.ad = ad
        self.bayt = bayt
```

```test
D = need("Dosya", "sınıf")
d = D("rapor.pdf", 1536)
eq(d.kb, 1.5, "1536 B → 1.5 KB")
eq(D("x", 5 * 1024 * 1024).mb, 5.0, "5 MB")
eq(D("x", 500).okunakli, "500 B", "500 B")
eq(d.okunakli, "1.5 KB", "1.5 KB")
eq(D("x", 3 * 1024 * 1024 + 300000).okunakli, "3.3 MB", "3.3 MB")
d.bayt = 2048
eq(d.kb, 2.0, "bayt değişince kb de değişir")
raises(AttributeError, setattr, d, "kb", 9, msg="kb salt okunur")
eq(D("x", 1023).okunakli, "1023 B", "1023 B")
eq(D("x", 1024).okunakli, "1.0 KB", "tam 1024 bayt → 1.0 KB")
eq(D("x", 1024 ** 2).okunakli, "1.0 MB", "tam 1 MB")
```

```solution
class Dosya:
    def __init__(self, ad, bayt):
        self.ad = ad
        self.bayt = bayt

    @property
    def kb(self):
        return round(self.bayt / 1024, 2)

    @property
    def mb(self):
        return round(self.bayt / 1024 ** 2, 2)

    @property
    def okunakli(self):
        if self.bayt < 1024:
            return f"{self.bayt} B"
        if self.bayt < 1024 ** 2:
            return f"{self.bayt / 1024:.1f} KB"
        return f"{self.bayt / 1024 ** 2:.1f} MB"
```

```hint
Hesaplanan alanları saklama, her okunuşta `self.bayt`'tan hesapla.
```
:::
