---
id: bs07
title: Borular ve Yönlendirme
summary: |, >, >>, <, 2>, 2>&1, /dev/null, here-doc ve tee; Unix felsefesinin kalbi.
kazanim: LPIC1 103.4
---

::: anlat Üç akış ve boru
Her süreç üç standart akışla doğar:

| Numara | Ad | Varsayılan |
|---|---|---|
| 0 | stdin (girdi) | klavye |
| 1 | stdout (çıktı) | ekran |
| 2 | stderr (hata) | ekran |

**Boru** `|`, bir komutun stdout'unu bir sonrakinin stdin'ine bağlar. Küçük araçları zincirleyerek büyük işler yapmak Unix felsefesinin kalbidir:

```bash
printf "b\na\nc\na\n" | sort | uniq            #! sırala, tekrarları at
echo "kelime sayısı: $(echo 'bir iki üç' | wc -w)"
```

### Yönlendirme
| Yazım | Anlamı |
|---|---|
| `komut > dosya` | stdout'u dosyaya yaz (dosyayı **sıfırlar**) |
| `komut >> dosya` | stdout'u dosyanın sonuna ekle |
| `komut < dosya` | stdin'i dosyadan oku |
| `komut 2> dosya` | stderr'i dosyaya yaz |
| `komut > dosya 2>&1` | ikisini de aynı dosyaya |
| `komut > /dev/null` | çıktıyı çöpe at |

```bash
echo "başlık" > rapor.txt
echo "satır 1" >> rapor.txt
ls /olmayan 2> hatalar.txt        #! hata ekrana değil dosyaya
cat rapor.txt
echo "hata dosyası: $(wc -l < hatalar.txt) satır"
```

> [!TUZAK]
> `komut > dosya 2>&1` ile `komut 2>&1 > dosya` aynı şey değildir: yönlendirmeler **soldan sağa** uygulanır. İkincisinde stderr, stdout'un **o anki** hedefine (ekrana) bağlanır, sonra stdout dosyaya taşınır. Ayrıca `sort dosya > dosya` dosyayı **boşaltır**: kabuk önce hedefi sıfırlar, sonra sort okumaya başlar.

### here-doc ve here-string
Çok satırlı metni bir komutun girdisine vermek için:

```bash
host="web01"
cat <<EOF > ayar.ini
[sunucu]
host = $host
port = 443
EOF
cat ayar.ini
tr 'a-z' 'A-Z' <<< "küçük harfler"   #! here-string: tek satırlık girdi
```

`<<'EOF'` (tırnaklı) yazarsan içerideki `$` açılmaz.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
printf "b\na\nc\n" > liste.txt
sort liste.txt | head -n 2
wc -l < liste.txt
```

???

`a`, `b`, `3`. `sort` alfabetik sıralar, `head -n 2` ilk iki satırı alır. `wc -l < dosya` dosyayı stdin'den okuduğu için sadece sayıyı yazar (`wc -l liste.txt` olsaydı dosya adını da yazardı).
:::

::: gorev Rapor dosyası
`rapor.txt` dosyasını oluştur: ilk satır `RAPOR`, sonra **sona ekleyerek** `disk: tamam` ve `ağ: tamam` satırları. En sonda dosyanın içeriğini ekrana yazdır.

```starter
echo "RAPOR" > rapor.txt
echo "disk: tamam" > rapor.txt
echo "ağ: tamam" > rapor.txt
cat rapor.txt
```

```test
eq(out, "RAPOR\ndisk: tamam\nağ: tamam\n", "ekran çıktısı")
eq(open("rapor.txt", encoding="utf-8").read(), "RAPOR\ndisk: tamam\nağ: tamam\n", "dosya içeriği")
```

```solution
echo "RAPOR" > rapor.txt
echo "disk: tamam" >> rapor.txt
echo "ağ: tamam" >> rapor.txt
cat rapor.txt
```

```hint
`>` dosyayı her seferinde sıfırlar; sona eklemek için `>>`.
```
:::

::: gorev Hataları ayır
Şu iki komutu çalıştır: `ls olmayan_dosya.txt` ve `ls mevcut.txt`. Hata mesajları ekrana değil `hata.log` dosyasına gitsin. Sonunda `bitti` yazdır.

```setup
open("mevcut.txt", "w").write("x")
```

```starter
ls olmayan_dosya.txt
ls mevcut.txt
echo "bitti"
```

```test
eq(out, "mevcut.txt\nbitti\n", "ekranda sadece normal çıktı")
ok("olmayan_dosya" in open("hata.log", encoding="utf-8").read(), "hata mesajı hata.log'da")
eq(hata_cikti, "", "standart hataya hiçbir şey gitmemeli")
```

```solution
ls olmayan_dosya.txt 2> hata.log
ls mevcut.txt 2>> hata.log
echo "bitti"
```

```hint
stderr'i yönlendirmek: `2> dosya`. İkinci komutun hatası da aynı dosyaya eklensin istiyorsan `2>>`.
```
:::

::: gorev Ayar dosyası üret
İlk argümanı host adı olarak al ve here-doc ile `ayar.ini` dosyasını şu içerikte oluştur (host argümandan gelsin), sonra dosyayı ekrana yazdır:

```cikti
[sunucu]
host = web01
port = 443
```

```starter
host=$1
echo "[sunucu]" > ayar.ini
cat ayar.ini
```

```meta
argv: web01
```

```test
beklenen = "[sunucu]\nhost = web01\nport = 443\n"
eq(out, beklenen, "web01 için çıktı")
eq(open("ayar.ini", encoding="utf-8").read(), beklenen, "dosya içeriği")
eq(run(argv=["db01"]), beklenen.replace("web01", "db01"), "db01 için")
ok("<<" in src, "here-doc kullan")
```

```solution
host=$1
cat <<EOF > ayar.ini
[sunucu]
host = $host
port = 443
EOF
cat ayar.ini
```

```hint
`cat <<EOF > ayar.ini` ... `EOF`. Kapanış `EOF` satırın başında ve tek başına olmalı.
```
:::
