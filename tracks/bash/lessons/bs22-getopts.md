---
id: bs22
title: getopts ile Komut Satırı Aracı
summary: Seçenekleri getopts ile ayrıştırmak, OPTARG ve OPTIND, kalan argümanlar, sessiz hata kipi, kullanım mesajı ve doğru çıkış kodları.
kazanim: LPIC1 105.2
---

::: anlat Gerçek bir araç gibi davranmak
İyi bir komut satırı aracı seçenek alır (`-v`, `-n 5`, `-o dosya`), yanlış kullanımda kısa bir kullanım mesajı verir ve doğru çıkış kodlarıyla döner. Bash'in yerleşik `getopts` komutu tek harfli seçenekleri ayrıştırır:

```bash
set -- -v -n 5 -o rapor.txt kayit1 kayit2      #! betiğe bu argümanlar verilmiş gibi
ayrintili=0; adet=10; cikti=""
while getopts ":vn:o:" secenek; do             #! harf: seçenek; harften sonra ':' : değer alır
    case $secenek in
        v) ayrintili=1 ;;
        n) adet=$OPTARG ;;                      #! seçeneğin değeri OPTARG'da
        o) cikti=$OPTARG ;;
        :) echo "-$OPTARG bir değer ister" >&2; exit 2 ;;
        \?) echo "bilinmeyen seçenek: -$OPTARG" >&2; exit 2 ;;
    esac
done
shift $((OPTIND - 1))                           #! işlenen seçenekleri at; geriye konum argümanları kalır
echo "ayrıntılı=$ayrintili adet=$adet çıktı=$cikti kalanlar: $*"
```

| Yazım | Anlamı |
|---|---|
| `"vn:o:"` | `-v` değersiz, `-n` ve `-o` değerli |
| baştaki `:` | **sessiz kip**: hataları getopts yazmaz, `:` (değer eksik) ve `?` (bilinmeyen) olarak sana bildirir |
| `OPTARG` | seçeneğin değeri (ya da hatalı seçeneğin harfi) |
| `OPTIND` | işlenecek sıradaki argümanın sırası |

`-vn 5` gibi birleşik yazımları ve `-n5` gibi bitişik değerleri de getopts kendiliğinden anlar.

### Kullanım mesajı ve çıkış kodları
Gelenek: kullanım hatası **2**, çalışma zamanı hatası **1**, başarı **0**; hata mesajları standart hataya:

```bash
kullanim() {
    echo "kullanım: ${0##*/} [-v] [-n ADET] DOSYA" >&2
    exit 2
}
```

> [!NOT]
> `getopts` uzun seçenekleri (`--yardim`) desteklemez. Onlar için argümanlar bir `while (( $# )); do case $1 in --yardim) ...; esac; shift; done` döngüsüyle elle ayrıştırılır. GNU `getopt` (s'siz, harici program) uzun seçenekleri destekler ama her sistemde aynı değildir.
:::

::: tahmin
Tek satır yazar:

```bash
set -- -v -n 3 rapor.txt
while getopts "vn:" s; do
    case $s in
        v) ayrintili=1 ;;
        n) adet=$OPTARG ;;
    esac
done
shift $((OPTIND - 1))
echo "$ayrintili $adet $1 $#"
```

???

`1 3 rapor.txt 1`. `-v` ayrintili'yi 1 yapar, `-n 3` adet'i 3. `OPTIND` işlenmemiş ilk argümanı (rapor.txt) gösterir; `shift` seçenekleri atınca `$1` rapor.txt olur ve geriye bir argüman kalır.
:::

::: gorev Seçenekli selam
Betik `-a AD` (varsayılan `dünya`) ve `-b` (büyük harf) seçeneklerini alsın ve `Merhaba, AD!` yazdırsın; `-b` verilmişse bütün satır büyük harf olsun. Bilinmeyen bir seçenekte standart hataya `kullanım: selam [-b] [-a AD]` yazıp **2** koduyla çıksın.

```starter
echo "Merhaba, $1!"
```

```test
eq(run(), "Merhaba, dünya!\n", "seçeneksiz")
eq(run(argv=["-a", "Ece"]), "Merhaba, Ece!\n", "-a Ece")
eq(run(argv=["-b", "-a", "web"]), "MERHABA, WEB!\n", "-b -a web")
eq(run(argv=["-ba", "can"]), "MERHABA, CAN!\n", "birleşik yazım -ba can")
r = calis(argv=["-x"])
eq(r["kod"], 2, "bilinmeyen seçenek → 2")
ok("kullanım" in r["hata"], "kullanım mesajı stderr'de", got=r["hata"])
```

```solution
ad="dünya"; buyuk=0
while getopts ":a:b" s; do
    case $s in
        a) ad=$OPTARG ;;
        b) buyuk=1 ;;
        *) echo "kullanım: selam [-b] [-a AD]" >&2; exit 2 ;;
    esac
done
satir="Merhaba, $ad!"
if (( buyuk )); then
    satir=${satir^^}
fi
echo "$satir"
```

```hint
`getopts ":a:b" s`: `a` değer alır, `b` almaz; baştaki `:` sessiz kip. Bilinmeyen seçenek `?` olarak gelir; `*)` ile yakala.
```

```hint
Büyük harf için parametre genişletmesi: `${satir^^}`.
```
:::

::: gorev Ayırıcıyla birleştir
Betik `-s AYIRICI` seçeneğini (varsayılan tek boşluk) ve ardından istenen sayıda kelimeyi alsın; kelimeleri ayırıcıyla birleştirip yazdırsın.

```starter
echo "$@"
```

```meta
argv: -s , a b c
```

```test
eq(out, "a,b,c\n", "-s , a b c")
eq(run(argv=["x", "y"]), "x y\n", "varsayılan ayırıcı")
eq(run(argv=["-s", " | ", "web01", "db01"]), "web01 | db01\n", "çok karakterli ayırıcı")
eq(run(argv=["-s", "-"]), "\n", "kelime yoksa boş satır")
```

```solution
ayirici=" "
while getopts "s:" s; do
    case $s in
        s) ayirici=$OPTARG ;;
        *) exit 2 ;;
    esac
done
shift $((OPTIND - 1))
sonuc=""
for k in "$@"; do
    sonuc+="${sonuc:+$ayirici}$k"
done
echo "$sonuc"
```

```hint
Seçenekleri işledikten sonra `shift $((OPTIND - 1))`; geriye kelimeler kalır.
```

```hint
Ayırıcı çok karakterli olabildiği için `IFS` hilesi işe yaramaz; döngüyle biriktir: `sonuc+="${sonuc:+$ayirici}$k"`.
```
:::

::: gorev Zorunlu seçenek
Betik zorunlu `-f DOSYA` seçeneği alsın ve dosyanın satır sayısını `N satır` olarak yazdırsın. `-f` verilmezse stderr'e `kullanım: say -f DOSYA` yazıp **2** ile; dosya yoksa stderr'e `hata: dosya yok: <ad>` yazıp **1** ile çıksın.

```setup
open("veri.txt", "w", encoding="utf-8", newline="\n").write("a\nb\nc\n")
```

```starter
wc -l < "$2"
```

```meta
argv: -f veri.txt
```

```test
eq(out, "3 satır\n", "-f veri.txt")
r = calis()
eq(r["kod"], 2, "-f yok → 2")
ok("kullanım: say -f DOSYA" in r["hata"], "kullanım mesajı", got=r["hata"])
r = calis(argv=["-f", "yok.txt"])
eq(r["kod"], 1, "dosya yok → 1")
ok("hata: dosya yok: yok.txt" in r["hata"], "hata mesajı", got=r["hata"])
r = calis(argv=["-f"])
eq(r["kod"], 2, "-f değersiz → 2")
```

```solution
kullanim() { echo "kullanım: say -f DOSYA" >&2; exit 2; }
dosya=""
while getopts ":f:" s; do
    case $s in
        f) dosya=$OPTARG ;;
        *) kullanim ;;
    esac
done
[[ -n $dosya ]] || kullanim
if [[ ! -f $dosya ]]; then
    echo "hata: dosya yok: $dosya" >&2
    exit 1
fi
echo "$(wc -l < "$dosya") satır"
```

```hint
Sessiz kipte (`":f:"`) değersiz `-f`, `:` olarak gelir; bilinmeyen seçenekle birlikte `*)` ile kullanım mesajına yönlendir.
```

```hint
Döngüden sonra `[[ -n $dosya ]] || kullanim` ile zorunluluğu denetle.
```
:::
