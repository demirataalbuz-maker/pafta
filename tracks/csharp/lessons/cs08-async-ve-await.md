---
id: cs08
title: Eşzamansız Kod · Task<T>, async/await ve WhenAll
summary: C# Task ve Task<T>, async/await yürütme sırası, Task.WhenAll ve try/catch içinde unutulan await tuzağı.
---

::: anlat `Task<T>` ve `async` / `await` yürütme sırası
ASP.NET Core denetleyicilerinin ve veritabanı sorgularının neredeyse tamamı **`async Task<IActionResult>`** biçiminde eşzamansız (*asynchronous*) yazılır:
- Bir `async` metot çağrıldığında, ilk gerçek beklemeye (`await` edilen tamamlanmamış bir `Task`'e) gelene kadar **senkron olarak** (çağıran iş parçacığında) adım adım çalışır.
- `Task.FromResult(deger)` zaten tamamlanmış bir görev döndürür.
- Birden fazla bağımsız görev **`await Task.WhenAll(g1, g2)`** ile paralel beklenir ve sonuçları görevlerin verildiği sırayla dizi olarak döner.

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

class AsyncSira
{
    static async Task<int> VeriGetirAsync(List<string> iz)
    {
        iz.Add("B:Basladi");
        await Task.Delay(10);                     #! kontrol çağıran metoda döner
        iz.Add("D:Tamamlandi");
        return 42;
    }

    static async Task Main()
    {
        var iz = new List<string>();
        iz.Add("A:CagriOncesi");
        Task<int> gorev = VeriGetirAsync(iz);     #! B:Basladi hemen çalışır!
        iz.Add("C:AwaitOncesi");
        int sonuc = await gorev;                  #! D:Tamamlandi beklenir
        iz.Add("E:Sonuc=" + sonuc);
        Console.WriteLine(string.Join(" -> ", iz));
    }
}
```
:::

::: anlat `try` / `catch` içinde `await` unutma tuzağı!
Bir metot `Task` veya `Task<T>` döndürürken `try { return TehlikeliIslemAsync(); } catch { ... }` şeklinde **`await` yazmadan** doğrudan `Task` döndürürse, görev henüz tamamlanmadan `try` bloğundan çıkılır! Görev içinde sonradan fırlatılan istisna bu `catch` bloğuna **yakalanmaz**, doğrudan çağıran tarafa fırlar!

```csharp
using System;
using System.Threading.Tasks;

class AwaitTuzagi
{
    static async Task<string> HataFirlatAsync()
    {
        await Task.Yield();
        throw new InvalidOperationException("DB_KOPTU");
    }

    // KUSURLU: async/await yok, Task doğrudan döndürülüyor -> catch çalışmaz!
    static Task<string> KusurluSarmalayici()
    {
        try
        {
            return HataFirlatAsync();
        }
        catch (Exception)
        {
            return Task.FromResult("YEDEK_DEGER");
        }
    }

    // DOĞRU: await ile bekleniyor -> catch istisnayı yakalar!
    static async Task<string> DogruSarmalayiciAsync()
    {
        try
        {
            return await HataFirlatAsync();
        }
        catch (Exception)
        {
            return "YEDEK_DEGER";
        }
    }
}
```

> [!TUZAK]
> Benzer şekilde `using var baglanti = new SqlConnection(...); return SorguAsync(baglanti);` yazıldığında `await` unutulursa, `SorguAsync` henüz çalışırken `using` bloğu biter ve veritabanı bağlantısı erken kapatılır (`ObjectDisposedException`)!
:::

::: tahmin
```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

class Tahmin
{
    static async Task<string> ServisCagirAsync(string ad, List<string> iz)
    {
        iz.Add("1:" + ad);
        await Task.Yield();
        if (ad == "bozuk")
            throw new InvalidOperationException("HATA");
        iz.Add("3:" + ad);
        return ad.ToUpperInvariant();
    }

    static async Task<string> GuvenliCagirAsync(string ad, List<string> iz)
    {
        try
        {
            Task<string> t = ServisCagirAsync(ad, iz);
            iz.Add("2:bekleniyor");
            return await t;
        }
        catch (InvalidOperationException)
        {
            iz.Add("3:yakalandi");
            return "YEDEK";
        }
    }

    static async Task Main()
    {
        var iz1 = new List<string>();
        string s1 = await GuvenliCagirAsync("ok", iz1);
        Console.WriteLine(s1 + " | " + string.Join(",", iz1));

        var iz2 = new List<string>();
        string s2 = await GuvenliCagirAsync("bozuk", iz2);
        Console.WriteLine(s2 + " | " + string.Join(",", iz2));
    }
}
```

```gercek
OK | 1:ok,2:bekleniyor,3:ok
YEDEK | 1:bozuk,2:bekleniyor,3:yakalandi
```

???

`OK | 1:ok,2:bekleniyor,3:ok` ve `YEDEK | 1:bozuk,2:bekleniyor,3:yakalandi`. `ServisCagirAsync` çağrıldığında ilk `await Task.Yield()` satırına kadar senkron çalışır ve `"1:" + ad` kaydını hemen ekler. Ardından kontrol `GuvenliCagirAsync` metoduna döner, `"2:bekleniyor"` eklenir ve `await t` ile görevin kalanı çalıştırılır. `"ok"` için `"3:ok"` eklenip `"OK"` döner; `"bozuk"` için `InvalidOperationException` fırlatılır, `await` kullanıldığı için `catch` bloğu hatayı yakalar, `"3:yakalandi"` ekler ve `"YEDEK"` döndürür.
:::

::: gorev `async`/`await` iz sırası ve `await` unutma tuzağını simüle et
Aşağıdaki iki C# metodundan `BekleyerekCagirAsync` görevi `await` ile beklerken, `BeklemedenCagir` `await` kullanmadan doğrudan `Task` döndürüyor. Python'da `cagri_simule_et(servis_adi, hata_var_mi, await_kullanildi_mi)` fonksiyonunu yaz ve `(sonuc_veya_hata, iz_listesi)` demetini döndür:
- Çağrı başladığında `iz` listesine önce `f"BASLA:{servis_adi}"` eklenir (`await` satırından önceki senkron kısım).
- Ardından çağıran metotta `await` öncesi `"CAGIRAN:DEVAM"` izi eklenir.
- Görev tamamlanırken:
  - `hata_var_mi == False` ise `iz` listesine `f"BITTI:{servis_adi}"` eklenir ve sonuç `f"200:{servis_adi.upper()}"` olur.
  - `hata_var_mi == True` ve `await_kullanildi_mi == True` ise `try/catch` hatayı yakalar, `iz` listesine `"YAKALANDI"` eklenir ve sonuç `"503:YEDEK"` olur.
  - `hata_var_mi == True` ve `await_kullanildi_mi == False` ise `try/catch` bloktan erken çıktığı için hatayı **yakalayamaz**, `iz` listesine `"YAKALANAMADI"` eklenir ve sonuç `"FIRLATILDI:InvalidOperationException"` olur.

```starter
def cagri_simule_et(servis_adi, hata_var_mi, await_kullanildi_mi):
    return f"200:{servis_adi.upper()}", []
```

```test
need("cagri_simule_et")
eq(cagri_simule_et("odeme", False, True),
   ("200:ODEME", ["BASLA:odeme", "CAGIRAN:DEVAM", "BITTI:odeme"]),
   "hatasız çağrıda iz sırası BASLA -> CAGIRAN:DEVAM -> BITTI olmalı")
eq(cagri_simule_et("odeme", False, False),
   ("200:ODEME", ["BASLA:odeme", "CAGIRAN:DEVAM", "BITTI:odeme"]),
   "hatasız çağrıda await olmasa da Task sonunda 200:ODEME üretir")
eq(cagri_simule_et("stok", True, True),
   ("503:YEDEK", ["BASLA:stok", "CAGIRAN:DEVAM", "YAKALANDI"]),
   "hata varken await kullanıldıysa catch bloğu çalışır -> 503:YEDEK")
eq(cagri_simule_et("stok", True, False),
   ("FIRLATILDI:InvalidOperationException", ["BASLA:stok", "CAGIRAN:DEVAM", "YAKALANAMADI"]),
   "hata varken await unutulduysa catch bloğu hatayı kaçırır")
```

```solution
def cagri_simule_et(servis_adi, hata_var_mi, await_kullanildi_mi):
    iz = [f"BASLA:{servis_adi}", "CAGIRAN:DEVAM"]
    if not hata_var_mi:
        iz.append(f"BITTI:{servis_adi}")
        return f"200:{servis_adi.upper()}", iz
    if await_kullanildi_mi:
        iz.append("YAKALANDI")
        return "503:YEDEK", iz
    iz.append("YAKALANAMADI")
    return "FIRLATILDI:InvalidOperationException", iz
```

```hint
İki boolean durumunu (`hata_var_mi` ve `await_kullanildi_mi`) sırayla kontrol et; `BASLA:{servis_adi}` ve `CAGIRAN:DEVAM` her durumda ilk iki iz kaydıdır.
```
:::

::: gorev `Task.WhenAll` ve zaman aşımı (`CancellationToken`) toplayıcı
Bir ASP.NET Core sağlık kontrolü uç noktası birden fazla alt servisi `Task.WhenAll` ile paralel sorguluyor ve `zaman_asimi_ms` süresini aşanları `"ZAMAN_ASIMI"` olarak işaretliyor. Python'da `saglik_topla(servisler, zaman_asimi_ms)` fonksiyonunu yaz:
- `servisler`, `[{"ad": str, "sure_ms": int, "durum": int}, ...]` listesidir.
- Verilen sıra korunarak her servis için:
  - `sure_ms > zaman_asimi_ms` ise `f"{ad}:ZAMAN_ASIMI"`
  - `sure_ms <= zaman_asimi_ms` ve `200 <= durum < 300` ise `f"{ad}:OK"`
  - Diğer durumlarda `f"{ad}:HATA:{durum}"` üretilir.
- Tüm servisler `"OK"` ise `("SAGLIKLI", sonuc_listesi)`, en az biri `"OK"` değilse `("BOZUK", sonuc_listesi)` döndür (servis listesi boşsa `("BOS", [])`).

```starter
def saglik_topla(servisler, zaman_asimi_ms):
    return "SAGLIKLI", []
```

```test
need("saglik_topla")
eq(saglik_topla([], 500), ("BOS", []), "boş servis listesi -> ('BOS', [])")
eq(saglik_topla([
    {"ad": "db", "sure_ms": 500, "durum": 200},
    {"ad": "önbellek", "sure_ms": 100, "durum": 299},
], 500), ("SAGLIKLI", ["db:OK", "önbellek:OK"]), "tam zaman aşımı sınırında (500 <= 500) ve 200..299 aralığında SAGLIKLI")
eq(saglik_topla([
    {"ad": "db", "sure_ms": 501, "durum": 200},
    {"ad": "arama", "sure_ms": 200, "durum": 300},
    {"ad": "kuyruk", "sure_ms": 50, "durum": 199},
], 500), ("BOZUK", ["db:ZAMAN_ASIMI", "arama:HATA:300", "kuyruk:HATA:199"]), "501 ms zaman aşımı, 300 ve 199 durum kodları HATA vermeli")
```

```solution
def saglik_topla(servisler, zaman_asimi_ms):
    if not servisler:
        return "BOS", []
    rapor = []
    hepsi_ok = True
    for s in servisler:
        ad = s["ad"]
        sure = s["sure_ms"]
        durum = s["durum"]
        if sure > zaman_asimi_ms:
            rapor.append(f"{ad}:ZAMAN_ASIMI")
            hepsi_ok = False
        elif 200 <= durum < 300:
            rapor.append(f"{ad}:OK")
        else:
            rapor.append(f"{ad}:HATA:{durum}")
            hepsi_ok = False
    return ("SAGLIKLI" if hepsi_ok else "BOZUK"), rapor
```

```hint
`sure > zaman_asimi_ms` kontrolünü önce yap; sınır değeri `sure == zaman_asimi_ms` zaman aşımı sayılmaz. Durum kodunda ise `200 <= durum < 300` aralığı başarılıdır.
```
:::
