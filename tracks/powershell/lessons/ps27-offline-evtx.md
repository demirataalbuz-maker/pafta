---
id: ps27
title: Offline EVTX · Get-WinEvent -Path ve Kaynakta Süzmek
summary: Başka bir makineden gelen .evtx dosyasını canlı günlüğe dokunmadan okumak: Get-WinEvent -Path, varsayılan sıranın en yeniden başlaması ve -Oldest, Properties ile sıralı alanlar, ToXml, TimeCreated'ın yerel saat olması; FilterXPath (EventID, Level, TimeCreated/@SystemTime UTC, Data değeri) ve FilterHashtable'ın StartTime'ı; boş dosya, eşleşme yok, bozuk dosya ve olmayan dosya hatalarını birbirinden ayırmak; XPath'e girdi koymadan önce biçimi denetlemek.
kazanim: AZ040 2.3, AZ040 7.4
---

::: anlat Bir olay dosyasını yerinde okumak
`ps16`–`ps21` derslerinde olayları önceden dönüştürülmüş veriden okuduk. Bir incelemede ise çoğu zaman elinde **başka bir makineden kopyalanmış** `.evtx` dosyası olur: `System.evtx`, `Security.evtx`, `Microsoft-Windows-PowerShell%4Operational.evtx`. Bu dosyayı kendi makinenin günlüğüne aktarmadan, yönetici olmadan, olduğu yerde okursun:

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps27"]()
```

```powershell
Get-WinEvent -Path .\sistem.evtx -Oldest -MaxEvents 4 | ForEach-Object {
    "{0} {1} L{2} {3} | {4}" -f $_.RecordId, $_.Id, $_.Level,
        $_.TimeCreated.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss'Z'"),
        ($_.Properties.Value -join " | ")
}
```

Bu dersin çalışma klasöründeki `sistem.evtx`, `bos.evtx` ve `bozuk.evtx` her çalıştırmada yeniden üretilir. Dönüşümü Windows'un kendisi yapar (`wevtutil epl`); hiçbir canlı günlüğe yazılmaz.

| Özellik | Ne verir |
|---|---|
| `RecordId` | Dosyadaki kayıt numarası; dosya içinde sırayı gösterir |
| `Id`, `ProviderName` | Olay kimliği ve sağlayıcı: `7045` + `Service Control Manager` = yeni servis |
| `Level` | Sayı: 1 kritik, 2 hata, 3 uyarı, 4 bilgi, 5 ayrıntı. `LevelDisplayName` sistem diline göre çevrilir; karşılaştırmada sayıyı kullan |
| `TimeCreated` | **Yerel saate** çevrilmiş `DateTime`. Raporda `.ToUniversalTime()` |
| `Properties` | `EventData` değerleri, **sırayla**: `$_.Properties[0].Value` |
| `Message` | Sağlayıcının mesaj şablonuyla üretilen metin. Şablon bu makinede yoksa boş gelir, varsa dile göre değişir; kanıt olarak alanları kullan |
| `ToXml()` | Olayın ham XML'i: `[xml]$_.ToXml()` |

> [!TUZAK] Varsayılan sıra en yeniden eskiye
> `Get-WinEvent` kayıtları **en yeniden** başlayarak verir. `-MaxEvents 2` dosyanın ilk iki kaydını değil, **son** iki kaydını getirir; bu dosyada `10 9`. Dosya sırası için `-Oldest` ekle. Bir dizi olayı zaman çizelgesi gibi okuyacaksan `-Oldest` hemen hemen her zaman gerekir.

> [!DERİN] Bu derste Data alanlarının adı yok
> Gerçek bir manifest sağlayıcısının olayında XML `<Data Name='ServiceName'>PaftaYedek</Data>` gibidir. Bu dersin dosyaları Windows'un eski EVT biçiminden çevrildiği için `<Data>PaftaYedek</Data>` olarak, **adsız** gelir. `Properties[n]` iki durumda da aynı sırayla çalışır; ada göre seçen sorgular (`Data[@Name='ServiceName']`) burada eşleşmez.
:::

::: anlat Kaynakta süzmek: FilterXPath ve FilterHashtable
`Get-WinEvent ... | Where-Object` bütün dosyayı okuyup sonra eler. Büyük bir `Security.evtx`'te bu dakikalar sürer. Süzgeci okuyucuya ver; yalnız eşleşen kayıtlar okunur:

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps27"]()
```

```powershell
$sorgu = "*[System[(EventID=7036 or EventID=7045) and Level<=3]]"
(Get-WinEvent -Path .\sistem.evtx -Oldest -FilterXPath $sorgu).RecordId -join ","
$pencere = "*[System[TimeCreated[@SystemTime>='2026-01-01T09:01:00Z' and @SystemTime<='2026-01-01T09:02:00Z']]]"
(Get-WinEvent -Path .\sistem.evtx -Oldest -FilterXPath $pencere).RecordId -join ","
(Get-WinEvent -Path .\sistem.evtx -Oldest -FilterXPath "*[EventData[Data='PaftaYedek']]").RecordId -join ","
```

| XPath parçası | Anlamı |
|---|---|
| `*[System[EventID=7045]]` | Olay kimliği |
| `(EventID=7036 or EventID=7045)` | Birkaç kimlik |
| `Level<=3` | Uyarı ve daha ağırları (3 uyarı, 2 hata, 1 kritik) |
| `TimeCreated[@SystemTime>='...Z']` | Zaman, **UTC** ve ISO biçiminde; `>=` ve `<=` uçları dahil eder |
| `*[EventData[Data='PaftaYedek']]` | Herhangi bir `Data` değeri tam olarak bu |

`FilterHashtable` aynı şeyi anahtarlarla söyler: `@{ Path = "$PWD\sistem.evtx"; Id = 7036, 7045; Level = 2, 3; StartTime = ...; Data = 'PaftaYedek' }`.

Eşleşme yoksa ya da dosya boşsa sonuç boş bir liste değildir: `Get-WinEvent` bir **hata** yazar. Ayırt etmen gereken dört durum:

| Durum | Ne olur | Hata türü |
|---|---|---|
| Eşleşme yok / dosya boş | `NoMatchingEventsFound`, `$?` `$false`, sonuç `$null` | sonlandırmayan |
| Dosya yok | Yol bulunamadı hatası | sonlandırmayan |
| Dosya bozuk | `EventLogException`: "Insufficient information exists to identify the cause of failure" | **sonlandıran** |
| XPath bozuk | `EventLogException`: "The specified query is invalid" | **sonlandıran** |

> [!TUZAK] `-ErrorAction` bu hataların hepsini aynı biçimde etkilemez
> Bu derste ölçüldü. `-ErrorAction SilentlyContinue` sonlandırmayan iki hatayı susturur: olmayan bir dosya da sessizce "0 olay" olur. Bozuk dosya ve bozuk XPath ise `SilentlyContinue` yazsan bile `EventLogException` fırlatır ve `try` yoksa betik orada durur. Bir incelemede "olay yok", "dosya yok" ve "dosyayı okuyamadım" üç ayrı sonuçtur. Dosyanın varlığını `Test-Path -LiteralPath` ile sor. Okumayı `-ErrorAction Stop` ile yap, okunamayan dosyayı `catch [System.Diagnostics.Eventing.Reader.EventLogException]` ile ayır, `NoMatchingEventsFound`'u sıfır olay say.

> [!TUZAK] XPath'e girdiyi biçimini denetlemeden koyma
> Kullanıcıdan gelen bir kimliği `"*[System[EventID=$girdi]]"` diye sorguya yapıştırırsan `7036 or 1=1` gibi bir girdi sorgunun anlamını değiştirir. Bu SQL'deki enjeksiyonun aynısıdır, yalnız dil farklıdır. Önce biçimi (`^\d+$`, ISO zaman) bir düzenli ifadeyle denetle, uymayanı reddet.
:::

::: tahmin
Bu makinenin saat dilimi Türkiye (UTC+3). Ne yazar?

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps27"]()
```

```powershell
$utc = [datetime]::new(2026, 1, 1, 9, 4, 0, [DateTimeKind]::Utc)
@(Get-WinEvent -FilterHashtable @{ Path = "$PWD\sistem.evtx"; StartTime = $utc }).Count
@(Get-WinEvent -Path .\sistem.evtx -FilterXPath "*[System[TimeCreated[@SystemTime>='2026-01-01T09:04:00Z']]]").Count
```

???

`10` ve `3`.

Dosyada UTC 09:04'ten sonra üç kayıt var (8, 9 ve 10); XPath bunları bulur. `FilterHashtable` ise `StartTime`'ı, `DateTime`'ın `Kind` değeri `Utc` olsa bile **yerel saat** sayar. Bu derste ölçüldü: `09:04` İstanbul saatiyle okunur, yani UTC 06:04. Dosyanın on kaydının hepsi bundan sonradır. Aynı anı `FilterHashtable` ile istiyorsan `StartTime = [datetime]'2026-01-01 12:04:00'` (yerel) yazmalısın. Zamanı UTC düşünüyorsan XPath'te `@SystemTime` kullan; orada saat dilimi tartışması yoktur.
:::

::: gorev Olay dosyası özeti
Girdinin ilk satırı bir `.evtx` dosyasının adıdır. Dosyadaki olayları **olay kimliği ve seviyeye** göre say. Her satır `<Id> <Level> <adet>` olsun; satırları kimliğe, sonra seviyeye göre **sayısal** sırala. En sona `toplam <olay sayısı>` ekle.

- Dosya boşsa yalnız `toplam 0` yazdır.
- Dosya okunamıyorsa (bozuksa) `HATA: okunamadi`, böyle bir dosya yoksa `HATA: dosya yok`, girdi boşsa `HATA: girdi yok` yazdır.

Çalışma klasöründe `sistem.evtx`, boş bir `bos.evtx` ve olay günlüğü olmayan bir `bozuk.evtx` var.

```stdin
sistem.evtx
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps27"]()
```

```starter
$dosya = $Girdi[0]
Get-WinEvent -Path $dosya | Group-Object Id | ForEach-Object { "$($_.Name) $($_.Count)" }
```

```test
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
fx = runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))
eq(out, "1074 4 1\n6005 4 1\n6006 4 1\n7031 2 1\n7036 4 4\n7045 3 1\n7045 4 1\ntoplam 10\n",
   "sistem.evtx: kimlik ve seviyeye göre")
B, H, U = fx["BILGI"], fx["HATA"], fx["UYARI"]
fx["evtx"]("ek.evtx", [(900, B, 0, "Pafta", ["a"]), (10000, H, 1, "Pafta", ["b"]), (1074, U, 2, "Pafta", ["c"]),
                       (900, H, 3, "Pafta", ["d"]), (900, B, 4, "Pafta", ["e"])])
eq(run(stdin="ek.evtx\n"), "900 2 1\n900 4 2\n1074 3 1\n10000 2 1\ntoplam 5\n",
   "sayısal sıra: 900 < 1074 < 10000 (metin olarak sıralarsan 10000 başa geçer)")
eq(run(stdin="bos.evtx\n"), "toplam 0\n", "boş dosya: hata değil, sıfır olay")
eq(run(stdin="bozuk.evtx\n"), "HATA: okunamadi\n", "bozuk dosya sıfır olay sayılmamalı")
eq(run(stdin="yok.evtx\n"), "HATA: dosya yok\n", "olmayan dosya")
eq(run(stdin=""), "HATA: girdi yok\n", "boş girdi")
eq(run(stdin="  \n"), "HATA: girdi yok\n", "yalnız boşluk")
```

```solution
$dosya = if ($Girdi.Count) { $Girdi[0].Trim() } else { "" }
if (-not $dosya) { "HATA: girdi yok"; exit 0 }
if (-not (Test-Path -LiteralPath $dosya -PathType Leaf)) { "HATA: dosya yok"; exit 0 }
try {
    $olaylar = @(Get-WinEvent -Path $dosya -Oldest -ErrorAction Stop)
} catch [System.Diagnostics.Eventing.Reader.EventLogException] {
    "HATA: okunamadi"
    exit 0
} catch {
    if ($_.FullyQualifiedErrorId -notlike "NoMatchingEventsFound*") { throw }
    $olaylar = @()
}
$olaylar | Group-Object Id, Level | ForEach-Object {
    [pscustomobject]@{ Id = [int]$_.Group[0].Id; Level = [int]$_.Group[0].Level; Adet = $_.Count }
} | Sort-Object Id, Level | ForEach-Object { "{0} {1} {2}" -f $_.Id, $_.Level, $_.Adet }
"toplam $($olaylar.Count)"
```

```hint
`Get-WinEvent -ErrorAction Stop` hatayı yakalanabilir yapar. `catch [System.Diagnostics.Eventing.Reader.EventLogException]` okunamayan dosyayı yakalar. Boş dosyanın hatası başka türdendir: genel `catch`'te `$_.FullyQualifiedErrorId -like "NoMatchingEventsFound*"` ise sıfır olay say. Dosyanın varlığını önce `Test-Path -LiteralPath` ile sor.
```

```hint
`Group-Object Id, Level` grubun adını metin yapar (`"7045, 3"`); o adla sıralarsan `10000` `900`'den önce gelir. Her gruptan `[int]` kimlik ve seviyeyi bir nesneye koy, `Sort-Object Id, Level` ile sırala.
```
:::

::: gorev Zaman penceresinde XPath
`sistem.evtx`'ten belirli olayları **kaynakta süzerek** getir. Girdi:

1. satır: virgülle ayrılmış olay kimlikleri, boşluksuz (`7036,7045`)
2. satır: başlangıç, UTC: `2026-01-01T09:01:00Z`
3. satır: bitiş, aynı biçimde

Kimliklerden biriyle eşleşen ve iki uç **dahil** pencerede kalan olayları dosya sırasıyla `<RecordId> <UTC zaman> <ilk Data değeri>` biçiminde yazdır. Zaman `yyyy-MM-ddTHH:mm:ssZ` biçiminde olsun; olayın hiç `Data` değeri yoksa üçüncü alan `-` olur. Eşleşme yoksa `yok` yazdır.

Kimlik satırı yalnız rakam ve tek virgüllerden oluşmuyorsa ya da zamanlar bu biçimde değilse sorguyu hiç kurma, `HATA` yazdır. Süzmeyi `-FilterXPath` ile yap; `Where-Object` kullanma.

```stdin
7036,7045
2026-01-01T09:01:00Z
2026-01-01T09:04:00Z
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps27"]()
```

```starter
$sorgu = "*[System[EventID=$($Girdi[0])]]"
Get-WinEvent -Path .\sistem.evtx -FilterXPath $sorgu | ForEach-Object { "$($_.RecordId) $($_.TimeCreated)" }
```

```test
import re
eq(out, "3 2026-01-01T09:01:00Z PaftaYedek\n4 2026-01-01T09:01:01Z PaftaYedek\n6 2026-01-01T09:02:01Z PaftaYedek\n"
        "7 2026-01-01T09:03:00Z Guncelleyici\n8 2026-01-01T09:04:00Z Windows Update\n",
   "iki kimlik, 09:01–09:04 UTC; bitiş anındaki kayıt (8) dahil")
eq(run(stdin="6005,6006\n2026-01-01T09:00:00Z\n2026-01-01T09:05:01Z\n"),
   "1 2026-01-01T09:00:00Z -\n10 2026-01-01T09:05:01Z -\n", "iki uç dahil; Data'sı olmayan olayda -")
eq(run(stdin="7031\n2026-01-01T09:02:00Z\n2026-01-01T09:02:00Z\n"), "5 2026-01-01T09:02:00Z PaftaYedek\n",
   "başlangıç ve bitiş aynı an")
eq(run(stdin="7031\n2026-01-01T09:02:01Z\n2026-01-01T09:03:00Z\n"), "yok\n", "pencerede olay yok")
eq(run(stdin="7036\n2026-01-01T09:04:00Z\n2026-01-01T09:01:00Z\n"), "yok\n", "başlangıç bitişten sonra")
eq(run(stdin="7036 or 1=1\n2026-01-01T09:00:00Z\n2026-01-01T09:10:00Z\n"), "HATA\n", "kimlik satırında XPath parçası")
eq(run(stdin="7036\n2026-01-01T09:00:00Z' or '1'='1\n2026-01-01T09:10:00Z\n"), "HATA\n", "zamanda tırnak")
eq(run(stdin="7036,,7045\n2026-01-01T09:00:00Z\n2026-01-01T09:10:00Z\n"), "HATA\n", "boş kimlik")
eq(run(stdin="7036\n2026-01-01T09:00:00\n2026-01-01T09:10:00Z\n"), "HATA\n", "Z'siz zaman")
eq(run(stdin="7036\n"), "HATA\n", "eksik satırlar")
eq(run(stdin=""), "HATA\n", "boş girdi")
ok("FilterXPath" in src, "süzmeyi -FilterXPath ile yap")
ok(not re.search(r"Where-Object|\?\s*\{", src), "Where-Object kullanma: süzgeç okuyucuda olmalı")
```

```solution
$satir = @($Girdi | ForEach-Object { $_.Trim() }) + @("", "", "")
$kimlik, $bas, $son = $satir[0], $satir[1], $satir[2]
$zaman = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
if ($kimlik -notmatch '^\d+(,\d+)*$' -or $bas -notmatch $zaman -or $son -notmatch $zaman) {
    "HATA"
    exit 0
}
$idler = ($kimlik -split "," | ForEach-Object { "EventID=$_" }) -join " or "
$sorgu = "*[System[($idler) and TimeCreated[@SystemTime>='$bas' and @SystemTime<='$son']]]"
try {
    $olaylar = @(Get-WinEvent -Path .\sistem.evtx -Oldest -FilterXPath $sorgu -ErrorAction Stop)
} catch {
    if ($_.FullyQualifiedErrorId -notlike "NoMatchingEventsFound*") { throw }
    $olaylar = @()
}
if (-not $olaylar.Count) { "yok"; exit 0 }
foreach ($o in $olaylar) {
    $ilk = if ($o.Properties.Count) { $o.Properties[0].Value } else { "-" }
    "{0} {1} {2}" -f $o.RecordId, $o.TimeCreated.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss'Z'"), $ilk
}
```

```hint
Kimlikleri `-split ","` ile ayırıp her birini `"EventID=$_"` yap, `-join " or "` ile birleştir ve parantez içine al. Zaman koşulu: `TimeCreated[@SystemTime>='$bas' and @SystemTime<='$son']`. Biçim denetimi sorguyu kurmadan **önce** gelmeli: `-notmatch '^\d+(,\d+)*$'`.
```

```hint
`TimeCreated` yerel saattir: `.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss'Z'")`. Tırnak içindeki `T` ve `Z` biçim harfi sayılmaz, olduğu gibi yazılır.
```
:::
