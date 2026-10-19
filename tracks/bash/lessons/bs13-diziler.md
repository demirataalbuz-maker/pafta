---
id: bs13
title: Diziler ve İlişkisel Diziler
summary: Sıralı diziler, "${a[@]}" ile güvenli dolaşma, dilimleme, mapfile ile satırları diziye okumak, declare -A ile anahtar-değer tabloları ve sayaçlar.
---

::: anlat Sıralı diziler
Bir değişkende birden çok değer tutmak için dizi kullanılır. Elemanlar boşluk içerebilir ve doğru tırnaklandığı sürece bozulmaz:

```bash
sunucular=(web01 db01 "yedek sunucu")
echo "${sunucular[1]}"            #! indeks 0'dan başlar
echo "${#sunucular[@]}"           #! eleman sayısı
for s in "${sunucular[@]}"; do    #! her eleman ayrı ve bozulmadan
    echo "- $s"
done
sunucular+=(cache01)              #! sona ekle
echo "${sunucular[@]:1:2}"        #! dilim: 1'den başlayarak 2 eleman
echo "${!sunucular[@]}"           #! indeksler
```

`"${a[@]}"`, `"$@"` gibi davranır: her eleman ayrı bir kelimedir. Tırnaksız `${a[@]}` ya da `${a[*]}` kelime bölmeye uğrar ve "yedek sunucu"yu ikiye ayırır.

### Satırları diziye okumak
`mapfile` (eş anlamlısı `readarray`) her satırı bir eleman yapar; `-t` satır sonlarını atar:

```bash
mapfile -t satirlar <<'EOF'
birinci satır
ikinci satır
EOF
echo "${#satirlar[@]} satır, ilki: ${satirlar[0]}"
```

> [!TUZAK]
> `dizi=( $(komut) )` yazımı çıktıyı satırlara değil **kelimelere** böler ve glob genişlemesine de uğratır: boşluklu satırlar parçalanır, `*` içeren satırlar dosya adlarına dönüşür. Satır satır okumak için her zaman `mapfile -t dizi < <(komut)`.
:::

::: anlat İlişkisel diziler
`declare -A` anahtarı metin olan bir tablo yaratır; Python'daki sözlüğe karşılık gelir:

```bash
declare -A cpu=([web01]=72 [db01]=91)
cpu[cache01]=84
echo "${cpu[db01]}"
echo "${#cpu[@]} sunucu"
for ad in "${!cpu[@]}"; do         #! anahtarlar
    echo "$ad=${cpu[$ad]}"
done | sort                         #! anahtar sırası garanti değil: sırala
```

Sayaç kalıbı, metin işlemenin en sık kullanılan aracıdır:

```bash
declare -A say
for kelime in web db web yedek web; do
    (( say[$kelime]++ ))
done
for k in "${!say[@]}"; do echo "$k ${say[$k]}"; done | sort -k2,2nr
```

> [!NOT]
> İlişkisel dizinin anahtar sırası tanımsızdır; çıktının sırası önemliyse sonucu `sort`'tan geçir. `[[ -v cpu[web01] ]]` bir anahtarın tanımlı olup olmadığını sınar.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
a=(bir "iki üç" dört)
echo "${#a[@]}"
for x in "${a[@]}"; do echo "<$x>"; done
a+=(beş)
echo "${a[@]:1:2}"
echo "${!a[@]}"
```

???

`3`, `<bir>`, `<iki üç>`, `<dört>`, `iki üç dört`, `0 1 2 3`. Dizide üç eleman var; tırnaklı `"${a[@]}"` "iki üç"yü bozmaz. `beş` eklenince dört eleman olur. Dilim 1. indeksten başlayıp iki eleman alır ve echo onları boşlukla yan yana yazar. `${!a[@]}` indeksleri verir.
:::

::: gorev Ters sıra
Girdinin satırlarını **ters sırayla** yazdır. `tac` kullanma; satırları bir diziye oku.

```starter
while read -r satir; do
    echo "$satir"
done
```

```stdin
birinci
ikinci satır
üçüncü
```

```test
eq(run("birinci\nikinci satır\nüçüncü\n"), "üçüncü\nikinci satır\nbirinci\n", "üç satır, boşluklar korunur")
eq(run("tek\n"), "tek\n", "tek satır")
ok("tac" not in src, "tac kullanma")
```

```solution
mapfile -t satirlar
for (( i = ${#satirlar[@]} - 1; i >= 0; i-- )); do
    echo "${satirlar[i]}"
done
```

```hint
`mapfile -t satirlar` girdiyi diziye okur. Sondan başa: `for (( i = ${#satirlar[@]} - 1; i >= 0; i-- ))`.
```
:::

::: gorev Kelime sıklığı
Girdideki kelimeleri say ve `kelime sayı` biçiminde, **çoktan aza**, eşitlikte kelimeye göre artan sırayla yazdır. Sayımı bir ilişkisel diziyle yap.

```starter
cat
```

```stdin
web db web
db web yedek
```

```test
eq(run("web db web\ndb web yedek\n"), "web 3\ndb 2\nyedek 1\n", "web 3, db 2, yedek 1")
eq(run("b a\na b\n"), "a 2\nb 2\n", "eşitlikte kelimeye göre")
ok("declare -A" in src, "declare -A ile say")
```

```solution
declare -A say
while read -r -a kelimeler; do
    for k in "${kelimeler[@]}"; do
        (( say[$k]++ ))
    done
done
for k in "${!say[@]}"; do
    echo "$k ${say[$k]}"
done | sort -k2,2nr -k1,1
```

```hint
`read -r -a kelimeler` satırı kelimelerden bir diziye okur. Sayaç: `(( say[$k]++ ))`.
```

```hint
Sıralama: `sort -k2,2nr -k1,1`: önce 2. alana göre sayısal azalan, sonra 1. alana göre.
```
:::

::: gorev Rollere göre grupla
Girdinin her satırı `ad rol`. Her rol için `rol: ad1 ad2 …` yazdır; roller alfabetik, adlar girdi sırasıyla.

```starter
while read -r ad rol; do
    echo "$rol: $ad"
done
```

```stdin
web01 web
db01 db
web02 web
```

```test
eq(run("web01 web\ndb01 db\nweb02 web\n"), "db: db01\nweb: web01 web02\n", "iki rol")
eq(run("a x\nb x\nc x\n"), "x: a b c\n", "tek rol")
```

```solution
declare -A grup
while read -r ad rol; do
    grup[$rol]+="${grup[$rol]:+ }$ad"
done
for rol in "${!grup[@]}"; do
    echo "$rol: ${grup[$rol]}"
done | sort
```

```hint
Her rolün adlarını bir metinde biriktir: `grup[$rol]+=" $ad"`. Baştaki boşluğu önlemek için `${grup[$rol]:+ }`: doluysa bir boşluk, değilse hiçbir şey.
```
:::
