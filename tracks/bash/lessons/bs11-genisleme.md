---
id: bs11
title: Genişleme Sırası ve Tırnaklama
summary: Kabuğun bir satırı çalıştırmadan önce yaptığı yedi genişleme adımı, kelime bölme ve IFS, "$@" ile "$*" farkı, printf ve glob.
kazanim: LPIC1 103.1, LPIC1 103.3
---

::: anlat Kabuk satırı önce dönüştürür, sonra çalıştırır
Bash bir komut satırını çalıştırmadan önce onu sırayla **genişletir**. Bu sırayı bilmek, kabuk betiklerindeki tuhaf davranışların neredeyse hepsini açıklar:

| Sıra | Genişleme | Örnek | Sonuç |
|---|---|---|---|
| 1 | süslü parantez | `yedek-{a,b}.tar` | `yedek-a.tar yedek-b.tar` |
| 2 | tilde | `~/notlar` | `/home/ece/notlar` |
| 3 | parametre | `$HOME`, `${ad}` | değişkenin değeri |
| 4 | komut ikamesi | `$(date +%Y)` | komutun çıktısı |
| 5 | aritmetik | `$((3 * 4))` | `12` |
| 6 | **kelime bölme** | tırnaksız `$x` | IFS karakterlerinden bölünür |
| 7 | **dosya adı (glob)** | `*.log` | eşleşen dosya adları |

Ardından tırnaklar kaldırılır ve komut çalışır. 6. ve 7. adımlar yalnızca **tırnaksız** sonuçlara uygulanır; çift tırnak ikisini de durdurur.

```bash
echo yedek-{pzt,sal,car}.tar        #! 1. adım: virgüllü liste
echo {1..5} {a..e}                  #! aralık
echo {01..10..3}                    #! sıfırla doldurma ve adım
x="a b   c"
printf '[%s]\n' $x                  #! 6. adım: üç kelimeye bölünür
printf '[%s]\n' "$x"                #! tırnaklı: tek parça, boşluklar korunur
```

> [!DERİN]
> Süslü parantez genişlemesi **ilk** adımdır, parametre genişlemesinden önce yapılır. Bu yüzden `n=5; echo {1..$n}` çalışmaz, `{1..$n}` olarak kalır. Değişken bir aralık için `seq 1 "$n"` ya da `for ((i = 1; i <= n; i++))` kullanılır.
:::

::: anlat "$@", "$*" ve IFS
Argümanların hepsine erişmenin dört yolu vardır; yalnızca biri her zaman doğrudur:

| Yazım | Sonuç |
|---|---|
| `"$@"` | her argüman **ayrı ve bozulmadan**: neredeyse her zaman istenen budur |
| `"$*"` | bütün argümanlar **tek metin**, IFS'nin ilk karakteriyle birleşmiş |
| `$@`, `$*` (tırnaksız) | kelime bölmeye ve glob'a uğrar: boşluklu argümanlar parçalanır |

```bash
set -- "yıllık rapor.txt" notlar.txt     #! argümanları elle ayarla
printf '<%s>\n' "$@"
(IFS=,; echo "$*")                      #! alt kabukta IFS'yi değiştir, birleştir
```

**IFS** (Internal Field Separator) kelime bölmenin hangi karakterlerden yapılacağını söyler; varsayılanı boşluk, sekme ve satır sonudur. `read` da satırı IFS'ye göre böler. Tek komut için değiştirmek en güvenli yoldur:

```bash
IFS=, read -r ad rol cpu <<< "web01,web,72"
echo "$ad / $rol / $cpu"
```

### echo yerine printf
`echo`'nun davranışı kabuktan kabuğa değişir (`-e`, `-n`, ters eğik çizgiler). `printf` her yerde aynıdır ve biçim belirteçleri C'deki gibidir: `printf '%-8s %5.1f\n' web01 72.46`.

> [!TUZAK]
> Hiçbir dosyayla eşleşmeyen bir glob **olduğu gibi** kalır: klasörde `.log` dosyası yoksa `for f in *.log` döngüsü bir kez, `f='*.log'` metniyle çalışır. `shopt -s nullglob` eşleşmeyen glob'u boş listeye çevirir.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
set -- "bir iki" üç
printf '<%s>\n' "$@"
printf '<%s>\n' "$*"
printf '<%s>\n' $@
```

???

`<bir iki>`, `<üç>`, `<bir iki üç>`, `<bir>`, `<iki>`, `<üç>`. `"$@"` iki argümanı bozmadan verir. `"$*"` hepsini tek metne birleştirir. Tırnaksız `$@` ise kelime bölmeye uğrar ve "bir iki" argümanı ikiye ayrılır: üç ayrı parça.
:::

::: gorev Yedek adları
`yedek-01.tar`'dan `yedek-05.tar`'a kadar beş dosya adını, her biri ayrı satırda olacak şekilde yazdır. Süslü parantez genişlemesi kullan.

```starter
echo yedek-1.tar
```

```test
eq(out, "".join(f"yedek-0{i}.tar\n" for i in range(1, 6)), "yedek-01.tar … yedek-05.tar")
ok("{" in src and ".." in src, "süslü parantez aralığı kullan")
```

```solution
printf '%s\n' yedek-{01..05}.tar
```

```hint
`{01..05}` sıfırla doldurulmuş bir aralık üretir; `printf '%s\n'` her parçayı ayrı satıra yazar.
```
:::

::: gorev Virgülle birleştir
Betik aldığı argümanları **virgülle** birleştirip tek satırda yazdırsın; boşluklu argümanlar bozulmamalı.

```starter
echo "$@"
```

```meta
argv: "yıllık rapor.txt" notlar.txt
```

```test
eq(out, "yıllık rapor.txt,notlar.txt\n", "iki argüman")
eq(run(argv=["a b", "c", "d"]), "a b,c,d\n", "üç argüman, ilki boşluklu")
eq(run(argv=["tek"]), "tek\n", "tek argüman")
```

```solution
(IFS=,; echo "$*")
```

```hint
`"$*"` argümanları IFS'nin **ilk** karakteriyle birleştirir. IFS'yi yalnızca bir alt kabukta değiştir: `(IFS=,; echo "$*")`.
```
:::

::: gorev CSV satırları
Girdinin her satırı `ad,rol,cpu` biçiminde. Her satır için `ad (rol): cpu%` yazdır. Ad boşluk içerebilir.

```starter
while read satir; do
    echo "$satir"
done
```

```stdin
web01,web,72
yedek sunucu,yedek,12
```

```test
eq(run("web01,web,72\nyedek sunucu,yedek,12\n"), "web01 (web): 72%\nyedek sunucu (yedek): 12%\n", "iki satır")
eq(run("db01,db,91\n"), "db01 (db): 91%\n", "tek satır")
```

```solution
while IFS=, read -r ad rol cpu; do
    printf '%s (%s): %s%%\n' "$ad" "$rol" "$cpu"
done
```

```hint
`IFS=, read -r ad rol cpu` satırı virgülden üç değişkene böler. `printf` içinde yüzde işareti `%%` ile yazılır.
```
:::
