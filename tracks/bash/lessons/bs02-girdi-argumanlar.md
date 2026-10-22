---
id: bs02
title: Girdi ve Argümanlar
summary: read ile satır okumak, $1 $2 $# $@ ile argümanlar, varsayılan değerler ve shift.
kazanim: LPIC1 105.2
---

::: anlat read: satır oku
`read` standart girdiden **bir satır** okur ve değişkenlere dağıtır. Tezgahta standart girdi alttaki **Girdi** kutusudur.

```bash
read -r ad                    #! -r: ters eğik çizgileri olduğu gibi bırak
echo "Merhaba, $ad"
```

Birden fazla değişken verirsen satır boşluklardan bölünür; **son değişken kalan her şeyi** alır:

```bash
read -r kullanici durum mesaj
echo "kullanıcı=$kullanici durum=$durum"
echo "mesaj=$mesaj"
```

Bu örneği tezgaha al ve Girdi kutusuna `root FAIL parola yanlış girildi` yaz.

> [!NOT]
> `read`'i her zaman `-r` ile kullan. Onsuz, satırdaki `\` karakterleri kaçış olarak yorumlanır ve Windows yolları ya da regex'ler bozulur.

### Komut satırı argümanları
Betik `./betik.sh web01 443` diye çağrıldığında:

| Değişken | Değer |
|---|---|
| `$0` | betiğin adı |
| `$1`, `$2`, ... | 1., 2., ... argüman |
| `$#` | argüman sayısı |
| `"$@"` | bütün argümanlar, her biri ayrı ve korunmuş |
| `$?` | son komutun çıkış kodu |

```bash norun
echo "$# argüman geldi"
echo "ilki: $1"
for a in "$@"; do echo "- $a"; done
```

Tezgahta komut satırı yok; argüman alan betiklerini görev testleri çağırır.

### Varsayılan değerler
```bash
hedef=${1:-localhost}         #! $1 boşsa ya da yoksa localhost
port=${2:-22}
echo "$hedef:$port"
```

| Yazım | Anlamı |
|---|---|
| `${x:-v}` | x boşsa v kullan (x değişmez) |
| `${x:=v}` | x boşsa v kullan **ve** x'e ata |
| `${x:?mesaj}` | x boşsa mesajla birlikte hata verip çık |
:::

::: tahmin
Girdi kutusunda tek satır var: `Ada Lovelace King`. Çıktı ne olur?

```bash
read -r ad soyad
echo "Soyad: $soyad, Ad: $ad"
```

```stdin
Ada Lovelace King
```

???

`Soyad: Lovelace King, Ad: Ada`. İlk kelime `ad`'a gider, **son** değişken `soyad` satırın geri kalanını alır.
:::

::: gorev Selamla
Girdiden bir ad oku ve `Merhaba, <ad>!` yazdır.

```starter
# girdiden oku

```

```stdin
Ali
```

```test
eq(run("Ali\n"), "Merhaba, Ali!\n", "Ali")
eq(run("Ayşe Yılmaz\n"), "Merhaba, Ayşe Yılmaz!\n", "boşluklu ad tek parça kalmalı")
ok("read" in src, "read kullan")
```

```solution
read -r ad
echo "Merhaba, $ad!"
```

```hint
`read -r ad` ve çift tırnaklı `echo`.
```
:::

::: gorev Argüman sayımı
Betik kaç argüman aldığını ve ilk argümanı şu biçimde yazdırsın. Tezgahta `a "b c"` argümanlarıyla çalışır; beklenen çıktı:

```cikti
2 argüman, ilki: a
```

```starter
echo "argümanlar"
```

```meta
argv: a "b c"
```

```test
eq(run(argv=["a", "b c"]), "2 argüman, ilki: a\n", "a ve 'b c'")
eq(run(argv=["tek"]), "1 argüman, ilki: tek\n", "tek argüman")
eq(run(argv=["x y", "z", "w"]), "3 argüman, ilki: x y\n", "boşluklu ilk argüman")
```

```solution
echo "$# argüman, ilki: $1"
```

```hint
`$#` sayıyı, `$1` ilk argümanı verir.
```
:::

::: gorev Varsayılan hedef
Betik ilk argümanı hedef olarak alsın; argüman yoksa `localhost` kullansın ve `Hedef: <hedef>` yazdırsın.

```starter
hedef=$1
echo "Hedef: $hedef"
```

```test
eq(run(), "Hedef: localhost\n", "argümansız → localhost")
eq(run(argv=["web01"]), "Hedef: web01\n", "web01")
```

```solution
hedef=${1:-localhost}
echo "Hedef: $hedef"
```

```hint
`${1:-localhost}`
```
:::
