---
id: cm04
title: set /p ile Satır Satır Girdi
summary: Standart girdiden satır okumak; boş satır ve EOF eski değeri değiştirmez, önceden temizlemek ve ardışık okumalar.
---

::: anlat Argüman başka, standart girdi başka
Argümanlar betik çağrılırken numaralı parametreler olur. Standart girdi ise okunacak metin akışıdır. `set /p "pafta_satir="` bir girdi satırını değişkene almaya çalışır. Eşittirden sonra istem metni olmadığı için ekrana soru yazmaz. `set /p "pafta_satir=Ad: "` ise istemi çıktı akışına da yazar; testli görevlerde görünmez sanma.

Pafta Girdi kutusunu CMD için UTF-8, Windows satır sonlu geçici dosyadan standart girdiye yönlendirir. Bu sözleşme ardışık set /p komutlarının kısa satırları sırayla almasını sağlar. Başka bir programın pipe girişiyle aynı tamponlama davranışını varsayma. SET /P'nin yerel tampon sınırı vardır; uzun satırda veri kesilebilir veya sonraki okumanın sınırı değişebilir. Bu paftanın görevlerinde her satır en fazla **200 karakterdir**. Etkileşimli klavye, özel tuşlar veya genel uzun satır okuyucu yazmak bu alıştırmanın kapsamında değildir.

Değerin içinde boşluk, Türkçe ve kabuk için özel karakter bulunabilir. Veriyi başka bir komut satırına tırnaksız yapıştırma. Önceki paftadaki gibi `echo "%pafta_satir%"` ile görünen tırnakları bilinçli olarak koruyacağız. Bu görevlerde satır içi çift tırnak ve NUL yoktur; bunları destekleyen genel bir veri taşıma biçimi tasarlamıyoruz.
:::

::: anlat Boş satır yeni bir boş değer atamaz
set /p boş satır veya EOF gördüğünde önceden var olan değeri boş metne dönüştürmez. Örneğin önce `set "pafta_satir=eski"` yazdıysan boş girişten sonra eski değer kalabilir. Eski veriyi yeni giriş sanmamak için okuma öncesinde `set "pafta_satir="` ile temizlemek gerekir. Alternatif olarak bilinçli bir varsayılan atayıp boş girişte onun kalmasını isteyebilirsin.

`if defined pafta_satir` değerin tanımlı olup olmadığını sorar; komutu sonraki paftada ayrıntılandıracağız. Burada verilen hazırlık kodundaki boş giriş kararını okuyabilirsin. Tek bir boşluk içeren satır, sıfır uzunlukta satır değildir; varsayılanla değiştirilmemelidir. Satır sonu verinin parçası olmaz, iki satır ise iki ayrı okumaya gider.

Bu görevler boş satır ile EOF'u ayrı durumlar olarak raporlamaz; ikisi de tanımlı değer bırakmıyorsa belirtilen varsayılana gider. İlk çalıştırmanın başarıyla bitebilmesi için normal/hata dönüşü açıkça `exit /b 0` ile tamamlanır. Girdiyi okuyamama durumunun bütün programlarda başarı olması gerektiği sonucu çıkarma; burada tasarlanan arayüz varsayılan kullanıyor.

Kaynaklar (21 Ekim 2026): [set /p](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set_1), [if defined](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if). Boş satır ve EOF davranışları ayrıca bu makinedeki gerçek cmd.exe ile sınandı.
:::

::: tahmin

Aşağıdaki gerçek batch betiğini cmd.exe çalıştıracak. Çıktıyı satır satır tahmin et; komutların kendisini değil, ekrana yazılan metni düşün.

```cmd
@echo off
set "pafta_ilk=eski"
set "pafta_ikinci=onceki"
set /p "pafta_ilk="
set /p "pafta_ikinci="
echo "ilk=%pafta_ilk%"
echo "ikinci=%pafta_ikinci%"
exit /b 0
```

```stdin

yeni
```

???

Girdi ilk satırda boştur; ilk değişkenin eski değeri değişmez. İkinci satır yeni olduğundan ikinci değer değişir: `"ilk=eski"` ve `"ikinci=yeni"`. İki ayrı set /p aynı değişkeni kendiliğinden sıfırlamaz.

:::

::: gorev Boş girişe bilinçli varsayılan

Girdi sözleşmesi: her fiziksel satır en fazla 200 karakter.

Bir satır oku. Okumadan önce pafta_satir değerini temizle. Boş satır veya EOF sonucunda tanımsızsa `varsayılan` ata. Sonra değeri tırnaklı tek satır yazıp 0 dön. İkinci ve sonraki girdi satırlarını kullanma. Tek boşluk dolu bir satırdır. Girdide çift tırnak yoktur.

```starter
@echo off
set "pafta_satir=eski"
set /p "pafta_satir="
echo "%pafta_satir%"
exit /b 0
```

```stdin
şube 1
```

```test
eq(out, '"şube 1"\n', "ilk giriş")
eq(run_code('@echo off\nset "pafta_satir=önceki"\n'+src, stdin='\n'), '"varsayılan"\n', 'okumadan önceki değer de temizlenir')
eq(run(stdin='ş'*200+'\n'), '"'+'ş'*200+'"\n', 'kısa satır sözleşmesinin 200 karakter ucu')
for stdin, expected in [('','varsayılan'),('\n','varsayılan'),(' \n',' '),('0\n','0'),('-1\n','-1'),('A&B %PATH%!^\n','A&B %PATH%!^'),('Türkçe giriş\n','Türkçe giriş'),('ilk\nikinci\n','ilk')]:
    r = calis(stdin=stdin)
    eq(r['kod'], 0, 'varsayılan arayüzü başarıyla döner')
    eq(r['cikti'], '"'+expected+'"\n', 'satır ve boşluk sınırı')
    eq(r['hata'], '', 'veri kabuk komutu değildir')
```

```solution
@echo off
set "pafta_satir="
set /p "pafta_satir="
if not defined pafta_satir set "pafta_satir=varsayılan"
echo "%pafta_satir%"
exit /b 0
```

```hint
set /p boş satırda eski değeri silmez; temizle, oku, sonra defined kararı ver.
```

:::

::: gorev İki bağımsız satırı karıştırma

Girdi sözleşmesi: her fiziksel satır en fazla 200 karakter.

Önce pafta_bir ve pafta_iki değerlerini temizle, sonra iki set /p ile iki satır oku. Tam iki satır yaz: `"bir=<ilk>"`, `"iki=<ikinci>"`. Boş satır veya eksik ikinci satır, ilgili alanda boş metin olarak görünür; birinciyi ikinciye kopyalama. Kod 0. Üçüncü satır kullanılmaz; satırlarda çift tırnak yoktur.

```starter
@echo off
set "pafta_bir="
set /p "pafta_bir="
set "pafta_iki=%pafta_bir%"
echo "bir=%pafta_bir%"
echo "iki=%pafta_iki%"
exit /b 0
```

```stdin
kullanıcı
başarılı
```

```test
eq(out, '"bir=kullanıcı"\n"iki=başarılı"\n', "iki satırın sırası")
eq(run_code('@echo off\nset "pafta_bir=eski-bir"\nset "pafta_iki=eski-iki"\n'+src, stdin='\n\n'), '"bir="\n"iki="\n', 'iki eski değer de temizlenir')
eq(run(stdin='x'*200+'\n'+'ş'*200+'\n'), '"bir='+'x'*200+'"\n"iki='+'ş'*200+'"\n', 'iki satır da 200 karakter sınırında')
for stdin, first, second in [('a\nb\n','a','b'),('a\n\n','a',''),('\nb\n','','b'),('a\n','a',''),('','',''),('0\n-1\n','0','-1'),('A&B\nyüzde%PATH%!^\n','A&B','yüzde%PATH%!^'),('x\ny\nz\n','x','y')]:
    r = calis(stdin=stdin)
    eq(r['kod'], 0, 'iki satırlı arayüz')
    eq(r['cikti'], '"bir='+first+'"\n"iki='+second+'"\n', 'satır/EOF eşleşmesi')
    eq(r['hata'], '', 'hata yok')
```

```solution
@echo off
set "pafta_bir="
set "pafta_iki="
set /p "pafta_bir="
set /p "pafta_iki="
echo "bir=%pafta_bir%"
echo "iki=%pafta_iki%"
exit /b 0
```

```hint
İki değişkeni de okumadan önce temizle; ayrı set /p komutları sıradaki satırı okur.
```

:::
