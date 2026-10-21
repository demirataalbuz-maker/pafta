---
id: cm16
title: Dosya Akışı · Listele, Kopyala, Adlandır
summary: Sentetik klasörlerde dosyaları bir kez listelemek, varlık kontrolü yapmak ve kopyayı güvenle hazırlamak.
---

::: anlat Klasör gezmek ve dosya seçmek
`for /d` jokerle eşleşen klasörleri, `for /r "lab"` ise belirtilen kökün altını gezer. Batch dosyasında döngü değişkeni `%%F` biçimindedir. `%%~fF` tam yolu, `%%~nxF` yalnız dosya adını ve uzantısını verir. Yolları tırnakla; boşluk bir dosyayı iki argümana bölmesin. Gecikmeli genişlemeyi kapalı tutmak, dosya adındaki `!` işaretini yakalarken korur.

Birbirini örten `(*.log olay*)` desenleri aynı dosyayı tekrar seçebilir. Bu dersin envanterinde tek `*.log` deseni kullanacağız; aynı adlı iki ayrı dosya ise ayrı tam yollar olarak kalacak. Liste sırasını alfabetik varsayma. `if exist` ile adayın varlığını, `if not exist "YOL\"` ile klasör olmadığını ayrıca denetle. Bunlar bağlar/junction'lar için genel tekilleştirme çözümü değildir; laboratuvarda böyle bağlantılar bulunmaz.

Kaynak: [Microsoft FOR](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for).
:::

::: anlat Kaynağı koru, sonucu doğrula
`copy /b` dosyanın bütün baytlarını taşır; Ctrl+Z içeren veri kesilmez. `/y` üzerine yazma sorusunu kapatır; bu yüzden önce hedefin varlığına karar ver. `ren "rapor\taslak.txt" "hazir.txt"` ikinci parametrede yeni klasör değil, aynı klasörde yeni ad ister. `attrib -R "rapor\hazir.txt"` yalnız o dosyanın salt okunur özniteliğini kaldırır. Öznitelik değişikliği içeriği temizlemez veya dosyayı güvenilir yapmaz.

Öznitelik işlemini gerçekten gözlemek için bu ayrı örnekte önce salt okunur durumunu koyup sonra kaldırıyoruz. `%%~aF` dosyanın öznitelik metnini verir; ilk satırda `r` bulunurken ikinci satırda bulunmaz. COPY ile yeni oluşturulan normal dosyada R zaten kapalı olabildiğinden, sonraki kopyalama görevine etkisiz bir öznitelik kaldırma adımı eklemiyoruz.

```cmd
@echo off
>"ornek.txt" echo sentetik
attrib +R "ornek.txt"
for %%F in ("ornek.txt") do echo(once=%%~aF
attrib -R "ornek.txt"
for %%F in ("ornek.txt") do echo(sonra=%%~aF
exit /b 0
```

Kopyalama ve yeniden adlandırma sonrası dönüş kodunu hemen denetle. Tek bir `komut || goto hata`, o komut başarısızsa hata dalına gider; bu, `A && B || C` zincirini genel if/else saymakla aynı şey değildir. `hazir` yazmak dosyanın hazır olduğunu kanıtlamaz; testte gerçek hedef baytlarını da okuyacağız. Alıştırmalar yalnız koşucunun geçici çalışma klasöründeki `lab` ve `rapor` dizinlerini kullanır; sistem dizinleri veya gerçek kullanıcı dosyaları bu görevin girdisi değildir.

Kaynaklar: [COPY](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/copy), [RENAME](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/rename), [ATTRIB](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/attrib).
:::

::: tahmin
Geçici klasörde yalnız bu kodun oluşturduğu bir alt klasör ve bir log dosyası var. /d ve /r hangi adları yazar?

```cmd
@echo off
setlocal DisableDelayedExpansion
mkdir "lab\alt"
>"lab\alt\olay.log" echo veri
for /d %%D in ("lab\*") do echo(klasor=%%~nxD
for /r "lab" %%F in (*.log) do if exist "%%~fF" if not exist "%%~fF\" echo(dosya=%%~nxF
exit /b 0
```

???

`klasor=alt` ve `dosya=olay.log` yazılır. /d yalnız doğrudan eşleşen klasörü seçer; /r belirtilen kökün altındaki dosyaya ulaşır. Tam geçici yol yazılmadığı için çıktı bu örnekte sabittir.
:::

::: gorev Log envanterini tekilleştir
`lab` altındaki gerçek `*.log` dosyalarının tam yollarını, her dosya için bir satır ve yalnız bir kez yaz. Aynı adın farklı klasörlerdeki kopyalarını birleştirme. Klasörler, `.txt`, `.log.bak` ve `.log` adlı klasörler çıktı olmasın. Eşleşme yoksa çıktı boş olsun; sıra önemli değil. Bağ/junction yoktur. Dosya adları boşluk, Unicode, `&`, `%`, `!`, `^` içerebilir; çift tırnak ve satır sonu içermez. Yalnız `lab` kökünü gez.

```setup
from pathlib import Path
kok=Path('lab')
for ad in ('olay.log','alt/olay.log','alt/iki öğe.log','alt/A&B.log','alt/x!y.log','alt/%PATH%.log','alt/sona^.log','alt/haric.txt','alt/olay.log.bak'):
    p=kok/ad
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('sentetik\n',encoding='utf-8')
(kok/'sahte.log').mkdir()
```

```starter
@echo off
for %%F in ("lab\*.log") do echo(%%~fF
exit /b 0
```

```test
from pathlib import Path
kok=Path('lab').resolve()
def kontrol(cikti):
    yollar=[Path(s) for s in cikti.splitlines()]
    beklenen={p.resolve() for p in kok.rglob('*.log') if p.is_file()}
    eq(set(yollar),beklenen,'yalnız gerçek log dosyaları')
    eq(len(yollar),len(beklenen),'her tam yol bir kez')
kontrol(out)
for p in list(kok.rglob('*')):
    if p.is_file() and p.suffix.lower()=='.log':
        p.unlink()
eq(run(),'','sıfır eşleşme')
(kok/'tek.log').write_text('bir',encoding='utf-8')
kontrol(run())
(kok/'alt'/'ikinci.log').write_text('iki',encoding='utf-8')
kontrol(run())
```

```solution
@echo off
setlocal DisableDelayedExpansion
for /r "lab" %%F in (*.log) do if exist "%%~fF" if not exist "%%~fF\" echo(%%~fF
exit /b 0
```

```hint
Tek desen ve tam yol kullan. Varlık kontrolünü ve klasör elemesini aynı aday üzerinde uygula; çıktı sırasına güvenme.
```
:::

::: gorev Kopyayı hazırlarken mevcut raporu koru
Kaynak `lab\giris.txt`, sonuç `rapor\hazir.txt` olsun. Sonuç zaten varsa onu değiştirmeden `var` yaz ve 0 dön. Sonuç yokken kaynak da yoksa stderr'e `kaynak-yok` yazıp 1 dön. Aksi durumda rapor klasörünü gerekirse oluştur, kaynağı `rapor\taslak.txt` olarak baytları koruyarak kopyala, `hazir.txt` diye yeniden adlandır ve `hazir` yazıp 0 dön. Kopyalama/adlandırma hatasında stderr'e yalnız `islem-hatasi`, çıkış 1 olsun; araçların kendi mesajlarını bastır. Kaynak boş olmayan normal dosyadır. İlk başarılı çalışmada taslak yoktur; sonraki hata örneklerinde eski taslak başka bir işlem tarafından yazmaya veya ad değiştirmeye kapatılmış olabilir. Kaynağı değiştirme; var olan sonucun önceliği kaynak kontrolünden öncedir.

```setup
from pathlib import Path
Path('lab').mkdir()
Path('lab/giris.txt').write_bytes('Başlangıç\n'.encode('utf-8')+b'\x1ason\n')
```

```starter
@echo off
echo hazir
exit /b 0
```

```test
from pathlib import Path
srcp=Path('lab/giris.txt')
hedef=Path('rapor/hazir.txt')
ilk=srcp.read_bytes()
eq(out,'hazir\n','ilk hazırlık')
ok(hedef.is_file(),'sonuç gerçekten var')
eq(hedef.read_bytes(),ilk,'Ctrl+Z dahil aynı baytlar')
eq(srcp.read_bytes(),ilk,'kaynak aynı')
ok(not Path('rapor/taslak.txt').exists(),'taslak adından çıkıldı')
hedef.write_bytes(b'korunacak')
eq(run(),'var\n','var olan hedef')
eq(hedef.read_bytes(),b'korunacak','üzerine yazma yok')
srcp.unlink()
eq(run(),'var\n','hedef varsa kaynak aranmaz')
hedef.unlink()
r=calis()
eq((r['kod'],r['cikti'],r['hata']),(1,'','kaynak-yok\n'),'kaynak yok dalı')
for veri in (b'x',b'iki\x1auc', 'Türkçe & % ! ^\n'.encode('utf-8')):
    srcp.write_bytes(veri)
    eq(run(),'hazir\n','yeniden kaynak var')
    eq(hedef.read_bytes(),veri,'değişken içerik aynen kopyalandı')
    eq(srcp.read_bytes(),veri,'kaynak yine aynı')
    hedef.unlink()
# Yalnız sentetik taslak üzerinde gerçek Windows paylaşım kilitleri.
import ctypes
k32=ctypes.WinDLL('kernel32',use_last_error=True)
ac=k32.CreateFileW
ac.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p]
ac.restype=ctypes.c_void_p
k32.CloseHandle.argtypes=[ctypes.c_void_p]
taslak=Path('rapor/taslak.txt')
for paylasim in (1,3):
    taslak.write_bytes(b'eski-taslak')
    h=ac(str(taslak.resolve()),0x80000000,paylasim,None,3,128,None)
    ok(h!=ctypes.c_void_p(-1).value,'sentetik dosya kilidi açıldı')
    try:
        r=calis()
    finally:
        k32.CloseHandle(h)
    eq((r['kod'],r['cikti'],r['hata']),(1,'','islem-hatasi\n'),'yazma veya ad değiştirme engelli')
    ok(not hedef.exists(),'başarısız işlem hazır sonucu üretmedi')
    eq(taslak.read_bytes(),b'eski-taslak' if paylasim==1 else srcp.read_bytes(),'ilk kilit COPY, ikinci kilit REN adımını durdurdu')
    taslak.unlink()
```

```solution
@echo off
setlocal DisableDelayedExpansion
if exist "rapor\hazir.txt" goto var
if not exist "lab\giris.txt" goto eksik
if not exist "rapor\" mkdir "rapor"
copy /b /y "lab\giris.txt" "rapor\taslak.txt" >nul 2>nul || goto hata
ren "rapor\taslak.txt" "hazir.txt" >nul 2>nul || goto hata
echo hazir
exit /b 0
:var
echo var
exit /b 0
:eksik
>&2 echo kaynak-yok
exit /b 1
:hata
>&2 echo islem-hatasi
exit /b 1
```

```hint
Önce mevcut sonucu, sonra kaynağı denetle. COPY ve REN çıktısını kendi başarı mesajınla karıştırma; başarısızlık kodunu hemen yakala.
```
:::
