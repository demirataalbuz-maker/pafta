---
id: cm01
title: CMD ile İlk Batch Betiğin
summary: cmd.exe ile PowerShell farkı; .cmd dosyası, @echo off, rem ve echo; görünür çıktı ile komut yankısını ayırmak.
---

::: anlat Bir Windows terminali, tek bir dil değildir
Windows Terminal birden çok kabuğu barındırabilir; CMD ve PowerShell aynı dil değildir. CMD'de ortam değişkenini `%AD%`, PowerShell'de değişkeni `$ad` biçiminde görürsün. CMD'nin `dir` komutunu bilmen PowerShell'in nesne boru hattını aynı kurallarla çalıştırmaz. Burada `cmd.exe` yorumlayıcısına verilen `.cmd` batch dosyaları yazıyoruz; `.bat` da bu yorumlayıcının yaygın betik uzantısıdır.

Bir batch dosyası sırayla yürütülen komutlardan oluşur. `echo Merhaba` bir satır yazdırır. `rem Aciklama` yorum satırıdır; echo kapalıyken yorum metni çıktı olmaz. Rem satırlarını da kabuk sözdiziminin dışında büyülü bir metin alanı sayma: yönlendirme/pipe karakterlerini gelişi güzel yorum içine yerleştirmek beklenmedik ayrıştırma etkisi yaratabilir.

Pafta gerçek Windows cmd.exe kullanır. Dersler geçici bir çalışma klasöründe çalışır; burası bilgisayarın dosyalarına erişimi engelleyen bir güvenlik kum havuzu değildir. Bu başlangıç paftalarında yalnız eğitim metni yazdırıyoruz. Yeni bir kabuk açmak veya bilgisayar ayarı değiştirmek gerekmiyor.
:::

::: anlat Komutun yankısı ile komutun çıktısı
`echo off`, komut satırlarının çalıştırılmadan önce ekrana yazılmasını kapatır; echo komutunun ürettiği mesajı kapatmaz. Satır başındaki `@`, yalnız o satırın yankısını bastırır. Bu yüzden yaygın başlangıç `@echo off`tur: ayarın kendi satırı da görünmez. Koşucunun `/q` ayarı yankıyı zaten kapalı başlatsa da betiğin niyetini dosyada açık yazmak faydalıdır.

Boş satır için `echo.` kullanabilirsin; echo ile nokta arasına boşluk koyma. Yalnız `echo` yazarsan boş satır yerine echo durumunu sorarsın. Çıktıdaki büyük harf, noktalama ve satır sonu testlerde anlamlıdır.

`exit /b 0` mevcut batch'i başarı koduyla bitirir. Bu komutun ayrıntısını ileride işleyeceğiz; şimdilik örneklerin sonundaki 0, başarılı bitiş sözleşmesidir. Pafta testlerinde `out` ilk çalıştırmanın metni, `run()` betiği yeniden çalıştırıp aldığı metindir. Bunlar Python test yardımcılarıdır; editöre yazdığın çözüm yine batch kodudur.

Kaynaklar (21 Ekim 2026): [cmd](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), [echo](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/echo), [rem](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/rem), [exit](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/exit).
:::

::: tahmin

Aşağıdaki gerçek batch betiğini cmd.exe çalıştıracak. Çıktıyı satır satır tahmin et; komutların kendisini değil, ekrana yazılan metni düşün.

```cmd
@echo off
rem Bu satir ekrana yazilmaz
echo basla
echo.
echo bitti
exit /b 0
```

???

`basla`, bir boş satır ve `bitti` çıkar. Rem metni ve komut satırları görünmez. Echo kapalı olması, echo mesajlarının da kapatılması değildir.

:::

::: gorev İlk iki satırın

Komut yankısı olmadan tam iki satır yazdır: `Merhaba, Pafta!` ve `CMD hazir`. Sonunda başarı koduyla bitir. Yorum metnini çıktı olarak ekleme.

```starter
@echo off
rem Iki mesaji buraya yaz
exit /b 0
```

```test
eq(out, "Merhaba, Pafta!\nCMD hazir\n", "iki satırın tamamı")
eq(run(), "Merhaba, Pafta!\nCMD hazir\n", "yeniden çalıştırma aynı çıktıyı verir")
eq(hata_cikti, "", "hata akışı temiz")
```

```solution
@echo off
rem Acilis mesaji
echo Merhaba, Pafta!
echo CMD hazir
exit /b 0
```

```hint
Her görünür satır için echo; rem açıklamadır.
```

:::

::: gorev Türkçe durum kartı

Tam olarak `Çalışma kartı`, bir boş satır ve `Durum: hazır` yazdır. Başarı koduyla bitir. Tezgahtaki Unicode desteğini de bu çıktıda görebilirsin.

```starter
@echo off
echo Calisma karti
echo Durum: hazir
exit /b 0
```

```test
eq(out.splitlines(), ["Çalışma kartı", "", "Durum: hazır"], "Türkçe ve boş satır")
eq(out, "Çalışma kartı\n\nDurum: hazır\n", "son satır sonu da var")
eq(hata_cikti, "", "kodlama hatası yok")
```

```solution
@echo off
echo Çalışma kartı
echo.
echo Durum: hazır
exit /b 0
```

```hint
Boş satır echo. ile; Türkçe karakterleri metne doğrudan yaz.
```

:::
