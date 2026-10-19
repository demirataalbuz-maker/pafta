---
id: bs23
title: Betik Mimarisi
summary: Büyük betikleri düzenlemek; main fonksiyonu, log fonksiyonları, sabitler, ayar dosyasını source etmeden güvenle okumak, mkdir ile kilit ve kuru çalıştırma kipi.
---

::: anlat Uzun betiğin iskeleti
Yüz satırı aşan bir betik, fonksiyonlara bölünmüş ve tek bir giriş noktasından yönetilen bir program gibi yazılmalıdır:

```bash norun
#!/usr/bin/env bash
set -Eeuo pipefail                         # hata, tanımsız değişken ve boru hatası olunca dur

readonly SURUM="1.2.0"
readonly KILIT="/tmp/yedekle.kilit"

log()  { printf '[bilgi] %s\n' "$*" >&2; }
hata() { printf '[hata] %s\n' "$*" >&2; exit 1; }

kullanim() { echo "kullanım: ${0##*/} [-n] KAYNAK" >&2; exit 2; }

ayarlari_oku() { ...; }
kilitle()      { ...; }
calis()        { ...; }

main() {
    ayarlari_oku
    kilitle
    calis "$@"
}

main "$@"                                  # bütün iş tek satırdan başlar
```

Bu düzenin faydası: bütün fonksiyonlar tanımlandıktan sonra iş başlar, her parça ayrı ayrı okunabilir ve denenebilir, log mesajları standart hataya gittiği için standart çıktı **yalnızca sonuç** taşır ve boruya güvenle bağlanabilir.

### Ayar dosyasını güvenle okumak
`source ayar.conf` en kolay yoldur ama dosyadaki her satırı **kod olarak çalıştırır**: `port=$(rm -rf ~)` gibi bir satır gerçekten çalışır.

> [!GÜVENLİK]
> Kaynağı tam güvenilir olmayan bir ayar dosyasını `source` etme. `anahtar=değer` satırlarını `read` ile ayrıştır, yorumları atla, beklenmeyen anahtarları reddet. Değer bir metin olarak kalır, asla çalıştırılmaz.

```bash
printf '# ayarlar\nport = 8080\nhost=web01\n\nkomut=$(echo tehlike)\n' > ayar.conf
declare -A ayar
while IFS='=' read -r anahtar deger; do
    anahtar="${anahtar//[[:space:]]/}"                  #! boşlukları at
    [[ -z $anahtar || $anahtar == \#* ]] && continue      #! boş ve yorum satırı
    deger="${deger#"${deger%%[![:space:]]*}"}"           #! baştaki boşluklar
    ayar[$anahtar]=$deger
done < ayar.conf
for k in "${!ayar[@]}"; do echo "$k=${ayar[$k]}"; done | sort
```

### Kilit: aynı anda iki kopya çalışmasın
`mkdir` **atomiktir**: klasör zaten varsa başarısız olur. Bu yüzden basit ve güvenilir bir kilit olarak kullanılır:

```bash
if mkdir kilit.d 2>/dev/null; then
    trap 'rmdir kilit.d' EXIT
    echo "kilidi aldım, çalışıyorum"
else
    echo "başka bir kopya çalışıyor" >&2
fi
```

### Kuru çalıştırma
Değişiklik yapan araçlarda `-n` (dry run) kipi, ne yapılacağını gösterip hiçbir şey yapmamak demektir. Tek bir sarmalayıcı fonksiyon bunu bütün betiğe yayar:

```bash
KURU=1
calistir() { if (( KURU )); then echo "[kuru] $*"; else "$@"; fi; }
calistir rm -f eski.log
```
:::

::: tahmin
İki satır yazar:

```bash
KURU=1
calistir() { if (( KURU )); then echo "[kuru] $*"; else "$@"; fi; }
calistir rm -f eski.log
KURU=0
calistir echo "gerçekten çalıştı"
```

???

`[kuru] rm -f eski.log`, sonra `gerçekten çalıştı`. Kuru kipte komut yalnızca yazdırılır. `KURU=0` olunca `"$@"` komutu argümanlarıyla birlikte gerçekten çalıştırır: `echo` metni yazar.
:::

::: gorev Güvenli ayar okuyucu
`ayar.conf` dosyasını `source` etmeden oku ve ayarları `anahtar=değer` biçiminde, anahtara göre sıralı yazdır. Yorum ve boş satırları atla; `=` çevresindeki boşlukları temizle. Değerler asla çalıştırılmamalı.

```setup
open("ayar.conf", "w", encoding="utf-8", newline="\n").write(
    "# sunucu ayarları\nport = 8080\nhost=web01\n\n   # girintili yorum\nkomut=$(echo tehlike)\nyol = /var/log/uygulama\n")
```

```starter
source ayar.conf
echo "port=$port"
```

```test
eq(out, "host=web01\nkomut=$(echo tehlike)\nport=8080\nyol=/var/log/uygulama\n", "dört ayar, değerler harfi harfine")
ok("source" not in src and not src.lstrip().startswith(". "), "source kullanma")
```

```solution
declare -A ayar
while IFS='=' read -r anahtar deger; do
    anahtar="${anahtar//[[:space:]]/}"
    [[ -z $anahtar || $anahtar == \#* ]] && continue
    deger="${deger#"${deger%%[![:space:]]*}"}"
    deger="${deger%"${deger##*[![:space:]]}"}"
    ayar[$anahtar]=$deger
done < ayar.conf
for k in "${!ayar[@]}"; do
    echo "$k=${ayar[$k]}"
done | sort
```

```hint
`while IFS='=' read -r anahtar deger` satırı ilk `=`'ten böler; değerdeki sonraki `=`'ler değerde kalır.
```

```hint
Baştaki boşlukları silmek: `${deger#"${deger%%[![:space:]]*}"}`; sondakiler: `${deger%"${deger##*[![:space:]]}"}`.
```
:::

::: gorev Kilitli çalışma
Betik `kilit.d` klasörünü kilit olarak kullansın. Kilidi alabilirse `çalıştı` yazdırsın ve çıkarken kilidi kaldırsın. Kilit zaten varsa standart hataya `zaten çalışıyor` yazıp **1** koduyla çıksın.

```starter
mkdir -p kilit.d
echo "çalıştı"
```

```test
import os
r = calis()
eq((r["kod"], r["cikti"]), (0, "çalıştı\n"), "kilit boşken çalışır")
ok(not os.path.exists("kilit.d"), "çıkarken kilit kaldırılmalı")
os.mkdir("kilit.d")
r = calis()
eq(r["kod"], 1, "kilit varken 1")
ok("zaten çalışıyor" in r["hata"], "mesaj stderr'de", got=r["hata"])
ok(os.path.isdir("kilit.d"), "başkasının kilidine dokunulmamalı")
```

```solution
if ! mkdir kilit.d 2>/dev/null; then
    echo "zaten çalışıyor" >&2
    exit 1
fi
trap 'rmdir kilit.d' EXIT
echo "çalıştı"
```

```hint
`mkdir -p` klasör varsa da başarılı olur; kilit için `-p`'siz `mkdir` gerekir. Başarısızsa çık, başarılıysa `trap 'rmdir kilit.d' EXIT`.
```

```hint
Kilidi alamayınca `trap`'i kurma: yoksa başka kopyanın kilidini silersin.
```
:::

::: gorev Kuru çalıştırma kipi
Betik çalışma klasöründeki `.tmp` dosyalarını silsin ve her biri için `silindi: ad` yazdırsın (ada göre sıralı). `-n` verilirse hiçbir şey silmeden her dosya için `[kuru] rm -f ad` yazdırsın.

```setup
for ad in ["b.tmp", "a.tmp", "notlar.txt"]:
    open(ad, "w", newline="\n").write("x")
```

```starter
for f in *.tmp; do
    rm -f "$f"
    echo "silindi: $f"
done
```

```meta
argv: -n
```

```test
import os
eq(out, "[kuru] rm -f a.tmp\n[kuru] rm -f b.tmp\n", "kuru kipte yalnızca listele")
ok(os.path.exists("a.tmp") and os.path.exists("b.tmp"), "kuru kipte dosyalar silinmemeli")
eq(run(), "silindi: a.tmp\nsilindi: b.tmp\n", "gerçek kip")
ok(not os.path.exists("a.tmp") and not os.path.exists("b.tmp"), "gerçek kipte silinmeli")
ok(os.path.exists("notlar.txt"), "başka dosyalara dokunulmamalı")
```

```solution
KURU=0
while getopts "n" s; do
    case $s in
        n) KURU=1 ;;
        *) exit 2 ;;
    esac
done
calistir() { if (( KURU )); then echo "[kuru] $*"; else "$@"; fi; }
shopt -s nullglob
for f in *.tmp; do
    calistir rm -f "$f"
    (( KURU )) || echo "silindi: $f"
done
```

```hint
`-n`'yi getopts ile oku, `calistir` sarmalayıcısıyla `rm`'yi çağır. Gerçek kipte ayrıca `silindi:` satırını yaz.
```
:::
