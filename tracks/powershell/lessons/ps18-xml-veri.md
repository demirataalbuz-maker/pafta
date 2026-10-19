---
id: ps18
title: XML ve Veri Biçimleri
summary: [xml] ile XML okumak, öğe ve öznitelik gezinmesi, Select-Xml ve XPath, XML değiştirip kaydetmek, Export-Clixml ile nesneleri eksiksiz saklamak ve ConvertFrom-StringData.
---

::: anlat XML'i nesne gibi gezmek
Windows dünyasında yapılandırma dosyaları, olay günlüğü kayıtları, grup ilkesi raporları ve zamanlanmış görev tanımları çoğunlukla **XML**'dir. PowerShell bir XML metnini `[xml]` dönüşümüyle gezilebilir bir nesneye çevirir; öğeler ve öznitelikler nokta ile erişilen özelliklere dönüşür:

```powershell
[xml]$x = @"
<sunucular>
  <sunucu ad="web01" rol="web"><cpu>72</cpu><etiket>uretim</etiket></sunucu>
  <sunucu ad="db01" rol="db"><cpu>91</cpu><etiket>uretim</etiket><etiket>kritik</etiket></sunucu>
  <sunucu ad="test01" rol="test"><cpu>3</cpu></sunucu>
</sunucular>
"@
$x.sunucular.sunucu.Count
$x.sunucular.sunucu | ForEach-Object { "{0,-7} {1,-5} {2}" -f $_.ad, $_.rol, $_.cpu }
```

Öznitelikler (`ad="web01"`) ve tek metinli öğeler (`<cpu>72</cpu>`) aynı şekilde okunur. Değerler **metindir**; sayısal karşılaştırmadan önce `[int]` ile çevir.

### XPath ile sorgu
`Select-Xml` bir XPath ifadesiyle eşleşen düğümleri döndürür; her sonucun `.Node` özelliği düğümün kendisidir:

| XPath | Anlamı |
|---|---|
| `//sunucu` | belgenin herhangi bir yerindeki bütün `sunucu` öğeleri |
| `//sunucu[@rol='web']` | `rol` özniteliği web olanlar |
| `//sunucu[cpu > 80]/@ad` | CPU'su 80'den büyüklerin `ad` öznitelikleri |
| `//sunucu[etiket='kritik']` | etiketlerinden biri kritik olanlar |
| `count(//etiket)` | sayım (XPath fonksiyonu) |

```powershell
[xml]$x = '<s><u ad="web01" rol="web"><cpu>72</cpu></u><u ad="db01" rol="db"><cpu>91</cpu></u></s>'
Select-Xml -Xml $x -XPath "//u[cpu > 80]/@ad" | ForEach-Object { $_.Node.Value }
Select-Xml -Xml $x -XPath "//u[@rol='web']" | ForEach-Object { $_.Node.ad }
```

### Değiştirmek ve kaydetmek
```powershell
[xml]$x = '<s><u ad="web01"><cpu>72</cpu></u></s>'
$u = $x.s.u
$u.SetAttribute("durum", "normal")
$yeni = $x.CreateElement("not")
$yeni.InnerText = "bakım pazar"
[void]$u.AppendChild($yeni)
$x.Save("$PWD\yeni.xml")
Get-Content yeni.xml
```

### Nesneleri eksiksiz saklamak
`Export-Clixml` bir nesneyi bütün özellikleri ve türleriyle XML'e yazar, `Import-Clixml` aynen geri getirir. CSV'nin aksine iç içe yapılar ve türler kaybolmaz; bir makinede toplanan veriyi başka yerde incelemek için kullanılır. `ConvertFrom-StringData` ise `anahtar=değer` satırlarını hashtable'a çevirir:

```powershell
"port=8080`nhost=web01" | ConvertFrom-StringData
```

> [!GÜVENLİK]
> Güvenilmeyen kaynaktan gelen XML'i işlerken dış varlık (external entity) çözümlemesi kapalı olmalıdır. PowerShell'in `[xml]` dönüşümü ve .NET'in varsayılan XmlDocument ayarları güncel .NET sürümlerinde dış varlıkları çözümlemez; başka dillerde ya da eski kütüphanelerde bu ayarı açıkça denetle.
:::

::: tahmin
Dört satır yazar:

```powershell
[xml]$x = '<s><u ad="web01"><cpu>72</cpu></u><u ad="db01"><cpu>91</cpu></u></s>'
$x.s.u.Count
$x.s.u[1].ad
($x.s.u | Where-Object { [int]$_.cpu -gt 80 }).ad
@(Select-Xml -Xml $x -XPath "//u[cpu > 50]").Count
```

???

`2`, `db01`, `db01`, `2`. İki `u` öğesi var; ikincisinin `ad` özniteliği db01. CPU'su 80'i aşan yalnızca db01. XPath ifadesindeki `cpu > 50` iki öğeyi de tutar.
:::

::: gorev Sunucu listesi
`sunucular.xml` dosyasındaki her sunucu için `ad rol cpu` yazdır; CPU'ya göre **büyükten küçüğe**.

```setup
open("sunucular.xml", "w", encoding="utf-8", newline="\n").write(
    '<sunucular>\n'
    '  <sunucu ad="web01" rol="web"><cpu>72</cpu><etiket>uretim</etiket></sunucu>\n'
    '  <sunucu ad="db01" rol="db"><cpu>91</cpu><etiket>uretim</etiket><etiket>kritik</etiket></sunucu>\n'
    '  <sunucu ad="test01" rol="test"><cpu>3</cpu></sunucu>\n'
    '  <sunucu ad="cache01" rol="onbellek"><cpu>84</cpu><etiket>kritik</etiket></sunucu>\n'
    '</sunucular>\n')
```

```starter
Get-Content sunucular.xml
```

```test
eq(out, "db01 db 91\ncache01 onbellek 84\nweb01 web 72\ntest01 test 3\n", "CPU'ya göre azalan")
```

```solution
[xml]$x = Get-Content sunucular.xml -Raw -Encoding UTF8
$x.sunucular.sunucu |
    Sort-Object { [int]$_.cpu } -Descending |
    ForEach-Object { "$($_.ad) $($_.rol) $($_.cpu)" }
```

```hint
`[xml]$x = Get-Content sunucular.xml -Raw`; sunucular `$x.sunucular.sunucu`. CPU metin olduğu için sıralarken `{ [int]$_.cpu }`.
```
:::

::: gorev XPath ile seç
`sunucular.xml` dosyasından **kritik** etiketli sunucuların adlarını alfabetik sırayla yazdır. `Select-Xml` ve XPath kullan.

```setup
open("sunucular.xml", "w", encoding="utf-8", newline="\n").write(
    '<sunucular>\n'
    '  <sunucu ad="web01" rol="web"><cpu>72</cpu><etiket>uretim</etiket></sunucu>\n'
    '  <sunucu ad="db01" rol="db"><cpu>91</cpu><etiket>uretim</etiket><etiket>kritik</etiket></sunucu>\n'
    '  <sunucu ad="test01" rol="test"><cpu>3</cpu></sunucu>\n'
    '  <sunucu ad="cache01" rol="onbellek"><cpu>84</cpu><etiket>kritik</etiket></sunucu>\n'
    '</sunucular>\n')
```

```starter
[xml]$x = Get-Content sunucular.xml -Raw -Encoding UTF8
$x.sunucular.sunucu.ad
```

```test
eq(out, "cache01\ndb01\n", "iki kritik sunucu")
ok("Select-Xml" in src, "Select-Xml kullan")
```

```solution
Select-Xml -Path sunucular.xml -XPath "//sunucu[etiket='kritik']/@ad" |
    ForEach-Object { $_.Node.Value } |
    Sort-Object
```

```hint
XPath: `//sunucu[etiket='kritik']/@ad`. Öznitelik düğümünün değeri `$_.Node.Value`.
```
:::

::: gorev İşaretle ve kaydet
`sunucular.xml` dosyasında CPU'su **80 ve üstü** olan her sunucuya `durum="yogun"` özniteliğini ekle, sonucu `yeni.xml` olarak kaydet ve kaç sunucunun işaretlendiğini `N sunucu işaretlendi` olarak yazdır.

```setup
open("sunucular.xml", "w", encoding="utf-8", newline="\n").write(
    '<sunucular>\n'
    '  <sunucu ad="web01" rol="web"><cpu>72</cpu></sunucu>\n'
    '  <sunucu ad="db01" rol="db"><cpu>91</cpu></sunucu>\n'
    '  <sunucu ad="cache01" rol="onbellek"><cpu>84</cpu></sunucu>\n'
    '</sunucular>\n')
```

```starter
[xml]$x = Get-Content sunucular.xml -Raw -Encoding UTF8
"0 sunucu işaretlendi"
```

```test
import xml.etree.ElementTree as ET
eq(out, "2 sunucu işaretlendi\n", "iki sunucu")
kok = ET.parse("yeni.xml").getroot()
durum = {s.get("ad"): s.get("durum") for s in kok.findall("sunucu")}
eq(durum, {"web01": None, "db01": "yogun", "cache01": "yogun"}, "yeni.xml'deki öznitelikler")
```

```solution
[xml]$x = Get-Content sunucular.xml -Raw -Encoding UTF8
$isaretli = 0
foreach ($s in $x.sunucular.sunucu) {
    if ([int]$s.cpu -ge 80) {
        $s.SetAttribute("durum", "yogun")
        $isaretli++
    }
}
$x.Save("$PWD\yeni.xml")
"$isaretli sunucu işaretlendi"
```

```hint
Her `sunucu` düğümünde `[int]$s.cpu -ge 80` ise `$s.SetAttribute("durum", "yogun")`.
```

```hint
`Save` tam yol ister: `$x.Save("$PWD\yeni.xml")`.
```
:::
