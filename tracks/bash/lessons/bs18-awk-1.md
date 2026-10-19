---
id: bs18
title: awk Dili I · Desen ve Eylem
summary: awk programının yapısı, BEGIN ve END, alanlar ve NF/NR/FNR, FS ve OFS, karşılaştırmalar ve düzenli ifade eşleşmesi, printf ve -v ile değer geçirmek.
---

::: anlat awk bir programlama dilidir
BS09'da awk'yi tek satırlık bir araç olarak kullandın. Aslında awk, satır satır veri işlemek için tasarlanmış **küçük bir programlama dilidir**. Bir awk programı `desen { eylem }` çiftlerinden oluşur; awk her satırı okur ve deseni tutan her satır için eylemi çalıştırır:

```bash
printf 'web01 web 72\ndb01 db 91\nweb03 web 18\n' |
awk '
    BEGIN { print "rapor başlıyor" }          #! ilk satırdan önce bir kez
    $2 == "web" { web++; toplam += $3 }       #! desen: 2. alan web ise
    $3 > 80 { print "yoğun:", $1 }             #! desen: 3. alan 80 üstü ise
    END { print web, "web sunucusu, ortalama", toplam / web }   #! en sonda bir kez
'
```

| Ad | Anlamı |
|---|---|
| `$0`, `$1`, `$NF` | bütün satır, 1. alan, son alan |
| `NF` | bu satırdaki alan sayısı |
| `NR`, `FNR` | toplam satır sayacı / o dosyadaki satır sayacı |
| `FS`, `-F` | girdi alan ayırıcısı (varsayılan: boşluklar) |
| `OFS` | çıktı alan ayırıcısı (`print a, b` arasına konur) |

Desen bir karşılaştırma (`$3 > 80`), bir düzenli ifade (`/HATA/`, `$1 ~ /^web/`), bir aralık (`NR == 2, NR == 4`) ya da boş (her satır) olabilir. Eylem yazılmazsa varsayılan eylem `print`'tir.

### Ayırıcılar ve biçim
```bash
printf 'ad,rol,cpu\nweb01,web,72\ndb01,db,91\n' |
awk -F, 'NR > 1 { printf "%-6s %5.1f\n", $1, $3 }'      #! başlığı atla, biçimli yaz

printf 'a b c\n' | awk 'BEGIN { OFS = "|" } { $1 = $1; print }'   #! alanı yeniden atamak satırı OFS ile kurar
```

Kabuktan değer geçirmek için `-v`: `awk -v esik=80 '$3 > esik' dosya`. awk programını tek tırnak içinde yazmak, `$1`'in kabuk tarafından genişletilmesini önler.

> [!DERİN]
> awk'de değişkenler bildirilmez; ilk kullanımda boş metin ya da 0'dır. Bir değer bağlama göre sayı ya da metin gibi davranır: `"10" + 5` 15'tir, `"10" "5"` (yan yana yazmak birleştirmedir) "105"tir. `$3 > 80` karşılaştırması iki taraf da sayıya benziyorsa sayısal, değilse metin karşılaştırmasıdır.
:::

::: tahmin
Tek satır yazar:

```bash
printf 'a 1\nb 2\nc 3\n' | awk '$2 > 1 { t += $2 } END { print NR, t }'
```

???

`3 5`. `NR` END bloğunda okunan toplam satır sayısıdır (3). Yalnızca 2. alanı 1'den büyük olan iki satırın değerleri toplanır: 2 + 3 = 5.
:::

::: gorev Rol toplamı
Girdi `ad,rol,cpu` başlıklı bir CSV. `-v rol=...` ile verilen roldeki sunucuların CPU toplamını yazdır. Rol, betiğe 1. argüman olarak gelir.

```starter
awk -F, '{ print $2 }'
```

```stdin
ad,rol,cpu
web01,web,72
db01,db,91
web03,web,18
```

```meta
argv: web
```

```test
csv = "ad,rol,cpu\nweb01,web,72\ndb01,db,91\nweb03,web,18\n"
eq(out, "90\n", "web: 72 + 18 = 90")
eq(run(csv, argv=["db"]), "91\n", "db: 91")
eq(run(csv, argv=["yok"]), "0\n", "eşleşme yoksa 0")
```

```solution
awk -F, -v rol="$1" 'NR > 1 && $2 == rol { t += $3 } END { print t + 0 }'
```

```hint
Kabuktaki `$1`'i awk'ye `-v rol="$1"` ile ver. Başlığı `NR > 1` ile atla.
```

```hint
Hiç eşleşme olmazsa `t` boş metin kalır; `print t + 0` onu 0'a çevirir.
```
:::

::: gorev Ayırıcı değiştir
Girdi `:` ile ayrılmış `ad:rol:cpu:ram` satırları. Her satırı **virgülle** ayrılmış `ad,cpu` olarak yazdır; en başa `ad,cpu` başlığını ekle.

```starter
awk -F: '{ print $1, $3 }'
```

```stdin
web01:web:72:16
db01:db:91:64
```

```test
eq(run("web01:web:72:16\ndb01:db:91:64\n"), "ad,cpu\nweb01,72\ndb01,91\n", "başlık ve iki satır")
```

```solution
awk -F: 'BEGIN { OFS = ","; print "ad", "cpu" } { print $1, $3 }'
```

```hint
`print a, b` arasına `OFS` konur; `BEGIN { OFS = "," }` ile virgül yap. Başlığı da BEGIN'de yazdır.
```
:::

::: gorev En uzun satır
Girdideki **en uzun** satırın uzunluğunu ve kendisini `uzunluk: satır` biçiminde yazdır. Eşit uzunlukta birden çok satır varsa ilkini al.

```starter
awk '{ print length($0) }'
```

```stdin
kısa
çok daha uzun bir satır
orta uzunlukta
```

```test
eq(run("kısa\nçok daha uzun bir satır\norta uzunlukta\n"), "23: çok daha uzun bir satır\n", "en uzun satır")
eq(run("ab\ncd\n"), "2: ab\n", "eşitlikte ilk")
```

```solution
awk 'length($0) > enuzun { enuzun = length($0); satir = $0 } END { print enuzun ": " satir }'
```

```hint
Şimdiye kadarki en uzunu bir değişkende tut: `length($0) > enuzun { ... }`. Yalnızca **büyükse** güncellersen eşitlikte ilk satır kalır.
```
:::
