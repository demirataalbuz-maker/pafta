---
id: ps05
title: Boru Hattı ve Döngüler
summary: Nesne akan boru hattı, ForEach-Object, Where-Object, $_, Measure-Object; foreach, for ve while.
---

::: anlat Boruda nesne akar
Bash'te borudan **metin** akar ve her araç onu yeniden ayrıştırır. PowerShell'de borudan **nesneler** akar: sayılar, dosya bilgileri, süreçler, kendi oluşturduğun kayıtlar. Bir sonraki komut özelliklere doğrudan erişir.

```powershell
1..10 | Where-Object { $_ % 2 -eq 0 }                 #! süz: $_ = o anki nesne
1..5 | ForEach-Object { $_ * $_ }                     #! dönüştür
1..100 | Measure-Object -Sum -Average -Maximum        #! özetle
"web01", "db01", "dc01" | Where-Object { $_ -like "d*" } | ForEach-Object { $_.ToUpper() }
(1..10 | Measure-Object -Sum).Sum
```

| Cmdlet | Kısaltma | İş |
|---|---|---|
| `Where-Object { koşul }` | `where`, `?` | süz |
| `ForEach-Object { ... }` | `foreach`, `%` | her nesne için çalıştır |
| `Select-Object` | `select` | özellik seç, ilk/son N |
| `Sort-Object` | `sort` | sırala |
| `Measure-Object` | `measure` | say, topla, ortalama |
| `Group-Object` | `group` | grupla (PS07) |

> [!NOT]
> Kısaltmalar (`%`, `?`) etkileşimli kullanımda hızlıdır ama betiklerde okunabilirliği bozar. Paylaşacağın betiklerde tam adları yaz.

### Döngüler
```powershell
foreach ($host_ in @("web01", "db01")) { "kontrol: $host_" }   #! foreach ifadesi
for ($i = 3; $i -ge 1; $i--) { $i }
$n = 1
while ($n -lt 100) { $n *= 3 }
$n
```

`foreach (...)` bir **ifadedir** ve tüm koleksiyonu belleğe alır, hızlıdır. `ForEach-Object` bir **cmdlet**'tir ve nesneleri boru hattından tek tek, akış halinde işler; dev dosyalarda bellek dostudur.

> [!TUZAK]
> `$host` PowerShell'de **ayrılmış** bir otomatik değişkendir (konsol ana bilgisayarı nesnesi). Döngü değişkenine `$host` adını verirsen hata alırsın. `$input`, `$_`, `$args`, `$Error`, `$PSItem` de otomatik değişkenlerdir.
:::

::: tahmin
Çıktıyı satır satır yaz:

```powershell
1..10 | Where-Object { $_ % 3 -eq 0 } | ForEach-Object { $_ * 10 }
(1..4 | Measure-Object -Sum).Sum
```

???

`30`, `60`, `90`, `10`. 1–10 arasında 3'e bölünenler 3, 6, 9'dur; her biri 10 ile çarpılır. 1+2+3+4 = 10.
:::

::: gorev Sayıları topla
`$Girdi`'nin satırlarındaki tam sayıları topla; boş satırları atla. Boru hattı kullan.

```starter
$toplam = 0
$toplam
```

```stdin
10
20

12
```

```test
eq(run("10\n20\n\n12\n"), "42\n", "10+20+12")
eq(run("-3\n3\n"), "0\n", "negatifler")
eq(run("7\n"), "7\n", "tek sayı")
ok("|" in src, "boru hattı kullan")
```

```solution
($Girdi | Where-Object { $_ -ne "" } | ForEach-Object { [int]$_ } | Measure-Object -Sum).Sum
```

```hint
Boşları ele: `Where-Object { $_ -ne "" }`. Sayıya çevir: `ForEach-Object { [int]$_ }`. Topla: `Measure-Object -Sum` ve `.Sum`.
```
:::

::: gorev Geri sayım
`$Girdi[0]`'daki n'den 1'e kadar her sayıyı ayrı satıra, sonunda `Ateş!` yazdır. `for` döngüsü kullan.

```starter
$n = [int]$Girdi[0]

```

```stdin
3
```

```test
eq(run("3\n"), "3\n2\n1\nAteş!\n", "3")
eq(run("0\n"), "Ateş!\n", "0 → sadece Ateş!")
ok("for" in src.lower(), "for kullan")
```

```solution
$n = [int]$Girdi[0]
for ($i = $n; $i -ge 1; $i--) {
    $i
}
"Ateş!"
```

```hint
`for ($i = $n; $i -ge 1; $i--) { $i }`
```
:::

::: gorev Hata satırları
`$Girdi` bir log. İçinde `error` geçen satırları (büyük-küçük harf fark etmez) **satır numaralarıyla** `N: satır` biçiminde yazdır; en sonda `toplam: K` yaz.

```starter
foreach ($satir in $Girdi) {
    $satir
}
```

```stdin
INFO başladı
ERROR bağlantı koptu
WARN yavaş
error disk dolu
```

```test
eq(run("INFO başladı\nERROR bağlantı koptu\nWARN yavaş\nerror disk dolu\n"), "2: ERROR bağlantı koptu\n4: error disk dolu\ntoplam: 2\n", "iki hata")
eq(run("INFO tamam\n"), "toplam: 0\n", "hata yok")
```

```solution
$toplam = 0
for ($i = 0; $i -lt $Girdi.Count; $i++) {
    if ($Girdi[$i] -like "*error*") {
        "$($i + 1): $($Girdi[$i])"
        $toplam++
    }
}
"toplam: $toplam"
```

```hint
Satır numarası için indeksli `for` kullan (`$i + 1`). `-like "*error*"` harf duyarsızdır.
```
:::
