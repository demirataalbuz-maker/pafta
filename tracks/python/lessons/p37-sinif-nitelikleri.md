---
id: p37
title: Sınıf Nitelikleri ve Özel Metotlar
summary: Sınıfa ait veri, paylaşılan değiştirilebilir nitelik tuzağı, @classmethod ve @staticmethod.
kazanim: PCAP 4.2, PCPP1 1.5
---

::: anlat Sınıfın kendi verisi
`self.x` ile atanan nitelikler **nesneye** aittir. Sınıf gövdesinde doğrudan atanan isimler ise **sınıfa** aittir ve bütün örnekler tarafından paylaşılır:

```python
class Kural:
    toplam = 0                     #! sınıf niteliği: herkes için tek
    varsayilan_seviye = "orta"

    def __init__(self, ad):
        Kural.toplam += 1          #! sınıf niteliğini sınıf adıyla değiştir
        self.no = Kural.toplam     #! örnek niteliği
        self.ad = ad

a = Kural("ssh-bruteforce")
b = Kural("yeni-yonetici")
print(Kural.toplam, a.no, b.no)
print(a.varsayilan_seviye)         #! nesnede yok → sınıfta bulunur
b.varsayilan_seviye = "yuksek"     #! b'ye ÖZEL bir örnek niteliği oluşturur
print(a.varsayilan_seviye, b.varsayilan_seviye, Kural.varsayilan_seviye)
```

Okuma sırası: **önce nesne, sonra sınıf**. Ama `nesne.x = ...` ataması **her zaman nesneye** yazar ve sınıftakini gölgeler.

> [!TUZAK]
> Sınıf niteliği olarak **değiştirilebilir** bir nesne (liste, sözlük) koymak, P21'deki varsayılan argüman tuzağının sınıf versiyonudur:
>
> ```python norun
> class Kullanici:
>     roller = []              # TÜM kullanıcılar aynı listeyi paylaşır!
>     def rol_ekle(self, r):
>         self.roller.append(r)   # atama değil, değiştirme → sınıftaki listeye yazar
> ```
>
> Her nesneye ayrı liste için `__init__` içinde `self.roller = []` yaz.
:::

::: tahmin
Çıktı tek satır:

```python
class A:
    sayi = 0
    def __init__(self):
        A.sayi += 1

a, b = A(), A()
a.sayi = 99
print(A.sayi, a.sayi, b.sayi)
```

???

`2 99 2`. İki nesne oluştuğu için `A.sayi` 2'dir. `a.sayi = 99` sadece a'ya özel bir nitelik yaratır ve sınıftakini gölgeler. b'de böyle bir nitelik yok, bu yüzden sınıftakini okur.
:::

::: anlat @classmethod ve @staticmethod
Normal metot nesneyi (`self`) alır. İki özel tür daha var:

- **`@classmethod`**: ilk argüman olarak **sınıfı** (`cls`) alır. En yaygın kullanımı **alternatif kurucudur**: "şu biçimdeki metinden bir nesne üret".
- **`@staticmethod`**: ne nesneyi ne sınıfı alır. Sınıfla mantıksal olarak ilgili, ama durumuna ihtiyaç duymayan yardımcı fonksiyondur.

```python
class Hedef:
    def __init__(self, host, port):
        self.host, self.port = host, port

    @classmethod
    def metinden(cls, metin):                  #! cls = Hedef (ya da alt sınıfı)
        host, port = metin.rsplit(":", 1)
        return cls(host, int(port))            #! cls(...) ile yeni nesne

    @staticmethod
    def port_gecerli(p):                       #! self/cls yok
        return isinstance(p, int) and 0 < p < 65536

    def __repr__(self):
        return f"Hedef({self.host!r}, {self.port})"

h = Hedef.metinden("10.0.0.5:443")
print(h, Hedef.port_gecerli(443), Hedef.port_gecerli(70000))
```

Neden `Hedef(...)` değil de `cls(...)`? Çünkü bir alt sınıf `metinden`'i çağırdığında `cls` o alt sınıf olur ve doğru türde nesne üretilir. Standart kütüphanede bolca görürsün: `dict.fromkeys`, `datetime.fromisoformat`, `int.from_bytes`.

> [!DERİN]
> `@classmethod` ve `@staticmethod` sihir değil, **tanımlayıcı** (descriptor) adı verilen nesnelerdir. Bir metodu `nesne.metot` ile okuduğunda Python, fonksiyonun `__get__` metodunu çağırır ve fonksiyonu nesneye "bağlar" (bound method). classmethod ise sınıfa bağlar, staticmethod hiçbir şeye bağlamaz. Bu mekanizmayı P64'ta söküp yeniden yazacaksın.
:::

::: tahmin
Ne yazdırır?

```python
class Kullanici:
    roller = []
    def __init__(self, ad):
        self.ad = ad

u1, u2 = Kullanici("a"), Kullanici("b")
u1.roller.append("admin")
print(u2.roller)
```

???

`['admin']`. `u1.roller.append` bir atama değil, değiştirmedir. `u1`'de `roller` niteliği olmadığı için sınıftaki **tek** liste bulunur ve ona eklenir. u2 de aynı listeyi görür: tüm kullanıcılar admin oldu! Gerçek bir yetki sisteminde bu bir **yetki yükseltme** hatasıdır.
:::

::: gorev Kural numaralandırma
`Kural` sınıfı oluşturulan her kural için artan bir numara versin:

- sınıf niteliği `toplam`: şimdiye kadar oluşturulan kural sayısı
- her kuralın `no` niteliği: 1, 2, 3...
- `Kural(ad)` ile `ad` niteliği

```starter
class Kural:
    def __init__(self, ad):
        self.ad = ad
```

```test
K = need("Kural", "sınıf")
K.toplam = 0
a = K("x"); b = K("y"); c = K("z")
eq((a.no, b.no, c.no), (1, 2, 3), "numaralar 1, 2, 3")
eq(K.toplam, 3, "Kural.toplam = 3")
eq(c.ad, "z", "ad niteliği")
ok("toplam" not in a.__dict__, "toplam nesnede değil, sınıfta tutulmalı")
```

```solution
class Kural:
    toplam = 0

    def __init__(self, ad):
        Kural.toplam += 1
        self.no = Kural.toplam
        self.ad = ad
```

```hint
Sınıf gövdesinde `toplam = 0`; `__init__` içinde `Kural.toplam += 1` (self.toplam değil!).
```
:::

::: gorev Alternatif kurucu
`Hedef` sınıfını tamamla:

- `Hedef(host, port)`
- `@classmethod metinden(metin)`: `"host:port"` metninden nesne üretsin; port int olsun. IPv6 gibi birden fazla `:` içeren host'lar için **son** iki noktadan böl.
- `@staticmethod port_gecerli(p)`: p 1–65535 arası bir int ise `True`
- `metinden` geçersiz port gelirse `ValueError` yükseltsin

```starter
class Hedef:
    def __init__(self, host, port):
        self.host = host
        self.port = port
```

```test
H = need("Hedef", "sınıf")
h = H.metinden("10.0.0.5:443")
ok(isinstance(h, H), "metinden bir Hedef döndürmeli")
eq((h.host, h.port), ("10.0.0.5", 443), "10.0.0.5:443")
eq(H.metinden("::1:8080").host, "::1", "son ':' den böl")
eq(H.port_gecerli(22), True, "22 geçerli")
eq(H.port_gecerli(0), False, "0 geçersiz")
eq(H.port_gecerli("22"), False, "metin geçersiz")
raises(ValueError, H.metinden, "web:99999", msg="99999 → ValueError")
class Alt(H):
    pass
ok(type(Alt.metinden("a:1")) is Alt, "alt sınıftan çağrılınca alt sınıf nesnesi (cls kullan)")
```

```solution
class Hedef:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @classmethod
    def metinden(cls, metin):
        host, port = metin.rsplit(":", 1)
        port = int(port)
        if not cls.port_gecerli(port):
            raise ValueError(f"geçersiz port: {port}")
        return cls(host, port)

    @staticmethod
    def port_gecerli(p):
        return type(p) is int and 1 <= p <= 65535
```

```hint
`rsplit(":", 1)` sağdan bir kez böler. Nesneyi `cls(host, port)` ile üret.
```
:::

::: gorev Paylaşılan liste hatası
Bu kodda bir kullanıcıya rol eklemek **herkese** ekliyor. Her kullanıcının kendi rol listesi olacak şekilde düzelt.

```starter
class Kullanici:
    roller = []

    def __init__(self, ad):
        self.ad = ad

    def rol_ekle(self, rol):
        self.roller.append(rol)
```

```test
K = need("Kullanici", "sınıf")
a = K("ali"); b = K("veli")
a.rol_ekle("admin")
eq(a.roller, ["admin"], "ali'nin rolü admin")
eq(b.roller, [], "veli'nin rolü olmamalı")
ok("roller" in a.__dict__, "roller nesneye ait olmalı (__init__ içinde)")
```

```solution
class Kullanici:
    def __init__(self, ad):
        self.ad = ad
        self.roller = []

    def rol_ekle(self, rol):
        self.roller.append(rol)
```

```hint
Listeyi sınıf gövdesinden `__init__` içine taşı: `self.roller = []`.
```
:::
