---
id: ps09
title: Hata Yönetimi
summary: Sonlandıran ve sonlandırmayan hatalar, -ErrorAction, try/catch/finally, throw, TryParse ve çıkış kodları.
---

::: anlat İki tür hata
PowerShell'de hatalar ikiye ayrılır:

- **Sonlandırmayan** (non-terminating): komut hatayı bildirir ama **devam eder**. `Get-Item a.txt, yok.txt, b.txt` olmayan dosya için hata yazar, diğerlerini döndürür.
- **Sonlandıran** (terminating): akış durur ve `try/catch` ile yakalanabilir. `throw`, .NET istisnaları ve parametre doğrulama hataları bu türdendir.

`try/catch` **sadece sonlandıran** hataları yakalar. Bir cmdlet'in hatasını yakalamak istiyorsan onu `-ErrorAction Stop` ile sonlandırana çevirmelisin:

```powershell
try {
    Get-Item "C:\olmayan\dosya.txt" -ErrorAction Stop     #! Stop olmadan catch ÇALIŞMAZ
    "buraya gelinmez"
} catch {
    "yakalandı: $($_.Exception.GetType().Name)"           #! $_ = hata kaydı
} finally {
    "temizlik her durumda çalışır"
}
```

Betik genelinde varsayılanı değiştirmek için `$ErrorActionPreference = "Stop"`, Bash'teki `set -e`'nin (P10) karşılığıdır.

### throw ve belirli türleri yakalamak
```powershell
function Get-Bolum($a, $b) {
    if ($b -eq 0) { throw [System.DivideByZeroException]::new("bölen sıfır olamaz") }
    $a / $b
}
try {
    Get-Bolum 10 0
} catch [System.DivideByZeroException] {
    "sıfıra bölme: $($_.Exception.Message)"
} catch {
    "başka bir hata"
}
```

### Güvenli dönüşüm: TryParse
`[int]"abc"` hata verir; `[int]"3.5"` ise sessizce **4**'e yuvarlar. Kullanıcı girdisini doğrularken bunlar istenmeyen davranışlardır. .NET'in `TryParse` metodu dönüşümü dener, başarıyı `$true`/`$false` olarak döndürür ve sonucu `[ref]` ile verir:

```powershell
$sonuc = 0
[int]::TryParse("42", [ref]$sonuc)
$sonuc
[int]::TryParse("3.5", [ref]$sonuc)
```

> [!NOT]
> Çıkış kodu: bir betik `exit 3` ile çıkarsa onu çağıran (zamanlanmış görev, CI hattı, başka bir betik) `$LASTEXITCODE` ile okur. Hata mesajlarını standart hataya yazmak için `Write-Error` ya da en sade haliyle `[Console]::Error.WriteLine("...")` kullanılır.
:::

::: tahmin
Çıktıyı satır satır yaz:

```powershell
try {
    Get-Item "C:\olmayan\dosya.txt" -ErrorAction Stop
    "buraya gelinmez"
} catch {
    "yakalandı"
} finally {
    "temizlik"
}
```

???

`yakalandı`, sonra `temizlik`. `-ErrorAction Stop` hatayı sonlandırana çevirir, akış `catch`'e atlar; `finally` her durumda çalışır.
:::

::: gorev Güvenli tam sayı
`ConvertTo-GuvenliInt` fonksiyonunu yaz: `$Deger` metnini **katı** biçimde tam sayıya çevirsin; çevrilemiyorsa `$Varsayilan` (varsayılanı 0) döndürsün. `3.5` gibi ondalıklı metinler de geçersiz sayılmalı. Betik `$Girdi`'nin her satırı için sonucu yazdırsın.

```starter
function ConvertTo-GuvenliInt($Deger, $Varsayilan = 0) {
    [int]$Deger
}
foreach ($satir in $Girdi) { ConvertTo-GuvenliInt $satir }
```

```stdin
42
abc
```

```test
eq(run("42\nabc\n3.5\n-7\n 9 \n").splitlines(), ["42", "0", "0", "-7", "9"], "katı dönüşüm")
ok("tryparse" in src.lower(), "[int]::TryParse kullan")
```

```solution
function ConvertTo-GuvenliInt($Deger, $Varsayilan = 0) {
    $sonuc = 0
    if ([int]::TryParse($Deger, [ref]$sonuc)) { $sonuc } else { $Varsayilan }
}
foreach ($satir in $Girdi) { ConvertTo-GuvenliInt $satir }
```

```hint
`$sonuc = 0; if ([int]::TryParse($Deger, [ref]$sonuc)) { $sonuc } else { $Varsayilan }`. TryParse kenar boşluklarını tolere eder.
```
:::

::: gorev Dosya satır sayıları
`$Girdi`'nin her satırı bir dosya adı. Her dosya için `ad: N satır` yazdır; dosya okunamıyorsa `okunamadı: ad` yazıp devam et.

```setup
open("a.txt", "w", encoding="utf-8", newline="\n").write("1\n2\n3\n")
open("b.txt", "w", encoding="utf-8", newline="\n").write("tek\n")
```

```starter
foreach ($ad in $Girdi) {
    $n = (Get-Content $ad).Count
    "${ad}: $n satır"
}
```

```stdin
a.txt
yok.txt
b.txt
```

```test
eq(run("a.txt\nyok.txt\nb.txt\n"), "a.txt: 3 satır\nokunamadı: yok.txt\nb.txt: 1 satır\n", "satır sayıları")
eq(hata_cikti, "", "hata mesajları standart hataya sızmamalı")
```

```solution
foreach ($ad in $Girdi) {
    try {
        $n = @(Get-Content $ad -ErrorAction Stop).Count
        "${ad}: $n satır"
    } catch {
        "okunamadı: $ad"
    }
}
```

```hint
`Get-Content $ad -ErrorAction Stop` ve `try/catch`. Tek satırlık dosyada `Get-Content` dizi değil tek metin döner; `@( ... ).Count` ile her zaman diziye çevir.
```
:::

::: gorev Port doğrulama
Betik `$Port` parametresi alsın. 1–65535 arası bir tam sayıysa `port: N` yazdırsın; değilse standart hataya `geçersiz port: <değer>` yazıp **1** koduyla çıksın.

```starter
param($Port)
"port: $Port"
```

```meta
argv: 443
```

```test
r = calis(argv=["443"])
eq((r["kod"], r["cikti"]), (0, "port: 443\n"), "443 geçerli")
r = calis(argv=["70000"])
eq(r["kod"], 1, "70000 → kod 1")
ok("geçersiz port: 70000" in r["hata"], "hata mesajı stderr'de", got=r["hata"])
eq(calis(argv=["abc"])["kod"], 1, "abc → kod 1")
```

```solution
param($Port)
$sayi = 0
if (-not [int]::TryParse("$Port", [ref]$sayi) -or $sayi -lt 1 -or $sayi -gt 65535) {
    [Console]::Error.WriteLine("geçersiz port: $Port")
    exit 1
}
"port: $sayi"
```

```hint
TryParse ile dönüştür, aralığı kontrol et; geçersizse `[Console]::Error.WriteLine(...)` ve `exit 1`.
```
:::
