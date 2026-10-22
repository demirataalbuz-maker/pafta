---
id: bs21
title: Sıralama, Birleştirme ve Tablo Araçları
summary: sort'un anahtar ve kip seçenekleri, sürüm sıralaması, uniq, join ve comm ile kümeler, paste, column ile hizalı tablo, cut ve tr ileri kullanım.
kazanim: LPIC1 103.2
---

::: anlat sort'u gerçekten tanımak
`sort` basit görünür ama seçenekleri onu güçlü bir araca çevirir:

| Seçenek | Anlamı |
|---|---|
| `-t,` | alan ayırıcı virgül |
| `-k2,2` | yalnızca 2. alana göre (`-k2` 2. alandan satır sonuna kadar demektir!) |
| `-n`, `-h`, `-V` | sayısal / insan okunur boyut (2K, 1G) / sürüm sırası |
| `-r` | ters |
| `-u` | tekrarları at |
| `-s` | kararlı: eşit anahtarlarda girdi sırasını koru |
| `-k3,3nr -k1,1` | önce 3. alana göre sayısal azalan, eşitlikte 1. alana göre |

```bash
printf 'web01,web,72\ncache01,onbellek,84\nweb03,web,18\ndb01,db,84\n' | sort -t, -k3,3nr -k1,1
printf '2K\n1G\n512\n30M\n' | sort -h
printf 'v1.10\nv1.9\nv1.2\n' | sort -V
```

> [!TUZAK]
> `-k2` "2. alan" değil, "2. alandan **satır sonuna kadar**" demektir. Yalnızca bir alana göre sıralamak için başlangıç ve bitişi birlikte ver: `-k2,2`. Sıralama düzeni de yerel ayara bağlıdır; betiklerde aynı sonucu almak için `LC_ALL=C sort` kullanılır.

### Kümeler: uniq, comm, join
`uniq` yalnızca **yan yana** tekrarları görür, bu yüzden hemen her zaman `sort`'tan sonra gelir: `-c` say, `-d` yalnızca tekrarlananlar, `-u` yalnızca bir kez geçenler.

`comm` iki **sıralı** listeyi üç sütunda karşılaştırır (yalnız 1'de, yalnız 2'de, ikisinde); `-12` ortakları, `-23` yalnız 1'dekileri verir. `join` iki sıralı dosyayı ortak alana göre birleştirir; SQL'deki JOIN'in kabuktaki karşılığıdır:

```bash
printf 'web01 72\ndb01 91\ncache01 84\n' > cpu.txt
printf 'db01 10.0.0.9\nweb01 10.0.0.5\n' > ip.txt
join <(sort cpu.txt) <(sort ip.txt)              #! iç birleştirme
join -a1 -e '-' -o 0,1.2,2.2 <(sort cpu.txt) <(sort ip.txt)   #! sol birleştirme, eksik alan '-'
```

### Sütunlarla çalışmak
```bash
printf 'web01\ndb01\n' > adlar.txt
printf '72\n91\n' > cpular.txt
paste -d, adlar.txt cpular.txt                   #! dosyaları yan yana birleştir
printf 'ad,rol,cpu\nweb01,web,72\ncache01,onbellek,84\n' | column -t -s,    #! hizalı tablo
echo "2026-10-19T08:15:02" | cut -c12-16          #! karakter aralığı
echo "a  b   c" | tr -s ' '                       #! tekrarlanan boşlukları sıkıştır
echo "Web-01" | tr -d '-' | tr 'A-Z' 'a-z'
```
:::

::: tahmin
İki komutun çıktısı:

```bash
printf 'web10\nweb2\nweb1\n' | sort
printf 'web10\nweb2\nweb1\n' | sort -V
```

???

`web1`, `web10`, `web2`; sonra `web1`, `web2`, `web10`. Düz `sort` metni karakter karakter karşılaştırır: "web10"un dördüncü karakteri "1", "web2"ninki "2" olduğu için web10 önce gelir. `-V` içindeki sayıları sayı olarak karşılaştırır.
:::

::: gorev Sürümleri sırala
Girdideki sürüm numaralarını **en yeniden en eskiye** sırala.

```starter
sort -r
```

```stdin
2.10.0
2.9.1
10.0
2.10.1
```

```test
eq(run("2.10.0\n2.9.1\n10.0\n2.10.1\n"), "10.0\n2.10.1\n2.10.0\n2.9.1\n", "sürüm sırasıyla, azalan")
```

```solution
sort -V -r
```

```hint
Düz `sort -r` "2.9.1"i "2.10.1"den büyük sanar. Sürüm sıralaması: `-V`.
```
:::

::: gorev İki listeyi birleştir
`cpu.txt` (`ad cpu`) ve `ip.txt` (`ad ip`) sırasız. **Her iki** dosyada da bulunan sunucular için `ad cpu ip` yazdır, ada göre sıralı. `join` kullan.

```setup
open("cpu.txt", "w", encoding="utf-8", newline="\n").write("web01 72\ndb01 91\ncache01 84\n")
open("ip.txt", "w", encoding="utf-8", newline="\n").write("db01 10.0.0.9\nweb01 10.0.0.5\nyedek01 10.0.0.7\n")
```

```starter
cat cpu.txt ip.txt
```

```test
eq(out, "db01 91 10.0.0.9\nweb01 72 10.0.0.5\n", "iki ortak sunucu")
ok("join" in src, "join kullan")
```

```solution
join <(sort cpu.txt) <(sort ip.txt)
```

```hint
`join` iki dosyanın da birleştirme alanına göre **sıralı** olmasını ister: `join <(sort cpu.txt) <(sort ip.txt)`.
```
:::

::: gorev Tekrar eden adresler
Girdinin her satırı bir istemci adresi. **Birden fazla kez** geçen adresleri, kaç kez geçtikleriyle `sayı adres` biçiminde, çoktan aza (eşitlikte adrese göre) yazdır.

```starter
sort | uniq -c
```

```stdin
10.0.0.5
10.0.0.9
10.0.0.5
10.0.0.7
10.0.0.9
10.0.0.5
```

```test
eq(run("10.0.0.5\n10.0.0.9\n10.0.0.5\n10.0.0.7\n10.0.0.9\n10.0.0.5\n"), "3 10.0.0.5\n2 10.0.0.9\n", "yalnızca tekrarlananlar")
```

```solution
sort | uniq -c | awk '$1 > 1 { print $1, $2 }' | sort -k1,1nr -k2,2
```

```hint
`uniq -c` sayıyı başa, boşluklarla hizalı koyar. `awk '$1 > 1 { print $1, $2 }'` hem süzer hem boşlukları temizler.
```
:::
