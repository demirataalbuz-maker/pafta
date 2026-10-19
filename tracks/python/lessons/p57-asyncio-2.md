---
id: p57
title: asyncio II · Zaman Aşımı, Sınırlar, Akışlar
summary: wait_for ve timeout, iptal, Semaphore ile eşzamanlılık sınırı, to_thread ve yerel asenkron TCP sunucusu.
---

::: anlat Zaman aşımı ve iptal
Ağ dünyasında her bekleme bir gün **asılı kalır**. asyncio'da zaman aşımı ve iptal birinci sınıf kavramlardır:

```python
import asyncio

async def yavas_servis():
    try:
        await asyncio.sleep(5)
        return "yanıt"
    except asyncio.CancelledError:
        print("  iptal edildi, temizlik yapılıyor")
        raise                                     #! iptali YUTMA, yeniden yükselt

async def ana():
    try:
        await asyncio.wait_for(yavas_servis(), timeout=0.2)   #! süre dolunca görev iptal edilir
    except TimeoutError:
        print("wait_for: zaman aşımı")

    try:
        async with asyncio.timeout(0.2):          #! 3.11+: blok düzeyinde zaman aşımı
            await yavas_servis()
    except TimeoutError:
        print("timeout bloğu: zaman aşımı")

    gorev = asyncio.create_task(yavas_servis())
    await asyncio.sleep(0.1)
    gorev.cancel()                                #! elle iptal
    try:
        await gorev
    except asyncio.CancelledError:
        print("görev iptal durumunda:", gorev.cancelled())

asyncio.run(ana())
```

İptal, eşyordamın **o anki `await` noktasında** `CancelledError` yükseltilerek yapılır. Bu sayede `try/finally` ile temizlik yapabilirsin. Kural: `CancelledError`'ı yakalarsan mutlaka **yeniden yükselt**.

### Engelleyen kodu döngüden uzak tut
```python
import asyncio, time

def eski_kutuphane(x):                            #! senkron, engelleyen bir fonksiyon
    time.sleep(0.2)
    return x * 2

async def ana():
    sonuclar = await asyncio.gather(*(asyncio.to_thread(eski_kutuphane, i) for i in range(5)))
    print(sonuclar)                               #! ~0.2 sn: her çağrı ayrı iş parçacığında

asyncio.run(ana())
```
:::

::: tahmin
Ne yazdırır?

```python
import asyncio

async def yavas():
    await asyncio.sleep(1)
    return "geç"

async def ana():
    try:
        return await asyncio.wait_for(yavas(), timeout=0.1)
    except TimeoutError:
        return "zaman aşımı"

print(asyncio.run(ana()))
```

???

`zaman aşımı`. 0.1 saniye dolunca `wait_for` içteki görevi iptal eder ve `TimeoutError` yükseltir. (Python 3.11'den beri `asyncio.TimeoutError`, yerleşik `TimeoutError`'ın kendisidir.)
:::

::: anlat Semaphore ve asenkron akışlar
Binlerce eşyordamı aynı anda başlatmak kolaydır; ama karşı taraf (bir API, bir veritabanı, kendi dosya tanıtıcı sınırın) bunu kaldırmayabilir. **Semaphore** aynı anda en fazla N eşyordamın bir bölgeye girmesine izin verir:

```python
import asyncio

async def istek(sem, n):
    async with sem:                               #! en fazla 3 tanesi aynı anda içeride
        await asyncio.sleep(0.1)
        return n

async def ana():
    sem = asyncio.Semaphore(3)
    sonuclar = await asyncio.gather(*(istek(sem, n) for n in range(9)))
    print(sonuclar)                               #! 9 iş, 3'erli dalgalar: ~0.3 sn

asyncio.run(ana())
```

> [!GÜVENLİK]
> Eşzamanlılık sınırı **nezaket ve güvenlik** meselesidir: kendi izleme ya da envanter aracın, sorguladığı servisleri istemeden bir hizmet reddine (DoS) sokmamalı. Kurumsal API'lerin hız sınırları (rate limit) vardır ve aşınca hesabın kilitlenebilir. Profesyonel araçlar her zaman ayarlanabilir bir eşzamanlılık ve hız sınırı sunar.

### Asenkron TCP: streams
P51'deki soket kodunun asyncio versiyonu çok daha kısadır. Sunucu her bağlantı için bir eşyordam çalıştırır:

```python
import asyncio

async def isleyici(okuyucu, yazici):
    satir = await okuyucu.readline()              #! \n gelene kadar oku
    yazici.write(b"YANKI: " + satir)
    await yazici.drain()                          #! tampon boşalana kadar bekle
    yazici.close()
    await yazici.wait_closed()

async def ana():
    sunucu = await asyncio.start_server(isleyici, "127.0.0.1", 0)
    port = sunucu.sockets[0].getsockname()[1]
    async with sunucu:
        okuyucu, yazici = await asyncio.open_connection("127.0.0.1", port)
        yazici.write(b"merhaba\n")
        await yazici.drain()
        print(await okuyucu.readline())
        yazici.close()
        await yazici.wait_closed()

asyncio.run(ana())
```

> [!DERİN]
> `write()` veriyi hemen göndermez, bir tampona koyar; `drain()` ise tampon belli bir eşiği aşınca karşı tarafın okumasını bekleyerek **geri basınç** (backpressure) uygular. `drain`'i unutan bir sunucu, yavaş okuyan bir istemci yüzünden belleğini tüketebilir. Bu, asenkron sunucularda klasik bir kaynak tükenme hatasıdır.
:::

::: tahmin
Ne yazdırır?

```python
import asyncio

aktif = 0
tepe = 0

async def is_(sem):
    global aktif, tepe
    async with sem:
        aktif += 1
        tepe = max(tepe, aktif)
        await asyncio.sleep(0.01)
        aktif -= 1

async def ana():
    sem = asyncio.Semaphore(3)
    await asyncio.gather(*(is_(sem) for _ in range(10)))

asyncio.run(ana())
print(tepe)
```

???

`3`. 10 eşyordam başlasa da semafor aynı anda en fazla 3 tanesini içeri alır. Tek iş parçacığında çalıştığımız için `aktif += 1` burada bir yarış durumu yaratmaz: eşyordamlar sadece `await` noktalarında yer değiştirir.
:::

::: gorev Sınırlı eşzamanlılık
`async def sinirli(gecikmeler, limit)` her gecikme için `asyncio.sleep(g)` yapan bir iş çalıştırsın ama aynı anda **en fazla `limit`** iş çalışsın (`asyncio.Semaphore`). Fonksiyon `(sonuclar, tepe)` demeti döndürsün: `sonuclar` gecikmelerin girdi sırasıyla listesi, `tepe` ise aynı anda çalışan en yüksek iş sayısı.

```starter
import asyncio

async def sinirli(gecikmeler, limit):
    pass
```

```test
import asyncio, time
need("sinirli")
bas = time.perf_counter()
sonuclar, tepe = asyncio.run(sinirli([0.1] * 9, 3))
gecen = time.perf_counter() - bas
eq(sonuclar, [0.1] * 9, "sonuçlar")
eq(tepe, 3, "aynı anda en fazla 3")
ok(0.25 <= gecen < 0.8, "3'erli dalgalar: ~0.3 sn", got=round(gecen, 2))
eq(asyncio.run(sinirli([0.05, 0.01], 5))[1], 2, "iş sayısı limitten azsa tepe = iş sayısı")
ok(calls("Semaphore"), "asyncio.Semaphore kullan")
```

```solution
import asyncio

async def sinirli(gecikmeler, limit):
    sem = asyncio.Semaphore(limit)
    durum = {"aktif": 0, "tepe": 0}

    async def is_(g):
        async with sem:
            durum["aktif"] += 1
            durum["tepe"] = max(durum["tepe"], durum["aktif"])
            await asyncio.sleep(g)
            durum["aktif"] -= 1
            return g

    sonuclar = await asyncio.gather(*(is_(g) for g in gecikmeler))
    return list(sonuclar), durum["tepe"]
```

```hint
Sayaçları bir sözlükte tut (iç fonksiyondan değiştirmek için `nonlocal` gerekmesin). `async with sem:` bloğunun girişinde artır, çıkışında azalt.
```
:::

::: gorev Asenkron yankı sunucusu
`async def yanki(okuyucu, yazici)` bir `asyncio.start_server` işleyicisi olsun: istemci bağlantıyı kapatana kadar **satır satır** okusun ve her satır için `YANKI: <satır>` gönderip `drain` etsin. Boş satır (sadece `\n`) gelirse `BOŞ\n` göndersin. Sonunda bağlantıyı kapatsın.

```starter
import asyncio

async def yanki(okuyucu, yazici):
    pass
```

```meta
timeout: 15
```

```test
import asyncio
need("yanki")
async def dene():
    sunucu = await asyncio.start_server(yanki, "127.0.0.1", 0)
    port = sunucu.sockets[0].getsockname()[1]
    async with sunucu:
        r, w = await asyncio.open_connection("127.0.0.1", port)
        w.write("merhaba\n\nikinci satır\n".encode())
        await w.drain()
        w.write_eof()
        veri = await asyncio.wait_for(r.read(), timeout=3)
        w.close()
        await w.wait_closed()
        return veri.decode()
eq(asyncio.run(dene()), "YANKI: merhaba\nBOŞ\nYANKI: ikinci satır\n", "üç satırlık konuşma")
```

```solution
import asyncio

async def yanki(okuyucu, yazici):
    try:
        while True:
            satir = await okuyucu.readline()
            if not satir:
                break
            if satir.strip() == b"":
                yazici.write("BOŞ\n".encode())
            else:
                yazici.write(b"YANKI: " + satir)
            await yazici.drain()
    finally:
        yazici.close()
        await yazici.wait_closed()
```

```hint
`readline()` bağlantı kapanınca boş bayt (`b""`) döndürür; döngüyü orada bitir. Sadece `\n` olan satır boş değildir ama `strip()` sonrası boştur.
```
:::

::: gorev Zaman aşımlı toplu bekleme
`async def toplu(gorevler, sure)` `{ad: eşyordam}` sözlüğündeki eşyordamları **aynı anda** çalıştırsın; her biri için `sure` saniyelik zaman aşımı uygulasın. `{ad: sonuç}` döndürsün; zaman aşımına uğrayanlar için sonuç `"zaman aşımı"`, hata verenler için `"hata: <TürAdı>"` olsun.

```starter
import asyncio

async def toplu(gorevler, sure):
    pass
```

```test
import asyncio, time
need("toplu")
async def bekle(s, deger):
    await asyncio.sleep(s)
    return deger
async def patla():
    await asyncio.sleep(0.01)
    raise ConnectionResetError()
bas = time.perf_counter()
s = asyncio.run(toplu({"a": bekle(0.05, 1), "b": bekle(3, 2), "c": patla()}, 0.3))
eq(s, {"a": 1, "b": "zaman aşımı", "c": "hata: ConnectionResetError"}, "sonuçlar")
ok(time.perf_counter() - bas < 1.0, "yavaş görevi beklemeden dönmeli", got=round(time.perf_counter() - bas, 2))
eq(asyncio.run(toplu({}, 1)), {}, "boş")
```

```solution
import asyncio

async def toplu(gorevler, sure):
    async def tek(e):
        try:
            return await asyncio.wait_for(e, timeout=sure)
        except TimeoutError:
            return "zaman aşımı"
        except Exception as hata:
            return f"hata: {type(hata).__name__}"

    adlar = list(gorevler)
    sonuclar = await asyncio.gather(*(tek(gorevler[a]) for a in adlar))
    return dict(zip(adlar, sonuclar))
```

```hint
Her eşyordamı zaman aşımı ve hata yakalama yapan küçük bir sarmalayıcıyla sar, sonra hepsini `gather` ile çalıştır.
```
:::
