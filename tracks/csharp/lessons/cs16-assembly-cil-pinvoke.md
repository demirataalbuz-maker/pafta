---
id: cs16
title: Assembly, CIL ve P/Invoke Sınırı
summary: Derlenmiş bir assembly'de yönetilen yöntemin CIL gövdesi vardır ve okunabilir (ldarg.0 ldarg.1 add ret = 02 03 58 2a); P/Invoke yönteminin gövdesi yoktur, yerine PinvokeImpl bayrağı ve DllImport metadata'sı bulunur — sınır tam burada görünür. Marshalling tarafında CharSet.Unicode metni UTF-16 kod birimleriyle, CharSet.Ansi tek bayta çevirir ve karşılığı olmayan karakterler sessizce 0x3f ('?') olur; dönüş IntPtr olmazsa 64 bitlik handle kırpılır, SetLastError ile hata kodu okunur.
---

::: anlat Yönetilen yöntemin gövdesi okunabilir
Kaynak kod elinde olmadığında bile derlenmiş bir assembly çok şey anlatır: tür ve yöntem **metadata**'sı ile yönetilen yöntemlerin **CIL** gövdeleri dosyanın içindedir. `System.Reflection` ile ikisine de bakabilirsin.

```csharp norun
public static int Topla(int a, int b) => a + b;

var il = typeof(P).GetMethod("Topla")!.GetMethodBody()!.GetILAsByteArray()!;
// 02 03 58 2a
```

Dört bayt, dört komut:

| Bayt | Komut | Ne yapar |
|---|---|---|
| `02` | `ldarg.0` | ilk argümanı yığına koy |
| `03` | `ldarg.1` | ikinci argümanı yığına koy |
| `58` | `add` | yığındaki ikisini topla |
| `2a` | `ret` | dön |

CIL bir **yığın makinesi** dilidir: komutlar değerleri bir yığına koyar ve oradan tüketir. Değişken adları, parametre adları ve satır numaraları metadata'da (ve varsa `.pdb`'de) durur; IL'in kendisinde yalnız konumlar vardır.
:::

::: anlat Sınır: gövdesi olmayan yöntem
Bir `DllImport` yöntemi derleyici için sıradan bir yöntem bildirimidir, ama arkasında **CIL yoktur**. Ölçüldü (.NET 8.0.31):

```csharp norun
[DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
public static extern int lstrlenW(string s);
```

| Soru | Yanıt |
|---|---|
| `GetMethodBody()` | **null** |
| Yöntem bayrakları | `PinvokeImpl` |
| `DllImport` metadata | `dll=kernel32`, `charset=Unicode`, `setLastError=True` |

Yönetilen/yerel sınırı bir incelemede tam olarak böyle görünür: gövdesi olmayan, yerine "hangi kütüphanenin hangi sembolünü, nasıl çağıracağım" bilgisini taşıyan yöntemler. Bir assembly'de çağrı izini sürerken IL'in bittiği yer budur.

Sınırı geçerken veri **marshalling** edilir ve asıl tuzaklar oradadır.

**Metin.** `CharSet.Unicode` .NET'in UTF-16 dizgisini olduğu gibi geçirir; `CharSet.Ansi` tek baytlık kod sayfasına çevirir. Ölçülen baytlar:

| Metin | Unicode (W) | Ansi (A) |
|---|---|---|
| `pafta` | `70 00 61 00 66 00 74 00 61 00` | `70 61 66 74 61` |
| `çğı` | `e7 00 1f 01 31 01` | `e7 3f 3f` |
| `ab😀cd` | `61 00 62 00 3d d8 00 de 63 00 64 00` | `61 62 3f 3f 63 64` |

`ç` kod sayfasında karşılığı olduğu için korundu; `ğ` ve `ı` **sessizce `3f` yani `'?'`** oldu. Emoji bir vekil çifttir (`3d d8 00 de`) ve Ansi tarafında iki `'?'`e indi.

> [!TUZAK] Uzunluk tutabilir, veri bozulmuş olabilir
> Aynı metinler için `lstrlenW` ve `lstrlenA` bu ölçümde **aynı sayıyı** döndürdü (`çğı` için 3, emoji için 6). Yanlış `CharSet` seçtiğini uzunluğa bakarak anlayamazsın; sayı tutarken baytlar bozulmuş olabilir. Doğrulamayı dönen sayıyla değil, karşıya giden baytlarla yap.

**Dönüş ve hata.** Handle döndüren bir fonksiyonun dönüşünü `int` yazarsan 64 bitlik değer kırpılır; `IntPtr` kullanılır. Ölçüldü: `GetModuleHandleW("kernel32.dll")` sıfırdan farklı ve değeri **32 biti aşıyor**. Olmayan bir modül için dönüş `IntPtr.Zero` ve `SetLastError = true` sayesinde `Marshal.GetLastWin32Error()` **126**'dır. Hata kodunu yalnız dönüş başarısızlık dediğinde oku.
:::

::: tahmin Gövde var mı, sayı kaç?
```csharp
var yonetilen = typeof(P).GetMethod("Topla")!;        // public static int Topla(int a, int b) => a + b;
Console.WriteLine(string.Join(" ", yonetilen.GetMethodBody()!.GetILAsByteArray()!.Select(b => b.ToString("x2"))));
var yerli = typeof(Yerli).GetMethod("lstrlenW")!;      // [DllImport("kernel32", CharSet=Unicode, SetLastError=true)]
Console.WriteLine(yerli.GetMethodBody() is null ? "YOK (null)" : "var");
Console.WriteLine(yerli.Attributes & MethodAttributes.PinvokeImpl);
var h = Yerli.GetModuleHandleW("pafta_yok_12345.dll");
Console.WriteLine($"{h == IntPtr.Zero} {Marshal.GetLastWin32Error()}");
```

```gercek
02 03 58 2a
YOK (null)
PinvokeImpl
True 126
```

???

`02 03 58 2a`: dört baytlık bir toplama. `ldarg.0`, `ldarg.1`, `add`, `ret` — gövde gerçekten assembly'nin içinde duruyor ve okunabiliyor.

`YOK (null)`: `lstrlenW` bir yöntem gibi bildirildi ama **CIL gövdesi yok**. Burada iş yapan şey assembly'nin içinde değil; çalışma zamanı, metadata'daki yönergeye bakıp yerel kütüphaneyi çağırıyor.

`PinvokeImpl`: bayrağın adı sınırı doğrudan söylüyor. Bir assembly'yi incelerken bu bayraklı yöntemleri listelemek, "bu kod dışarıya nerede çıkıyor?" sorusunun en hızlı yanıtıdır.

`True 126`: modül bulunamadı, dönüş `IntPtr.Zero` oldu ve son hata 126. `SetLastError = true` yazılmamış olsaydı `Marshal.GetLastWin32Error()` güvenilir olmazdı — çağrı sonrası araya giren başka çağrılar değeri ezebilir.
:::

::: gorev CIL baytlarını çöz
`cozIl(baytlar)` yaz: tek baytlık CIL komutlarından oluşan bir diziyi komut adlarına çevir.

Bilinen komutlar:

| Bayt | Ad | | Bayt | Ad |
|---|---|---|---|---|
| `0x00` | `nop` | | `0x17` | `ldc.i4.1` |
| `0x02` | `ldarg.0` | | `0x2a` | `ret` |
| `0x03` | `ldarg.1` | | `0x58` | `add` |
| `0x04` | `ldarg.2` | | `0x59` | `sub` |
| `0x06` | `ldloc.0` | | `0x5a` | `mul` |
| `0x16` | `ldc.i4.0` | | | |

Listede olmayan bir bayt için `"bilinmeyen(0xNN)"` döndür; `NN` iki haneli küçük harfli onaltılıktır. Boş dizi boş liste verir.

```starter
KOMUTLAR = {0x02: "ldarg.0", 0x03: "ldarg.1", 0x58: "add", 0x2a: "ret"}

def cozIl(baytlar):
    return [KOMUTLAR[b] for b in baytlar]
```

```test
need("cozIl")
eq(cozIl([0x02, 0x03, 0x58, 0x2a]), ["ldarg.0", "ldarg.1", "add", "ret"],
   "ölçülen Topla yöntemi: dört bayt, dört komut")
eq(cozIl([0x02, 0x03, 0x59, 0x2a]), ["ldarg.0", "ldarg.1", "sub", "ret"], "çıkarma")
eq(cozIl([0x16, 0x2a]), ["ldc.i4.0", "ret"], "sabit sıfır döndüren yöntem")
eq(cozIl([0x00, 0x06, 0x2a]), ["nop", "ldloc.0", "ret"], "hata ayıklama derlemesinde nop")
eq(cozIl([0x02, 0x04, 0x5a, 0x2a]), ["ldarg.0", "ldarg.2", "mul", "ret"], "üçüncü argüman ve çarpma")
eq(cozIl([0xfe]), ["bilinmeyen(0xfe)"], "çok baytlı komut öneki: bu tabloda yok")
eq(cozIl([0x0a]), ["bilinmeyen(0x0a)"], "tek haneli değer iki haneye tamamlanır")
eq(cozIl([0x02, 0x99, 0x2a]), ["ldarg.0", "bilinmeyen(0x99)", "ret"], "arada bilinmeyen bayt")
eq(cozIl([]), [], "boş gövde")
```

```solution
KOMUTLAR = {0x00: "nop", 0x02: "ldarg.0", 0x03: "ldarg.1", 0x04: "ldarg.2", 0x06: "ldloc.0",
            0x16: "ldc.i4.0", 0x17: "ldc.i4.1", 0x2a: "ret", 0x58: "add", 0x59: "sub", 0x5a: "mul"}

def cozIl(baytlar):
    return [KOMUTLAR.get(b, f"bilinmeyen(0x{b:02x})") for b in baytlar]
```

```hint
Başlangıç kodu hem tabloyu eksik bırakıyor hem de bilinmeyen baytta `KeyError` atıyor. `dict.get` ile varsayılan ver: `f"bilinmeyen(0x{b:02x})"` iki haneli küçük harfli onaltılık üretir.
```
:::

::: gorev Ansi'ye çevirirken ne kayboluyor?
`ansiBaytlar(metin, kodSayfasi)` yaz: `CharSet.Ansi` marshalling'inin ürettiği bayt listesini modelle.

- `kodSayfasi`: kod sayfasında karşılığı olan karakterleri `{karakter: bayt}` biçiminde veren sözlük.
- Karşılığı olan karakter kendi baytını verir.
- Karşılığı olmayan her karakter `0x3f` olur.
- Temel Çok Dilli Düzlem dışındaki bir karakter (Python'da `ord(c) > 0xFFFF`) UTF-16'da **iki** kod birimidir ve Ansi tarafında **iki** adet `0x3f` üretir.

```starter
def ansiBaytlar(metin, kodSayfasi):
    return [kodSayfasi.get(k, 0x3f) for k in metin]
```

```test
need("ansiBaytlar")
CP = {"p": 0x70, "a": 0x61, "f": 0x66, "t": 0x74, "ç": 0xe7, "b": 0x62, "c": 0x63, "d": 0x64}
eq(ansiBaytlar("pafta", CP), [0x70, 0x61, 0x66, 0x74, 0x61], "ölçülen: hepsi tek bayt")
eq(ansiBaytlar("çğı", CP), [0xe7, 0x3f, 0x3f],
   "ölçülen: ç korunur, ğ ve ı sessizce '?' olur")
eq(ansiBaytlar("ab\U0001F600cd", CP), [0x61, 0x62, 0x3f, 0x3f, 0x63, 0x64],
   "ölçülen: emoji vekil çifttir, iki '?' üretir")
eq(ansiBaytlar("", CP), [], "boş metin")
eq(ansiBaytlar("\U0001F600", CP), [0x3f, 0x3f], "tek başına BMP dışı karakter")
utf16_birim = len("ab\U0001F600cd".encode("utf-16-le")) // 2
eq(len(ansiBaytlar("ab\U0001F600cd", CP)), utf16_birim,
   "bayt sayısı C#'ın Length'i (UTF-16 kod birimi) ile aynı kalır: sayıya bakarak bozulmayı göremezsin")

eq(ansiBaytlar('\uffff',CP),[0x3f],'U+FFFF tek UTF16 birimi')
eq(ansiBaytlar('\U00010000',CP),[0x3f,0x3f],'U+10000 iki UTF16 birimi')

```

```solution
def ansiBaytlar(metin, kodSayfasi):
    cikti = []
    for k in metin:
        if k in kodSayfasi:
            cikti.append(kodSayfasi[k])
        elif ord(k) > 0xFFFF:
            cikti.extend([0x3f, 0x3f])
        else:
            cikti.append(0x3f)
    return cikti
```

```hint
Başlangıç kodu her karakteri tek bayta çeviriyor; BMP dışı karakterler UTF-16'da iki kod birimi olduğu için iki `0x3f` vermeli. Python dizgisinde böyle bir karakter tek `str` öğesidir, bu yüzden `ord(k) > 0xFFFF` denetimini sen yapmalısın.
```
:::
