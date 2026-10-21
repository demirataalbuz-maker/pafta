---
id: cs01
title: Türler, Değer/Referans Ayrımı ve checked
summary: C# program yapısı, değer (struct) ve referans (class) türleri, tam sayı bölmesi ve checked/unchecked taşma davranışı.
---

::: anlat Bir C# programı, `var` ve temel türler
Kurumsal .NET web servislerini (ASP.NET Core) okurken kod ya klasik `namespace` + `class` + `Main` düzeniyle ya da C# 9+ **üst düzey deyimler** (*top-level statements*) biçiminde karşımıza çıkar.

Temel değer türleri (*value types*) bellekte doğrudan değerlerini taşır:
- **`int`:** 32-bit işaretli tam sayı (`-2_147_483_648` .. `2_147_483_647`)
- **`long`:** 64-bit işaretli tam sayı (`100L`)
- **`decimal`:** parasal ve hassas ondalık hesaplamalar (`19.99m`)
- **`bool`:** yalnızca `true` veya `false` (C#'ta `if (1)` veya `if ("metin")` derlenmez; koşul **kesinlikle** `bool` olmalıdır!)

```csharp
using System;

class SayfaHesabi
{
    static void Main()
    {
        int toplamKayit = 25;             #! 32-bit tam sayı
        int sayfaBoyutu = 10;
        var tamSayfa = toplamKayit / sayfaBoyutu;   #! var: derleyici türü sağ taraftan (int) çıkarır
        bool bosMu = toplamKayit == 0;    #! bool: çıktıda "True" veya "False" (baş harfi büyük!)

        Console.WriteLine(tamSayfa);      #! 2 (ondalık kısım kesilir)
        Console.WriteLine(bosMu);         #! False
    }
}
```

> [!TUZAK]
> Java ve JSON'un aksine C#'ta `bool.ToString()` ve `Console.WriteLine(bool)` çıktısı baş harfi büyük olarak **`True`** veya **`False`** üretir!
:::

::: anlat `struct` (değer) ve `class` (referans) farkı + `checked` / `unchecked`
C#'ı Java'dan ayıran iki kritik davranış vardır:

1. **`struct` değer kopyalar, `class` referans paylaşır:** Bir `struct` değişkenini başka bir değişkene atadığında (veya metoda gönderdiğinde) tüm alanlarının **bağımsız bir kopyası** oluşur; kopyayı değiştirmek asıl değişkeni etkilemez. `class` ise referans kopyalar; her iki değişken aynı nesneyi gösterir.
2. **Varsayılan `unchecked` taşma ve `checked` bloğu:** C#'ta `int` aritmetiği varsayılan olarak (`unchecked`) Java gibi 32-bit sınırında sessizce alt sınıra sarar (`int.MaxValue + 1 == int.MinValue`). Ancak işlem **`checked(...)`** içine alınırsa taşma anında **`OverflowException`** fırlatılır!

```csharp
using System;

struct NoktaDeger { public int X; }       #! struct -> değer türü (kopyalanır)
class NoktaRef    { public int X; }       #! class  -> referans türü (paylaşılır)

class TasmaOrnek
{
    static void Main()
    {
        var d1 = new NoktaDeger { X = 10 };
        var d2 = d1;                      #! tüm değer kopyalandı
        d2.X = 99;
        Console.WriteLine(d1.X);          #! 10 (d1 etkilenmedi!)

        var r1 = new NoktaRef { X = 10 };
        var r2 = r1;                      #! aynı nesneye referans
        r2.X = 99;
        Console.WriteLine(r1.X);          #! 99 (aynı nesne değişti)

        int tavan = int.MaxValue;
        int sessiz = unchecked(tavan + 1); #! -2147483648 (sessiz sarma)
        Console.WriteLine(sessiz);
    }
}
```

> [!GÜVENLİK]
> Bir API uç noktasında bakiye, kota veya dizin boyutu `int` ile toplanırken `checked` kullanılmamışsa, büyük bir pozitif sayı eklenerek toplam negatif sayıya (`< 0`) düşürülebilir ve üst sınır kontrolü atlatılabilir.
:::

::: tahmin
```csharp
using System;

struct SayacDeger { public int Adet; }
class SayacRef    { public int Adet; }

class Tahmin
{
    static void Main()
    {
        var s1 = new SayacDeger { Adet = 5 };
        var s2 = s1;
        s2.Adet += 10;

        var r1 = new SayacRef { Adet = 5 };
        var r2 = r1;
        r2.Adet += 10;

        Console.WriteLine(s1.Adet + ":" + r1.Adet);
        Console.WriteLine(17 / 5);
        Console.WriteLine(17 / 5 == 3);
        try
        {
            int x = int.MaxValue;
            int y = checked(x + 1);
            Console.WriteLine(y);
        }
        catch (OverflowException)
        {
            Console.WriteLine("TASMA_YAKALANDI");
        }
    }
}
```

```gercek
5:15
3
True
TASMA_YAKALANDI
```

???

`5:15`, `3`, `True`, `TASMA_YAKALANDI`. `SayacDeger` bir `struct` (değer türü) olduğu için `s2 = s1` bağımsız bir kopya oluşturur ve `s1.Adet` `5` kalır; `SayacRef` ise `class` (referans türü) olduğu için `r2.Adet += 10` işlemi `r1.Adet` değerini `15` yapar (`5:15`). `17 / 5` tam sayı bölmesiyle `3` verir. C#'ta `bool` ekrana yazdırılırken baş harfi büyük `True` olarak görünür. `checked(x + 1)` bloğu 32-bit taşmayı yakalayıp `OverflowException` fırlatır ve `TASMA_YAKALANDI` yazdırılır.
:::

::: gorev `checked` ve `unchecked` kota kontrolü
Aşağıdaki C# metodunun davranışını Python'da `kota_hesapla(mevcut, eklenen, sinir, denetimli_mi)` fonksiyonu olarak kur:
- `eklenen <= 0` ise `"GECERSIZ_MIKTAR"` döndür.
- `denetimli_mi` (`bool`) `True` ise `checked(mevcut + eklenen)` gibi davran: gerçek toplam 32-bit işaretli `int` aralığını (`-2_147_483_648 .. 2_147_483_647`) aşarsa `"TASMA_HATASI"` döndür.
- `denetimli_mi` `False` ise `unchecked(mevcut + eklenen)` gibi 32-bit işaretli tam sayıya sar.
- Sonuçta oluşan `yeni_toplam <= sinir` ise `f"KABUL:{yeni_toplam}"`, değilse `f"RED:{yeni_toplam}"` döndür.

```csharp
public static string KotaHesapla(int mevcut, int eklenen, int sinir, bool denetimliMi)
{
    if (eklenen <= 0)
        return "GECERSIZ_MIKTAR";
    try
    {
        int yeniToplam = denetimliMi
            ? checked(mevcut + eklenen)
            : unchecked(mevcut + eklenen);
        return yeniToplam <= sinir ? $"KABUL:{yeniToplam}" : $"RED:{yeniToplam}";
    }
    catch (OverflowException)
    {
        return "TASMA_HATASI";
    }
}
```

```starter
def kota_hesapla(mevcut, eklenen, sinir, denetimli_mi):
    toplam = mevcut + eklenen
    return f"KABUL:{toplam}"
```

```test
need("kota_hesapla")
eq(kota_hesapla(400, 600, 1000, True), "KABUL:1000", "tam sınırda (1000 <= 1000) kabul edilmeli")
eq(kota_hesapla(400, 601, 1000, True), "RED:1001", "sınırın 1 üstü reddedilmeli")
eq(kota_hesapla(400, 0, 1000, True), "GECERSIZ_MIKTAR", "eklenen 0 ise GECERSIZ_MIKTAR")
eq(kota_hesapla(400, -5, 1000, False), "GECERSIZ_MIKTAR", "negatif eklenen GECERSIZ_MIKTAR")
eq(kota_hesapla(2_147_483_646, 1, 2_147_483_647, True), "KABUL:2147483647", "int.MaxValue tam sınırda taşma yapmaz")
eq(kota_hesapla(2_147_483_647, 1, 1000, True), "TASMA_HATASI", "checked modda int.MaxValue + 1 TASMA_HATASI verir")
eq(kota_hesapla(2_147_483_647, 1, 1000, False), "KABUL:-2147483648", "unchecked modda int.MaxValue + 1 -2147483648'e sarar ve <= 1000 olur")
```

```solution
def _int32(n):
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n

def kota_hesapla(mevcut, eklenen, sinir, denetimli_mi):
    if eklenen <= 0:
        return "GECERSIZ_MIKTAR"
    ham = mevcut + eklenen
    if denetimli_mi and ham > 2_147_483_647:
        return "TASMA_HATASI"
    yeni_toplam = _int32(ham)
    return f"KABUL:{yeni_toplam}" if yeni_toplam <= sinir else f"RED:{yeni_toplam}"
```

```hint
`eklenen > 0` olduğunda `denetimli_mi` açıkken `mevcut + eklenen > 2_147_483_647` ise `"TASMA_HATASI"` döndür; kapalıyken 32-bit taşma formülünü uygula.
```
:::

::: gorev C# biçiminde sayfalama özeti (`bool` çıktısı)
Aşağıdaki C# metodunun döndürdüğü metni birebir üreten `sayfa_raporu(toplam_kayit, sayfa_boyutu, sayfa_no)` fonksiyonunu Python'da yaz. C#'ta `bool` değerinin metin içinde `"True"` veya `"False"` olarak biçimlendiğine dikkat et!

```csharp
public static string SayfaRaporu(int toplamKayit, int sayfaBoyutu, int sayfaNo)
{
    if (toplamKayit < 0 || sayfaBoyutu <= 0)
        return "HATALI_PARAMETRE";
    int toplamSayfa = toplamKayit == 0 ? 1 : (toplamKayit + sayfaBoyutu - 1) / sayfaBoyutu;
    bool varMi = sayfaNo >= 1 && sayfaNo <= toplamSayfa;
    return $"Sayfa={sayfaNo}/{toplamSayfa}|VarMi={varMi}";
}
```

```starter
def sayfa_raporu(toplam_kayit, sayfa_boyutu, sayfa_no):
    return f"Sayfa={sayfa_no}/1|VarMi=True"
```

```test
need("sayfa_raporu")
eq(sayfa_raporu(25, 10, 1), "Sayfa=1/3|VarMi=True", "25 kayıt, 10'luk sayfada 3 sayfa eder; alt sınır sayfaNo=1 geçerli")
eq(sayfa_raporu(20, 10, 2), "Sayfa=2/2|VarMi=True", "tam bölünen 20 kayıt -> 2 sayfa; üst sınır sayfaNo=2 geçerli")
eq(sayfa_raporu(20, 10, 3), "Sayfa=3/2|VarMi=False", "sayfaNo=3 (> 2) VarMi=False olmalı")
eq(sayfa_raporu(20, 10, 0), "Sayfa=0/2|VarMi=False", "sayfaNo=0 (< 1) VarMi=False olmalı")
eq(sayfa_raporu(0, 10, 1), "Sayfa=1/1|VarMi=True", "0 kayıtta toplamSayfa 1 olur")
eq(sayfa_raporu(-1, 10, 1), "HATALI_PARAMETRE", "negatif toplamKayit -> HATALI_PARAMETRE")
eq(sayfa_raporu(10, 0, 1), "HATALI_PARAMETRE", "sayfaBoyutu=0 -> HATALI_PARAMETRE")
```

```solution
def sayfa_raporu(toplam_kayit, sayfa_boyutu, sayfa_no):
    if toplam_kayit < 0 or sayfa_boyutu <= 0:
        return "HATALI_PARAMETRE"
    toplam_sayfa = 1 if toplam_kayit == 0 else (toplam_kayit + sayfa_boyutu - 1) // sayfa_boyutu
    var_mi = 1 <= sayfa_no <= toplam_sayfa
    return f"Sayfa={sayfa_no}/{toplam_sayfa}|VarMi={var_mi}"
```

```hint
Python'da `bool` zaten `"True"` ve `"False"` olarak metne çevrilir; bu açıdan C#'ın `$"...{varMi}"` davranışıyla birebir aynıdır!
```
:::
