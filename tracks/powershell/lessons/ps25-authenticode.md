---
id: ps25
title: Authenticode · İmzayı Dosya İncelemesine Katmak
summary: Get-AuthenticodeSignature ile bir dosyanın imza durumunu okumak: Valid, NotSigned, HashMismatch, UnknownError; gömülü (Authenticode) ve katalog (Catalog) imzası farkı, kopyalanan ve bir baytı değişen dosyada ne olduğu; yayıncı (SignerCertificate), zaman damgası ve IsOSBinary; geçerli imzayı tek başına güven kararı saymamak.
---

::: anlat Bir dosyanın imzasını sormak
Windows'ta yürütülebilir dosyalar, DLL'ler, sürücüler ve PowerShell betikleri **Authenticode** ile imzalanabilir: yayıncı dosyanın özetini kendi kod imzalama sertifikasıyla imzalar. Bir olay incelemesinde ilk sorulardan biri "bu dosya imzalı mı, kim imzalamış, imzadan sonra değişmiş mi?"dir. Windows PowerShell'de yanıtı `Get-AuthenticodeSignature` verir:

```powershell
$s = Get-AuthenticodeSignature -LiteralPath "$env:windir\System32\notepad.exe"
$s.Status
$s.SignatureType
$s.SignerCertificate.Subject -replace ',.*'
$s.IsOSBinary
```

| Özellik | Ne söyler |
|---|---|
| `Status` | `Valid`, `NotSigned`, `HashMismatch`, `NotTrusted`, `UnknownError` ... |
| `SignatureType` | `Authenticode` (imza dosyanın içinde), `Catalog` (imza Windows'un katalog dosyasında), `None` |
| `SignerCertificate` | imzalayan sertifika: `Subject` yayıncının adı, `Thumbprint` parmak izi |
| `TimeStamperCertificate` | imzaya zaman damgası vuran yetkili; sertifikanın süresi dolsa da imzanın atıldığı anı kanıtlar |
| `IsOSBinary` | Windows'un kendi bileşeni mi |
| `StatusMessage` | durumun açıklaması |

`-LiteralPath` köşeli parantez gibi joker karakterleri olduğu gibi okur. Olmayan bir dosyada cmdlet `FileNotFoundException` taşıyan bir hata yazar; bunu durum sanıp `NotSigned` diye raporlamamak gerekir.

Kaynak: [Get-AuthenticodeSignature](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-authenticodesignature?view=powershell-5.1), [SignatureStatus](https://learn.microsoft.com/en-us/dotnet/api/system.management.automation.signaturestatus).
:::

::: anlat Gömülü imza, katalog imzası ve bozulma
İki imza türü bozulmaya **farklı** tepki verir ve bu fark incelemede yanlış sonuca götürebilir:

| Durum | Gömülü imza (`Authenticode`) | Katalog imzası (`Catalog`) |
|---|---|---|
| dosya başka bir klasöre kopyalandı | `Valid`: imza dosyayla gider | `Valid`: katalog dosyanın **özetine** bakar, yerine değil |
| dosyanın tek bir baytı değişti | `HashMismatch`: imza var, özet tutmuyor; yayıncı hâlâ görünür | `NotSigned`: dosyada imza yok, yeni özet hiçbir katalogda yok |
| imzalanmamış betik | `NotSigned` | `NotSigned` |
| imza taşıyamayan biçim (`.txt`, boş dosya) | `UnknownError` | `UnknownError` |

Windows'un kendi dosyalarının çoğu (örneğin `notepad.exe`, `powershell.exe`) katalog imzalıdır. Bu yüzden bozulmuş bir sistem dosyası `HashMismatch` değil **`NotSigned`** görünür. "İmzasız" sonucu, dosyanın hiç imzalanmamış olduğunu değil, **bu hâliyle** hiçbir imzayla eşleşmediğini söyler.

```powershell
$t = Join-Path $env:TEMP ("imza_" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $t | Out-Null
Copy-Item "$env:windir\System32\notepad.exe" "$t\kopya.exe"
$b = [IO.File]::ReadAllBytes("$t\kopya.exe"); $b[1000] = $b[1000] -bxor 1
[IO.File]::WriteAllBytes("$t\bozuk.exe", $b)
foreach ($ad in 'kopya.exe', 'bozuk.exe') {
    $s = Get-AuthenticodeSignature -LiteralPath "$t\$ad"
    '{0}: {1} ({2})' -f $ad, $s.Status, $s.SignatureType
}
Remove-Item $t -Recurse -Force
```

> [!GÜVENLİK]
> `Valid` yalnızca "bu dosya, imzalandığından beri değişmedi ve imzalayan sertifika güvenilen bir köke zincirleniyor" demektir. **Kim** imzaladığını ayrıca okumak gerekir: geçerli bir sertifikayı herhangi bir şirket alabilir ve çalınmış sertifikalarla imzalı zararlılar bilinen bir olgudur. Microsoft'un kendi imzalı programları da kötüye kullanılabilir. Güven kararı imza durumu, **beklenen yayıncı** (adı ya da daha iyisi sertifika parmak izi), dosyanın beklenen yeri ve davranışı birlikte değerlendirilerek verilir. Çevrimdışı makinede iptal (revocation) denetimi yapılamayabilir; sonuç ağ ve sertifika deposuna bağlıdır.
:::

::: tahmin Kopya ve bozuk kopya
```powershell
$t = Join-Path $env:TEMP ("imza_" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $t | Out-Null
Copy-Item "$env:windir\System32\MpSigStub.exe" "$t\stub.exe"
$b = [IO.File]::ReadAllBytes("$t\stub.exe"); $b[2000] = $b[2000] -bxor 1
[IO.File]::WriteAllBytes("$t\stub_bozuk.exe", $b)
'Write-Output merhaba' | Set-Content "$t\betik.ps1"
foreach ($ad in 'stub.exe', 'stub_bozuk.exe', 'betik.ps1') {
    $s = Get-AuthenticodeSignature -LiteralPath "$t\$ad"
    '{0}|{1}|{2}|{3}' -f $ad, $s.Status, $s.SignatureType, ($s.SignerCertificate.Subject -replace ',.*')
}
Remove-Item $t -Recurse -Force
```

???

```text
stub.exe|Valid|Authenticode|CN=Microsoft Corporation
stub_bozuk.exe|HashMismatch|Authenticode|CN=Microsoft Corporation
betik.ps1|NotSigned|None|
```

`MpSigStub.exe` (Defender'ın güncelleme yardımcısı) imzasını kendi içinde taşır: kopyası yine `Valid`'dir. Tek bir bayt değişince imza hâlâ dosyadadır ve yayıncı okunur, ama içindeki özet dosyanın yeni özetiyle tutmaz: `HashMismatch`. Yayıncı adının görünmesi dosyanın güvenilir olduğunu göstermez. İmzalanmamış betiğin yayıncısı yoktur; son alan boş kalır.
:::

::: gorev İmza envanteri
Çalışma klasöründe `ornekler\` altında birkaç dosya var. Klasördeki her dosya için, ada göre sıralı, şu biçimde bir satır yazdır:

```text
<ad>|<Status>|<SignatureType>|<yayıncı CN'i>
```

- Yayıncı, `SignerCertificate.Subject`'in ilk virgüle kadarki kısmıdır (`CN=...`); imza yoksa boş bırak.
- `$Girdi`'nin ilk satırı klasörün adıdır. Klasör yoksa tek satır `HATA` yazdır.
- Alt klasörlere inme; yalnız dosyaları listele.

Hazırlık şu dosyaları üretir: `notepad.exe`'nin kopyası ve bir baytı değişmiş kopyası, `MpSigStub.exe`'nin kopyası ve bozuk kopyası, `git.exe`'nin kopyası, imzasız bir betik, boş bir dosya ve köşeli parantezli adı olan bir kopya.

```stdin
ornekler
```

```setup
import os, shutil
os.makedirs("ornekler/alt", exist_ok=True)
w = os.environ["WINDIR"] + r"\System32"
def bozuk(kaynak, hedef, konum):
    b = bytearray(open(kaynak, "rb").read()); b[konum] ^= 1
    open(hedef, "wb").write(b)
shutil.copy(w + r"\notepad.exe", "ornekler/notepad.exe")
bozuk(w + r"\notepad.exe", "ornekler/notepad_bozuk.exe", 1000)
shutil.copy(w + r"\MpSigStub.exe", "ornekler/stub.exe")
bozuk(w + r"\MpSigStub.exe", "ornekler/stub_bozuk.exe", 2000)
shutil.copy(w + r"\MpSigStub.exe", "ornekler/[kopya] stub.exe")
git = os.path.join(os.environ["ProgramFiles"], "Git", "cmd", "git.exe")
shutil.copy(git, "ornekler/git.exe")
open("ornekler/betik.ps1", "w").write("Write-Output merhaba\n")
open("ornekler/bos.ps1", "w").close()
shutil.copy(w + r"\notepad.exe", "ornekler/alt/derin.exe")
```

```starter
$klasor = $Girdi[0].Trim()
Get-ChildItem $klasor | ForEach-Object {
    $s = Get-AuthenticodeSignature $_.FullName
    '{0}|{1}' -f $_.Name, $s.Status
}
```

```test
import os
eq(out, "[kopya] stub.exe|Valid|Authenticode|CN=Microsoft Corporation\n"
        "betik.ps1|NotSigned|None|\n"
        "bos.ps1|UnknownError|None|\n"
        "git.exe|Valid|Authenticode|CN=Johannes Schindelin\n"
        "notepad.exe|Valid|Catalog|CN=Microsoft Windows\n"
        "notepad_bozuk.exe|NotSigned|None|\n"
        "stub.exe|Valid|Authenticode|CN=Microsoft Corporation\n"
        "stub_bozuk.exe|HashMismatch|Authenticode|CN=Microsoft Corporation\n",
   "sekiz dosya; katalog imzalı bozuk kopya NotSigned, gömülü imzalı bozuk kopya HashMismatch; köşeli parantezli ad -LiteralPath ister")
eq(run(stdin="olmayan\n"), "HATA\n", "olmayan klasör")
os.makedirs("bos_klasor", exist_ok=True)
eq(run(stdin="bos_klasor\n"), "", "boş klasör")
eq(run(stdin="ornekler\\alt\n"), "derin.exe|Valid|Catalog|CN=Microsoft Windows\n", "alt klasör kendi başına")
```

```solution
$klasor = $Girdi[0].Trim()
if (-not $klasor -or -not (Test-Path -LiteralPath $klasor -PathType Container)) {
    'HATA'
    return
}
Get-ChildItem -LiteralPath $klasor -File | Sort-Object Name | ForEach-Object {
    $s = Get-AuthenticodeSignature -LiteralPath $_.FullName
    $yayinci = if ($s.SignerCertificate) { $s.SignerCertificate.Subject -replace ',.*' } else { '' }
    '{0}|{1}|{2}|{3}' -f $_.Name, $s.Status, $s.SignatureType, $yayinci
}
```

```hint
`Get-ChildItem -LiteralPath $klasor -File | Sort-Object Name` yalnız dosyaları ada göre verir. Köşeli parantezli adlar için hem `Get-ChildItem`'de hem `Get-AuthenticodeSignature`'da `-LiteralPath` kullan.
```

```hint
İmza yoksa `SignerCertificate` `$null`'dur; `-replace ',.*'` ile ilk virgülden sonrasını at.
```
:::

::: gorev Güven kararı
`$Girdi`'nin ilk satırı bir dosya yolu, ikinci satırı **beklenen yayıncının** CN'idir (örneğin `Microsoft Corporation`). Tek satırlık bir karar yazdır:

- `güven`: imza `Valid` **ve** yayıncının CN'i beklenenle birebir aynı;
- `imza geçersiz: <Status>`: durum `Valid` değil;
- `yayıncı farklı: <CN>`: imza geçerli ama yayıncı beklenen değil;
- `HATA`: dosya yoksa ya da satırlardan biri eksikse.

CN karşılaştırması büyük-küçük harfe duyarlıdır ve tam eşleşme ister: `Microsoft Corporation` beklenirken `Microsoft Windows` imzası **farklıdır**.

```stdin
ornekler\stub.exe
Microsoft Corporation
```

```setup
import os, shutil
os.makedirs("ornekler", exist_ok=True)
w = os.environ["WINDIR"] + r"\System32"
shutil.copy(w + r"\MpSigStub.exe", "ornekler/stub.exe")
b = bytearray(open(w + r"\MpSigStub.exe", "rb").read()); b[2000] ^= 1
open("ornekler/stub_bozuk.exe", "wb").write(b)
shutil.copy(w + r"\notepad.exe", "ornekler/notepad.exe")
shutil.copy(os.path.join(os.environ["ProgramFiles"], "Git", "cmd", "git.exe"), "ornekler/git.exe")
open("ornekler/betik.ps1", "w").write("Write-Output merhaba\n")
```

```starter
$s = Get-AuthenticodeSignature $Girdi[0]
if ($s.Status -eq 'Valid') { 'güven' } else { 'imza geçersiz' }
```

```test
eq(out, "güven\n", "geçerli imza ve beklenen yayıncı")
eq(run(stdin="ornekler\\stub_bozuk.exe\nMicrosoft Corporation\n"), "imza geçersiz: HashMismatch\n",
   "yayıncı adı okunsa bile bozuk dosyaya güvenilmez")
eq(run(stdin="ornekler\\notepad.exe\nMicrosoft Corporation\n"), "yayıncı farklı: Microsoft Windows\n",
   "geçerli imza, ama beklenen yayıncı değil")
eq(run(stdin="ornekler\\git.exe\nMicrosoft Corporation\n"), "yayıncı farklı: Johannes Schindelin\n", "üçüncü taraf yayıncı")
eq(run(stdin="ornekler\\git.exe\nJohannes Schindelin\n"), "güven\n", "beklenen üçüncü taraf yayıncı")
eq(run(stdin="ornekler\\stub.exe\nmicrosoft corporation\n"), "yayıncı farklı: Microsoft Corporation\n", "büyük-küçük harf duyarlı")
eq(run(stdin="ornekler\\stub.exe\nMicrosoft\n"), "yayıncı farklı: Microsoft Corporation\n", "kısmi ad yetmez")
eq(run(stdin="ornekler\\betik.ps1\nMicrosoft Corporation\n"), "imza geçersiz: NotSigned\n", "imzasız betik")
eq(run(stdin="ornekler\\yok.exe\nMicrosoft Corporation\n"), "HATA\n", "olmayan dosya")
eq(run(stdin="ornekler\\stub.exe\n"), "HATA\n", "beklenen yayıncı satırı yok")
```

```solution
if ($Girdi.Count -lt 2 -or -not $Girdi[0].Trim() -or -not $Girdi[1].Trim()) {
    'HATA'
    return
}
$yol = $Girdi[0].Trim()
$beklenen = $Girdi[1].Trim()
if (-not (Test-Path -LiteralPath $yol -PathType Leaf)) {
    'HATA'
    return
}
$s = Get-AuthenticodeSignature -LiteralPath $yol
if ($s.Status -ne 'Valid') {
    "imza geçersiz: $($s.Status)"
    return
}
$cn = ($s.SignerCertificate.Subject -replace ',.*') -replace '^CN='
if ($cn -ceq $beklenen) { 'güven' } else { "yayıncı farklı: $cn" }
```

```hint
Önce durum: `Valid` değilse karar orada biter. Sonra yayıncı: `Subject`'in ilk virgüle kadarki kısmından `CN=`'i at ve beklenenle karşılaştır.
```

```hint
PowerShell'de `-eq` büyük-küçük harfe duyarsızdır; birebir karşılaştırma için `-ceq` kullan. Olmayan dosyayı `Test-Path -LiteralPath -PathType Leaf` ile önce sen ayır.
```
:::
