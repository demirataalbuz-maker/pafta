---
id: ps29
title: PSSession · Kalıcı Oturum ve Serileştirilmiş Sonuç
summary: Invoke-Command'ın her çağrıda sıfırdan başlamasıyla New-PSSession'ın kalıcı oturumu arasındaki fark; oturumun ayrı bir süreçte yaşaması ve değişkenlerin orada kalması; oturum sınırını geçen nesnelerin serileştirilmesi (Deserialized.* tipleri, metotların kaybolması, DateTime gibi bilinen tiplerin sağlam geçmesi, ScriptBlock'un metne dönmesi); hatadan sonra oturumun açık kalması, Remove-PSSession ve silinmiş oturumun InvalidOperation vermesi. Gerçek PowerShell 7.6.8 ile, yönetici ve WinRM olmadan.
kazanim: AZ040 8.1, AZ040 8.2
---

::: anlat Her çağrıda sıfırdan mı?
PS20'de `Invoke-Command` ile bir betik bloğu çalıştırdın. Orada her çağrı kendi başınadır: bir çağrıda kurduğun değişken, ikinci çağrıda yoktur. Bir makinede arka arkaya on iş yapacaksan (önce veriyi topla, sonra süz, sonra raporla) bu hem yavaştır hem de bağlamı kaybeder.

**PSSession** kalıcı bir oturumdur: bir kez açarsın, içine komut göndermeye devam edersin, işin bitince kapatırsın.

```powershell norun
$s = New-PSSession -UseWindowsPowerShell       # oturumu aç
Invoke-Command -Session $s { $sayac = 5 }      # oturumda bir değişken kur
Invoke-Command -Session $s { $sayac + 1 }      # 6 · değişken hâlâ orada
Remove-PSSession $s                            # oturumu kapat
```

| Komut | İşi |
|---|---|
| `New-PSSession` | oturumu açar; `$s.State` → `Opened` |
| `Invoke-Command -Session $s { ... }` | komutu **o** oturumda çalıştırır |
| `Get-PSSession` | açık oturumları listeler |
| `Remove-PSSession $s` | oturumu kapatır; `$s.State` → `Closed` |

> [!NOT] Bu paftanın laboratuvarı
> Gerçek bir SOC'ta `New-PSSession -ComputerName sunucu01` yazarsın; bu, ağ üzerinden **WinRM** ile bağlanır ve hedefte WinRM'in açık olmasını ister. Bu pafta onun yerine `-UseWindowsPowerShell` kullanır: PowerShell 7, **aynı makinede** ayrı bir Windows PowerShell 5.1 süreci başlatır ve oturumu ona açar. Ağ yok, WinRM yok, yönetici yetkisi yok — ama oturum, süreç sınırı ve serileştirme **gerçektir**; öğrendiğin her şey uzak oturumda da aynı çalışır. Bu derste tezgah PowerShell 7.6.8'dir (`motor: pwsh`); uzak makineye bağlanma ve kopan oturuma yeniden bağlanma (`Disconnect-PSSession`) WinRM istediği için bu paftanın dışında.
:::

::: anlat Oturum ayrı bir süreçtir
Oturumun içi başka bir süreçtir; kendi `$PID`'i, kendi değişkenleri vardır. Üstelik bu laboratuvarda **kendi PowerShell sürümü** de vardır: istemci 7.6.8, oturum 5.1.

```powershell norun
$s = New-PSSession -UseWindowsPowerShell
"yerel : $PID / $($PSVersionTable.PSVersion)"
Invoke-Command -Session $s { "oturum: $PID / $($PSVersionTable.PSVersion)" }
```

Bu ayrılığın bedeli şudur: oturumdan sana dönen her nesne **serileştirilir** (XML'e çevrilip karşıda yeniden kurulur). Yeniden kurulan nesne, aslının bir **fotoğrafıdır**:

- Tipinin başına `Deserialized.` gelir: `Deserialized.System.Diagnostics.Process`.
- **Metotları yoktur.** Bir süreç nesnesinin `Kill()`'i gelmez; çağırırsan `MethodNotFound` alırsın.
- Özellikleri (ad, kimlik, boyut) olduğu gibi gelir ve sayılar sayı kalır.
- Bilinen temel tipler (`int`, `string`, `DateTime`, `bool`) sağlam geçer: `DateTime` yine `DateTime`'dır ve `AddDays()` çalışır.
- `ScriptBlock` metne dönüşür: karşı tarafta çalıştırılabilir kod taşımak güvenlik gereği engellidir.

> [!TUZAK] Nesneyi geri gönderip üstünde iş yapma
> `$p = Invoke-Command -Session $s { Get-Process -Name notepad }` yazıp sonra yerelde `$p.Kill()` demek çalışmaz. Doğrusu, **işi oturumun içinde yaptırmaktır**: `Invoke-Command -Session $s { (Get-Process -Name notepad).Kill() }`. Oturumdan yalnız **sonucu** (sayı, metin, rapor satırı) geri al.
:::

::: tahmin
Bu betik ne yazdırır?

```powershell
$s = New-PSSession -UseWindowsPowerShell
Invoke-Command -Session $s { $kayit = @(1, 2, 3) } | Out-Null
Invoke-Command -Session $s { $kayit += 4; $kayit.Count }
Invoke-Command -Session $s { $kayit.Count }
"yerelde: $($kayit.Count)"
Remove-PSSession $s
```

???

**`4`, `4` ve `yerelde: 0`:**

```
4
4
yerelde: 0
```

İlk iki satır oturumda çalıştı: dizi oturumda yaşıyor, ikinci çağrı birincinin bıraktığı yerden devam etti. Üçüncü satır **yerelde** çalıştı; orada `$kayit` diye bir değişken hiç olmadı. Tanımsız bir değişken `$null`'dur ve `$null.Count` PowerShell'de hata vermeden `0` verir. Oturumun içi ile dışı iki ayrı dünyadır.

```meta
motor: pwsh
```
:::

::: gorev 1 · Oturumu aç, kullan, kapat
`Olc` adında bir fonksiyon yaz: parametresi `$Sayilar` (tam sayı dizisi). Bir PSSession açsın, **sayıları oturuma biriktirsin** ve her eklemeden sonraki toplamı oturumda hesaplatsın; sonunda oturumu kapatsın.

Her sayı için bir satır yazdır: `<sayı> → <o ana kadarki toplam>`. En sonda bir satır daha: `durum: <oturumun kapandıktan sonraki durumu>`.

- Toplamı yerelde hesaplama; oturumda tutulan bir değişkenle oturumda hesaplat.
- `$Sayilar` boşsa yalnız `durum:` satırı yazılsın.
- Değeri oturuma geçirmek için `Invoke-Command`'ın `-ArgumentList` parametresini ve betik bloğunda `param($n)` kullan.

```starter
function Olc {
    param([int[]]$Sayilar)
    $toplam = 0
    foreach ($n in $Sayilar) {
        $toplam += $n
        "$n -> $toplam"
    }
    "durum: ?"
}

Olc -Sayilar @(3, 4, 10)
```

```test
eq(out, "3 -> 3\n4 -> 7\n10 -> 17\ndurum: Closed\n", "her adımda birikmiş toplam, sonra kapanan oturumun durumu")
ok("New-PSSession" in src and "Remove-PSSession" in src, "oturumu aç ve kapat")
ok("-Session" in src, "hesabı oturumda yaptır: Invoke-Command -Session")
yerel = [r for r in src.splitlines() if "+=" in r and "-Session" not in r and "ScriptBlock" not in r]
eq(yerel, [], "toplamı yerelde biriktirme; oturumdaki değişkeni kullan")
bos = run_code(src.replace("Olc -Sayilar @(3, 4, 10)", "Olc -Sayilar @()"))
eq(bos, "durum: Closed\n", "boş dizi: yalnız durum satırı")
tek = run_code(src.replace("Olc -Sayilar @(3, 4, 10)", "Olc -Sayilar @(-5)"))
eq(tek, "-5 -> -5\ndurum: Closed\n", "negatif tek sayı")
iki = run_code(src.replace("Olc -Sayilar @(3, 4, 10)", "Olc -Sayilar @(1,2); Olc -Sayilar @(7)"))
eq(iki, "1 -> 1\n2 -> 3\ndurum: Closed\n7 -> 7\ndurum: Closed\n", "her çağrı kendi oturumunu açar: ikinci çağrı sıfırdan başlar")
```

```solution
function Olc {
    param([int[]]$Sayilar)
    $s = New-PSSession -UseWindowsPowerShell
    Invoke-Command -Session $s { $toplam = 0 } | Out-Null
    foreach ($n in $Sayilar) {
        $t = Invoke-Command -Session $s -ArgumentList $n -ScriptBlock { param($n) $toplam += $n; $toplam }
        "$n -> $t"
    }
    Remove-PSSession $s
    "durum: $($s.State)"
}

Olc -Sayilar @(3, 4, 10)
```

```hint
Oturumu açtıktan sonra `Invoke-Command -Session $s { $toplam = 0 } | Out-Null` ile sayacı kur. `| Out-Null` olmazsa atamanın çıktısı yoktur ama alışkanlık olarak yaz.
```

```hint
Yerel bir değeri oturuma geçirmek: `Invoke-Command -Session $s -ArgumentList $n -ScriptBlock { param($n) $toplam += $n; $toplam }`. Betik bloğunun içi yerel değişkenlerini görmez; `param` ile alman gerekir.
```

```hint
`Remove-PSSession $s`'ten sonra `$s` nesnesi hâlâ elindedir ve `$s.State` artık `Closed` der.
```

```meta
motor: pwsh
```
:::

::: gorev 2 · Serileştirme sınırını ölç
`Sinir` adında bir fonksiyon yaz: bir oturum açsın ve oturumdan üç şey getirip her biri için bir satır yazsın, sonra oturumu kapatsın.

```text
process: <PSTypeNames[0]> | metot: <VAR ya da YOK>
tarih  : <GetType().Name> | yil: <yıl>
blok   : <GetType().Name>
```

- `process`: oturumda `Get-Process -Id $PID` ile alınan süreç nesnesi. `metot` alanı, nesnenin `Kill` metodu **varsa** `VAR`, yoksa `YOK`.
- `tarih`: oturumda `Get-Date -Date "2026-10-19"` ile alınan tarih.
- `blok`: oturumda `{ 1 + 1 }` betik bloğu.
- Metodun varlığını `Get-Member` ile sor; çağırmayı deneme.

```starter
function Sinir {
    $p = Get-Process -Id $PID
    $t = Get-Date -Date "2026-10-19"
    $b = { 1 + 1 }
    "process: $($p.PSTypeNames[0]) | metot: ?"
    "tarih  : $($t.GetType().Name) | yil: $($t.Year)"
    "blok   : $($b.GetType().Name)"
}

Sinir
```

```test
eq(out, "process: Deserialized.System.Diagnostics.Process | metot: YOK\n"
        "tarih  : DateTime | yil: 2026\n"
        "blok   : String\n",
   "süreç nesnesi serileştirilmiş ve metotsuz; DateTime sağlam; betik bloğu metne dönmüş")
eq(src.count("Invoke-Command -Session"), 3, "üçünü de oturumdan getir")
ok("New-PSSession" in src and "Remove-PSSession" in src, "oturumu aç ve kapat")
ok("Get-Member" in src, "metodun varlığını Get-Member ile sor")
```

```solution
function Sinir {
    $s = New-PSSession -UseWindowsPowerShell
    $p = Invoke-Command -Session $s { Get-Process -Id $PID }
    $t = Invoke-Command -Session $s { Get-Date -Date "2026-10-19" }
    $b = Invoke-Command -Session $s { { 1 + 1 } }
    $metot = if ($p | Get-Member -MemberType Method -Name Kill) { "VAR" } else { "YOK" }
    "process: $($p.PSTypeNames[0]) | metot: $metot"
    "tarih  : $($t.GetType().Name) | yil: $($t.Year)"
    "blok   : $($b.GetType().Name)"
    Remove-PSSession $s
}

Sinir
```

```hint
Metodun varlığı: `if ($p | Get-Member -MemberType Method -Name Kill) { "VAR" } else { "YOK" }`. `Get-Member` eşleşme bulamazsa hiçbir şey döndürmez, `if` de bunu yanlış sayar.
```

```hint
`$t.GetType().Name` oturumdan gelen tarih için yine `DateTime` der: bilinen temel tipler serileştirmeden sağlam çıkar. Betik bloğu ise `String`'e dönüşür.
```

```meta
motor: pwsh
```
:::
