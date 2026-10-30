---
id: cm24
title: icacls · Token ile DACL'yi Birlikte Oku
summary: Geçici dosyanın DACL'sini salt okunur sorgula, token tanıklarıyla ilişkilendir ve gerçek okuma sonucunu ayrıca ölç.
timeout: 90
---

::: anlat DACL satırı tek başına erişim kararı değildir
`icacls.exe "delil dosyasi.txt"` dosyanın DACL satırlarını gösterir. Parantezdeki `(R)` okuma, `(M)` değiştirme, `(F)` tam denetim gibi hakları; `(I)` devralınmış ACE'yi, `(DENY)` ret ACE'sini işaretleyebilir. Bir ACE'deki adın tokenla bağlantısını SID ve etkin grup durumu üzerinden araştır. Yetki değerlendirmesi ACE sırası, istenen hak ve etkin SID'leri dikkate alır; yalnız metinde kullanıcı adını aramak kesin karar vermez.

```cmd norun
icacls.exe "delil dosyasi.txt"
whoami.exe /groups /fo CSV /nh
```

Öğrenci betiği yalnız koşucunun geçici klasöründeki dosyaları **okur**. Denetim düzeneği ayrıca yeni bir geçici dosyada geçerli kullanıcı için yalnız ReadData Deny ekler, gerçek okumayı ölçer, özgün DACL'yi geri yükleyip dosyayı siler. Bu durumda icacls ile DACL okuması başarılıyken type başarısız olabilir; ACL raporu okuma yetkisini kanıtlamaz. Kalıcı sistem dosyası veya üst klasör izni değiştirilmez, yükseltilmiş hak gerekmez. Kaynak: [icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls), [AccessCheck](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object).
:::

::: anlat Birlikte bak, sonra gerçek erişimi ölç
CM23'teki `whoami /user`, `/groups`, `/priv` tokenın bu süreçteki görünümünü verir. `icacls` DACL'yi gösterir. Dosyayı gerçekten `type` ile okumak ayrı bir tanıktır. Okuma başarılıysa bunun hangi tek ACE sayesinde olduğunu sırf satırları gözleyerek kesinleştirme: sahibi, devralma, birden çok grup, deny ve istenen hakların birleşimi olabilir. Ayrıca `SeBackupPrivilege` gibi bir adın listede oluşu, uygulamanın yedekleme semantiğiyle açma isteği yaptığı anlamına gelmez.

Bir hata yolunda `icacls` stdout'una İngilizce veya Türkçe hata metni koyabilir. Öğrenci betiği native sonucu kontrol edip görev sözleşmesindeki sabit hata mesajına çevirecek. Kaynak: [whoami](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami), [icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls).
:::

::: tahmin Dosya var, yanlış yol yok
```setup
from pathlib import Path
Path('delil dosyasi.txt').write_text('KANIT\n',encoding='ascii')
```
```cmd
@echo off
icacls.exe "delil dosyasi.txt" >nul 2>nul
if not errorlevel 1 echo acl-ok
icacls.exe "olmayan delil.txt" >nul 2>nul
if errorlevel 1 echo acl-yok
exit /b 0
```

???

```text
acl-ok
acl-yok
```

Dosyanın DACL'si salt okunur sorgulanır; olmayan yol başarısızdır. Gerçek ACE adları ve miras durumu makineye bağlı olduğu için tahminde sabitlenmez.
:::

::: gorev Dosyanın ACL raporunu al
İlk argüman dosya yolu; boş/yoksa `delil dosyasi.txt`. `icacls.exe` ile DACL görünümünü `acl.txt` dosyasına yaz. Başarıda stdout `acl-hazir`, çıkış 0. Dosya yoksa veya okunamıyorsa stdout boş, stderr `acl-hatasi`, çıkış 1. Native hata metnini gösterme. Dosya verisini ve ACL'yi değiştirme.

```setup
from pathlib import Path
Path('delil dosyasi.txt').write_text('KANIT\n',encoding='ascii')
```
```starter
@echo off
type "delil dosyasi.txt" >"acl.txt"
echo acl-hazir
```
```test
from pathlib import Path
src=Path('delil dosyasi.txt')
before=src.read_bytes()
eq(out,'acl-hazir\n','Varsayılan dosya')
raw=Path('acl.txt').read_bytes()
eq(b'delil dosyasi.txt' in raw,True,'Gerçek dosya adı')
eq(b'Successfully processed 1 files' in raw,True,'Gerçek ICACLS başarı satırı')
eq(b':(' in raw,True,'ACE/hak gösterimi')
eq(src.read_bytes(),before,'Dosya aynı')
alt=Path('A&B !.txt'); alt.write_text('ALT\n',encoding='ascii')
r=calis(argv=[str(alt)])
eq((r['kod'],r['cikti'],r['hata']),(0,'acl-hazir\n',''),'Özel karakterli yol')
eq(b'A&B !.txt' in Path('acl.txt').read_bytes(),True,'Doğru dosya')
r=calis(argv=['olmayan delil.txt'])
eq((r['kod'],r['cikti'],r['hata']),(1,'','acl-hatasi\n'),'Eksik yol')
eq(alt.read_text(encoding='ascii'),'ALT\n','Kaynak korunur')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "dosya=%~1"
if not defined dosya set "dosya=delil dosyasi.txt"
(icacls.exe "%dosya%" >"acl.txt") 2>nul || goto hata
echo acl-hazir
exit /b 0
:hata
>&2 echo acl-hatasi
exit /b 1
```
```hint
Dosya yolunu tırnakla. `icacls` argümansız DACL gösterir; önceki raporu `>` ile yenile ve hata kodunu denetle.
```
:::

::: gorev Proje · Token + DACL + gerçek okuma tanığı
İlk argüman dosya yolu; boş/yoksa `delil dosyasi.txt`. Aynı çalıştırmada şu dosyaları yenile: `kullanici.csv` (`whoami /user /fo CSV /nh`), `gruplar.csv` (`whoami /groups /fo CSV /nh`), `ayricaliklar.csv` (`whoami /priv /fo CSV /nh`), `acl.txt` (`icacls` ile istenen dosya), `okuma.txt` (istenen dosyayı `type` ile gerçekten okuyarak). Hepsi başarılıysa stdout `kanit-hazir`, çıkış 0. Komutlardan biri başarısızsa stdout boş, stderr `kanit-hatasi`, çıkış 1. Başarısız çalışmada kısmen yazılmış raporlar geçerli sayılmaz; atomik güncelleme istenmiyor. Kaynağın içeriğini ve ACL'sini değiştirme.

```setup
from pathlib import Path
Path('delil dosyasi.txt').write_text('KANIT\n',encoding='ascii')
```
```starter
@echo off
whoami.exe /user /fo CSV /nh >"kullanici.csv"
type "delil dosyasi.txt" >"okuma.txt"
echo kanit-hazir
```
```test
import csv, io
from pathlib import Path
def rows(name):
    return list(csv.reader(io.StringIO(Path(name).read_bytes().decode('utf-8-sig',errors='replace'))))
def check(path):
    eq(Path('okuma.txt').read_bytes(),path.read_bytes(),'Gerçek okuma ve bayt eşitliği')
    eq(len(rows('kullanici.csv')),1,'Tek kullanıcı')
    eq(rows('kullanici.csv')[0][1].startswith('S-1-'),True,'Kullanıcı SID')
    eq(any(r[2]=='S-1-1-0' for r in rows('gruplar.csv')),True,'Grup SID')
    eq(all(len(r)==4 for r in rows('gruplar.csv')),True,'Grup öznitelikleri')
    eq(all(len(r)==3 for r in rows('ayricaliklar.csv')),True,'Ayrıcalık ve durum')
    acl=Path('acl.txt').read_bytes()
    eq(path.name.encode() in acl,True,'İstenen dosyanın ACLsi')
    eq(b':(' in acl,True,'Gerçek ACE')
source=Path('delil dosyasi.txt'); before=source.read_bytes()
eq(out,'kanit-hazir\n','Varsayılan')
check(source)
eq(source.read_bytes(),before,'Kaynak değişmedi')
alt=Path('A&B !.txt'); alt.write_text('BASKA\n',encoding='ascii')
r=calis(argv=[str(alt)])
eq((r['kod'],r['cikti'],r['hata']),(0,'kanit-hazir\n',''),'Başka geçici dosya')
check(alt)
eq(alt.read_text(encoding='ascii'),'BASKA\n','İkinci kaynak aynı')
r=calis(argv=['olmayan delil.txt'])
eq((r['kod'],r['cikti'],r['hata']),(1,'','kanit-hatasi\n'),'Eksik dosya')
r=calis()
eq((r['kod'],r['cikti'],r['hata']),(0,'kanit-hazir\n',''),'Hata sonrası toparlanma')
check(source)

# ACL görünür kalsın, yalnız dosya baytlarını açma ReadData hakkı reddedilsin.
import os,runpy,sys,subprocess
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,'__file__',None) or '')=='py_harness.py'))
fixtures=runpy.run_path(os.path.join(_s,'cmd_deny_fixtures.py'))
with fixtures['file_fixture']() as lab:
    expected=lab.path.read_bytes()
    lab.deny_read()
    try:lab.path.read_bytes()
    except PermissionError:pass
    else:stop('test dosyası gerçek okuma reddi üretmedi')
    acl=subprocess.run(['icacls.exe',str(lab.path)],capture_output=True)
    eq(acl.returncode,0,'ReadData Deny ACL raporunu engellemez')
    ok(b'(DENY)' in acl.stdout,'gerçek icacls ret ACE tanığı')
    r=calis(argv=[str(lab.path)])
    eq((r['kod'],r['cikti'],r['hata']),(1,'','kanit-hatasi\n'),'type erişim reddi başarı diye raporlanamaz')
    eq(Path('okuma.txt').read_bytes(),b'','reddedilen okumada önceki kaynak raporu kalmaz')
    lab.restore()
    r=calis(argv=[str(lab.path)])
    eq((r['kod'],r['cikti'],r['hata']),(0,'kanit-hazir\n',''),'aynı dosya DACL geri yüklenince okunur')
    eq(Path('okuma.txt').read_bytes(),expected,'gerçek geri yüklenmiş baytlar')
eq(lab.path.exists(),False,'yalnız teste ait geçici dosya silindi')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "dosya=%~1"
if not defined dosya set "dosya=delil dosyasi.txt"
(whoami.exe /user /fo CSV /nh >"kullanici.csv") 2>nul || goto hata
(whoami.exe /groups /fo CSV /nh >"gruplar.csv") 2>nul || goto hata
(whoami.exe /priv /fo CSV /nh >"ayricaliklar.csv") 2>nul || goto hata
(icacls.exe "%dosya%" >"acl.txt") 2>nul || goto hata
(type "%dosya%" >"okuma.txt") 2>nul || goto hata
echo kanit-hazir
exit /b 0
:hata
>&2 echo kanit-hatasi
exit /b 1
```
```hint
Beş çağrının her birini `||` hata dalına bağla. Token ve DACL raporlarının yanına gerçek dosya okumasını da koy; başarıyı yalnız raporun varlığından çıkarma.
```
:::
