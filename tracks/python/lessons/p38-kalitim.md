---
id: p38
title: Kalıtım ve MRO
summary: Alt sınıflar, override, super(), çok biçimlilik, çoklu kalıtım ve C3 metot çözüm sırası.
---

::: anlat Bir sınıftan türetmek
**Kalıtım**, mevcut bir sınıfın davranışlarını alıp üzerine ekleme yapan ya da bazılarını değiştiren yeni bir sınıf yazmaktır:

```python
class Bildirim:
    def __init__(self, alici):
        self.alici = alici

    def bicimle(self, mesaj):
        return mesaj

    def gonder(self, mesaj):                           #! ortak akış tabanda
        return f"→ {self.alici}: {self.bicimle(mesaj)}"

class Eposta(Bildirim):                                #! Eposta, Bildirim'den türer
    def bicimle(self, mesaj):                          #! override: davranışı değiştir
        return f"[Konu: Uyarı] {mesaj}"

class Sms(Bildirim):
    def bicimle(self, mesaj):
        return mesaj[:20]                              #! SMS kısa olmalı

for kanal in [Eposta("soc@ornek.com"), Sms("+90555"), Bildirim("log")]:
    print(kanal.gonder("Şüpheli giriş tespit edildi"))
```

`gonder` sadece tabanda yazıldı ama her alt sınıf kendi `bicimle`'sini kullandı: `self.bicimle(...)` çağrısı nesnenin **gerçek türünde** aranır. Aynı çağrının nesneye göre farklı davranmasına **çok biçimlilik** (polymorphism) denir.

```python norun
print(isinstance(Eposta("x"), Bildirim))   #! alt sınıf nesnesi tabanın da örneğidir
print(issubclass(Sms, Bildirim), Sms.__bases__)
```

### super(): tabanın sürümünü çağır
Override ederken tabanın işini **tamamen silmek** değil, **üstüne eklemek** istersen `super()` kullanırsın:

```python
class Calisan:
    def __init__(self, ad, maas):
        self.ad, self.maas = ad, maas
    def bilgi(self):
        return f"{self.ad} ({self.maas} TL)"

class Yonetici(Calisan):
    def __init__(self, ad, maas, ekip):
        super().__init__(ad, maas)             #! tabanın kurucusunu çalıştır
        self.ekip = ekip
    def bilgi(self):
        return super().bilgi() + f", ekip: {len(self.ekip)} kişi"

print(Yonetici("Ayşe", 90000, ["ali", "veli"]).bilgi())
```

> [!TUZAK]
> Alt sınıfta `__init__` yazıp `super().__init__(...)` çağırmayı unutursan tabanın kurduğu nitelikler **hiç oluşmaz**. İlk kullanımda `AttributeError` alırsın.
:::

::: tahmin
Çıktı tek satır:

```python
class Hayvan:
    def ses(self):
        return "..."
    def tanit(self):
        return f"Ben {self.ses()}"

class Kedi(Hayvan):
    def ses(self):
        return "miyav"

print(Kedi().tanit(), Hayvan().tanit())
```

???

`Ben miyav Ben ...`. `tanit` tabanda tanımlı ama içindeki `self.ses()` nesnenin gerçek türünde aranır. Kedi için `miyav` bulunur.
:::

::: anlat Çoklu kalıtım, MRO ve mixin
Python'da bir sınıf **birden fazla** tabandan türeyebilir. O zaman şu soru doğar: bir metot birden çok tabanda varsa hangisi çalışır? Cevap **MRO**'dur (Method Resolution Order, metot çözüm sırası). Python bunu **C3 doğrusallaştırma** algoritmasıyla hesaplar:

```python
class A:
    def kim(self): return "A"
class B(A):
    def kim(self): return "B>" + super().kim()
class C(A):
    def kim(self): return "C>" + super().kim()
class D(B, C):                                 #! elmas: D → B, C → A
    def kim(self): return "D>" + super().kim()

print(D().kim())
print([k.__name__ for k in D.__mro__])
```

`super()` "tabanım" demek **değildir**: "MRO'da benden **sonraki** sınıf" demektir. B'deki `super()` D nesnesi için çağrılınca A'ya değil C'ye gider. Bu tasarım sayesinde elmas yapıda her sınıf **tam bir kez** çağrılır.

### Mixin: davranış paketleri
Çoklu kalıtımın en temiz kullanımı **mixin**'dir: tek başına anlamı olmayan, başka sınıflara yetenek ekleyen küçük sınıflar.

```python
import json

class JsonMixin:
    def json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

class ZamanDamgaliMixin:
    def damgala(self, t):
        self.zaman = t
        return self

class Olay(JsonMixin, ZamanDamgaliMixin):
    def __init__(self, tur, kullanici):
        self.tur, self.kullanici = tur, kullanici

print(Olay("giris", "ali").damgala("08:00").json())
```

> [!ZEN]
> Kalıtım güçlüdür ama bağımlılık yaratır: taban değişince bütün alt sınıflar etkilenir. "Bu nesne **bir** X midir?" (is-a) sorusuna evet diyemiyorsan kalıtım değil **bileşim** (composition) kullan: nesneyi başka bir nesnenin niteliği yap (`self.bildirim = Eposta(...)`).
:::

::: tahmin
Çıktı tek satır:

```python
class A:
    def kim(self): return "A"
class B(A):
    def kim(self): return "B" + super().kim()
class C(A):
    def kim(self): return "C" + super().kim()
class D(B, C):
    def kim(self): return "D" + super().kim()

print(D().kim(), [k.__name__ for k in D.__mro__])
```

???

`DBCA ['D', 'B', 'C', 'A', 'object']`. MRO zinciri D → B → C → A'dır. Her `super()` zincirdeki bir sonrakine gider: B'nin `super()`'i A'ya değil C'ye gider. Her sınıfın en sonunda `object` vardır.
:::

::: gorev Bildirim kanalları
`Kanal` taban sınıfı ve iki alt sınıf yaz:

- `Kanal(alici)` ve `gonder(mesaj)` → `"<alici>: <bicimle(mesaj)>"`; tabanın `bicimle`'si mesajı olduğu gibi döndürsün
- `Eposta(Kanal)`: `bicimle` → `"[UYARI] " + mesaj`
- `Sms(Kanal)`: `bicimle` → mesajın **ilk 10 karakteri**
- Fonksiyon `hepsine(kanallar, mesaj)` → her kanalın `gonder` sonucunun listesi

```starter
class Kanal:
    pass
```

```test
K = need("Kanal", "sınıf"); E = need("Eposta", "sınıf"); S = need("Sms", "sınıf"); need("hepsine")
ok(issubclass(E, K) and issubclass(S, K), "Eposta ve Sms, Kanal'dan türemeli")
eq(K("log").gonder("selam"), "log: selam", "taban kanal")
eq(E("soc").gonder("disk dolu"), "soc: [UYARI] disk dolu", "eposta biçimi")
eq(S("555").gonder("Şüpheli giriş tespit edildi"), "555: Şüpheli gi", "sms ilk 10 karakter")
eq(hepsine([E("a"), S("b")], "0123456789XYZ"), ["a: [UYARI] 0123456789XYZ", "b: 0123456789"], "hepsine")
ok("gonder" not in E.__dict__ and "gonder" not in S.__dict__, "gonder sadece tabanda olmalı (alt sınıflar bicimle'yi override etsin)")
```

```solution
class Kanal:
    def __init__(self, alici):
        self.alici = alici

    def bicimle(self, mesaj):
        return mesaj

    def gonder(self, mesaj):
        return f"{self.alici}: {self.bicimle(mesaj)}"


class Eposta(Kanal):
    def bicimle(self, mesaj):
        return "[UYARI] " + mesaj


class Sms(Kanal):
    def bicimle(self, mesaj):
        return mesaj[:10]


def hepsine(kanallar, mesaj):
    return [k.gonder(mesaj) for k in kanallar]
```

```hint
Ortak akış (`gonder`) tabanda, değişen kısım (`bicimle`) alt sınıflarda.
```
:::

::: gorev super() ile kurucu
`Cihaz(ad, ip)` sınıfı `ad` ve `ip` niteliklerini tutsun ve `etiket()` → `"ad (ip)"` döndürsün. `Sunucu(Cihaz)` ek olarak `servisler` listesi alsın; `etiket()` tabanın etiketine `" [ssh, http]"` gibi servisleri eklesin. Alt sınıf **mutlaka `super()`** kullansın.

```starter
class Cihaz:
    pass

class Sunucu(Cihaz):
    pass
```

```test
C = need("Cihaz", "sınıf"); S = need("Sunucu", "sınıf")
eq(C("yazici", "10.0.0.50").etiket(), "yazici (10.0.0.50)", "Cihaz etiketi")
s = S("web01", "10.0.0.5", ["ssh", "http"])
eq((s.ad, s.ip, s.servisler), ("web01", "10.0.0.5", ["ssh", "http"]), "Sunucu nitelikleri")
eq(s.etiket(), "web01 (10.0.0.5) [ssh, http]", "Sunucu etiketi")
eq(S("bos", "1.1.1.1", []).etiket(), "bos (1.1.1.1) []", "servis yoksa []")
ok(src.count("super()") >= 2, "hem __init__ hem etiket içinde super() kullan")
```

```solution
class Cihaz:
    def __init__(self, ad, ip):
        self.ad = ad
        self.ip = ip

    def etiket(self):
        return f"{self.ad} ({self.ip})"


class Sunucu(Cihaz):
    def __init__(self, ad, ip, servisler):
        super().__init__(ad, ip)
        self.servisler = servisler

    def etiket(self):
        return super().etiket() + f" [{', '.join(self.servisler)}]"
```

```hint
`super().__init__(ad, ip)` ve `super().etiket() + ...`
```
:::

::: gorev Sözlüğe çevirme mixin'i
`SozlukMixin` adında bir mixin yaz: `sozluk()` metodu nesnenin niteliklerinden, adı `_` ile **başlamayanları** içeren yeni bir sözlük döndürsün. Sonra `Bulgu(baslik, seviye)` sınıfını bu mixin'i kullanarak tanımla; içinde `_gizli_not` adlı bir nitelik de olsun (sözlükte görünmemeli).

```starter
class SozlukMixin:
    pass

class Bulgu:
    def __init__(self, baslik, seviye):
        self.baslik = baslik
        self.seviye = seviye
        self._gizli_not = "dahili"
```

```test
M = need("SozlukMixin", "sınıf"); B = need("Bulgu", "sınıf")
ok(issubclass(B, M), "Bulgu, SozlukMixin'den türemeli")
b = B("Varsayılan parola", "yuksek")
eq(b.sozluk(), {"baslik": "Varsayılan parola", "seviye": "yuksek"}, "_ ile başlayanlar hariç")
d = b.sozluk(); d["baslik"] = "x"
eq(b.baslik, "Varsayılan parola", "döndürülen sözlük yeni olmalı (nesneyi değiştirmemeli)")
class Baska(M):
    def __init__(self):
        self.a = 1
eq(Baska().sozluk(), {"a": 1}, "mixin başka sınıflarda da çalışmalı")
```

```solution
class SozlukMixin:
    def sozluk(self):
        return {k: v for k, v in vars(self).items() if not k.startswith("_")}


class Bulgu(SozlukMixin):
    def __init__(self, baslik, seviye):
        self.baslik = baslik
        self.seviye = seviye
        self._gizli_not = "dahili"
```

```hint
`vars(self)` nesnenin `__dict__`'idir. Bir sözlük üreteciyle süz.
```
:::
