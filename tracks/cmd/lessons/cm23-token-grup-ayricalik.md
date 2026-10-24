---
id: cm23
title: whoami · Token, Grup ve Ayrıcalık
summary: Çalışan sürecin kullanıcı SID'sini, grup SID/özniteliklerini ve ayrıcalık durumlarını gerçek token çıktısından ayır.
timeout: 90
---

::: anlat Hesap adı tek başına yetkiyi anlatmaz
Windows bir işlem için erişim tokenı kullanır. Token kullanıcı SID'si, grup SID'leri ve ayrıcalıkları taşır. `whoami /user`, `/groups` ve `/priv` bunları mevcut sürecin bağlamında gösterir. `whoami /all` toplu görünümdür. Yönetici grubunun listede görünmesi, **etkin** olduğu anlamına gelmez; UAC altında “deny only” özniteliği bulunabilir. Ayrıcalığın token içinde bulunması da “Enabled” olmasıyla aynı şey değildir.

```cmd norun
whoami.exe /user /fo CSV /nh
whoami.exe /groups /fo CSV /nh
whoami.exe /priv /fo CSV /nh
```

CSV'de kullanıcı 2, grup 4, ayrıcalık 3 sütunludur. Açıklama alanı virgül içerebildiğinden CSV'yi `tokens=1,2,3 delims=,` ile genel olarak ayrıştırma. Sütun adları ve durum metinleri Windows diline göre değişebilir; SID ve sistem ayrıcalığı adı daha kararlı tanıklardır. Kaynak: [whoami](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami), [access token](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens).
:::

::: anlat İzin değerlendirmesine hazırlık
Grup çıktısındaki “Enabled group”, “Group used for deny only” ve Mandatory Label aynı anlama gelmez. Dosyanın DACL'sindeki bir grup adıyla token satırını ilişkilendirirken SID ve özniteliği beraber oku. Windows erişim denetimi etkin olmayan grup SID'lerini olumlu izin için kullanmaz; deny ACE, allow ACE ve istenen haklar da sonuca etki eder. Bir privilege'ın “Disabled” olması, dosya DACL'sinden çıkan hakkı tek başına açıklamaz. CM24'te gerçek dosya üzerinde ayrıca okuma deneyi yapacaksın. Kaynak: [AccessCheck](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object).
:::

::: tahmin Üç sorgu, üç farklı soru
```cmd
@echo off
whoami.exe /user /fo CSV /nh >nul 2>nul
if not errorlevel 1 echo kullanici-ok
whoami.exe /groups /fo CSV /nh >nul 2>nul
if not errorlevel 1 echo gruplar-ok
whoami.exe /priv /fo CSV /nh >nul 2>nul
if not errorlevel 1 echo ayricaliklar-ok
exit /b 0
```

???

```text
kullanici-ok
gruplar-ok
ayricaliklar-ok
```

Bu üç salt okunur sorgu mevcut oturumda başarılıdır. Gerçek kullanıcı/grup adları ve privilege listesi kişiye ve tokena bağlıdır; tahmin yalnız komut kodlarını kullanır.
:::

::: gorev Kullanıcı ve grupları CSV'ye ayır
Gerçek tokenı sorgula: `whoami.exe /user /fo CSV /nh` sonucunu `kullanici.csv`, `whoami.exe /groups /fo CSV /nh` sonucunu `gruplar.csv` dosyasına yaz. İki komut başarılıysa stdout yalnız `token-hazir`, çıkış 0; biri başarısızsa stdout boş, stderr `token-hatasi`, çıkış 1. CSV başlığı ekleme; dosyaları her çalıştırmada yenile. Başka hesapları sorgulama.

```starter
@echo off
whoami.exe >"kullanici.csv"
echo token-hazir
```
```test
import csv, io
from pathlib import Path
def read(name):
    return list(csv.reader(io.StringIO(Path(name).read_bytes().decode('utf-8-sig',errors='replace'))))
eq(out,'token-hazir\n','Başarı')
u=read('kullanici.csv'); g=read('gruplar.csv')
eq(len(u),1,'Tek kullanıcı satırı')
eq(len(u[0]),2,'Kullanıcı adı ve SID')
eq(u[0][1].startswith('S-1-'),True,'Gerçek kullanıcı SID')
eq(len(g)>0,True,'Gerçek grup listesi')
eq(all(len(row)==4 and row[2].startswith('S-1-') for row in g),True,'Grup SID ve öznitelik sütunları')
eq(any(row[2]=='S-1-1-0' for row in g),True,'Everyone SID tanığı')
r=calis()
eq((r['kod'],r['cikti'],r['hata']),(0,'token-hazir\n',''),'Yeniden sorgu')
eq(len(read('kullanici.csv')),1,'Rapor eklenmez')
```
```solution
@echo off
setlocal DisableDelayedExpansion
(whoami.exe /user /fo CSV /nh >"kullanici.csv") 2>nul || goto hata
(whoami.exe /groups /fo CSV /nh >"gruplar.csv") 2>nul || goto hata
echo token-hazir
exit /b 0
:hata
>&2 echo token-hatasi
exit /b 1
```
```hint
/user ve /groups ayrı çağrıdır. /fo CSV /nh ile başlıksız dosya üret, ikinci komutun başarısını da denetle.
```
:::

::: gorev Ayrıcalığı tam adla seç
Gerçek `whoami.exe /priv /fo CSV /nh` çıktısını `ayricaliklar.csv` dosyasına yaz. İlk argüman aranacak privilege adı; boş/yoksa `SeChangeNotifyPrivilege`. Privilege adını ilk CSV alanında tam ve büyük/küçük harf duyarsız karşılaştır. Bulursan o satırı `secim.csv` dosyasına yazıp stdout `bulundu`, çıkış 0 üret; yoksa `secim.csv` boş, stdout `yok`, çıkış 0. Native sorgu başarısızsa stdout boş, stderr `token-hatasi`, çıkış 1. Her seferinde eski `secim.csv` içeriğini temizle. İlk alan privilege adlarında virgül/çift tırnak yoktur; sonraki CSV alanlarını virgüle göre parçalayarak yorumlama.

```starter
@echo off
whoami.exe /priv /fo TABLE >"ayricaliklar.csv"
echo bulundu
```
```test
import csv, io
from pathlib import Path
def rows(path):
    return list(csv.reader(io.StringIO(Path(path).read_bytes().decode('utf-8-sig',errors='replace'))))
eq(out,'bulundu\n','Varsayılan privilege')
allrows=rows('ayricaliklar.csv')
eq(len(allrows)>0,True,'Gerçek privilege listesi')
eq(all(len(r)==3 and r[0].startswith('Se') and r[0].endswith('Privilege') for r in allrows),True,'Başlıksız CSV')
eq(rows('secim.csv')[0][0],'SeChangeNotifyPrivilege','Varsayılan tam ad')
first=allrows[0][0]
for name in (first,first.lower(),'SeChangeNotifyPrivilege'):
    r=calis(argv=[name])
    eq((r['kod'],r['cikti'],r['hata']),(0,'bulundu\n',''),'Mevcut tam ad')
    selected=rows('secim.csv')
    eq(len(selected),1,'Tek kayıt')
    eq(selected[0][0].lower(),name.lower(),'Tam ad seçildi')
    eq(len(selected[0]),3,'Açıklama ve durum korundu')
for name in ('SeChangeNotifyPrivilegeX','ChangeNotifyPrivilege','PaftaYokPrivilege'):
    r=calis(argv=[name])
    eq((r['kod'],r['cikti'],r['hata']),(0,'yok\n',''),'Yakın veya eksik ad')
    eq(Path('secim.csv').read_bytes(),b'','Eski seçim kalmadı')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "hedef=%~1"
if not defined hedef set "hedef=SeChangeNotifyPrivilege"
(whoami.exe /priv /fo CSV /nh >"ayricaliklar.csv") 2>nul || goto hata
>"secim.csv" type nul
for /f "usebackq tokens=1,* delims=," %%A in ("ayricaliklar.csv") do if /i "%%~A"=="%hedef%" (
    >>"secim.csv" echo(%%A,%%B
)
for %%F in ("secim.csv") do if %%~zF GTR 0 goto bulundu
echo yok
exit /b 0
:bulundu
echo bulundu
exit /b 0
:hata
>&2 echo token-hatasi
exit /b 1
```
```hint
İlk virgüle kadar olan tırnaklı privilege adını %%~A ile karşılaştır; `tokens=1,*` kalan CSV metnini tek parça taşır. Seçim dosyasını önce boşalt.
```
:::
