---
id: bs19
title: awk Dili II · Diziler ve Fonksiyonlar
summary: İlişkisel dizilerle gruplamak, for (k in a), sıralı dolaşma, split, sub ve gsub, match ve substr, kendi fonksiyonların ve iki dosyayı birleştiren FNR==NR kalıbı.
---

::: anlat Diziler ile gruplamak
awk dizileri **ilişkiseldir**: indeks herhangi bir metin olabilir. Bu, awk'yi küçük bir veritabanına çevirir; "rol başına toplam", "IP başına istek sayısı" gibi soruların cevabı tek satırdır:

```bash
printf 'web01 web 72\ndb01 db 91\nweb03 web 18\ncache01 onbellek 84\n' |
awk '
    { adet[$2]++; toplam[$2] += $3 }
    END {
        for (rol in adet)
            printf "%-9s %d sunucu, ort %.1f\n", rol, adet[rol], toplam[rol] / adet[rol]
    }
' | sort
```

`for (k in a)` sırası tanımsızdır. Sonuç sıralı olmalıysa çıktıyı `sort`'a ver ya da GNU awk'de dolaşma sırasını ayarla: `PROCINFO["sorted_in"] = "@ind_str_asc"` (anahtara göre), `"@val_num_desc"` (değere göre azalan).

`(k in a)` bir anahtarın varlığını sınar, `delete a[k]` siler.

### Metin fonksiyonları
| Fonksiyon | Ne yapar |
|---|---|
| `length(s)` | uzunluk |
| `substr(s, baş, uz)` | alt metin (1'den sayar) |
| `index(s, t)` | t'nin s içindeki konumu (yoksa 0) |
| `split(s, dizi, ayırıcı)` | s'yi böler, parça sayısını döndürür |
| `sub(/re/, yeni, hedef)`, `gsub(...)` | ilk / bütün eşleşmeleri değiştirir, sayıyı döndürür |
| `match(s, /re/)` | eşleşme konumu; `RSTART` ve `RLENGTH`'i doldurur |
| `tolower(s)`, `toupper(s)` | harf dönüşümü |
| `sprintf(biçim, ...)` | biçimli metin döndürür |

```bash
echo "2026-10-19 08:15:02 kullanici=ece sure=125ms" |
awk '{
    split($1, t, "-"); print "gün:", t[3]
    if (match($0, /sure=[0-9]+/)) print "süre:", substr($0, RSTART + 5, RLENGTH - 5)
    satir = $0; gsub(/[0-9]+/, "N", satir); print satir
}'
```

### Kendi fonksiyonların
```bash
awk 'function yuzde(a, b) { return b ? 100 * a / b : 0 }
     BEGIN { printf "%.1f%%\n", yuzde(3, 8) }'
```

### İki dosyayı birleştirmek: FNR == NR
awk birden çok dosyayı sırayla okur. `NR` toplam sayaçtır, `FNR` her dosyada baştan başlar; ikisi yalnızca **ilk** dosyada eşittir. Bu yüzden `FNR == NR` "birinci dosyayı okuyorum" demektir: önce bir sözlük doldurulur, ikinci dosyada kullanılır:

```bash
printf 'web01 10.0.0.5\ndb01 10.0.0.9\n' > adresler.txt
printf 'web01 72\ndb01 91\ncache01 84\n' > cpu.txt
awk 'FNR == NR { ip[$1] = $2; next }       #! 1. dosya: sözlük doldur, sonraki satıra geç
     { print $1, ($1 in ip ? ip[$1] : "-"), $2 }' adresler.txt cpu.txt
```
:::

::: tahmin
Çıktı ne olur?

```bash
printf 'a x\nb y\nc x\nd x\n' | awk '{ s[$2] = s[$2] $1 } END { print s["x"], length(s), ("z" in s) }'
```

???

`acd 2 0`. Her satırın 1. alanı, 2. alana göre bir metnin sonuna eklenir: x için "acd", y için "b". Dizide iki anahtar var; "z" anahtarı hiç oluşmadığı için `in` sınaması 0 verir.
:::

::: gorev Rol başına ortalama
Girdinin her satırı `ad rol cpu`. Her rol için `rol ortalama` yazdır; ortalama bir ondalık hane olsun, roller alfabetik sıralı.

```starter
awk '{ print $2, $3 }'
```

```stdin
web01 web 72
db01 db 91
web03 web 18
```

```test
eq(run("web01 web 72\ndb01 db 91\nweb03 web 18\n"), "db 91.0\nweb 45.0\n", "db 91.0, web 45.0")
eq(run("a x 1\nb x 2\n"), "x 1.5\n", "tek rol")
```

```solution
awk '{ adet[$2]++; toplam[$2] += $3 }
     END { PROCINFO["sorted_in"] = "@ind_str_asc"
           for (r in adet) printf "%s %.1f\n", r, toplam[r] / adet[r] }'
```

```hint
İki dizi tut: `adet[$2]++` ve `toplam[$2] += $3`. Sonda ortalamayı `printf "%.1f"` ile yaz.
```

```hint
Sıralı dolaşmak için `PROCINFO["sorted_in"] = "@ind_str_asc"` ya da çıktıyı `sort`'a ver.
```
:::

::: gorev Adresleri ekle
`adresler.txt` dosyasında `ad ip`, `cpu.txt` dosyasında `ad cpu` satırları var. `cpu.txt`'deki her sunucu için `ad ip cpu` yazdır; adresi bilinmiyorsa ip yerine `-` yaz. Sıra `cpu.txt`'deki gibi kalsın. Tek bir awk komutu kullan.

```setup
open("adresler.txt", "w", encoding="utf-8", newline="\n").write("db01 10.0.0.9\nweb01 10.0.0.5\n")
open("cpu.txt", "w", encoding="utf-8", newline="\n").write("web01 72\ncache01 84\ndb01 91\n")
```

```starter
cat cpu.txt
```

```test
eq(out, "web01 10.0.0.5 72\ncache01 - 84\ndb01 10.0.0.9 91\n", "adresli satırlar, cpu.txt sırasıyla")
ok("FNR" in src, "FNR == NR kalıbını kullan")
```

```solution
awk 'FNR == NR { ip[$1] = $2; next } { print $1, ($1 in ip ? ip[$1] : "-"), $2 }' adresler.txt cpu.txt
```

```hint
`FNR == NR { ip[$1] = $2; next }` birinci dosyayı sözlüğe okur. İkinci dosyada `($1 in ip ? ip[$1] : "-")`.
```
:::

::: gorev Log şablonları
Girdi bir uygulama logu. Her satırdaki **sayıları** `N` ile değiştirerek satırın "şablonunu" çıkar; her şablonun kaç kez geçtiğini `sayı şablon` biçiminde, çoktan aza (eşitlikte şablona göre artan) yazdır.

```starter
awk '{ print }'
```

```stdin
istek 12 ms sürdü
istek 340 ms sürdü
disk 2 yüzde 91 dolu
istek 7 ms sürdü
```

```test
eq(run("istek 12 ms sürdü\nistek 340 ms sürdü\ndisk 2 yüzde 91 dolu\nistek 7 ms sürdü\n"),
   "3 istek N ms sürdü\n1 disk N yüzde N dolu\n", "iki şablon")
ok("gsub" in src, "gsub kullan")
```

```solution
awk '{ s = $0; gsub(/[0-9]+/, "N", s); say[s]++ }
     END { for (k in say) print say[k], k }' | sort -k1,1nr -k2
```

```hint
Satırı bir değişkene kopyala ve `gsub(/[0-9]+/, "N", s)` ile sayıları değiştir; şablonları bir dizide say.
```

```hint
Sıralama: `sort -k1,1nr -k2`.
```
:::
