---
id: bs09
title: sed ve awk
summary: sed ile akış düzenleme ve değiştirme; awk ile alan tabanlı süzme, hesaplama ve raporlama.
---

::: anlat sed: akış düzenleyici
`sed` metni satır satır okur ve verdiğin komutları uygular. En çok kullanılan komutu **değiştirmedir**: `s/desen/yeni/bayraklar`.

```bash
echo "renk: kırmızı, zemin: kırmızı" | sed 's/kırmızı/mavi/'     #! sadece ilk geçiş
echo "renk: kırmızı, zemin: kırmızı" | sed 's/kırmızı/mavi/g'    #! g: hepsi
echo "http://ornek.com/a" | sed 's#http://#https://#'           #! ayraç olarak # da olur
printf "a\nb\nc\nd\n" | sed -n '2,3p'                            #! -n + p: sadece 2-3. satırlar
printf "a\n# yorum\nb\n" | sed '/^#/d'                           #! deseni tutan satırları sil
echo "2026-10-19" | sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\3.\2.\1/'   #! -E: genişletilmiş regex, gruplar
```

Yol gibi `/` içeren metinlerde ayraç olarak `#`, `|` ya da `:` kullanmak, `\/\/` kaçışlarından kurtarır. Dosyayı yerinde değiştirmek için `sed -i` vardır; dikkatli kullan, önce `-i.bak` ile yedek al.

### awk: alanlarla düşünen dil
`awk` her satırı boşluklardan **alanlara** böler (`$1`, `$2`, ... `$0` tüm satır, `NF` alan sayısı, `NR` satır numarası) ve `desen { eylem }` kurallarını uygular:

```bash
cat > erisim.log <<'EOF'
10.0.0.5 GET /index.html 200 5120
10.0.0.8 POST /api/siparis 201 312
10.0.0.5 GET /yok 404 120
10.0.0.9 GET /api/rapor 500 90
EOF
awk '{ print $1, $4 }' erisim.log                     #! 1. ve 4. alan
awk '$4 >= 400 { print NR": "$3 }' erisim.log          #! koşullu: sadece hatalar
awk '{ toplam += $5 } END { print "toplam:", toplam }' erisim.log   #! END: hepsi okunduktan sonra
awk -F: '{ print $1 }' <<< "ali:x:1000"               #! -F: ayraç
awk '{ say[$1]++ } END { for (ip in say) print ip, say[ip] }' erisim.log | sort   #! dizilerle gruplama
```

`awk` tam bir programlama dilidir: değişkenler, ilişkisel diziler, `printf`, ondalıklı aritmetik. Bash'in tam sayı sınırına takıldığında hesap için de kullanılır: `awk 'BEGIN { print 7 / 2 }'`.

> [!NOT]
> Kabaca kural: **satır** seçmek için `grep`, satırda **değiştirmek** için `sed`, **sütunlarla** hesap ve rapor için `awk`. Üçü de regex konuşur.
:::

::: tahmin
İki satır yazar:

```bash
echo "renk: kırmızı" | sed 's/kırmızı/mavi/'
printf "a 1\nb 2\nc 3\n" | awk '{ toplam += $2 } END { print toplam }'
```

???

`renk: mavi`, sonra `6`. awk her satırın ikinci alanını toplar ve `END` bloğunda bir kez yazdırır.
:::

::: gorev Bağlantıları güvenli yap
`linkler.txt` dosyasındaki bütün `http://` öneklerini `https://` ile değiştirip sonucu yazdır (dosyayı değiştirmeden). Bir satırda birden fazla bağlantı olabilir.

```setup
open("linkler.txt", "w", encoding="utf-8", newline="\n").write(
    "http://ornek.com\nbelge: http://a.org/x ve http://b.org/y\nzaten https://guvenli.net\n")
```

```starter
sed 's/http:/https:/' linkler.txt
```

```test
eq(out, "https://ornek.com\nbelge: https://a.org/x ve https://b.org/y\nzaten https://guvenli.net\n", "hepsi https")
```

```solution
sed 's#http://#https://#g' linkler.txt
```

```hint
Bir satırdaki **bütün** geçişler için `g` bayrağı. `/` içeren desenlerde ayraç olarak `#` kullan.
```
:::

::: gorev Toplam trafik
`erisim.log` dosyasında beşinci alan yanıt boyutu (bayt). Toplamı `toplam: N bayt` biçiminde yazdır.

```setup
open("erisim.log", "w", encoding="utf-8", newline="\n").write(
    "10.0.0.5 GET / 200 5120\n10.0.0.8 POST /api 201 312\n10.0.0.5 GET /yok 404 120\n10.0.0.9 GET /r 500 90\n")
```

```starter
cut -d' ' -f5 erisim.log
```

```test
eq(out, "toplam: 5642 bayt\n", "5120+312+120+90")
ok("awk" in src, "awk kullan")
```

```solution
awk '{ toplam += $5 } END { print "toplam:", toplam, "bayt" }' erisim.log
```

```hint
`awk '{ t += $5 } END { print ... }'`
```
:::

::: gorev Hata raporu
Aynı biçimdeki `erisim.log` dosyasından durum kodu (4. alan) **400 ve üstü** olan satırları `durum yol` biçiminde yazdır.

```setup
open("erisim.log", "w", encoding="utf-8", newline="\n").write(
    "10.0.0.5 GET / 200 5120\n10.0.0.8 POST /api 201 312\n10.0.0.5 GET /yok 404 120\n10.0.0.9 GET /rapor 500 90\n10.0.0.3 GET /admin 403 64\n")
```

```starter
grep 40 erisim.log
```

```test
eq(out, "404 /yok\n500 /rapor\n403 /admin\n", "üç hata satırı")
```

```solution
awk '$4 >= 400 { print $4, $3 }' erisim.log
```

```hint
awk'ta koşul desen kısmına yazılır: `$4 >= 400 { print $4, $3 }`.
```
:::
