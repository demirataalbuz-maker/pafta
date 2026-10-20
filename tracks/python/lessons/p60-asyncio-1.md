---
id: p60
title: asyncio I · async ve await
summary: Olay döngüsü, eşyordamlar, await, gather, create_task, TaskGroup ve engelleyen kodun tehlikesi.
---

::: anlat Tek iş parçacığında binlerce bekleme
İş parçacıkları her bekleme için ayrı bir işletim sistemi iş parçacığı harcar. 10.000 bağlantıyı aynı anda beklemek isteyen bir sunucu için bu pahalıdır. **asyncio** başka bir yol sunar: **tek** iş parçacığında çalışan bir **olay döngüsü** ve beklerken kontrolü gönüllü olarak geri veren **eşyordamlar** (coroutines).

```python
import asyncio, time

async def indir(ad, sure):                    #! async def → eşyordam fonksiyonu
    print(f"{ad} başladı")
    await asyncio.sleep(sure)                 #! await: "beklerken döngü başka işe baksın"
    print(f"{ad} bitti")
    return f"{ad}:{sure}"

async def ana():
    bas = time.perf_counter()
    sonuclar = await asyncio.gather(          #! hepsini aynı anda yürüt, hepsini bekle
        indir("a", 0.3), indir("b", 0.2), indir("c", 0.1))
    print(sonuclar, f"{time.perf_counter() - bas:.2f} sn")

asyncio.run(ana())                            #! olay döngüsünü kur, ana()'yı çalıştır, kapat
```

Kavramlar:

- **`async def`**: çağrıldığında gövdeyi çalıştırmaz, bir **eşyordam nesnesi** döndürür (P45'teki üreteçler gibi).
- **`await x`**: x bitene kadar **bu** eşyordamı askıya alır; döngü bu sırada başka eşyordamları ilerletir. Sadece `async def` içinde kullanılabilir.
- **`asyncio.run(e)`**: programın giriş noktası; bir döngü kurar, `e` bitene kadar çalıştırır.
- **`asyncio.gather(...)`**: birden çok eşyordamı eşzamanlı yürütür ve sonuçları **verilen sırayla** döndürür.

> [!TUZAK]
> Eşyordam içinde **`time.sleep()` ya da engelleyen herhangi bir çağrı** (requests ile HTTP, büyük bir dosya okuma, ağır hesap) kullanma. Döngü tek iş parçacığında çalıştığı için engelleyen çağrı **bütün** eşyordamları dondurur. Asenkron eşdeğerini kullan (`asyncio.sleep`, `aiohttp`, `asyncio.open_connection`) ya da engelleyen işi `await asyncio.to_thread(f, ...)` ile bir iş parçacığına gönder (P61).
:::

::: tahmin
Üç satır:

```python
import asyncio

async def selam(ad, s):
    await asyncio.sleep(s)
    print(ad)
    return ad.upper()

async def ana():
    sonuc = await asyncio.gather(selam("a", 0.2), selam("b", 0.1))
    print(sonuc)

asyncio.run(ana())
```

???

`b`, `a`, `['A', 'B']`. İkisi aynı anda bekler; b daha kısa beklediği için önce yazar. Ama `gather` sonuçları **verildiği sırayla** döndürür.
:::

::: anlat Görevler ve TaskGroup
`await e` yazmak `e`'yi **hemen** çalıştırır ve bitmesini bekler. Bir eşyordamı **arka planda başlatıp** sonra beklemek için onu bir **göreve** (Task) sararsın:

```python
import asyncio

async def is_(n):
    await asyncio.sleep(0.1)
    return n * n

async def ana():
    g1 = asyncio.create_task(is_(3))          #! hemen zamanlandı, arka planda başlıyor
    g2 = asyncio.create_task(is_(4))
    print("görevler başladı, bu arada başka iş...")
    print(await g1, await g2)                 #! sonuçları topla

    async with asyncio.TaskGroup() as tg:     #! 3.11+: yapılandırılmış eşzamanlılık
        gorevler = [tg.create_task(is_(n)) for n in range(5)]
    print([g.result() for g in gorevler])     #! blok çıkışında hepsi bitmiş olur

asyncio.run(ana())
```

**TaskGroup** modern ve güvenli yoldur: bloktan çıkarken bütün görevlerin bitmesini bekler. Görevlerden biri hata verirse **diğerlerini iptal eder** ve hataları P26'da sözünü ettiğimiz bir `ExceptionGroup` içinde yükseltir; `except*` ile yakalanır.

> [!DERİN]
> asyncio'nun kalbi `select`/`epoll`/IOCP gibi işletim sistemi çağrılarıdır: döngü "şu soketlerden hangisinde veri var?" diye sorar ve hazır olanın eşyordamını uyandırır. `await` aslında üreteçlerin `yield`'inin yakın akrabasıdır: eşyordam döngüye bir **Future** verir ve "bu tamamlanınca beni uyandır" der. Bu yüzden asyncio tek iş parçacığında **eşzamanlıdır** (concurrent) ama **paralel** değildir: CPU işi hızlanmaz, beklemeler üst üste biner.
:::

::: tahmin
İki satır:

```python
import asyncio

async def f():
    return 42

c = f()
print(type(c).__name__)
print(asyncio.run(c))
```

???

`coroutine`, sonra `42`. `f()` çağrısı gövdeyi çalıştırmaz, sadece bir eşyordam nesnesi üretir. Değeri almak için onu bir olay döngüsünde çalıştırman (`asyncio.run` ya da başka bir eşyordamda `await`) gerekir.
:::

::: gorev Eşzamanlı indirme taklidi
`async def hepsini_getir(gecikmeler)` her gecikme için `asyncio.sleep(g)` bekleyip `g`'yi döndüren bir eşyordamı **aynı anda** çalıştırsın ve sonuçları sırayla liste olarak döndürsün. Toplam süre en uzun gecikme kadar olmalı, toplamı kadar değil.

```starter
import asyncio

async def getir(g):
    await asyncio.sleep(g)
    return g

async def hepsini_getir(gecikmeler):
    sonuclar = []
    for g in gecikmeler:
        sonuclar.append(await getir(g))
    return sonuclar
```

```test
import asyncio, time, inspect
need("hepsini_getir")
ok(inspect.iscoroutinefunction(hepsini_getir), "async def olmalı")
bas = time.perf_counter()
eq(asyncio.run(hepsini_getir([0.3, 0.1, 0.3, 0.2])), [0.3, 0.1, 0.3, 0.2], "sonuçlar sırayla")
gecen = time.perf_counter() - bas
ok(gecen < 0.6, "eşzamanlı çalışmalı (~0.3 sn, 0.9 değil)", got=round(gecen, 2))
eq(asyncio.run(hepsini_getir([])), [], "boş liste")
```

```solution
import asyncio

async def getir(g):
    await asyncio.sleep(g)
    return g

async def hepsini_getir(gecikmeler):
    return list(await asyncio.gather(*(getir(g) for g in gecikmeler)))
```

```hint
Döngüde tek tek `await` etmek onları **sırayla** çalıştırır. `asyncio.gather(*eşyordamlar)` ile hepsini birden ver.
```
:::

::: gorev TaskGroup ile görevler
`async def kareler(n)` `asyncio.TaskGroup` içinde 0'dan n-1'e kadar her i için bir görev başlatsın (her görev `await asyncio.sleep(0.01)` yapıp `i * i` döndürsün) ve sonuçları sırayla liste olarak döndürsün.

```starter
import asyncio

async def kare(i):
    await asyncio.sleep(0.01)
    return i * i

async def kareler(n):
    pass
```

```test
import asyncio
need("kareler")
eq(asyncio.run(kareler(6)), [0, 1, 4, 9, 16, 25], "6 görev")
eq(asyncio.run(kareler(0)), [], "0 görev")
ok("TaskGroup" in src, "asyncio.TaskGroup kullan")
```

```solution
import asyncio

async def kare(i):
    await asyncio.sleep(0.01)
    return i * i

async def kareler(n):
    async with asyncio.TaskGroup() as tg:
        gorevler = [tg.create_task(kare(i)) for i in range(n)]
    return [g.result() for g in gorevler]
```

```hint
`async with asyncio.TaskGroup() as tg:` içinde `tg.create_task(kare(i))`. Bloktan sonra `g.result()`.
```
:::

::: gorev Asenkron işçi kuyruğu
`async def isle(ogeler, isci=3)` bir `asyncio.Queue` ve `isci` sayısı kadar işçi görevle her öğeyi işlesin: işçi öğeyi alır, `await asyncio.sleep(0.01)` bekler ve `x * 2` sonucunu bir listeye ekler. Bütün öğeler bitince işçileri iptal et ve sonuçları **sıralı** döndür.

```starter
import asyncio

async def isle(ogeler, isci=3):
    pass
```

```test
import asyncio
need("isle")
eq(asyncio.run(isle([5, 1, 3])), [2, 6, 10], "3 öğe")
eq(asyncio.run(isle(list(range(30)), isci=5)), [i * 2 for i in range(30)], "30 öğe, 5 işçi")
eq(asyncio.run(isle([])), [], "boş")
ok(calls("Queue"), "asyncio.Queue kullan")
```

```solution
import asyncio

async def isle(ogeler, isci=3):
    kuyruk = asyncio.Queue()
    sonuclar = []

    async def calisan():
        while True:
            x = await kuyruk.get()
            try:
                await asyncio.sleep(0.01)
                sonuclar.append(x * 2)
            finally:
                kuyruk.task_done()

    for x in ogeler:
        kuyruk.put_nowait(x)
    gorevler = [asyncio.create_task(calisan()) for _ in range(isci)]
    await kuyruk.join()
    for g in gorevler:
        g.cancel()
    await asyncio.gather(*gorevler, return_exceptions=True)
    return sorted(sonuclar)
```

```hint
Kalıp: öğeleri kuyruğa koy, işçileri `create_task` ile başlat, `await kuyruk.join()` ile hepsinin işlenmesini bekle (işçi her öğeden sonra `task_done()` demeli), sonra işçileri `cancel()` et.
```
:::
