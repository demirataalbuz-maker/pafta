---
id: cs04
title: Koleksiyonlar · List<T>, Dictionary<K,V> ve TryGetValue
summary: C# genel koleksiyonları, Dictionary indeksleyici tuzağı, TryGetValue(out var) ve StringComparer.OrdinalIgnoreCase.
---

::: anlat `List<T>`, `Dictionary<TKey, TValue>` ve `KeyNotFoundException` tuzağı
C#'ta en sık kullanılan koleksiyonlar `System.Collections.Generic` ad alanındadır:
- **`List<T>`:** dinamik dizi (`.Add(x)`, `.Count`, `liste[i]`).
- **`HashSet<T>`:** tekrarsız küme (`.Add(x)` yeni eklendiyse `true`, zaten varsa `false` döndürür!).
- **`Dictionary<TKey, TValue>`:** anahtar-değer sözlüğü.

Java'daki `map.get(k)` anahtar yoksa `null` döndürürken, C#'ta **`sozluk[k]`** indeksleyicisi anahtar yoksa (tıpkı Python'daki `KeyError` gibi) **`KeyNotFoundException`** fırlatır! Bu yüzden C# kodunda güvenli okuma için **`TryGetValue(anahtar, out var deger)`** veya `.GetValueOrDefault(anahtar, varsayilan)` kullanılır.

```csharp
using System;
using System.Collections.Generic;

class SozlukOrnek
{
    static void Main()
    {
        var portlar = new Dictionary<string, int>
        {
            ["http"] = 80,
            ["https"] = 443
        };

        if (portlar.TryGetValue("ssh", out int sshPort))   #! anahtar yoksa false döner, istisna fırlatmaz
            Console.WriteLine(sshPort);
        else
            Console.WriteLine("YOK");                      #! YOK

        Console.WriteLine(portlar.GetValueOrDefault("http", 8080)); #! 80
    }
}
```
:::

::: anlat `StringComparer.OrdinalIgnoreCase` ve `TryAdd`
HTTP başlıklarını, yapılandırma anahtarlarını veya kullanıcı adlarını tutan bir `Dictionary` ya da `HashSet` oluşturulurken kurucuya **`StringComparer.OrdinalIgnoreCase`** verilirse tüm anahtar aramaları büyük-küçük harf duyarsız çalışır!

Ayrıca sözlüğe yazarken üç yöntem farklı davranır:
- **`sozluk[k] = v`:** anahtar varsa üzerine yazar, yoksa ekler.
- **`sozluk.Add(k, v)`:** anahtar zaten varsa **`ArgumentException`** fırlatır!
- **`sozluk.TryAdd(k, v)`:** yalnızca anahtar yoksa ekler (`true` döner); varsa dokunmaz (`false` döner).

```csharp
using System;
using System.Collections.Generic;

class BaslikTablosu
{
    static void Main()
    {
        var basliklar = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        basliklar.TryAdd("X-Hedef", "web01");
        basliklar.TryAdd("x-hedef", "web02");          #! OrdinalIgnoreCase yüzünden aynı anahtar sayılır -> eklenmez!

        Console.WriteLine(basliklar["X-HEDEF"]);       #! web01
        Console.WriteLine(basliklar.Count);            #! 1
    }
}
```
:::

::: tahmin
```csharp
using System;
using System.Collections.Generic;

class Tahmin
{
    static void Main()
    {
        var roller = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["Ali"] = "okuyucu"
        };

        bool eklendi1 = roller.TryAdd("ali", "admin");
        bool eklendi2 = roller.TryAdd("Ayse", "operator");
        roller["ALI"] = "denetci";

        Console.WriteLine(eklendi1 + ":" + eklendi2);
        Console.WriteLine(roller["ali"]);
        Console.WriteLine(roller.TryGetValue("Mehmet", out var mRol) ? mRol : "YOK");
        Console.WriteLine(roller.Count);
    }
}
```

```gercek
False:True
denetci
YOK
2
```

???

`False:True`, `denetci`, `YOK`, `2`. Sözlük `StringComparer.OrdinalIgnoreCase` ile kurulduğu için `"Ali"`, `"ali"` ve `"ALI"` aynı anahtardır. `TryAdd("ali", "admin")` anahtar zaten var olduğundan ekleme yapmaz ve `False` döner; `TryAdd("Ayse", "operator")` ise `True` döner (`False:True`). Ardından `roller["ALI"] = "denetci"` indeksleyici ataması mevcut `"Ali"` kaydının değerini `"denetci"` olarak günceller. `"Mehmet"` sözlükte olmadığı için `TryGetValue` `false` döner ve `YOK` yazdırılır; sözlükte toplam `2` kayıt vardır.
:::

::: gorev `StringComparer.OrdinalIgnoreCase` ve `TryAdd` ile başlık toplayıcı
Aşağıdaki C# metodu gelen `"Anahtar: Değer"` satırlarını `StringComparer.OrdinalIgnoreCase` kullanan bir sözlükte topluyor. `TryAdd` kullanıldığı için aynı başlık (büyük-küçük harf duyarsız) birden fazla kez gelirse **ilk gelen değer** korunuyor ve kaç kez çakışma olduğu sayılıyor. Aynı davranışı Python'da `basliklari_topla(satirlar, aranan_anahtar)` fonksiyonu olarak kur ve `(bulunan_deger, essiz_sayisi, cakisma_sayisi)` demetini döndür.

```csharp
public static (string Deger, int EssizSayisi, int CakismaSayisi) BasliklariTopla(
    List<string> satirlar, string arananAnahtar)
{
    var tablo = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
    int cakisma = 0;
    foreach (string satir in satirlar)
    {
        int ikiNokta = satir.IndexOf(':');
        if (ikiNokta <= 0)
            continue;
        string k = satir.Substring(0, ikiNokta).Trim();
        string v = satir.Substring(ikiNokta + 1).Trim();
        if (k.Length == 0)
            continue;
        if (!tablo.TryAdd(k, v))
            cakisma++;
    }
    string sonuc = tablo.TryGetValue(arananAnahtar.Trim(), out var bulunan) ? bulunan : "YOK";
    return (sonuc, tablo.Count, cakisma);
}
```

```starter
def basliklari_topla(satirlar, aranan_anahtar):
    return "YOK", 0, 0
```

```test
need("basliklari_topla")
eq(basliklari_topla(["X-Kimlik: ali", "x-kimlik: veli", "Content-Type: application/json"], "X-KIMLIK"),
   ("ali", 2, 1),
   "TryAdd ilk değeri ('ali') korumalı, ikinci 'x-kimlik' çakışma sayısını 1 artırmalı")
eq(basliklari_topla([":bozuk", "iki_noktasiz", "   :bos_anahtar", "Host: pafta.local:8080"], "  host "),
   ("pafta.local:8080", 1, 0),
   "geçersiz satırlar atlanmalı; değer içindeki ikinci ':' korunmalı")
eq(basliklari_topla(["A: 1", "a: 2", "A: 3"], "B"),
   ("YOK", 1, 2),
   "olmayan anahtar için 'YOK' ve 2 çakışma dönmeli")
```

```solution
def basliklari_topla(satirlar, aranan_anahtar):
    tablo = {}
    cakisma = 0
    for satir in satirlar:
        if ":" not in satir:
            continue
        ham_k, ham_v = satir.split(":", 1)
        k = ham_k.strip().lower()
        v = ham_v.strip()
        if not k:
            continue
        if k in tablo:
            cakisma += 1
        else:
            tablo[k] = v
    bulunan = tablo.get(aranan_anahtar.strip().lower(), "YOK")
    return bulunan, len(tablo), cakisma
```

```hint
Anahtarları küçük harfe (`.strip().lower()`) normalize ederek `StringComparer.OrdinalIgnoreCase` davranışını kurabilirsin. `k in tablo` ise üzerine yazma, yalnızca `cakisma += 1` yap.
```
:::

::: gorev `HashSet<string>.Add` dönüş değeriyle tekrarlı istek avcısı
C#'ta `HashSet<T>.Add(eleman)` metodu eleman kümeye ilk kez eklendiyse `true`, zaten kümede varsa `false` döndürür. Aşağıdaki C# metodunun döndürdüğü tekrarlı kimlik listesini Python'da `tekrarlilari_bul(istek_kimlikleri)` fonksiyonu olarak üret.

```csharp
public static List<string> TekrarlilariBul(List<string> istekKimlikleri)
{
    var gorulenler = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
    var tekrarEdenler = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
    var sonuc = new List<string>();

    foreach (string ham in istekKimlikleri)
    {
        string id = ham.Trim();
        if (id.Length == 0)
            continue;
        if (!gorulenler.Add(id) && tekrarEdenler.Add(id))
        {
            sonuc.Add(id.ToUpperInvariant());
        }
    }
    return sonuc;
}
```

```starter
def tekrarlilari_bul(istek_kimlikleri):
    return []
```

```test
need("tekrarlilari_bul")
eq(tekrarlilari_bul(["req-1", "REQ-2", "  req-1 ", "req-1", "req-2", "req-3"]),
   ["REQ-1", "REQ-2"],
   "3 kez geçen req-1 sonuç listesine yalnızca 1 kez (ikinci görülüşünde) eklenmeli")
eq(tekrarlilari_bul(["   ", "a", "b", "c"]), [], "tekrar yoksa ve boşluk satırı varsa boş liste dönmeli")
eq(tekrarlilari_bul(["x", "y", "Y", "X"]), ["Y", "X"], "sıra ikinci kez görüldükleri sıraya göre olmalı")
```

```solution
def tekrarlilari_bul(istek_kimlikleri):
    gorulenler = set()
    tekrar_edenler = set()
    sonuc = []
    for ham in istek_kimlikleri:
        norm = ham.strip().upper()
        if not norm:
            continue
        if norm in gorulenler:
            if norm not in tekrar_edenler:
                tekrar_edenler.add(norm)
                sonuc.append(norm)
        else:
            gorulenler.add(norm)
    return sonuc
```

```hint
`!gorulenler.Add(id) && tekrarEdenler.Add(id)` koşulu, bir kimliğin tam olarak **ikinci kez** görüldüğü anda `true` olur; üçüncü ve sonraki görülüşlerinde `tekrarEdenler.Add(id)` `false` döndüğü için listeye tekrar eklenmez.
```
:::
