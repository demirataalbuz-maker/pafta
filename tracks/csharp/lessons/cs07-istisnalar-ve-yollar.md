---
id: cs07
title: İstisnalar, using Bildirimi ve Path.Combine Tuzağı
summary: C# catch when filtreleri, TryParse deseni, using var (IDisposable) ve Path.Combine kök sıfırlama tuzağı.
---

::: anlat `TryParse`, `catch when` filtreleri ve `using var`
C#'ta denetlenen istisna (*checked exception*) kavramı yoktur; tüm istisnalar `Exception` sınıfından türer. Ancak iyi yazılmış C# kodunda kullanıcı girdisi ayrıştırılırken `int.Parse` yerine istisna fırlatmayan **`int.TryParse(metin, out int sonuc)`** tercih edilir.

İstisna yakalanırken C# 6+ **`catch (Exception ex) when (koşul)`** sözdizimiyle istisna filtresi yazılabilir. Kaynak yönetiminde ise C# 8+ **`using var akis = ...;`** bildirimi, değişkenin kapsamı bittiği anda otomatik olarak `Dispose()` çağırır.

```csharp
using System;

class IstisnaOrnek
{
    static string PortOku(string girdi)
    {
        if (!int.TryParse(girdi, out int port))         #! istisna fırlatmadan dener
            return "SAYI_DEGIL";
        return (port >= 1 && port <= 65535) ? $"PORT:{port}" : "ARALIK_DISI";
    }

    static void Main()
    {
        Console.WriteLine(PortOku("8080"));             #! PORT:8080
        Console.WriteLine(PortOku("abc"));              #! SAYI_DEGIL
    }
}
```
:::

::: anlat `Path.Combine` kök sıfırlama tuzağı!
.NET kaynak kodu denetimlerinde (OSWE / CWEE) en kritik dosya yolu tuzağı **`Path.Combine(tabanYol, kullaniciYolu)`** davranışıdır:
- Eğer ikinci argüman (`kullaniciYolu`) **`/`** veya **`\`** (ya da Windows'ta `C:\`) ile başlıyorsa, `Path.Combine` onu **mutlak (köklü) yol** kabul eder ve **birinci argümanı (`tabanYol`) tamamen çöpe atıp yalnızca ikinci argümanı döndürür!**

```csharp
using System;
using System.IO;

class YolTuzagi
{
    static void Main()
    {
        string taban = "/var/uygulama/raporlar";

        string normal = Path.Combine(taban, "ekim.pdf");
        Console.WriteLine(normal.Replace('\\', '/'));   #! /var/uygulama/raporlar/ekim.pdf

        string tuzak = Path.Combine(taban, "/etc/passwd");
        Console.WriteLine(tuzak.Replace('\\', '/'));    #! /etc/passwd  (taban tamamen silindi!)
    }
}
```

> [!GÜVENLİK]
> C#'ta güvenli dosya yolu doğrulaması için:
> 1. `Path.GetFullPath(Path.Combine(taban, girdi))` ile tam yolu çöz.
> 2. Taban dizinin sonuna dizin ayırıcısı (`/` veya `\`) ekleyerek `tamHedef.StartsWith(tamTaban + Path.DirectorySeparatorChar, StringComparison.Ordinal)` kontrolü yap (veya `Path.GetRelativePath(tamTaban, tamHedef)` sonucunun `".."` ile başlamadığını ve köklü olmadığını denetle).
:::

::: tahmin
```csharp
using System;
using System.IO;

class Tahmin
{
    static string Bol(int a, int b)
    {
        try
        {
            return "SONUC:" + (a / b);
        }
        catch (DivideByZeroException) when (a == 0)
        {
            return "SIFIR_BOLU_SIFIR";
        }
        catch (DivideByZeroException)
        {
            return "SIFIRA_BOLME";
        }
    }

    static void Main()
    {
        Console.WriteLine(Bol(0, 0));
        Console.WriteLine(Bol(10, 0));
        Console.WriteLine(Path.Combine("/srv/veri", "gunluk.log").Replace('\\', '/'));
        Console.WriteLine(Path.Combine("/srv/veri", "/tmp/gizli.txt").Replace('\\', '/'));
    }
}
```

```gercek
SIFIR_BOLU_SIFIR
SIFIRA_BOLME
/srv/veri/gunluk.log
/tmp/gizli.txt
```

???

`SIFIR_BOLU_SIFIR`, `SIFIRA_BOLME`, `/srv/veri/gunluk.log`, `/tmp/gizli.txt`. `Bol(0, 0)` çağrısında `DivideByZeroException` fırlatılır ve `when (a == 0)` filtresi doğru olduğu için ilk `catch` bloğu çalışır (`SIFIR_BOLU_SIFIR`). `Bol(10, 0)` çağrısında `a == 0` yanlış olduğundan ikinci `catch` bloğuna düşer (`SIFIRA_BOLME`). `Path.Combine("/srv/veri", "gunluk.log")` bağıl yolu birleştirip `/srv/veri/gunluk.log` üretirken, ikinci argüman `/` ile başladığında (`"/tmp/gizli.txt"`) `Path.Combine` ilk yolu tamamen yok sayar ve `/tmp/gizli.txt` döndürür.
:::

::: gorev C# `Path.Combine` davranışını ve güvenli yol kontrolünü simüle et
POSIX biçimli (`/`) yollarda C#'ın `Path.Combine(taban, girdi)` davranışını ve ardından güvenli kök dizin kontrolünü Python'da `yol_analiz(taban, girdi)` fonksiyonu olarak kur ve `(combine_sonucu, guvenli_mi)` demetini döndür:
1. `girdi = girdi.strip()` sonrasında `girdi` boşsa `("", False)` döndür.
2. **C# `Path.Combine` kuralı:** `girdi` `"/"` ile başlıyorsa birleştirme sonucu doğrudan `girdi` olur; başlamıyorsa `taban.rstrip("/") + "/" + girdi` olur.
3. Tam yolu `posixpath.normpath(combine_sonucu)` ile normalize et (`combine_sonucu` olarak bu normalize edilmiş yolu döndür).
4. **Güvenli mi:** Normalize edilmiş yol, normalize edilmiş `taban` dizininin **gerçek bir alt yolu** ise (ör. `/srv/veri/a.txt` → `True`, ama `/srv/veri` kendisi, `/srv/veri_ek/a.txt` veya `/etc/passwd` → `False`) `True`, değilse `False` döndür.

```starter
import posixpath

def yol_analiz(taban, girdi):
    birlesik = posixpath.normpath(taban.rstrip("/") + "/" + girdi.strip())
    return birlesik, birlesik.startswith(taban)
```

```test
need("yol_analiz")
eq(yol_analiz("/srv/veri", "rapor/ekim.txt"), ("/srv/veri/rapor/ekim.txt", True), "normal alt dosya güvenli")
eq(yol_analiz("/srv/veri", "/etc/passwd"), ("/etc/passwd", False), "girdi '/' ile başlayınca Path.Combine tabanı siler ve güvensiz olur")
eq(yol_analiz("/srv/veri", "../veri_yedek/gizli.txt"), ("/srv/veri_yedek/gizli.txt", False), "kardeş klasör (/srv/veri_yedek) reddedilmeli")
eq(yol_analiz("/srv/veri", "alt/../ok.txt"), ("/srv/veri/ok.txt", True), "taban içinde kalan .. geçişi güvenli")
eq(yol_analiz("/srv/veri", "."), ("/srv/veri", False), "taban klasörün kendisi dosya yolu olarak kabul edilmemeli")
eq(yol_analiz("/srv/veri", "   "), ("", False), "boş girdi -> ('', False)")
```

```solution
import posixpath

def yol_analiz(taban, girdi):
    temiz = girdi.strip()
    if not temiz:
        return "", False
    norm_taban = posixpath.normpath(taban)
    if temiz.startswith("/"):
        ham = temiz
    else:
        ham = norm_taban.rstrip("/") + "/" + temiz
    hedef = posixpath.normpath(ham)
    guvenli = hedef.startswith(norm_taban.rstrip("/") + "/")
    return hedef, guvenli
```

```hint
Normalize edilmiş bir POSIX yolunda (`posixpath.normpath`), `hedef.startswith(norm_taban.rstrip("/") + "/")` koşulu hem kardeş klasörleri (`/srv/veri_yedek`) hem de taban dizinin kendisini (`/srv/veri`) tek adımda eler!
```
:::

::: gorev `catch when` istisna filtresi simülatörü
Aşağıdaki C# metodunun `try` / `catch when` / `finally` akışını Python'da `islem_calistir(kod_metni, ortam)` fonksiyonu olarak kur.

```csharp
public static string IslemCalistir(string kodMetni, string ortam)
{
    string iz = "BASLA";
    try
    {
        int kod = int.Parse(kodMetni.Trim());
        if (kod < 100 || kod > 599)
            throw new ArgumentOutOfRangeException(nameof(kod));
        if (kod >= 500)
            throw new InvalidOperationException($"SUNUCU_HATASI:{kod}");
        iz += $"->OK:{kod}";
    }
    catch (FormatException)
    {
        iz += "->FORMAT_HATASI";
    }
    catch (InvalidOperationException ex) when (ortam == "gelistirme")
    {
        iz += $"->ACIK_HATA:{ex.Message}";
    }
    catch (Exception)
    {
        iz += "->GENEL_HATA";
    }
    finally
    {
        iz += "->BITTI";
    }
    return iz;
}
```

```starter
def islem_calistir(kod_metni, ortam):
    return "BASLA->BITTI"
```

```test
need("islem_calistir")
eq(islem_calistir(" 200 ", "uretim"), "BASLA->OK:200->BITTI", "geçerli 200 kodu")
eq(islem_calistir("100", "uretim"), "BASLA->OK:100->BITTI", "alt sınır 100 geçerli")
eq(islem_calistir("499", "uretim"), "BASLA->OK:499->BITTI", "üst sınır 499 (< 500) OK dönmeli")
eq(islem_calistir("abc", "gelistirme"), "BASLA->FORMAT_HATASI->BITTI", "sayı olmayan metin -> FORMAT_HATASI")
eq(islem_calistir("500", "gelistirme"), "BASLA->ACIK_HATA:SUNUCU_HATASI:500->BITTI", "500 ve ortam=='gelistirme' -> ACIK_HATA")
eq(islem_calistir("599", "gelistirme"), "BASLA->ACIK_HATA:SUNUCU_HATASI:599->BITTI", "üst sınır 599 ve ortam=='gelistirme' -> ACIK_HATA")
eq(islem_calistir("550", "uretim"), "BASLA->GENEL_HATA->BITTI", "550 ve ortam!='gelistirme' -> when filtresi tutmaz, Exception bloğuna (GENEL_HATA) düşer")
eq(islem_calistir("99", "gelistirme"), "BASLA->GENEL_HATA->BITTI", "99 (< 100) ArgumentOutOfRangeException -> GENEL_HATA")
eq(islem_calistir("600", "gelistirme"), "BASLA->GENEL_HATA->BITTI", "600 (> 599) ArgumentOutOfRangeException -> GENEL_HATA")
```

```solution
import re

def islem_calistir(kod_metni, ortam):
    iz = "BASLA"
    temiz = kod_metni.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", temiz):
        iz += "->FORMAT_HATASI"
    else:
        kod = int(temiz)
        if kod < 100 or kod > 599:
            iz += "->GENEL_HATA"
        elif kod >= 500:
            if ortam == "gelistirme":
                iz += f"->ACIK_HATA:SUNUCU_HATASI:{kod}"
            else:
                iz += "->GENEL_HATA"
        else:
            iz += f"->OK:{kod}"
    return iz + "->BITTI"
```

```hint
`kod >= 500` olduğunda (ve `<= 599` iken) `InvalidOperationException` fırlatılır: eğer `ortam == "gelistirme"` ise `when` filtresi tutar (`ACIK_HATA`), değilse bir alttaki `catch (Exception)` bloğuna (`GENEL_HATA`) düşer.
```
:::
