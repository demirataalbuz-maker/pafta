---
id: cm25
title: Sigcheck ve Autorunsc · İmza ve Başlangıç Envanteri
summary: Sysinternals Sigcheck ile bir klasördeki dosyaların imza durumunu CSV olarak almak (Signed, Unsigned, "did not verify"; -e, -u, -s), aracın UTF-16 çıktısını CMD'de more ve type ile düz metne çevirmek, raporu taranan klasörün dışına yazmak ve çıkış koduna güvenmemek; Autorunsc'nin başlangıç envanteri CSV'si, konum başlığı satırları ve iki anlık görüntüyü findstr ile karşılaştırmak.
timeout: 120
---

::: anlat Sigcheck: bir klasörün imza envanteri
PS25'te bir dosyanın imzasını PowerShell'den sordun. Olay incelemesinde aynı soru yüzlerce dosya için sorulur ve Windows ekiplerinin standart aracı Sysinternals **Sigcheck**'tir. Bu tezgahta `sigcheck64.exe` ve `autorunsc64.exe` `PATH`'tedir (Microsoft imzalı, sürüm 2.93 ve 14.3; `tools/sysinternals_kur.ps1` imzayı ve sürümü doğrular).

```bat
@echo off
sigcheck64 -accepteula -nobanner -c "%WINDIR%\System32\notepad.exe" > "%TEMP%\tek.csv"
more < "%TEMP%\tek.csv"
```

| Seçenek | Anlamı |
|---|---|
| `-accepteula` | lisans penceresini açmadan kabul et (betikte şart) |
| `-nobanner` | başlık metnini yazma |
| `-c` | CSV çıktısı: `Path,Verified,Date,Publisher,Company,Description,Product,…` |
| `-h` | MD5, SHA1, PESHA1, PESHA256, SHA256 ve IMP sütunlarını ekle |
| `-e` | yalnız **yürütülebilir** dosyalar (uzantıya değil içeriğe bakar: boş bir `.exe` girmez) |
| `-u` | yalnız imzası doğrulanamayanlar |
| `-s` | alt klasörlere in |

Gerçek araçta ölçülen `Verified` değerleri (PS25'teki dosyaların kopyalarıyla):

| Dosya | `Verified` |
|---|---|
| `notepad.exe` kopyası (katalog imzalı) | `Signed` |
| aynısının bir baytı değişmiş | `Unsigned` |
| `MpSigStub.exe` kopyası (gömülü imza) | `Signed` |
| aynısının bir baytı değişmiş | `The digital signature of the object did not verify.` |
| metin dosyası | `Unsigned` |

Üç pratik tuzak, hepsi ölçüldü:

- **Çıktı UTF-16'dır.** Sigcheck yönlendirilmiş çıktıyı BOM'suz UTF-16 yazar; `type` onu harflerin arasında boş baytlarla gösterir, `findstr` "input is in Unicode format" der. **`more < dosya`** düz metne çevirir; `for /f` ile okumak için ``usebackq`` ve `` `more ^< dosya` `` kullanılır.
- **Raporu taranan klasöre yazma.** `sigcheck -s klasor > klasor\rapor.csv` yazılmakta olan raporu da tarar ve `Error accessing file` satırı üretir.
- **Çıkış koduna güvenme.** Olmayan bir dosya ya da klasör için de çıkış kodu 0'dır; çıktı `No matching files were found.` der. Varlığı `if exist` ile sen denetlersin.

Kaynak: [Sigcheck](https://learn.microsoft.com/en-us/sysinternals/downloads/sigcheck).
:::

::: anlat Autorunsc: başlangıçta ne çalışıyor?
**Autoruns** Windows'un açılışta ve oturum açılışında bir şey çalıştırabildiği yüzlerce yeri (Run anahtarları, servisler, zamanlanmış görevler, sürücüler, Winlogon, tarayıcı eklentileri …) tek listede toplar; `autorunsc` komut satırı sürümüdür. Kalıcılık (persistence) aramanın ilk aracıdır.

| Seçenek | Anlamı |
|---|---|
| `-a *` / `-a b`, `l`, `s`, `t` … | kategori: hepsi / boot execute, logon, servisler, zamanlanmış görevler … |
| `-c` | CSV |
| `-h` | özet sütunları (SHA-256 dahil) |
| `-s` | imzayı doğrula (`Signer` sütunu: `(Verified) Microsoft Windows`, `(Not Verified) …`) |
| `-m` | Microsoft imzalı kayıtları gizle |

```bat
@echo off
autorunsc64 -accepteula -nobanner -a b -c -s -h > "%TEMP%\boot.csv"
type "%TEMP%\boot.csv" | findstr /n "^" | findstr "^1:"
```

Autorunsc yönlendirilmiş çıktıyı **BOM'lu** UTF-16 yazar; bu kez `type` düz metne çevirir. CSV'de iki tür satır vardır: her konum için bir **başlık satırı** (zaman ve konum dolu, `Entry` ve sonrası boş) ve altında o konumun **kayıtları**. Gerçek çıktıdan:

```text
Time,Entry Location,Entry,Enabled,Category,Profile,Description,Signer,Company,Image Path,Version,Launch String,MD5,SHA-1,PESHA-1,PESHA-256,SHA-256,IMP
10/23/2026 2:03:44 AM,HKLM\System\CurrentControlSet\Control\Session Manager\BootExecute,,,Boot Execute,System-wide,,,,,,,,,,,,
9/9/2026 4:20:18 AM,HKLM\System\…\BootExecute,autocheck autochk *,enabled,Boot Execute,System-wide,Auto Check Utility,(Verified) Microsoft Windows,…
```

CMD'nin `for /f "delims=,"` ayrıştırıcısı **ardışık ayırıcıları birleştirir**: başlık satırında üçüncü belirteç `Entry` değil `Boot Execute` olur. Bu yüzden önce kayıt satırlarını süzersin: kayıt satırlarında `Enabled` sütunu `enabled` ya da `disabled`'dır (`findstr /c:",enabled," /c:",disabled,"`).

İki anlık görüntüyü karşılaştırmanın CMD'deki kısa yolu `findstr /v /x /l /g:eski.txt yeni.txt`'dir: yeni dosyanın, eski dosyada **birebir aynısı** olmayan satırları. Ama `findstr` uzun arama dizgilerini kabul etmez: yüzlerce karakterlik Autorunsc satırlarında `FINDSTR: Search string too long.` hatası verir (ölçüldü). Bu yüzden her kayıt önce kısa bir **anahtara** indirgenir: örneğin `Entry,Signer,SHA-256`. Değişen bir kayıt (örneğin SHA-256'sı değişen bir program) iki yönde de görünür: yeni anahtarı "eskide yok", eski anahtarı "yenide yok".

> [!GÜVENLİK]
> Autorunsc gerçek bir sistemde çalıştırıldığında o makinenin bütün başlangıç kayıtlarını, kullanıcı programları ve yolları dahil, listeler. Bu derste canlı çıktı yalnız başlık satırı için kullanılır; görevlerdeki anlık görüntüler gerçek biçimde hazırlanmış örnek satırlardır. Başlangıç kayıtlarını denemek için kayıt defterine yeni bir Run girdisi **eklenmez**: bu, makinenin her açılışını etkileyen kalıcı bir değişikliktir.

Kaynak: [Autoruns ve autorunsc](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns).
:::

::: tahmin Dosya adı ve doğrulama
`ornek` klasöründe beş dosya var: `notepad.exe`'nin kopyası ve bir baytı değişmiş kopyası, `MpSigStub.exe`'nin kopyası ve bir baytı değişmiş kopyası, bir metin dosyası. Ne yazar?

```bat
@echo off
sigcheck64 -accepteula -nobanner -c -s ornek > rapor.csv
for /f "usebackq skip=1 tokens=1,2 delims=," %%a in (`more ^< rapor.csv`) do echo %%~nxa: %%~b
```

```setup
import os, shutil
os.makedirs("ornek", exist_ok=True)
w = os.environ["WINDIR"] + r"\System32"
def bozuk(kaynak, hedef, konum):
    b = bytearray(open(kaynak, "rb").read()); b[konum] ^= 1
    open(hedef, "wb").write(b)
shutil.copy(w + r"\notepad.exe", "ornek/notepad.exe")
bozuk(w + r"\notepad.exe", "ornek/notepad_bozuk.exe", 1000)
shutil.copy(w + r"\MpSigStub.exe", "ornek/stub.exe")
bozuk(w + r"\MpSigStub.exe", "ornek/stub_bozuk.exe", 2000)
open("ornek/not.txt", "w").write("merhaba\n")
```

???

```text
not.txt: Unsigned
notepad.exe: Signed
notepad_bozuk.exe: Unsigned
stub.exe: Signed
stub_bozuk.exe: The digital signature of the object did not verify.
```

`more` UTF-16 raporu düz metne çevirir, `skip=1` başlık satırını atlar. Yol ve doğrulama alanı tırnaklıdır; `%%~nxa` yoldan dosya adını alır, `%%~b` tırnakları atar. Katalog imzalı `notepad.exe`'nin bozuk kopyası `Unsigned` görünür (imza dosyada değil katalogdadır, yeni özet hiçbir katalogda yoktur); gömülü imzalı `stub.exe`'nin bozuk kopyası "did not verify" der. Türkçe Windows aynı doğrulama hatasını `stub_bozuk.exe: Nesnenin dijital imzası doğrulanmadı.` olarak yazabilir; bu dil farkı, imzanın geçerli olduğu anlamına gelmez. Metin dosyası imza taşıyamaz. Rapor klasörün dışında olduğu için listeye girmez.
:::

::: gorev İmzası sorunlu yürütülebilirler
İlk argüman taranacak klasör; boşsa `ornek`. Klasördeki (alt klasörler dahil) **yürütülebilir** dosyalardan imzası `Signed` olmayanları, Sigcheck'in sırasıyla, her biri için tek satırda yazdır:

```text
<dosya adı>: <Verified değeri>
```

En sona `toplam <N>` satırını ekle (N: sorunlu dosya sayısı). Raporu taranan klasörün **içine** yazma. Klasör yoksa stdout boş, stderr `klasor-yok`, çıkış 1; başarıda çıkış 0.

```setup
import os, shutil
os.makedirs("ornek/alt", exist_ok=True)
w = os.environ["WINDIR"] + r"\System32"
def bozuk(kaynak, hedef, konum):
    b = bytearray(open(kaynak, "rb").read()); b[konum] ^= 1
    open(hedef, "wb").write(b)
shutil.copy(w + r"\notepad.exe", "ornek/notepad.exe")
bozuk(w + r"\notepad.exe", "ornek/notepad_bozuk.exe", 1000)
shutil.copy(w + r"\MpSigStub.exe", "ornek/stub.exe")
bozuk(w + r"\MpSigStub.exe", "ornek/alt/stub_bozuk.exe", 2000)
shutil.copy(os.path.join(os.environ["ProgramFiles"], "Git", "cmd", "git.exe"), "ornek/git.exe")
open("ornek/not.txt", "w").write("merhaba\n")
open("ornek/bos.exe", "wb").close()
```

```starter
@echo off
set "klasor=%~1"
if not defined klasor set "klasor=ornek"
sigcheck64 -accepteula -nobanner -c -u -s "%klasor%" > "%klasor%\rapor.csv"
type "%klasor%\rapor.csv"
```

```test
from pathlib import Path
import os, shutil
# Native verification messages are localized by Windows. Independently read
# the actual Sigcheck CSV; still require exactly the two damaged executables.
import csv, io, subprocess, sys
raw = subprocess.run([str(Path(sys.modules["__main__"].__file__).resolve().parents[1]/".deps"/"sysinternals"/"sigcheck64.exe"), "-accepteula", "-nobanner", "-c", "-e", "-u", "-s", "ornek"], capture_output=True, check=False).stdout
text = raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-16-le" if b"\x00" in raw[:100] else "utf-8-sig")
records = list(csv.reader(io.StringIO(text)))
rows = [r for r in records[1:] if len(r) >= 2 and r[1].strip()]
eq(sorted(Path(r[0]).name for r in rows), ["notepad_bozuk.exe", "stub_bozuk.exe"], "yalnız iki bozuk PE; metin, boş dosya ve imzalı kopyalar dışarıda")
ok(all(r[1] != "Signed" for r in rows), "iki doğrulama da başarısız")
expected = "".join(Path(r[0]).name + ": " + r[1] + "\n" for r in rows) + "toplam 2\n"
eq(out, expected, "Sigcheck sırası ve gerçek yerelleştirilmiş Verified alanı korunur")
ok(not any(p.name.lower().endswith(".csv") for p in Path("ornek").rglob("*")), "rapor taranan klasöre yazılmamış")
os.makedirs("temiz", exist_ok=True)
shutil.copy(os.environ["WINDIR"] + r"\System32\notepad.exe", "temiz/notepad.exe")
r = calis(argv=["temiz"])
eq((r["kod"], r["cikti"]), (0, "toplam 0\n"), "sorunsuz klasör")
os.makedirs("bos klasor", exist_ok=True)
r = calis(argv=["bos klasor"])
eq((r["kod"], r["cikti"]), (0, "toplam 0\n"), "boşluklu adlı boş klasör")
r = calis(argv=["olmayan"])
eq((r["kod"], r["cikti"], r["hata"]), (1, "", "klasor-yok\n"), "olmayan klasör: Sigcheck 0 döndürse de hata")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "klasor=%~1"
if not defined klasor set "klasor=ornek"
if not exist "%klasor%\" goto yok
sigcheck64 -accepteula -nobanner -c -e -u -s "%klasor%" > "rapor.csv"
set /a toplam=0
for /f "usebackq skip=1 tokens=1,2 delims=," %%a in (`more ^< rapor.csv`) do (
    if not "%%~b"=="" (
        echo %%~nxa: %%~b
        set /a toplam+=1
    )
)
echo toplam %toplam%
exit /b 0
:yok
>&2 echo klasor-yok
exit /b 1
```

```hint
`-e` yalnız yürütülebilirleri, `-u` yalnız imzası doğrulanamayanları verir; ikisi birlikte istenen listeyi çıkarır. Raporu klasörün dışında (çalışma klasöründe) tut.
```

```hint
Rapor UTF-16'dır: `for /f "usebackq skip=1 tokens=1,2 delims=," %%a in (`` `more ^< rapor.csv` ``)`. Sorunlu dosya yoksa Sigcheck "No matching files were found." yazar; bu satırda ikinci belirteç boştur, sayma. Klasörün varlığını `if not exist "%klasor%\"` ile sen denetle.
```
:::

::: gorev Başlangıç envanterini karşılaştır
Çalışma klasöründe iki Autorunsc anlık görüntüsü var: `onceki.csv` ve `simdi.csv` (`autorunsc -c -s -h` biçimi, BOM'lu UTF-16). Kayıt satırlarını (Enabled sütunu `enabled` ya da `disabled` olanlar) **Entry, Signer ve SHA-256** alanlarına göre karşılaştır ve yazdır:

- `simdi.csv`'de olup `onceki.csv`'de bu üç alanı aynı olan bir karşılığı **olmayan** her kayıt için, dosyadaki sırasıyla: `FARKLI <Entry> | <Signer>`
- `onceki.csv`'de olup `simdi.csv`'de karşılığı olmayan her kayıt için: `SILINEN <Entry>`
- En sonda: `toplam <farklı sayısı> farkli, <silinen sayısı> silinen`

Konum başlığı satırları (zamanı değişse bile) karşılaştırmaya girmez. Argümanlar: önce eski, sonra yeni dosya; boşsa `onceki.csv` ve `simdi.csv`. İki dosyadan biri yoksa stdout boş, stderr `dosya-yok`, çıkış 1.

```setup
BASLIK = "Time,Entry Location,Entry,Enabled,Category,Profile,Description,Signer,Company,Image Path,Version,Launch String,MD5,SHA-1,PESHA-1,PESHA-256,SHA-256,IMP"
def satir(zaman, konum, kayit, durum, kategori, profil, aciklama, imzaci, sirket, yol, surum, komut, sha256):
    return ",".join([zaman, konum, kayit, durum, kategori, profil, aciklama, imzaci, sirket, yol, surum, komut,
                     "A" * 32, "B" * 40, "C" * 40, "D" * 64, sha256, ""])
RUN_M = r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
RUN_U = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
GOREV = r"Task Scheduler"
def basliklar(zaman):
    return [f"{zaman},{RUN_M},,,Logon,System-wide,,,,,,,,,,,,", f"{zaman},{RUN_U},,,Logon,ornek-kullanici,,,,,,,,,,,,",
            f"{zaman},{GOREV},,,Tasks,System-wide,,,,,,,,,,,,"]
GUVENLIK = satir("9/9/2026 4:20:18 AM", RUN_M, "SecurityHealth", "enabled", "Logon", "System-wide", "Windows Security notification icon",
                 "(Verified) Microsoft Windows", "Microsoft Corporation", r"C:\Windows\System32\SecurityHealthSystray.exe",
                 "10.0.26100.1", r"%windir%\system32\SecurityHealthSystray.exe", "1" * 64)
ONEDRIVE = satir("9/1/2026 8:00:00 AM", RUN_U, "OneDrive", "enabled", "Logon", "ornek-kullanici", "Microsoft OneDrive",
                 "(Verified) Microsoft Corporation", "Microsoft Corporation", r"C:\Program Files\Microsoft OneDrive\OneDrive.exe",
                 "25.1.0.1", r"C:\Program Files\Microsoft OneDrive\OneDrive.exe /background", "2" * 64)
YEDEK_ESKI = satir("8/15/2026 2:00:00 AM", GOREV, r"\Pafta\GeceYedegi", "enabled", "Tasks", "System-wide", "Gece yedegi",
                   "(Not Verified) Pafta Lab", "Pafta Lab", r"C:\Araclar\yedek.exe", "1.0.0.0", r"C:\Araclar\yedek.exe /gece", "3" * 64)
YEDEK_YENI = YEDEK_ESKI.replace("3" * 64, "4" * 64)
SURUCU = satir("7/1/2026 9:00:00 AM", GOREV, r"\Pafta\Rapor", "disabled", "Tasks", "System-wide", "Haftalik rapor",
               "(Verified) Pafta Lab", "Pafta Lab", r"C:\Araclar\rapor.exe", "2.0.0.0", r"C:\Araclar\rapor.exe", "5" * 64)
GUNCELLEYICI = satir("10/24/2026 3:14:00 AM", RUN_U, "Guncelleyici", "enabled", "Logon", "ornek-kullanici", "Guncelleme Yardimcisi",
                     "(Not Verified)", "Bilinmiyor", r"C:\Users\Public\guncelle.exe", "0.1.0.0", r"C:\Users\Public\guncelle.exe -q", "6" * 64)
def yaz(ad, satirlar):
    open(ad, "w", encoding="utf-16", newline="\r\n").write("\n".join(satirlar) + "\n")
b1, b2 = basliklar("10/23/2026 2:03:44 AM"), basliklar("10/24/2026 9:00:00 AM")
yaz("onceki.csv", [BASLIK, b1[0], GUVENLIK, b1[1], ONEDRIVE, b1[2], YEDEK_ESKI, SURUCU])
yaz("simdi.csv", [BASLIK, b2[0], GUVENLIK, b2[1], GUNCELLEYICI, b2[2], YEDEK_YENI, SURUCU])
yaz("ayni.csv", [BASLIK, b2[0], GUVENLIK, b2[1], ONEDRIVE, b2[2], YEDEK_ESKI, SURUCU])
```

```starter
@echo off
fc onceki.csv simdi.csv
```

```test
eq(out, "FARKLI Guncelleyici | (Not Verified)\nFARKLI \\Pafta\\GeceYedegi | (Not Verified) Pafta Lab\n"
        "SILINEN OneDrive\nSILINEN \\Pafta\\GeceYedegi\ntoplam 2 farkli, 2 silinen\n",
   "yeni kayıt, SHA-256'sı değişen görev (iki yönde) ve silinen kayıt")
r = calis(argv=["onceki.csv", "ayni.csv"])
eq((r["kod"], r["cikti"]), (0, "toplam 0 farkli, 0 silinen\n"), "yalnız konum başlıklarının zamanı değişmiş: fark yok")
r = calis(argv=["simdi.csv", "onceki.csv"])
eq(r["cikti"], "FARKLI OneDrive | (Verified) Microsoft Corporation\nFARKLI \\Pafta\\GeceYedegi | (Not Verified) Pafta Lab\n"
               "SILINEN Guncelleyici\nSILINEN \\Pafta\\GeceYedegi\ntoplam 2 farkli, 2 silinen\n", "ters yönde karşılaştırma")
r = calis(argv=["onceki.csv", "olmayan.csv"])
eq((r["kod"], r["cikti"], r["hata"]), (1, "", "dosya-yok\n"), "yeni dosya yok")
r = calis(argv=["olmayan.csv", "simdi.csv"])
eq((r["kod"], r["cikti"], r["hata"]), (1, "", "dosya-yok\n"), "eski dosya yok")
r = calis(argv=["ayni.csv", "ayni.csv"])
eq((r["kod"], r["cikti"]), (0, "toplam 0 farkli, 0 silinen\n"), "önceki çalıştırmaların ara dosyaları sonuca karışmaz")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "eski=%~1"
if not defined eski set "eski=onceki.csv"
set "yeni=%~2"
if not defined yeni set "yeni=simdi.csv"
if not exist "%eski%" goto yok
if not exist "%yeni%" goto yok
type nul > eski_anahtar.txt
type nul > yeni_anahtar.txt
for /f "usebackq tokens=3,8,17 delims=," %%a in (`type "%eski%" ^| findstr /c:",enabled," /c:",disabled,"`) do >>eski_anahtar.txt echo %%a,%%b,%%c
for /f "usebackq tokens=3,8,17 delims=," %%a in (`type "%yeni%" ^| findstr /c:",enabled," /c:",disabled,"`) do >>yeni_anahtar.txt echo %%a,%%b,%%c
set /a farkli=0, silinen=0
for /f "usebackq tokens=1,2 delims=," %%a in (`findstr /v /x /l /g:eski_anahtar.txt yeni_anahtar.txt`) do (
    echo FARKLI %%a ^| %%b
    set /a farkli+=1
)
for /f "usebackq tokens=1 delims=," %%a in (`findstr /v /x /l /g:yeni_anahtar.txt eski_anahtar.txt`) do (
    echo SILINEN %%a
    set /a silinen+=1
)
echo toplam %farkli% farkli, %silinen% silinen
exit /b 0
:yok
>&2 echo dosya-yok
exit /b 1
```

```hint
Önce iki dosyayı da `type` ile düz metne çevirip yalnız kayıt satırlarını süz: `type dosya | findstr /c:",enabled," /c:",disabled,"`. Konum başlıklarında `Enabled` sütunu boştur.
```

```hint
Satırlar `findstr /g:` için fazla uzun: her kaydı `tokens=3,8,17 delims=,` ile `Entry,Signer,SHA-256` anahtarına indirip ayrı bir dosyaya yaz (bu örneklerde ilk on yedi alan dolu). Sonra `findstr /v /x /l /g:eski_anahtar.txt yeni_anahtar.txt` ve ters yönü. Ekrana `|` yazmak için `^|`.
```
:::
