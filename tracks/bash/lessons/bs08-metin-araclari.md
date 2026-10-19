---
id: bs08
title: Metin Araçları
summary: grep, cut, sort, uniq, wc, head, tail ve tr; boru hattıyla log analizi.
---

::: anlat Küçük araçlar, büyük işler
Unix'in metin araçları tek bir işi iyi yapar ve borularla birleşir. Log analizinin büyük kısmı bu yedi-sekiz komutla yapılır:

| Komut | İş | Sık seçenekler |
|---|---|---|
| `grep desen` | desene uyan satırlar | `-i` harf duyarsız, `-v` uymayanlar, `-c` say, `-E` genişletilmiş regex, `-o` sadece eşleşen kısım |
| `cut` | sütun kes | `-d' '` ayraç, `-f1,3` alanlar |
| `sort` | sırala | `-n` sayısal, `-r` ters, `-u` tekrarsız, `-k2` 2. alana göre |
| `uniq` | ardışık tekrarları birleştir | `-c` say (önce `sort` şart!) |
| `wc` | say | `-l` satır, `-w` kelime |
| `head` / `tail` | baş / son | `-n 5` |
| `tr` | karakter dönüştür/sil | `tr -d '\r'`, `tr ',' '\n'` |

```bash
cat > app.log <<'EOF'
INFO istek tamam
ERROR veritabanı zaman aşımı
INFO istek tamam
WARN yavaş yanıt
ERROR veritabanı zaman aşımı
ERROR disk dolu
EOF
grep -c ERROR app.log                         #! kaç hata satırı
grep ERROR app.log | cut -d' ' -f2- | sort | uniq -c | sort -rn   #! en sık hatalar
grep -v INFO app.log | head -n 2              #! INFO olmayanların ilk ikisi
```

İkinci satırdaki boru hattı "**say, grupla, sırala**" kalıbıdır: `sort | uniq -c | sort -rn`. Python'da `Counter.most_common()` (P31), SIEM'lerde `stats count by` / `summarize count() by` ne yapıyorsa bu satır da onu yapar.

> [!NOT]
> `uniq` sadece **ardışık** tekrarları birleştirir; bu yüzden önüne neredeyse her zaman `sort` gelir. `sort | uniq` yerine `sort -u` de yazılabilir.

> [!GÜVENLİK]
> Olay müdahalesinde ilk dakikalarda bir sunucuya bağlanıp `grep`, `cut`, `sort | uniq -c` ile auth ve web loglarını süzebilmek hâlâ temel bir beceridir: SIEM'in her zaman orada olmadığı, ya da logun SIEM'e hiç ulaşmadığı durumlar vardır.
:::

::: tahmin
İki satır yazar:

```bash
printf "ali\nveli\nali\nayse\n" | sort -u | wc -l
echo "2026-10-19 08:15:02 FAIL root" | cut -d' ' -f3
```

???

`3`, sonra `FAIL`. `sort -u` dört satırı üç benzersiz satıra indirir. `cut -d' ' -f3` boşlukla ayrılmış üçüncü alanı verir.
:::

::: gorev Hata sayısı
`app.log` dosyasında `ERROR` içeren satırların **sayısını** yazdır.

```setup
open("app.log", "w", encoding="utf-8", newline="\n").write(
    "INFO basladi\nERROR baglanti koptu\nINFO istek\nERROR disk dolu\nWARN yavas\nERROR baglanti koptu\n")
```

```starter
grep ERROR app.log
```

```test
eq(out, "3\n", "3 hata satırı")
```

```solution
grep -c ERROR app.log
```

```hint
`grep`'in sayma seçeneği: `-c`.
```
:::

::: gorev Benzersiz kullanıcılar
`giris.log` dosyasının her satırı `tarih saat durum kullanıcı` biçiminde. Dördüncü alandaki kullanıcıları **tekrarsız ve alfabetik** olarak yazdır.

```setup
open("giris.log", "w", encoding="utf-8", newline="\n").write(
    "2026-10-19 08:00:01 OK veli\n2026-10-19 08:00:05 FAIL root\n2026-10-19 08:01:00 OK ali\n"
    "2026-10-19 08:02:13 FAIL root\n2026-10-19 08:03:40 OK veli\n2026-10-19 08:04:02 OK ayse\n")
```

```starter
cat giris.log
```

```test
eq(out, "ali\nayse\nroot\nveli\n", "dört benzersiz kullanıcı")
```

```solution
cut -d' ' -f4 giris.log | sort -u
```

```hint
`cut -d' ' -f4` alanı keser; `sort -u` sıralayıp tekrarları atar.
```
:::

::: gorev En yoğun istemciler
`web.log` dosyasında her satırın ilk alanı istemci IP'si. En çok istek yapan **3 IP'yi**, çoktan aza, `ip sayı` biçiminde yazdır.

```setup
satirlar = (["10.0.0.5 GET /"] * 5 + ["10.0.0.8 GET /api"] * 3 + ["10.0.0.9 POST /giris"] * 2 + ["10.0.0.7 GET /x"])
open("web.log", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
cut -d' ' -f1 web.log | sort | uniq
```

```test
eq(out, "10.0.0.5 5\n10.0.0.8 3\n10.0.0.9 2\n", "ilk üç IP ve sayıları")
```

```solution
cut -d' ' -f1 web.log | sort | uniq -c | sort -rn | head -n 3 | awk '{ print $2, $1 }'
```

```hint
Kalıp: `cut ... | sort | uniq -c | sort -rn | head -n 3`. `uniq -c` çıktısı `   5 10.0.0.5` biçimindedir.
```

```hint
Sütunların yerini değiştirmek için en kolayı `awk '{ print $2, $1 }'` (P09'da göreceksin).
```
:::
