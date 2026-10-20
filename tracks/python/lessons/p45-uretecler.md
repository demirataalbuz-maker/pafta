---
id: p45
title: Üreteçler · yield
summary: Durumunu hatırlayan fonksiyonlar, tembel değerlendirme, işlem hatları ve yield from.
---

::: anlat Duraklatılabilen fonksiyon
Gövdesinde `yield` geçen bir fonksiyon **üreteç fonksiyonudur**. Çağırdığında gövde çalışmaz; bunun yerine bir **üreteç nesnesi** (bir yineleyici) döner. Her `next()` çağrısında gövde bir sonraki `yield`'e kadar çalışır, değeri verir ve **orada donar**: yerel değişkenleriyle birlikte. Sonraki `next()` kaldığı yerden devam eder.

```python
def sayac(bas, son):
    print("  [başladı]")
    n = bas
    while n <= son:
        yield n                    #! değeri ver ve DURAKLA
        n += 1
    print("  [bitti]")

g = sayac(1, 3)                    #! henüz hiçbir şey çalışmadı
print(type(g).__name__)
print(next(g))
print(next(g))
for x in g:                        #! kalanını for tüketir
    print(x)
```

P44'deki `GeriSayim` sınıfının 15 satırı burada 5 satıra indi: `__iter__`, `__next__` ve `StopIteration` Python tarafından otomatik yazılır. Fonksiyon bitince (ya da `return` gelince) `StopIteration` kendiliğinden yükselir.

Röntgen ile mutlaka izle: `yield` satırında üretecin çerçevesi **kaybolur** ama yok olmaz. Sonraki `next()`'te aynı değişkenlerle geri gelir.

### Üreteç ifadeleri
P18'de gördüğün üreteç ifadesi `(x*x for x in ...)` aynı makinenin kısa yazımıdır. Fark **bellekte**:

```python
import sys
liste = [x * x for x in range(1_000_000)]      #! milyon eleman hemen bellekte
uretec = (x * x for x in range(1_000_000))     #! sadece "tarif" bellekte
print(sys.getsizeof(liste), "bayt")
print(sys.getsizeof(uretec), "bayt")
print(sum(uretec))                             #! elemanlar tek tek üretilip tüketilir
```

> [!NOT]
> **Tembel değerlendirme** sayesinde sonsuz diziler bile yazabilirsin: `while True: yield ...`. Sadece tüketen tarafın bir noktada durması gerekir (`islice`, `break`, `zip`).
:::

::: tahmin
Çıktıyı satır satır yaz:

```python
def f():
    print("başla")
    yield 1
    print("orta")
    yield 2

g = f()
print("oluştu")
print(next(g))
print(next(g))
```

???

```cikti
oluştu
başla
1
orta
2
```

`f()` çağrısı gövdeyi **çalıştırmaz**, bu yüzden "oluştu" önce gelir. İlk `next` ilk yield'e kadar ("başla", sonra 1), ikinci `next` ikinci yield'e kadar ("orta", sonra 2) çalıştırır.
:::

::: anlat İşlem hatları ve yield from
Üreteçler zincirlenerek Unix boru hattı (`cat | grep | cut`) gibi **işlem hatları** kurar. Her aşama bir sonrakine elemanı tek tek iletir; 50 GB'lık bir log bile sabit bellekle işlenir:

```python
def satirlar(metin):                       #! kaynak
    for s in metin.splitlines():
        yield s.strip()

def suz(satirlar, kelime):                 #! süzgeç
    for s in satirlar:
        if kelime in s:
            yield s

def alan(satirlar, i):                     #! dönüştürücü
    for s in satirlar:
        yield s.split()[i]

log = """08:00 OK 10.0.0.5
08:01 FAIL 203.0.113.9
08:02 FAIL 198.51.100.4
08:03 OK 10.0.0.8"""
hat = alan(suz(satirlar(log), "FAIL"), 2)  #! hiçbir şey çalışmadı, sadece hat kuruldu
print(list(hat))
```

**`yield from`** başka bir yinelenebilirin tüm elemanlarını sırayla verir; özyinelemeli üreteçlerin anahtarıdır:

```python
def agac_dolas(dugum, derinlik=0):
    yield "  " * derinlik + dugum["ad"]
    for cocuk in dugum.get("cocuklar", []):
        yield from agac_dolas(cocuk, derinlik + 1)   #! alt ağacın tamamını aktar

dizin = {"ad": "/", "cocuklar": [{"ad": "etc", "cocuklar": [{"ad": "ssh"}]}, {"ad": "var"}]}
print("\n".join(agac_dolas(dizin)))
```

> [!DERİN]
> Üreteçler iki yönlüdür: `deger = yield x` yazarsan dışarıdan `g.send(v)` ile üretecin **içine** değer gönderebilirsin. `g.throw(Hata)` içeride bir istisna yükseltir, `g.close()` ise içeride `GeneratorExit` yükseltip temizlik (`finally`) yaptırır. Bu "eşyordam" (coroutine) fikri, Python'un `async/await` sisteminin tarihsel atasıdır (P60). Bir üretecin durumu: `inspect.getgeneratorstate(g)` → GEN_CREATED, GEN_SUSPENDED, GEN_CLOSED.
:::

::: tahmin
Çıktı tek satır:

```python
def ic():
    yield 1
    yield 2

def dis():
    yield 0
    yield from ic()
    yield 3

print(list(dis()), sum(x * x for x in range(4)))
```

???

`[0, 1, 2, 3] 14`. `yield from ic()` iç üretecin bütün elemanlarını sırayla aktarır. 0+1+4+9 = 14.
:::

::: gorev Sonsuz Fibonacci
`fib_uret()` adında **sonsuz** bir üreteç yaz: 0, 1, 1, 2, 3, 5, ... sonsuza kadar versin.

```starter
def fib_uret():
    pass
```

```test
import inspect
from itertools import islice
need("fib_uret")
ok(inspect.isgeneratorfunction(fib_uret), "fib_uret bir üreteç fonksiyonu olmalı (yield)")
eq(list(islice(fib_uret(), 10)), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34], "ilk 10 eleman")
g = fib_uret()
for _ in range(100):
    son = next(g)
eq(son, 218922995834555169026, "100. eleman (sonsuz olmalı)")
```

```solution
def fib_uret():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

```hint
`while True:` içinde `yield a` ve `a, b = b, a + b`.
```
:::

::: gorev Log işlem hattı
Üç üreteç fonksiyonu yaz ve zincirle:

- `satirlar(yol)`: dosyayı satır satır okuyup **kenar boşlukları temizlenmiş** ve **boş olmayan** satırları versin
- `hatalar(satirlar)`: içinde `ERROR` geçen satırları versin
- `ipler(satirlar)`: her satırın **ilk alanını** versin

Sonra `list(ipler(hatalar(satirlar("app.log"))))` sonucunu yazdır.

```setup
with open("app.log", "w", encoding="utf-8") as f:
    f.write("""10.0.0.5 INFO istek tamam
203.0.113.9 ERROR kimlik doğrulama başarısız

198.51.100.4 ERROR çok fazla istek
10.0.0.8 WARN yavaş yanıt
   192.0.2.1 ERROR geçersiz belirteç
""")
```

```starter
def satirlar(yol):
    pass

def hatalar(satirlar):
    pass

def ipler(satirlar):
    pass

print(list(ipler(hatalar(satirlar("app.log")))))
```

```test
import inspect
for ad in ("satirlar", "hatalar", "ipler"):
    ok(inspect.isgeneratorfunction(kullanici.get(ad)), f"{ad} bir üreteç fonksiyonu olmalı")
eq(out.strip(), "['203.0.113.9', '198.51.100.4', '192.0.2.1']", "hata veren IP'ler")
eq(list(hatalar(iter(["a ERROR", "b OK"]))), ["a ERROR"], "hatalar herhangi bir yinelenebilirle çalışmalı")
```

```solution
def satirlar(yol):
    with open(yol, encoding="utf-8") as f:
        for s in f:
            s = s.strip()
            if s:
                yield s

def hatalar(satirlar):
    for s in satirlar:
        if "ERROR" in s:
            yield s

def ipler(satirlar):
    for s in satirlar:
        yield s.split()[0]

print(list(ipler(hatalar(satirlar("app.log")))))
```

```hint
Her fonksiyon bir `for` döngüsü ve koşula göre `yield`. `satirlar` içinde dosyayı `with` ile aç; üreteç tükenince dosya kapanır.
```
:::

::: gorev Özyinelemeli düzleştirici
P24'teki `duzlestir`'i bu kez **üreteç** olarak yaz: istediğin derinlikte iç içe listelerin (ve demetlerin) elemanlarını sırayla versin. `yield from` kullan.

```starter
def duzlestir(veri):
    pass
```

```test
import inspect
need("duzlestir")
ok(inspect.isgeneratorfunction(duzlestir), "üreteç fonksiyonu olmalı")
eq(list(duzlestir([1, [2, (3, 4)], [[5]], []])), [1, 2, 3, 4, 5], "liste ve demetler")
eq(list(duzlestir(["ab", ["cd"]])), ["ab", "cd"], "metinler parçalanmamalı")
eq(list(duzlestir([])), [], "boş")
ok(uses("yieldfrom"), "yield from kullan")
```

```solution
def duzlestir(veri):
    for oge in veri:
        if isinstance(oge, (list, tuple)):
            yield from duzlestir(oge)
        else:
            yield oge
```

```hint
Liste ya da demet ise `yield from duzlestir(oge)`, değilse `yield oge`. Metinleri liste sanma: sadece `(list, tuple)` kontrol et.
```
:::
