---
id: bs20
title: sed Ustalığı
summary: sed'in satır satır çalışma modeli, adresler ve aralıklar, s komutunun bayrakları, -E ile gruplar ve geri başvuru, a/i/c/y/q komutları ve -i ile yedekli yerinde düzenleme.
---

::: anlat sed nasıl düşünür
`sed` (stream editor) girdiyi satır satır okur. Her satır önce **desen alanına** konur, betikteki komutlar sırayla uygulanır, sonra desen alanı yazdırılır (`-n` verilmişse yazdırılmaz). Her komutun önüne, hangi satırlara uygulanacağını söyleyen bir **adres** yazılabilir:

| Adres | Hangi satırlar |
|---|---|
| `3` | 3. satır |
| `$` | son satır |
| `/HATA/` | düzenli ifadeyle eşleşenler |
| `3,7` | 3'ten 7'ye |
| `/başla/,/bitir/` | ilk desenden ikinci desene kadar (ikisi dahil) |
| `1~2` | 1'den başlayarak her 2 satırda bir (GNU) |
| `adres!` | adres dışındaki satırlar |

| Komut | Ne yapar |
|---|---|
| `p` | yazdır (genellikle `-n` ile) |
| `d` | sil (sonraki satıra geç) |
| `s/re/yeni/bayrak` | değiştir; `g` hepsi, `2` ikinci eşleşme, `I` harf duyarsız |
| `a metin`, `i metin`, `c metin` | sonrasına ekle / öncesine ekle / satırı değiştir |
| `y/abc/xyz/` | karakter karakter çevir |
| `q` | çık |
| `=` | satır numarasını yaz |

```bash
seq 1 10 | sed -n '3,5p'                      #! yalnızca 3–5
seq 1 10 | sed '2~3d' | tr '\n' ' '; echo     #! 2, 5, 8'i sil
printf 'a\n[ayar]\nb\nc\n[son]\nd\n' | sed -n '/\[ayar\]/,/\[son\]/p'
printf 'disk dolu\nağ tamam\n' | sed '/dolu/a  -> bilet açıldı'
```

### Değiştirme ustalığı
`-E` genişletilmiş düzenli ifadeleri açar (`+`, `?`, `{n}`, `( )` kaçışsız). Değiştirme kısmında `\1` … `\9` gruplara, `&` bütün eşleşmeye başvurur. Ayırıcı olarak `/` dışında bir karakter kullanmak yollarla çalışırken işi kolaylaştırır:

```bash
echo "2026-10-19 rapor" | sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\3.\2.\1/'
echo "web01 web02" | sed -E 's/web[0-9]+/[&]/g'
echo "/var/log/eski/a.log" | sed 's#/eski/#/arsiv/#'
```

### Yerinde düzenleme
`sed -i` dosyayı yerinde değiştirir; `-i.bak` önce `dosya.bak` adıyla bir yedek alır:

```bash
printf 'port=80\nhost=web01\n' > ayar.conf
sed -i.bak 's/^port=.*/port=8080/' ayar.conf
cat ayar.conf
cat ayar.conf.bak
```

> [!TUZAK]
> `sed -i` GNU ve BSD/macOS sürümlerinde farklı davranır: macOS'ta `-i` bir yedek uzantısı **zorunlu** bekler (`sed -i '' ...`). Taşınabilir betiklerde `-i.bak` kullanmak ya da çıktıyı geçici dosyaya yazıp `mv` etmek iki sistemde de çalışır.
:::

::: tahmin
Dört komutun çıktısı:

```bash
printf '1\n2\n3\n4\n5\n' | sed -n '2,4p'
printf 'a-b-c\n' | sed 's/-/+/'
printf 'a-b-c\n' | sed 's/-/+/g'
printf 'x\ny\n' | sed '1d'
```

???

`2`, `3`, `4`, `a+b-c`, `a+b+c`, `y`. `-n` otomatik yazdırmayı kapatır, `2,4p` yalnızca o aralığı yazar. `s` bayraksız yalnızca ilk eşleşmeyi, `g` ile hepsini değiştirir. `1d` ilk satırı siler.
:::

::: gorev Tarih biçimi
Girdideki bütün `YYYY-AA-GG` tarihlerini `GG.AA.YYYY` biçimine çevir. Bir satırda birden çok tarih olabilir.

```starter
sed 's/-/./g'
```

```stdin
rapor 2026-10-19 hazır
2026-10-12 ile 2026-10-18 arası
```

```test
eq(run("rapor 2026-10-19 hazır\n2026-10-12 ile 2026-10-18 arası\n"), "rapor 19.10.2026 hazır\n12.10.2026 ile 18.10.2026 arası\n", "tarihler çevrildi")
eq(run("sürüm 1-2-3 değişmez\n"), "sürüm 1-2-3 değişmez\n", "tarih olmayan metin değişmez")
```

```solution
sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\3.\2.\1/g'
```

```hint
`-E` ile gruplar: `([0-9]{4})-([0-9]{2})-([0-9]{2})`; değiştirme: `\3.\2.\1`. Bir satırdaki hepsi için `g`.
```
:::

::: gorev Ayar dosyasını temizle
Girdiden yorum satırlarını (başında boşluk olabilir, sonra `#`) ve boş ya da yalnızca boşluk içeren satırları sil; kalan satırlar değişmeden kalsın.

```starter
grep -v '#'
```

```stdin
# ana ayarlar
port=8080

  # eski değer: 80
host=web01   # yorum değil, satır kalır
   
```

```test
eq(run("# ana ayarlar\nport=8080\n\n  # eski değer: 80\nhost=web01   # yorum değil, satır kalır\n   \n"),
   "port=8080\nhost=web01   # yorum değil, satır kalır\n", "yalnızca ayar satırları")
ok("sed" in src, "sed kullan")
```

```solution
sed -E '/^[[:space:]]*(#|$)/d'
```

```hint
Tek desen iki durumu kapsar: satır başında boşluklar, ardından ya `#` ya da satır sonu: `^[[:space:]]*(#|$)`.
```
:::

::: gorev Yerinde düzenle
`ayar.conf` dosyasındaki `port` değerini `8443` yap; dosyayı **yerinde** düzenle ve orijinali `ayar.conf.bak` olarak yedekle. Sonra dosyanın yeni halini yazdır.

```setup
open("ayar.conf", "w", encoding="utf-8", newline="\n").write("host=web01\nport=80\nportal=acik\n")
```

```starter
sed 's/port=80/port=8443/' ayar.conf
```

```test
eq(out, "host=web01\nport=8443\nportal=acik\n", "yeni içerik (portal satırı değişmemeli)")
eq(open("ayar.conf", encoding="utf-8").read(), "host=web01\nport=8443\nportal=acik\n", "dosya yerinde değişti")
eq(open("ayar.conf.bak", encoding="utf-8").read(), "host=web01\nport=80\nportal=acik\n", "yedek eski içerikte")
```

```solution
sed -i.bak 's/^port=.*/port=8443/' ayar.conf
cat ayar.conf
```

```hint
`sed -i.bak` yedekli yerinde düzenleme yapar. Deseni `^port=` ile sabitle; yoksa `portal=` satırına da dokunabilirsin.
```
:::
