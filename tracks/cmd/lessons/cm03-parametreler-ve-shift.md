---
id: cm03
title: Argümanlar, Eksik Girdi ve shift
summary: %1 ile %~1, boşluklu argüman, tırnakların kaldırılması ve korunması; eksik parametre, çıkış kodu ve shift /1.
---

::: anlat Betik dosyasına dışarıdan bilgi ver
Bir batch dosyası argüman alabilir: ilk değer `%1`, ikinci `%2` biçiminde okunur. Değer boşluk içeriyorsa çağrıda tırnakla tek argüman olarak tutulmalıdır. `%~1` ilk argümanın çevresindeki tırnakları kaldırır. Sonra veriyi yeni komutta kullanırken gereken tırnağı tekrar **sen** koyarsın: `echo "%~1"`.

Tezgahtaki görevler args listesini güvenli çağrı sözleşmesiyle verir. Bu başlangıç yolunda argümanların içinde çift tırnak veya satır sonu yoktur. Boşluk, Türkçe ve `& % ! ^` gibi karakterler tek argümanın verisi olabilir. Bunları tırnaksız bir komut parçasına yerleştirip çalıştırma. Özellikle `call` ile ikinci kez genişletme bu derste yok; tek genişleme için yazılmış kodu rastgele yeniden genişletmek anlamı değiştirebilir.

Bir betik `%~1` boş olduğunda eksik girdi kararı verebilir: `if "%~1"=="" goto eksik`. Bu basit kontrol, argümanın hiç verilmemesini ve açık boş metin argümanını aynı kabul eder. İkisini ayırt ettiğimizi iddia etmiyoruz.
:::

::: anlat Parametre sırası da bir durumdur
`shift`, numaralı parametreleri kaydırır; varsayılan biçim %0'ı da değiştirir. Bu derste `shift /1` kullanarak %0'ı korur, eski %2'yi yeni %1 yaparız. `%*` bütün orijinal argümanları temsil eder ve shift ile kaymaz; numaralı alanlarla aynı şey değildir. Daha sonra döngüyle değişken sayıda argüman tüketmeyi göreceğiz; burada yalnız iki argüman var.

`goto etiket`, akışı `:etiket` satırına götürür. Bir eksik girdi yolunda `echo HATA` yazıp `exit /b 2` ile dönebilir, normal yolun yanlışlıkla bu etikete düşmesini `exit /b 0` ile önleyebilirsin. Bu dersin ilk görev çalıştırmasına geçerli argüman verilir; hata senaryoları Python testindeki `calis(argv=[...])` ile ayrıca sınanır.

`calis` sonuç sözlüğündeki kod çıkış kodu, cikti standart çıktı, hata hata akışıdır. Bu yardımcılar çözüme Python eklemek anlamına gelmez. Öğrencinin betiği gerçek CMD'de tekrar çalıştırılır; olumlu ve olumsuz girdileri çıktılarıyla birlikte görürsün.

Kaynaklar (21 Ekim 2026): [batch parametreleri](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/call), [shift](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/shift), [if](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if), [exit](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/exit).
:::

::: tahmin

Aşağıdaki gerçek batch betiğini cmd.exe çalıştıracak. Çıktıyı satır satır tahmin et; komutların kendisini değil, ekrana yazılan metni düşün.

```cmd
@echo off
echo "ilk=%~1"
shift /1
echo "yeni-ilk=%~1"
exit /b 0
```

```meta
argv: "web sunucusu" 443
```

???

İki satır: `"ilk=web sunucusu"` ve `"yeni-ilk=443"`. İlk boşluklu değer tek argümandır. shift /1 sonrasında yeni %1 eski ikinci değerdir.

:::

::: gorev Eksik hedefi bildir

İlk argümanı tırnaklı tek satır yazdır; başarı kodu 0 olsun. İlk argüman eksik veya boşsa yalnız `HATA: hedef gerekli` yazıp kod 2 ile bitir. Ek argümanlar bu görevde kullanılmaz. Görünen tırnaklar istenir; & ve benzeri karakterler komut olarak yorumlanmamalı.

```starter
@echo off
echo "%~1"
exit /b 0
```

```meta
argv: "web sunucusu"
```

```test
eq(out, '"web sunucusu"\n', "varsayılan argüman")
for value in ('sunucu', 'iki kelime', 'çalışma alanı', 'A&B', 'yüzde%PATH%', 'ünlem!', 'caret^', '0', '-1'):
    r = calis(argv=[value])
    eq(r['kod'], 0, 'geçerli hedef')
    eq(r['cikti'], '"'+value+'"\n', 'argüman veri olarak korunur')
    eq(r['hata'], '', 'yan komut veya hata yok')
for args in ([], ['']):
    r = calis(argv=args)
    eq(r['kod'], 2, 'eksik hedef kodu')
    eq(r['cikti'], 'HATA: hedef gerekli\n', 'eksik hedef mesajı')
eq(run(argv=['tek','ikinci']), '"tek"\n', 'yalnız ilk argüman')
```

```solution
@echo off
if "%~1"=="" goto eksik
echo "%~1"
exit /b 0
:eksik
echo HATA: hedef gerekli
exit /b 2
```

```hint
Normal yol hata etiketine düşmesin. %~1 değerini echo içinde tekrar tırnakla.
```

:::

::: gorev İkinci argümanı shift ile gör

İki argüman gerekir. İkisi de doluysa önce `"ilk=<birinci>"`, shift sonrasında `"kalan=<ikinci>"` yazıp kod 0 ile bitir. Biri eksik/boşsa yalnız `HATA: iki arguman gerekli` yazıp kod 2 dön. Üçüncü ve sonrası kullanılmaz. %0 dosya bilgisini kaydırmayan /1 biçimini öğrenmek için verilen shift satırını kullanabilirsin.

```starter
@echo off
echo "ilk=%~1"
rem shift burada olacak
echo "kalan=%~1"
exit /b 0
```

```meta
argv: kontrol "ödev klasörü"
```

```test
eq(out, '"ilk=kontrol"\n"kalan=ödev klasörü"\n', 'iki argüman')
for a,b in [('0','1'),('-1','0'),('A&B','ünlem!'),('iki kelime','yüzde%PATH%^'),('çığ','şube')]:
    r = calis(argv=[a,b,'fazla'])
    eq(r['kod'], 0, 'iki dolu argüman')
    eq(r['cikti'], '"ilk='+a+'"\n"kalan='+b+'"\n', 'sıra ve değerler')
    eq(r['hata'], '', 'girdi komut olmadı')
for args in ([],['tek'],['','ikinci'],['ilk','']):
    r = calis(argv=args)
    eq(r['kod'], 2, 'eksik parametre')
    eq(r['cikti'], 'HATA: iki arguman gerekli\n', 'hata yolunda kısmi çıktı yok')
```

```solution
@echo off
if "%~1"=="" goto eksik
if "%~2"=="" goto eksik
echo "ilk=%~1"
shift /1
echo "kalan=%~1"
exit /b 0
:eksik
echo HATA: iki arguman gerekli
exit /b 2
```

```hint
İki parametreyi çıktıdan önce doğrula; /1 eski ikinciyi yeni birinci yapar.
```

:::
