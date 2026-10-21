---
id: cm11
title: Yönlendirme · Çıktı ve Hata Akışları
summary: >, >>, 2> ve 2>&1; yönlendirme sırası hangi akışın nereye gittiğini değiştirir.
---

::: anlat Dosyaya yazmak ve eklemek
Normal çıktı stdout (1), hata çıktısı stderr (2) akışıdır. `>` stdout'u dosyaya yönlendirip mevcut içeriği değiştirir; `>>` sonuna ekler. Komutun hata kodu ise bu akışlardan ayrı bilgidir. Sadece stdout'u dosyaya almak stderr'i kendiliğinden toplamaz.

```cmd
@echo off
>"cm11 satirlar.txt" echo ILK
>>"cm11 satirlar.txt" echo IKINCI
type "cm11 satirlar.txt"
exit /b 0
```

Yönlendirmeyi satırın başına yazmak, echo sonundaki rakamın yanlışlıkla dosya tanıtıcısı sayılmasını da önler. Hedef dosyayı tırnakla; bu örneklerin dosyaları yalnız geçici çalışma klasöründedir. Kaynak: [cmd yönlendirme](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd).
:::

::: anlat Akışın o andaki hedefini kopyalarsın
`>"bir.txt" 2>&1` önce stdout'u dosyaya, sonra stderr'i stdout'un **o anki hedefine** bağlar. `2>&1 >"iki.txt"` önce stderr'i eski stdout'a bağlar; daha sonra stdout'u dosyaya taşıman stderr'i peşinden taşımaz. Bu nedenle sıra değişikliği aynı komutun gözlenen çıktısını değiştirir.

```cmd
@echo off
(
  echo NORMAL
  >&2 echo HATA
) >"cm11 birlikte.txt" 2>&1
type "cm11 birlikte.txt"
exit /b 0
```

Buradaki HATA yalnız bir eğitim mesajıdır; akış numarası bir cümlenin önemine bakmaz. Yazılım stderr'e bilgi de yazabilir. Otomasyonda çıkış kodunu ayrıca oku. Kaynak: [Microsoft: stdout ve stderr yönlendirme](https://learn.microsoft.com/en-us/troubleshoot/developer/visualstudio/cpp/language-compilers/redirecting-error-command-prompt).
:::

::: tahmin
Betik gerçek cmd.exe üzerinde çalışacak. Çıktıyı satır satır tahmin et; her blokta değişkenin ne zaman açıldığını veya metnin nereye gittiğini izle.

```cmd
@echo off
(
  echo OUT
  >&2 echo ERR
) >"cm11 bir.txt" 2>&1
echo BIR
type "cm11 bir.txt"
(
  echo OUT
  >&2 echo ERR
) 2>&1 >"cm11 iki.txt"
echo IKI
type "cm11 iki.txt"
exit /b 0
```

???

`BIR`, `OUT`, `ERR`, `ERR`, `IKI`, `OUT` yazılır. İlk ERR bir.txt içinden gelir. İkinci bloktaki ERR eski stdout'a bağlı olduğundan IKI yazılmadan önce görünür; iki.txt yalnız OUT içerir.
:::

::: gorev Değiştir, sonra iki kez ekle

İlk üç argümanı üç satır olarak cm11_rapor.txt dosyasına yaz. Birinci satır dosyanın eski içeriğini değiştirsin; ikinci ve üçüncü satır sona eklensin. Sonra dosyayı stdout'a yaz, stderr boş, çıkış 0. Eksik argüman boş satırdır. Veride Unicode, boşluk, &, %, ! ve ^ olabilir; çift tırnak ve CR/LF yoktur. Testler eski bir dosya da bırakarak üzerine yazma davranışını ölçer.

```starter
@echo off
exit /b 0
```

```test
from pathlib import Path
for args in [("bir","iki","uc"),("","x",""),("Ayşe Kaya","A&B","%ad%!^son")]:
    Path("cm11_rapor.txt").write_text("ESKI\nESKI\n", encoding="utf-8", newline="")
    r = calis(argv=list(args))
    beklenen = "".join(x + "\n" for x in args)
    eq((r["kod"],r["cikti"],r["hata"]), (0,beklenen,""), "üç satır stdout ve başarı")
    eq(Path("cm11_rapor.txt").read_text(encoding="utf-8"), beklenen, "eski içerik silinmiş, üç yeni satır kalmış")
eq(run(), "\n\n\n", "eksik argümanlar boş satır")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "a=%~1"
set "b=%~2"
set "c=%~3"
setlocal EnableDelayedExpansion
>"cm11_rapor.txt" echo(!a!
>>"cm11_rapor.txt" echo(!b!
>>"cm11_rapor.txt" echo(!c!
type "cm11_rapor.txt"
exit /b 0
```

```hint
Değerleri delayed expansion kapalıyken yakala. İlk echo için >, sonrakiler için >> kullan.
```

:::

::: gorev Üç yönlendirme düzeni

İlk argüman mod: ayri, birlesik veya ters. İkinci argüman normal mesaj, üçüncü hata mesajı. Önce cikti.txt ve hata.txt dosyalarını boşalt. İki mesajı sırayla stdout/stderr üreten bir bloktan yönlendir: ayri modda cikti.txt yalnız normal, hata.txt yalnız hata; birlesik modda cikti.txt iki mesaj, hata.txt boş; ters modda cikti.txt yalnız normal, hata.txt boş, hata mesajı çağıranın stdout'una gelsin. Her mesaj bir satırdır. Tüm modlarda gerçek stderr boş, çıkış 0. Argüman yoksa işlem yok.

```starter
@echo off
exit /b 0
```

```test
from pathlib import Path
for normal,hata in [("OUT","ERR"),("Ayşe & %!^","hata ! ve &"),("","")]:
    for mod in ("ayri","birlesik","ters"):
        r = calis(argv=[mod,normal,hata])
        eq(r["kod"], 0, "yönlendirme çıkış kodu")
        eq(r["hata"], "", "dış stderr boş")
        eq(r["cikti"], hata + "\n" if mod == "ters" else "", "ters sırada hata eski stdout'ta")
        eq(Path("cikti.txt").read_text(encoding="utf-8"), normal + "\n" + (hata + "\n" if mod == "birlesik" else ""), "stdout hedefi")
        eq(Path("hata.txt").read_text(encoding="utf-8"), hata + "\n" if mod == "ayri" else "", "stderr dosyası")
eq(run(), "", "argümansız işlem yok")
```

```solution
@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" exit /b 0
set "mod=%~1"
set "normal=%~2"
set "hata=%~3"
type nul >"cikti.txt"
type nul >"hata.txt"
setlocal EnableDelayedExpansion
if "!mod!"=="ayri" (
  (
    echo(!normal!
    >&2 echo(!hata!
  ) >"cikti.txt" 2>"hata.txt"
  exit /b 0
)
if "!mod!"=="birlesik" (
  (
    echo(!normal!
    >&2 echo(!hata!
  ) >"cikti.txt" 2>&1
  exit /b 0
)
if "!mod!"=="ters" (
  (
    echo(!normal!
    >&2 echo(!hata!
  ) 2>&1 >"cikti.txt"
)
exit /b 0
```

```hint
Akış kopyalama anını düşün: >dosya 2>&1 ile 2>&1 >dosya aynı değildir.
```

:::
