---
id: p59
title: concurrent.futures
summary: Havuzlar, Future nesneleri, map, as_completed, hataların taşınması; iş parçacığı mı süreç mi?
---

::: anlat Havuza iş at, sonucu sonra al
P58'te iş parçacıklarını elle yönettik. `concurrent.futures` bunu tek satıra indirir: bir **havuz** (executor) oluşturursun, iş verirsin, karşılığında bir **Future** ("gelecekteki sonuç") alırsın.

```python
import time
from concurrent.futures import ThreadPoolExecutor

def kontrol(host):
    time.sleep(0.2)                                   #! ağ gecikmesini taklit
    return f"{host}: ok"

hostlar = [f"web{i:02d}" for i in range(8)]
bas = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as havuz:      #! with: çıkışta bütün işleri bekler
    sonuclar = list(havuz.map(kontrol, hostlar))     #! sıra KORUNUR
print(sonuclar[:2], f"{time.perf_counter() - bas:.2f} sn")

with ThreadPoolExecutor() as havuz:
    f = havuz.submit(pow, 2, 100)                     #! tek iş → Future
    print(f.done(), f.result())                       #! result() biter bitmez döner
```

| Yöntem | İş |
|---|---|
| `havuz.submit(f, *args)` | işi gönderir, `Future` döndürür |
| `havuz.map(f, dizi)` | her elemana f; sonuçlar **girdi sırasıyla** |
| `future.result(timeout=)` | sonucu bekler; iş hata verdiyse **o hatayı burada yükseltir** |
| `future.exception()` | hata nesnesi ya da None |
| `as_completed(futures)` | futures'ı **bitiş sırasıyla** verir |
| `wait(futures, timeout=, return_when=)` | biten/bekleyen kümeleri |

```python
import time, random
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_(n):
    time.sleep(0.05 * (5 - n))
    return n

with ThreadPoolExecutor() as havuz:
    gelecekler = {havuz.submit(is_, n): n for n in range(5)}
    for f in as_completed(gelecekler):                #! kim önce biterse
        print("bitti:", gelecekler[f])
```

> [!NOT]
> İşçi sayısı için kural: G/Ç işlerinde onlarca işçi makul (beklerken GIL serbest). CPU işlerinde çekirdek sayısını aşmanın yararı yok (`os.cpu_count()`).
:::

::: tahmin
İki satır:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as ex:
    print(list(ex.map(lambda x: x * 10, [1, 2, 3])))
    f = ex.submit(pow, 2, 10)
    print(f.result(), f.done())
```

???

`[10, 20, 30]`, sonra `1024 True`. `map` sonuçları girdi sırasıyla verir. `result()` işin bitmesini bekler; döndükten sonra `done()` doğrudur.
:::

::: anlat Hatalar, zaman aşımı ve süreç havuzu
Bir işçi hata verirse program çökmez: hata Future'ın içinde saklanır ve `result()` çağrıldığında **ana iş parçacığında** yeniden yükselir:

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import time

def riskli(x):
    if x == 0:
        raise ValueError("sıfır geçersiz")
    time.sleep(x)
    return x

with ThreadPoolExecutor() as havuz:
    f1 = havuz.submit(riskli, 0)
    f2 = havuz.submit(riskli, 2)
    try:
        f1.result()
    except ValueError as e:
        print("işçide hata:", e)
    try:
        f2.result(timeout=0.1)                         #! en fazla 0.1 sn bekle
    except FutureTimeout:
        print("zaman aşımı (iş arka planda sürüyor)")
```

> [!TUZAK]
> `result(timeout=...)` süresi dolunca sadece **beklemeyi** bırakır; iş parçacığı çalışmaya devam eder. Python'da çalışan bir iş parçacığını dışarıdan öldürmenin güvenli bir yolu yoktur. İptal edilebilir işler tasarlamak istiyorsan iş fonksiyonuna bir `threading.Event` ver ve onu düzenli kontrol ettir. asyncio'da (P60) iptal birinci sınıf bir kavramdır.

### ProcessPoolExecutor: GIL'in etrafından dolaşmak
CPU ağırlıklı işler için aynı arayüzün **süreç** versiyonu var: her işçi ayrı bir Python süreci, dolayısıyla ayrı bir GIL. Bedeli: argümanlar ve sonuçlar `pickle` ile süreçler arasında kopyalanır.

```python norun
from concurrent.futures import ProcessPoolExecutor

def asal_mi(n): ...

if __name__ == "__main__":            # Windows'ta ZORUNLU
    with ProcessPoolExecutor() as havuz:
        print(sum(havuz.map(asal_mi, range(10**6))))
```

> [!DERİN]
> Windows'ta (ve macOS'ta varsayılan olarak) yeni süreçler **spawn** yöntemiyle başlar: çocuk süreç ana modülü **yeniden import eder**. `if __name__ == "__main__":` koruması yoksa her çocuk yeniden havuz kurar ve sonsuz bir süreç patlaması olur (Python bunu bir hatayla durdurur). P31'daki koruma burada hayati hale gelir. Tezgah kodunu bir dosyadan değil bellekten çalıştırdığı için süreç havuzunu Tezgahta değil, gerçek bir `.py` dosyasında denemelisin.
:::

::: tahmin
Üç satır:

```python
from concurrent.futures import ThreadPoolExecutor

def bol(x):
    return 10 // x

with ThreadPoolExecutor() as ex:
    fs = [ex.submit(bol, x) for x in (5, 0, 2)]
    for f in fs:
        print(f.result() if f.exception() is None else type(f.exception()).__name__)
```

???

`2`, `ZeroDivisionError`, `5`. İkinci iş hata verdi ama diğerlerini etkilemedi; hata Future'da saklandı ve `exception()` ile okunabildi.
:::

::: gorev Sıralı paralel uygulama
`paralel_uygula(fonk, ogeler, isci=4)` fonksiyonu `ThreadPoolExecutor` ile `fonk`'u her öğeye uygulasın ve sonuçları **girdi sırasıyla** liste olarak döndürsün.

```starter
from concurrent.futures import ThreadPoolExecutor

def paralel_uygula(fonk, ogeler, isci=4):
    pass
```

```test
import time
need("paralel_uygula")
eq(paralel_uygula(str.upper, ["a", "b", "c"]), ["A", "B", "C"], "sıra korunur")
def yavas(x):
    time.sleep(0.2)
    return x * x
bas = time.perf_counter()
eq(paralel_uygula(yavas, list(range(8)), isci=8), [i * i for i in range(8)], "8 yavaş iş")
ok(time.perf_counter() - bas < 1.0, "8 × 0.2 sn paralel çalışmalı (< 1 sn)", got=round(time.perf_counter() - bas, 2))
ok(calls("ThreadPoolExecutor"), "ThreadPoolExecutor kullan")
```

```solution
from concurrent.futures import ThreadPoolExecutor

def paralel_uygula(fonk, ogeler, isci=4):
    with ThreadPoolExecutor(max_workers=isci) as havuz:
        return list(havuz.map(fonk, ogeler))
```

```hint
`with ThreadPoolExecutor(max_workers=isci) as havuz: return list(havuz.map(fonk, ogeler))`
```
:::

::: gorev Sağlık panosu
`saglik(kontroller, zaman_asimi)` fonksiyonu `{ad: fonksiyon}` sözlüğündeki argümansız kontrol fonksiyonlarını **aynı anda** çalıştırsın ve `{ad: durum}` döndürsün:

- fonksiyon zamanında döndüyse: `"ok"`
- hata verdiyse: `"hata: <TürAdı>"`
- toplam `zaman_asimi` saniye içinde bitmediyse: `"zaman aşımı"`

Fonksiyon, yavaş kontrolleri beklemeden yaklaşık `zaman_asimi` saniyede dönmeli.

```starter
from concurrent.futures import ThreadPoolExecutor, wait

def saglik(kontroller, zaman_asimi):
    pass
```

```meta
timeout: 15
```

```test
import time
need("saglik")
def hizli(): return True
def bozuk(): raise ConnectionRefusedError("kapalı")
def yavas(): time.sleep(2); return True
bas = time.perf_counter()
s = saglik({"web": hizli, "db": bozuk, "yedek": yavas}, 0.5)
gecen = time.perf_counter() - bas
eq(s, {"web": "ok", "db": "hata: ConnectionRefusedError", "yedek": "zaman aşımı"}, "durumlar")
ok(gecen < 1.5, "yavaş kontrolü beklemeden dönmeli", got=round(gecen, 2))
eq(saglik({}, 1), {}, "kontrol yok → {}")
```

```solution
from concurrent.futures import ThreadPoolExecutor, wait

def saglik(kontroller, zaman_asimi):
    havuz = ThreadPoolExecutor(max_workers=max(1, len(kontroller)))
    gelecekler = {ad: havuz.submit(f) for ad, f in kontroller.items()}
    wait(gelecekler.values(), timeout=zaman_asimi)
    durum = {}
    for ad, fut in gelecekler.items():
        if not fut.done():
            durum[ad] = "zaman aşımı"
        elif fut.exception() is not None:
            durum[ad] = f"hata: {type(fut.exception()).__name__}"
        else:
            durum[ad] = "ok"
    havuz.shutdown(wait=False, cancel_futures=True)
    return durum
```

```hint
`with` bloğu çıkışta bütün işleri beklediği için burada kullanma; havuzu elle oluştur ve sonunda `shutdown(wait=False)` çağır.
```

```hint
`wait(futures, timeout=...)` en fazla o kadar bekler; sonra her future için `done()` ve `exception()` kontrol et.
```
:::

::: gorev İlk başarılı yanıt
Aynı veriyi birden çok kaynaktan (yansı sunucularından) isteyip **ilk başarılı** yanıtı kullanmak yaygın bir dayanıklılık kalıbıdır. `ilk_basarili(fonksiyonlar)` argümansız fonksiyonları aynı anda çalıştırsın ve **ilk başarıyla biten**in sonucunu döndürsün. Hepsi hata verirse `RuntimeError("hepsi başarısız")` yükseltsin. `as_completed` kullan.

```starter
from concurrent.futures import ThreadPoolExecutor, as_completed

def ilk_basarili(fonksiyonlar):
    pass
```

```meta
timeout: 15
```

```test
import time
need("ilk_basarili")
def yavas(): time.sleep(0.6); return "yavaş yansı"
def hizli(): time.sleep(0.1); return "hızlı yansı"
def bozuk(): raise OSError("kapalı")
eq(ilk_basarili([yavas, bozuk, hizli]), "hızlı yansı", "en hızlı başarılı sonuç")
eq(ilk_basarili([bozuk, yavas]), "yavaş yansı", "hata verenler atlanır")
try:
    ilk_basarili([bozuk, bozuk])
    ok(False, "hepsi bozuksa RuntimeError")
except RuntimeError as e:
    eq(str(e), "hepsi başarısız", "mesaj")
ok(calls("as_completed"), "as_completed kullan")
```

```solution
from concurrent.futures import ThreadPoolExecutor, as_completed

def ilk_basarili(fonksiyonlar):
    havuz = ThreadPoolExecutor(max_workers=max(1, len(fonksiyonlar)))
    try:
        gelecekler = [havuz.submit(f) for f in fonksiyonlar]
        for fut in as_completed(gelecekler):
            if fut.exception() is None:
                return fut.result()
        raise RuntimeError("hepsi başarısız")
    finally:
        havuz.shutdown(wait=False, cancel_futures=True)
```

```hint
`for fut in as_completed(gelecekler):` bitiş sırasıyla gelir; ilk `exception() is None` olanın sonucunu döndür.
```
:::
