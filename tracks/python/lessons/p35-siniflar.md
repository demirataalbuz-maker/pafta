---
id: p35
title: Sınıf ve Nesne
summary: class bir kalıptır, nesne onun örneği; __init__, self, nitelikler ve metotlar.
---

::: anlat Kalıp ve örnekler
Şimdiye kadar veriyi (sözlük, liste) ve davranışı (fonksiyon) ayrı tuttun. **Sınıf** ikisini bir araya getirir: bir nesnenin hangi **verileri** taşıdığını ve hangi **işleri** yapabildiğini tanımlayan bir kalıptır. O kalıptan üretilen her nesneye **örnek** (instance) denir.

```python
class Hedef:                               #! sınıf adı: BuyukHarfleBaslayan (PascalCase)
    def __init__(self, host, port=22):     #! kurucu: yeni nesne oluşurken çalışır
        self.host = host                   #! self.x = nitelik (nesnenin verisi)
        self.port = port
        self.notlar = []

    def adres(self):                       #! metot: nesneye bağlı fonksiyon
        return f"{self.host}:{self.port}"

    def not_ekle(self, metin):
        self.notlar.append(metin)

web = Hedef("web01", 443)                  #! örnek oluştur: __init__ çağrılır
db = Hedef("db01", 5432)
web.not_ekle("TLS 1.0 açık")
print(web.adres(), db.adres())
print(web.notlar, db.notlar)               #! her nesnenin kendi verisi var
```

Her nesne **kendi niteliklerini** taşır: `web.notlar` ile `db.notlar` ayrı listelerdir. Metotlar ise sınıfta bir kez tanımlanır ve bütün örnekler paylaşır.

### self nedir?
`self`, metodun **hangi nesne için** çağrıldığıdır. `web.adres()` yazdığında Python aslında `Hedef.adres(web)` çağırır: nesne ilk argüman olarak gizlice geçer. `self` bir anahtar kelime değil, sadece gelenek; ama herkes bu adı kullanır.

```python
class Sayac:
    def __init__(self):
        self.n = 0
    def artir(self):
        self.n += 1
        return self.n

s = Sayac()
print(s.artir(), Sayac.artir(s))           #! ikisi aynı şey
```

Röntgen'de bir metot çağrısını izle: yeni çerçevede `self` adlı bir yerel değişken görürsün ve rengi dışarıdaki nesneyle **aynıdır**.
:::

::: tahmin
Çıktı tek satır:

```python
class Sayac:
    def __init__(self):
        self.n = 0
    def artir(self):
        self.n += 1
        return self.n

a = Sayac()
b = Sayac()
a.artir()
a.artir()
print(a.n, b.n, b.artir())
```

???

`2 0 1`. `a` ve `b` ayrı nesnelerdir ve her birinin kendi `n`'i vardır. print'in argümanları soldan sağa hesaplanır: `a.n` 2, `b.n` henüz 0, ardından `b.artir()` b'yi 1 yapar ve 1 döndürür.
:::

::: anlat Nesnenin içi: __dict__
Bir nesnenin nitelikleri aslında bir sözlükte durur: `nesne.__dict__`. Nitelik atamak o sözlüğe yazmaktır; Python sınıfta tanımlanmamış nitelikleri bile sonradan eklemene izin verir:

```python
class Kutu:
    def __init__(self, x):
        self.x = x

k = Kutu(5)
k.y = 10                                   #! sonradan nitelik eklemek serbest
print(k.__dict__)
print(isinstance(k, Kutu), type(k).__name__)
print(hasattr(k, "z"), getattr(k, "z", "yok"))   #! nitelik var mı / varsayılanla oku
setattr(k, "z", 3)                          #! adı metin olan nitelik ata
print(vars(k))                              #! vars(k) == k.__dict__
```

Nitelik okurken Python önce **nesnenin** `__dict__`'ine, bulamazsa **sınıfına** bakar. Metotlar bu yüzden bulunur: nesnede değil sınıfta dururlar. Bu arama zincirini P36'da ve P59'da derinleştireceğiz.

> [!NOT]
> Ne zaman sınıf yazmalı? Bir grup veri ve o veri üzerinde çalışan fonksiyonlar birlikte dolaşıyorsa, yani "şu sözlüğü alıp şu dört fonksiyona sırayla veriyorum" diyorsan sınıf zamanıdır. Sadece tek bir fonksiyonu olan bir sınıf genelde fonksiyon olmalıdır.

> [!DERİN]
> `class` ifadesi de çalıştırılabilir bir koddur: Python sınıf gövdesini bir isim alanında çalıştırır, sonra `type(isim, tabanlar, isim_alanı)` çağırarak bir **sınıf nesnesi** üretir. Yani sınıfın kendisi de bir nesnedir ve türü `type`'tır. Bunu P58'de açacağız.
:::

::: tahmin
Çıktı tek satır:

```python
class Kutu:
    def __init__(self, x):
        self.x = x

k = Kutu(5)
k.y = 10
print(k.__dict__, hasattr(k, "artir"))
```

???

`{'x': 5, 'y': 10} False`. `__init__` içinde atanan `x` ve sonradan eklenen `y` nesnenin sözlüğündedir. Kutu sınıfında `artir` diye bir şey yok.
:::

::: gorev Banka hesabı
`Hesap` sınıfını yaz:

- `Hesap(sahip, bakiye=0)`: `sahip` ve `bakiye` niteliklerini tutsun
- `yatir(miktar)`: miktar 0 ya da negatifse `ValueError`; değilse bakiyeye ekle ve yeni bakiyeyi döndür
- `cek(miktar)`: miktar 0 ya da negatifse ya da bakiyeden fazlaysa `ValueError`; değilse düş ve yeni bakiyeyi döndür

```starter
class Hesap:
    pass
```

```test
H = need("Hesap", "sınıf")
h = H("ayse")
eq(h.sahip, "ayse", "sahip niteliği")
eq(h.bakiye, 0, "varsayılan bakiye 0")
eq(h.yatir(100), 100, "yatir(100) → 100")
eq(h.cek(30), 70, "cek(30) → 70")
eq(h.bakiye, 70, "bakiye 70")
raises(ValueError, h.cek, 500, msg="bakiyeden fazla çekmek → ValueError")
raises(ValueError, h.yatir, -5, msg="negatif yatırma → ValueError")
raises(ValueError, h.cek, 0, msg="0 çekmek → ValueError")
h2 = H("ali", 50)
eq((h2.bakiye, h.bakiye), (50, 70), "hesaplar bağımsız")
```

```solution
class Hesap:
    def __init__(self, sahip, bakiye=0):
        self.sahip = sahip
        self.bakiye = bakiye

    def yatir(self, miktar):
        if miktar <= 0:
            raise ValueError("miktar pozitif olmalı")
        self.bakiye += miktar
        return self.bakiye

    def cek(self, miktar):
        if miktar <= 0 or miktar > self.bakiye:
            raise ValueError("geçersiz miktar")
        self.bakiye -= miktar
        return self.bakiye
```

```hint
Her metodun ilk parametresi `self`. Niteliklere `self.bakiye` diye eriş.
```
:::

::: gorev Dikdörtgen
`Dikdortgen(en, boy)` sınıfı `alan()`, `cevre()` ve `kare_mi()` metotlarını sunsun. `olcekle(k)` metodu en ve boyu k ile çarpıp **nesnenin kendisini** (`self`) döndürsün, böylece zincirleme çağrı yapılabilsin.

```starter
class Dikdortgen:
    pass
```

```test
D = need("Dikdortgen", "sınıf")
d = D(3, 4)
eq(d.alan(), 12, "alan 12")
eq(d.cevre(), 14, "çevre 14")
eq(d.kare_mi(), False, "3×4 kare değil")
eq(D(5, 5).kare_mi(), True, "5×5 kare")
ok(d.olcekle(2) is d, "olcekle self döndürmeli")
eq((d.en, d.boy), (6, 8), "ölçeklendikten sonra 6×8")
eq(D(1, 2).olcekle(3).alan(), 18, "zincirleme: D(1,2).olcekle(3).alan() → 18")
```

```solution
class Dikdortgen:
    def __init__(self, en, boy):
        self.en = en
        self.boy = boy

    def alan(self):
        return self.en * self.boy

    def cevre(self):
        return 2 * (self.en + self.boy)

    def kare_mi(self):
        return self.en == self.boy

    def olcekle(self, k):
        self.en *= k
        self.boy *= k
        return self
```

```hint
Zincirleme için metodun son satırı `return self`.
```
:::

::: gorev Giriş defteri
`GirisDefteri` sınıfı kullanıcıların giriş denemelerini tutsun:

- `ekle(kullanici, basarili)`: bir deneme kaydet
- `basarisiz(kullanici)`: o kullanıcının **art arda** son başarısız deneme sayısını döndür; başarılı bir giriş sayacı sıfırlar
- `kilitli_mi(kullanici, esik=3)`: art arda başarısız sayısı eşiğe ulaştıysa `True`

```starter
class GirisDefteri:
    pass
```

```test
G = need("GirisDefteri", "sınıf")
d = G()
for b in [False, False]:
    d.ekle("root", b)
eq(d.basarisiz("root"), 2, "root 2 başarısız")
eq(d.kilitli_mi("root"), False, "2 < 3 → kilitli değil")
d.ekle("root", False)
eq(d.kilitli_mi("root"), True, "3 başarısız → kilitli")
d.ekle("ali", False)
d.ekle("ali", True)
eq(d.basarisiz("ali"), 0, "başarılı giriş sayacı sıfırlar")
eq(d.basarisiz("bilinmeyen"), 0, "hiç denemesi olmayan → 0")
eq(G().basarisiz("root"), 0, "her defter bağımsız")
eq(d.kilitli_mi("root", esik=5), False, "eşik 5 → kilitli değil")
```

```solution
class GirisDefteri:
    def __init__(self):
        self.ardisik = {}

    def ekle(self, kullanici, basarili):
        if basarili:
            self.ardisik[kullanici] = 0
        else:
            self.ardisik[kullanici] = self.ardisik.get(kullanici, 0) + 1

    def basarisiz(self, kullanici):
        return self.ardisik.get(kullanici, 0)

    def kilitli_mi(self, kullanici, esik=3):
        return self.basarisiz(kullanici) >= esik
```

```hint
`__init__`'te bir sözlük aç: kullanıcı → art arda başarısız sayısı. Başarılı girişte 0'a çek.
```

```hint
Dikkat: sözlüğü sınıf gövdesinde değil `__init__` içinde oluştur, yoksa bütün defterler aynı sözlüğü paylaşır (P36'da bu tuzağı göreceksin).
```
:::
