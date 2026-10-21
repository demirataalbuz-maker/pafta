---
id: cs03
title: Null Güvenliği · ?, ?., ??, ??= ve int?
summary: Değer ve referans türlerinde nullable (?), null-conditional (?.), null-coalescing (?? ve ??=) ve IsNullOrWhiteSpace.
---

::: anlat Değer türlerinde `int?` (`Nullable<T>`) ve referans türlerinde `string?`
C#'ta değer türleri (`int`, `bool`, `DateTime`) normalde `null` alamaz. Bir veritabanı sütunu veya isteğin isteğe bağlı sayısal parametresi boş gelebiliyorsa türün sonuna `?` eklenir (`int?`, yani `Nullable<int>`):
- **`sayi.HasValue`:** değer var mı (`true` / `false`)?
- **`sayi.Value`:** değeri döndürür (`null` ise **`InvalidOperationException`** fırlatır!).
- **`sayi.GetValueOrDefault(varsayilan)`:** `null` ise varsayılan değeri döndürür.

C# 8+ ile birlikte referans türlerinde de (`string?`, `Kullanici?`) `?` işareti derleyiciye bu referansın `null` olabileceğini bildirir.

```csharp
using System;

class NullableOrnek
{
    static void Main()
    {
        int? limit = null;
        Console.WriteLine(limit.HasValue);              #! False
        Console.WriteLine(limit.GetValueOrDefault(25)); #! 25

        limit = 0;                                      #! 0 geçerli bir değerdir, null değildir!
        Console.WriteLine(limit.HasValue);              #! True
    }
}
```
:::

::: anlat `?.`, `?[]`, `??`, `??=` ve `IsNullOrWhiteSpace`
Modern C# kodunda `if (x != null)` blokları yerine dört işleç yoğun biçimde kullanılır:
- **`nesne?.Ozellik` / `dizi?[0]` (Null-conditional):** Sol taraf `null` ise sağ tarafı hiç çalıştırmaz (kısa devre yapar) ve ifadenin tamamı `null` üretir.
- **`sol ?? sag` (Null-coalescing):** `sol` yalnızca **`null`** ise `sag` değerini döndürür (`0`, `false` veya `""` `null` değildir; Python'daki `or` ile karıştırma!).
- **`degisken ??= varsayilan`:** `degisken` `null` ise ona `varsayilan` değerini atar.
- **`string.IsNullOrWhiteSpace(s)`:** `s` hem `null`, hem `""`, hem de `"   "` olduğunda `true` döner.

```csharp
using System;

class NullIslecler
{
    static void Main()
    {
        string? baslik = null;
        int? uzunluk = baslik?.Trim().Length;     #! baslik null -> kısa devre, uzunluk = null
        Console.WriteLine(uzunluk ?? -1);         #! -1

        int? sayfa = 0;
        Console.WriteLine(sayfa ?? 1);            #! 0! (0 null değildir; ?? yalnızca null yakalar)

        string? ortam = "   ";
        Console.WriteLine(ortam ?? "uretim");     #! "   " (boşluk metni null değildir!)
        Console.WriteLine(string.IsNullOrWhiteSpace(ortam) ? "uretim" : ortam.Trim()); #! uretim
    }
}
```

> [!TUZAK]
> Python veya JavaScript'teki `x or varsayilan` alışkanlığıyla C#'taki `x ?? varsayilan` ifadesini aynı sanma! C#'ta `"" ?? "varsayilan"` ifadesi **`""`** (boş metin) döndürür; çünkü `""` `null` değildir!
:::

::: tahmin
```csharp
using System;

class Istek
{
    public string? Kullanici { get; set; }
    public int? Sayfa { get; set; }
}

class Tahmin
{
    static void Main()
    {
        var i1 = new Istek { Kullanici = "  ", Sayfa = 0 };
        var i2 = new Istek { Kullanici = null, Sayfa = null };

        string k1 = i1.Kullanici?.Trim() ?? "misafir";
        string k2 = i2.Kullanici?.Trim() ?? "misafir";

        Console.WriteLine(k1 == "");
        Console.WriteLine(k2);
        Console.WriteLine((i1.Sayfa ?? 10) + ":" + (i2.Sayfa ?? 10));
        Console.WriteLine(string.IsNullOrWhiteSpace(i1.Kullanici));
    }
}
```

```gercek
True
misafir
0:10
True
```

???

`True`, `misafir`, `0:10`, `True`. `i1.Kullanici` `"  "` olduğu için `null` değildir; `?.Trim()` çalışır ve `""` (boş metin) üretir. Boş metin `null` olmadığı için `?? "misafir"` devreye girmez ve `k1` `""` olur (`k1 == ""` → `True`). `i2.Kullanici` ise `null` olduğundan `?.Trim()` sonucu `null` kalır ve `?? "misafir"` çalışarak `misafir` verir. `i1.Sayfa` `0` olduğu için `?? 10` onu değiştirmez (`0`), `i2.Sayfa` `null` olduğu için `10` olur (`0:10`). `string.IsNullOrWhiteSpace("  ")` ise `True` döndürür.
:::

::: gorev `?.` ve `??` zincirini doğru yorumlamak
Aşağıdaki C# metodunun davranışını Python'da `oturum_ozeti(kullanici_adi, rol, deneme_sayisi)` fonksiyonu olarak birebir kur. C#'ta `""` ve `0` değerlerinin `null` (`None`) olmadığına ve `??` işlecinin yalnızca `null` üzerinde devreye girdiğine dikkat et!

```csharp
public static string OturumOzeti(string? kullaniciAdi, string? rol, int? denemeSayisi)
{
    string ad = string.IsNullOrWhiteSpace(kullaniciAdi)
        ? "anonim"
        : kullaniciAdi.Trim().ToLowerInvariant();
    string temizRol = rol?.Trim() ?? "izleyici";
    int deneme = denemeSayisi ?? 1;
    return $"{ad}|{temizRol}|{deneme}";
}
```

```starter
def oturum_ozeti(kullanici_adi, rol, deneme_sayisi):
    return f"{kullanici_adi or 'anonim'}|{rol or 'izleyici'}|{deneme_sayisi or 1}"
```

```test
need("oturum_ozeti")
eq(oturum_ozeti("  Ayse ", " Admin ", 0), "ayse|Admin|0", "deneme_sayisi=0 null değildir, ?? 1 devreye girmez (0 kalmalı)")
eq(oturum_ozeti("   ", "   ", None), "anonim||1", "rol='   ' null olmadığı için rol?.Trim() boş metin '' üretir ve ?? 'izleyici' çalışmaz!")
eq(oturum_ozeti(None, None, None), "anonim|izleyici|1", "hepsi None olduğunda varsayılanlar devreye girer")
eq(oturum_ozeti("", "operator", 3), "anonim|operator|3", "boş kullanıcı adı IsNullOrWhiteSpace ile anonim olur")
```

```solution
def oturum_ozeti(kullanici_adi, rol, deneme_sayisi):
    if kullanici_adi is None or not kullanici_adi.strip():
        ad = "anonim"
    else:
        ad = kullanici_adi.strip().lower()
    temiz_rol = "izleyici" if rol is None else rol.strip()
    deneme = 1 if deneme_sayisi is None else deneme_sayisi
    return f"{ad}|{temiz_rol}|{deneme}"
```

```hint
Python'da `rol or "izleyici"` veya `deneme_sayisi or 1` yazarsan `""` ve `0` değerlerini de değiştirirsin; oysa C#'taki `??` yalnızca `is None` durumunda varsayılana geçer!
```
:::

::: gorev `int?` aralık doğrulayıcı
Aşağıdaki C# metodu isteğe bağlı (`int?`) alt ve üst fiyat sınırlarını doğruluyor. Aynı davranışı Python'da `aralik_dogrula(alt_sinir, ust_sinir)` fonksiyonu olarak kur.

```csharp
public static string AralikDogrula(int? altSinir, int? ustSinir)
{
    int alt = altSinir ?? 0;
    int ust = ustSinir ?? 1000;
    if (alt < 0 || ust > 10000)
        return "SINIR_DISI";
    if (alt > ust)
        return "TERS_ARALIK";
    return $"GEÇERLİ:{alt}..{ust}";
}
```

```starter
def aralik_dogrula(alt_sinir, ust_sinir):
    return f"GEÇERLİ:{alt_sinir}..{ust_sinir}"
```

```test
need("aralik_dogrula")
eq(aralik_dogrula(None, None), "GEÇERLİ:0..1000", "her ikisi None ise 0..1000")
eq(aralik_dogrula(0, 10000), "GEÇERLİ:0..10000", "alt=0 ve ust=10000 tam sınırda geçerli")
eq(aralik_dogrula(250, 250), "GEÇERLİ:250..250", "alt == ust geçerli")
eq(aralik_dogrula(-1, 500), "SINIR_DISI", "alt=-1 (< 0) -> SINIR_DISI")
eq(aralik_dogrula(0, 10001), "SINIR_DISI", "ust=10001 (> 10000) -> SINIR_DISI")
eq(aralik_dogrula(501, 500), "TERS_ARALIK", "alt > ust -> TERS_ARALIK")
```

```solution
def aralik_dogrula(alt_sinir, ust_sinir):
    alt = 0 if alt_sinir is None else alt_sinir
    ust = 1000 if ust_sinir is None else ust_sinir
    if alt < 0 or ust > 10000:
        return "SINIR_DISI"
    if alt > ust:
        return "TERS_ARALIK"
    return f"GEÇERLİ:{alt}..{ust}"
```

```hint
`alt_sinir is None` ise `0`, `ust_sinir is None` ise `1000` ata; ardından `alt < 0 or ust > 10000` ve `alt > ust` sınırlarını kontrol et.
```
:::
