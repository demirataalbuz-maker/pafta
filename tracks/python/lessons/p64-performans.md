---
id: p64
title: Performans ve Karmaşıklık
summary: Önce ölç; timeit ve cProfile, Big-O ile Python veri yapılarının maliyeti, algoritmik kazanç.
---

::: anlat Tahmin etme, ölç
Performans optimizasyonunun ilk kuralı: **önce ölç**. Yavaşlığın nerede olduğunu sezgiyle tahmin eden programcılar genelde yanılır. Donald Knuth'un sözüyle: "Erken optimizasyon tüm kötülüklerin anasıdır."

### timeit: küçük parçaları ölç
```python
import timeit

kelimeler = [str(i) for i in range(1000)]

def arti():
    s = ""
    for k in kelimeler:
        s += k + ","
    return s

def birlestir():
    return ",".join(kelimeler) + ","

for f in (arti, birlestir):
    t = timeit.timeit(f, number=2000)
    print(f"{f.__name__:<10} {t * 1000:.1f} ms")
```

`timeit` kodu çok kez çalıştırıp toplam süreyi verir; tek bir ölçümdeki gürültüyü (başka süreçler, önbellek) azaltır. Komut satırından da çalışır: `python -m timeit "','.join(map(str, range(100)))"`.

### cProfile: büyük resmi gör
```python
import cProfile, pstats, io

def ayristir(satir):
    return satir.split()

def analiz(n):
    sayim = {}
    for i in range(n):
        for parca in ayristir(f"10.0.0.{i % 50} GET /x 200"):
            sayim[parca] = sayim.get(parca, 0) + 1
    return len(sayim)

pr = cProfile.Profile()
pr.enable()
analiz(20000)
pr.disable()
cikti = io.StringIO()
pstats.Stats(pr, stream=cikti).sort_stats("cumulative").print_stats(5)
print(cikti.getvalue()[:900])
```

Profil, **hangi fonksiyonun kaç kez çağrıldığını** ve **zamanın nereye gittiğini** gösterir. `ncalls` sütunundaki beklenmedik büyük bir sayı çoğu zaman sorunun kendisidir.

> [!NOT]
> Komut satırından tüm bir programı profillemek için: `python -m cProfile -s cumulative betik.py`. Görsel analiz için `snakeviz` gibi araçlar var.
:::

::: tahmin
Çıktı tek satır:

```python
import timeit
liste = list(range(20000))
kume = set(liste)
t_liste = timeit.timeit(lambda: 19999 in liste, number=500)
t_kume = timeit.timeit(lambda: 19999 in kume, number=500)
print(t_liste > t_kume * 10)
```

???

`True`. Listede üyelik testi baştan sona tarama yapar (O(n)): sondaki elemanı bulmak için 20.000 karşılaştırma. Kümede ise hash ile doğrudan yuvaya bakılır (O(1)). Fark onlarca, hatta yüzlerce kat olur.
:::

::: anlat Big-O: ölçeklenme dili
**Big-O** gösterimi, girdi büyüdükçe çalışma süresinin **nasıl büyüdüğünü** anlatır:

| Gösterim | Ad | 1.000 → 1.000.000 olunca süre | Örnek |
|---|---|---|---|
| O(1) | sabit | aynı kalır | dict/set erişimi |
| O(log n) | logaritmik | ~2 kat | ikili arama |
| O(n) | doğrusal | 1000 kat | listede arama |
| O(n log n) | | ~2000 kat | sıralama |
| O(n²) | karesel | 1.000.000 kat | iç içe döngüyle her çifti karşılaştırmak |

### Python veri yapılarının maliyeti
| İşlem | list | dict / set | deque |
|---|---|---|---|
| sona ekle / sondan çıkar | O(1) | O(1) | O(1) |
| **başa** ekle / baştan çıkar | **O(n)** | | O(1) |
| `x in` | **O(n)** | O(1) | O(n) |
| indeksle erişim `l[i]` | O(1) | O(1) (anahtar) | O(n) |
| sırala | O(n log n) | | |

En büyük hızlanma mikro düzeltmelerden değil, **algoritmayı değiştirmekten** gelir: O(n²) bir iç içe döngüyü bir küme ile O(n)'e indirmek, 100.000 elemanda **saniyeleri milisaniyelere** çevirir. Bu paftanın görevleri tam olarak bu dönüşümleri istiyor.

### Python'a özgü küçük kurallar
- Yerleşik fonksiyonlar (`sum`, `max`, `sorted`, `str.join`) C ile yazılmıştır, elle yazılmış döngüden hızlıdır
- Döngü içinde aynı niteliği tekrar tekrar arama: `ekle = liste.append` yerel isme bağla
- Gereksiz kopyalardan kaçın: büyük veride dilim (`l[1:]`) yeni liste üretir
- Aynı hesabı tekrarlıyorsan önbellekle (`lru_cache`, P32)
- Gerçekten CPU sınırındaysan: NumPy, süreç havuzu (P55) ya da C uzantıları

> [!DERİN]
> Python 3.11, ortalama %25 hız kazancı getiren "Faster CPython" projesinin ilk büyük meyvesiydi: özelleştirici yorumlayıcı (P62), daha ucuz fonksiyon çağrıları ve sıfır maliyetli `try` blokları (istisna yükselmediği sürece `try`'ın maliyeti yok). 3.13 deneysel bir JIT derleyici ekledi. Yine de bir algoritmanın karmaşıklık sınıfını hiçbir yorumlayıcı optimizasyonu değiştiremez.
:::

::: tahmin
Çıktı tek satır:

```python
from collections import deque
import timeit
l = list(range(200000))
d = deque(l)
t_liste = timeit.timeit(lambda: l.insert(0, 1), number=300)
t_deque = timeit.timeit(lambda: d.appendleft(1), number=300)
print(t_liste > t_deque)
```

???

`True`. Listenin başına eklemek bütün elemanları bir konum kaydırır (O(n), burada 200.000 eleman). deque iki uçta da O(1)'dir.
:::

::: gorev Ortak elemanlar
Aşağıdaki fonksiyon doğru çalışıyor ama O(n·m): her eleman için diğer listeyi baştan tarıyor. 50.000'er elemanlı listelerde süre sınırını aşıyor. **Aynı sonucu** (ortak elemanların sıralı ve tekrarsız listesi) verecek şekilde hızlandır.

```starter
def ortak_elemanlar(a, b):
    sonuc = []
    for x in a:
        if x in b and x not in sonuc:
            sonuc.append(x)
    return sorted(sonuc)
```

```meta
timeout: 10
```

```test
import random, time
need("ortak_elemanlar")
eq(ortak_elemanlar([5, 1, 3, 3, 9], [3, 9, 9, 2]), [3, 9], "küçük örnek")
eq(ortak_elemanlar([], [1]), [], "boş")
random.seed(7)
a = [random.randrange(10**6) for _ in range(50000)]
b = [random.randrange(10**6) for _ in range(50000)]
bas = time.perf_counter()
s = ortak_elemanlar(a, b)
gecen = time.perf_counter() - bas
eq(s, sorted(set(a) & set(b)), "büyük girdide doğru sonuç")
ok(gecen < 1.0, "50.000'lik listelerde 1 saniyenin altında", got=round(gecen, 3))
```

```solution
def ortak_elemanlar(a, b):
    return sorted(set(a) & set(b))
```

```hint
`x in b` listede O(m)'dir. Kümelerde üyelik O(1), kesişim ise tek işlem: `set(a) & set(b)`.
```
:::

::: gorev İkili arama
`ikili_ara(sirali, hedef)` sıralı bir listede hedefin indeksini **O(log n)** ile bulsun; yoksa -1 döndürsün. `index()`, `in` ve `bisect` kullanmak yok; aralığı her adımda ikiye bölerek kendin yaz.

```starter
def ikili_ara(sirali, hedef):
    for i, x in enumerate(sirali):
        if x == hedef:
            return i
    return -1
```

```meta
timeout: 10
```

```test
import time
need("ikili_ara")
l = list(range(0, 2_000_000, 2))
eq(ikili_ara(l, 0), 0, "ilk eleman")
eq(ikili_ara(l, 1_999_998), len(l) - 1, "son eleman")
eq(ikili_ara(l, 777_778), 388_889, "ortadan bir eleman")
eq(ikili_ara(l, 777_777), -1, "olmayan (tek sayı)")
eq(ikili_ara([], 5), -1, "boş liste")
eq(ikili_ara([5], 5), 0, "tek eleman")
bas = time.perf_counter()
for h in range(0, 2_000_000, 400):
    ikili_ara(l, h)
gecen = time.perf_counter() - bas
ok(gecen < 1.0, "5000 arama 1 saniyenin altında (logaritmik olmalı)", got=round(gecen, 3))
ok(not calls("index") and not calls("bisect") and not calls("bisect_left"), "index/bisect kullanmadan")
```

```solution
def ikili_ara(sirali, hedef):
    alt, ust = 0, len(sirali) - 1
    while alt <= ust:
        orta = (alt + ust) // 2
        if sirali[orta] == hedef:
            return orta
        if sirali[orta] < hedef:
            alt = orta + 1
        else:
            ust = orta - 1
    return -1
```

```hint
İki sınır tut: `alt = 0`, `ust = len - 1`. Ortadaki eleman hedeften küçükse arama sağ yarıda, büyükse sol yarıda devam eder.
```
:::

::: gorev En uzun ortak alt dizi
İki metnin **en uzun ortak alt dizisinin** (LCS: sırası korunan ama bitişik olması gerekmeyen karakterler) uzunluğunu döndüren `lcs(a, b)` fonksiyonunu **dinamik programlama** ile yaz. Saf özyineleme üsteldir; tablo O(n·m)'dir. 1000×1000'lik girdide birkaç saniyenin altında bitmeli.

Örnek: `lcs("ABCBDAB", "BDCABA")` → 4 (ör. "BCBA")

```starter
def lcs(a, b):
    if not a or not b:
        return 0
    if a[0] == b[0]:
        return 1 + lcs(a[1:], b[1:])
    return max(lcs(a[1:], b), lcs(a, b[1:]))
```

```meta
timeout: 15
```

```test
import random, time
need("lcs")
eq(lcs("ABCBDAB", "BDCABA"), 4, "klasik örnek → 4")
eq(lcs("", "abc"), 0, "boş")
eq(lcs("python", "python"), 6, "aynı metin")
eq(lcs("abc", "xyz"), 0, "ortak yok")
random.seed(1)
a = "".join(random.choice("ACGT") for _ in range(1000))
b = "".join(random.choice("ACGT") for _ in range(1000))
bas = time.perf_counter()
s = lcs(a, b)
gecen = time.perf_counter() - bas
ok(600 < s < 700, "1000×1000 DNA dizisi makul sonuç", got=s)
ok(gecen < 6, "1000×1000 6 saniyenin altında", got=round(gecen, 2))
```

```solution
def lcs(a, b):
    onceki = [0] * (len(b) + 1)
    for ca in a:
        simdi = [0]
        for j, cb in enumerate(b, 1):
            if ca == cb:
                simdi.append(onceki[j - 1] + 1)
            else:
                simdi.append(max(onceki[j], simdi[j - 1]))
        onceki = simdi
    return onceki[-1]
```

```hint
Tablo: `T[i][j]` = a'nın ilk i, b'nin ilk j karakterinin LCS'i. Karakterler eşitse `T[i-1][j-1] + 1`, değilse `max(T[i-1][j], T[i][j-1])`.
```

```hint
Bellek için sadece önceki satırı tutmak yeter. Biyoinformatikte DNA dizileri ve `diff` aracındaki satır karşılaştırması bu algoritmanın akrabalarıdır.
```
:::
