---
id: p54
title: İş Parçacıkları ve GIL
summary: threading ile eşzamanlılık, join, yarış durumu, Lock, Queue ile üretici-tüketici ve GIL gerçeği.
---

::: anlat Aynı anda birden fazla iş
Bir programın çoğu zamanı **beklemekle** geçer: diskin, ağın, kullanıcının cevabını. **İş parçacıkları** (threads) bu bekleme sürelerini değerlendirir: biri beklerken diğeri çalışır.

```python
import threading, time

def indir(ad, sure):
    time.sleep(sure)                       #! ağ beklemesini taklit ediyor
    print(f"{ad} bitti ({sure} sn)")

bas = time.perf_counter()
isler = [threading.Thread(target=indir, args=(f"dosya{i}", 0.3)) for i in range(5)]
for t in isler:
    t.start()                              #! başlat: hemen döner
for t in isler:
    t.join()                               #! bitmesini bekle
print(f"toplam: {time.perf_counter() - bas:.2f} sn")   #! 5 × 0.3 değil, ~0.3
```

Beş iş sırayla yapılsa 1.5 saniye sürerdi; paralel beklemeyle ~0.3 saniye sürdü.

- `Thread(target=f, args=(...))`: iş parçacığını tanımla
- `start()`: çalıştırmaya başla
- `join(timeout=None)`: bitmesini bekle
- `daemon=True`: ana program bitince beklenmeden öldürülsün

### GIL gerçeği
CPython'da bir **Global Yorumlayıcı Kilidi** (GIL) vardır: aynı anda yalnızca **bir** iş parçacığı Python bytecode'u çalıştırabilir. Sonuç:

- **G/Ç ağırlıklı** işlerde (ağ, disk, `sleep`) iş parçacıkları **hızlandırır**, çünkü bekleyen iş parçacığı GIL'i bırakır.
- **CPU ağırlıklı** işlerde (asal sayı bulma, özet hesaplama döngüsü) iş parçacıkları **hızlandırmaz**, hatta yavaşlatabilir. Bunun için süreçler (P55) gerekir.

> [!DERİN]
> GIL, CPython'un referans sayımlı bellek yönetimini (P63) basit ve hızlı tutmak için var. Python 3.13 deneysel bir "GIL'siz" (free-threaded, `python3.13t`) derleme getirdi; ekosistem buna yavaş yavaş uyum sağlıyor. Ayrıca `hashlib`, `zlib` gibi C ile yazılmış bazı fonksiyonlar büyük verilerde GIL'i bırakır; bu yüzden onlarla iş parçacığı CPU işinde bile hızlanabilir.
:::

::: tahmin
Çıktı tek satır:

```python
import threading, time

def yavas(ad, bekle, liste):
    time.sleep(bekle)
    liste.append(ad)

l = []
a = threading.Thread(target=yavas, args=("a", 0.3, l))
b = threading.Thread(target=yavas, args=("b", 0.05, l))
a.start()
b.start()
a.join()
b.join()
print(l)
```

???

`['b', 'a']`. İkisi neredeyse aynı anda başlar; b daha kısa beklediği için listeye önce o ekler. `start` sırası bitiş sırasını belirlemez.
:::

::: anlat Yarış durumu ve kilitler
İş parçacıkları **aynı belleği** paylaşır. İki iş parçacığı aynı değişkeni "oku → hesapla → yaz" diye güncellerse güncellemeler birbirini ezebilir. Buna **yarış durumu** (race condition) denir:

```python
import threading, time

bakiye = 0

def yatir_kotu():
    global bakiye
    for _ in range(50):
        mevcut = bakiye                  #! oku
        time.sleep(0)                    #! diğer iş parçacığına geçiş fırsatı
        bakiye = mevcut + 1              #! yaz: arada başkası yazdıysa EZİLİR

ts = [threading.Thread(target=yatir_kotu) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("kilitsiz:", bakiye, "(200 olmalıydı)")

kilit = threading.Lock()
bakiye = 0

def yatir_iyi():
    global bakiye
    for _ in range(50):
        with kilit:                      #! aynı anda sadece bir iş parçacığı girer
            mevcut = bakiye
            time.sleep(0)
            bakiye = mevcut + 1

ts = [threading.Thread(target=yatir_iyi) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("kilitli:", bakiye)
```

GIL bu sorunu **çözmez**: `bakiye += 1` bile birden fazla bytecode komutudur ve aralarında iş parçacığı değişebilir.

### queue.Queue: güvenli haberleşme
Paylaşılan veriyi kilitlerle korumak yerine iş parçacıkları arasında **mesaj göndermek** daha az hataya açıktır. `queue.Queue` kendi içinde kilitlidir:

```python
import queue, threading

kuyruk = queue.Queue()
sonuclar = []

def isci():
    while True:
        is_ = kuyruk.get()               #! iş gelene kadar bekler
        if is_ is None:                  #! nöbetçi değer: "artık iş yok"
            break
        sonuclar.append(is_ * is_)

iscilar = [threading.Thread(target=isci) for _ in range(3)]
for t in iscilar: t.start()
for n in range(10): kuyruk.put(n)
for _ in iscilar: kuyruk.put(None)       #! her işçiye bir dur sinyali
for t in iscilar: t.join()
print(sorted(sonuclar))
```

> [!GÜVENLİK]
> Yarış durumları sadece yanlış sayılar üretmez, **güvenlik açığı** da olur. Bir web uygulaması "kupon kullanıldı mı?" kontrolüyle "kullanıldı olarak işaretle" adımı arasında kilit tutmazsa, aynı kupon paralel isteklerle onlarca kez kullanılabilir. P26'daki TOCTOU da bir yarış durumudur. Kontrol ve işlem **tek bir atomik adım** olmalıdır.
:::

::: tahmin
Çıktı tek satır:

```python
import threading

sonuc = []
def is_(n):
    sonuc.append(n * n)

ts = [threading.Thread(target=is_, args=(i,)) for i in range(5)]
for t in ts:
    t.start()
for t in ts:
    t.join()
print(sorted(sonuc), threading.current_thread().name)
```

???

`[0, 1, 4, 9, 16] MainThread`. Ekleme sırası garanti olmadığı için sıralayarak yazdırdık. `join`'ler sayesinde print anında bütün işler bitmiştir. Kodun kendisi ana iş parçacığında çalışır.
:::

::: gorev Paralel kareler
`paralel_kare(sayilar)` her sayı için **ayrı bir iş parçacığında** karesini hesaplasın ve sonuçları **girdi sırasıyla** liste olarak döndürsün. Her iş parçacığı sonucunu önceden boyutlandırılmış bir listenin kendi indeksine yazsın.

```starter
import threading

def paralel_kare(sayilar):
    pass
```

```test
need("paralel_kare")
eq(paralel_kare([3, 1, 4, 1, 5]), [9, 1, 16, 1, 25], "sıra korunmalı")
eq(paralel_kare([]), [], "boş → []")
eq(paralel_kare(list(range(50))), [i * i for i in range(50)], "50 iş parçacığı")
ok(calls("Thread") and calls("join"), "threading.Thread ve join kullan")
```

```solution
import threading

def paralel_kare(sayilar):
    sonuc = [None] * len(sayilar)

    def hesapla(i, n):
        sonuc[i] = n * n

    isler = [threading.Thread(target=hesapla, args=(i, n)) for i, n in enumerate(sayilar)]
    for t in isler:
        t.start()
    for t in isler:
        t.join()
    return sonuc
```

```hint
`sonuc = [None] * len(sayilar)` ve iş parçacığına indeksi de ver: `args=(i, n)`. Her biri farklı indekse yazdığı için kilit gerekmez.
```
:::

::: gorev Güvenli sayaç
`GuvenliSayac` sınıfı birden çok iş parçacığından aynı anda kullanılabilsin:

- `artir(n=1)`: değeri n artırır
- `deger`: mevcut değer (property)
- İçeride bir `threading.Lock` kullansın

```starter
import threading

class GuvenliSayac:
    def __init__(self):
        self._deger = 0

    def artir(self, n=1):
        self._deger += n

    @property
    def deger(self):
        return self._deger
```

```test
import threading
S = need("GuvenliSayac", "sınıf")
s = S()
def calis():
    for _ in range(5000):
        s.artir()
ts = [threading.Thread(target=calis) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
eq(s.deger, 40000, "8 × 5000 = 40000")
s.artir(10)
eq(s.deger, 40010, "artir(10)")
kilit_turu = type(threading.Lock())
ok(any(isinstance(v, kilit_turu) for v in vars(s).values()), "nesnede bir threading.Lock olmalı")
```

```solution
import threading

class GuvenliSayac:
    def __init__(self):
        self._deger = 0
        self._kilit = threading.Lock()

    def artir(self, n=1):
        with self._kilit:
            self._deger += n

    @property
    def deger(self):
        with self._kilit:
            return self._deger
```

```hint
`__init__`'te `self._kilit = threading.Lock()`; `artir` içinde `with self._kilit:`.
```
:::

::: gorev İşçi havuzu
`isle(isler, isci_sayisi)` fonksiyonu `queue.Queue` ve `isci_sayisi` kadar iş parçacığıyla her işi (bir sayı) işlesin: sonuç `n * 2`. Bütün sonuçları **küçükten büyüğe sıralı** liste olarak döndürsün. İşçileri nöbetçi değerle (`None`) durdur.

```starter
import queue, threading

def isle(isler, isci_sayisi):
    pass
```

```test
need("isle")
eq(isle([5, 1, 3], 2), [2, 6, 10], "3 iş, 2 işçi")
eq(isle(list(range(100)), 8), [i * 2 for i in range(100)], "100 iş, 8 işçi")
eq(isle([], 3), [], "iş yok")
import threading
once = threading.active_count()
isle([1, 2, 3], 4)
eq(threading.active_count(), once, "bütün işçiler bitmeli (join)")
ok(calls("Queue"), "queue.Queue kullan")
```

```solution
import queue, threading

def isle(isler, isci_sayisi):
    kuyruk = queue.Queue()
    sonuclar = queue.Queue()

    def isci():
        while True:
            n = kuyruk.get()
            if n is None:
                return
            sonuclar.put(n * 2)

    iscilar = [threading.Thread(target=isci) for _ in range(isci_sayisi)]
    for t in iscilar:
        t.start()
    for n in isler:
        kuyruk.put(n)
    for _ in iscilar:
        kuyruk.put(None)
    for t in iscilar:
        t.join()
    return sorted(sonuclar.get() for _ in range(sonuclar.qsize()))
```

```hint
İşler için bir kuyruk, sonuçlar için ikinci bir kuyruk (ya da kilitli bir liste). Her işçi `None` görünce `return`.
```
:::
