---
id: cm18
title: Proje · Parametreden Doğrulanmış Rapora
summary: Seçenekleri ayrıştır, geçersiz girdiyi yazmadan reddet ve sentetik kayıtlardan ölçülebilir bir rapor üret.
---

::: anlat Önce sözleşme, sonra işlem
Küçük bir batch aracında bile seçeneklerin adı, varsayılanı, geçerli aralığı ve hata kodu açık olmalı. Bu projede sayı olarak yalnız `1`, `2`, `3` kabul edeceğiz. Böylece `01`, `1+1` veya `abc` gibi metinleri SET /A'ya verip aritmetik ifade olarak yorumlatmak yerine önce reddederiz. Etiket ise komut değil veridir: gecikmeli genişleme kapalıyken tırnaklı SET ile yakalanır; CALL satırına taşınmaz.

`shift` ile işlenen seçenek ve değeri tüket. Alt yordamın `exit /b` ile dönmesi, ana akışın sonunda da açık bir `exit /b` bulunması gerekir. Başarı için 0, kullanım hatası için 2, dosya hatası için 1 seçmek bu aracın sözleşmesidir; bütün Windows programlarının ortak kod tablosu değildir. Hata açıklaması stderr'e, başarılı işlem sonucu stdout'a gider. `&&`/`||` zinciri yerine kritik adımlardaki kodu hemen ve açıkça denetle.

Kaynaklar: [Microsoft SHIFT](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/shift), [EXIT](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/exit), [IF](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if).
:::

::: anlat Raporun içeriği de bir çıktı sözleşmesidir
Raporu `>` ile bir kez başlatmak ile her çalışmada `>>` kullanmak farklıdır: ikincisi eski sonuçları biriktirir. Önce argümanı ve kaynak varlığını doğrula; kullanım hatası eski raporu bozmasın. Ardından başlığı yaz, seçilen kayıtları ekle, sonunda gerçekten yazılan kayıt sayısını belirt. Dosya okuma sırası, kayıt sınırı ve boş satır kuralı test edilebilir olmalı.

`for /f "usebackq eol=| delims="` tırnaklı dosya yolunu açar, satırın tamamını alır; boş satırları atlar ve `|` ile başlayan satırları yorum sayar. Bu projede kaynakta `|` ile başlayan kayıt yoktur. Noktalı virgülle başlayan kayıt ise korunmalıdır. Bu bir genel CSV/JSON raporlayıcı veya olay delili toplama aracı değildir; yalnız tanımlanan düz metin sözleşmesi uygulanır. Bütün dosyalar koşucunun sentetik geçici klasöründedir.

Kaynaklar: [FOR](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for), [CMD yönlendirme ve genişleme](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), [SETLOCAL](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setlocal).
:::

::: tahmin
Üç aday varken en fazla iki kaydı seçiyoruz. Sınır kontrolü artıştan önce yapılırsa ne yazılır?

```cmd
@echo off
setlocal EnableDelayedExpansion
set "adet=0"
for /l %%N in (1,1,3) do (
    if !adet! lss 2 (
        set /a adet+=1 >nul
        echo(kayit=%%N
    )
)
echo(adet=!adet!
exit /b 0
```

???

Çıktı `kayit=1`, `kayit=2`, `adet=2` satırlarıdır. İkinci yazımdan sonra adet 2 olur; üçüncü aday `2 lss 2` yanlış olduğundan seçilmez. Aynı blokta değişen sayı `!adet!` ile okunur.
:::

::: gorev Parametrik bir küçük araç yaz
Seçenekler `/etiket DEGER` ve `/n SAYI` olsun. Varsayılan etiket `demo`, sayı `1`. Seçenek sırası serbest; adları büyük/küçük harfe duyarsız, tekrarında son değer geçerli. Seçenek konumunda boş argüman yoktur. Bir seçeneğin değeri eksik/boşsa, bilinmeyen seçenek varsa veya son sayı tam `1`, `2`, `3` metinlerinden biri değilse stdout boş, stderr `kullanim`, çıkış 2 olsun. Başarıda `1:ETIKET` ile başlayarak N satır yaz ve 0 dön. Etiket çift tırnak/CR/LF dışında boşluk, Unicode, `&`, `%`, `!`, `^` içerebilir; bunlar veri kalsın. Veriyi CALL ile yeniden yorumlatma.

```starter
@echo off
echo 1:demo
exit /b 0
```

```test
eq(out,'1:demo\n','varsayılan')
for n in (1,2,3):
    eq(run(argv=['/n',str(n)]),''.join(f'{i}:demo\n' for i in range(1,n+1)),'geçerli sınır aralığı')
for etiket in ('iki öğe','A&B','%PATH%','x!y','sona^','Türkçe & % ! ^'):
    beklenen=''.join(f'{i}:{etiket}\n' for i in (1,2,3))
    eq(run(argv=['/etiket',etiket,'/n','3']),beklenen,'etiket veri olarak korunur')
    eq(run(argv=['/N','3','/ETIKET',etiket]),beklenen,'ters sıra ve seçenek harfleri')
eq(run(argv=['/n','1','/etiket','ilk','/n','2','/etiket','son']),'1:son\n2:son\n','son değer kazanır')
for argv in (['/n','0'],['/n','4'],['/n','01'],['/n','1+1'],['/n','abc'],['/n','%PATH%'],['/n'],['/n',''],['/etiket'],['/etiket',''],['/yok','x'],['/n','2','fazla']):
    r=calis(argv=argv)
    eq((r['kod'],r['cikti'],r['hata']),(2,'','kullanim\n'),'hatalı arayüz reddedildi')
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "etiket=demo"
set "n=1"
:ayristir
if "%~1"=="" goto dogrula
if /i "%~1"=="/etiket" goto etiket_al
if /i "%~1"=="/n" goto sayi_al
goto kullanim
:etiket_al
set "yeni=%~2"
if not defined yeni goto kullanim
set "etiket=%yeni%"
shift
shift
goto ayristir
:sayi_al
set "yeni=%~2"
if not defined yeni goto kullanim
set "n=%yeni%"
shift
shift
goto ayristir
:dogrula
if "%n%"=="1" goto yaz
if "%n%"=="2" goto yaz
if "%n%"=="3" goto yaz
goto kullanim
:yaz
setlocal EnableDelayedExpansion
for /l %%I in (1,1,!n!) do echo(%%I:!etiket!
endlocal
exit /b 0
:kullanim
>&2 echo kullanim
exit /b 2
```

```hint
Bir seçenek için iki SHIFT yap. Sayı doğrulanmadan FOR /L'ye girmesin. Etiketi delayed expansion kapalıyken yakala; yalnız yazarken !etiket! ile oku.
```
:::

::: gorev Sınırlı kayıt raporu üret
Kaynak `kayitlar.txt`, sonuç `rapor.txt`. Birinci argüman etiket; yoksa/boşsa `demo`. İkinci argüman sınır; yoksa/boşsa `2`; doluysa yalnız tam `1`, `2`, `3` geçerli. İkiden fazla argüman veya geçersiz sınır kullanım hatasıdır: stderr `kullanim`, çıkış 2, stdout boş ve eski rapor değişmeden kalsın. Geçerli argümanda kaynak yoksa stderr `kaynak-yok`, çıkış 1, eski rapor yine korunsun.

Başarıda raporu baştan yaz: önce `etiket=ETIKET`, sonra kaynak sırasındaki ilk N boş olmayan satır için `kayit=SATIR`, en sonda `adet=GERCEK_SAYI`. Az kayıt varsa var olanları yaz; kaynak boşsa adet 0. Stdout yalnız `rapor=rapor.txt`, çıkış 0. Kaynağı değiştirme. Etiket ve kayıtlar boşluk, Unicode, `&`, `%`, `!`, `^` içerebilir; çift tırnak/CR/LF kayıt içinde bulunmaz ve kayıt `|` ile başlamaz. `;` ile başlayan kayıtları koru. Dosyalar normal ve yazılabilirdir; çalışma klasörünün sistem hatalarını modellemek bu görevin dışında.

```setup
from pathlib import Path
Path('kayitlar.txt').write_text('ilk\n\nikinci\nüçüncü\n',encoding='utf-8')
```

```starter
@echo off
>"rapor.txt" echo etiket=demo
>>"rapor.txt" echo adet=0
echo rapor=rapor.txt
exit /b 0
```

```test
from pathlib import Path
kaynak=Path('kayitlar.txt')
rapor=Path('rapor.txt')
eq(out,'rapor=rapor.txt\n','başarı çıktısı')
eq(rapor.read_text(encoding='utf-8'),'etiket=demo\nkayit=ilk\nkayit=ikinci\nadet=2\n','varsayılan sınır')
eq(kaynak.read_text(encoding='utf-8'),'ilk\n\nikinci\nüçüncü\n','kaynak aynı')
satirlar=[';yorum değil','iki öğe','A&B','x!y','%PATH%','sona^']
for n in (1,2,3):
    veri='\n'.join(satirlar)+'\n'
    kaynak.write_text(veri,encoding='utf-8')
    etiket='Türkçe & % ! ^'
    eq(run(argv=[etiket,str(n)]),'rapor=rapor.txt\n','sınırın her değeri')
    eq(rapor.read_text(encoding='utf-8'),f'etiket={etiket}\n'+''.join('kayit='+s+'\n' for s in satirlar[:n])+f'adet={n}\n','tam kayıt sınırı ve üzerine yazma')
    eq(kaynak.read_text(encoding='utf-8'),veri,'kaynak değiştirilmedi')
for satir in ('A&B','x!y','%PATH%','sona^','iki öğe',';başlangıç'):
    kaynak.write_text(satir+'\n',encoding='utf-8')
    eq(run(argv=['demo','3']),'rapor=rapor.txt\n','sınırdan az kayıt')
    eq(rapor.read_text(encoding='utf-8'),f'etiket=demo\nkayit={satir}\nadet=1\n','özel karakterli tek kayıt')
kaynak.write_text('\n\n',encoding='utf-8')
eq(run(),'rapor=rapor.txt\n','boş kaynak')
eq(rapor.read_text(encoding='utf-8'),'etiket=demo\nadet=0\n','boş satırlar kayıt sayılmaz')
eq(run(argv=['','']),'rapor=rapor.txt\n','boş argümanlar varsayılan')
eq(rapor.read_text(encoding='utf-8'),'etiket=demo\nadet=0\n','boş etiket demo olur')
for argv in (['x','0'],['x','4'],['x','01'],['x','1+1'],['x','abc'],['x','2','fazla'],['x','2','']):
    once=rapor.read_bytes()
    r=calis(argv=argv)
    eq((r['kod'],r['cikti'],r['hata']),(2,'','kullanim\n'),'hata kodu ve kanalı')
    eq(rapor.read_bytes(),once,'doğrulama yazmadan önce')
kaynak.unlink()
once=rapor.read_bytes()
r=calis()
eq((r['kod'],r['cikti'],r['hata']),(1,'','kaynak-yok\n'),'eksik kaynak')
eq(rapor.read_bytes(),once,'eksik kaynak raporu bozmaz')
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "etiket=%~1"
if not defined etiket set "etiket=demo"
set "n=%~2"
if not defined n set "n=2"
if not [%3]==[] goto kullanim
if "%n%"=="1" goto kaynak_kontrol
if "%n%"=="2" goto kaynak_kontrol
if "%n%"=="3" goto kaynak_kontrol
goto kullanim
:kaynak_kontrol
if not exist "kayitlar.txt" goto eksik
set "adet=0"
setlocal EnableDelayedExpansion
>"rapor.txt" echo(etiket=!etiket!
endlocal
for /f "usebackq eol=| delims=" %%L in ("kayitlar.txt") do (
    set "satir=%%L"
    call :kayit
)
>>"rapor.txt" echo(adet=%adet%
echo rapor=rapor.txt
exit /b 0
:kayit
if %adet% geq %n% exit /b 0
set /a adet+=1 >nul
setlocal EnableDelayedExpansion
>>"rapor.txt" echo(kayit=!satir!
endlocal
exit /b 0
:kullanim
>&2 echo kullanim
exit /b 2
:eksik
>&2 echo kaynak-yok
exit /b 1
```

```hint
Raporu açmadan bütün kullanım kontrollerini bitir. FOR /F'nin her satırını delayed expansion kapalıyken yakala, sabit CALL ile sayacı denetle; metni yalnız yazarken genişlet. Kayıt alt yordamının kendi SETLOCAL'ından önce artırılan sayaç çağıranda kalır.
```
:::
