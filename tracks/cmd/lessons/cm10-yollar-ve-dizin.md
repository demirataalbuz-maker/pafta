---
id: cm10
title: Yollar · Argüman, Betik ve Çalışma Dizini
summary: %~f1, %~nx1 ve %~dp0 aynı şeyi anlatmaz; cd /d ve pushd/popd ile dizin bağlamını yönet.
---

::: anlat Göreli yol hangi dizine göre?
`%~f1`, ilk argümanı tam yola açar; dosyanın var olduğunu kanıtlamaz. `%~nx1` yalnız adı ve uzantıyı verir. `%~dp0`, çalışan batch dosyasının sürücü ve klasör kısmıdır. Çalışma dizini farklı olsa bile betiğin yanındaki bir dosyayı bulmak için `%~dp0` ile kurulan yol kullanılabilir.

```cmd
@echo off
setlocal DisableDelayedExpansion
if exist "%~f0" echo kendi_betigi=var
if exist "%~dp0." echo betik_dizini=var
exit /b 0
```

Yolları tırnaklamak boşluk ve özel karakterlerin komut yapısı sanılmasını önler. Bu yolda tüm yazma örnekleri koşucunun oluşturduğu geçici çalışma alanındadır. Kaynak: [Batch parametre değiştiricileri](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/call).
:::

::: anlat Dizine gir ve geri dön
`cd /d "yol"` hem sürücüyü hem dizini değiştirir. `cd` tek başına başka sürücüye her bağlamda geçiş yapmaz. `pushd "yol"` önce mevcut dizini yığına koyar, hedefe geçer; `popd` geri döner. Bir alt adımın göreli yollarını asıl çağıranın dizininden ayırmak için kullanışlıdır.

```cmd
@echo off
setlocal DisableDelayedExpansion
if not exist "cm10 ornek" mkdir "cm10 ornek"
pushd "cm10 ornek"
>"not.txt" echo YEREL
popd
type "cm10 ornek\not.txt"
exit /b 0
```

Başarısız pushd sonrasında yanlış klasörde işlem yapma: hata kodunu kontrol et. İçeride başka bir hata olsa da geri dönüşü planla. Bu görevler yerel geçici dizin kullanır; ağ sürücüsü eşleme veya gerçek kullanıcı klasörlerini taşıma/silme yapmaz. Kaynaklar: [cd /d](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cd), [pushd/popd](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/pushd).
:::

::: tahmin
Betik gerçek cmd.exe üzerinde çalışacak. Çıktıyı satır satır tahmin et; her blokta değişkenin ne zaman açıldığını veya metnin nereye gittiğini izle.

```cmd
@echo off
setlocal DisableDelayedExpansion
if not exist "cm10 alt" mkdir "cm10 alt"
>"cm10 alt\isaret.txt" echo DIZIN
set "once=%CD%"
pushd "cm10 alt"
type "isaret.txt"
popd
if "%CD%"=="%once%" echo geri=evet
exit /b 0
```

???

`DIZIN` ve `geri=evet` yazılır. type iç dizindeki göreli dosyayı açar; popd ardından başlangıç dizinine dönülmüştür.
:::

::: gorev Yol kartı

İlk argüman bir yoldur. `tam=...` satırında tam yolunu, `ad=...` satırında yalnız dosya adı ve uzantısını, `betik=...` satırında betiğin klasörünü yaz. Dosyanın var olması gerekmez. Argüman yoksa sessizce çıkış 0. Yollarda boşluk, Unicode, &, %, ! ve ^ olabilir; çift tırnak ve CR/LF yoktur. Tam yol mevcut çalışma dizinine göre çözülmeli; çıkış 0.

```starter
@echo off
exit /b 0
```

```test
from pathlib import Path
import os
for yol in ["rapor.txt", "alt klasor\iki.uzanti.txt", "Ayşe &!%^.log", str(Path.cwd() / "mutlak klasor" / "ornek.bin")]:
    result = calis(argv=[yol])
    eq(result["kod"], 0, "başarılı kart")
    lines = result["cikti"].splitlines()
    eq(len(lines), 3, "üç kart satırı")
    if len(lines) == 3:
        kart = dict(line.split("=",1) for line in lines)
        eq(os.path.normcase(kart["tam"]), os.path.normcase(os.path.abspath(yol)), "tam yol")
        eq(kart["ad"], os.path.basename(yol), "ad ve son uzantı")
        eq(Path(kart["betik"]).resolve(), Path.cwd().resolve(), "betik çalışma alanındaki gerçek .cmd dosyası")
eq(run(), "", "argümansız işlem yok")
```

```solution
@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" exit /b 0
set "tam=%~f1"
set "ad=%~nx1"
set "betik=%~dp0"
setlocal EnableDelayedExpansion
echo(tam=!tam!
echo(ad=!ad!
echo(betik=!betik!
exit /b 0
```

```hint
Dönüştürmeleri delayed expansion kapalıyken tırnaklı set ile al; yazdırırken !tam! gibi aç.
```

:::

::: gorev Geçici dizin ziyareti

İlk argümandaki geçici hedefe pushd yap, isaret.txt içeriğini stdout'a yaz, popd ile başlangıca dön. Dönüşte başlangıç klasörüne donus.txt içine DONDU satırı yaz ve stdout'a `geri=EVET` ekle. Argüman yoksa işlem yok, çıkış 0. Hedef yoksa stderr `dizin_yok`, çıkış 2; hedef var ama işaret yoksa geri dönüp stderr `isaret_yok`, çıkış 4. Başarılı çıkış 0. Yalnız testlerin oluşturduğu yerel hedefleri kullan; silme/taşıma yok.

```starter
@echo off
exit /b 0
```

```setup
from pathlib import Path
for name, content in [("hedef A", "ilk\n"),("hedef &!%^ B", "Ayşe & kayıt!%^\n")]:
    p = Path(name)
    p.mkdir(exist_ok=True)
    (p / "isaret.txt").write_text(content, encoding="utf-8", newline="")
Path("bos hedef").mkdir(exist_ok=True)
```

```test
from pathlib import Path
for hedef, icerik in [("hedef A","ilk\n"),("hedef &!%^ B","Ayşe & kayıt!%^\n")]:
    r = calis(argv=[hedef])
    eq(r["kod"], 0, "hedefe gidip dön")
    eq(r["cikti"], icerik + "geri=EVET\n", "doğru dizindeki dosya")
    eq(r["hata"], "", "başarıda hata yok")
    eq(Path("donus.txt").read_text(encoding="utf-8"), "DONDU\n", "dönüşte başlangıç dizinine yaz")
    ok(not Path(hedef,"donus.txt").exists(), "dönüş dosyası hedefte olmamalı")
r = calis(argv=["olmayan hedef"])
eq((r["kod"],r["cikti"],r["hata"]), (2,"","dizin_yok\n"), "hedef hatası")
r = calis(argv=["bos hedef"])
eq((r["kod"],r["cikti"],r["hata"]), (4,"","isaret_yok\n"), "içerik eksikliği ayrı hata")
eq(run(), "", "argümansız işlem yok")
```

```solution
@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" exit /b 0
set "baslangic=%CD%"
pushd "%~1" 2>nul
if errorlevel 1 (
  >&2 echo dizin_yok
  exit /b 2
)
if not exist "isaret.txt" (
  popd
  >&2 echo isaret_yok
  exit /b 4
)
type "isaret.txt"
popd
if not "%CD%"=="%baslangic%" exit /b 3
>"donus.txt" echo DONDU
echo geri=EVET
exit /b 0
```

```hint
Başarısız pushd sonrası type çalıştırma; hedefte dosya eksikse bile popd yapıp dön.
```

:::
