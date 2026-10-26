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

CSV'de kullanıcı 2, grup 4, ayrıcalık 3 sütunludur. Grup satırının son alanı birden çok özniteliği **virgülle** sayar (`"Mandatory group, Enabled by default, Enabled group"`), bu yüzden CSV'yi `tokens=1,2,3 delims=,` ile genel olarak ayrıştırma. Sütun adları ve durum metinleri Windows diline göre değişebilir; SID ve sistem ayrıcalığı adı daha kararlı tanıklardır. Kaynak: [whoami](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami), [access token](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens).

> [!TUZAK] Hangi whoami.exe?
> Git Bash'ten açılmış bir `cmd` penceresinde `PATH`'in başında Git'in Unix araçları durur. Bu derste ölçüldü: orada `where whoami` önce `C:\Program Files\Git\usr\bin\whoami.exe`'yi gösterir ve `whoami.exe /groups` "extra operand '/groups'" hatası verir. Windows aracını kesin çağırmak için tam yolu yaz: `"%SystemRoot%\System32\whoami.exe"`.
:::

::: anlat İzin değerlendirmesine hazırlık
Grup çıktısındaki “Enabled group”, “Group used for deny only” ve Mandatory Label aynı anlama gelmez. Dosyanın DACL'sindeki bir grup adıyla token satırını ilişkilendirirken SID ve özniteliği beraber oku. Windows erişim denetimi etkin olmayan grup SID'lerini olumlu izin için kullanmaz; deny ACE, allow ACE ve istenen haklar da sonuca etki eder. Bir privilege'ın “Disabled” olması, dosya DACL'sinden çıkan hakkı tek başına açıklamaz. CM24'te gerçek dosya üzerinde ayrıca okuma deneyi yapacaksın. Kaynak: [AccessCheck](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object).
:::

::: tahmin Virgülle bölünen öznitelikler
Bu makinedeki (İngilizce Windows) `Everyone` satırı: `"Everyone","Well-known group","S-1-1-0","Mandatory group, Enabled by default, Enabled group"`. Ne yazar?

```cmd
@echo off
for /f "tokens=1-4 delims=," %%A in ('%SystemRoot%\System32\whoami.exe /groups /fo CSV /nh ^| findstr /l /c:"S-1-1-0"') do echo [%%~C] [%%~D]
```

???

```text
[S-1-1-0] [Mandatory group]
```

`delims=,` tırnakları tanımaz: dördüncü alanın içindeki ilk virgülde keser. `%%D` `"Mandatory group` olur, `~` baştaki tırnağı da siler. Grubun **etkin** olduğunu söyleyen `Enabled group` hiç okunmadı. Öznitelikleri alan alan ayrıştırmaya çalışma: SID'i tırnaklı tam alan olarak bul, satırın tamamında özniteliği ara.
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
eq(len(read('gruplar.csv')),len(g),'Grup dosyası da yenilenir, eklenmez')

# SystemRoot yalnız bu test alt sürecinde değiştirilir; whoami mutlak yolu bulunamaz.
import os,tempfile
saved_root=os.environ.get('SystemRoot')
try:
    with tempfile.TemporaryDirectory(prefix='pafta_no_whoami_') as root:
        os.environ['SystemRoot']=root
        r=calis()
        eq((r['kod'],r['cikti'],r['hata'].strip()),(1,'','token-hatasi'),'whoami hatası başarı çıktısına dönüşmez')
finally:
    if saved_root is None:os.environ.pop('SystemRoot',None)
    else:os.environ['SystemRoot']=saved_root


job=calis.__self__.job
original_code=job['code']
try:
    job['code']=src.replace('"%whoami%" /groups /fo CSV /nh','"%SystemRoot%\\System32\\cmd.exe" /d /c "echo forced-error 1>&2 & exit /b 7"',1)
    r=calis()
    eq((r['kod'],r['cikti'],r['hata'].strip()),(1,'','token-hatasi'),'ikinci whoami hata yolu ve stderr temizliği')
finally:
    job['code']=original_code

```
```solution
@echo off
setlocal DisableDelayedExpansion
set "whoami=%SystemRoot%\System32\whoami.exe"
("%whoami%" /user /fo CSV /nh >"kullanici.csv") 2>nul || goto hata
("%whoami%" /groups /fo CSV /nh >"gruplar.csv") 2>nul || goto hata
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
for name in ('SeChangeNotifyPrivilegeX','ChangeNotifyPrivilege','PaftaYokPrivilege','%PATH%','Se!Change','Se Change','a&echo SeChangeNotifyPrivilege'):
    r=calis(argv=[name])
    eq((r['kod'],r['cikti'],r['hata']),(0,'yok\n',''),'Yakın veya eksik ad')
    eq(Path('secim.csv').read_bytes(),b'','Eski seçim kalmadı')

# SystemRoot yalnız bu test alt sürecinde değiştirilir; whoami mutlak yolu bulunamaz.
import os,tempfile
saved_root=os.environ.get('SystemRoot')
try:
    with tempfile.TemporaryDirectory(prefix='pafta_no_whoami_') as root:
        os.environ['SystemRoot']=root
        r=calis()
        eq((r['kod'],r['cikti'],r['hata'].strip()),(1,'','token-hatasi'),'whoami hatası başarı çıktısına dönüşmez')
finally:
    if saved_root is None:os.environ.pop('SystemRoot',None)
    else:os.environ['SystemRoot']=saved_root

```
```solution
@echo off
setlocal DisableDelayedExpansion
set "hedef=%~1"
if not defined hedef set "hedef=SeChangeNotifyPrivilege"
("%SystemRoot%\System32\whoami.exe" /priv /fo CSV /nh >"ayricaliklar.csv") 2>nul || goto hata
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

::: gorev Yönetici grubu etkin mi, bütünlük seviyesi ne?
Bir grup CSV'sine bakıp iki soruyu yanıtla. İlk argüman bir grup CSV dosyasıdır (`whoami /groups /fo CSV /nh` biçiminde). Argüman yoksa gerçek tokenı `gruplar.csv`'ye yaz ve onu kullan.

Birinci satır, SID'i **tam olarak** `S-1-5-32-544` (BUILTIN\Administrators) olan grup satırına göre:

- `yonetici-reddet`: öznitelikte `Group used for deny only` var (UAC'nin süzdüğü, yükseltilmemiş token)
- `yonetici-etkin`: öznitelikte `Enabled group` var
- `yonetici-diger`: satır var ama ikisi de yok
- `yonetici-yok`: böyle bir satır yok

Bir satırda ikisi birden geçerse `yonetici-reddet` kazanır: deny-only işaretli bir SID olumlu izin için kullanılmaz.

İkinci satır, `S-1-16-` ile başlayan zorunlu etiket SID'ine göre `butunluk=<seviye>`: `S-1-16-4096` `Low`, `S-1-16-8192` `Medium`, `S-1-16-12288` `High`, `S-1-16-16384` `System`. Bu tablodaki dört değerden biri değilse `butunluk=bilinmiyor`, hiç etiket satırı yoksa `butunluk=yok`.

Dosya yoksa stdout boş, stderr `dosya-yok`, çıkış 1; gerçek sorgu başarısızsa stderr `token-hatasi`, çıkış 1. Öznitelik alanı virgül içerdiği için `delims=,` ile alan alan ayırma: SID'i tırnaklı tam alan olarak (`,"S-1-5-32-544",`) ara. Adında ya da SID'inde `544` geçen başka satırlar seni yanıltmasın.

```starter
@echo off
findstr /c:"S-1-5-32-544" "%~1" >nul && echo yonetici-etkin
echo butunluk=Medium
```
```test
import csv, io
from pathlib import Path

def satirlar(ad):
    return list(csv.reader(io.StringIO(Path(ad).read_bytes().decode('utf-8-sig', errors='replace'))))

def beklenen(ad):
    rows = satirlar(ad)
    yon = 'yonetici-yok'
    for r in rows:
        if len(r) == 4 and r[2] == 'S-1-5-32-544':
            yon = ('yonetici-reddet' if 'Group used for deny only' in r[3] else
                   'yonetici-etkin' if 'Enabled group' in r[3] else 'yonetici-diger')
    seviye = 'yok'
    for r in rows:
        if len(r) == 4 and r[2].startswith('S-1-16-'):
            seviye = {'S-1-16-4096': 'Low', 'S-1-16-8192': 'Medium', 'S-1-16-12288': 'High',
                      'S-1-16-16384': 'System'}.get(r[2], 'bilinmiyor')
    return f'{yon}\nbutunluk={seviye}\n'

eq(out, beklenen('gruplar.csv'), 'gerçek token: bu oturumun yönetici durumu ve bütünlük seviyesi')
ETIKET = '"Mandatory Label\\{0} Mandatory Level","Label","S-1-16-{1}",""\n'
EVERYONE = '"Everyone","Well-known group","S-1-1-0","Mandatory group, Enabled by default, Enabled group"\n'
def yaz(ad, metin):
    Path(ad).write_text(metin, encoding='utf-8')
    return ad
yaz('suzulmus.csv', ETIKET.format('Medium', 8192) + EVERYONE +
    '"BUILTIN\\Administrators","Alias","S-1-5-32-544","Group used for deny only"\n')
yaz('yukseltilmis.csv', ETIKET.format('High', 12288) + EVERYONE +
    '"BUILTIN\\Administrators","Alias","S-1-5-32-544","Mandatory group, Enabled by default, Enabled group, Group owner"\n')
yaz('standart.csv', EVERYONE + ETIKET.format('Low', 4096) + '"BUILTIN\\Users","Alias","S-1-5-32-545","Mandatory group, Enabled by default, Enabled group"\n')
yaz('tuzak.csv', ETIKET.format('Medium', 8192) +
    '"S-1-5-32-544","Alias","S-1-5-21-1-1001","Mandatory group, Enabled by default, Enabled group"\n'
    '"Kopya Yoneticiler","Alias","S-1-5-32-5440","Mandatory group, Enabled by default, Enabled group"\n'
    '"BUILTIN\\Administrators","Alias","S-1-5-32-544","Group used for deny only"\n')
yaz('etiketsiz.csv', EVERYONE + '"BUILTIN\\Administrators","Alias","S-1-5-32-544","Mandatory group"\n')
yaz('guvenilmez.csv', ETIKET.format('Untrusted', 0) + EVERYONE)
yaz('sahte.csv', ETIKET.format('Medium', 8192) +
    '"S-1-5-32-544","Alias","S-1-5-21-1-1001","Mandatory group, Enabled by default, Enabled group"\n'
    '"Kopya Yoneticiler","Alias","S-1-5-32-5440","Mandatory group, Enabled by default, Enabled group"\n')
yaz('sistem.csv', ETIKET.format('System', 16384) + EVERYONE +
    '"BUILTIN\\Administrators","Alias","S-1-5-32-544","Mandatory group, Enabled by default, Enabled group"\n')
yaz('ikisi.csv', ETIKET.format('Medium', 8192) + EVERYONE +
    '"BUILTIN\\Administrators","Alias","S-1-5-32-544","Mandatory group, Enabled group, Group used for deny only"\n')
for ad, cevap, neden in (
        ('suzulmus.csv', 'yonetici-reddet\nbutunluk=Medium\n', 'UAC süzgeci: grup var ama yalnız reddetmek için'),
        ('yukseltilmis.csv', 'yonetici-etkin\nbutunluk=High\n', 'yükseltilmiş token'),
        ('standart.csv', 'yonetici-yok\nbutunluk=Low\n', 'yönetici grubu hiç yok; etiket satırı ortada'),
        ('tuzak.csv', 'yonetici-reddet\nbutunluk=Medium\n', 'adı S-1-5-32-544 olan grup ve S-1-5-32-5440 yanıltmamalı'),
        ('etiketsiz.csv', 'yonetici-diger\nbutunluk=yok\n', 'ne etkin ne reddet; etiket yok'),
        ('guvenilmez.csv', 'yonetici-yok\nbutunluk=bilinmiyor\n', 'tablodaki dört seviyenin dışındaki etiket'),
        ('sahte.csv', 'yonetici-yok\nbutunluk=Medium\n', 'gerçek yönetici satırı yok: yalnız adında ya da önekinde 544 geçenler'),
        ('sistem.csv', 'yonetici-etkin\nbutunluk=System\n', 'dördüncü seviye: S-1-16-16384 System'),
        ('ikisi.csv', 'yonetici-reddet\nbutunluk=Medium\n', 'aynı satırda Enabled group ve deny only: reddet kazanır')):
    r = calis(argv=[ad])
    eq((r['kod'], r['cikti'], r['hata']), (0, cevap, ''), neden)
yaz('bos.csv', '')
eq(calis(argv=['bos.csv'])['cikti'], 'yonetici-yok\nbutunluk=yok\n', 'boş dosya')
r = calis(argv=['yok.csv'])
eq((r['kod'], r['cikti'], r['hata'].strip()), (1, '', 'dosya-yok'), 'olmayan dosya')

# SystemRoot yalnız bu test alt sürecinde değiştirilir; whoami mutlak yolu bulunamaz.
import os,tempfile
saved_root=os.environ.get('SystemRoot')
try:
    with tempfile.TemporaryDirectory(prefix='pafta_no_whoami_') as root:
        os.environ['SystemRoot']=root
        r=calis()
        eq((r['kod'],r['cikti'],r['hata'].strip()),(1,'','token-hatasi'),'whoami hatası başarı çıktısına dönüşmez')
finally:
    if saved_root is None:os.environ.pop('SystemRoot',None)
    else:os.environ['SystemRoot']=saved_root

```
```solution
@echo off
setlocal DisableDelayedExpansion
set "dosya=%~1"
if defined dosya goto oku
set "dosya=gruplar.csv"
("%SystemRoot%\System32\whoami.exe" /groups /fo CSV /nh >"%dosya%") 2>nul || goto hata
:oku
if not exist "%dosya%" goto yok
set "yonetici=yonetici-yok"
findstr /l /c:",\"S-1-5-32-544\"," "%dosya%" >nul && set "yonetici=yonetici-diger"
findstr /l /c:",\"S-1-5-32-544\"," "%dosya%" | findstr /l /c:"Enabled group" >nul && set "yonetici=yonetici-etkin"
findstr /l /c:",\"S-1-5-32-544\"," "%dosya%" | findstr /l /c:"Group used for deny only" >nul && set "yonetici=yonetici-reddet"
set "seviye=yok"
findstr /r /c:",\"S-1-16-[0-9]*\"," "%dosya%" >nul && set "seviye=bilinmiyor"
findstr /l /c:",\"S-1-16-4096\"," "%dosya%" >nul && set "seviye=Low"
findstr /l /c:",\"S-1-16-8192\"," "%dosya%" >nul && set "seviye=Medium"
findstr /l /c:",\"S-1-16-12288\"," "%dosya%" >nul && set "seviye=High"
findstr /l /c:",\"S-1-16-16384\"," "%dosya%" >nul && set "seviye=System"
echo %yonetici%
echo butunluk=%seviye%
exit /b 0
:yok
>&2 echo dosya-yok
exit /b 1
:hata
>&2 echo token-hatasi
exit /b 1
```
```hint
`findstr /l /c:",\"S-1-5-32-544\","` SID'i yalnız üçüncü alanda, tam değer olarak bulur: önündeki `,"` ve ardındaki `",` başka bir SID'in önekini ya da ad alanını dışarıda bırakır. İkinci `findstr`'i ilkinin çıktısına bağla: `... | findstr /l /c:"Group used for deny only"`.
```
```hint
Önce varsayılanı ata, sonra koşulları artan önemle sırala: satır varsa `diger`, `Enabled group` varsa `etkin`, `deny only` varsa `reddet`. Son eşleşen kazanır. Bir `/c:"..."` deseninde çift tırnak sayısı tek kalırsa `cmd` satırın geri kalanını (`>nul && set ...`) de `findstr`'e argüman sanır; `\"` `cmd` için kaçış değildir.
```
:::
