---
id: cm02
title: Değişkenler, Tırnaklar ve Boş Değer
summary: set "ad=değer" biçimi, %ad% genişlemesi, boşluk ve silme; veri tırnakları ile set sözdizimi tırnaklarını ayırmak.
---

::: anlat set bir ortam metni oluşturur
CMD değişkenleri bu aşamada metindir. `set "pafta_ad=web sunucusu"` adı pafta_ad olan bir ortam değerini atar. Sonraki ayrı satırdaki `%pafta_ad%` bu değere genişler. `set` eşittir işaretinin çevresindeki boşlukları sırf okunaklı diye yok saymaz; `set ad = veri` başka bir ad/değer yaratabilir. Düzenli biçim olarak tırnağı bütün `ad=değer` ifadesinin çevresine koyacağız.

`set "pafta_ad=örnek değer"` biçimindeki dış tırnaklar değerin parçası olmaz. Buna karşılık `set pafta_ad="örnek değer"` tırnakları değerin içine koyar. İkisini karıştırmak dosya yolu ve karşılaştırma sorunları yaratır. Sabit testlerde sonda istenmeyen boşluk bırakmamak da önemlidir; bütün atamayı saran tırnak bunu görünür kılar.

Bir değeri yazdırırken `echo "%pafta_ad%"` kullanacağız. Buradaki echo tırnakları **çıktıda görünür**. Bu bilinçli sözleşme, boşluğu ve `&` gibi kabuk karakterlerini veri olarak tutmayı kolaylaştırır. Tırnakların görünmesini istemediğin her senaryoya bu örneği körce taşımayacaksın; CMD ayrıştırmasını ileride daha ayrıntılı inceleyeceğiz.
:::

::: anlat Boş değer ve yeniden atama
`set "pafta_ad="` değişkeni ortamdan temizler. CMD'de “tanımlı ama boş metin” ile “tanımsız” durumunu bu basit set biçimiyle ayrı tutmazsın. `echo "%pafta_ad%"` artık `""` yazdırır. Yalnız `echo %pafta_ad%` yazmak ise değer boşken echo durumunu gösterebilir; çıktıyı karıştırmamak için burada tırnaklı biçimi koruyoruz.

`%ad%` genişlemesinin zamanı önemlidir. Bu ilk örneklerde her atama ve her okuma ayrı satırdadır. Parantezli bir blokta önce atayıp aynı blok içinde `%ad%` ile yeni değeri göreceğini varsayma; blok genişlemesi ayrı bir dersin konusudur. Koşucu gecikmeli genişlemeyi kapalı başlatır; bu nedenle `!ad!` burada ikinci bir değişken yazımı olarak kullanılmaz.

Programın kendi değişkenleri için pafta_ öneki kullanıyoruz. PATH, TEMP ve kullanıcı ortamındaki başka önemli adları deneme değişkeni yapma; basit bir atama sonraki komutların hangi programı bulduğunu etkileyebilir. Bu ders yalnız kendi eğitim adlarını atar ve her çalışmada baştan kurar.

Kaynaklar (21 Ekim 2026): [set ve değişken genişlemesi](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set_1), [cmd tırnak ve genişleme seçenekleri](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd).
:::

::: tahmin

Aşağıdaki gerçek batch betiğini cmd.exe çalıştıracak. Çıktıyı satır satır tahmin et; komutların kendisini değil, ekrana yazılan metni düşün.

```cmd
@echo off
set "pafta_ad=web sunucusu"
echo "%pafta_ad%"
set "pafta_ad=veritabani"
echo "%pafta_ad%"
set "pafta_ad="
echo "%pafta_ad%"
exit /b 0
```

???

Üç satır: `"web sunucusu"`, `"veritabani"`, `""`. İlk atama dış tırnakları değere katmaz; ekranda görünen tırnaklar echo satırlarının kendi tırnaklarıdır.

:::

::: gorev İki alanlı kart

pafta_makine değerini `web sunucusu`, pafta_durum değerini `hazır` yap. Tam iki satır üret: `"makine=web sunucusu"` ve `"durum=hazır"`. Tırnaklar çıktının parçasıdır. Değişkenleri ayrı satırlarda ata ve oku.

```starter
@echo off
set "pafta_makine="
set "pafta_durum="
echo "makine=%pafta_makine%"
echo "durum=%pafta_durum%"
exit /b 0
```

```test
eq(out, '"makine=web sunucusu"\n"durum=hazır"\n', "iki değişkenli kart")
eq(run().splitlines(), ['"makine=web sunucusu"','"durum=hazır"'], "boşluk ve Türkçe korunur")
eq(hata_cikti, "", "fazladan komut hatası yok")
```

```solution
@echo off
set "pafta_makine=web sunucusu"
set "pafta_durum=hazır"
echo "makine=%pafta_makine%"
echo "durum=%pafta_durum%"
exit /b 0
```

```hint
Dış tırnak set ifadesinin tamamını sarsın; echo metnindeki tırnaklar görünür.
```

:::

::: gorev Yenile ve temizle

pafta_not değerini önce `ilk kayıt`, sonra `ikinci kayıt` yap; her atamadan sonra tırnaklı yazdır. Sonra değeri temizleyip tırnaklı boş sonucu yazdır. Tam üç satır olsun; yorum veya echo durum mesajı eklenmesin.

```starter
@echo off
set "pafta_not=ilk kayıt"
echo "%pafta_not%"
echo "%pafta_not%"
echo "%pafta_not%"
exit /b 0
```

```test
eq(out, '"ilk kayıt"\n"ikinci kayıt"\n""\n', "yeniden atama ve temizleme")
eq(len(out.splitlines()), 3, "tam üç satır")
eq(hata_cikti, "", "hata yok")
```

```solution
@echo off
set "pafta_not=ilk kayıt"
echo "%pafta_not%"
set "pafta_not=ikinci kayıt"
echo "%pafta_not%"
set "pafta_not="
echo "%pafta_not%"
exit /b 0
```

```hint
Temizlemek için set "pafta_not="; bütün okumalar atamadan sonraki ayrı satırda.
```

:::
