---
id: cm09
title: for /f · Satırlar, Tokenlar ve Dosyalar
summary: tokens, delims, eol, skip ve usebackq ile basit metni ayır; boş alanların kaybolduğunu gör.
---

::: anlat Dosya adı mı, metin mi, komut mu?
`for /f`, satırları tokenlara ayırır; varsayılan olarak boş satırları atlar ve ilk boşluk/tab ayrılmış tokenı alır. `usebackq`, çift tırnaklı kısmı dosya adı olarak kullanmana izin verir. Aynı seçenekte tek tırnak literal metin, ters tırnak ise komut çıktısı anlamına gelir. Bu derste dosya adlarını açıkça tırnaklıyoruz.

```cmd
@echo off
>"cm09_ornek.txt" echo u1;fail;web01
for /f "usebackq tokens=1,3 delims=;" %%A in ("cm09_ornek.txt") do echo(%%A:%%B
exit /b 0
```

`tokens=1,3` ilk seçileni A'ya, ikinci seçileni B'ye verir; B üçüncü sütunun değeridir. `skip=1` dosyanın ilk fiziksel satırını atlar. `eol=#` yorum başlangıç karakterini seçer. Kaynak: [for /f seçenekleri](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for).
:::

::: anlat Ayraç kümesi CSV ayrıştırıcısı değildir
`delims=;|` birden fazla karakterli tek ayraç değil, noktalı virgül **veya** dik çizgi karakterlerinden oluşan bir ayraç kümesidir. Bitişik ayraçlar boş sütun korumaz. `a;;c` satırında ikinci token c olur. Tırnaklı CSV alanları, gömülü ayraç ve çok satırlı alanlar bu araçla genel olarak çözülemez.

```cmd
@echo off
for /f "tokens=2,* delims=|" %%A in ("id|alice|bir|iki") do echo(%%A:%%B
exit /b 0
```

Sondaki `*`, son istenen tokenın ardından kalan parçayı ek değişkene verir; burada B `bir|iki` olur. Ancak kalan parçanın **başındaki ayraçlar da atlanır**: `1|alice||bir` satırı `tokens=2,*` ile A=`alice`, B=`bir` üretir; B=`|bir` olmaz. İlk dolu parça başladıktan sonraki iç ayraçlar korunur. Bu yüzden ikinci görevin ayrıntı alanı | ile başlamaz; içteki | işaretlerine izin verilir.

Görev verileri özellikle basit biçimde sınırlandırılmıştır. Gerçek CSV/JSON için o biçimin ayrıştırıcısını seçmek gerekir. Kaynak: [Token seçimi ve kalan parça](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for).
:::

::: tahmin
Betik gerçek cmd.exe üzerinde çalışacak. Çıktıyı satır satır tahmin et; her blokta değişkenin ne zaman açıldığını veya metnin nereye gittiğini izle.

```cmd
@echo off
setlocal DisableDelayedExpansion
>"cm09_tahmin.txt" (
  echo baslik
  echo #yorum
  echo user1;fail;web01
  echo user2;;web02
  echo(
  echo user3;ok;web03
)
for /f "usebackq skip=1 eol=# tokens=1,2 delims=;" %%A in ("cm09_tahmin.txt") do echo(%%A:%%B
exit /b 0
```

???

`user1:fail`, `user2:web02`, `user3:ok` yazılır. Başlık, yorum ve boş satır işlenmez. user2 satırındaki boş alan korunmadığından web02 ikinci token olur.
:::

::: gorev Birinci ve üçüncü token

İlk argüman giriş dosyası; yoksa kayitlar.txt kullan. İlk fiziksel satırı atla, # ile başlayan yorumları ve boş satırları geç. Noktalı virgülle ayrılmış tokenların 1. ve 3.'sünü `birinci:ucuncu` biçiminde sırayla yaz. İşlenen veri satırlarında en az üç dolu token vardır; tokenlarda noktalı virgül, çift tırnak, CR/LF yoktur. Boşluk, Unicode, %, !, &, ^ korunmalı. Dosya yalnız görev geçici klasöründe hazırlanır; çıkış 0.

```starter
@echo off
exit /b 0
```

```setup
from pathlib import Path
Path("kayitlar.txt").write_text("id;sonuc;host\n#yorum\nuser1;fail;web01\nuser2;ok;db01\n", encoding="utf-8", newline="")
```

```test
from pathlib import Path
cases = [[], [("u","ok","web")], [("Ayşe Kaya","fail","sunucu 2"),("A&B","ok","bir!iki^%")]]
for i, rows in enumerate(cases):
    path = Path(f"cm09 veri {i}.txt")
    data = "baslik;sonuc;host\n#yorum;asla;alma\n\n" + "".join(";".join(row) + "\n" for row in rows)
    path.write_text(data, encoding="utf-8", newline="")
    beklenen = "".join(f"{a}:{c}\n" for a,b,c in rows)
    eq(run(argv=[str(path)]), beklenen, "0/1/2 veri satırı; yorum, başlık ve özel veri")
eq(run(), "user1:web01\nuser2:db01\n", "varsayılan dosya")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "dosya=%~1"
if not defined dosya set "dosya=kayitlar.txt"
for /f "usebackq skip=1 eol=# tokens=1,3 delims=;" %%A in ("%dosya%") do (
  set "bir=%%A"
  set "uc=%%B"
  setlocal EnableDelayedExpansion
  echo(!bir!:!uc!
  endlocal
)
exit /b 0
```

```hint
usebackq dosya adını tırnaklayabilmeni sağlar. tokens=1,3 için ikinci çıktı değişkeni %%B olur.
```

:::

::: gorev İkinci token ve kalan parça

İlk argüman giriş dosyası; yoksa ayrinti.txt kullan. İlk satır başlık, # ile başlayan satırlar yorumdur. Veri `id|actor|ayrinti` biçimindedir; actor ve ayrıntı doludur. Ayrıntı **| ile başlamaz**, fakat içindeki başka | işaretleri korunmalıdır. `actor=DEGER;rest=KALAN` yaz. `tokens=2,*` ile kalan parçadaki iç ayraçları koru. Boş satırları atla, sıra korunsun, çıkış 0. Bu sözleşme tırnaklı CSV kapsamaz.

```starter
@echo off
exit /b 0
```

```setup
from pathlib import Path
Path("ayrinti.txt").write_text("id|actor|detail\n#yorum\n1|alice|bir|iki\n", encoding="utf-8", newline="")
```

```test
from pathlib import Path
for i, rows in enumerate([[], [("1","alice","tek")], [("9","Ayşe Kaya","bir|iki|uc"),("10","A&B!%","yol^son"),("11","can","ic||cift|son")]]):
    path = Path(f"cm09 ayrinti {i}.txt")
    path.write_text("id|actor|detail\n#yorum|gec|gec\n\n" + "".join("|".join(row) + "\n" for row in rows), encoding="utf-8", newline="")
    eq(run(argv=[str(path)]), "".join(f"actor={a};rest={r}\n" for _,a,r in rows), "kalan parçadaki ayraçlar ve satır sayısı")
eq(run(), "actor=alice;rest=bir|iki\n", "varsayılan dosya")
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "dosya=%~1"
if not defined dosya set "dosya=ayrinti.txt"
for /f "usebackq skip=1 eol=# tokens=2,* delims=|" %%A in ("%dosya%") do (
  set "actor=%%A"
  set "rest=%%B"
  setlocal EnableDelayedExpansion
  echo(actor=!actor!;rest=!rest!
  endlocal
)
exit /b 0
```

```hint
tokens=2,* sonrasında %%A ikinci token, %%B geri kalandır; delims yalnız | olsun.
```

:::
