---
id: cm15
title: Kapsam · setlocal, endlocal ve Veri
summary: Yerel değişkenler, endlocal ile kontrollü dönüş ve ! işareti içeren veriyi bozmadan okuyup yazmak.
---

::: anlat Yerel değişiklik ve kontrollü dönüş
`setlocal` sonrasında değiştirdiğin ortam, karşılık gelen `endlocal` veya batch bağlamının sonuna kadar yereldir. İç içe setlocal açılabilir. Bu, alt yordamın geçici değişkenlerini çağıranın değişkenlerinden ayırır. Parametreli setlocal ayrıca dönüş kodunu 0 yapabildiğinden, bir önceki komutun kodunu bunun ardından okuyarak koruduğunu sanma.

```cmd
@echo off
set "dis=koru"
setlocal DisableDelayedExpansion
set "dis=gecici"
set "sonuc=hazir"
endlocal & set "donus=%sonuc%"
echo dis=%dis%
echo donus=%donus%
exit /b 0
```

Son satırdaki `%sonuc%`, bütün satır ayrıştırılırken yerel kapsam henüz açıkken genişler; `endlocal` kapanınca SET bu değeri dış kapsama yazar. İsimleri sabit tut. Bu aktarım örneğinde hem iç hem dış gecikmeli genişleme kapalıdır; çift tırnak/CR/LF içeren veri sözleşme dışıdır. Bir komut satırını keyfi veriden yeniden kurmak için bu kalıbı kullanma.
:::

::: anlat Ünlemi okurken koru, yazarken genişlet
Gecikmeli genişleme açıkken literal `!` işaretleri genişleme işaretleri olarak ele alınabilir. Dosya veya argümandan alınan veriyi yakalamadan önce gecikmeli genişlemeyi kapat. Sonra değişkeni `!degisken!` olarak okumak ile kaynak satıra literal ünlem yazmak aynı aşama değildir.

`set /p` boş satırda mevcut değeri değiştirmez; bu yüzden önce `set "satir="` ile temizle. `echo(!satir!`, boş değer için de boş satır üretir; `echo %satir%` boşken “echo kapalı” durum mesajına dönüşebilir. Bu derste giriş en fazla iki fiziksel satırdır; çift tırnak ve CR/LF satırın içinde değil, satır sınırında bulunur.

Bu yöntemlerin davranışını gerçek CMD'de sınayacağız. Başka kabukların yüzde/ünlem kurallarını buraya taşımıyoruz. Dosya döngüsünde yakalama ve yazma aşamalarını ayırmayı sonraki dersin projesinde yeniden kullanacaksın.

Kaynaklar: [Microsoft setlocal](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setlocal), [endlocal](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/endlocal), [set](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set).
:::

::: tahmin
Aktarılan değer endlocal'dan önce mi sonra mı okunuyor? Ünlem içeren ikinci değeri de izle.

```cmd
@echo off
setlocal DisableDelayedExpansion
set "ad=dis"
setlocal DisableDelayedExpansion
set "ad=ic"
endlocal & set "son=%ad%"
echo ad=%ad%
echo son=%son%
set "veri=A!B"
setlocal EnableDelayedExpansion
echo(!veri!
endlocal
exit /b 0
```

???

`ad=dis`, `son=ic`, `A!B` yazılır. `ad` dış değerine döner ama `son` içte genişlemiş değeri alır. `veri` gecikmeli genişleme kapalıyken yakalanmıştır; sonradan `!veri!` ile gelen ünlem veri olarak korunur.
:::

::: gorev Bir sonucu kapsam dışına taşı
İlk argüman bir etiket; yoksa veya boşsa `dünya` kullan. Ana akışta `dis=koru` olsun. `call :hazirla` alt yordamı kendi yerel kapsamında dis'i değiştirsin ve `rapor:ETIKET` sonucunu `sonuc` değişkeniyle geri versin. Son çıktı tam `dis=koru` ve `sonuc=rapor:ETIKET` satırları olsun. Veriyi CALL argümanı yapma. Çift tırnak ve satır sonu dışında boşluk/Türkçe/&/%/!/ ^ korunmalı.

```starter
@echo off
echo dis=koru
echo sonuc=rapor:dünya
exit /b 0
```

```test
eq(out, "dis=koru\nsonuc=rapor:dünya\n", "varsayılan")
for ad in ("Ece","iki öğe","A&B","%PATH%","ünlem!var","sona^","&%!^"):
    eq(run(argv=[ad]), f"dis=koru\nsonuc=rapor:{ad}\n", "kapsam ve veri birlikte")
eq(run(argv=[""]), "dis=koru\nsonuc=rapor:dünya\n", "boş argüman varsayılan")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "dis=koru"
set "girdi=%~1"
if not defined girdi set "girdi=dünya"
call :hazirla
setlocal EnableDelayedExpansion
echo(dis=!dis!
echo(sonuc=!sonuc!
endlocal
exit /b 0
:hazirla
setlocal DisableDelayedExpansion
set "dis=ic"
set "yeni=rapor:%girdi%"
endlocal & set "sonuc=%yeni%"
exit /b 0
```

```hint
Endlocal'ın yanındaki SET satırında %yeni% kapanmadan genişler. Dış gecikmeli genişleme de kapalı kalsın; yalnız çıktı anında aç.
```
:::

::: gorev İki satırı bozmadan ters sırada yaz

Girdi sözleşmesi: her fiziksel satır en fazla 200 karakterdir. SET /P tamponu uzun satırları kesebildiği için bu yöntem sınırsız uzunlukta metin okuma iddiası taşımaz.
Girdiden iki satır oku, ardından `B=ikinci` ve `A=birinci` yaz. Eksik veya boş satır boş değerdir; önceki değer kalmasın. Satırlardaki boşluk, Unicode, `&`, `%`, `!`, `^` aynen korunsun. Üçüncü satır varsa kullanılmasın. Harici program veya CALL ile veriyi yeniden yorumlatma.

```starter
@echo off
set /p "a="
echo A=%a%
exit /b 0
```

```test
eq(out, "B=\nA=\n", "girdi yok")
for a,b in (("bir","iki"),("ilk öğe","son öğe"),("A&B","x!y"),("%PATH%","^ ve %"),("","B!"),("A!","")):
    eq(run(a+"\n"+b+"\n"), f"B={b}\nA={a}\n", "iki ayrı okuma")
eq(run("tek\n"), "B=\nA=tek\n", "ikinci satır eksik")
eq(run("a\nb\ngizli\n"), "B=b\nA=a\n", "yalnız ilk iki satır")
eq(run("x"*200+"\n"+"ş"*200+"\n"), "B="+"ş"*200+"\nA="+"x"*200+"\n", "200 karakterlik iki ayrı satır")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "a="
set "b="
set /p "a="
set /p "b="
setlocal EnableDelayedExpansion
echo(B=!b!
echo(A=!a!
endlocal
exit /b 0
```

```hint
SET /P'den önce değişkeni temizle. İki satırı delayed expansion kapalıyken oku, çıktıdan önce aç.
```
:::
