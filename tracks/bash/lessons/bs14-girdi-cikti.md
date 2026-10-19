---
id: bs14
title: Girdi ve Çıktı Ustalığı
summary: printf biçimleri, read seçenekleri, here-doc çeşitleri ve here-string, süreç ikamesi <( ), dosya tanımlayıcıları ve yönlendirme sırasının önemi.
---

::: anlat printf ve read
`printf` biçim belirteçleriyle hizalı, öngörülebilir çıktı verir; argüman biçimden fazlaysa biçim **tekrar** uygulanır:

```bash
printf '%-8s|%5.1f|%03d\n' web01 72.46 7
printf '%s\n' bir iki üç                #! biçim her argüman için tekrar eder
printf '%q\n' "boşluklu ad.txt"         #! kabuğa güvenli tırnaklanmış hali
printf -v satir '%s-%s' web 01          #! çıktıyı bir değişkene yaz
echo "$satir"
```

`read`'in sık kullanılan seçenekleri:

| Seçenek | Anlamı |
|---|---|
| `-r` | ters eğik çizgiyi kaçış saymaz (neredeyse her zaman kullanılır) |
| `-a dizi` | kelimeleri bir diziye okur |
| `-d ''` | satır sonu yerine sıfır baytına kadar okur (`find -print0` ile) |
| `-p "metin"` | etkileşimli istem |
| `-t 5` | 5 saniye bekle, sonra vazgeç |
| `IFS= read -r satir` | baştaki ve sondaki boşlukları da koruyarak bütün satırı okur |

### Here-doc ve here-string
```bash
ad="web01"
cat <<EOF                  #! değişkenler genişler
sunucu: $ad
EOF
cat <<'EOF'                #! tırnaklı sınırlayıcı: hiçbir şey genişlemez
sunucu: $ad
EOF
tr a-z A-Z <<< "$ad"       #! here-string: tek bir metni standart girdiye ver
```

### Süreç ikamesi
`<(komut)` bir komutun çıktısını **dosya adı gibi** kullanılabilir hale getirir. İki komutun çıktısını, ara dosya yazmadan, dosya bekleyen bir araca vermek için idealdir:

```bash
diff <(printf 'a\nb\nc\n') <(printf 'a\nc\nd\n')
comm -12 <(printf 'db01\nweb01\n') <(printf 'web01\nyedek01\n')    #! ikisinde ortak olanlar
```
:::

::: anlat Dosya tanımlayıcıları ve yönlendirme sırası
Her süreç üç açık dosyayla başlar: 0 standart girdi, 1 standart çıktı, 2 standart hata. Yönlendirmeler **soldan sağa** uygulanır ve `2>&1` "2 numarayı, **şu anda** 1 numaranın gösterdiği yere yönlendir" demektir:

```bash
uret() { echo "çıktı satırı"; echo "hata satırı" >&2; }
uret > hepsi.txt 2>&1          #! önce 1 dosyaya, sonra 2 de oraya: ikisi de dosyada
uret 2>&1 > yalniz.txt         #! önce 2 terminale (1'in eski yeri), sonra 1 dosyaya
cat hepsi.txt
echo "---"
cat yalniz.txt
```

`exec` ile bir betiğin kendi tanımlayıcıları kalıcı olarak değiştirilebilir ya da yenileri açılabilir:

```bash
exec 3> ozet.txt               #! 3 numarayı dosyaya aç
echo "birinci kayıt" >&3
echo "ikinci kayıt" >&3
exec 3>&-                      #! kapat
cat ozet.txt
```

> [!TUZAK]
> `komut > dosya 2>&1` ile `komut 2>&1 > dosya` aynı şey değildir. İkincisinde hata akışı dosyaya **gitmez**: `2>&1` uygulandığı anda 1 numara henüz terminali gösteriyordu. "Her şeyi dosyaya" yazmak için `> dosya 2>&1` sırası (ya da Bash'e özgü kısaltması `&> dosya`) kullanılır.
:::

::: tahmin
Betiğin çıktısı ne olur?

```bash
{ echo çıktı; echo hata >&2; } 2>&1 >/dev/null
{ echo çıktı; echo hata >&2; } >/dev/null 2>&1
echo bitti
```

???

`hata`, sonra `bitti`. İlk satırda `2>&1` önce uygulanır ve hata akışı standart çıktının **o anki** yerine bağlanır; ardından standart çıktı `/dev/null`'a gider. Böylece yalnızca "hata" görünür. İkinci satırda önce çıktı `/dev/null`'a gider, hata da onun peşinden gider; hiçbir şey görünmez.
:::

::: gorev Hizalı tablo
Girdinin her satırı `ad cpu`. Her biri için adı 8 karakterlik alana **sola** yaslı, CPU'yu 3 karakterlik alana **sağa** yaslı yazdır: `web01   | 72`.

```starter
while read -r ad cpu; do
    echo "$ad | $cpu"
done
```

```stdin
web01 72
cache01 84
db 7
```

```test
eq(run("web01 72\ncache01 84\ndb 7\n"), "web01   | 72\ncache01 | 84\ndb      |  7\n", "hizalı satırlar")
ok("printf" in src, "printf kullan")
```

```solution
while read -r ad cpu; do
    printf '%-8s|%3d\n' "$ad" "$cpu"
done
```

```hint
`%-8s` 8 karakterlik alana sola yaslı metin, `%3d` 3 karakterlik alana sağa yaslı tam sayı.
```
:::

::: gorev Yalnız birinde olanlar
`a.txt` ve `b.txt` birer sunucu listesi (sırasız). Yalnızca `a.txt`'de olup `b.txt`'de olmayan adları sıralı yazdır. Ara dosya oluşturma; süreç ikamesi kullan.

```setup
open("a.txt", "w", encoding="utf-8", newline="\n").write("web02\ndb01\nweb01\ncache01\n")
open("b.txt", "w", encoding="utf-8", newline="\n").write("web01\nyedek01\ndb01\n")
```

```starter
cat a.txt
```

```test
eq(out, "cache01\nweb02\n", "cache01 ve web02")
ok("<(" in src, "süreç ikamesi <( ) kullan")
```

```solution
comm -23 <(sort a.txt) <(sort b.txt)
```

```hint
`comm` iki **sıralı** dosyayı karşılaştırır; `-23` yalnızca ilk dosyaya özgü satırları bırakır. Sıralamayı `<(sort a.txt)` ile yerinde yap.
```
:::

::: gorev Yalnız hataları say
Başlangıçtaki `uret` fonksiyonu hem standart çıktıya hem standart hataya satır yazıyor. Yalnızca **hata** satırlarının sayısını yazdır; normal çıktı ekrana düşmemeli.

```starter
uret() {
    echo "tamam 1"
    echo "HATA: disk" >&2
    echo "tamam 2"
    echo "HATA: ağ" >&2
}
uret | wc -l
```

```test
eq(out.strip(), "2", "2 hata satırı")
eq(hata_cikti, "", "hiçbir şey stderr'e sızmamalı")
```

```solution
uret() {
    echo "tamam 1"
    echo "HATA: disk" >&2
    echo "tamam 2"
    echo "HATA: ağ" >&2
}
uret 2>&1 >/dev/null | wc -l
```

```hint
Boru yalnızca standart çıktıyı taşır. Hata akışını boruya, normal çıktıyı çöpe gönder: sıra önemli, `2>&1 >/dev/null`.
```
:::
