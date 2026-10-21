---
id: cm13
title: Çıkış Kodları · errorlevel ve Komut Zinciri
summary: exit /b, eşik anlamındaki if errorlevel, büyükten küçüğe sınıflandırma ve &&/|| kararlarının sınırları.
---

::: anlat errorlevel bir eşitlik testi değildir
Bir komutun metin çıktısı ile dönüş kodu ayrı kanallardır. Başarı genellikle 0, hata ise sıfırdan farklı bir koddur; hangi kodun ne anlama geldiğini komutun sözleşmesi belirler. Batch içinde `exit /b 2` geçerli betik veya alt yordamdan 2 ile döner. `/b` olmadan `exit` komut işlemcisini kapatabilir.

`if errorlevel 2` demek “kod tam 2” değil, **2 veya daha büyük** demektir. Kod sınıflandırırken en yüksek eşiği önce denetle; ilk eşleşmeden sonra aynı işleme devam edip ikinci etiket basma. `%errorlevel%` ile eşitlik/numerik karşılaştırma da yapılabilir, fakat bu adı kendin ortam değişkeni olarak tanımlarsan dinamik değeri gölgelersin. Parantezli blokta `%...%` genişlemesinin zamanına da dikkat et.

```cmd
@echo off
cmd /d /c exit 2
if errorlevel 3 echo agir
if errorlevel 2 echo en-az-iki
if errorlevel 1 echo en-az-bir
exit /b 0
```

Bu örneğin son kodu 0'dır; önceki 2 yalnız koşulları göstermek için üretilmiştir. Gerçek araç kodunu, başka bir komut değiştirmeden hemen denetle.
:::

::: anlat && ile || bir if/else çifti kurmaz
`A && B` B'yi ancak A başarılıysa çalıştırır. `A || C` C'yi A başarısızsa çalıştırır. Fakat `A && B || C` ifadesinde B'nin başarısızlığı da C'yi çalıştırabilir. C'yi “yalnız A başarısızsa” sanmak iki farklı hatayı birbirine karıştırır.

```cmd
@echo off
cmd /d /c exit 0 && cmd /d /c exit 1 || echo zincirde-hata
exit /b 0
```

İlk komut başarılıdır ama ikinci komut 1 döner; son mesaj yine yazılır. İki ayrı adımın hatasını farklı raporlamak istiyorsan her birinden sonra ayrı `if errorlevel` ve etiket kullan. Bu dersteki sayısal girdiler açıkça 0–9 arasındaki tek basamaklı eğitim kodlarıdır; kullanıcı metnini doğrulamadan `cmd /c exit ...` içine yerleştirmek genel bir veri işleme yöntemi değildir.

Kaynaklar: [Microsoft if](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if), [cmd](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), [exit](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/exit).
:::

::: tahmin
Hangi üç satır yazılır? Betiğin sonunda hangi dönüş kodu üretildiğini metin çıktısından ayrı düşün.

```cmd
@echo off
cmd /d /c exit 2
if errorlevel 3 echo uc
if errorlevel 2 echo iki-ve-ustu
if errorlevel 1 echo bir-ve-ustu
cmd /d /c exit 0 && cmd /d /c exit 1 || echo zincirde-hata
exit /b 0
```

???

`iki-ve-ustu`, `bir-ve-ustu`, `zincirde-hata` yazılır. İlk kod 2 iki alt eşiği de sağlar. Son zincirde ilk komutun değil ikinci komutun hatası mesajı açar. En sondaki `exit /b 0`, bu örnek betiğini başarıyla bitirir.
:::

::: gorev Büyükten küçüğe sınıflandır
Girdinin ilk satırında 0–9 arasında tek basamaklı bir kod var; girdi yoksa 0 kullan. Kod 3 ve üzeriyse yalnız `agir`, 1–2 ise yalnız `uyari`, 0 ise yalnız `tamam` yazdır. Betik her durumda 0 ile bitsin. Bu görevde girdi sözleşmesi sayısal; başka metni komut olarak yürütme.

```starter
@echo off
echo tamam
exit /b 0
```

```test
eq(out, "tamam\n", "girdisiz varsayılan")
for n, mesaj in ((0,"tamam"),(1,"uyari"),(2,"uyari"),(3,"agir"),(4,"agir"),(9,"agir")):
    eq(run(str(n)+"\n"), mesaj+"\n", f"kod {n}")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "rc=0"
set /p "rc="
cmd /d /c exit %rc%
if errorlevel 3 goto agir
if errorlevel 1 goto uyari
echo tamam
exit /b 0
:agir
echo agir
exit /b 0
:uyari
echo uyari
exit /b 0
```

```hint
3 eşiğini 1'den önce denetle. Her çıktı dalını exit /b 0 ile bitir; aynı koda iki etiket yazma.
```
:::

::: gorev İki adımın hatasını ayır
İlk iki argüman iki eğitim komutunun dönüş kodudur; her biri 0, 1 veya 2 olabilir. Eksik argüman 0'dır. İlk kod sıfır değilse yalnız `ilk-basarisiz`; ilk başarılı ama ikinci sıfır değilse yalnız `ikinci-basarisiz`; ikisi de 0 ise yalnız `tamam` yaz. Betiğin kendi kodu 0 olsun. `&& B || C` ile ilk hatayı tahmin etmek yerine iki sonucu ayrı denetle.

```starter
@echo off
echo tamam
exit /b 0
```

```test
eq(out, "tamam\n", "varsayılanlar")
for ilk in (0,1,2):
    for ikinci in (0,1,2):
        mesaj = "ilk-basarisiz" if ilk else "ikinci-basarisiz" if ikinci else "tamam"
        eq(run(argv=[str(ilk),str(ikinci)]), mesaj+"\n", f"{ilk}/{ikinci}")
eq(run(argv=["1"]), "ilk-basarisiz\n", "ikinci argüman yok")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "ilk=%~1"
set "ikinci=%~2"
if not defined ilk set "ilk=0"
if not defined ikinci set "ikinci=0"
cmd /d /c exit %ilk%
if errorlevel 1 goto ilk_hata
cmd /d /c exit %ikinci%
if errorlevel 1 goto ikinci_hata
echo tamam
exit /b 0
:ilk_hata
echo ilk-basarisiz
exit /b 0
:ikinci_hata
echo ikinci-basarisiz
exit /b 0
```

```hint
İlk komuttan hemen sonra onun dönüşünü denetle. İlk dal biterse ikinci komuta düşmemeli.
```
:::
