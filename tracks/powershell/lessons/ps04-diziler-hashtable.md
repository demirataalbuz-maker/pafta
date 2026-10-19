---
id: ps04
title: Diziler ve Hashtable'lar
summary: @() diziler, aralıklar, -join ve -split; @{} hashtable'lar, [ordered], anahtarlar ve sayma kalıbı.
---

::: anlat Diziler
```powershell
$portlar = @(22, 80, 443)            #! dizi
$portlar[0]; $portlar[-1]            #! indeks, sondan indeks
$portlar.Count
$portlar += 3389                     #! sona ekle (aslında YENİ dizi oluşturur)
$portlar -join ", "                  #! birleştir
"a,b,,c" -split ","                  #! böl (regex ile!)
1..5                                 #! aralık
$portlar -contains 443               #! var mı
$portlar | Sort-Object -Descending
```

Bir komut tek sonuç döndürünce dizi değil **tek değer** gelir; sıfır sonuçta `$null`. Sonucu her zaman dizi olarak almak için `@( ... )` ile sar: `@(Get-ChildItem *.log).Count`.

> [!TUZAK]
> `+=` diziye ekler gibi görünür ama her seferinde **yeni bir dizi** kopyalar; on binlerce elemanlık döngülerde çok yavaştır. Büyük koleksiyonlar için `[System.Collections.Generic.List[object]]::new()` ve `.Add()` kullan. Ayrıca `-split` **regex** ile böler: `"a.b" -split "."` beklemediğin sonucu verir; düz metinle bölmek için `-split [regex]::Escape(".")` ya da `.Split(".")`.

### Hashtable: anahtar → değer
Python'daki sözlüğün (P16) karşılığı:

```powershell
$servis = @{ ssh = 22; http = 80 }
$servis["https"] = 443               #! ekle
$servis.ssh                          #! nokta ile de erişilir
$servis.ContainsKey("rdp")
$servis.Keys | Sort-Object
$sirali = [ordered]@{ ilk = 1; ikinci = 2 }   #! ekleme sırasını korur
$sirali.Keys -join ","
```

Düz hashtable'ın anahtar sırası **garanti değildir**; sıra önemliyse `[ordered]` kullan ya da yazdırırken sırala.

### Sayma kalıbı
```powershell
$sayim = @{}
foreach ($ip in @("10.0.0.7", "10.0.0.9", "10.0.0.7")) {
    $sayim[$ip] = $sayim[$ip] + 1    #! olmayan anahtar $null; $null + 1 = 1
}
$sayim.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Value)" }
```
:::

::: tahmin
Üç satırın çıktısını yaz:

```powershell
$a = @(3, 1, 2)
$a += 5
$a.Count
($a | Sort-Object) -join ","
$h = @{ ssh = 22; http = 80 }
$h["ssh"] + $h.http
```

???

`4`, `1,2,3,5`, `102`. `+=` dördüncü elemanı ekler, `Sort-Object` sıralar, `-join` birleştirir. Hashtable değerlerine hem köşeli parantez hem nokta ile erişilir.
:::

::: gorev Benzersiz IP'ler
`$Girdi`'nin ilk satırında boşlukla ayrılmış IP adresleri var. Her IP'yi **ilk görülme sırasıyla ve bir kez** olacak şekilde virgülle birleştirip yazdır.

```starter
$ipler = $Girdi[0] -split " "
$ipler -join ","
```

```stdin
10.0.0.1 10.0.0.2 10.0.0.1 10.0.0.3 10.0.0.2
```

```test
eq(run("10.0.0.1 10.0.0.2 10.0.0.1 10.0.0.3 10.0.0.2\n"), "10.0.0.1,10.0.0.2,10.0.0.3\n", "sıra korunur")
eq(run("b a b a c\n"), "b,a,c\n", "ilk görülme sırası")
```

```solution
$ipler = $Girdi[0] -split " "
$gorulen = @{}
$sonuc = foreach ($ip in $ipler) {
    if (-not $gorulen.ContainsKey($ip)) {
        $gorulen[$ip] = $true
        $ip
    }
}
$sonuc -join ","
```

```hint
Görülenleri bir hashtable'da tut. Ya da kısa yol: `$ipler | Select-Object -Unique` sırayı korur.
```
:::

::: gorev Başarısız giriş sayacı
`$Girdi`'nin her satırı `kullanici durum` biçiminde (`OK` ya da `FAIL`). Her kullanıcının FAIL sayısını hesapla; en az bir FAIL'i olanları **ada göre alfabetik** `kullanici: sayı` biçiminde yazdır.

```starter
foreach ($satir in $Girdi) {
    $satir
}
```

```stdin
root FAIL
ali FAIL
root FAIL
veli OK
ali FAIL
root FAIL
```

```test
eq(run("root FAIL\nali FAIL\nroot FAIL\nveli OK\nali FAIL\nroot FAIL\n"), "ali: 2\nroot: 3\n", "sayım")
eq(run("x OK\ny OK\n"), "", "FAIL yoksa çıktı boş")
```

```solution
$sayim = @{}
foreach ($satir in $Girdi) {
    $kullanici, $durum = $satir -split " "
    if ($durum -eq "FAIL") {
        $sayim[$kullanici] = $sayim[$kullanici] + 1
    }
}
$sayim.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Value)" }
```

```hint
Çoklu atama: `$kullanici, $durum = $satir -split " "`. Sayma: `$sayim[$k] = $sayim[$k] + 1`.
```

```hint
Hashtable'ı sıralı yazdırmak: `$sayim.GetEnumerator() | Sort-Object Name`.
```
:::

::: gorev Port → servis
Verilen hashtable'dan **port → ad** eşlemesi yapan yeni bir hashtable üret. Sonra `$Girdi[0]`'daki portun adını yazdır; yoksa `bilinmiyor`.

```starter
$servisler = @{ ssh = 22; http = 80; https = 443; dns = 53 }
$port = [int]$Girdi[0]

```

```stdin
443
```

```test
eq(run("443\n"), "https\n", "443 → https")
eq(run("53\n"), "dns\n", "53 → dns")
eq(run("3389\n"), "bilinmiyor\n", "3389 → bilinmiyor")
```

```solution
$servisler = @{ ssh = 22; http = 80; https = 443; dns = 53 }
$port = [int]$Girdi[0]
$portAdi = @{}
foreach ($oge in $servisler.GetEnumerator()) {
    $portAdi[$oge.Value] = $oge.Key
}
if ($portAdi.ContainsKey($port)) { $portAdi[$port] } else { "bilinmiyor" }
```

```hint
`foreach ($oge in $servisler.GetEnumerator()) { $portAdi[$oge.Value] = $oge.Key }`. Anahtarın türü önemli: `[int]` olarak arıyorsan int olarak eklemelisin (değerler zaten int).
```
:::
