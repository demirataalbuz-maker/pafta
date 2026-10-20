---
id: p33
title: itertools ve functools
summary: Kombinatorik, tembel zincirler, groupby, accumulate; reduce, partial ve lru_cache.
---

::: anlat itertools: yineleyici cebiri
`itertools`, yineleyicilerle çalışan hızlı (C ile yazılmış) yapı taşları sunar. Hepsi **tembeldir**: sonucu tek tek, istendikçe üretir.

### Kombinatorik
```python
from itertools import product, permutations, combinations

print(list(product("01", repeat=3)))        #! kartezyen çarpım: tüm 3 bitlik diziler
print(list(permutations("abc", 2)))         #! sıralı seçim (ab ≠ ba)
print(list(combinations([22, 80, 443], 2))) #! sırasız seçim (her çift bir kez)
```

| Fonksiyon | n elemandan k'lı | Sayı |
|---|---|---|
| `product(..., repeat=k)` | tekrarlı, sıralı | nᵏ |
| `permutations(..., k)` | tekrarsız, sıralı | n! / (n-k)! |
| `combinations(..., k)` | tekrarsız, sırasız | n! / (k!(n-k)!) |

> [!GÜVENLİK]
> `product` tablosundaki **nᵏ**, parola uzunluğunun neden bu kadar önemli olduğunu gösterir. 26 küçük harften 8 karakter 26⁸ ≈ 2×10¹¹ olasılık eder; 95 yazılabilir karakterden 14 karakter ise 95¹⁴ ≈ 5×10²⁷. Uzunluk **üstte** durur, karakter çeşitliliği tabanda. Bu yüzden uzun parola cümleleri, kısa ama karmaşık parolalardan daha güçlüdür.

### Zincirleme ve dilimleme
```python
from itertools import chain, islice, count, cycle

print(list(chain([1, 2], (3, 4), "ab")))     #! dizileri uç uca ekle
sayac = count(1000, 5)                       #! sonsuz: 1000, 1005, ...
print(list(islice(sayac, 4)))                #! sonsuzdan ilk 4 (dilim gibi ama tembel)
renk = cycle(["kırmızı", "mavi"])
print([next(renk) for _ in range(5)])
```

`count` ve `cycle` **sonsuzdur**; `list(count())` programını kilitler. Onları `islice`, `zip` ya da `break` ile sınırla.
:::

::: tahmin
Üç satır:

```python
from itertools import product, combinations, permutations
print(len(list(product("ab", repeat=3))))
print(list(combinations([1, 2, 3], 2)))
print(len(list(permutations(range(4)))))
```

???

`8`, `[(1, 2), (1, 3), (2, 3)]`, `24`. 2³ = 8; 3'ün 2'li kombinasyonu 3 tane; 4! = 24.
:::

::: anlat groupby, accumulate ve functools
**`groupby`** ardışık aynı anahtarlı elemanları gruplar. "Ardışık" kelimesi kritik: tüm eşitleri tek grupta toplamak istiyorsan önce aynı anahtarla **sırala**.

```python
from itertools import groupby, accumulate, pairwise

olaylar = [("ali", "giris"), ("ali", "dosya"), ("veli", "giris"), ("ali", "cikis")]
for kullanici, grup in groupby(olaylar, key=lambda o: o[0]):
    print(kullanici, [o[1] for o in grup])          #! ali iki ayrı grupta!
for kullanici, grup in groupby(sorted(olaylar), key=lambda o: o[0]):
    print(kullanici, len(list(grup)))

print(list(accumulate([3, 1, 4, 1, 5])))             #! birikimli toplam
print(list(accumulate([3, 1, 4, 1, 5], max)))        #! birikimli maksimum
print(list(pairwise([10, 13, 19, 20])))              #! ardışık çiftler (3.10+)
print([b - a for a, b in pairwise([10, 13, 19, 20])])   #! olaylar arası süre
```

### functools
```python
from functools import reduce, partial, lru_cache

print(reduce(lambda a, b: a * b, [1, 2, 3, 4, 5]))   #! katlama: ((((1*2)*3)*4)*5)

def log(seviye, mesaj):
    return f"[{seviye}] {mesaj}"
uyari = partial(log, "UYARI")                        #! ilk argümanı sabitlenmiş yeni fonksiyon
print(uyari("disk dolmak üzere"))

@lru_cache(maxsize=None)                             #! sonuçları hatırla (P24'teki hafızalama)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(150), fib.cache_info().hits)
```

`@lru_cache` satırı bir **dekoratördür**: fonksiyonu sarıp ona önbellek ekler. Nasıl çalıştığını P46'te kendin yazarak öğreneceksin.

> [!DERİN]
> `lru_cache` argümanları sözlük anahtarı olarak kullanır, yani argümanlar **hash'lenebilir** olmalıdır: liste verirsen `TypeError` alırsın. Ayrıca önbellek fonksiyon nesnesine bağlıdır ve sınırsızsa (`maxsize=None`) bellek sızıntısına dönüşebilir. Python 3.9+ `functools.cache` = sınırsız `lru_cache` kısayoludur.
:::

::: tahmin
İki satır:

```python
from itertools import groupby, accumulate
veri = "aaabccaa"
print([(k, len(list(g))) for k, g in groupby(veri)])
print(list(accumulate([1, 2, 3, 4])))
```

???

`[('a', 3), ('b', 1), ('c', 2), ('a', 2)]`, sonra `[1, 3, 6, 10]`. groupby **ardışık** grupları verir; sondaki "aa" ayrı bir grup olur.
:::

::: gorev Uzunluk kodlaması (RLE)
`sikistir(metin)` fonksiyonu ardışık tekrarları `karakter + sayı` biçiminde sıkıştırsın: `"aaabccaa"` → `"a3b1c2a2"`. `groupby` kullan.

```starter
from itertools import groupby

def sikistir(metin):
    pass
```

```test
need("sikistir")
eq(sikistir("aaabccaa"), "a3b1c2a2", "aaabccaa → a3b1c2a2")
eq(sikistir(""), "", "boş → boş")
eq(sikistir("x"), "x1", "x → x1")
eq(sikistir("zzzzzzzzzzzz"), "z12", "12 z → z12")
ok(calls("groupby"), "groupby kullan")
```

```solution
from itertools import groupby

def sikistir(metin):
    return "".join(f"{k}{len(list(g))}" for k, g in groupby(metin))
```

```hint
`for k, g in groupby(metin):` her grup için `len(list(g))` tekrar sayısıdır.
```
:::

::: gorev Kopya dosyalar
`kopyalar(hashler)` fonksiyonu bir `{dosya_adı: hash}` sözlüğü alsın ve **aynı hash'e sahip** dosya çiftlerini döndürsün. Her çift alfabetik sıralı bir demet `(a, b)` olsun, liste de sıralı olsun. `combinations` kullan.

```starter
from itertools import combinations

def kopyalar(hashler):
    pass
```

```test
need("kopyalar")
h = {"a.exe": "f1", "b.dll": "e2", "c.exe": "f1", "d.tmp": "f1", "e.bin": "e2", "f.txt": "99"}
eq(kopyalar(h), [("a.exe", "c.exe"), ("a.exe", "d.tmp"), ("b.dll", "e.bin"), ("c.exe", "d.tmp")], "tüm eş çiftler")
eq(kopyalar({"x": "1", "y": "2"}), [], "kopya yok → []")
ok(calls("combinations"), "combinations kullan")
```

```solution
from itertools import combinations

def kopyalar(hashler):
    return sorted(
        tuple(sorted((a, b)))
        for a, b in combinations(hashler, 2)
        if hashler[a] == hashler[b]
    )
```

```hint
`combinations(hashler, 2)` anahtar çiftlerini verir. Hash'leri eşitse çifti sıralı demet olarak topla.
```
:::

::: gorev Izgarada yollar
`yol_sayisi(m, n)` bir m×n ızgaranın sol üst köşesinden sağ alt köşesine, sadece **sağa** ya da **aşağı** giderek kaç farklı yol olduğunu döndürsün. Özyinelemeli yaz ve `@lru_cache` ile hızlandır. `yol_sayisi(18, 18)` anında dönmeli.

Kural: `yol_sayisi(1, n) = yol_sayisi(m, 1) = 1`, aksi halde `yol_sayisi(m-1, n) + yol_sayisi(m, n-1)`.

```starter
def yol_sayisi(m, n):
    if m == 1 or n == 1:
        return 1
    return yol_sayisi(m - 1, n) + yol_sayisi(m, n - 1)
```

```meta
timeout: 8
```

```test
need("yol_sayisi")
eq(yol_sayisi(2, 2), 2, "2×2 → 2")
eq(yol_sayisi(3, 3), 6, "3×3 → 6")
eq(yol_sayisi(3, 7), 28, "3×7 → 28")
eq(yol_sayisi(18, 18), 2333606220, "18×18 → 2333606220 (önbelleksiz çok yavaş)")
ok(uses("decorator") and ("lru_cache" in src or "cache" in src), "@lru_cache (ya da @cache) dekoratörü kullan")
```

```solution
from functools import lru_cache

@lru_cache(maxsize=None)
def yol_sayisi(m, n):
    if m == 1 or n == 1:
        return 1
    return yol_sayisi(m - 1, n) + yol_sayisi(m, n - 1)
```

```hint
`from functools import lru_cache` ve fonksiyonun üstüne `@lru_cache(maxsize=None)`.
```
:::
