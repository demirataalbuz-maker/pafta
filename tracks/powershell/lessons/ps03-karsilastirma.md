---
id: ps03
title: Karşılaştırma ve Koşullar
summary: -eq, -lt, -like, -match ve $Matches; büyük-küçük harf duyarsızlığı; if/elseif ve switch.
kazanim: AZ040 7.2
---

::: anlat İşleçler kelimedir
PowerShell'de karşılaştırma işleçleri sembol değil **kelimedir**, çünkü `>` ve `<` yönlendirme için ayrılmıştır:

| İşleç | Anlamı | Örnek |
|---|---|---|
| `-eq` `-ne` | eşit / değil | `$kod -eq 404` |
| `-gt` `-ge` `-lt` `-le` | büyük, büyük-eşit, küçük, küçük-eşit | `$cpu -gt 80` |
| `-like` `-notlike` | joker desen (`*`, `?`) | `$dosya -like "*.log"` |
| `-match` `-notmatch` | regex | `$satir -match "\d{3}"` |
| `-contains` `-in` | dizide var mı | `$roller -contains "admin"` |

```powershell
"ABC" -eq "abc"                       #! True: varsayılan olarak harf duyarsız!
"ABC" -ceq "abc"                      #! False: c öneki = case-sensitive
"rapor.txt" -like "*.txt"
"hata 404 bulunamadı" -match "\d+"    #! regex eşleşirse True
$Matches[0]                           #! son -match'in yakaladığı
@("web01", "db01") -contains "DB01"   #! diziler de harf duyarsız
```

> [!TUZAK]
> Metin karşılaştırmaları **varsayılan olarak büyük-küçük harf duyarsızdır**: `-eq`, `-like`, `-match`, `-contains`. Bu, Bash ve Python'dan gelenleri şaşırtır. Duyarlı karşılaştırma için önüne `c` ekle: `-ceq`, `-clike`, `-cmatch`. Parola ya da imza karşılaştırmasında bunu unutmak güvenlik hatasıdır.

### -match ve adlı gruplar
`-match` başarılı olunca yakalanan gruplar otomatik `$Matches` sözlüğüne dolar. .NET regex'i adlı grup için `(?<ad>...)` yazımını kullanır (Regex yolunda Python'un `(?P<ad>...)` yazımını görmüştün):

```powershell
$satir = "kullanici=ali ip=10.0.0.5"
if ($satir -match "kullanici=(?<k>\w+) ip=(?<ip>[\d.]+)") {
    "$($Matches.k) → $($Matches.ip)"
}
```

### if ve switch
```powershell
$kod = 404
if ($kod -ge 500) { "sunucu hatası" }
elseif ($kod -ge 400) { "istemci hatası" }
else { "tamam" }

switch -Wildcard ("yedek.tar.gz") {    #! switch: desen tabanlı dallanma
    "*.zip"    { "arşiv (zip)" }
    "*.tar.gz" { "arşiv (tar)" }
    default    { "bilinmiyor" }
}
```

`switch` -Wildcard, -Regex ve -CaseSensitive seçenekleri alabilir; bir dizi verilirse her elemanı sırayla işler.
:::

::: tahmin
Beş satırın çıktısını yaz:

```powershell
"ABC" -eq "abc"
"ABC" -ceq "abc"
"rapor.txt" -like "*.txt"
"hata 404" -match "\d+"
$Matches[0]
```

???

`True`, `False`, `True`, `True`, `404`. `-eq` harf duyarsızdır, `-ceq` duyarlıdır. `-match` eşleşmeyi `$Matches`'e yazar; `[0]` eşleşen metnin tamamıdır.
:::

::: gorev HTTP durum sınıfı
`$Girdi`'nin ilk satırındaki durum kodunu sınıflandır: 200–299 `başarılı`, 300–399 `yönlendirme`, 400–499 `istemci hatası`, 500–599 `sunucu hatası`, diğerleri `geçersiz`.

```starter
$kod = [int]$Girdi[0]

```

```stdin
404
```

```test
for girdi, beklenen in [("200", "başarılı"), ("301", "yönlendirme"), ("404", "istemci hatası"), ("503", "sunucu hatası"), ("99", "geçersiz")]:
    eq(run(girdi + "\n").strip(), beklenen, f"{girdi} → {beklenen}")
```

```solution
$kod = [int]$Girdi[0]
if ($kod -ge 200 -and $kod -le 299) { "başarılı" }
elseif ($kod -ge 300 -and $kod -le 399) { "yönlendirme" }
elseif ($kod -ge 400 -and $kod -le 499) { "istemci hatası" }
elseif ($kod -ge 500 -and $kod -le 599) { "sunucu hatası" }
else { "geçersiz" }
```

```hint
Mantıksal VE de kelimedir: `-and`. `($kod -ge 200 -and $kod -le 299)`.
```
:::

::: gorev Dosya türü
`$Girdi`'nin her satırı bir dosya adı. Her biri için `ad: tür` yazdır: `*.jpg`/`*.png` → `görsel`, `*.log` → `log`, `*.zip`/`*.tar.gz` → `arşiv`, diğerleri → `diğer`. `switch -Wildcard` kullan; büyük harfli uzantılar da tanınmalı.

```starter
foreach ($dosya in $Girdi) {
    "${dosya}: diğer"
}
```

```stdin
foto.jpg
yedek.tar.gz
```

```test
girdi = "foto.jpg\nyedek.tar.gz\napp.log\nEKRAN.PNG\nnotlar.txt\nsiparis.zip\n"
eq(run(girdi).splitlines(), ["foto.jpg: görsel", "yedek.tar.gz: arşiv", "app.log: log", "EKRAN.PNG: görsel", "notlar.txt: diğer", "siparis.zip: arşiv"], "türler")
ok("switch" in src.lower(), "switch kullan")
```

```solution
foreach ($dosya in $Girdi) {
    $tur = switch -Wildcard ($dosya) {
        "*.jpg"    { "görsel" }
        "*.png"    { "görsel" }
        "*.log"    { "log" }
        "*.zip"    { "arşiv" }
        "*.tar.gz" { "arşiv" }
        default    { "diğer" }
    }
    "${dosya}: $tur"
}
```

```hint
`switch` bir değer üretir: `$tur = switch -Wildcard ($dosya) { "*.jpg" { "görsel" } ... default { "diğer" } }`. -Wildcard varsayılan olarak harf duyarsızdır.
```
:::

::: gorev Alan çıkarma
`$Girdi`'nin her satırı `kullanici=AD ip=ADRES ...` biçiminde. `-match` ve **adlı gruplarla** her satır için `AD@ADRES` yazdır; biçime uymayan satırları atla.

```starter
foreach ($satir in $Girdi) {
    $satir
}
```

```stdin
kullanici=ali ip=10.0.0.5 durum=ok
bozuk satır
```

```test
eq(run("kullanici=ali ip=10.0.0.5 durum=ok\nbozuk satır\nkullanici=veli_2 ip=192.168.1.20\n").splitlines(), ["ali@10.0.0.5", "veli_2@192.168.1.20"], "iki geçerli satır")
ok("(?<" in src, "adlı grup (?<ad>...) kullan")
```

```solution
foreach ($satir in $Girdi) {
    if ($satir -match "kullanici=(?<k>\w+) ip=(?<ip>[\d.]+)") {
        "$($Matches.k)@$($Matches.ip)"
    }
}
```

```hint
`if ($satir -match "kullanici=(?<k>\w+) ip=(?<ip>[\d.]+)") { ... }`, içeride `$Matches.k` ve `$Matches.ip`.
```
:::
