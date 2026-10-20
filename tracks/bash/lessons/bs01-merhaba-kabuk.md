---
id: bs01
title: Merhaba Kabuk
summary: echo, değişkenler, tek ve çift tırnak farkı, komut ikamesi ve aritmetik.
---

::: anlat Kabuk bir programlama dilidir
**Bash**, Linux ve macOS sunucularının varsayılan **kabuğudur** (shell): komutları okuyup çalıştıran program. Komutları tek tek yazmak yerine bir dosyaya koyarsan **betik** (script) olur.

Tezgahta yazdığın kod gerçek bir Bash'te (Windows'ta Git Bash) çalışır.

```bash
echo "Merhaba, kabuk!"        #! echo: argümanlarını yazdırır
ad="Pafta"                    #! değişken ataması: = etrafında BOŞLUK YOK
echo "Merhaba, $ad"           #! $ad: değişkenin değeri
echo "${ad}lar"               #! süslü parantez: ismin nerede bittiğini belirtir
# bu bir yorum satırı
```

> [!TUZAK]
> `ad = "Pafta"` yazarsan Bash bunu "`ad` adlı komutu `=` ve `"Pafta"` argümanlarıyla çalıştır" diye anlar ve `ad: command not found` hatası verir. Atamada `=`'in iki yanında boşluk **olmaz**.

### Tek tırnak, çift tırnak
- **Tek tırnak** `'...'`: içindeki her şey düz metindir; `$` bile.
- **Çift tırnak** `"..."`: `$değişken` ve `$(komut)` açılır, ama metin **tek bir argüman** olarak kalır.
- **Tırnaksız**: değişken açılır ve sonuç **boşluklardan bölünür** (yeni başlayanların en büyük derdi).

```bash
dosya="yıllık rapor.txt"
echo '$dosya'                 #! tek tırnak: olduğu gibi
echo "$dosya"                 #! çift tırnak: açılır, tek parça kalır
printf "[%s]\n" $dosya        #! tırnaksız: İKİ ayrı argümana bölünür!
printf "[%s]\n" "$dosya"      #! tırnaklı: tek argüman
```

**Kural: değişkenleri her zaman çift tırnak içinde kullan**: `"$dosya"`. Bölünmesini bilerek istediğin nadir durumlar dışında.

> [!GÜVENLİK]
> Tırnaksız değişkenler bir güvenlik açığıdır: dosya adında boşluk ya da `*` gibi joker karakterler varsa betik başka dosyalar üzerinde işlem yapabilir. `rm $dosya` satırı, adı `* ` olan bir dosya için dizindeki her şeyi silmeye kalkar. `rm -- "$dosya"` yaz: tırnak bölünmeyi, `--` ise `-` ile başlayan bir adın seçenek sanılmasını önler.
:::

::: tahmin
Üç satırın çıktısını yaz:

```bash
ad="Pafta"
echo 'Merhaba $ad'
echo "Merhaba $ad"
echo "${ad}lar"
```

???

`Merhaba $ad`, `Merhaba Pafta`, `Paftalar`. Tek tırnak hiçbir şeyi açmaz. `${ad}lar` yazımındaki süslü parantezler olmasaydı Bash `$adlar` adlı (boş) bir değişken arardı.
:::

::: anlat Komut ikamesi ve aritmetik
Bir komutun **çıktısını** bir değişkene ya da başka bir komutun içine koymak için `$( ... )` kullanılır:

```bash
bugun=$(date +%Y)             #! komutun çıktısı değişkene
echo "Yıl: $bugun"
echo "Bu dizinde $(ls | wc -l) öğe var"
```

Tam sayı aritmetiği için `$(( ... ))`:

```bash
x=7
y=$((x * 6))                  #! içeride $ gerekmez
echo "$x * 6 = $y"
echo $(( 17 / 5 )) $(( 17 % 5 ))   #! tam bölme ve kalan
printf "%05d|%-6s|\n" 42 ab   #! printf: biçimli yazdırma (C'deki gibi)
```

Bash'te sadece **tam sayı** aritmetiği vardır; ondalıklı işlem için `awk` ya da `bc` kullanılır (BS09).

> [!NOT]
> `echo` hızlı ve kolaydır, ama davranışı kabuktan kabuğa değişir (`-e`, `-n` seçenekleri, ters eğik çizgiler). Biçim önemliyse ve taşınabilirlik istiyorsan `printf` kullan.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
x=7
y=$((x * 6))
echo "$x * 6 = $y"
printf "%05d|%-6s|\n" 42 ab
```

???

`7 * 6 = 42`, sonra `00042|ab    |`. Çift tırnak içindeki `*` joker olarak açılmaz. `%05d` beş haneye sıfırla tamamlar, `%-6s` 6 karakterlik alanda sola yaslar.
:::

::: gorev Hedef kartı
`host` değişkenine `web01`, `port` değişkenine `443` ata ve **değişkenleri kullanarak** şunu yazdır:

```cikti
web01:443
```

```starter
# değişkenleri ata ve yazdır

```

```test
eq(out, "web01:443\n", "çıktı: web01:443")
ok("$host" in src or "${host}" in src, "host değişkenini kullan")
ok("web01:443" not in src, "çıktıyı hazır metin olarak yazma")
```

```solution
host="web01"
port=443
echo "${host}:${port}"
```

```hint
`echo "$host:$port"` çalışır; `${host}` yazımı daha güvenlidir.
```
:::

::: gorev Dolar işaretli metin
Şu satırı **tam olarak** yazdır. `$5` bir değişken gibi açılmamalı:

```cikti
Fiyat: $5 (vergi dahil)
```

```starter
echo "Fiyat: $5 (vergi dahil)"
```

```test
eq(out, "Fiyat: $5 (vergi dahil)\n", "dolar işareti korunmalı")
```

```solution
echo 'Fiyat: $5 (vergi dahil)'
```

```hint
Çift tırnak içinde `$5` beşinci argüman olarak açılır (boş). Tek tırnak kullan ya da `\$` ile kaçışla.
```
:::

::: gorev Saniye çözücü
`toplam=3725` değişkenini saat, dakika ve saniyeye ayırıp şu biçimde yazdır. Aritmetik genişletme `$(( ))` kullan.

```cikti
1 saat 2 dakika 5 saniye
```

```starter
toplam=3725

```

```test
eq(out, "1 saat 2 dakika 5 saniye\n", "3725 saniye")
ok("$((" in src, "$(( )) kullan")
ok(src.count("3725") == 1, "sonucu elle hesaplama, toplam'dan türet")
```

```solution
toplam=3725
saat=$((toplam / 3600))
dakika=$((toplam % 3600 / 60))
saniye=$((toplam % 60))
echo "$saat saat $dakika dakika $saniye saniye"
```

```hint
Python'daki gibi: `/` tam bölme, `%` kalan. `$((toplam / 3600))`.
```
:::
