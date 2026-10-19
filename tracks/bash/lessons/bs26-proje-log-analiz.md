---
id: bs26
title: Proje · Erişim Logu Analiz Aracı
summary: getopts, awk, sort ve sağlam betik kurallarını birleştiren, web sunucusu erişim logunu raporlayan gerçek bir komut satırı aracı.
---

::: anlat Proje tanımı
Bir web uygulamasının erişim logu her isteği bir satıra yazıyor:

```text
10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET /api/sunucular HTTP/1.1" 200 512 34
```

Boşluklara göre bölündüğünde alanlar: `$1` istemci adresi, `$4` zaman (`[` ile başlar), `$6` yöntem (`"` ile başlar), `$7` istenen yol, `$9` durum kodu, `$10` yanıt boyutu (bayt), `$11` süre (ms).

Bu projede, adım adım şu aracı yazacaksın:

```text
kullanım: analiz [-n ADET] [-s DURUM] DOSYA
```

1. Durum kodu dağılımı
2. En yavaş N istek (`-n`, varsayılan 3)
3. Durum koduna göre süzme (`-s`) ve doğru hata davranışı

Her görevin başlangıç kodu bir öncekinin çözümüdür. Araç BS10'daki kurallara uysun: `set -euo pipefail`, tırnaklanmış değişkenler, hatalar stderr'e, kullanım hatası 2, çalışma zamanı hatası 1.

> [!İPUCU]
> Bir raporu tek bir dev boru hattıyla değil, her biri tek bir soruyu cevaplayan küçük fonksiyonlarla yaz: `durumlar()`, `en_yavaslar()`. Hata ayıklarken her fonksiyonu tek başına çalıştırıp çıktısına bakabilirsin.
:::

::: gorev 1 · Durum dağılımı
Betik log dosyasının adını 1. argüman olarak alsın ve her durum kodu için `durum sayı` yazdırsın: çoktan aza, eşitlikte koda göre artan.

```cikti
200 7
404 2
500 2
201 1
```

```setup
satirlar = [
    '10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET /api/sunucular HTTP/1.1" 200 512 34',
    '10.0.0.9 - - [19/Oct/2026:08:15:09 +0300] "GET /api/biletler HTTP/1.1" 200 2048 120',
    '10.0.0.5 - - [19/Oct/2026:08:16:30 +0300] "POST /api/biletler HTTP/1.1" 201 128 210',
    '10.0.0.7 - - [19/Oct/2026:08:20:11 +0300] "GET /eski-sayfa HTTP/1.1" 404 64 5',
    '10.0.0.9 - - [19/Oct/2026:09:01:45 +0300] "GET /api/rapor HTTP/1.1" 500 32 1830',
    '10.0.0.5 - - [19/Oct/2026:09:02:10 +0300] "GET /api/sunucular HTTP/1.1" 200 512 41',
    '10.0.0.8 - - [19/Oct/2026:09:05:00 +0300] "GET /api/rapor HTTP/1.1" 500 32 2100',
    '10.0.0.7 - - [19/Oct/2026:09:10:20 +0300] "GET /favicon.ico HTTP/1.1" 404 0 3',
    '10.0.0.9 - - [19/Oct/2026:10:00:01 +0300] "GET /api/biletler HTTP/1.1" 200 2048 98',
    '10.0.0.5 - - [19/Oct/2026:10:12:44 +0300] "PUT /api/biletler/17 HTTP/1.1" 200 256 175',
    '10.0.0.8 - - [19/Oct/2026:10:30:00 +0300] "GET /api/rapor HTTP/1.1" 200 4096 950',
    '10.0.0.5 - - [19/Oct/2026:10:45:12 +0300] "GET /api/sunucular HTTP/1.1" 200 512 38',
]
open("erisim.log", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
set -euo pipefail
dosya="$1"
cat "$dosya"
```

```meta
argv: erisim.log
```

```test
eq(out, "200 7\n404 2\n500 2\n201 1\n", "durum dağılımı")
```

```solution
set -euo pipefail
dosya="$1"

durumlar() {
    awk '{ say[$9]++ } END { for (d in say) print d, say[d] }' "$1" | sort -k2,2nr -k1,1n
}

durumlar "$dosya"
```

```hint
Durum kodu 9. alandır: `awk '{ say[$9]++ } END { for (d in say) print d, say[d] }'`.
```

```hint
Sıralama: `sort -k2,2nr -k1,1n`: sayıya göre azalan, eşitlikte koda göre artan.
```
:::

::: gorev 2 · En yavaş istekler
Araca `-n ADET` seçeneği ekle (varsayılan 3). Çıktı iki bölümden oluşsun: önce `== durumlar ==` başlığı ve dağılım, sonra `== en yavaş N ==` başlığı ve en yavaş N istek (`süre yol`, süreye göre azalan).

```cikti
== durumlar ==
200 7
404 2
500 2
201 1
== en yavaş 2 ==
2100 /api/rapor
1830 /api/rapor
```

```setup
satirlar = [
    '10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET /api/sunucular HTTP/1.1" 200 512 34',
    '10.0.0.9 - - [19/Oct/2026:08:15:09 +0300] "GET /api/biletler HTTP/1.1" 200 2048 120',
    '10.0.0.5 - - [19/Oct/2026:08:16:30 +0300] "POST /api/biletler HTTP/1.1" 201 128 210',
    '10.0.0.7 - - [19/Oct/2026:08:20:11 +0300] "GET /eski-sayfa HTTP/1.1" 404 64 5',
    '10.0.0.9 - - [19/Oct/2026:09:01:45 +0300] "GET /api/rapor HTTP/1.1" 500 32 1830',
    '10.0.0.5 - - [19/Oct/2026:09:02:10 +0300] "GET /api/sunucular HTTP/1.1" 200 512 41',
    '10.0.0.8 - - [19/Oct/2026:09:05:00 +0300] "GET /api/rapor HTTP/1.1" 500 32 2100',
    '10.0.0.7 - - [19/Oct/2026:09:10:20 +0300] "GET /favicon.ico HTTP/1.1" 404 0 3',
    '10.0.0.9 - - [19/Oct/2026:10:00:01 +0300] "GET /api/biletler HTTP/1.1" 200 2048 98',
    '10.0.0.5 - - [19/Oct/2026:10:12:44 +0300] "PUT /api/biletler/17 HTTP/1.1" 200 256 175',
    '10.0.0.8 - - [19/Oct/2026:10:30:00 +0300] "GET /api/rapor HTTP/1.1" 200 4096 950',
    '10.0.0.5 - - [19/Oct/2026:10:45:12 +0300] "GET /api/sunucular HTTP/1.1" 200 512 38',
]
open("erisim.log", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
set -euo pipefail
dosya="$1"

durumlar() {
    awk '{ say[$9]++ } END { for (d in say) print d, say[d] }' "$1" | sort -k2,2nr -k1,1n
}

durumlar "$dosya"
```

```meta
argv: -n 2 erisim.log
```

```test
DURUMLAR = "== durumlar ==\n200 7\n404 2\n500 2\n201 1\n"
eq(out, DURUMLAR + "== en yavaş 2 ==\n2100 /api/rapor\n1830 /api/rapor\n", "-n 2")
eq(run(argv=["erisim.log"]), DURUMLAR + "== en yavaş 3 ==\n2100 /api/rapor\n1830 /api/rapor\n950 /api/rapor\n", "varsayılan 3")
```

```solution
set -euo pipefail

adet=3
while getopts "n:" s; do
    case $s in
        n) adet=$OPTARG ;;
        *) exit 2 ;;
    esac
done
shift $((OPTIND - 1))
dosya="$1"

durumlar() {
    awk '{ say[$9]++ } END { for (d in say) print d, say[d] }' "$1" | sort -k2,2nr -k1,1n
}

en_yavaslar() {
    awk '{ print $11, $7 }' "$1" | sort -k1,1nr | head -n "$2"
}

echo "== durumlar =="
durumlar "$dosya"
echo "== en yavaş $adet =="
en_yavaslar "$dosya" "$adet"
```

```hint
`getopts "n:"` ile `adet`'i oku, ardından `shift $((OPTIND - 1))`: dosya adı `$1` olur.
```

```hint
Süre 11., yol 7. alan: `awk '{ print $11, $7 }' | sort -k1,1nr | head -n "$adet"`.
```
:::

::: gorev 3 · Süzme ve hatalar
Araca `-s DURUM` seçeneği ekle: verilirse **her iki** rapor da yalnızca o durum kodlu isteklerden yapılsın. Ayrıca: dosya argümanı yoksa stderr'e `kullanım: analiz [-n ADET] [-s DURUM] DOSYA` yazıp **2**; dosya yoksa stderr'e `hata: dosya yok: <ad>` yazıp **1** ile çık.

```setup
satirlar = [
    '10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET /api/sunucular HTTP/1.1" 200 512 34',
    '10.0.0.9 - - [19/Oct/2026:08:15:09 +0300] "GET /api/biletler HTTP/1.1" 200 2048 120',
    '10.0.0.5 - - [19/Oct/2026:08:16:30 +0300] "POST /api/biletler HTTP/1.1" 201 128 210',
    '10.0.0.7 - - [19/Oct/2026:08:20:11 +0300] "GET /eski-sayfa HTTP/1.1" 404 64 5',
    '10.0.0.9 - - [19/Oct/2026:09:01:45 +0300] "GET /api/rapor HTTP/1.1" 500 32 1830',
    '10.0.0.5 - - [19/Oct/2026:09:02:10 +0300] "GET /api/sunucular HTTP/1.1" 200 512 41',
    '10.0.0.8 - - [19/Oct/2026:09:05:00 +0300] "GET /api/rapor HTTP/1.1" 500 32 2100',
    '10.0.0.7 - - [19/Oct/2026:09:10:20 +0300] "GET /favicon.ico HTTP/1.1" 404 0 3',
    '10.0.0.9 - - [19/Oct/2026:10:00:01 +0300] "GET /api/biletler HTTP/1.1" 200 2048 98',
    '10.0.0.5 - - [19/Oct/2026:10:12:44 +0300] "PUT /api/biletler/17 HTTP/1.1" 200 256 175',
    '10.0.0.8 - - [19/Oct/2026:10:30:00 +0300] "GET /api/rapor HTTP/1.1" 200 4096 950',
    '10.0.0.5 - - [19/Oct/2026:10:45:12 +0300] "GET /api/sunucular HTTP/1.1" 200 512 38',
]
open("erisim.log", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
set -euo pipefail

adet=3
while getopts "n:" s; do
    case $s in
        n) adet=$OPTARG ;;
        *) exit 2 ;;
    esac
done
shift $((OPTIND - 1))
dosya="$1"

durumlar() {
    awk '{ say[$9]++ } END { for (d in say) print d, say[d] }' "$1" | sort -k2,2nr -k1,1n
}

en_yavaslar() {
    awk '{ print $11, $7 }' "$1" | sort -k1,1nr | head -n "$2"
}

echo "== durumlar =="
durumlar "$dosya"
echo "== en yavaş $adet =="
en_yavaslar "$dosya" "$adet"
```

```meta
argv: -s 200 -n 2 erisim.log
```

```test
eq(out, "== durumlar ==\n200 7\n== en yavaş 2 ==\n950 /api/rapor\n175 /api/biletler/17\n", "-s 200 -n 2")
eq(run(argv=["-s", "404", "erisim.log"]), "== durumlar ==\n404 2\n== en yavaş 3 ==\n5 /eski-sayfa\n3 /favicon.ico\n", "-s 404")
r = calis()
eq(r["kod"], 2, "dosyasız → 2")
ok("kullanım: analiz [-n ADET] [-s DURUM] DOSYA" in r["hata"], "kullanım mesajı", got=r["hata"])
r = calis(argv=["yok.log"])
eq(r["kod"], 1, "olmayan dosya → 1")
ok("hata: dosya yok: yok.log" in r["hata"], "hata mesajı", got=r["hata"])
```

```solution
set -euo pipefail

kullanim() {
    echo "kullanım: analiz [-n ADET] [-s DURUM] DOSYA" >&2
    exit 2
}

adet=3
durum=""
while getopts ":n:s:" s; do
    case $s in
        n) adet=$OPTARG ;;
        s) durum=$OPTARG ;;
        *) kullanim ;;
    esac
done
shift $((OPTIND - 1))
(( $# == 1 )) || kullanim
dosya="$1"
if [[ ! -f $dosya ]]; then
    echo "hata: dosya yok: $dosya" >&2
    exit 1
fi

suz() {
    awk -v d="$durum" 'd == "" || $9 == d' "$dosya"
}

durumlar() {
    awk '{ say[$9]++ } END { for (d in say) print d, say[d] }' | sort -k2,2nr -k1,1n
}

en_yavaslar() {
    awk '{ print $11, $7 }' | sort -k1,1nr | head -n "$1"
}

echo "== durumlar =="
suz | durumlar
echo "== en yavaş $adet =="
suz | en_yavaslar "$adet"
```

```hint
Süzmeyi tek bir fonksiyona topla: `suz() { awk -v d="$durum" 'd == "" || $9 == d' "$dosya"; }`. Rapor fonksiyonları dosya yerine standart girdiden okusun: `suz | durumlar`.
```

```hint
`set -u` açıkken `$1` olmadan `dosya="$1"` satırı kendi hatasını verir; önce `(( $# == 1 )) || kullanim` ile denetle.
```
:::
