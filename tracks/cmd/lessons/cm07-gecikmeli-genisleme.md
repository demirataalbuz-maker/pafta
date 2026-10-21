---
id: cm07
title: Bloklar · Erken ve Gecikmeli Genişleme
summary: %var% ile !var! aynı anda okunmaz; blok içinde değişen sayıyı izle, ünlem içeren veriyi koru.
---

::: anlat Blok okunurken, komut çalışırken
CMD bir parantez bloğunu okurken `%n%` yerlerine o andaki değeri koyabilir. Blok içindeki sonraki `set` işlemi bu önceden hazırlanmış metni değiştirmez. `setlocal EnableDelayedExpansion` sonrasında `!n!`, komut yürütülürken güncel değeri alır. Bu yüzden tek satırda veya blokta “az önce değiştirdim, neden eski değer geldi?” sorusu doğabilir.

```cmd
@echo off
setlocal EnableDelayedExpansion
set "n=2"
(
  set /a n+=1 >nul
  echo erken=%n%
  echo guncel=!n!
)
exit /b 0
```

Buradaki `set /a n+=1` aritmetik işlemi değişken adını kendi okur; bloktaki `%n%` açılımına ihtiyaç duymaz. Betik yerel değişkenlerle çalışır. Kaynaklar: [cmd /v ve gecikmeli açılım](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), [setlocal](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setlocal).
:::

::: anlat Ünlem de veri olabilir
Gecikmeli genişleme açıkken doğrudan okunan bir `!` işareti değişken sınırı sanılabilir. Parola, etiket veya dosya adı gibi bir verinin içinde ünlem bulunabileceğini düşün. Veri alırken `DisableDelayedExpansion`, değeri yazdıracağın ayrı komutta kontrollü `EnableDelayedExpansion` kullanmak bu dersin kalıbıdır.

```cmd
@echo off
setlocal DisableDelayedExpansion
set "etiket=LAB!KAYIT"
setlocal EnableDelayedExpansion
echo(!etiket!
endlocal
exit /b 0
```

Değişken değerinden gelen ünlem bu yazdırma aşamasında yeniden değişken açılımı gibi taranmaz. Bu kalıp her CMD bağlamını sihirli biçimde güvenli yapmaz: `call`, yeniden yorumlanan komut metni ve boru gibi bağlamlar ayrıca değerlendirilmelidir. Görevler tek satır veriyi komut olarak çalıştırmadan geri yazar. Kaynak: [setlocal açılım kapsamı](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setlocal).
:::

::: tahmin
Betik gerçek cmd.exe üzerinde çalışacak. Çıktıyı satır satır tahmin et; her blokta değişkenin ne zaman açıldığını veya metnin nereye gittiğini izle.

```cmd
@echo off
setlocal EnableDelayedExpansion
set "n=10"
(
  set "n=11"
  echo yuzde=%n%
  echo unlem=!n!
)
echo disarida=%n%
exit /b 0
```

???

`yuzde=10`, `unlem=11`, `disarida=11` yazılır. Yüzdeli değer blok okunurken 10 idi; ünlemli değer set işleminden sonra 11 olur. Dışarıdaki satır yeni okunduğundan yüzdeyle de 11 görür.
:::

::: gorev Blokta bir artır

İlk argüman 0–10000 aralığında bir onluk integer'dır; argüman yoksa 0 kullan. Bir parantez bloğunda önce `once=N`, sayıyı bir artırdıktan sonra `blok=N+1` yazdır. Blok bittikten sonra `sonra=N+1` yazdır. Gereksiz aritmetik çıktısı olmasın; çıkış 0. Testler farklı N değerleriyle güncel değeri gerçekten kullanıp kullanmadığını sınar.

```starter
@echo off
exit /b 0
```

```test
for n in (0, 1, 2, 5, 9999, 10000):
    eq(run(argv=[str(n)]), f"once={n}\nblok={n + 1}\nsonra={n + 1}\n", "blokta eski ve güncel değer")
eq(run(), "once=0\nblok=1\nsonra=1\n", "argümansız başlangıç")
```

```solution
@echo off
setlocal EnableDelayedExpansion
set "n=%~1"
if not defined n set "n=0"
(
  echo once=%n%
  set /a n+=1 >nul
  echo blok=!n!
)
echo sonra=%n%
exit /b 0
```

```hint
Blok içinde set sonrasındaki echo için !n! gerekir; set /a çıktısını >nul ile sustur.
```

:::

::: gorev Veriyi olduğu gibi geri ver

Bu SET /P alıştırmasında girdi satırı en fazla 200 karakterdir. Native SET /P'nin tampon sınırı bulunduğundan bu kalıp genel uzun satır okuyucusu değildir.

Standart girdiden bir satır oku ve aynı satırı bir yeni satırla geri yaz. Boş satır da kabul edilsin. Veride boşluk, Unicode, yüzde, ünlem, ampersand ve şapka bulunabilir; çift tırnak ve satır içi CR/LF yoktur. Metni komut olarak yeniden yorumlama. `set /p` öncesi değişkeni temizle; veri alınırken gecikmeli açılım kapalı olsun. Çıkış 0.

```starter
@echo off
exit /b 0
```

```test
for metin in ("", "x", "iki kelime", "Ayşe ve çağrı", "yuzde%DEGISKEN%", "bir!iki!uc", "A&B ^ C", "!bas %son% & ^ bitis!"):
    eq(run(stdin=metin + "\n"), metin + "\n", "bir satırlık veri aynen korunmalı")
eq(run(stdin="ilk\nikinci\n"), "ilk\n", "yalnız ilk satır okunur")
eq(run(stdin="ş"*200+"\n"), "ş"*200+"\n", "200 karakterlik girdi sözleşmesi")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "metin="
set /p "metin="
setlocal EnableDelayedExpansion
echo(!metin!
endlocal
exit /b 0
```

```hint
Önce delayed expansion kapalıyken set /p, sonra ayrı kapsamda echo(!metin! kullan.
```

:::
