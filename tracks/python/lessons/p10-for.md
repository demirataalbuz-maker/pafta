---
id: p10
title: for ve range
summary: Bir dizinin her elemanı için; range, enumerate ve biriktirici kalıbı.
---

::: anlat Her eleman için
`for`, bir dizinin (metin, liste, aralık...) elemanlarını **sırayla** bir isme bağlar ve her biri için bloğu çalıştırır:

```python
for harf in "SSH":           #! harf sırayla 'S', 'S', 'H' olur
    print(harf)

for port in [22, 80, 443]:   #! listeler de dolaşılır
    print("port", port)
```

`while`'daki gibi sayaç yönetmek, ilerlemeyi unutmak yok: `for` dizinin sonuna gelince kendiliğinden durur.

### range: sayı aralığı
`range` sayı dizisi üretir ve dur değeri **hariçtir** (dilimlerdeki gibi):

```python
print(list(range(5)))          #! [0, 1, 2, 3, 4] — 0'dan başlar, 5 hariç
print(list(range(2, 6)))       #! [2, 3, 4, 5]
print(list(range(0, 20, 5)))   #! [0, 5, 10, 15] — adım 5
print(list(range(5, 0, -1)))   #! [5, 4, 3, 2, 1] — geri sayım
for i in range(3):
    print("deneme", i + 1)
```

> [!DERİN]
> `range(10**12)` bellekte bir trilyon sayılık liste **oluşturmaz**. `range` tembel (lazy) bir nesnedir: sadece başlangıç, bitiş ve adımı saklar, sayıları istendikçe hesaplar. `len(range(10**12))` anında cevap verir, `10**11 in range(10**12)` bile matematikle hesaplanır, dolaşmaz. Bu tembellik fikri P43'te (üreteçler) Python'un süper gücüne dönüşecek.
:::

::: tahmin
Çıktı tek satır:

```python
for i in range(2, 11, 3):
    print(i, end=",")
```

???

`2,5,8,`. 2'den başla, 3'er atla: 2, 5, 8. Sıradaki 11 olurdu ama bitiş değeri hariç olduğu için durur.
:::

::: anlat Biriktirici, sayaç ve enumerate
Döngülerle yazılan programların çoğu üç kalıptan birine uyar:

```python
# 1) BİRİKTİRİCİ: döngüden önce başlat, her turda ekle
toplam = 0
for n in [4, 8, 15, 16, 23, 42]:
    toplam += n
print("toplam:", toplam)

# 2) SAYAÇ: koşulu sağlayanları say
basarisiz = 0
for durum in ["OK", "FAIL", "OK", "FAIL", "FAIL"]:
    if durum == "FAIL":
        basarisiz += 1
print("başarısız:", basarisiz)

# 3) EN BÜYÜK/EN KÜÇÜK: ilk elemanla başla, daha iyisini bul
en_buyuk = None
for n in [3, 17, 9]:
    if en_buyuk is None or n > en_buyuk:
        en_buyuk = n
print("en büyük:", en_buyuk)
```

Hem elemanı hem sırasını istiyorsan `range(len(...))` yerine **`enumerate`** kullan. Python'cası budur:

```python
hedefler = ["web01", "db01", "dc01"]
for i, ad in enumerate(hedefler, 1):   #! 1'den başlayarak numarala
    print(f"{i}. {ad}")
```

> [!NOT]
> Bu kalıpların hazırları da var: `sum(liste)`, `max(liste)`, `liste.count(x)`. Ama nasıl çalıştıklarını bilmeden kullanmak, bir gün onlara uymayan bir problemle karşılaşınca elini kolunu bağlar. Görevlerde önce elle yazacaksın.
:::

::: tahmin
Ne yazdırır?

```python
toplam = 0
for c in "a1b22c3":
    if c.isdigit():
        toplam += int(c)
print(toplam)
```

???

`8`. Metin karakter karakter dolaşılır, rakam olanlar (1, 2, 2, 3) toplanır. "22" tek bir sayı değil, iki ayrı `2` karakteridir.
:::

::: gorev Çarpım tablosu
Girdiden bir n sayısı oku ve 1'den 5'e kadar çarpımlarını şu biçimde yazdır:

```cikti
7 x 1 = 7
7 x 2 = 14
7 x 3 = 21
7 x 4 = 28
7 x 5 = 35
```

```starter
n = int(input())

```

```stdin
7
```

```test
eq(run("7").strip().splitlines(), [f"7 x {i} = {7*i}" for i in range(1, 6)], "7 için 5 satır")
eq(run("12").strip().splitlines(), [f"12 x {i} = {12*i}" for i in range(1, 6)], "12 için 5 satır")
ok(uses("for"), "for ve range kullan")
```

```solution
n = int(input())
for i in range(1, 6):
    print(f"{n} x {i} = {n * i}")
```

```hint
`range(1, 6)` → 1, 2, 3, 4, 5
```
:::

::: gorev Sesli harf sayacı
Girdiden **küçük harfli** bir metin oku ve içindeki sesli harfleri say. Türkçe sesliler: `aeıioöuü`.

```starter
metin = input()
sesliler = "aeıioöuü"

```

```stdin
merhaba dünya
```

```test
eq(run("merhaba dünya").strip(), "5", "merhaba dünya → 5")
eq(run("python").strip(), "1", "python → 1")
eq(run("xyz").strip(), "0", "xyz → 0")
eq(run("ığdır").strip(), "2", "ığdır → 2")
ok(uses("for"), "for döngüsüyle say")
```

```solution
metin = input()
sesliler = "aeıioöuü"
sayi = 0
for harf in metin:
    if harf in sesliler:
        sayi += 1
print(sayi)
```

```hint
Sayaç kalıbı: döngüden önce `sayi = 0`; her harf için `if harf in sesliler:`.
```
:::

::: gorev Asal mı?
Girdiden bir tam sayı oku. Asalsa `True`, değilse `False` yazdır. 1 asal değildir. Verimli ol: bir sayının bölenini aramak için **kareköküne kadar** bakmak yeter.

```starter
n = int(input())

```

```stdin
97
```

```test
eq(run("2").strip(), "True", "2 → True")
eq(run("1").strip(), "False", "1 → False")
eq(run("97").strip(), "True", "97 → True")
eq(run("91").strip(), "False", "91 → False (7 × 13)")
eq(run("7919").strip(), "True", "7919 → True")
eq(run("1000000007").strip(), "True", "1000000007 → True (karekök sınırıyla hızlı olmalı)")
```

```solution
n = int(input())
asal = n >= 2
for i in range(2, int(n ** 0.5) + 1):
    if n % i == 0:
        asal = False
        break
print(asal)
```

```hint
Bir bayrakla başla: `asal = n >= 2`. Bölen bulursan `asal = False` ve `break`.
```

```hint
Karekök: `int(n ** 0.5)`. `range`'in sonu hariç olduğu için `+ 1` ekle.
```
:::
