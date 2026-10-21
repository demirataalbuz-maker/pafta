---
id: cs06
title: LINQ Boru Hattı · Where, Select, OrderBy ve Ertelenmiş Çalıştırma
summary: LINQ metot sözdizimi, FirstOrDefault ile SingleOrDefault farkı, Any/All ve ertelenmiş çalıştırma (deferred execution).
---

::: anlat LINQ metot zinciri ve `FirstOrDefault` vs `SingleOrDefault`
C# kodunun en ayırt edici özelliği **LINQ** (*Language Integrated Query*) boru hattıdır (`using System.Linq;`):
- **`.Where(x => koşul)`:** koşulu sağlayanları süzer.
- **`.OrderBy(x => alan)` / `.OrderByDescending(x => alan)`:** ana sıralamayı kurar; ikincil sıralama için **`.ThenBy(...)`** / **`.ThenByDescending(...)`** eklenir (ikinci bir `.OrderBy` yazmak ilk sıralamayı ezer!).
- **`.Skip(n).Take(m)`:** ilk `n` elemanı atlar, sonraki en fazla `m` elemanı alır.
- **`.Select(x => ...)`:** her elemanı dönüştürür.

Tek bir kayıt çekerken kullanılan iki metot arasındaki fark güvenlik ve kararlılık açısından çok önemlidir:
- **`FirstOrDefault(...)`:** eşleşen **ilk** kaydı döndürür; hiç yoksa `null` (veya varsayılan) döner. Birden fazla eşleşme olsa bile hata vermez!
- **`SingleOrDefault(...)`:** eşleşen kayıt yoksa `null`, **tam 1** kayıt varsa o kaydı döndürür; ancak **2 veya daha fazla** eşleşme varsa **`InvalidOperationException`** fırlatır!

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

class LinqOrnek
{
    static void Main()
    {
        var kodlar = new List<int> { 200, 500, 404, 502, 200 };

        int ilkHata = kodlar.FirstOrDefault(k => k >= 500);
        Console.WriteLine(ilkHata);                         #! 500 (ilk eşleşeni alır)

        try
        {
            int tekHata = kodlar.SingleOrDefault(k => k >= 500); #! 500 ve 502 var -> 2 eşleşme!
            Console.WriteLine(tekHata);
        }
        catch (InvalidOperationException)
        {
            Console.WriteLine("COKLU_ESLESME_HATASI");      #! COKLU_ESLESME_HATASI
        }
    }
}
```
:::

::: anlat Ertelenmiş çalıştırma (*Deferred Execution*) tuzağı
`Where`, `Select`, `OrderBy`, `Take` gibi LINQ metotları çağrıldığı anda listeyi **taramaz**; yalnızca bir **sorgu tarifi** (`IEnumerable<T>`) oluşturur! Sorgu ancak `ToList()`, `ToArray()`, `Count()`, `FirstOrDefault()` veya `foreach` ile tüketildiğinde çalışır.

Eğer `.ToList()` ile sonuç dondurulmadan önce kaynak listeye yeni eleman eklenir veya filtrede kullanılan dış değişken değiştirilirse, sorgu tüketildiği andaki **güncel** değerleri kullanır!

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

class ErtelenmisOrnek
{
    static void Main()
    {
        var sayilar = new List<int> { 10, 20, 30 };
        int esik = 15;

        var ertelenmis = sayilar.Where(x => x >= esik);     #! henüz çalışmadı!
        var dondurulmus = sayilar.Where(x => x >= esik).ToList(); #! hemen çalıştı: [20, 30]

        sayilar.Add(40);
        esik = 25;                                          #! dış değişken değişti!

        Console.WriteLine(string.Join(",", dondurulmus));   #! 20,30
        Console.WriteLine(string.Join(",", ertelenmis));    #! 30,40 (esik=25 ve 40 eklendi!)
    }
}
```
:::

::: tahmin
```csharp
using System;
using System.Collections.Generic;
using System.Linq;

class Tahmin
{
    static void Main()
    {
        var sureler = new List<int> { 120, 45, 300, 120 };
        int minSure = 100;

        var sorgu = sureler
            .Where(s => s >= minSure)
            .OrderByDescending(s => s);

        sureler.Add(250);
        minSure = 120;

        var sonuc = sorgu.Take(3).ToList();
        Console.WriteLine(string.Join(",", sonuc));

        Console.WriteLine(sureler.FirstOrDefault(s => s > 200));
        try
        {
            Console.WriteLine(sureler.SingleOrDefault(s => s == 120));
        }
        catch (InvalidOperationException)
        {
            Console.WriteLine("COKLU_KAYIT");
        }
    }
}
```

```gercek
300,250,120
300
COKLU_KAYIT
```

???

`300,250,120`, `300`, `COKLU_KAYIT`. `sorgu` tanımlandığında `.ToList()` çağrılmadığı için ertelenmiş çalıştırma (*deferred execution*) geçerlidir. `ToList()` çağrıldığı anda `sureler` listesi `{ 120, 45, 300, 120, 250 }` ve `minSure` değeri `120` olmuştur; `>= 120` olanlar azalan sırayla `300, 250, 120, 120` olur ve `.Take(3)` ilk üçünü (`300,250,120`) alır. `FirstOrDefault(s => s > 200)` listedeki ilk eşleşen `300` değerini döndürür. `SingleOrDefault(s => s == 120)` ise listede iki tane `120` bulunduğu için `InvalidOperationException` fırlatır ve `COKLU_KAYIT` yazdırılır.
:::

::: gorev `SingleOrDefault` ve `FirstOrDefault` oturum doğrulayıcı
Aşağıdaki C# metodunun davranışını Python'da `kullanici_bul(kayitlar, aranan_eposta, tekil_zorunlu_mu)` fonksiyonu olarak kur:
- Her kayıt `{"id": int, "eposta": str, "aktif": bool}` sözlüğüdür.
- Yalnızca `aktif == True` olan ve `eposta` alanı `aranan_eposta.strip()` ile büyük-küçük harf duyarsız (`OrdinalIgnoreCase`) eşleşen kayıtlar seçilir.
- `tekil_zorunlu_mu` `True` ise `SingleOrDefault` kullanılır (0 eşleşmede `"BULUNAMADI"`, 1 eşleşmede `f"OK:{id}"`, 2+ eşleşmede `"COKLU_HESAP_HATASI"`).
- `tekil_zorunlu_mu` `False` ise `FirstOrDefault` kullanılır (0 eşleşmede `"BULUNAMADI"`, 1+ eşleşmede `id` değerine göre küçükten büyüğe sıralanmış ilk kaydın `f"OK:{id}"` sonucu).

```csharp
public static string KullaniciBul(
    List<Hesap> kayitlar, string arananEposta, bool tekilZorunluMu)
{
    var sorgu = kayitlar
        .Where(h => h.Aktif && h.Eposta.Equals(arananEposta.Trim(), StringComparison.OrdinalIgnoreCase))
        .OrderBy(h => h.Id);
    try
    {
        Hesap? bulunan = tekilZorunluMu
            ? sorgu.SingleOrDefault()
            : sorgu.FirstOrDefault();
        return bulunan == null ? "BULUNAMADI" : $"OK:{bulunan.Id}";
    }
    catch (InvalidOperationException)
    {
        return "COKLU_HESAP_HATASI";
    }
}
```

```starter
def kullanici_bul(kayitlar, aranan_eposta, tekil_zorunlu_mu):
    return "BULUNAMADI"
```

```test
need("kullanici_bul")
ornek = [
    {"id": 9, "eposta": "ali@pafta.local", "aktif": True},
    {"id": 3, "eposta": "ALI@pafta.local", "aktif": True},
    {"id": 1, "eposta": "ali@pafta.local", "aktif": False},
    {"id": 5, "eposta": "ayse@pafta.local", "aktif": True},
]
eq(kullanici_bul(ornek, "  ayse@PAFTA.local ", True), "OK:5", "tek aktif eşleşmede SingleOrDefault OK:5 döndürür")
eq(kullanici_bul(ornek, "ali@pafta.local", True), "COKLU_HESAP_HATASI", "2 aktif eşleşmede SingleOrDefault InvalidOperationException fırlatır")
eq(kullanici_bul(ornek, "ali@pafta.local", False), "OK:3", "FirstOrDefault OrderBy(Id) sonrası en küçük aktif id'yi (3) alır; pasif id=1 elenir")
eq(kullanici_bul(ornek, "yok@pafta.local", True), "BULUNAMADI", "eşleşme yoksa SingleOrDefault null döner -> BULUNAMADI")
eq(kullanici_bul(ornek, "yok@pafta.local", False), "BULUNAMADI", "eşleşme yoksa FirstOrDefault null döner -> BULUNAMADI")
```

```solution
def kullanici_bul(kayitlar, aranan_eposta, tekil_zorunlu_mu):
    hedef = aranan_eposta.strip().lower()
    eslesenler = sorted(
        (h for h in kayitlar if h["aktif"] and h["eposta"].lower() == hedef),
        key=lambda h: h["id"],
    )
    if not eslesenler:
        return "BULUNAMADI"
    if tekil_zorunlu_mu and len(eslesenler) > 1:
        return "COKLU_HESAP_HATASI"
    return f"OK:{eslesenler[0]['id']}"
```

```hint
Pasif kayıtları (`aktif == False`) eledikten sonra `id` değerine göre artan sırala; `tekil_zorunlu_mu` doğruyken `len(eslesenler) > 1` ise `"COKLU_HESAP_HATASI"` döndür.
```
:::

::: gorev LINQ `OrderByDescending` + `ThenBy` + `Skip` + `Take` sayfalama boru hattı
Aşağıdaki C# LINQ boru hattının döndürdüğü listeyi Python'da `bilet_sayfasi(biletler, min_oncelik, sayfa_no, sayfa_boyutu)` fonksiyonu olarak üret. Her bilet `{"kod": str, "oncelik": int, "acik": bool}` sözlüğüdür.

```csharp
public static List<string> BiletSayfasi(
    List<Bilet> biletler, int minOncelik, int sayfaNo, int sayfaBoyutu)
{
    if (sayfaNo < 1 || sayfaBoyutu < 1)
        return new List<string>();

    return biletler
        .Where(b => b.Acik && b.Oncelik >= minOncelik)
        .OrderByDescending(b => b.Oncelik)
        .ThenBy(b => b.Kod)
        .Skip((sayfaNo - 1) * sayfaBoyutu)
        .Take(sayfaBoyutu)
        .Select(b => $"{b.Kod}:{b.Oncelik}")
        .ToList();
}
```

```starter
def bilet_sayfasi(biletler, min_oncelik, sayfa_no, sayfa_boyutu):
    return []
```

```test
need("bilet_sayfasi")
ornek = [
    {"kod": "B-03", "oncelik": 3, "acik": True},
    {"kod": "B-01", "oncelik": 5, "acik": True},
    {"kod": "B-02", "oncelik": 3, "acik": True},
    {"kod": "B-04", "oncelik": 5, "acik": False},
    {"kod": "B-05", "oncelik": 2, "acik": True},
    {"kod": "B-00", "oncelik": 5, "acik": True},
]
eq(bilet_sayfasi(ornek, 3, 1, 2), ["B-00:5", "B-01:5"], "1. sayfa: oncelik>=3 ve acik olanlar, önce oncelik azalan sonra kod artan")
eq(bilet_sayfasi(ornek, 3, 1, 1), ["B-00:5"], "alt sınır sayfaBoyutu=1 geçerli")
eq(bilet_sayfasi(ornek, 3, 2, 2), ["B-02:3", "B-03:3"], "2. sayfa: Skip(2).Take(2) -> B-02:3 ve B-03:3")
eq(bilet_sayfasi(ornek, 3, 3, 2), [], "3. sayfa: eleman kalmadı -> []")
eq(bilet_sayfasi(ornek, 3, 0, 2), [], "sayfaNo=0 (< 1) -> []")
eq(bilet_sayfasi(ornek, 3, -1, 2), [], "negatif sayfaNo (-1) -> []")
eq(bilet_sayfasi(ornek, 3, 1, 0), [], "sayfaBoyutu=0 (< 1) -> []")
eq(bilet_sayfasi(ornek, 3, 1, -1), [], "negatif sayfaBoyutu (-1) -> []")
```

```solution
def bilet_sayfasi(biletler, min_oncelik, sayfa_no, sayfa_boyutu):
    if sayfa_no < 1 or sayfa_boyutu < 1:
        return []
    secilen = [
        b for b in biletler
        if b["acik"] and b["oncelik"] >= min_oncelik
    ]
    secilen.sort(key=lambda b: (-b["oncelik"], b["kod"]))
    bas = (sayfa_no - 1) * sayfa_boyutu
    return [f"{b['kod']}:{b['oncelik']}" for b in secilen[bas : bas + sayfa_boyutu]]
```

```hint
`OrderByDescending(b => b.Oncelik).ThenBy(b => b.Kod)` sıralaması Python'da `key=lambda b: (-b["oncelik"], b["kod"])` ile birebir kurulur.
```
:::
