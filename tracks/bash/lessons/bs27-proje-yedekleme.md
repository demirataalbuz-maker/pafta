---
id: bs27
title: Proje · Yedekleme ve Döndürme Betiği
summary: tar ile sıkıştırılmış yedek almak, zaman damgalı adlar, son N yedeği tutup eskileri silmek, kuru çalıştırma kipi ve sağlam hata davranışıyla gerçek bir bakım betiği.
---

::: anlat Proje tanımı
Sunucularda en sık yazılan betiklerden biri yedekleme betiğidir: bir klasörü sıkıştırılmış bir arşive koyar, arşive zaman damgalı bir ad verir ve disk dolmasın diye eski yedekleri siler (döndürme, rotation).

```text
kullanım: yedekle -k KAYNAK -h HEDEF [-t TUT] [-d DAMGA] [-n]
```

| Seçenek | Anlamı |
|---|---|
| `-k KAYNAK` | yedeklenecek klasör (zorunlu) |
| `-h HEDEF` | yedeklerin konacağı klasör (zorunlu) |
| `-t TUT` | en yeni kaç yedek tutulsun (varsayılan 5) |
| `-d DAMGA` | arşiv adındaki damga (varsayılan: şimdiki zaman `YYYYAAGG-SSDDss`); testlerde sabit damga vermek için |
| `-n` | kuru çalıştırma: ne yapılacağını yaz, hiçbir şey yapma |

`tar` ile arşiv almanın ve içine bakmanın temel kalıpları:

```bash
mkdir -p belgeler/alt && printf 'a\n' > belgeler/a.txt && printf 'b\n' > belgeler/alt/b.txt
tar -czf arsiv.tar.gz belgeler          #! c: oluştur, z: gzip, f: dosya adı
tar -tzf arsiv.tar.gz | sort            #! t: içeriği listele
mkdir -p geri && tar -xzf arsiv.tar.gz -C geri   #! x: aç, -C: hedef klasör
ls geri/belgeler
```

Damgaların `YYYYAAGG-SSDDss` biçiminde olması, **ada göre sıralamanın zamana göre sıralamayla aynı olması** demektir. Döndürme bu yüzden basit bir `sort` işidir.

> [!İPUCU]
> Bir şeyi silen her betiği önce `-n` ile çalıştır ve listeye bak. Yanlış bir desen ya da boş bir değişken yüzünden bütün yedekleri silen betik, bakım işlerinin en bilinen kâbusudur.
:::

::: tahmin
Döndürmenin mantığı. `-t 2` verildiğinde hangi yedekler silinir? Üç satır yazar:

```bash
yedekler='yedek-20261017-120000.tar.gz
yedek-20261019-120000.tar.gz
yedek-20261018-090000.tar.gz
yedek-20261016-230000.tar.gz'
echo "$yedekler" | sort | tail -n 1
echo "$yedekler" | sort -r | tail -n +3
```

???

`yedek-20261019-120000.tar.gz`, sonra `yedek-20261017-120000.tar.gz` ve `yedek-20261016-230000.tar.gz`. Damga `YYYYAAGG-SSDDss` biçiminde olduğu için ada göre sıralama zamana göre sıralamadır: `sort` sonrası en yeni yedek en sondadır. `sort -r` en yeniyi başa alır, `tail -n +3` üçüncü satırdan başlar, yani en yeni iki yedeği atlar. Kalanlar silinecek olanlardır.
:::

::: gorev 1 · Arşiv al
Betik `-k KAYNAK`, `-h HEDEF` ve `-d DAMGA` seçeneklerini alsın; hedef klasör yoksa oluştursun, `HEDEF/yedek-DAMGA.tar.gz` arşivini oluşturup `oluşturuldu: yedek-DAMGA.tar.gz` yazdırsın.

```setup
import os
os.makedirs("veri/alt", exist_ok=True)
open("veri/a.txt", "w", newline="\n").write("a\n")
open("veri/alt/b.txt", "w", newline="\n").write("b\n")
```

```starter
set -euo pipefail
tar -czf yedek.tar.gz veri
echo "tamam"
```

```meta
argv: -k veri -h yedekler -d 20261019-120000
```

```test
import tarfile
eq(out, "oluşturuldu: yedek-20261019-120000.tar.gz\n", "çıktı")
with tarfile.open("yedekler/yedek-20261019-120000.tar.gz") as t:
    adlar = set(t.getnames())
ok({"veri/a.txt", "veri/alt/b.txt"} <= adlar, "arşivde veri klasörünün dosyaları olmalı", got=sorted(adlar))
```

```solution
set -euo pipefail

kaynak=""; hedef=""; damga="$(date +%Y%m%d-%H%M%S)"
while getopts "k:h:d:" s; do
    case $s in
        k) kaynak=$OPTARG ;;
        h) hedef=$OPTARG ;;
        d) damga=$OPTARG ;;
        *) exit 2 ;;
    esac
done

ad="yedek-$damga.tar.gz"
mkdir -p -- "$hedef"
tar -czf "$hedef/$ad" -C "$(dirname -- "$kaynak")" "$(basename -- "$kaynak")"
echo "oluşturuldu: $ad"
```

```hint
Seçenekleri `getopts "k:h:d:"` ile oku; hedef klasörü `mkdir -p` ile oluştur.
```

```hint
Arşivin içinde yolun tamamı değil yalnızca klasör adı olsun: `tar -czf "$hedef/$ad" -C "$(dirname -- "$kaynak")" "$(basename -- "$kaynak")"`.
```
:::

::: gorev 2 · Döndürme
`-t TUT` seçeneği ekle (varsayılan 5). Yeni arşiv oluşturulduktan sonra hedefteki `yedek-*.tar.gz` dosyalarından **en yeni TUT tanesini** tut, eskileri sil ve her silinen için `silindi: ad` yazdır (eskiden yeniye).

```cikti
oluşturuldu: yedek-20261019-120000.tar.gz
silindi: yedek-20261015-020000.tar.gz
silindi: yedek-20261016-020000.tar.gz
```

```setup
import os
os.makedirs("veri", exist_ok=True)
open("veri/a.txt", "w", newline="\n").write("a\n")
os.makedirs("yedekler", exist_ok=True)
for gun in ("15", "16", "17", "18"):
    open(f"yedekler/yedek-202610{gun}-020000.tar.gz", "w").write("eski")
open("yedekler/notlar.txt", "w").write("dokunma")
```

```starter
set -euo pipefail

kaynak=""; hedef=""; damga="$(date +%Y%m%d-%H%M%S)"
while getopts "k:h:d:" s; do
    case $s in
        k) kaynak=$OPTARG ;;
        h) hedef=$OPTARG ;;
        d) damga=$OPTARG ;;
        *) exit 2 ;;
    esac
done

ad="yedek-$damga.tar.gz"
mkdir -p -- "$hedef"
tar -czf "$hedef/$ad" -C "$(dirname -- "$kaynak")" "$(basename -- "$kaynak")"
echo "oluşturuldu: $ad"
```

```meta
argv: -k veri -h yedekler -d 20261019-120000 -t 3
```

```test
import os
eq(out, "oluşturuldu: yedek-20261019-120000.tar.gz\nsilindi: yedek-20261015-020000.tar.gz\nsilindi: yedek-20261016-020000.tar.gz\n", "iki eski yedek silindi")
kalan = sorted(os.listdir("yedekler"))
eq(kalan, ["notlar.txt", "yedek-20261017-020000.tar.gz", "yedek-20261018-020000.tar.gz", "yedek-20261019-120000.tar.gz"], "en yeni üç yedek ve diğer dosya kaldı")
```

```solution
set -euo pipefail

kaynak=""; hedef=""; damga="$(date +%Y%m%d-%H%M%S)"; tut=5
while getopts "k:h:d:t:" s; do
    case $s in
        k) kaynak=$OPTARG ;;
        h) hedef=$OPTARG ;;
        d) damga=$OPTARG ;;
        t) tut=$OPTARG ;;
        *) exit 2 ;;
    esac
done

ad="yedek-$damga.tar.gz"
mkdir -p -- "$hedef"
tar -czf "$hedef/$ad" -C "$(dirname -- "$kaynak")" "$(basename -- "$kaynak")"
echo "oluşturuldu: $ad"

shopt -s nullglob
yedekler=( "$hedef"/yedek-*.tar.gz )            # glob sonucu ada göre sıralıdır: eskiden yeniye
silinecek=$(( ${#yedekler[@]} - tut ))
for (( i = 0; i < silinecek; i++ )); do
    rm -f -- "${yedekler[i]}"
    echo "silindi: ${yedekler[i]##*/}"
done
```

```hint
Glob sonuçları ada göre sıralı gelir; damga biçimi sayesinde bu eskiden yeniye demektir: `yedekler=( "$hedef"/yedek-*.tar.gz )`.
```

```hint
Silinecek sayı `${#yedekler[@]} - tut`; dizinin başından o kadarını sil. Negatifse döngü hiç çalışmaz.
```
:::

::: gorev 3 · Kuru çalıştırma ve hatalar
`-n` seçeneği ekle: verilirse hiçbir dosya oluşturulmasın ya da silinmesin; arşiv için `[kuru] oluşturulacak: ad`, silinecekler için `[kuru] silinecek: ad` yazdırılsın (yeni arşiv sayıma dahil). Ayrıca `-k` ya da `-h` eksikse stderr'e `kullanım: yedekle -k KAYNAK -h HEDEF [-t TUT] [-d DAMGA] [-n]` yazıp **2**, kaynak klasör yoksa stderr'e `hata: kaynak yok: <ad>` yazıp **1** ile çık.

```setup
import os
os.makedirs("veri", exist_ok=True)
open("veri/a.txt", "w", newline="\n").write("a\n")
os.makedirs("yedekler", exist_ok=True)
for gun in ("15", "16", "17", "18"):
    open(f"yedekler/yedek-202610{gun}-020000.tar.gz", "w").write("eski")
```

```starter
set -euo pipefail

kaynak=""; hedef=""; damga="$(date +%Y%m%d-%H%M%S)"; tut=5
while getopts "k:h:d:t:" s; do
    case $s in
        k) kaynak=$OPTARG ;;
        h) hedef=$OPTARG ;;
        d) damga=$OPTARG ;;
        t) tut=$OPTARG ;;
        *) exit 2 ;;
    esac
done

ad="yedek-$damga.tar.gz"
mkdir -p -- "$hedef"
tar -czf "$hedef/$ad" -C "$(dirname -- "$kaynak")" "$(basename -- "$kaynak")"
echo "oluşturuldu: $ad"

shopt -s nullglob
yedekler=( "$hedef"/yedek-*.tar.gz )
silinecek=$(( ${#yedekler[@]} - tut ))
for (( i = 0; i < silinecek; i++ )); do
    rm -f -- "${yedekler[i]}"
    echo "silindi: ${yedekler[i]##*/}"
done
```

```meta
argv: -k veri -h yedekler -d 20261019-120000 -t 3 -n
```

```test
import os
eq(out, "[kuru] oluşturulacak: yedek-20261019-120000.tar.gz\n[kuru] silinecek: yedek-20261015-020000.tar.gz\n[kuru] silinecek: yedek-20261016-020000.tar.gz\n", "kuru kip çıktısı")
eq(len(os.listdir("yedekler")), 4, "kuru kipte hiçbir dosya değişmemeli")
r = calis(argv=["-h", "yedekler"])
eq(r["kod"], 2, "-k eksik → 2")
ok("kullanım: yedekle" in r["hata"], "kullanım mesajı", got=r["hata"])
r = calis(argv=["-k", "yok", "-h", "yedekler"])
eq(r["kod"], 1, "olmayan kaynak → 1")
ok("hata: kaynak yok: yok" in r["hata"], "hata mesajı", got=r["hata"])
eq(len(os.listdir("yedekler")), 4, "hata durumunda da hiçbir şey değişmemeli")
eq(run(argv=["-k", "veri", "-h", "yedekler", "-d", "20261019-120000", "-t", "3"]),
   "oluşturuldu: yedek-20261019-120000.tar.gz\nsilindi: yedek-20261015-020000.tar.gz\nsilindi: yedek-20261016-020000.tar.gz\n", "gerçek kip hâlâ çalışıyor")
```

```solution
set -euo pipefail

kullanim() {
    echo "kullanım: yedekle -k KAYNAK -h HEDEF [-t TUT] [-d DAMGA] [-n]" >&2
    exit 2
}

kaynak=""; hedef=""; damga="$(date +%Y%m%d-%H%M%S)"; tut=5; kuru=0
while getopts ":k:h:d:t:n" s; do
    case $s in
        k) kaynak=$OPTARG ;;
        h) hedef=$OPTARG ;;
        d) damga=$OPTARG ;;
        t) tut=$OPTARG ;;
        n) kuru=1 ;;
        *) kullanim ;;
    esac
done
[[ -n $kaynak && -n $hedef ]] || kullanim
if [[ ! -d $kaynak ]]; then
    echo "hata: kaynak yok: $kaynak" >&2
    exit 1
fi

ad="yedek-$damga.tar.gz"
if (( kuru )); then
    echo "[kuru] oluşturulacak: $ad"
else
    mkdir -p -- "$hedef"
    tar -czf "$hedef/$ad" -C "$(dirname -- "$kaynak")" "$(basename -- "$kaynak")"
    echo "oluşturuldu: $ad"
fi

shopt -s nullglob
yedekler=( "$hedef"/yedek-*.tar.gz )
if (( kuru )); then
    # arşiv henüz yok: listeye ekleyip yeniden sırala
    mapfile -t yedekler < <(printf '%s\n' "${yedekler[@]}" "$hedef/$ad" | sort -u)
fi
silinecek=$(( ${#yedekler[@]} - tut ))
for (( i = 0; i < silinecek; i++ )); do
    if (( kuru )); then
        echo "[kuru] silinecek: ${yedekler[i]##*/}"
    else
        rm -f -- "${yedekler[i]}"
        echo "silindi: ${yedekler[i]##*/}"
    fi
done
```

```hint
Kuru kipte yeni arşiv diskte olmadığı için glob onu bulmaz; sayıma dahil etmek için listeye kendin ekle ve yeniden sırala.
```

```hint
Doğrulamaları iş başlamadan **önce** yap: eksik seçenek → kullanım (2), olmayan kaynak → hata (1). Böylece hata durumunda hiçbir dosyaya dokunulmaz.
```
:::
