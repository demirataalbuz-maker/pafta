---
id: kq03
title: Metin İşleçleri
summary: contains ile has farkı, startswith/endswith, == ile =~, olumsuz işleçler, matches regex ve extract ile metinden parça çıkarmak.
---

::: anlat contains mi has mi?
Kayıt sorgularının büyük kısmı metin aramaktır. KQL'in metin işleçleri varsayılan olarak **büyük-küçük harfe duyarsızdır**:

| İşleç | Doğru olduğu durum | Örnek |
|---|---|---|
| `contains` | metnin **herhangi bir yerinde** geçiyorsa | `"Disk doluluğu" contains "isk"` |
| `has` | **bütün bir terim** olarak geçiyorsa | `"Disk doluluğu" has "disk"` |
| `startswith`, `endswith` | baştan / sondan eşleşiyorsa | `"web01" startswith "web"` |
| `=~` | büyük-küçük harf gözetmeden eşitse | `"web01" =~ "WEB01"` |
| `==` | **harfi harfine** eşitse | `"web01" == "WEB01"` yanlış |

Her birinin olumsuzu başına `!` alır: `!contains`, `!has`, `!startswith`, `!in`. Harfe duyarlı sürümler `_cs` ekiyle biter: `contains_cs`, `has_cs`.

```kql
biletler
| where baslik has "disk"
| project id, baslik

biletler
| where baslik contains "sun"           #! "sunucusu" içinde geçer
| project id, baslik

sunucular
| where isletim !startswith "Windows"
| project ad, isletim
```

> [!DERİN]
> Gerçek Kusto'da `has`, `contains`'ten çok daha hızlıdır: Kusto her metni terimlere ayırıp dizinler, `has` doğrudan bu dizine bakar; `contains` ise her satırın metnini baştan sona tarar. Milyarlarca satırlık tablolarda bu fark saniyelerle dakikalar arasındaki farktır. Aradığın şey bütün bir kelimeyse `has` kullan.

### Düzenli ifade ve extract
`matches regex` bir deseni sınar, `extract(desen, grup, metin)` desenin yakaladığı grubu çıkarır. Desenleri `@"..."` biçiminde **ham metin** olarak yaz; böylece `\d` gibi ters eğik çizgiler olduğu gibi kalır (Regex yolundan tanıdığın sözdizimi):

```kql
sunucular
| where ad matches regex @"^(web|db)\d+$"
| project ad

sunucular
| extend surum = extract(@"(\d+)\.\d+", 1, isletim)
| project ad, isletim, surum
```

> [!TUZAK]
> `has` terim arar: `"Disk doluluğu" has "dis"` **yanlıştır**, çünkü "dis" tek başına bir terim değil. Kelimenin bir parçasını arıyorsan `contains` gerekir.
:::

::: tahmin
Üç sorgu, üç sayı:

```kql
biletler
| where baslik contains "web"
| count

biletler
| where baslik has "we"
| count

biletler
| where baslik startswith "Disk"
| count
```

???

`2`, `0`, `3`. İki bilet başlığı "Web sunucusu 502 dönüyor"; `contains` büyük-küçük harf gözetmez ve bulur. Hiçbir başlıkta "we" tek başına bir terim değil, `has` hiçbirini bulmaz. Üç başlık "Disk doluluğu" ile başlıyor.
:::

::: gorev Disk biletleri
Başlığında **disk** kelimesi geçen biletlerin `id` ve `durum` sütunlarını getir.

```starter
biletler
| where baslik == "disk"
| project id, durum
```

```test
eq(sorted(sonuc), [(1, "çözüldü"), (13, "çözüldü"), (20, "açık")], "1, 13 ve 20 numaralı biletler")
```

```solution
biletler
| where baslik has "disk"
| project id, durum
```

```hint
`==` harfi harfine bütün başlığı karşılaştırır. Bir kelimeyi aramak için `has "disk"`.
```
:::

::: gorev Debian dışındakiler
İşletim sistemi `Debian` ile **başlamayan** sunucuların adlarını getir.

```starter
sunucular
| where isletim startswith "Debian"
| project ad
```

```test
eq(sorted(r[0] for r in sonuc), sorted(r[0] for r in sorgu("SELECT ad FROM sunucular WHERE isletim NOT LIKE 'Debian%'")), "Debian olmayan sekiz sunucu")
eq(len(sonuc), 8, "8 sunucu")
```

```solution
sunucular
| where isletim !startswith "Debian"
| project ad
```

```hint
Olumsuz işleç: `!startswith`.
```
:::

::: gorev Ubuntu sürümleri
Ubuntu çalıştıran sunucular için `ad` ve işletim sisteminden çıkarılmış sürüm numarasını (`24.04` gibi) `surum` adıyla getir; `extract` kullan.

```starter
sunucular
| where isletim startswith "Ubuntu"
| project ad, isletim
```

```test
eq(sutunlar, ["ad", "surum"], "sütunlar: ad, surum")
eq(sorted(sonuc), [("cache01", "24.04"), ("izleme01", "22.04"), ("test01", "24.04"), ("web01", "24.04"), ("web02", "24.04"), ("web03", "22.04")], "altı Ubuntu sunucusu ve sürümleri")
ok(kullanir("extract"), "extract kullan")
```

```solution
sunucular
| where isletim startswith "Ubuntu"
| project ad, surum = extract(@"(\d+\.\d+)", 1, isletim)
```

```hint
Desen: `@"(\d+\.\d+)"`: rakamlar, bir nokta, rakamlar. `1` birinci grubu ister.
```
:::
