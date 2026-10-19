---
id: bs25
title: Tarih, Saat ve Sayılar
summary: date biçimleri ve -d ile tarih hesabı, epoch saniyeleri, saat dilimi ve TZ, tarihleri metin olarak karşılaştırmak, tam sayı aritmetiği ve ondalık hesap için awk.
---

::: anlat date ile zaman
`date +BİÇİM` şimdiki zamanı istenen biçimde yazar; GNU `date -d` ise bir tarihi okuyup hesap yapar:

| Biçim | Anlamı | Örnek |
|---|---|---|
| `%F`, `%T` | tarih, saat | `2026-10-19`, `08:15:02` |
| `%Y%m%d-%H%M%S` | dosya adına uygun damga | `20261019-081502` |
| `%s` | epoch: 1970-01-01 00:00 UTC'den beri saniye | `1792396800` |
| `%A`, `%j`, `%V` | gün adı, yılın günü, ISO hafta | `Monday`, `292`, `43` |

```bash
TZ=UTC date -d '2026-10-19 08:00' +%s           #! tarihi epoch'a çevir
TZ=UTC date -d '@1792396800' '+%F %H:%M'        #! epoch'u tarihe çevir
date -d '2026-10-19 +3 days' +%F               #! göreli hesap
date -d '2026-10-19 next monday' +%F
```

**Süre hesabı** için iki zamanı epoch'a çevirip çıkarmak en güvenilir yoldur:

```bash
bas=$(TZ=UTC date -d '2026-10-19T08:15' +%s)
son=$(TZ=UTC date -d '2026-10-19T11:45' +%s)
echo "$(( (son - bas) / 60 )) dakika"
```

> [!TUZAK]
> Saat dilimi belirtilmeyen zamanlar makinenin yerel saat dilimiyle yorumlanır. Aynı betik İstanbul'da ve UTC'de çalışan bir sunucuda farklı epoch değerleri üretir; yaz saati geçişlerinde bir gün 23 ya da 25 saat sürebilir. Kayıt analizinde zamanları **UTC'de** tut ve hesapla: `TZ=UTC date ...`.

ISO biçimindeki (`YYYY-AA-GG SS:DD`) zamanlar metin olarak karşılaştırıldığında da doğru sıralanır: `[[ "2026-10-12" < "2026-10-19" ]]`.

### Sayılar
Bash yalnızca **tam sayı** aritmetiği yapar: `$(( 7 / 2 ))` 3'tür. Ondalık hesap için awk ya da `printf` kullanılır:

```bash
echo $(( 7 / 2 )) $(( 7 % 2 )) $(( 2 ** 10 ))
awk 'BEGIN { printf "%.2f\n", 7 / 2 }'
printf '%.1f\n' 72.46
printf '%02d:%02d\n' $(( 125 / 60 )) $(( 125 % 60 ))   #! 125 dakika → 02:05
seq -s, 0 5 20                                          #! 0'dan 20'ye 5'er
```
:::

::: tahmin
Dört satır yazar:

```bash
TZ=UTC date -d '2026-10-19 08:00' +%s
TZ=UTC date -d '@1792396800' '+%F %H:%M'
date -d '2026-10-19 +3 days' +%F
printf '%02d:%02d\n' $(( 125 / 60 )) $(( 125 % 60 ))
```

???

`1792396800`, `2026-10-19 08:00`, `2026-10-22`, `02:05`. İlk iki satır birbirinin tersidir: UTC'de 19 Ekim 08:00 epoch'a çevrilir, aynı sayı tarihe geri döner. Üç gün sonrası 22 Ekim'dir. 125 dakika 2 saat 5 dakikadır; `%02d` tek haneli sayıları sıfırla doldurur.
:::

::: gorev Süreler
Girdinin her satırı boşlukla ayrılmış iki zaman: `başlangıç bitiş` (`YYYY-AA-GGTSS:DD`). Her satır için aradaki süreyi **dakika** olarak yazdır. Hesabı UTC'de yap.

```starter
while read -r bas son; do
    echo "$bas $son"
done
```

```stdin
2026-10-19T08:15 2026-10-19T11:45
2026-10-18T22:00 2026-10-19T01:30
```

```test
eq(run("2026-10-19T08:15 2026-10-19T11:45\n2026-10-18T22:00 2026-10-19T01:30\n"), "210\n210\n", "aynı gün ve gece yarısını aşan")
eq(run("2026-10-12T09:00 2026-10-13T10:00\n"), "1500\n", "bir gün bir saat")
```

```solution
while read -r bas son; do
    b=$(TZ=UTC date -d "$bas" +%s)
    s=$(TZ=UTC date -d "$son" +%s)
    echo $(( (s - b) / 60 ))
done
```

```hint
İki zamanı `TZ=UTC date -d "$bas" +%s` ile epoch'a çevir, farkı 60'a böl.
```
:::

::: gorev Gün farkı
Betik iki tarih argümanı alsın (`YYYY-AA-GG`) ve ikincinin birinciden kaç gün sonra olduğunu `N gün` biçiminde yazdırsın (önceyse eksi).

```starter
echo "$1 $2"
```

```meta
argv: 2026-10-19 2026-11-02
```

```test
eq(out, "14 gün\n", "19 Ekim → 2 Kasım")
eq(run(argv=["2026-11-02", "2026-10-19"]), "-14 gün\n", "ters sıra → eksi")
eq(run(argv=["2026-12-31", "2027-01-01"]), "1 gün\n", "yıl geçişi")
```

```solution
b=$(TZ=UTC date -d "$1" +%s)
s=$(TZ=UTC date -d "$2" +%s)
echo "$(( (s - b) / 86400 )) gün"
```

```hint
Bir gün 86400 saniyedir. UTC'de hesaplarsan yaz saati geçişi farkı bozmaz.
```
:::

::: gorev Ondalık ortalama
Girdinin her satırı bir sayı. Ortalamayı **iki ondalık haneyle** yazdır. Girdi boşsa `0.00` yazdır.

```starter
toplam=0; adet=0
while read -r x; do
    toplam=$(( toplam + x )); adet=$(( adet + 1 ))
done
echo $(( toplam / adet ))
```

```stdin
72
91
18
```

```test
eq(run("72\n91\n18\n"), "60.33\n", "60.33")
eq(run("1\n2\n"), "1.50\n", "1.50")
eq(run(""), "0.00\n", "boş girdi")
eq(run("2.5\n3.5\n"), "3.00\n", "ondalıklı girdiler")
```

```solution
awk '{ t += $1; n++ } END { printf "%.2f\n", n ? t / n : 0 }'
```

```hint
Bash ondalık hesap yapmaz ve ondalıklı girdiyi de okuyamaz. Bütün işi awk'ye ver: `awk '{ t += $1; n++ } END { ... }'`.
```
:::
