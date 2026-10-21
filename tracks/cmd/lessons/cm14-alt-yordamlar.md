---
id: cm14
title: Alt Yordamlar · call, shift ve Dönüş
summary: call :etiket, parametre bağlamı, shift'in %* üzerindeki etkisizliği ve veriyi ikinci genişlemeye sokmamak.
---

::: anlat Bir etikete gidip geri dönmek
`goto etiket` akışı taşır; `call :etiket` ise geri dönüş noktası oluşturur. Alt yordamın `exit /b N` komutu çağrıldığı yere N koduyla döner. Ana akışı `exit /b` ile bitirmezsen dosyada aşağıda duran etiketler kendiliğinden de çalışabilir. `goto :eof`, komut uzantıları açıkken geçerli batch bağlamının sonuna dönmek için kullanılabilir.

```cmd
@echo off
call :bolum "iki kelime" son
echo ana-akis
exit /b 0
:bolum
echo ilk=%~1
shift
echo sonra=%~1
exit /b 0
```

Çağrılan etiket kendi `%1`, `%2` bağlamına sahiptir. `%~1` dış tırnakları kaldırır; tek argümandaki boşluğu iki argümana dönüştürmez. `shift`, konumları sola kaydırır. `%*` ise başlangıçtaki bütün argüman metnini temsil eder ve shift ile değişmez. “Kalan argümanlar” için `%*` kullanarak aynı veriyi tekrar işlemek bu yüzden bir hatadır.
:::

::: anlat call, veri kaçırmanın kısayolu değildir
CALL komutunun tekrar genişletme davranışı nedeniyle `call echo %%degisken%%` gibi kalıplar bir değeri ikinci kez yorumlatabilir. Veri içindeki yüzde işaretini değişken, komut karakterini sözdizimi haline getirmek istemiyoruz. Aşağıdaki görevlerde `call :yaz` sabittir; kullanıcı verisi CALL satırına eklenmez, önceden yakalanmış ortam değişkeninden okunur.

Veriyi `setlocal DisableDelayedExpansion` altında `set "deger=%~1"` ile alacağız. Yalnız yazarken gecikmeli genişlemeyi açıp `echo(!deger!` kullanmak, bu sözleşmedeki veriyi yeniden komut metni olarak ayrıştırmadan basar. Çift tırnak ve CR/LF argüman içinde kabul edilmez; boşluk, Türkçe, `&`, `%`, `!`, `^` verinin parçası olabilir. Bu sınırları “her metin her konuma güvenle yerleştirilir” diye genelleme.

Kaynaklar: [Microsoft call](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/call), [shift](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/shift), [goto](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/goto).
:::

::: tahmin
`shift` sonrasında `%~1` ile `%*` aynı biçimde mi değişir? Dönüş kodunu kontrol eden ana akışı da izle.

```cmd
@echo off
call :incele "iki kelime" son
if errorlevel 7 echo donus=7
exit /b 0
:incele
echo ilk=%~1
shift
echo sonra=%~1
echo tum=%*
exit /b 7
```

???

`ilk=iki kelime`, `sonra=son`, `tum="iki kelime" son`, `donus=7` yazılır. `%*` değişmeden kalır; tırnakları da özgün argüman metninin parçası olarak görünür. Alt yordamın 7 kodu ana akışta okunur; örneğin son kodu 0'dır.
:::

::: gorev Veri taşımayan alt yordam çağrısı
İlk iki argümanı yakala; `call :yaz` ile bir alt yordam çağır. Çıktı iki satır olsun: `ilk=DEGER`, `son=DEGER`. Eksik argüman boş değerdir. Özel karakterleri ve harfleri aynen koru. Alt yordamdan ana akışa dön; çıktı iki kez basılmasın. Argümanları CALL satırına koyma; yordam önceden yakalanmış değişkenleri kullansın.

```starter
@echo off
echo ilk=%~1
exit /b 0
```

```test
eq(out, "ilk=\nson=\n", "eksik argümanlar")
for a,b in (("bir","iki"),("iki kelime","üçüncü öğe"),("A&B","x!y"),("%PATH%","yüzde% ve ^"),("son^","&%!^")):
    eq(run(argv=[a,b]), f"ilk={a}\nson={b}\n", "değerler bir kez basılır")
eq(run(argv=["tek"]), "ilk=tek\nson=\n", "bir argüman")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "ilk=%~1"
set "son=%~2"
call :yaz
exit /b 0
:yaz
setlocal EnableDelayedExpansion
echo(ilk=!ilk!
echo(son=!son!
endlocal
exit /b 0
```

```hint
Önce gecikmeli genişleme kapalıyken yakala. call :yaz sabit olsun; yordam içinde veriyi !ilk! ve !son! ile oku.
```
:::

::: gorev shift ile argümanları numaralandır
Boş olmayan bütün argümanları sırayla `1:DEGER`, `2:DEGER` biçiminde yazdır; sonunda `adet=N` olsun. Hiç argüman yoksa yalnız `adet=0`. Bu görevin argümanlarında boş metin yok; içinde boşluk ve önceki görevin özel karakterleri olabilir. Her turda `shift` ile ilerle. Sabit alt yordam çağrısı kullanarak veriyi ikinci genişlemeye sokmadan bas.

```starter
@echo off
echo adet=0
exit /b 0
```

```test
eq(out, "adet=0\n", "sıfır argüman")
for degerler in (["bir"],["bir","iki"],["üç öğe","A&B","%PATH%","x!y","son^"], [str(i) for i in range(12)]):
    beklenen = "".join(f"{i}:{v}\n" for i,v in enumerate(degerler,1)) + f"adet={len(degerler)}\n"
    eq(run(argv=degerler), beklenen, "sıra ve ondan fazla argüman")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set /a adet=0
:sonraki
if "%~1"=="" goto bitti
set "deger=%~1"
set /a adet+=1
call :yaz
shift
goto sonraki
:bitti
echo adet=%adet%
exit /b 0
:yaz
setlocal EnableDelayedExpansion
echo(!adet!:!deger!
endlocal
goto :eof
```

```hint
%* ile dönersen shift etkisi görünmez. %~1'i yakala, sabit yordamı çağır, shift yap ve etikete dön.
```
:::
