---
id: ps08
title: Dosyalar, CSV ve JSON
summary: Get-Content ve Set-Content, kodlama tuzakları, Import-Csv ve Export-Csv, ConvertFrom-Json ve ConvertTo-Json.
---

::: anlat Dosya okumak ve yazmak
```powershell
Set-Content -Path notlar.txt -Value "ilk satır", "ikinci satır" -Encoding UTF8   #! yaz (üzerine)
Add-Content -Path notlar.txt -Value "üçüncü satır" -Encoding UTF8               #! sona ekle
$satirlar = Get-Content -Path notlar.txt -Encoding UTF8                         #! satır dizisi
"$($satirlar.Count) satır, ilki: $($satirlar[0])"
Test-Path notlar.txt
Get-ChildItem -Filter *.txt | ForEach-Object { "$($_.Name) $($_.Length) bayt" }
Join-Path "C:\loglar" "2026\auth.log"                                           #! yol birleştir
```

`Get-Content` dosyayı **satır dizisi** olarak verir; tek metin istiyorsan `-Raw`. `Get-ChildItem` (`ls`, `dir`) dosya **nesneleri** döndürür: `Name`, `Length`, `LastWriteTime`, `FullName` gibi özelliklerle.

> [!TUZAK]
> **Windows PowerShell 5.1'in kodlama tuzakları**: `Out-File` ve `>` varsayılan olarak **UTF-16** yazar; `Get-Content` ve `Import-Csv` BOM'suz UTF-8 dosyaları sistemin eski kod sayfasıyla okur ve Türkçe karakterler bozulur. 5.1'de her zaman `-Encoding UTF8` ver. PowerShell 7'de varsayılan BOM'suz UTF-8'dir ve bu sorun büyük ölçüde yoktur.

### CSV: tablolar nesneye dönüşür
`Import-Csv` başlık satırını özellik adı yapar ve her satırı bir nesneye çevirir; tırnaklı alanları ve içlerindeki virgülleri doğru işler:

```powershell
@"
ad,rol,not
ali,admin,"yetkili, dikkat"
veli,user,
"@ | Set-Content kullanicilar.csv -Encoding UTF8
$k = Import-Csv kullanicilar.csv -Encoding UTF8
$k | Where-Object rol -eq "admin" | ForEach-Object { "$($_.ad): $($_.not)" }
$k | Select-Object ad, rol | Export-Csv cikti.csv -NoTypeInformation -Encoding UTF8
(Get-Content cikti.csv -Encoding UTF8)[0]
```

`@" ... "@` çok satırlı bir **here-string**'dir; Bash'teki here-doc'un karşılığı.

### JSON
```powershell
$olay = '{"kullanici":"ali","roller":["admin","user"],"aktif":true}' | ConvertFrom-Json
$olay.kullanici
$olay.roller -join "/"
[pscustomobject]@{ ip = "10.0.0.5"; port = 443 } | ConvertTo-Json -Compress
```

`ConvertTo-Json` varsayılan olarak sadece **2 seviye** derinliğe iner; daha derin yapılarda iç kısımları metne çevirir. İç içe veride `-Depth 10` ver.

> [!NOT]
> Gerçek bir API'den JSON almak için `Invoke-RestMethod` kullanılır: yanıtı otomatik olarak nesneye çevirir. Python'daki `urllib` + `json` ikilisinin (P52) tek satırlık karşılığıdır.
:::

::: tahmin
Üç satırın çıktısını yaz:

```powershell
$o = '{"ad":"ali","roller":["admin","user"]}' | ConvertFrom-Json
$o.ad
$o.roller.Count
[pscustomobject]@{ x = 1 } | ConvertTo-Json -Compress
```

???

`ali`, `2`, `{"x":1}`. JSON nesnesi özellikli bir nesneye, JSON dizisi PowerShell dizisine dönüşür. `-Compress` boşluksuz tek satır üretir.
:::

::: gorev Yöneticiler
`kullanicilar.csv` dosyasında `ad,rol,not` sütunları var. Rolü `admin` olanların adlarını **alfabetik** sırayla virgülle birleştirip yazdır.

```setup
open("kullanicilar.csv", "w", encoding="utf-8", newline="\n").write(
    'ad,rol,not\nzeynep,admin,"vardiya, gece"\nali,user,\nmert,admin,\nayse,admin,"izinli, pazartesi"\nveli,user,\n')
```

```starter
Get-Content kullanicilar.csv
```

```test
eq(out, "ayse,mert,zeynep\n", "adminler alfabetik")
ok("import-csv" in src.lower(), "Import-Csv kullan")
```

```solution
$kullanicilar = Import-Csv kullanicilar.csv -Encoding UTF8
($kullanicilar | Where-Object rol -eq "admin" | Sort-Object ad | ForEach-Object { $_.ad }) -join ","
```

```hint
`Import-Csv ... | Where-Object rol -eq "admin" | Sort-Object ad`, sonra adları `-join ","` ile birleştir.
```
:::

::: gorev Olay türleri
`olaylar.jsonl` dosyasının her satırı bir JSON olayı. Her olayın `tur` alanına göre say ve `tur: sayı` biçiminde **türe göre alfabetik** yazdır. JSON olmayan bozuk satırları atla.

```setup
satirlar = ['{"tur": "giris", "k": "ali"}', '{"tur": "giris", "k": "root"}', 'BOZUK {{',
            '{"tur": "dosya", "k": "ali"}', '{"tur": "giris", "k": "veli"}', '', '{"tur": "cikis", "k": "ali"}']
open("olaylar.jsonl", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
Get-Content olaylar.jsonl -Encoding UTF8
```

```test
eq(out, "cikis: 1\ndosya: 1\ngiris: 3\n", "türlere göre sayım")
ok("convertfrom-json" in src.lower(), "ConvertFrom-Json kullan")
```

```solution
$olaylar = foreach ($satir in Get-Content olaylar.jsonl -Encoding UTF8) {
    if (-not $satir) { continue }
    try {
        $satir | ConvertFrom-Json -ErrorAction Stop
    } catch {
        continue
    }
}
$olaylar | Group-Object tur | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Count)" }
```

```hint
Her satırı `try { $satir | ConvertFrom-Json -ErrorAction Stop } catch { }` ile dene; sonra `Group-Object tur`.
```
:::

::: gorev Rapor dosyası
`rapor.txt` dosyasını UTF-8 olarak oluştur: `RAPOR`, `disk: tamam`, `ağ: tamam` satırları. Sonra dosyayı okuyup `satır: N` yazdır.

```starter
"RAPOR" > rapor.txt
"satır: 1"
```

```test
eq(out, "satır: 3\n", "3 satır")
icerik = open("rapor.txt", encoding="utf-8-sig").read().splitlines()
eq(icerik, ["RAPOR", "disk: tamam", "ağ: tamam"], "dosya içeriği (UTF-8, Türkçe karakterler bozulmadan)")
```

```solution
Set-Content -Path rapor.txt -Value "RAPOR", "disk: tamam", "ağ: tamam" -Encoding UTF8
$satirlar = Get-Content -Path rapor.txt -Encoding UTF8
"satır: $($satirlar.Count)"
```

```hint
`Set-Content -Path rapor.txt -Value "RAPOR", "disk: tamam", "ağ: tamam" -Encoding UTF8`. `>` ise 5.1'de UTF-16 yazar.
```
:::
