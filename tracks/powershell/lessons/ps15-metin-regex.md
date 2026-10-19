---
id: ps15
title: Metin, Regex ve Kültür
summary: -f ile biçimlendirme, -match ve $Matches, adlı gruplar, [regex]::Matches ile bütün eşleşmeler, -replace ve geri başvuru, -split, Select-String ve Türkçe I/i kültür tuzağı.
---

::: anlat Biçimlendirme ve düzenli ifadeler
PowerShell'in metin işleçleri .NET düzenli ifadelerini kullanır ve Regex yolundaki sözdiziminin neredeyse tamamı burada geçerlidir:

| İşleç / yöntem | Ne yapar |
|---|---|
| `"{0,-8}{1,5:N1}" -f $a, $b` | biçimlendirme: hizalama, ondalık |
| `$m -match 'desen'` | ilk eşleşme; gruplar `$Matches`'a dolar |
| `[regex]::Matches($s, 'desen')` | **bütün** eşleşmeler |
| `$s -replace 'desen', 'yeni'` | bütün eşleşmeleri değiştirir; `$1`, `${ad}` geri başvuru |
| `$s -split 'desen'` | düzenli ifadeyle böler |
| `Select-String -Pattern` | dosyalarda ya da metinlerde grep benzeri arama |
| `-cmatch`, `-creplace` | büyük-küçük harfe **duyarlı** sürümler |

```powershell
"{0,-8}|{1,6:N1}|{2:P0}" -f "web01", 72.456, 0.25
$satir = "2026-10-19 08:15:02 kullanici=ece sure=125ms"
if ($satir -match 'kullanici=(?<ad>\w+) sure=(?<ms>\d+)ms') {
    "$($Matches.ad) $($Matches.ms)"
}
[regex]::Matches("a1b22c333", '\d+') | ForEach-Object { $_.Value }
"2026-10-19" -replace '(\d{4})-(\d{2})-(\d{2})', '$3.$2.$1'
"web01, db01;cache01" -split '[,;]\s*'
```

> [!TUZAK]
> `-replace`'in değiştirme metni **tek tırnakla** yazılmalıdır: çift tırnak içinde `"$1"` PowerShell değişkeni sanılır ve boş metne dönüşür. `'$3.$2.$1'` doğru, `"$3.$2.$1"` yanlış.

### Select-String: PowerShell'in grep'i
```powershell
@"
INFO baslatildi
ERROR disk dolu
INFO istek
ERROR ag zaman asimi
"@ | Set-Content uygulama.log
Select-String -Path uygulama.log -Pattern '^ERROR (.+)$' | ForEach-Object {
    "{0}: {1}" -f $_.LineNumber, $_.Matches[0].Groups[1].Value
}
```

### Kültür ve Türkçe I
Metin dönüşümleri ve karşılaştırmaları **kültüre** bağlıdır. Türkçede büyük `I`'nın küçüğü `ı`, küçük `i`'nin büyüğü `İ`'dir; İngilizcede ise `I` ↔ `i`. Bu yüzden aynı kod Türkçe ayarlı bir makinede farklı davranabilir:

```powershell
$tr = [cultureinfo]"tr-TR"
"TITLE".ToLower($tr)          #! tıtle
"title".ToUpper($tr)          #! TİTLE
"TITLE".ToLowerInvariant()    #! title: kültürden bağımsız
```

> [!TUZAK]
> Dosya uzantısı, komut adı, protokol adı gibi **makine için anlamlı** metinleri karşılaştırırken kültüre bağlı dönüşüm kullanma: Türkçe Windows'ta `"FILE".ToLower()` "fıle" olur ve `-eq "file"` tutmaz. `ToLowerInvariant()`, `ToUpperInvariant()` ya da `[StringComparison]::OrdinalIgnoreCase` kullan. Kullanıcıya **gösterilen** metinlerde ise kültüre uygun dönüşüm doğrudur.
:::

::: tahmin
Üç satır yazar:

```powershell
"web01 db01 web02" -replace 'web(\d+)', 'srv$1'
([regex]::Matches("a1b22c333", '\d+')).Count
"TITLE".ToLower([cultureinfo]"tr-TR")
```

???

`srv01 db01 srv02`, `3`, `tıtle`. `-replace` bütün eşleşmeleri değiştirir ve `$1` yakalanan rakamları geri koyar. `Matches` üç sayı grubu bulur. Türk kültüründe büyük I'nın küçüğü noktasız ı'dır.
:::

::: gorev Log alanları
Girdinin her satırı `ZAMAN kullanici=AD sure=SAYIms` biçiminde. Her satır için adlı grupları kullanarak `AD SAYI` yazdır; kalıba uymayan satırları atla.

```starter
foreach ($s in $Girdi) {
    $s
}
```

```stdin
08:15:02 kullanici=ece sure=125ms
bozuk satır
08:16:40 kullanici=can sure=7ms
```

```test
eq(run("08:15:02 kullanici=ece sure=125ms\nbozuk satır\n08:16:40 kullanici=can sure=7ms\n"), "ece 125\ncan 7\n", "iki geçerli satır")
ok("?<" in src, "adlı grup kullan: (?<ad>...)")
```

```solution
foreach ($s in $Girdi) {
    if ($s -match 'kullanici=(?<ad>\w+) sure=(?<ms>\d+)ms') {
        "$($Matches.ad) $($Matches.ms)"
    }
}
```

```hint
`if ($s -match 'kullanici=(?<ad>\w+) sure=(?<ms>\d+)ms') { "$($Matches.ad) $($Matches.ms)" }`. `$Matches` yalnızca eşleşme başarılıysa güncellenir; `if` şart.
```
:::

::: gorev Bütün adresler
Girdideki metinde geçen **bütün** IPv4 adreslerini (dört grup 1–3 rakam, noktayla ayrılmış) her biri ayrı satırda, **tekrarsız** ve ilk geçiş sırasıyla yazdır.

```starter
foreach ($s in $Girdi) {
    if ($s -match '\d+\.\d+\.\d+\.\d+') { $Matches[0] }
}
```

```stdin
10.0.0.5 ile 10.0.0.9 arasında bağlantı
yeniden: 10.0.0.5 -> 192.168.1.20
```

```test
eq(run("10.0.0.5 ile 10.0.0.9 arasında bağlantı\nyeniden: 10.0.0.5 -> 192.168.1.20\n"), "10.0.0.5\n10.0.0.9\n192.168.1.20\n", "üç farklı adres")
ok("Matches" in src, "[regex]::Matches kullan")
```

```solution
$gorulen = [System.Collections.Generic.HashSet[string]]::new()
foreach ($s in $Girdi) {
    foreach ($m in [regex]::Matches($s, '\b\d{1,3}(\.\d{1,3}){3}\b')) {
        if ($gorulen.Add($m.Value)) { $m.Value }
    }
}
```

```hint
`-match` yalnızca ilk eşleşmeyi bulur. Satırdaki hepsi için `[regex]::Matches($s, 'desen')`.
```

```hint
Tekrarları atıp sırayı korumak için bir `HashSet`: `Add` yeni elemanda `$true` döner.
```
:::

::: gorev Uzantı karşılaştırması
Girdinin her satırı bir dosya adı. Uzantısı (büyük-küçük harf fark etmeksizin) `.ini` olanların adını yazdır. Betiğin ilk satırı, Türkçe ayarlı bir Windows'u taklit etmek için kültürü **tr-TR** yapıyor; o satırı silme. Çözüm bu kültürde de doğru çalışmalı.

```starter
[System.Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]"tr-TR"   # Türkçe Windows: silme
foreach ($ad in $Girdi) {
    if ([System.IO.Path]::GetExtension($ad).ToLower() -ceq ".ini") { $ad }
}
```

```stdin
ayar.INI
notlar.txt
eski.Ini
```

```test
eq(run("ayar.INI\nnotlar.txt\neski.Ini\nSISTEM.INI\n"), "ayar.INI\neski.Ini\nSISTEM.INI\n", "üç .ini dosyası, Türkçe kültürde")
ok("tr-TR" in src, "kültür satırını silme")
```

```solution
[System.Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]"tr-TR"   # Türkçe Windows: silme
foreach ($ad in $Girdi) {
    if ([System.IO.Path]::GetExtension($ad).ToLowerInvariant() -ceq ".ini") { $ad }
}
```

```hint
`ToLower()` kültüre bağlıdır: Türkçede ".INI" → ".ını" olur. `ToLowerInvariant()` kullan.
```
:::
