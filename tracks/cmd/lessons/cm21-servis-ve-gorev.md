---
id: cm21
title: sc ve schtasks · Başlatan Yapılandırmayı Oku
summary: Servis adını görünen adından ayır; servis yapılandırmasını ve zamanlanmış görevleri gerçek Windows araçlarıyla sorgula.
timeout: 90
---

::: anlat Çalışan sürecin arkasındaki servis
CM17'de süreç listesini okudun. `sc.exe qc EventLog` hizmetin **yapılandırmasını** (başlangıç türü, çalıştırılan yol, hesap) gösterir; `sc.exe query EventLog` ise o anki **durumunu** gösterir. `EventLog` hizmet adıdır, görünen ad yerelleştirilebilir. `sc.exe` yaz: PowerShell'deki `sc` takma adıyla karışmaz. Bir hizmetin çalışıyor olması başlangıç türünün otomatik olduğunu kanıtlamaz; iki sorgu farklı sorulara yanıt verir.

```cmd norun
sc.exe qc EventLog
sc.exe query EventLog
```

Servis listesi ve gerçek durum makineye göre değişir. Buradaki görevler hizmet kurmaz, başlatmaz veya durdurmaz; yalnızca okur. Kaynak: [sc query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query), [sc qc](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-qc).
:::

::: anlat Zamanlanmış görevi bul
`schtasks.exe /query /fo CSV /nh` görevleri CSV olarak listeler. `/tn "\Klasor\Gorev"` tek bir görev yolunu seçer; joker kabul etmez. `/v` ayrıntı sütunları ekler. CSV alanlarını virgülden körlemesine bölme: tırnaklı alan virgül içerebilir. Görev adı, son çalışma ve durum canlı sistemde farklı olabilir. Listeyi bir dosyaya yönlendirip gerçek CSV ayrıştırıcısıyla aç.

```cmd norun
schtasks.exe /query /fo CSV /nh >"gorevler.csv"
schtasks.exe /query /tn "\Microsoft\Windows\Defrag\ScheduledDefrag" /fo LIST /v
```

Kaynak: [schtasks query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query).
:::

::: tahmin Olmayan hizmeti başarı sayma
```cmd
@echo off
sc.exe qc "PaftaKesinlikleOlmayanServis_2026" >nul 2>nul
if errorlevel 1 echo servis-yok
echo rapor-devam
exit /b 0
```

???

```text
servis-yok
rapor-devam
```

Olmayan servis sorgusu sıfırdan farklı kod döndürür. `if errorlevel 1` tam 1 eşitliği değil, en az 1 koşuludur. Hata metni Windows diline bağlıdır; burada kodu yorumluyoruz.
:::

::: gorev Servis yapılandırmasını kaydet
İlk argüman hizmet adı; yok/boşsa `EventLog`. `sc.exe qc` ile yapılandırmayı `servis.txt` dosyasına yaz. Komut başarılıysa yalnız `servis-hazir` yaz ve 0 ile çık. Olmayan veya erişilemeyen hizmette stdout boş, stderr yalnız `servis-hatasi`, çıkış 1 olsun. Araç hata metnini gösterme. Hizmete dokunma.

```starter
@echo off
sc.exe query EventLog >"servis.txt"
echo servis-hazir
```
```test
from pathlib import Path
import subprocess
import os
def check(ad):
    native=subprocess.run([os.path.join(os.environ['SystemRoot'],'System32','sc.exe'),'qc',ad],capture_output=True)
    r=calis(argv=[ad])
    eq((r['kod'],r['cikti'],r['hata']),(0,'servis-hazir\n',''),'Başarılı sorgu')
    got=Path('servis.txt').read_bytes()
    for marker in (b'SERVICE_NAME: '+ad.encode(),b'START_TYPE',b'BINARY_PATH_NAME'):
        eq(marker in got,True,'Gerçek QC alanı')
    eq(b'QueryServiceConfig' in got,True,'Durum sorgusu değil QC')
    eq(native.returncode,0,'Bağımsız native tanık')
eq(out,'servis-hazir\n','Varsayılan hizmet')
check('EventLog')
check('RpcSs')
check('EventLog')
old=Path('servis.txt').read_bytes()
r=calis(argv=['PaftaKesinlikleOlmayanServis_2026'])
eq((r['kod'],r['cikti'],r['hata']),(1,'','servis-hatasi\n'),'Eksik hizmet')
r=calis(argv=['EventLog'])
eq((r['kod'],r['cikti'],r['hata']),(0,'servis-hazir\n',''),'Hata sonrası toparlanma')
eq(Path('servis.txt').read_bytes()!=old,False,'Aynı hizmetin yapılandırması')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "ad=%~1"
if not defined ad set "ad=EventLog"
(sc.exe qc "%ad%" >"servis.txt") 2>nul || goto hata
echo servis-hazir
exit /b 0
:hata
>&2 echo servis-hatasi
exit /b 1
```
```hint
QC yapılandırma, QUERY anlık durum içindir. Yönlendirme dahil çağrının başarı kodunu denetle.
```
:::

::: gorev Görev listesini ve tek görevi sorgula
Argüman verilmezse bütün zamanlanmış görevleri `gorevler.csv` dosyasına CSV biçiminde, başlıksız yaz. İlk argüman verilirse `/tn` ile yalnız o **tam görev yolunu** sorgula. Başarıda stdout yalnız `gorevler-hazir`, çıkış 0. Görev bulunamaz veya sorgu başarısızsa stdout boş, stderr `gorev-hatasi`, çıkış 1. Araç hata metnini gösterme. Dosyada her gerçek kayıt CSV olarak ayrıştırılabilmeli; görev yaratma, değiştirme ve silme yok.

```starter
@echo off
schtasks.exe /query /fo TABLE >"gorevler.csv"
echo gorevler-hazir
```
```test
from pathlib import Path
import csv, io
def rows():
    return list(csv.reader(io.StringIO(Path('gorevler.csv').read_bytes().decode('utf-8-sig',errors='replace'))))
eq(out,'gorevler-hazir\n','Liste başarısı')
allrows=rows()
eq(len(allrows)>0,True,'En az bir yerel görev')
eq(all(len(row)==3 and row[0].startswith('\\') for row in allrows),True,'Başlıksız CSV ve tam görev yolları')
name=allrows[0][0]
r=calis(argv=[name])
eq((r['kod'],r['cikti'],r['hata']),(0,'gorevler-hazir\n',''),'Tek görev')
selected=rows()
eq(len(selected),1,'Sadece tek görev')
eq(selected[0][0],name,'İstenen yol')
r=calis(argv=['\\PaftaKesinlikleOlmayanGorev_2026'])
eq((r['kod'],r['cikti'],r['hata']),(1,'','gorev-hatasi\n'),'Eksik görev')
r=calis()
eq((r['kod'],r['cikti'],r['hata']),(0,'gorevler-hazir\n',''),'Hata sonrası liste')
eq(len(rows())>=len(selected),True,'Tek görevin listede olması')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "ad=%~1"
if defined ad goto tek
(schtasks.exe /query /fo CSV /nh >"gorevler.csv") 2>nul || goto hata
goto tamam
:tek
(schtasks.exe /query /tn "%ad%" /fo CSV /nh >"gorevler.csv") 2>nul || goto hata
:tamam
echo gorevler-hazir
exit /b 0
:hata
>&2 echo gorev-hatasi
exit /b 1
```
```hint
Başlıksız CSV için /fo CSV /nh. Tek görev seçerken /tn ile yolu tırnak içinde ver; hata kodu başarı mesajından önce sınanmalı.
```
:::
