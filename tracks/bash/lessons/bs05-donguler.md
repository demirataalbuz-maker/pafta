---
id: bs05
title: Döngüler
summary: for ile liste ve aralık, C tarzı for, while read ile satır satır okuma, break ve continue.
kazanim: LPIC1 105.2
---

::: anlat for: listenin her elemanı için
```bash
for host in web01 db01 dc01; do         #! boşlukla ayrılmış liste
    echo "kontrol: $host"
done

for i in $(seq 1 3); do echo "tur $i"; done   #! seq: sayı dizisi

for ((i = 10; i > 0; i -= 3)); do       #! C tarzı for
    printf "%s " "$i"
done
echo
```

Joker desenler de liste üretir: `for f in *.log; do ...` dizindeki `.log` dosyalarını dolaşır. Eşleşen dosya yoksa desen olduğu gibi (`*.log` metni olarak) kalır; bu bir tuzaktır ve `[[ -e "$f" ]] || continue` ile korunulur.

### while read: satır satır işleme
Bir dosyayı ya da bir komutun çıktısını **satır satır** işlemenin doğru kalıbı:

```bash
printf "web01 10.0.0.5\ndb01 10.0.0.6\n" > hostlar.txt
while read -r ad ip; do                 #! her satır boşluklardan bölünür
    echo "$ad → $ip"
done < hostlar.txt                      #! dosyayı döngünün girdisine bağla
```

`while read -r satir` girdi bitene kadar döner, çünkü `read` dosya sonunda 1 (başarısız) döndürür.

> [!TUZAK]
> Windows'ta hazırlanmış dosyaların satırları `\r\n` ile biter. Bash `\r`'yi satırın parçası sayar: `"web01\r"` ile `"web01"` eşit değildir, "boş" görünen bir satır aslında `\r` içerir. Windows'tan gelen bir dosyada tuhaf davranışlar görürsen önce satır sonlarına bak: `cat -A dosya` satır sonlarını `^M$` olarak gösterir, `tr -d '\r'` ya da `dos2unix` temizler.

> [!TUZAK]
> `for satir in $(cat dosya)` yazma: satırları değil **kelimeleri** dolaşır (boşluklardan böler) ve joker karakterleri genişletir. Satır satır işlemek için her zaman `while read -r`.

> [!DERİN]
> `komut | while read ...` yazarsan döngü bir **alt kabukta** (subshell) çalışır: döngü içinde değiştirdiğin değişkenler döngüden sonra kaybolur. Sayaç tutuyorsan girdiyi `done < dosya` ya da süreç ikamesiyle `done < <(komut)` ver.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
for i in $(seq 1 3); do echo "tur $i"; done
toplam=0
for n in 4 8 15; do toplam=$((toplam + n)); done
echo "$toplam"
```

???

`tur 1`, `tur 2`, `tur 3`, `27`. İkinci döngü bir biriktiricidir: 4 + 8 + 15.
:::

::: gorev Geri sayım
Girdiden bir n sayısı oku; n'den 1'e kadar her sayıyı ayrı satıra, sonunda `Ateş!` yazdır.

```starter
read -r n

```

```stdin
3
```

```test
eq(run("3\n"), "3\n2\n1\nAteş!\n", "3")
eq(run("1\n"), "1\nAteş!\n", "1")
eq(run("0\n"), "Ateş!\n", "0 → sadece Ateş!")
```

```solution
read -r n
for ((i = n; i >= 1; i--)); do
    echo "$i"
done
echo "Ateş!"
```

```hint
C tarzı for: `for ((i = n; i >= 1; i--))`.
```
:::

::: gorev Sayıları topla
Girdiden satır satır tam sayılar gelecek (sayısı belli değil). Hepsinin toplamını yazdır. Boş satırları atla.

```starter
toplam=0

echo "$toplam"
```

```stdin
10
20

12
```

```test
eq(run("10\n20\n\n12\n"), "42\n", "10+20+12")
eq(run("5\n"), "5\n", "tek sayı")
eq(run("-3\n3\n"), "0\n", "negatifler")
ok("while" in src and "read" in src, "while read kullan")
```

```solution
toplam=0
while read -r n; do
    [[ -z "$n" ]] && continue
    toplam=$((toplam + n))
done
echo "$toplam"
```

```hint
`while read -r n; do ... done`. Boş satır için `[[ -z "$n" ]] && continue`.
```
:::

::: gorev Envanter listesi
`hostlar.txt` dosyasında her satırda bir host adı var; `#` ile başlayan yorum satırları ve boş satırlar da var. Gerçek host'ları `N. ad` biçiminde numaralandırarak yazdır.

```setup
open("hostlar.txt", "w", encoding="utf-8", newline="\n").write("# üretim\nweb01\ndb01\n\n# yedek\nyedek01\n")
```

```starter
i=1
while read -r host; do
    echo "$i. $host"
    i=$((i + 1))
done < hostlar.txt
```

```test
eq(out, "1. web01\n2. db01\n3. yedek01\n", "yorumlar ve boş satırlar atlanmalı")
```

```solution
i=1
while read -r host; do
    [[ -z "$host" || "$host" == \#* ]] && continue
    echo "$i. $host"
    i=$((i + 1))
done < hostlar.txt
```

```hint
Atlanacak satırlar: boş (`-z`) ya da `#` ile başlayanlar. `[[ "$host" == \#* ]]` (diyezi kaçışla).
```
:::
