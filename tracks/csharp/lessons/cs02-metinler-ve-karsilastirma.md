---
id: cs02
title: Metinler · string, == ve StringComparison
summary: C#'ta string == değer eşitliği, Substring(başlangıç, uzunluk) farkı, StringComparison ve StringSplitOptions.
---

::: anlat C#'ta `string ==` değer karşılaştırır!
Java'dan C#'a geçen bir kod okuyucunun bilmesi gereken ilk fark şudur:
- **Java'da** `str1 == str2` referans (bellek adresi) karşılaştırır.
- **C#'ta** `string` türü için `==` ve `!=` işleçleri aşırı yüklenmiştir (*operator overloading*) ve karakterleri **değer olarak** (ordinal, büyük-küçük harfe duyarlı) karşılaştırır!

Büyük-küçük harf duyarsız karşılaştırma için ise `string.Equals(a, b, StringComparison.OrdinalIgnoreCase)` veya `a.StartsWith(b, StringComparison.OrdinalIgnoreCase)` kullanılır.

```csharp
using System;

class MetinEsitlik
{
    static void Main()
    {
        string a = "pafta";
        string b = new string("pafta".ToCharArray());   #! yeni nesne

        Console.WriteLine(a == b);                      #! True! (C#'ta == değer karşılaştırır)
        Console.WriteLine(object.ReferenceEquals(a, b));#! False (referansları farklı)
        Console.WriteLine(a.Equals("PAFTA", StringComparison.OrdinalIgnoreCase)); #! True
    }
}
```

> [!NOT]
> C#'ta iki tür özel metin yazımı sık görülür:
> - **`$"Kullanıcı: {ad}"`:** metin enterpolasyonu (Python'daki `f"..."` gibi).
> - **`@"C:\rapor\gunluk.txt"`:** kaçışsız (*verbatim*) metin; ters eğik çizgi `\` kaçış dizisi sayılmaz.
:::

::: anlat `Substring(başlangıç, uzunluk)` ve `Split` seçenekleri
Java veya Python okuyanların C# kodunda en sık düştüğü tuzak **`Substring`** metodunun ikinci parametresidir:
- **Java'da** `s.substring(2, 5)` → indeks `2`'den indeks `5`'e kadar (`3` karakter) alır.
- **C#'ta** `s.Substring(2, 5)` → indeks `2`'den başlayarak **5 karakter uzunluğunda** (`s[2..7]`) parça alır!

`Split` metodunda ise `StringSplitOptions` bayrakları davranışı belirler:
- **`StringSplitOptions.None`** (varsayılan): boş parçaları korur.
- **`StringSplitOptions.RemoveEmptyEntries`**: boş parçaları atar.
- **`StringSplitOptions.TrimEntries`** (.NET 5+): her parçanın kenar boşluklarını kırpar.

```csharp
using System;

class Parcalama
{
    static void Main()
    {
        string yol = "/api/v2/biletler";
        Console.WriteLine(yol.Substring(1, 3));   #! "api" (indeks 1'den itibaren 3 karakter!)
        Console.WriteLine(yol.Substring(8));      #! "biletler" (indeks 8'den sona kadar)

        string ham = "  oku , yaz , , sil ";
        string[] temiz = ham.Split(',',
            StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        Console.WriteLine(temiz.Length);          #! 3 ("oku", "yaz", "sil")
        Console.WriteLine(string.Join("|", temiz)); #! oku|yaz|sil
    }
}
```
:::

::: tahmin
```csharp
using System;

class Tahmin
{
    static void Main()
    {
        string k1 = "admin";
        string k2 = new string("admin".ToCharArray());
        Console.WriteLine(k1 == k2);

        string rota = "/servis/v1/durum";
        Console.WriteLine(rota.Substring(8, 2));

        string giris = " web01 ; ; db01 ;   ; app01 ";
        string[] sunucular = giris.Split(';',
            StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        Console.WriteLine(sunucular.Length);
        Console.WriteLine(string.Join(",", sunucular));
    }
}
```

```gercek
True
v1
3
web01,db01,app01
```

???

`True`, `v1`, `3`, `web01,db01,app01`. C#'ta `string ==` işleci referans değil karakter değeri karşılaştırdığı için `k1 == k2` sonucu `True` olur. `rota.Substring(8, 2)` indeks `8`'den başlayarak **2 karakter** (`"v1"`) alır. `Split` çağrısında `TrimEntries` önce her parçanın boşluklarını kırpar (böylece `"   "` parçası da boş metne dönüşür), `RemoveEmptyEntries` ise boş parçaları eler; geriye `3` eleman (`web01,db01,app01`) kalır.
:::

::: gorev C# `Substring(baslangic, uzunluk)` ile sabit genişlikli kayıt okuyucu
Aşağıdaki C# metodu 12 karakterlik sabit genişlikli bir sistem kodunu `Substring(baslangic, uzunluk)` ile üç parçaya (`bolge`, `ortam`, `numara`) ayırıyor. Aynı davranışı Python'da `kayit_coz(kod)` fonksiyonu olarak kur.

```csharp
public static string KayitCoz(string kod)
{
    if (kod == null)
        return "GECERSIZ";
    string temiz = kod.Trim();
    if (temiz.Length != 12)
        return "GECERSIZ";
    string bolge = temiz.Substring(0, 3).ToUpperInvariant();
    string ortam = temiz.Substring(3, 4).ToLowerInvariant();
    string numara = temiz.Substring(7, 5);
    for (int i = 0; i < numara.Length; i++)
    {
        if (!char.IsAsciiDigit(numara[i]))
            return "GECERSIZ_NUMARA";
    }
    return $"{bolge}:{ortam}:{numara}";
}
```

```starter
def kayit_coz(kod):
    if not kod:
        return "GECERSIZ"
    return f"{kod[:3]}:{kod[3:4]}:{kod[7:5]}"
```

```test
need("kayit_coz")
eq(kayit_coz("istPROD00421"), "IST:prod:00421", "0'dan 3 karakter, 3'ten 4 karakter, 7'den 5 karakter alınmalı")
eq(kayit_coz("  ankTEST99000 "), "ANK:test:99000", "kenar boşlukları kırpıldıktan sonra 12 karakter geçerli")
eq(kayit_coz("istPROD0042"), "GECERSIZ", "11 karakter -> GECERSIZ")
eq(kayit_coz("istPROD004219"), "GECERSIZ", "13 karakter -> GECERSIZ")
eq(kayit_coz("istPROD12a45"), "GECERSIZ_NUMARA", "numara kısmında harf varsa GECERSIZ_NUMARA")
eq(kayit_coz(None), "GECERSIZ", "None -> GECERSIZ")
```

```solution
def kayit_coz(kod):
    if kod is None:
        return "GECERSIZ"
    temiz = kod.strip()
    if len(temiz) != 12:
        return "GECERSIZ"
    bolge = temiz[0:3].upper()
    ortam = temiz[3:7].lower()
    numara = temiz[7:12]
    if not (numara.isascii() and numara.isdigit()):
        return "GECERSIZ_NUMARA"
    return f"{bolge}:{ortam}:{numara}"
```

```hint
C#'taki `temiz.Substring(baslangic, uzunluk)` Python dilimlemesinde `temiz[baslangic : baslangic + uzunluk]` karşılığına gelir: `Substring(3, 4)` → `temiz[3:7]`, `Substring(7, 5)` → `temiz[7:12]`.
```
:::

::: gorev `StringSplitOptions` ve `OrdinalIgnoreCase` izin denetimi
Aşağıdaki C# metodunun davranışını Python'da `rol_kontrol(etiket_metni, aranan_rol)` fonksiyonu olarak kur.

```csharp
public static string RolKontrol(string etiketMetni, string arananRol)
{
    if (etiketMetni == null || arananRol == null)
        return "YOK";
    string[] roller = etiketMetni.Split(',',
        StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
    int indeks = 0;
    foreach (string rol in roller)
    {
        if (rol.Equals(arananRol.Trim(), StringComparison.OrdinalIgnoreCase))
            return $"BULUNDU:{indeks}:{rol.ToLowerInvariant()}";
        indeks++;
    }
    return $"YOK:{roller.Length}";
}
```

```starter
def rol_kontrol(etiket_metni, aranan_rol):
    return "YOK:0"
```

```test
need("rol_kontrol")
eq(rol_kontrol(" Okuyucu , , YAZAR ,  Denetci ", "yazar"), "BULUNDU:1:yazar", "boş parçalar elendikten sonra YAZAR 1. indekste bulunmalı")
eq(rol_kontrol("admin, , operator", "  OPERATOR "), "BULUNDU:1:operator", "arananRol de kırpılıp büyük-küçük harf duyarsız eşleşmeli")
eq(rol_kontrol("okuyucu, , yazar,   ", "admin"), "YOK:2", "bulunamadığında temizlenmiş rol sayısı (2) dönmeli")
eq(rol_kontrol(" ,  , ", "admin"), "YOK:0", "yalnızca boşluk ve virgüllerden oluşan metinde 0 rol vardır")
eq(rol_kontrol(None, "admin"), "YOK", "etiketMetni None ise YOK")
eq(rol_kontrol("admin", None), "YOK", "arananRol None ise YOK")
```

```solution
def rol_kontrol(etiket_metni, aranan_rol):
    if etiket_metni is None or aranan_rol is None:
        return "YOK"
    roller = [p.strip() for p in etiket_metni.split(",") if p.strip()]
    hedef = aranan_rol.strip().lower()
    for i, rol in enumerate(roller):
        if rol.lower() == hedef:
            return f"BULUNDU:{i}:{rol.lower()}"
    return f"YOK:{len(roller)}"
```

```hint
`RemoveEmptyEntries | TrimEntries` birleşimi önce her parçayı `.strip()` ile kırpar, ardından boş kalanları (`if p.strip()`) eler.
```
:::
