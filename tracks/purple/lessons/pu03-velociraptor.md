---
id: pu03
title: Uç Nokta Avcılığı · Velociraptor ve VQL
summary: Velociraptor ve VQL ile bir uç noktanın dosya ağacında avcılık; SELECT ... FROM glob(...) WHERE, birden çok desen, relpath, Mtime ve timestamp ile zaman penceresi, hash() ile SHA256; Velociraptor glob'unun Linux'ta da büyük-küçük harfe duyarsız olması; kullanıcı ve bütün kullanıcılar başlangıç klasörleri ile zamanlanmış görev dosyaları; desktop.ini gibi sıradan dosyaları ayıklamak. Gerçek Velociraptor 0.77.3, toplanmış bir disk kopyası.
---

::: anlat Bir uç noktaya soru sormak
Olay müdahalesinde PU02'deki zaman çizelgesi "pc-ayse'de bir şey çalıştı" der. Sonraki soru o cihazın üstündedir: **ne bıraktı, açılışta ne başlıyor?** **Velociraptor**, binlerce uç noktaya aynı anda bu tür soruları soran açık kaynak bir avcılık ve adli bilişim aracıdır. Sorular **VQL** ile yazılır; SQL'e benzer, ama tablolar yerine **eklentilerden** okur:

```vql
SELECT relpath(path=OSPath, base=Kok) AS Yol, Size, Mtime
FROM glob(globs="Users/*/Downloads/*", root=Kok)
WHERE Size > 0
ORDER BY Mtime
```

| Parça | Anlamı |
|---|---|
| `glob(globs=..., root=...)` | dosya ağacında desenle arar; `*` bir ad parçası, `**` her derinlik; `globs` bir liste de olabilir |
| `OSPath`, `Size`, `Mtime` | glob'un her satırı: tam yol, boyut, son değişiklik zamanı (UTC) |
| `relpath(path=OSPath, base=Kok)` | yolu köke göre göreli yazar |
| `hash(path=OSPath).SHA256` | dosyanın SHA256 özeti; bir IOC listesine girer |
| `timestamp(string="2026-10-19T09:00:00Z")` | metinden zaman; `Mtime` ile karşılaştırılır |
| `Ad =~ "desen"` | düzenli ifade eşleşmesi; VQL'de varsayılan olarak büyük-küçük harfe duyarsız |

Windows'ta açılışta başlayan en eski yerlerden ikisi **başlangıç klasörleridir**: her kullanıcınınki `Users/<ad>/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup` ve bütün kullanıcılarınki `ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp`. Zamanlanmış görevler de `Windows/System32/Tasks` altında birer XML dosyasıdır.

> [!NOT] Laboratuvar
> Gerçek bir dizüstünün dosya ağacı yerine, görevin hazırlığı çalışma klasöründe küçük bir **laboratuvar disk kopyası** kurar (dosyalar zararsız metinlerdir). Velociraptor'ın resmi Linux sürümü WSL'de `velociraptor query` ile tek bir sorgu olarak çalışır; istemci ya da sunucu kurulmaz. Kopyanın kökü sorguda `Kok` değişkenidir. Gerçek bir olayda aynı sorguyu Velociraptor sunucusundan bir "hunt" olarak bütün cihazlara gönderirsin.
:::

::: tahmin
Kopyada iki başlangıç klasörü var: ayşe'nin ve can'ın `Startup` klasörleri ve bütün kullanıcıların `StartUp` klasörü (büyük **U**). İçlerinde toplam dört dosya var: `guncelle.lnk`, `desktop.ini`, `OneNote.lnk` ve `yedek.bat`. Bu sorgu kaç sayar? Velociraptor burada Linux'ta çalışıyor.

```vql
SELECT count() AS n FROM glob(globs="**/Startup/*", root=Kok) GROUP BY 1
```

???

**`4`.**

```
4
```

Linux dosya adlarında büyük-küçük harf ayrıdır, ama Velociraptor'ın `glob`'u desenleri **duyarsız** eşler. Bu, Windows'tan toplanmış ağaçlarda tam istenen şeydir: `Startup` deseni `StartUp`'ı da buldu. Dört dosyanın biri (`desktop.ini`) ise klasörün kendi ayar dosyasıdır; bir avcılık sorgusu onu ayıklamalıdır.

```meta
motor: velociraptor
```

```setup
import calendar
import os
import time


def dosya(yol, icerik, zaman):
    yol = os.path.join("disk", *yol.split("/"))
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "wb") as f:
        f.write(icerik if isinstance(icerik, bytes) else icerik.encode("utf-8"))
    t = calendar.timegm(time.strptime(zaman, "%Y-%m-%d %H:%M:%S"))
    os.utime(yol, (t, t))


BASLAT = "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
dosya(f"Users/ayse/{BASLAT}/guncelle.lnk", "lnk: C:\\Users\\ayse\\AppData\\Local\\Temp\\guncelle.exe", "2026-10-19 09:03:50")
dosya(f"Users/ayse/{BASLAT}/desktop.ini", "[.ShellClassInfo]\n", "2025-06-01 08:00:00")
dosya(f"Users/can/{BASLAT}/OneNote.lnk", "lnk: C:\\Program Files\\Microsoft Office\\ONENOTE.EXE", "2025-03-01 10:00:00")
dosya("ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/yedek.bat", "@echo off\r\ncopy *.docx \\\\srv-yedek\\pay\r\n", "2026-10-19 09:10:05")
dosya("Users/ayse/Downloads/fatura.zip", b"PK\x03\x04egitim", "2026-10-19 09:02:30")
dosya("Users/ayse/Downloads/fatura.exe", b"MZ egitim verisi", "2026-10-19 09:03:40")
dosya("Users/ayse/Downloads/rapor.pdf", b"%PDF-1.7 egitim", "2026-09-30 14:00:00")
dosya("Users/can/Downloads/kurulum.msi", b"msi egitim", "2026-10-19 08:10:00")
dosya("Windows/System32/Tasks/GuncellemeKontrol", "<Task><Exec><Command>C:\\Users\\ayse\\AppData\\Local\\Temp\\guncelle.exe</Command></Exec></Task>", "2026-10-19 09:10:00")
dosya("Windows/System32/Tasks/OneDrive Standalone Update Task", "<Task><Exec><Command>OneDriveStandaloneUpdater.exe</Command></Exec></Task>", "2026-01-15 12:00:00")
```
:::

::: gorev 1 · Açılışta ne başlıyor?
Kullanıcıların **ve** bütün kullanıcıların başlangıç klasörlerindeki dosyaları listele; `desktop.ini` gelmesin. Sütunlar: `Yol` (köke göre göreli), `Mtime`; `Yol`'a göre sıralı.

Başlangıç sorgusu yalnız kullanıcıların klasörlerine bakıyor.

```starter
SELECT relpath(path=OSPath, base=Kok) AS Yol, Mtime
FROM glob(globs="Users/*/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/*", root=Kok)
ORDER BY Yol
```

```test
eq(sutunlar, ["Yol", "Mtime"], "sütunlar")
eq(sonuc, [("ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/yedek.bat", "2026-10-19T09:10:05Z"),
           ("Users/ayse/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/guncelle.lnk", "2026-10-19T09:03:50Z"),
           ("Users/can/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/OneNote.lnk", "2025-03-01T10:00:00Z")],
   "iki kullanıcı klasörü ve bütün kullanıcılar klasörü; desktop.ini yok")
EK = ('import os\n'
      'os.makedirs("disk/Users/mert/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup", exist_ok=True)\n'
      'open("disk/Users/mert/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/Desktop.ini", "w").write("x")\n'
      'open("disk/Users/mert/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/not.txt.lnk", "w").write("x")\n'
      'os.makedirs("disk/Users/mert/Downloads/Startup", exist_ok=True)\n'
      'open("disk/Users/mert/Downloads/Startup/kurulum.exe", "w").write("x")\n')
eq([r[0] for r in dene(EK) if "/mert/" in r[0]], ["Users/mert/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/not.txt.lnk"],
   "yeni kullanıcının başlangıç dosyası gelir; büyük harfli Desktop.ini gelmez; adı Startup olan başka bir klasör gelmez")
```

```solution
SELECT relpath(path=OSPath, base=Kok) AS Yol, Mtime
FROM glob(globs=["Users/*/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/*",
                 "ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/*"], root=Kok)
WHERE NOT OSPath.Basename =~ "^desktop[.]ini$"
ORDER BY Yol
```

```hint
`globs` bir liste alır: `globs=["Users/*/AppData/.../Startup/*", "ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/*"]`. `**/Startup/*` yazma: adı Startup olan her klasörü bulur.
```

```hint
Dosya adını ayıklamak için `WHERE NOT OSPath.Basename =~ "^desktop[.]ini$"`. `=~` düzenli ifade eşleşmesidir ve VQL'de **varsayılan olarak büyük-küçük harfe duyarsızdır** (bu derste ölçüldü): `Desktop.ini`'yi de ayıklar. Duyarlı eşleşme gerekirse desenin başına `(?-i)` yazılır.
```

```meta
motor: velociraptor
```

```setup
import calendar
import os
import time


def dosya(yol, icerik, zaman):
    yol = os.path.join("disk", *yol.split("/"))
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "wb") as f:
        f.write(icerik if isinstance(icerik, bytes) else icerik.encode("utf-8"))
    t = calendar.timegm(time.strptime(zaman, "%Y-%m-%d %H:%M:%S"))
    os.utime(yol, (t, t))


BASLAT = "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
dosya(f"Users/ayse/{BASLAT}/guncelle.lnk", "lnk: C:\\Users\\ayse\\AppData\\Local\\Temp\\guncelle.exe", "2026-10-19 09:03:50")
dosya(f"Users/ayse/{BASLAT}/desktop.ini", "[.ShellClassInfo]\n", "2025-06-01 08:00:00")
dosya(f"Users/can/{BASLAT}/OneNote.lnk", "lnk: C:\\Program Files\\Microsoft Office\\ONENOTE.EXE", "2025-03-01 10:00:00")
dosya("ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/yedek.bat", "@echo off\r\ncopy *.docx \\\\srv-yedek\\pay\r\n", "2026-10-19 09:10:05")
dosya("Users/ayse/Downloads/fatura.zip", b"PK\x03\x04egitim", "2026-10-19 09:02:30")
dosya("Users/ayse/Downloads/fatura.exe", b"MZ egitim verisi", "2026-10-19 09:03:40")
dosya("Users/ayse/Downloads/rapor.pdf", b"%PDF-1.7 egitim", "2026-09-30 14:00:00")
dosya("Users/can/Downloads/kurulum.msi", b"msi egitim", "2026-10-19 08:10:00")
dosya("Windows/System32/Tasks/GuncellemeKontrol", "<Task><Exec><Command>C:\\Users\\ayse\\AppData\\Local\\Temp\\guncelle.exe</Command></Exec></Task>", "2026-10-19 09:10:00")
dosya("Windows/System32/Tasks/OneDrive Standalone Update Task", "<Task><Exec><Command>OneDriveStandaloneUpdater.exe</Command></Exec></Task>", "2026-01-15 12:00:00")
```
:::

::: gorev 2 · Olay penceresindeki dosyalar ve özetleri
Olay penceresi 2026-10-19 **09:00:00 (dahil) ile 09:30:00 (hariç)** UTC. Bu pencerede değişen dosyaları üç yerde ara: kullanıcıların `Downloads` klasörleri, başlangıç klasörleri ve `Windows/System32/Tasks`. Sütunlar: `Ad` (dosya adı), `Mtime`, `SHA256`; `Mtime`'a göre sıralı. Bu liste, öteki cihazlarda aranacak IOC'lerin ilk hâlidir.

```starter
SELECT OSPath.Basename AS Ad, Mtime
FROM glob(globs="Users/*/Downloads/*", root=Kok)
ORDER BY Mtime
```

```test
eq(sutunlar, ["Ad", "Mtime", "SHA256"], "sütunlar")
eq([(r[0], r[1]) for r in sonuc], [("fatura.zip", "2026-10-19T09:02:30Z"), ("fatura.exe", "2026-10-19T09:03:40Z"),
                                   ("guncelle.lnk", "2026-10-19T09:03:50Z"), ("GuncellemeKontrol", "2026-10-19T09:10:00Z"),
                                   ("yedek.bat", "2026-10-19T09:10:05Z")],
   "pencerede beş dosya; can'ın 08:10'daki kurulumu ve eski dosyalar değil")
import hashlib
eq(sonuc[1][2], hashlib.sha256(b"MZ egitim verisi").hexdigest(), "SHA256 dosyanın içeriğinden")
EK = ('import calendar, os, time\n'
      'for ad, z in [("sinir.txt", "2026-10-19 09:00:00"), ("son.txt", "2026-10-19 09:30:00")]:\n'
      '    os.makedirs("disk/Users/ayse/Downloads", exist_ok=True)\n'
      '    open("disk/Users/ayse/Downloads/" + ad, "w").write(ad)\n'
      '    t = calendar.timegm(time.strptime(z, "%Y-%m-%d %H:%M:%S")); os.utime("disk/Users/ayse/Downloads/" + ad, (t, t))\n')
eq([r[0] for r in dene(EK) if r[0].endswith(".txt")], ["sinir.txt"], "09:00:00 dahil, 09:30:00 hariç")
```

```solution
SELECT OSPath.Basename AS Ad, Mtime, hash(path=OSPath).SHA256 AS SHA256
FROM glob(globs=["Users/*/Downloads/*",
                 "Users/*/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/*",
                 "ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/*",
                 "Windows/System32/Tasks/*"], root=Kok)
WHERE Mtime >= timestamp(string="2026-10-19T09:00:00Z") AND Mtime < timestamp(string="2026-10-19T09:30:00Z")
ORDER BY Mtime
```

```hint
Pencere: `WHERE Mtime >= timestamp(string="2026-10-19T09:00:00Z") AND Mtime < timestamp(string="2026-10-19T09:30:00Z")`. Özet için seçime `hash(path=OSPath).SHA256 AS SHA256` ekle.
```

```meta
motor: velociraptor
```

```setup
import calendar
import os
import time


def dosya(yol, icerik, zaman):
    yol = os.path.join("disk", *yol.split("/"))
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "wb") as f:
        f.write(icerik if isinstance(icerik, bytes) else icerik.encode("utf-8"))
    t = calendar.timegm(time.strptime(zaman, "%Y-%m-%d %H:%M:%S"))
    os.utime(yol, (t, t))


BASLAT = "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
dosya(f"Users/ayse/{BASLAT}/guncelle.lnk", "lnk: C:\\Users\\ayse\\AppData\\Local\\Temp\\guncelle.exe", "2026-10-19 09:03:50")
dosya(f"Users/ayse/{BASLAT}/desktop.ini", "[.ShellClassInfo]\n", "2025-06-01 08:00:00")
dosya(f"Users/can/{BASLAT}/OneNote.lnk", "lnk: C:\\Program Files\\Microsoft Office\\ONENOTE.EXE", "2025-03-01 10:00:00")
dosya("ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp/yedek.bat", "@echo off\r\ncopy *.docx \\\\srv-yedek\\pay\r\n", "2026-10-19 09:10:05")
dosya("Users/ayse/Downloads/fatura.zip", b"PK\x03\x04egitim", "2026-10-19 09:02:30")
dosya("Users/ayse/Downloads/fatura.exe", b"MZ egitim verisi", "2026-10-19 09:03:40")
dosya("Users/ayse/Downloads/rapor.pdf", b"%PDF-1.7 egitim", "2026-09-30 14:00:00")
dosya("Users/can/Downloads/kurulum.msi", b"msi egitim", "2026-10-19 08:10:00")
dosya("Windows/System32/Tasks/GuncellemeKontrol", "<Task><Exec><Command>C:\\Users\\ayse\\AppData\\Local\\Temp\\guncelle.exe</Command></Exec></Task>", "2026-10-19 09:10:00")
dosya("Windows/System32/Tasks/OneDrive Standalone Update Task", "<Task><Exec><Command>OneDriveStandaloneUpdater.exe</Command></Exec></Task>", "2026-01-15 12:00:00")
```
:::
