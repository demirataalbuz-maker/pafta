---
id: cs17
title: XML Ayrıştırıcı Ayarları · DTD ve Dış Varlık Sınırı
summary: .NET 8'de XmlReaderSettings varsayılanı DtdProcessing.Prohibit'tir ve DTD içeren belge XmlException verir; Ignore da varlık başvurusunu çözmez. Dış varlığın okunması için iki ayrı gevşetme gerekir: DtdProcessing.Parse ve bir XmlResolver. Parse + XmlResolver null durumunda dış varlık hata vermeden sessizce boş gelir; XmlResolver özelliği yalnız yazılabilir olduğu için mevcut değeri koddan okuyamazsın, yapılandırmayı okumak zorundasın.
---

::: anlat Varsayılan kapalıdır
`CS07`'de yol birleştirmedeki sınırı gördün. XML ayrıştırmada benzer bir sınır **DTD** ve **dış varlık** (external entity) çevresindedir: bir XML belgesi kendi içinde kısaltma tanımlayabilir, hatta bu kısaltmanın içeriğini başka bir kaynaktan çekmesini isteyebilir.

```xml norun
<!DOCTYPE k [<!ENTITY ic "IC-DEGER">]><k>&ic;</k>                  <!-- iç varlık -->
<!DOCTYPE k [<!ENTITY dis SYSTEM "file:///.../dosya.txt">]><k>&dis;</k>   <!-- dış varlık -->
```

İkincisi, ayrıştırıcıyı belgenin seçtiği bir kaynağı okumaya yönlendirir. .NET 8 bunu varsayılan olarak kapatır. Ölçüldü (.NET 8.0.31):

```csharp norun
new XmlReaderSettings().DtdProcessing   // Prohibit
```

`DtdProcessing` üç değer alır ve ölçülen davranışları şöyledir (belge bir varlık başvurusu içeriyor):

| `DtdProcessing` | `XmlResolver` | Sonuç |
|---|---|---|
| `Prohibit` (varsayılan) | — | `XmlException` |
| `Ignore` | — | `XmlException` |
| `Parse` | `null` | iç varlık genişler: `IC-DEGER` |
| `Parse` | `null`, **dış** varlık | **hata yok**, içerik boş |
| `Parse` | `XmlUrlResolver`, **dış** varlık | içerik okunur |

`Prohibit` ile `Ignore` farklı gerekçelerle aynı sonucu verir: ilki DTD'yi yasaklar, ikincisi atlar — atlanınca `&ic;` tanımsız bir varlık olur ve yine `XmlException` çıkar.

Dikkat edilecek nokta, bir belgenin dış kaynağa ulaşması için **iki** ayrı ayarın birlikte gevşetilmiş olması gerektiğidir: `DtdProcessing = Parse` **ve** bir çözücü. Kod incelemesinde ikisini ayrı ayrı aramak gerekir; biri tek başına yeterli değildir.
:::

::: anlat Sessiz boşluk ve okunamayan ayar
Tablodaki dördüncü satır en kolay gözden kaçandır: `DtdProcessing = Parse` ama `XmlResolver = null` iken **dış** varlığa başvuran bir belge hata vermez; varlık boş dizgiye çözülür ve program hiçbir şey olmamış gibi devam eder.

```csharp norun
var ayar = new XmlReaderSettings { DtdProcessing = DtdProcessing.Parse, XmlResolver = null };
// <k>&dis;</k>  ->  InnerText == ""   (XmlException YOK)
```

Bu iyi haber gibi durur — dış kaynak okunmadı — ama bir sorun doğurur: veri **sessizce kayboluyor**. Belgenin bir alanını bekleyen kod boş dizgi alır ve bunu "alan boş gelmiş" diye yorumlar. Beklenen davranış buysa sorun yok; değilse, DTD'yi hiç kabul etmemek (`Prohibit`) daha dürüst bir yapılandırmadır: orada en azından bir istisna alırsın.

> [!TUZAK] Mevcut çözücüyü koddan soramazsın
> `XmlReaderSettings.XmlResolver` **yalnız yazılabilir** bir özelliktir; okumaya çalışmak derleme hatası verir (`lacks the get accessor`). Yani çalışan bir nesneye bakıp "bunun çözücüsü ne?" diye soramazsın. Bir incelemede tek yol, ayarların kurulduğu kodu okumaktır: `XmlReaderSettings`'in nerede oluşturulduğunu, hangi alanlarının atandığını ve o nesnenin hangi `XmlReader.Create` çağrılarına geçtiğini izle.

Daha yüksek seviyedeki tiplerde de aynı soruyu sor: .NET Core/.NET 5+ üzerinde `XmlDocument`'ın `XmlResolver`'ı varsayılan olarak `null`'dır, ama kod onu açıkça atayabilir. "Varsayılan güvenli" bilgisi, o varsayılanın değiştirilmediğini doğrulamadan güvence değildir.
:::

::: tahmin Beş yapılandırma, kaç istisna?
Belge ya iç varlığa (`&ic;`) ya da dış varlığa (`&dis;`) başvuruyor; dış varlık yerel bir dosyayı gösteriyor ve o dosyanın içeriği `DISARIDAN-GELEN-ICERIK`.

```csharp
Console.WriteLine(new XmlReaderSettings().DtdProcessing);
Dene("1 ic-entity  varsayilan ", icEntity,  DtdProcessing.Prohibit, null);
Dene("2 ic-entity  Ignore     ", icEntity,  DtdProcessing.Ignore,   null);
Dene("3 ic-entity  Parse      ", icEntity,  DtdProcessing.Parse,    null);
Dene("4 dis-entity Parse+null ", disEntity, DtdProcessing.Parse,    null);
Dene("5 dis-entity Parse+resol", disEntity, DtdProcessing.Parse,    new XmlUrlResolver());
```

```gercek
Prohibit
1 ic-entity  varsayilan : XmlException
2 ic-entity  Ignore     : XmlException
3 ic-entity  Parse      : OK icerik=[IC-DEGER]
4 dis-entity Parse+null : OK icerik=[]
5 dis-entity Parse+resol: OK icerik=[DISARIDAN-GELEN-ICERIK]
```

???

İlk satır varsayılanı doğruluyor: **`Prohibit`**. Hiçbir şey yapmadığında ayrıştırıcı DTD'yi reddeder.

`1` ve `2` aynı sonucu farklı gerekçeyle verir. `Prohibit` DTD'yi yasakladığı için, `Ignore` ise DTD'yi atladığı ve geriye tanımsız bir `&ic;` kaldığı için `XmlException` çıkar.

`3`: `Parse` ile iç varlık genişler. Burada dışarıdan bir şey okunmuyor; tehlike iç varlıkta değil.

`4`: **hata yok ama içerik boş**. `Parse` açık, çözücü yok: ayrıştırıcı dış varlığı çözmeye yetkili değil ve bunu sessizce geçiyor. Bu satırı tahmin ederken çoğu kişi istisna bekler.

`5`: iki gevşetme bir arada — `Parse` **ve** bir `XmlUrlResolver`. Ancak o zaman belgenin gösterdiği kaynak okunur ve içeriği belgeye girer.
:::

::: gorev Yapılandırma sonucunu söyle
`oku(dtd, cozucuVar, varlik)` yaz: bir `XmlReader` yapılandırmasının, varlık başvurusu içeren bir belgede ne üreteceğini döndür.

- `dtd`: `"Prohibit"`, `"Ignore"` ya da `"Parse"`.
- `cozucuVar`: bir `XmlResolver` atanmış mı.
- `varlik`: `"ic"` ya da `"dis"`.

Dönüş:

- `"Prohibit"` ya da `"Ignore"` ise `"XmlException"`.
- `"Parse"` ve `varlik == "ic"` ise `"IC-DEGER"`.
- `"Parse"`, `varlik == "dis"` ve çözücü **yoksa** `""` (boş dizgi, istisna yok).
- `"Parse"`, `varlik == "dis"` ve çözücü **varsa** `"DISARIDAN-GELEN-ICERIK"`.

```starter
def oku(dtd, cozucuVar, varlik):
    if dtd == "Prohibit":
        return "XmlException"
    return "IC-DEGER" if varlik == "ic" else "DISARIDAN-GELEN-ICERIK"
```

```test
need("oku")
eq(oku("Prohibit", False, "ic"), "XmlException", "ölçülen varsayılan: DTD yasak")
eq(oku("Prohibit", True, "dis"), "XmlException", "çözücü atansa da Prohibit kazanır")
eq(oku("Ignore", False, "ic"), "XmlException", "ölçülen: Ignore'da varlık tanımsız kalır")
eq(oku("Ignore", True, "dis"), "XmlException", "Ignore'da çözücünün etkisi yok")
eq(oku("Parse", False, "ic"), "IC-DEGER", "iç varlık genişler")
eq(oku("Parse", True, "ic"), "IC-DEGER", "iç varlık için çözücü gerekmez")
eq(oku("Parse", False, "dis"), "", "ölçülen: dış varlık sessizce boş gelir, istisna yok")
eq(oku("Parse", True, "dis"), "DISARIDAN-GELEN-ICERIK", "iki gevşetme bir arada: içerik okunur")
```

```solution
def oku(dtd, cozucuVar, varlik):
    if dtd in ("Prohibit", "Ignore"):
        return "XmlException"
    if varlik == "ic":
        return "IC-DEGER"
    return "DISARIDAN-GELEN-ICERIK" if cozucuVar else ""
```

```hint
Başlangıç kodu iki şeyi kaçırıyor: `Ignore` da istisna verir, ve `Parse` + dış varlık + çözücü **yokken** sonuç boş dizgidir. Çözücü yalnız `Parse` ve dış varlık birlikteyken fark yaratır.
```
:::

::: gorev Yapılandırmaları denetle
`denetle(ayarlar)` yaz: bir kod tabanında bulunan `XmlReaderSettings` yapılandırmalarını sınıflandır. Her ayar `(dtd, cozucuVar)` demetidir.

Sınıflar:

- `"guvenli"`: `dtd` `"Prohibit"` ya da `"Ignore"`.
- `"ic-varlik"`: `"Parse"` ve çözücü yok — iç varlıklar genişler, dış varlık sessizce boş gelir.
- `"dis-varlik"`: `"Parse"` ve çözücü var — belge dış kaynak okutabilir.

Dönüş `(siniflar, incelenecek)`: `siniflar` girdi sırasıyla sınıf adlarının listesi, `incelenecek` ise `"guvenli"` olmayanların sayısı.

```starter
def denetle(ayarlar):
    siniflar = ["guvenli" if d == "Prohibit" else "dis-varlik" for d, _ in ayarlar]
    return (siniflar, len(ayarlar))
```

```test
need("denetle")
eq(denetle([("Prohibit", False)]), (["guvenli"], 0), "varsayılan yapılandırma")
eq(denetle([("Ignore", True)]), (["guvenli"], 0), "Ignore da güvenli sayılır, çözücü önemsiz")
eq(denetle([("Parse", False)]), (["ic-varlik"], 1), "Parse tek başına incelenmeli")
eq(denetle([("Parse", True)]), (["dis-varlik"], 1), "iki gevşetme bir arada")
eq(denetle([("Prohibit", False), ("Parse", True), ("Ignore", False), ("Parse", False)]),
   (["guvenli", "dis-varlik", "guvenli", "ic-varlik"], 2), "karışık liste, sıra korunur")
eq(denetle([]), ([], 0), "hiç yapılandırma yok")
eq(denetle([("Parse", True), ("Parse", True)]), (["dis-varlik", "dis-varlik"], 2), "ikisi de sayılır")
```

```solution
def denetle(ayarlar):
    siniflar = []
    for dtd, cozucuVar in ayarlar:
        if dtd in ("Prohibit", "Ignore"):
            siniflar.append("guvenli")
        elif cozucuVar:
            siniflar.append("dis-varlik")
        else:
            siniflar.append("ic-varlik")
    return (siniflar, sum(1 for s in siniflar if s != "guvenli"))
```

```hint
Başlangıç kodu `Ignore`'u güvensiz sayıyor ve her ayarı incelenecek listesine koyuyor. Önce `dtd`'ye bak: güvenli ikiliyse çözücüye hiç bakma. Sayıyı sınıflandırmadan sonra, `"guvenli"` olmayanları sayarak çıkar.
```
:::
