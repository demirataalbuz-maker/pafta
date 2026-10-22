---
id: bs17
title: find, xargs ve Dosya Sistemi
summary: find ile ada, türe, boyuta ve zamana göre aramak, -exec ile + farkı, boşluklu adlar için -print0 ve xargs -0, stat, du ve dosya izinleri.
kazanim: LPIC1 103.3, LPIC1 103.4, LPIC1 104.5, LPIC1 104.7
---

::: anlat find: dosya sisteminde sorgu
`find başlangıç [koşullar] [eylem]` bir klasör ağacını gezer ve koşulları sağlayan her girdi için eylemi uygular. Koşullar yan yana yazılınca VE olur:

| Koşul | Anlamı |
|---|---|
| `-name '*.log'`, `-iname` | ada göre (glob; büyük-küçük harf duyarlı / duyarsız) |
| `-type f`, `-type d` | dosya / klasör |
| `-size +1M`, `-size -10k` | 1 MiB'tan büyük / 10 KiB'tan küçük |
| `-mtime -7`, `-mmin -30` | son 7 günde / 30 dakikada değişmiş |
| `-newer dosya` | o dosyadan daha yeni |
| `-maxdepth 1` | alt klasörlere inme |
| `-path '*/eski/*' -prune -o ...` | bir klasörü tamamen atla |
| `! -name ...`, `-o` | değil, veya |

```bash
mkdir -p proje/src proje/eski
printf 'a\n' > proje/src/main.sh
printf 'b\nc\n' > proje/src/yardimci.sh
printf 'd\n' > proje/eski/eski.sh
printf 'not\n' > proje/BENIOKU.txt
find proje -type f -name '*.sh' | sort
find proje -path '*/eski' -prune -o -type f -name '*.sh' -print | sort
find proje -maxdepth 1 -type f
```

### Eylemler: -exec ve xargs
`-exec komut {} \;` her dosya için komutu **ayrı ayrı** çalıştırır; `-exec komut {} +` dosyaları toplayıp komutu olabildiğince az kez çalıştırır (çok daha hızlıdır):

```bash
mkdir -p proje/src && printf 'a\n' > proje/src/main.sh && printf 'b\nc\n' > proje/src/yardimci.sh   #! örnek dosyalar
find proje -name '*.sh' -exec wc -l {} + | sort -k2
```

`find`'ın çıktısını başka bir komuta vermenin güvenli yolu, adları **sıfır baytıyla** ayırmaktır. Boşluk, satır sonu ya da tırnak içeren adlar bu yolla bozulmaz:

```bash
mkdir -p proje/src && printf 'a\n' > proje/src/main.sh && printf 'b\nc\n' > proje/src/yardimci.sh   #! örnek dosyalar
printf 'x\n' > "proje/boşluklu ad.sh"
find proje -name '*.sh' -print0 | xargs -0 wc -l | tail -n 1
find proje -name '*.sh' -print0 | while IFS= read -r -d '' f; do
    printf '%s\n' "${f##*/}"
done | sort
```

### Boyut, ayrıntı ve izinler
```bash
mkdir -p proje/src && printf 'a\n' > proje/src/main.sh      #! örnek dosya
stat -c '%n %s bayt' proje/src/main.sh      #! ad ve boyut
du -sh proje                                 #! klasörün toplam boyutu
ls -l proje/src
```

`ls -l` çıktısının başındaki `-rwxr-xr--`: tür, ardından sahibin, grubun ve diğerlerinin okuma (r), yazma (w), çalıştırma (x) izinleri. `chmod 750 dosya` sayısal biçimdir: 7 = rwx, 5 = r-x, 0 = ---; `chmod u+x dosya` sembolik biçimdir.

> [!TUZAK]
> `for f in $(find ...)` ya da `for f in $(ls)` boşluklu adları parçalar ve glob karakterlerini genişletir. Dosya listesini her zaman `-print0` ile `xargs -0`'a ya da `while IFS= read -r -d ''` döngüsüne ver.

> [!NOT]
> Git Bash Windows'un NTFS dosya sistemi üzerinde çalıştığı için `chmod` izinleri ancak kısmen taklit edilir. İzin dersleri gerçek bir Linux makinede tam anlamıyla denenir.
:::

::: tahmin
Kurulumdaki klasör ağacında komut ne yazar?

```setup
import os
os.makedirs("veri/eski", exist_ok=True)
for yol in ["veri/a.log", "veri/b.txt", "veri/eski/c.log", "veri/d.log"]:
    open(yol, "w", encoding="utf-8", newline="\n").write("x\n")
```

```bash
find veri -path '*/eski' -prune -o -name '*.log' -print | sort
```

???

`veri/a.log` ve `veri/d.log`. `-prune` `eski` klasörüne girilmesini engeller, bu yüzden `c.log` hiç görülmez. `-print` yalnızca `-o`'nun sağ tarafındaki koşul doğru olunca çalışır; `b.txt` `.log` olmadığı için elenir.
:::

::: gorev Bütün log dosyaları
`loglar` klasörünün altındaki (alt klasörler dahil) bütün `.log` dosyalarının yollarını **sıralı** yazdır. Adlarda boşluk var.

```setup
import os
os.makedirs("loglar/eski", exist_ok=True)
dosyalar = {"loglar/web.log": "1\n2\n3\n", "loglar/notlar.txt": "x\n", "loglar/eski/db.log": "1\n",
            "loglar/yedek gece.log": "1\n2\n"}
for yol, icerik in dosyalar.items():
    open(yol, "w", encoding="utf-8", newline="\n").write(icerik)
```

```starter
ls loglar
```

```test
eq(out, "loglar/eski/db.log\nloglar/web.log\nloglar/yedek gece.log\n", "üç log dosyası, sıralı")
ok("find" in src, "find kullan")
```

```solution
find loglar -type f -name '*.log' | sort
```

```hint
`find loglar -type f -name '*.log'`, sonra `sort`.
```
:::

::: gorev Satır sayıları
Aynı klasördeki her `.log` dosyası için `satır_sayısı yol` yazdır, yola göre sıralı. Boşluklu adlar bozulmamalı.

```setup
import os
os.makedirs("loglar/eski", exist_ok=True)
dosyalar = {"loglar/web.log": "1\n2\n3\n", "loglar/notlar.txt": "x\n", "loglar/eski/db.log": "1\n",
            "loglar/yedek gece.log": "1\n2\n"}
for yol, icerik in dosyalar.items():
    open(yol, "w", encoding="utf-8", newline="\n").write(icerik)
```

```starter
for f in $(find loglar -name '*.log'); do
    echo "$(wc -l < "$f") $f"
done
```

```test
eq(out, "1 loglar/eski/db.log\n3 loglar/web.log\n2 loglar/yedek gece.log\n", "her dosyanın satır sayısı")
```

```solution
find loglar -type f -name '*.log' -print0 | sort -z | while IFS= read -r -d '' f; do
    echo "$(wc -l < "$f") $f"
done
```

```hint
`for f in $(find ...)` "yedek gece.log"u ikiye böler. `find ... -print0 | while IFS= read -r -d '' f` adları sıfır baytıyla taşır.
```

```hint
Sıfırla ayrılmış listeyi sıralamak için `sort -z`.
```
:::

::: gorev Büyük dosyalar
`depo` klasöründe **1 KiB'tan büyük** dosyaların yalnızca adlarını (yol olmadan) sıralı yazdır.

```setup
import os
os.makedirs("depo/alt", exist_ok=True)
open("depo/kucuk.txt", "w", newline="\n").write("a" * 100)
open("depo/buyuk.bin", "w", newline="\n").write("b" * 5000)
open("depo/alt/orta.dat", "w", newline="\n").write("c" * 3000)
open("depo/alt/minik.dat", "w", newline="\n").write("d" * 10)
```

```starter
find depo -type f
```

```test
eq(out, "buyuk.bin\norta.dat\n", "iki büyük dosya")
```

```solution
find depo -type f -size +1k -printf '%f\n' | sort
```

```hint
`-size +1k` 1 KiB'tan büyükleri seçer; `-printf '%f\n'` yalnızca dosya adını yazar.
```
:::
