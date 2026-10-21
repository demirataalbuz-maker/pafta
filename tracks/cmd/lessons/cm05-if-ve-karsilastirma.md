---
id: cm05
title: if, Tanımlılık ve Sayısal Kararlar
summary: if/not/defined, /i ile harf duyarlılığı, string == ile EQU/GEQ; sıfır, negatif ve eşik komşularını ayırmak.
---

::: anlat Hangi soruyu karşılaştırıyorsun?
`if "%pafta_ad%"=="admin" ...` iki metni karşılaştırır; `/i` verilmedikçe harf farkı önemlidir. `if /i "%pafta_ad%"=="admin" ...` Admin gibi ASCII harf varyasyonlarını da kabul eder. Değerin boş olması if ifadesini bozmasın diye tırnaklı biçimi koruyoruz; burada veri içinde çift tırnak yoktur.

`if defined pafta_ad` ise belirli bir metni değil, değişkenin tanımlı olup olmadığını sorar. `set "pafta_ad="` tanımı temizlediğinden sonrasında false olur. `if not defined` bunun tersini ister. Boşluk veya `0` dolu değerdir; “yok” sayılmaz. Bu kontrolle sayısal sıfırı aynı anlamda kullanmak hata olur.

Komut uzantıları açıkken EQU, NEQ, LSS, LEQ, GTR, GEQ karşılaştırmaları da vardır. Bu derste tırnaksız canonical tamsayı operandlarıyla sayısal karşılaştırma yapacağız: `if 10 GEQ 10 ...`. `"01"=="1"` bir metin eşitliği olarak farklıdır; `if 01 EQU 1` sayısal eşitlikte aynı kabul edilebilir. Her girdi metninin otomatik olarak güvenli bir sayısal operand olduğunu varsayma.
:::

::: anlat Sınıflandırmada sınırın iki tarafı
“En az 10” ile “10'dan büyük” farklı gereksinimlerdir. GEQ sınırı dahil, GTR hariç tutar; LSS küçük, LEQ küçük veya eşittir. Bir sınıflandırıcı için 9, 10 ve 11'i denemek, yalnız 99 gibi uzak bir olumlu örneğe bakmaktan daha fazla hata yakalar. Negatif, sıfır ve 1 de farklı köşelerdir.

Parantezli if/else düzeninde `) else (` aynı satırda durmalıdır. Bu paftadaki sayısal sınıflandırma, veri giriş sözleşmesi olarak başında gereksiz sıfır olmayan ondalık tamsayı alır; örneğin -1, 0, 10. İfadeler, metin ve başka kabuk karakterleri sayısal göreve verilmez. Tam doğrulama ve güvenli genel argüman ayrıştırma daha ileri çalışmadır; burada sayısal dal mantığını öğreniyoruz.

if gövdesinde echo ile karar yazdırabilir, ardından exit /b 0 ile normal akışı bitirebilirsin. Eksik girdi kendi hata dalıyla kod 2 döner; bu sıradan beklenen hata testini ilk varsayılan çalışmayı başarısız bırakmadan calis ile sınayacağız. Sayısal görevlerde negatif sonucu hata koduyla karıştırma: -1 geçerli bir girdidir.

Kaynak (21 Ekim 2026): [if: not, defined, /i ve sayısal karşılaştırmalar](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if).
:::

::: tahmin

Aşağıdaki gerçek batch betiğini cmd.exe çalıştıracak. Çıktıyı satır satır tahmin et; komutların kendisini değil, ekrana yazılan metni düşün.

```cmd
@echo off
set "pafta_ad=Admin"
if "%pafta_ad%"=="admin" (echo tam-esit) else echo farkli
if /i "%pafta_ad%"=="admin" (echo harf-esnek) else echo esnek-degil
if 10 GEQ 10 echo sinir-dahil
exit /b 0
```

???

Sırasıyla `farkli`, `harf-esnek`, `sinir-dahil`. İlk karşılaştırma harf farkını görür; /i ASCII varyasyonunu kabul eder. GEQ eşit 10 değerini dışlamaz.

:::

::: gorev Tanım ve kullanıcı sınıfı

İlk argümanı pafta_ad değerine al. Tanımlıysa ilk satır `VAR`, eksik/boşsa `YOK` olsun. İkinci satırda /i ile tam admin metnine eşitse `YONETICI`, diğer durumda `DIGER` yaz. Her durumda kod 0. Boşluk, 0 ve özel karakter içeren dolu argümanlar VAR sayılır; veri içinde çift tırnak yoktur.

```starter
@echo off
set "pafta_ad=%~1"
echo VAR
echo YONETICI
exit /b 0
```

```meta
argv: admin
```

```test
eq(out, 'VAR\nYONETICI\n', "varsayılan admin")
for args, expected in [([], 'YOK\nDIGER\n'),([''], 'YOK\nDIGER\n'),(['Admin'], 'VAR\nYONETICI\n'),(['ADMIN'], 'VAR\nYONETICI\n'),(['administrator'], 'VAR\nDIGER\n'),(['0'], 'VAR\nDIGER\n'),([' '], 'VAR\nDIGER\n'),(['A&B%!^'], 'VAR\nDIGER\n')]:
    r = calis(argv=args)
    eq(r['kod'], 0, 'sınıflandırma başarıyla döner')
    eq(r['cikti'], expected, 'tanım ve tam metin')
    eq(r['hata'], '', 'girdi korunur')
```

```solution
@echo off
set "pafta_ad=%~1"
if defined pafta_ad (echo VAR) else echo YOK
if /i "%pafta_ad%"=="admin" (echo YONETICI) else echo DIGER
exit /b 0
```

```hint
defined boş olmayan tanımı sorar; ikinci karar tam metin eşitliği ve /i kullanır.
```

:::

::: gorev On eşiğinde üç sınıf

İlk argüman canonical ondalık tamsayıdır (-100000..100000; başta gereksiz sıfır yok). 10’dan küçükse `DUSUK`, eşitse `ESIT`, büyükse `YUKSEK` yaz ve 0 dön. Eksik/boş argümanda yalnız `HATA: sayi gerekli` yazıp kod 2 dön. Sayısal sözleşme dışındaki ifadeleri çözümleme; bunlar bu göreve verilmez.

```starter
@echo off
echo YUKSEK
exit /b 0
```

```meta
argv: 10
```

```test
eq(out, 'ESIT\n', "varsayılan eşit sınır")
for n, expected in [(-1,'DUSUK'),(0,'DUSUK'),(1,'DUSUK'),(9,'DUSUK'),(10,'ESIT'),(11,'YUKSEK'),(100000,'YUKSEK'),(-100000,'DUSUK')]:
    r = calis(argv=[str(n)])
    eq(r['kod'], 0, 'negatif de geçerli bir tamsayı')
    eq(r['cikti'], expected+'\n', 'eşik sınıfı '+str(n))
for args in ([],['']):
    r = calis(argv=args)
    eq(r['kod'], 2, 'eksik sayı kodu')
    eq(r['cikti'], 'HATA: sayi gerekli\n', 'eksik mesajı')
```

```solution
@echo off
if "%~1"=="" goto eksik
set "pafta_n=%~1"
if %pafta_n% LSS 10 (
    echo DUSUK
    exit /b 0
)
if %pafta_n% EQU 10 (
    echo ESIT
    exit /b 0
)
echo YUKSEK
exit /b 0
:eksik
echo HATA: sayi gerekli
exit /b 2
```

```hint
Eksik girdi kararından sonra sayısal karşılaştırmaya geç. 9/10/11 üç ayrı tanıktır.
```

:::
