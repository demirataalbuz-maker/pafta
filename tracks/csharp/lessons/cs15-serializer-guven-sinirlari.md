---
id: cs15
title: Serializer'larda Güvenilmeyen Veri Akışı
summary: Bir serializer'ın temel sorusu "veriyi kim okuyor" değil, "türü kim seçiyor": BinaryFormatter .NET 8'de hem derleme hatası (SYSLIB0011) hem çalışma anında NotSupportedException; System.Text.Json türü veriye hiç seçtirmiyor — object olarak çözünce JsonElement verir, soyut hedefte ve $type alanıyla NotSupportedException atar; çoklu biçim ancak geliştirici [JsonDerivedType] ile kapalı bir ayrımcı listesi bildirirse çalışır ve liste dışındaki tür, gerçek bir alt sınıf olsa bile reddedilir.
---

::: anlat Asıl soru: türü kim seçiyor?
`CS11`'de `System.Text.Json` ile nesne okudun. Güvenilmeyen veriyle çalışırken serializer'ları ayıran şey hız ya da biçim değildir; **hangi tarafın tür seçtiğidir**.

| Model | Türü kim belirler | Sonuç |
|---|---|---|
| Veri türü adlandırır | gelen yük | yük, kurulacak nesneyi seçer |
| Geliştirici türü bildirir | kod | yük yalnız alanları doldurur |

`BinaryFormatter` birinci modeldeydi: akışın içinde tür adları taşınır ve okuma sırasında o türler kurulurdu. .NET 8'de bu API hem derlemede hem çalışmada kapalıdır. Ölçüldü (.NET 8.0.31):

- Kaynakta kullanmak `SYSLIB0011` **hatası** verir — uyarı değil, hata; derlenmesi için açıkça bastırman gerekir.
- Bastırıp çalıştırırsan `Serialize` bile **`NotSupportedException`** atar.

> [!TUZAK] "Binder yazarım" bir güvenlik çözümü değildir
> Eski kodda `SerializationBinder` ile gelen tür adlarını süzmek yaygın bir yamadır. Bunu bir çözüm gibi sunma: binder, türü hâlâ **yükün** seçmesine izin veren bir modelin üstüne konmuş bir süzgeçtir ve Microsoft'un kendi rehberi bu API'nin güvenilmeyen veriyle kullanılmamasını söyler. Doğru hamle süzgeci iyileştirmek değil, türü veriye seçtirmeyen bir biçime geçmektir.
:::

::: anlat System.Text.Json ne yapmıyor
`System.Text.Json` ikinci modeldedir ve bunu varsayılan davranışıyla gösterir. Ölçülenler:

| Yapılan | Sonuç |
|---|---|
| Bilinmeyen fazla alan | sessizce **yok sayılır** |
| `Deserialize<object>` | `JsonElement` döner, rastgele bir tür kurulmaz |
| Soyut bir hedefe çözmek | `NotSupportedException` |
| Yükte `"$type"` alanı olması | tek başına **hiçbir şey yapmaz**: `NotSupportedException` |

Son satır önemlidir: `$type` sihirli bir anahtar değildir. Çoklu biçim ancak geliştirici kodda **kapalı bir liste** bildirirse çalışır:

```csharp norun
[JsonDerivedType(typeof(Oku), "oku")]
[JsonDerivedType(typeof(Yaz), "yaz")]
public abstract class Istek { }
public class Gizli : Istek { public string Komut { get; set; } = ""; }   // bildirilmedi
```

Bu bildirimle ölçülenler: `"$type":"oku"` → `Oku`, `"$type":"yaz"` → `Yaz`. Buna karşılık `"$type":"gizli"` **`JsonException`** verir — `Gizli` gerçek bir alt sınıftır ama listede yoktur. `"$type":"Gizli"` diye **sınıf adını** vermek de `JsonException` verir; ayrımcılar sınıf adı değil, geliştiricinin seçtiği etiketlerdir.

Yani yük bir tür *adlandıramaz*; yalnız listedeki etiketlerden birini *seçebilir*. Aradaki fark, bu konunun tamamıdır.

Sıkılık bir ayar daha ister: fazla alanlar varsayılanda yok sayılır, `JsonUnmappedMemberHandling.Disallow` ile `JsonException` olur. Bir API'de "gönderilen ama tanınmayan alan" sessizce düşsün mü yoksa reddedilsin mi, bilinçli bir karardır.
:::

::: tahmin Hangi çağrı hangi hatayı verir?
```csharp
// 1
var bf = new BinaryFormatter();           // SYSLIB0011 bastırılmış
bf.Serialize(new MemoryStream(), new Ayar { Ad = "x", Port = 1 });
// 2
var a = JsonSerializer.Deserialize<Ayar>("{\"Ad\":\"web\",\"Port\":80,\"Fazla\":1}");
// 3
var o = JsonSerializer.Deserialize<object>("{\"Ad\":\"web\"}");
// 4  Taban soyut, [JsonDerivedType] YOK
var t4 = JsonSerializer.Deserialize<Taban>("{\"Tur\":\"Alt\",\"Komut\":\"x\"}");
// 5
var t5 = JsonSerializer.Deserialize<Taban>("{\"$type\":\"Alt\",\"Komut\":\"x\"}");
```

```gercek
1 BinaryFormatter.Serialize: NotSupportedException
2 fazla alan: Ad=web Port=80
3 object olarak: JsonElement
4 soyut taban: NotSupportedException
5 $type ile: NotSupportedException
```

???

`1`: `BinaryFormatter` .NET 8'de yalnız "önerilmiyor" değil, **çalışmıyor**. Derleyici `SYSLIB0011` hatası veriyor; bastırsan bile çalışma anında `NotSupportedException`. Yazma yönü bile kapalı, okuma yönü de öyle.

`2`: `Fazla` alanı yoktu ve **hata da olmadı**; varsayılan davranış bilinmeyen alanı sessizce atmaktır. Bir alan adını yanlış yazmış olsan da aynı sessizlikle karşılaşırsın.

`3`: `object` istemek "ne gelirse onu kur" demek değildir; elinde **`JsonElement`** olur, yani çözümlenmiş ama henüz bir türe bağlanmamış veri.

`4` ve `5`: ikisi de `NotSupportedException`. Soyut bir tür kurulamaz ve `$type` yazmak bunu değiştirmez — ayrımcı listesi kodda bildirilmediği sürece yükün tür seçme yetkisi yoktur. Bu, `BinaryFormatter`'dan ayrıldığı noktadır.
:::

::: gorev Ayrımcı listesi
`coz(ayrimci, izinliler, hedefSoyut)` yaz: bir JSON yükünün hangi türe çözüleceğini modelle.

- `ayrimci`: yükteki `$type` değeri; yoksa `None`.
- `izinliler`: `[JsonDerivedType]` ile bildirilmiş `{etiket: tür adı}` sözlüğü.
- `hedefSoyut`: hedef tür soyut mu.

Kurallar (ölçüldü):

- `ayrimci` verilmişse ve `izinliler` içindeyse o türün adını döndür.
- `ayrimci` verilmiş ama listede yoksa `"JsonException"` döndür — gerçek bir alt sınıfın adı olsa bile.
- `ayrimci` yoksa: hedef soyutsa `"NotSupportedException"`, değilse `"hedef"`.

```starter
def coz(ayrimci, izinliler, hedefSoyut):
    if ayrimci:
        return izinliler.get(ayrimci, ayrimci)
    return "hedef"
```

```test
need("coz")
IZIN = {"oku": "Oku", "yaz": "Yaz"}
eq(coz("oku", IZIN, True), "Oku", "bildirilmiş etiket")
eq(coz("yaz", IZIN, True), "Yaz", "listenin ikinci etiketi")
eq(coz("gizli", IZIN, True), "JsonException", "gerçek alt sınıf olsa da listede yoksa reddedilir")
eq(coz("Gizli", IZIN, True), "JsonException", "sınıf adı vermek de işe yaramaz")
eq(coz(None, IZIN, True), "NotSupportedException", "ayrımcı yok ve hedef soyut")
eq(coz(None, IZIN, False), "hedef", "ayrımcı yok ama hedef somut: alanlar doldurulur")
eq(coz(None, {}, False), "hedef", "liste boş olsa da somut hedef çözülür")
eq(coz("oku", {}, True), "JsonException", "hiç bildirim yoksa her etiket reddedilir")
```

```solution
def coz(ayrimci, izinliler, hedefSoyut):
    if ayrimci is None:
        return "NotSupportedException" if hedefSoyut else "hedef"
    if ayrimci in izinliler:
        return izinliler[ayrimci]
    return "JsonException"
```

```hint
Başlangıç kodu listede bulunmayan etiketi olduğu gibi döndürüyor — yani yükün tür adlandırmasına izin veriyor. Listede olmayan her etiket `"JsonException"` olmalı; liste dışına çıkış yok.
```
:::

::: gorev Tanınmayan alanlar
`baglan(govde, alanlar, sert)` yaz: bir JSON gövdesini hedef türün alanlarına bağla.

- `govde`: gelen anahtar-değer sözlüğü.
- `alanlar`: hedef türün alan adları kümesi.
- `sert`: `JsonUnmappedMemberHandling.Disallow` açık mı.

Dönüş: sert kipte tanınmayan bir alan varsa `("JsonException", <ilk tanınmayan alan>)`; değilse `("tamam", <bağlanan alan sayısı>)`. Tanınmayan alanlar gevşek kipte sessizce atılır. Alanlar `govde`'deki sırayla değerlendirilir.

```starter
def baglan(govde, alanlar, sert):
    return ("tamam", len(govde))
```

```test
need("baglan")
A = {"Ad", "Port"}
eq(baglan({"Ad": "web", "Port": 80}, A, False), ("tamam", 2), "hepsi tanınıyor")
eq(baglan({"Ad": "web", "Port": 80}, A, True), ("tamam", 2), "sert kipte de sorun yok")
eq(baglan({"Ad": "web", "Fazla": 1}, A, False), ("tamam", 1),
   "ölçülen varsayılan: tanınmayan alan sessizce atılır, sayıya girmez")
eq(baglan({"Ad": "web", "Fazla": 1}, A, True), ("JsonException", "Fazla"), "sert kipte reddedilir")
eq(baglan({"Bir": 1, "Iki": 2}, A, True), ("JsonException", "Bir"), "ilk tanınmayan alan bildirilir")
eq(baglan({}, A, True), ("tamam", 0), "boş gövde")
eq(baglan({"port": 80}, A, False), ("tamam", 0),
   "alan adı büyük/küçük harfiyle tutmuyorsa tanınmaz sayılır")
```

```solution
def baglan(govde, alanlar, sert):
    bagli = 0
    for anahtar in govde:
        if anahtar in alanlar:
            bagli += 1
        elif sert:
            return ("JsonException", anahtar)
    return ("tamam", bagli)
```

```hint
Tek bir döngü yeter: tanınan alanı say, tanınmayanı sert kipte hemen bildir. `len(govde)` kullanma — tanınmayan alanlar sayıya girmemeli.
```
:::
