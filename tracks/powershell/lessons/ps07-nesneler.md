---
id: ps07
title: Nesnelerle Çalışmak
summary: [pscustomobject], Select-Object ve hesaplanan özellikler, Sort-Object, Group-Object, Measure-Object, Get-Member.
---

::: anlat Kendi nesnelerin
PowerShell'in gücü yapılandırılmış veridir. `[pscustomobject]` ile istediğin özelliklerde bir kayıt oluşturursun:

```powershell
$sunucular = @(
    [pscustomobject]@{ Ad = "web01"; Cpu = 75; Rol = "web" }
    [pscustomobject]@{ Ad = "db01";  Cpu = 92; Rol = "veritabanı" }
    [pscustomobject]@{ Ad = "dc01";  Cpu = 40; Rol = "dizin" }
)
$sunucular | Where-Object Cpu -gt 70 | Sort-Object Cpu -Descending | ForEach-Object { "$($_.Ad) $($_.Cpu)" }
($sunucular | Measure-Object Cpu -Average -Maximum).Maximum
$sunucular[0] | Get-Member -MemberType NoteProperty | ForEach-Object Name   #! hangi özellikler var?
```

`Where-Object Cpu -gt 70` yazımı `Where-Object { $_.Cpu -gt 70 }`'in kısa halidir.

### Seçmek, hesaplamak, gruplamak
```powershell
$olaylar = @(
    [pscustomobject]@{ Kullanici = "root"; Sonuc = "FAIL" }
    [pscustomobject]@{ Kullanici = "ali";  Sonuc = "OK" }
    [pscustomobject]@{ Kullanici = "root"; Sonuc = "FAIL" }
    [pscustomobject]@{ Kullanici = "veli"; Sonuc = "FAIL" }
)
$olaylar | Group-Object Sonuc | ForEach-Object { "$($_.Name): $($_.Count)" }      #! grupla ve say
$olaylar | Where-Object Sonuc -eq "FAIL" | Group-Object Kullanici |
    Sort-Object Count -Descending | Select-Object -First 1 -ExpandProperty Name
$olaylar | Select-Object Kullanici, @{ Name = "Basarili"; Expression = { $_.Sonuc -eq "OK" } } |
    ForEach-Object { "$($_.Kullanici) → $($_.Basarili)" }                       #! hesaplanan özellik
```

`Group-Object` her grup için `Name` (anahtar), `Count` ve `Group` (o gruptaki nesneler) özellikleri olan bir nesne üretir. Bash'teki `sort | uniq -c` ve SIEM'lerdeki `stats count by` / `summarize count() by` ile aynı işi yapar.

> [!NOT]
> Ekrana tablo basmak için `Format-Table` vardır ama onu **en sona** koy: Format-* cmdlet'leri nesneleri biçimlendirme nesnelerine çevirir ve sonrasındaki komutlar artık özelliklere erişemez. Kural: "önce süz, sonra biçimle". Veriyi başka yere aktaracaksan `Export-Csv` ya da `ConvertTo-Json` (PS08).
:::

::: tahmin
İki satır yazar:

```powershell
$s = @(
    [pscustomobject]@{ Ad = "web01"; Cpu = 75 }
    [pscustomobject]@{ Ad = "db01";  Cpu = 92 }
    [pscustomobject]@{ Ad = "dc01";  Cpu = 40 }
)
($s | Sort-Object Cpu -Descending | Select-Object -First 1).Ad
($s | Measure-Object Cpu -Average).Average
```

???

`db01`, sonra `69`. En yüksek CPU 92 ile db01'dir; ortalama (75 + 92 + 40) / 3 = 69.
:::

::: gorev Yüklü sunucular
`$Girdi`'nin her satırı `ad cpu` biçiminde. Her satırdan bir `[pscustomobject]` (`Ad`, `Cpu` [int]) oluştur; CPU'su **80'den büyük** olanları CPU'ya göre **büyükten küçüğe** `ad cpu` biçiminde yazdır.

```starter
foreach ($satir in $Girdi) {
    $satir
}
```

```stdin
web01 75
db01 92
cache01 85
dc01 40
```

```test
eq(run("web01 75\ndb01 92\ncache01 85\ndc01 40\n"), "db01 92\ncache01 85\n", "yüksek CPU'lular, sıralı")
eq(run("a 10\n"), "", "yüksek yoksa boş")
ok("pscustomobject" in src.lower(), "[pscustomobject] kullan")
```

```solution
$sunucular = foreach ($satir in $Girdi) {
    $ad, $cpu = $satir -split " "
    [pscustomobject]@{ Ad = $ad; Cpu = [int]$cpu }
}
$sunucular | Where-Object Cpu -gt 80 | Sort-Object Cpu -Descending | ForEach-Object { "$($_.Ad) $($_.Cpu)" }
```

```hint
`foreach` ifadesinin çıktısı bir değişkene atanabilir: `$sunucular = foreach (...) { [pscustomobject]@{ ... } }`.
```

```hint
`[int]` dönüşümünü unutma: metin olarak "9" > "85" sıralanır.
```
:::

::: gorev Durum dağılımı
`$Girdi`'nin her satırı `kullanici durum` biçiminde. Durumlara göre grupla ve `durum sayı` biçiminde, **sayıya göre çoktan aza** yazdır.

```starter
$Girdi
```

```stdin
root FAIL
ali OK
root FAIL
veli FAIL
ayse OK
root LOCKED
```

```test
eq(run("root FAIL\nali OK\nroot FAIL\nveli FAIL\nayse OK\nroot LOCKED\n"), "FAIL 3\nOK 2\nLOCKED 1\n", "gruplar")
ok("group-object" in src.lower(), "Group-Object kullan")
```

```solution
$Girdi |
    ForEach-Object { ($_ -split " ")[1] } |
    Group-Object |
    Sort-Object Count -Descending |
    ForEach-Object { "$($_.Name) $($_.Count)" }
```

```hint
Önce her satırdan durumu çıkar (`($_ -split " ")[1]`), sonra `Group-Object`, `Sort-Object Count -Descending`.
```
:::

::: gorev Hesaplanan özellik
`$Girdi`'nin her satırı `ad cpu`. `Select-Object` ile **hesaplanan** bir `Durum` özelliği ekle: CPU 80'den büyükse `yüksek`, değilse `normal`. Her sunucu için `ad: durum` yazdır (girdi sırasıyla).

```starter
foreach ($satir in $Girdi) {
    $ad, $cpu = $satir -split " "
    "${ad}: normal"
}
```

```stdin
web01 75
db01 92
```

```test
eq(run("web01 75\ndb01 92\ndc01 81\n"), "web01: normal\ndb01: yüksek\ndc01: yüksek\n", "durumlar")
ok("expression" in src.lower(), "Select-Object ile hesaplanan özellik (Expression) kullan")
```

```solution
$Girdi |
    ForEach-Object {
        $ad, $cpu = $_ -split " "
        [pscustomobject]@{ Ad = $ad; Cpu = [int]$cpu }
    } |
    Select-Object Ad, @{ Name = "Durum"; Expression = { if ($_.Cpu -gt 80) { "yüksek" } else { "normal" } } } |
    ForEach-Object { "$($_.Ad): $($_.Durum)" }
```

```hint
Hesaplanan özellik bir hashtable'dır: `@{ Name = "Durum"; Expression = { ... } }`. İçeride `$_` o anki nesnedir.
```
:::
