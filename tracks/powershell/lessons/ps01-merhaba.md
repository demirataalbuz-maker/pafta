---
id: ps01
title: Merhaba PowerShell
summary: Fiil-İsim komutlar, Write-Output, değişkenler, tek ve çift tırnak, $( ) ve -f biçimleme.
kazanim: AZ040 1.1, AZ040 1.2, AZ040 2.3, AZ040 6.1
---

::: anlat Fiil-İsim dünyası
**PowerShell**, Windows'un yönetim kabuğu ve betik dilidir (PowerShell 7 ile Linux ve macOS'ta da çalışır). Komutlarına **cmdlet** denir ve hepsi `Fiil-İsim` biçimindedir: `Get-Process`, `Stop-Service`, `Import-Csv`. Adı, ne yaptığını söyler.

Tezgahta kodun gerçek **Windows PowerShell 5.1**'de çalışır.

```powershell
Write-Output "Merhaba, PowerShell!"      #! çıktıyı boru hattına yazar
"Bu da çıktı olur"                       #! tek başına bir değer = Write-Output
$ad = "Pafta"                            #! değişkenler $ ile başlar
"Merhaba, $ad"                           #! çift tırnakta değişken açılır
'Merhaba, $ad'                           #! tek tırnakta açılmaz
"Uzunluk: $($ad.Length)"                 #! $( ): tırnak içinde ifade
# bu bir yorum
```

PowerShell'in en önemli farkı: borularda **metin değil nesne** akar. `$ad.Length` diyebilmen, `$ad`'ın bir .NET `String` nesnesi olmasındandır. Bunu PS05 ve PS07'de derinleştireceğiz.

> [!NOT]
> `Write-Host` doğrudan ekrana yazar, boru hattına **yazmaz**: çıktısı bir değişkene atanamaz ya da başka bir komuta iletilemez. Veri üreten betiklerde `Write-Output` (ya da çıplak değer) kullan; `Write-Host`'u sadece kullanıcıya renkli mesaj göstermek için sakla.

### Değişkenler ve türler
```powershell
$port = 443                       #! tür otomatik: Int32
$oran = 0.75                      #! Double
[int]$sayi = "42"                 #! tür belirt: metin int'e çevrilir
$sayi + 1
$port.GetType().Name
```
:::

::: tahmin
Üç satırın çıktısını yaz:

```powershell
$ad = "Pafta"
'Merhaba $ad'
"Merhaba $ad"
"Uzunluk: $($ad.Length)"
```

???

`Merhaba $ad`, `Merhaba Pafta`, `Uzunluk: 5`. Tek tırnak hiçbir şey açmaz. Çift tırnak içinde `$ad.Length` yazsaydın sadece `$ad` açılır ve sonuna düz `.Length` metni eklenirdi; özelliğe erişmek için `$( )` gerekir.
:::

::: anlat Aritmetik ve -f biçimleme
```powershell
$x = 7
$y = $x * 6
"$x * 6 = $y"
7 / 2                              #! / ondalıklı böler: 3.5
[math]::Floor(7 / 2)               #! tam bölme için
7 % 2                              #! kalan
"{0} ve {1}" -f "bir", "iki"       #! -f biçim işleci (.NET String.Format)
"{0:D5}|{1,-6}|{2:N1}" -f 42, "ab", 3.14159   #! D5: 5 hane, -6: sola yasla, N1: 1 ondalık
```

`-f` işleci, Python'daki f-string biçim tanımlarının (P05) .NET karşılığıdır: `{indeks:biçim}` ve `{indeks,genişlik}`.

> [!TUZAK]
> PowerShell'de `/` her zaman ondalıklı bölme yapar: `7 / 2` → `3.5`. Bir değeri `[int]`'e çevirmek ise **yuvarlar** (bankacı yuvarlaması: `[int]2.5` → 2, `[int]3.5` → 4). Tam bölme için `[math]::Floor()` ya da `[math]::Truncate()` kullan.
:::

::: tahmin
Çıktıyı satır satır yaz:

```powershell
$x = 7
$y = $x * 6
"{0} * 6 = {1}" -f $x, $y
"{0:D5}|{1,-6}|" -f 42, "ab"
```

???

`7 * 6 = 42`, sonra `00042|ab    |`. `D5` tam sayıyı 5 haneye sıfırla tamamlar, `{1,-6}` metni 6 karakterlik alanda sola yaslar.
:::

::: gorev Hedef kartı
`$hostAdi` değişkenine `web01`, `$port` değişkenine `443` ata ve değişkenleri kullanarak şunu yazdır:

```cikti
web01:443
```

```starter
# değişkenleri ata ve yazdır

```

```test
eq(out, "web01:443\n", "çıktı: web01:443")
ok("$hostAdi" in src and "$port" in src, "değişkenleri kullan")
ok("web01:443" not in src, "çıktıyı hazır metin olarak yazma")
```

```solution
$hostAdi = "web01"
$port = 443
"${hostAdi}:${port}"
```

```hint
Çift tırnak içinde `"$hostAdi:$port"` yazarsan PowerShell `$hostAdi:` yazımını bir **kapsam** öneki sanabilir. Süslü parantezle ayır: `"${hostAdi}:${port}"`. Ya da `-f` kullan: `"{0}:{1}" -f $hostAdi, $port`.
```
:::

::: gorev Dolar işaretli metin
Şu satırı **tam olarak** yazdır:

```cikti
Fiyat: $5 (vergi dahil)
```

```starter
"Fiyat: $5 (vergi dahil)"
```

```test
eq(out, "Fiyat: $5 (vergi dahil)\n", "dolar işareti korunmalı")
```

```solution
'Fiyat: $5 (vergi dahil)'
```

```hint
Tek tırnak kullan ya da çift tırnak içinde dolar işaretini PowerShell'in kaçış karakteri olan ters tırnakla kaçışla: `` `$5 ``.
```
:::

::: gorev Saniye çözücü
`$toplam = 3725` değerini saat, dakika ve saniyeye ayır ve şu biçimde yazdır. Tam bölme için `[math]::Floor` kullan.

```cikti
1 saat 2 dakika 5 saniye
```

```starter
$toplam = 3725

```

```test
eq(out, "1 saat 2 dakika 5 saniye\n", "3725 saniye")
ok(src.count("3725") == 1, "sonucu elle hesaplama")
```

```solution
$toplam = 3725
$saat = [math]::Floor($toplam / 3600)
$dakika = [math]::Floor(($toplam % 3600) / 60)
$saniye = $toplam % 60
"$saat saat $dakika dakika $saniye saniye"
```

```hint
`[math]::Floor($toplam / 3600)` saati verir. Kalan için `%`.
```
:::
