---
id: bs06
title: Fonksiyonlar
summary: Bash fonksiyonları, $1 argümanları, local değişkenler, echo ile değer döndürmek ve return ile durum kodu.
---

::: anlat Fonksiyon = isimli komut
Bash fonksiyonu, kendi argümanları olan küçük bir komut gibidir:

```bash
selamla() {                       #! tanım: ad() { ... }
    echo "Merhaba, $1"            #! $1: fonksiyonun ilk argümanı
}
selamla "Ali"                     #! çağrı: komut gibi, parantez yok
selamla "Ayşe"
```

Fonksiyon içinde `$1`, `$2`, `$#`, `"$@"` **fonksiyonun** argümanlarını gösterir, betiğinkini değil.

### İki tür "dönüş"
Bash fonksiyonlarının iki ayrı çıkış kanalı vardır ve karıştırılmaları en sık yapılan hatadır:

1. **Çıktı** (`echo`): asıl veri. Çağıran onu `$(fonksiyon)` ile yakalar
2. **Çıkış kodu** (`return N`): başarı/başarısızlık (0–255). `if fonksiyon; then` ile sınanır

```bash
kare() { echo $(( $1 * $1 )); }   #! veriyi echo ile "döndür"
sonuc=$(kare 7)
echo "7'nin karesi $sonuc"

cift_mi() { (( $1 % 2 == 0 )); }  #! son komutun kodu fonksiyonun kodudur
if cift_mi 4; then echo "4 çift"; fi
cift_mi 5 || echo "5 tek"
```

> [!TUZAK]
> `return 42` yazıp sonucu `$?`'den okumaya çalışma: çıkış kodu sadece 0–255 arasıdır ve "veri" değil "durum" içindir. Veriyi `echo` ile ver.

### local: fonksiyonun kendi değişkenleri
Bash'te değişkenler varsayılan olarak **globaldir**: fonksiyon içinde atanan bir değişken dışarıdakini ezer. `local` ile fonksiyona özel yap:

```bash
sayac=100
kotu()  { sayac=0; }
iyi()   { local sayac=0; }
iyi;  echo "iyi'den sonra: $sayac"
kotu; echo "kotu'dan sonra: $sayac"
```
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
kare() { echo $(( $1 * $1 )); }
sonuc=$(kare 7)
echo "7'nin karesi $sonuc"
cift_mi() { (( $1 % 2 == 0 )); }
cift_mi 4 && echo "4 çift"
cift_mi 5 || echo "5 tek"
```

???

`7'nin karesi 49`, `4 çift`, `5 tek`. `kare` veriyi çıktıyla, `cift_mi` sonucu çıkış koduyla bildirir.
:::

::: gorev Toplayan fonksiyon
`topla` adında, **kaç argüman verilirse verilsin** hepsinin toplamını yazdıran bir fonksiyon yaz. Betik, kendisine verilen argümanlarla `topla`'yı çağırıp sonucu yazdırsın.

```starter
topla() {
    echo 0
}

topla "$@"
```

```meta
argv: 1 2
```

```test
eq(run(argv=["1", "2", "3", "4"]), "10\n", "1+2+3+4")
eq(run(argv=["100"]), "100\n", "tek argüman")
eq(run(argv=["-5", "5"]), "0\n", "negatif")
ok("topla()" in src.replace(" ", "") or "functiontopla" in src.replace(" ", ""), "topla fonksiyonunu tanımla")
```

```solution
topla() {
    local toplam=0
    for n in "$@"; do
        toplam=$((toplam + n))
    done
    echo "$toplam"
}

topla "$@"
```

```hint
Fonksiyonun içinde `for n in "$@"` ile argümanları dolaş, biriktir, sonunda `echo`.
```
:::

::: gorev local hatası
Bu betikte `rapor` fonksiyonu kendi döngü sayacını kullanırken betiğin global `i` değişkenini bozuyor. `local` ile düzelt; beklenen çıktı:

```cikti
satır 1
satır 2
global i hâlâ: 99
```

```starter
i=99
rapor() {
    for ((i = 1; i <= 2; i++)); do
        echo "satır $i"
    done
}
rapor
echo "global i hâlâ: $i"
```

```test
eq(out, "satır 1\nsatır 2\nglobal i hâlâ: 99\n", "global i korunmalı")
ok("local" in src, "local kullan")
```

```solution
i=99
rapor() {
    local i
    for ((i = 1; i <= 2; i++)); do
        echo "satır $i"
    done
}
rapor
echo "global i hâlâ: $i"
```

```hint
Fonksiyonun ilk satırına `local i`.
```
:::

::: gorev IP denetleyici
`ip_mi` adında bir fonksiyon yaz: argümanı `sayı.sayı.sayı.sayı` biçimindeyse (her parça 1–3 rakam) **0**, değilse **1** döndürsün (çıktı vermesin). Betik girdiden satır satır okuyup her satır için `geçerli` ya da `geçersiz` yazdırsın.

```starter
ip_mi() {
    return 0
}

while read -r satir; do
    echo "geçerli"
done
```

```stdin
10.0.0.5
abc
```

```test
eq(run("10.0.0.5\nabc\n192.168.1.300\n1.2.3\n").splitlines(), ["geçerli", "geçersiz", "geçerli", "geçersiz"], "biçim denetimi (sadece biçim, 300 de biçime uyar)")
```

```solution
ip_mi() {
    [[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
}

while read -r satir; do
    if ip_mi "$satir"; then
        echo "geçerli"
    else
        echo "geçersiz"
    fi
done
```

```hint
Fonksiyonun son komutu `[[ "$1" =~ ^...$ ]]` olursa onun kodu fonksiyonun kodu olur; `return` yazmana gerek yok.
```
:::
