---
id: cm08
title: for · Öğeler ve Dahil Sayı Aralığı
summary: Batch dosyasında %%I, konsolda %I; for /l başlangıç, adım ve dahil bitişiyle çalışır.
---

::: anlat Tek yüzde ile çift yüzdeyi karıştırma
Komut istemine doğrudan yazılan `for` değişkeni `%I` biçimindedir; `.cmd` dosyasında `%%I` yazılır. Pafta kodu batch dosyası olarak çalıştırdığı için bu yolda çift yüzde kullanacaksın. `%%~I`, seçilen öğenin dış tırnaklarını kaldırır; böylece boşluklu öğeyi tek parça alabilirsin.

```cmd
@echo off
setlocal DisableDelayedExpansion
for %%I in ("web01" "iki kelime") do echo(%%~I
exit /b 0
```

Döngü değişkenleri büyük-küçük harfe duyarlıdır. Dosya kümeleriyle de çalışabilirler; ancak burada yalnız açıkça verilen öğeleri kullanıyoruz. Kaynak: [for değişkenleri ve batch biçimi](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for).
:::

::: anlat Sayısal aralıkta bitiş dahil
`for /l %%I in (baslangic,adim,bitis)` sayılar üretir. Ulaşılabiliyorsa bitiş sayısı da gelir. `(1,2,6)` ise 1, 3, 5 üretir; aralığı aşan 7 üretilmez. Negatif adım azalan aralık içindir. Adımın sıfır olması durmayan bir döngüye yol açabileceğinden bu görevlerin sözleşmesi sıfırı dışlar.

```cmd
@echo off
for /l %%I in (3,-1,1) do echo(%%I
exit /b 0
```

Pozitif adımda başlangıç bitişten büyükse sıfır, eşitse bir sonuç vardır. Testlerde bu sınır durumları ayrıca çalışır. Gövdedeki sayaç için `set /a adet+=1` kullanabilirsin; blok içinde yazdıracağın değişen değerin açılım anını önceki dersten hatırla. Kaynak: [for /l aralığı](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for).
:::

::: tahmin
Betik gerçek cmd.exe üzerinde çalışacak. Çıktıyı satır satır tahmin et; her blokta değişkenin ne zaman açıldığını veya metnin nereye gittiğini izle.

```cmd
@echo off
setlocal EnableDelayedExpansion
set "n=0"
for /l %%I in (2,2,6) do (
  set /a n+=1 >nul
  echo(%%I
)
echo adet=!n!
exit /b 0
```

???

`2`, `4`, `6`, `adet=3` yazılır. Bitiş 6 dahil olduğu için üç tur vardır; sayaç artışlarının sayısal çıktıları >nul ile gizlenmiştir.
:::

::: gorev Aralığı üret

Üç argüman başlangıç, sıfır olmayan adım ve bitiştir. Argüman yoksa 1,1,3 kullan. Değerler -20–20 aralığında onluk integer; adımın mutlak değeri 1–5 arasındadır. for /l aralığını her sayıyı ayrı satırda yazdır; başka çıktı verme, çıkış 0. Ulaşılamayan bitişi zorla ekleme.

```starter
@echo off
exit /b 0
```

```test
for bas, adim, son in [(1,1,0),(1,1,1),(1,1,2),(2,2,6),(2,2,7),(3,-1,4),(3,-1,3),(3,-1,2),(5,-2,-1),(-2,1,2)]:
    beklenen = "".join(f"{n}\n" for n in range(bas, son + (1 if adim > 0 else -1), adim))
    eq(run(argv=[str(bas),str(adim),str(son)]), beklenen, "sıfır/bir tur, bitiş ve yön")
eq(run(), "1\n2\n3\n", "varsayılan aralık")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "bas=%~1"
set "adim=%~2"
set "son=%~3"
if not defined bas set "bas=1"
if not defined adim set "adim=1"
if not defined son set "son=3"
for /l %%I in (%bas%,%adim%,%son%) do echo(%%I
exit /b 0
```

```hint
for /l üçüncü değeri dahil kabul eder; Python range gibi son değeri ayrıca azaltma.
```

:::

::: gorev İki tırnaklı öğeyi koru

İlk iki argümanı for öğeleri olarak sırayla gez. Her öğe için `[değer]`, sonra `adet=2` yazdır. Argüman eksikse o öğe boş metindir; her zaman iki öğe vardır. Veride boşluk, Unicode, &, %, ! ve ^ olabilir; çift tırnak ve satır sonu yoktur. Veri alınırken delayed expansion kapalı kalsın; yazdırırken ayrı yerel kapsamda değişken açılımı kullan. Çıkış 0.

```starter
@echo off
exit /b 0
```

```test
for a,b in [("web01","db01"),("iki kelime","Ayşe"),("A&B","bir!iki"),("%AD%","etiket^son"),("","dolu"),("dolu","")]:
    eq(run(argv=[a,b]), f"[{a}]\n[{b}]\nadet=2\n", "öğe sınırları ve özel veri")
eq(run(), "[]\n[]\nadet=2\n", "iki eksik argüman iki boş öğe")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "adet=0"
for %%I in ("%~1" "%~2") do (
  set "oge=%%~I"
  set /a adet+=1 >nul
  setlocal EnableDelayedExpansion
  echo([!oge!]
  endlocal
)
echo adet=%adet%
exit /b 0
```

```hint
for kümesindeki her argümanı tırnakla; %%~I ile tırnağı kaldırıp delayed expansion kapalıyken değişkene al.
```

:::
