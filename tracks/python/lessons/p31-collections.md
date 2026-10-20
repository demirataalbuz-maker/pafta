---
id: p31
title: collections
summary: Counter, defaultdict, deque, namedtuple ve OrderedDict ile hazır veri yapıları.
---

::: anlat Sayma ve varsayılanlar
P16'da elle yazdığın kalıpların endüstriyel sürümleri `collections` modülündedir.

### Counter: sayan sözlük
```python
from collections import Counter

ipler = ["10.0.0.7", "10.0.0.9", "10.0.0.7", "10.0.0.3", "10.0.0.7", "10.0.0.9"]
c = Counter(ipler)
print(c)
print(c.most_common(2))             #! en sık 2
print(c["10.0.0.7"], c["yok"])      #! olmayan anahtar 0 döner, KeyError yok
c.update(["10.0.0.3", "10.0.0.3"])  #! sayıları artır
print(c.most_common(1))
print(Counter("aab") + Counter("abc"))   #! sayaçlar toplanabilir
print(Counter(kelime for kelime in "a b a c a".split()))
```

### defaultdict: anahtar yoksa üret
```python
from collections import defaultdict

gruplar = defaultdict(list)           #! olmayan anahtar → otomatik []
for ip, port in [("10.0.0.7", 22), ("10.0.0.9", 80), ("10.0.0.7", 443)]:
    gruplar[ip].append(port)          #! setdefault'a gerek yok
print(dict(gruplar))

benzersiz = defaultdict(set)          #! set, int, list... hangi "fabrika" istersen
benzersiz["ali"].add("web01")
benzersiz["ali"].add("web01")
print(dict(benzersiz))
```

`defaultdict(f)`'deki `f` bir **fonksiyondur** (fabrika): eksik anahtar okunduğunda çağrılır ve sonucu yerleştirilir. `list` ve `int` de fonksiyondur: `int()` → 0.

> [!TUZAK]
> defaultdict'te sadece **okumak** bile anahtarı oluşturur: `if gruplar["yok"]:` satırı sözlüğe `"yok": []` ekler. Varlık kontrolü için `in` kullan.
:::

::: tahmin
İki satır:

```python
from collections import Counter
c = Counter("mississippi")
print(c.most_common(2))
print(c["z"], sum(c.values()))
```

???

`[('i', 4), ('s', 4)]`, sonra `0 11`. i ve s 4'er kez geçer; eşitlikte ilk görülen önce gelir. Olmayan anahtar 0 döner. Toplam harf sayısı 11'dir.
:::

::: anlat deque, namedtuple, OrderedDict
### deque: iki uçlu kuyruk
Listenin başına eklemek/çıkarmak O(n)'dir, çünkü tüm elemanlar kayar. `deque`'da iki uç da O(1)'dir. `maxlen` verirsen **kayan pencere** olur: dolunca en eskisi kendiliğinden düşer.

```python
from collections import deque

kuyruk = deque(["a", "b"])
kuyruk.appendleft("acil")             #! başa ekle
kuyruk.append("c")
print(kuyruk.popleft(), kuyruk)       #! baştan al: FIFO kuyruk

son5 = deque(maxlen=5)                #! "tail" mantığı
for i in range(1, 13):
    son5.append(f"satır {i}")
print(list(son5))
```

### namedtuple: alan adlı demet
```python
from collections import namedtuple

Olay = namedtuple("Olay", ["zaman", "ip", "durum"])
o = Olay("08:02", "203.0.113.9", "FAIL")
print(o.ip, o[2])                     #! hem isimle hem indeksle
zaman, ip, durum = o                  #! hâlâ bir demet
print(o._replace(durum="OK"))         #! değiştirilemez: yeni kopya üretir
print(o._asdict())
```

### OrderedDict: sırayı yönet
Normal dict de sıralıdır, ama `OrderedDict`'in `move_to_end` gibi sıra işlemleri vardır. En bilinen kullanımı **LRU önbellek** (en son kullanılan sona, taşınca baştakini at):

```python
from collections import OrderedDict

onbellek = OrderedDict()
for anahtar in ["a", "b", "c", "a", "d"]:
    if anahtar in onbellek:
        onbellek.move_to_end(anahtar)      #! kullanıldı → en sona
    onbellek[anahtar] = True
    if len(onbellek) > 3:
        onbellek.popitem(last=False)       #! en eskiyi at
print(list(onbellek))
```

> [!GÜVENLİK]
> `deque(maxlen=N)` hız sınırlamanın (rate limiting) ve kaba kuvvet tespitinin temel taşıdır: her IP için son N denemenin zaman damgasını tut. Penceredeki en eski deneme X saniyeden yeniyse alarm üret. Bu paftanın son görevinde tam olarak bunu yazacaksın.
:::

::: tahmin
İki satır:

```python
from collections import deque, defaultdict
d = deque(maxlen=3)
for i in range(5):
    d.append(i)
print(list(d))
g = defaultdict(list)
g["a"].append(1)
print(dict(g), g["b"])
```

???

`[2, 3, 4]`, sonra `{'a': [1]} []`. maxlen=3 dolunca baştakiler düşer. `dict(g)` önce hesaplanır (henüz sadece 'a' var), sonra `g["b"]` okunurken boş liste üretilir ve yazılır.
:::

::: gorev En gürültülü IP'ler
İlk satırda N, ardından N satır log var. Her satırın **ilk alanı** IP adresi. `Counter` ile en çok görünen **3 IP'yi** `ip sayı` biçiminde, çoktan aza yazdır.

```starter
from collections import Counter
n = int(input())

```

```stdin
7
203.0.113.9 GET /login
10.0.0.5 GET /
203.0.113.9 POST /login
198.51.100.4 GET /admin
203.0.113.9 POST /login
198.51.100.4 GET /admin
192.0.2.1 GET /
```

```test
girdi = "7\n203.0.113.9 GET /login\n10.0.0.5 GET /\n203.0.113.9 POST /login\n198.51.100.4 GET /admin\n203.0.113.9 POST /login\n198.51.100.4 GET /admin\n192.0.2.1 GET /"
eq(run(girdi).strip().splitlines(), ["203.0.113.9 3", "198.51.100.4 2", "10.0.0.5 1"], "ilk 3 (eşitlikte ilk görülen)")
eq(run("1\n1.1.1.1 x").strip(), "1.1.1.1 1", "tek satır")
ok(calls("Counter") and calls("most_common"), "Counter ve most_common kullan")
```

```solution
from collections import Counter
n = int(input())
c = Counter(input().split()[0] for _ in range(n))
for ip, sayi in c.most_common(3):
    print(ip, sayi)
```

```hint
`Counter(input().split()[0] for _ in range(n))` bir satırda sayar.
```
:::

::: gorev tail
`son_satirlar(yol, n)` fonksiyonu dosyanın **son n satırını** (satır sonları olmadan) liste olarak döndürsün. Dosyanın tamamını belleğe almadan, `deque(maxlen=n)` ile yap.

```setup
with open("buyuk.log", "w", encoding="utf-8") as f:
    for i in range(1, 10001):
        f.write(f"olay {i}\n")
with open("kisa.log", "w", encoding="utf-8") as f:
    f.write("tek\n")
```

```starter
from collections import deque

def son_satirlar(yol, n):
    pass
```

```test
need("son_satirlar")
eq(son_satirlar("buyuk.log", 3), ["olay 9998", "olay 9999", "olay 10000"], "son 3 satır")
eq(son_satirlar("kisa.log", 5), ["tek"], "dosya n'den kısaysa hepsi")
ok(calls("deque"), "deque(maxlen=n) kullan")
```

```solution
from collections import deque

def son_satirlar(yol, n):
    with open(yol, encoding="utf-8") as f:
        son = deque(f, maxlen=n)
    return [s.rstrip("\n") for s in son]
```

```hint
`deque(f, maxlen=n)` dosyayı satır satır tüketir ve sadece son n satırı tutar.
```
:::

::: gorev Kaba kuvvet dedektörü
`tespit(olaylar, esik, pencere)` fonksiyonunu yaz. `olaylar`, zamana göre sıralı `(zaman_sn, ip)` demetlerinden oluşan bir liste (başarısız giriş denemeleri). Herhangi bir **`pencere` saniyelik aralıkta** en az **`esik`** deneme yapan IP'leri **sıralı liste** olarak döndür.

Örnek: `esik=3, pencere=10` → bir IP'nin 3 denemesi 10 saniye içine sığıyorsa (son deneme − ilk deneme < 10) alarm.

```starter
from collections import defaultdict, deque

def tespit(olaylar, esik, pencere):
    pass
```

```test
need("tespit")
olaylar = [(0, "A"), (1, "B"), (2, "A"), (5, "A"), (30, "B"), (31, "B"), (50, "C"), (55, "C"), (61, "C")]
eq(tespit(olaylar, 3, 10), ["A"], "A 0-5 arası 3 deneme → alarm; C 11 saniyeye yayılmış → yok")
eq(tespit(olaylar, 2, 10), ["A", "B", "C"], "eşik 2 → hepsi")
eq(tespit(olaylar, 3, 12), ["A", "C"], "pencere 12 → C de yakalanır")
eq(tespit([], 3, 10), [], "olay yok → []")
eq(tespit([(0, "X"), (100, "X"), (200, "X")], 3, 60), [], "yavaş denemeler → yok")
eq(tespit([(0, "X"), (5, "X"), (10, "X")], 3, 10), [], "tam 10 saniye: 10 < 10 değil → yok")
eq(tespit([(0, "X"), (5, "X"), (9, "X")], 3, 10), ["X"], "9 saniye → alarm")
```

```solution
from collections import defaultdict, deque

def tespit(olaylar, esik, pencere):
    son = defaultdict(lambda: deque(maxlen=esik))
    alarm = set()
    for zaman, ip in olaylar:
        q = son[ip]
        q.append(zaman)
        if len(q) == esik and q[-1] - q[0] < pencere:
            alarm.add(ip)
    return sorted(alarm)
```

```hint
Her IP için son `esik` denemenin zamanını tutan bir `deque(maxlen=esik)`: `defaultdict(lambda: deque(maxlen=esik))`.
```

```hint
Kuyruk doluysa ve `q[-1] - q[0] < pencere` ise o IP alarm verir.
```
:::
