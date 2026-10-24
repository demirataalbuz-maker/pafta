---
id: ps26
title: Pester · Kendi Fonksiyonunun Testlerini Yazmak
summary: Pester 5 ile test yazmak: Describe/Context/It, Should operatörleri, -TestCases, BeforeAll ve keşif/çalıştırma ayrımı, Invoke-Pester -PassThru ve $LASTEXITCODE; Mock (modül içi çağrılarda -ModuleName), Should -Invoke ve TestDrive:. Testlerinin değeri, bozuk sürümleri yakalayıp yakalamamasıyla ölçülür.
---

::: anlat Testi sen yazınca
Şimdiye kadar Pafta'nın gizli testlerini geçtin. Gerçek bir araç yazdığında testleri **sen** yazarsın ve iyi bir testin tek ölçüsü vardır: kod bozulduğunda kırmızıya dönmesi. Bu derste görevlerin teslimi bir fonksiyon değil, o fonksiyonun **testleridir**. Gizli test, senin testlerini önce doğru uygulamaya, sonra her birinde tek bir hata bulunan **bozuk sürümlere** (mutant) karşı çalıştırır: doğru sürümde hepsi geçmeli, her bozuk sürümde en az biri kırılmalı.

PowerShell'in test çatısı **Pester**'dir. Windows PowerShell 5.1 ile eski Pester 3.4 gelir; bu derste projeye sabitlenmiş **Pester 5.9.0** kullanılır (`.deps\psmodules` altında; koşucu onu önce bulur). Sözdizimi farklıdır: 3.4'te `Should Be 5`, 5'te `Should -Be 5`.

```powershell
Import-Module Pester -RequiredVersion 5.9.0
(Get-Module Pester).Version.ToString()
```

Bir test dosyası şöyle görünür:

```text
BeforeAll {
    . $PSScriptRoot/Topla.ps1            # test edilen kodu yükle
}
Describe 'Topla' {
    It 'iki sayıyı toplar' {
        Topla 2 3 | Should -Be 5
    }
    It '<a> + <b> = <beklenen>' -TestCases @(
        @{ a = 0; b = 0; beklenen = 0 }
        @{ a = -1; b = 1; beklenen = 0 }
    ) {
        Topla $a $b | Should -Be $beklenen
    }
}
```

| Operatör | Ne zaman geçer |
|---|---|
| `Should -Be x` | eşit (metinde büyük-küçük harfe duyarsız) |
| `Should -BeExactly x` | birebir eşit (harfe duyarlı) |
| `Should -BeNullOrEmpty` | `$null` ya da boş |
| `Should -HaveCount n` | n eleman |
| `Should -Throw` / `Should -Throw -ExpectedMessage '*metin*'` | betik bloğu hata fırlatır (`{ ... } \| Should -Throw`) |
| `Should -Not -Be x` | olumsuzu |

Pester 5'in en çok şaşırtan kuralı: dosya iki kez işlenir. Önce **keşif** (discovery) aşamasında `Describe` ve `It` blokları bulunur, sonra **çalıştırma** aşamasında `It`'lerin içi koşar. Test edilen kodu `Describe`'ın dışına düz yazarsan keşif aşamasında yüklenir ama çalıştırma aşamasında görünmez; yüklemeyi **`BeforeAll`** içine koy. `-TestCases` ise keşifte değerlendirilir; içindeki değerler sabit olmalıdır.

`Invoke-Pester -Path dosya -Output None -PassThru` sonucu bir nesne olarak verir: `Result`, `TotalCount`, `PassedCount`, `FailedCount`, `SkippedCount` ve başarısız testlerin listesi `Failed`. Pester bittiğinde `$LASTEXITCODE`'u başarısız test sayısına ayarlar; bir betiğin içinde çalıştırdıysan ve bu bilerek bir hataysa sıfırlaman gerekir.

Kaynak: [Pester 5 hızlı başlangıç](https://pester.dev/docs/v5/quick-start), [Keşif ve çalıştırma](https://pester.dev/docs/usage/discovery-and-run).
:::

::: anlat Bağımlılığı taklit etmek: Mock ve TestDrive
Test edilen fonksiyon saate, dosya sistemine ya da ağa bakıyorsa sonuç her çalıştırmada değişir. Pester iki araç verir:

- **`Mock Komut { ... }`**: o komutun yerine senin bloğunu çalıştırır. `Mock Get-Date { [datetime]'2026-10-24 12:00' }` dedikten sonra test edilen kod hep o anı görür. `Should -Invoke Komut -Times 1 -Exactly` taklidin kaç kez çağrıldığını denetler.
- **`TestDrive:`**: her `Describe` için açılan, sonunda silinen geçici bir klasör. `Set-Content TestDrive:\yedek.zip 'x'` ile dosya kurar, `(Get-Item TestDrive:\yedek.zip).LastWriteTime = ...` ile zamanını ayarlarsın.

Test edilen fonksiyon bir **modülün** içindeyse, modülün içinden yapılan çağrıları taklit etmek için `-ModuleName` gerekir: `Mock Get-Date -ModuleName Yedek { ... }`. `-ModuleName` olmadan taklit test dosyasının kapsamında kalır ve modülün içi gerçek `Get-Date`'i görmeye devam eder. Bu, "testim neden saate göre değişiyor?" sorusunun en yaygın yanıtıdır.

> [!NOT]
> Hata senaryoları da test edilir: olmayan dosya, boş girdi, eşiğin tam kendisi. Yalnız "mutlu yol"u sınayan bir test, sınırdaki bir `-gt`/`-ge` karışıklığını hiçbir zaman yakalamaz.
:::

::: tahmin Bir başarısız, bir atlanan
```powershell
Import-Module Pester -RequiredVersion 5.9.0
Set-Content -Path topla.ps1 -Value 'function Topla([int]$a, [int]$b) { $a + $b }'
Set-Content -Path topla.Tests.ps1 -Value @'
BeforeAll { . $PSScriptRoot/topla.ps1 }
Describe 'Topla' {
    It 'iki sayıyı toplar' { Topla 2 3 | Should -Be 5 }
    It 'yanlis beklenti' { Topla 2 2 | Should -Be 5 }
    It 'atlanan' -Skip { 1 | Should -Be 1 }
}
'@
$sonuc = Invoke-Pester -Path ./topla.Tests.ps1 -Output None -PassThru
'{0} {1} {2} {3} {4}' -f $sonuc.Result, $sonuc.TotalCount, $sonuc.PassedCount, $sonuc.FailedCount, $sonuc.SkippedCount
$sonuc.Failed | ForEach-Object { $_.ExpandedName + ' :: ' + ($_.ErrorRecord[0].Exception.Message -split "`n")[0] }
"exit: $LASTEXITCODE"
$global:LASTEXITCODE = 0
```

???

```text
Failed 3 1 1 1
yanlis beklenti :: Expected 5, but got 4.
exit: 1
```

Üç test bulundu: biri geçti, biri kırıldı, biri `-Skip` ile atlandı. Tek bir kırık test bile bütün sonucu `Failed` yapar. Pester kırılan testin beklenen ve gerçek değerini yazar. `$LASTEXITCODE` başarısız test sayısıdır (1); betik bunu sıfırlamasaydı kendisi de 1 ile biterdi.
:::

::: gorev Parola gücü için testler
Çalışma klasöründe `Parola.psm1` modülü var; içindeki `Get-ParolaGucu -Parola <metin>` fonksiyonu şu kurala göre `zayıf`, `orta` ya da `güçlü` döndürür:

- 8 karakterden kısa her parola (boş metin dahil): `zayıf`.
- Dört karakter sınıfı sayılır: küçük harf `a-z`, büyük harf `A-Z`, rakam, bunların dışındaki her karakter.
- En az 12 karakter **ve** en az 3 sınıf: `güçlü`.
- Değilse en az 2 sınıf: `orta`; yoksa `zayıf`.

Bu fonksiyonun **Pester 5 testlerini** yaz. Betiğin bir Pester test dosyasıdır: `BeforeAll` içinde `Import-Module "$PSScriptRoot/Parola.psm1" -Force` ile modülü yükle ve `Describe`/`It` bloklarını yaz.

Gizli test senin testlerini doğru modüle ve altı bozuk sürüme karşı çalıştırır. Doğru modülde **hepsi geçmeli**, her bozuk sürümde **en az biri kırılmalı**. Bozuk sürümlerin her biri yukarıdaki kuraldan tek bir noktada sapar; hangi noktalar olduğunu kuralı sınırlarıyla okuyarak bul.

```setup
open("Parola.psm1", "w", encoding="utf-8-sig").write(r'''function Get-ParolaGucu {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Parola)
    if ($Parola.Length -lt 8) { return 'zayıf' }
    $sinif = 0
    if ($Parola -cmatch '[a-z]') { $sinif++ }
    if ($Parola -cmatch '[A-Z]') { $sinif++ }
    if ($Parola -match '\d') { $sinif++ }
    if ($Parola -match '[^a-zA-Z\d]') { $sinif++ }
    if ($Parola.Length -ge 12 -and $sinif -ge 3) { return 'güçlü' }
    if ($sinif -ge 2) { return 'orta' }
    'zayıf'
}
Export-ModuleMember -Function Get-ParolaGucu
''')
```

```starter
BeforeAll { Import-Module "$PSScriptRoot/Parola.psm1" -Force }
Describe 'Get-ParolaGucu' {
    It 'uzun ve karışık parola güçlüdür' {
        Get-ParolaGucu -Parola 'Abcdefgh123!' | Should -Be 'güçlü'
    }
}
```

```test
import re
DOGRU = open("Parola.psm1", encoding="utf-8-sig").read()
open("ogrenci.Tests.ps1", "w", encoding="utf-8-sig").write(src)
def pester(modul):
    open("Parola.psm1", "w", encoding="utf-8-sig").write(modul)
    cikti = run_code("Import-Module Pester -RequiredVersion 5.9.0\n"
                     "$r = Invoke-Pester -Path ./ogrenci.Tests.ps1 -Output None -PassThru\n"
                     "'{0} {1} {2}' -f $r.TotalCount, $r.FailedCount, ($r.FailedContainersCount + $r.FailedBlocksCount)\n"
                     "$global:LASTEXITCODE = 0\n")
    return tuple(int(x) for x in cikti.split()[-3:])
toplam, kirik, blok = pester(DOGRU)
ok(toplam >= 6, "en az altı test", got=toplam)
eq((kirik, blok), (0, 0), "doğru modülde bütün testler geçer")
MUTANTLAR = [
    ("-lt 8", "-lt 7", "8 karakter sınırı (7 karakterli parola)"),
    ("-ge 12", "-ge 13", "12 karakter sınırı (tam 12 karakter)"),
    ("-and $sinif -ge 3", "-and $sinif -ge 2", "güçlü için 3 sınıf şartı"),
    ("$Parola -cmatch '[a-z]'", "$Parola -match '[a-z]'", "küçük harf sınıfı harfe duyarlı"),
    ("    if ($Parola -match '[^a-zA-Z\\d]') { $sinif++ }\n", "", "özel karakter sınıfı"),
    ("[AllowEmptyString()]", "", "boş metin zayıf döner, hata fırlatmaz"),
]
for eski, yeni, ne in MUTANTLAR:
    ok(eski in DOGRU, "mutant hazırlığı: " + ne)
    t, k, b = pester(DOGRU.replace(eski, yeni))
    ok(k + b > 0, "bozuk sürüm yakalanmalı: " + ne, got=(t, k))
open("Parola.psm1", "w", encoding="utf-8-sig").write(DOGRU)
```

```solution
BeforeAll { Import-Module "$PSScriptRoot/Parola.psm1" -Force }
Describe 'Get-ParolaGucu' {
    It '<p> -> <beklenen>' -TestCases @(
        @{ p = '';             beklenen = 'zayıf' }
        @{ p = 'Abcdef1';      beklenen = 'zayıf' }
        @{ p = 'Abcdefg1';     beklenen = 'orta' }
        @{ p = 'abcdefgh';     beklenen = 'zayıf' }
        @{ p = 'Abcdefghij1!'; beklenen = 'güçlü' }
        @{ p = 'Abcdefghi1!';  beklenen = 'orta' }
        @{ p = 'abcdefghijk1'; beklenen = 'orta' }
        @{ p = 'ABCDEFGHIJK1'; beklenen = 'orta' }
        @{ p = 'abcdefghijk!'; beklenen = 'orta' }
    ) {
        Get-ParolaGucu -Parola $p | Should -BeExactly $beklenen
    }
}
```

```hint
Her kural bir sınırdır; sınırın iki yanını sına: 7 ve 8 karakter, 11 ve 12 karakter, 2 ve 3 sınıf. Boş metin de bir girdidir.
```

```hint
Bir sınıfın sayılıp sayılmadığını, **o sınıf olmadan** sonucun değiştiği bir parolayla sınarsın: yalnız büyük harf ve rakamdan oluşan 12 karakterli bir parola iki sınıftır (`orta`); büyük harfi küçük harf sayan bir hata onu `güçlü` yapar.
```
:::

::: gorev Yedek tazeliği için Mock'lu testler
`Yedek.psm1` modülündeki `Get-YedekDurumu -Yol <dosya> -EsikSaat <sayı>` fonksiyonu bir yedek dosyasının durumunu döndürür:

- dosya yoksa `yok`;
- dosyanın **son yazılma** zamanından bu yana geçen süre eşikten **büyükse** `eski`;
- değilse (eşiğin tam kendisi dahil) `taze`.

"Şimdi"yi `Get-Date` ile öğrenir. Bu fonksiyonun Pester 5 testlerini yaz. Testlerin saatten bağımsız olmalı: `Get-Date`'i **Mock** ile sabitle (fonksiyon bir modülde olduğu için `-ModuleName Yedek`) ve dosyaları **`TestDrive:`** içinde kurup zamanlarını kendin ayarla.

Gizli test, testlerini doğru modüle ve beş bozuk sürüme karşı çalıştırır. Bozuk sürümlerden biri "şimdi"yi `Get-Date` yerine başka bir yoldan okur; taklidin işe yaradığını da testlerin göstermeli.

```setup
open("Yedek.psm1", "w", encoding="utf-8-sig").write(r'''function Get-YedekDurumu {
    param([Parameter(Mandatory)][string]$Yol, [Parameter(Mandatory)][int]$EsikSaat)
    if (-not (Test-Path -LiteralPath $Yol -PathType Leaf)) { return 'yok' }
    $yas = (Get-Date) - (Get-Item -LiteralPath $Yol).LastWriteTime
    if ($yas.TotalHours -gt $EsikSaat) { 'eski' } else { 'taze' }
}
Export-ModuleMember -Function Get-YedekDurumu
''')
```

```starter
BeforeAll { Import-Module "$PSScriptRoot/Yedek.psm1" -Force }
Describe 'Get-YedekDurumu' {
    It 'yeni yazılmış dosya tazedir' {
        Set-Content TestDrive:\yedek.zip 'x'
        Get-YedekDurumu -Yol TestDrive:\yedek.zip -EsikSaat 24 | Should -Be 'taze'
    }
}
```

```test
import re
DOGRU = open("Yedek.psm1", encoding="utf-8-sig").read()
open("ogrenci.Tests.ps1", "w", encoding="utf-8-sig").write(src)
def pester(modul):
    open("Yedek.psm1", "w", encoding="utf-8-sig").write(modul)
    cikti = run_code("Import-Module Pester -RequiredVersion 5.9.0\n"
                     "$r = Invoke-Pester -Path ./ogrenci.Tests.ps1 -Output None -PassThru\n"
                     "'{0} {1} {2}' -f $r.TotalCount, $r.FailedCount, ($r.FailedContainersCount + $r.FailedBlocksCount)\n"
                     "$global:LASTEXITCODE = 0\n")
    return tuple(int(x) for x in cikti.split()[-3:])
toplam, kirik, blok = pester(DOGRU)
ok(toplam >= 4, "en az dört test", got=toplam)
eq((kirik, blok), (0, 0), "doğru modülde bütün testler geçer")
ok(re.search(r"\bMock\s+Get-Date\b", src, re.I) and re.search(r"-ModuleName\s+'?\"?Yedek", src, re.I), "Get-Date modülün içinde Mock'lanır (-ModuleName Yedek)")
ok("testdrive:" in src.lower(), "dosyalar TestDrive: içinde")
MUTANTLAR = [
    ("-gt $EsikSaat", "-ge $EsikSaat", "eşiğin tam kendisi taze sayılır"),
    (".LastWriteTime", ".CreationTime", "yazılma zamanı, oluşturulma değil"),
    ("return 'yok'", "return 'eski'", "olmayan dosya"),
    ("$yas.TotalHours", "$yas.TotalMinutes", "süre saat cinsinden"),
    ("$yas = (Get-Date) - (Get-Item -LiteralPath $Yol).LastWriteTime", "$yas = [datetime]::Now - (Get-Item -LiteralPath $Yol).LastWriteTime", "şimdi Get-Date'ten gelir (Mock'u atlatan sürüm)"),
]
for eski, yeni, ne in MUTANTLAR:
    ok(eski in DOGRU, "mutant hazırlığı: " + ne)
    t, k, b = pester(DOGRU.replace(eski, yeni))
    ok(k + b > 0, "bozuk sürüm yakalanmalı: " + ne, got=(t, k))
open("Yedek.psm1", "w", encoding="utf-8-sig").write(DOGRU)
```

```solution
BeforeAll {
    Import-Module "$PSScriptRoot/Yedek.psm1" -Force
    $script:simdi = [datetime]'2030-01-15 12:00'
}
Describe 'Get-YedekDurumu' {
    BeforeEach {
        Mock Get-Date -ModuleName Yedek { $script:simdi }
        Set-Content TestDrive:\yedek.zip 'x'
        (Get-Item TestDrive:\yedek.zip).CreationTime = $script:simdi
    }
    It 'eşikten bir saat önce yazılmış: taze' {
        (Get-Item TestDrive:\yedek.zip).LastWriteTime = $script:simdi.AddHours(-23)
        Get-YedekDurumu -Yol TestDrive:\yedek.zip -EsikSaat 24 | Should -Be 'taze'
    }
    It 'tam eşikte yazılmış: taze' {
        (Get-Item TestDrive:\yedek.zip).LastWriteTime = $script:simdi.AddHours(-24)
        Get-YedekDurumu -Yol TestDrive:\yedek.zip -EsikSaat 24 | Should -Be 'taze'
    }
    It 'eşikten bir dakika sonra: eski' {
        (Get-Item TestDrive:\yedek.zip).LastWriteTime = $script:simdi.AddHours(-24).AddMinutes(-1)
        Get-YedekDurumu -Yol TestDrive:\yedek.zip -EsikSaat 24 | Should -Be 'eski'
    }
    It 'olmayan dosya: yok' {
        Get-YedekDurumu -Yol TestDrive:\olmayan.zip -EsikSaat 24 | Should -Be 'yok'
    }
    It 'şimdiyi Get-Date ten alır' {
        (Get-Item TestDrive:\yedek.zip).LastWriteTime = $script:simdi.AddHours(-1)
        Get-YedekDurumu -Yol TestDrive:\yedek.zip -EsikSaat 24 | Out-Null
        Should -Invoke Get-Date -ModuleName Yedek -Times 1 -Exactly
    }
}
```

```hint
`Mock Get-Date -ModuleName Yedek { [datetime]'2030-01-15 12:00' }` modülün içindeki çağrıyı sabitler. Dosyanın zamanını `(Get-Item TestDrive:\yedek.zip).LastWriteTime = ...` ile ayarla; geleceğe sabitlenmiş bir "şimdi", gerçek saatle karışan bir hatayı hemen ortaya çıkarır.
```

```hint
Sınırları sına: eşikten biraz önce, tam eşik, eşikten biraz sonra. Oluşturulma zamanını yazılma zamanından farklı tut ki ikisini karıştıran bir hata yakalansın. `Should -Invoke Get-Date -ModuleName Yedek` taklidin gerçekten kullanıldığını kanıtlar.
```
:::
