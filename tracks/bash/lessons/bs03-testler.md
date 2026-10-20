---
id: bs03
title: Testler ve Çıkış Kodları
summary: Her komut bir çıkış kodu döndürür; [[ ]] testleri, (( )) karşılaştırmaları, && ve ||.
---

::: anlat Başarı = 0
Bash'te her komut bitince bir **çıkış kodu** döndürür: **0 başarı**, 1–255 arası **hata** demektir (programlama dillerinin tersine!). Son komutun kodu `$?` değişkenindedir:

```bash
ls / > /dev/null
echo "ls kodu: $?"            #! 0: başarılı
ls /olmayan/yol 2> /dev/null
echo "ls kodu: $?"            #! 0'dan farklı: hata
true; echo "true: $?"
false; echo "false: $?"
```

`if`, `&&`, `||` ve `while` hep bu koda bakar. `komut1 && komut2`: birinci **başarılıysa** ikinciyi çalıştır. `komut1 || komut2`: birinci **başarısızsa** ikinciyi çalıştır.

### [[ ]]: koşul sınama
`[[ ... ]]` bir koşulu sınar ve sonuca göre 0 ya da 1 döndürür:

| Metin | Sayı (tam sayı) | Dosya |
|---|---|---|
| `==` `!=` eşit / değil | `-eq` `-ne` | `-e` var mı |
| `<` `>` sözlük sırası | `-lt` `-le` `-gt` `-ge` | `-f` normal dosya |
| `-z` boş mu | | `-d` dizin |
| `-n` dolu mu | | `-r` `-w` `-x` izinler |
| `=~` regex eşleşmesi | | `-s` boyutu > 0 |

```bash
dosya="rapor.txt"
[[ -f "$dosya" ]] && echo "var" || echo "yok"
[[ "$dosya" == *.txt ]] && echo "metin dosyası"   #! == sağında joker desen
[[ 10 -gt 9 ]] && echo "sayısal: 10 > 9"
[[ "10" > "9" ]] || echo "metin olarak: \"10\" < \"9\""
```

Sayılar için daha okunaklı bir yol: `(( ... ))` aritmetik test. İçeride `<`, `>`, `==` normal sayı karşılaştırmasıdır:

```bash
n=42
(( n % 2 == 0 )) && echo "$n çift"
(( n > 100 )) || echo "$n küçük"
```

> [!TUZAK]
> `[[ "10" > "9" ]]` **yanlıştır**: `>` metinleri karşılaştırır ve "1", "9"dan önce gelir. Sayıları `-gt` ya da `(( ))` ile karşılaştır. Eski `[ ]` (tek köşeli) yapısında ise `>` bir **yönlendirmedir** ve `9` adında bir dosya oluşturur!
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
[[ 5 -gt 3 ]] && echo "büyük"
[[ "abc" == a* ]] && echo "a ile başlıyor"
[[ -z "" ]] && echo "boş"
[[ 2 -gt 10 ]] || echo "değil"
```

???

`büyük`, `a ile başlıyor`, `boş`, `değil`. Son satırda test başarısız olur (kod 1), bu yüzden `||` sağındaki komut çalışır.
:::

::: gorev Çift mi tek mi?
Girdiden bir tam sayı oku; çiftse `çift`, tekse `tek` yazdır.

```starter
read -r n

```

```stdin
42
```

```test
eq(run("42\n"), "çift\n", "42 çift")
eq(run("7\n"), "tek\n", "7 tek")
eq(run("0\n"), "çift\n", "0 çift")
eq(run("-3\n"), "tek\n", "-3 tek")
```

```solution
read -r n
if (( n % 2 == 0 )); then
    echo "çift"
else
    echo "tek"
fi
```

```hint
`(( n % 2 == 0 )) && echo çift || echo tek` ya da bir `if` bloğu (BS04).
```
:::

::: gorev Dosya var mı?
Betik ilk argümanı bir dosya adı olarak alsın; dosya varsa `var: <ad>`, yoksa `yok: <ad>` yazdırsın. Adında boşluk olan dosyalarla da çalışmalı.

```setup
open("rapor.txt", "w").write("x")
open("yıllık rapor.txt", "w").write("y")
```

```starter
if [[ -f $1 ]]; then echo "var: $1"; fi
```

```meta
argv: rapor.txt
```

```test
eq(run(argv=["rapor.txt"]), "var: rapor.txt\n", "rapor.txt var")
eq(run(argv=["olmayan.txt"]), "yok: olmayan.txt\n", "olmayan dosya")
eq(run(argv=["yıllık rapor.txt"]), "var: yıllık rapor.txt\n", "boşluklu ad")
```

```solution
if [[ -f "$1" ]]; then
    echo "var: $1"
else
    echo "yok: $1"
fi
```

```hint
`[[ -f "$1" ]]` ve bir `else` dalı.
```
:::

::: gorev Sayı doğrulayıcı
Betik ilk argümanı denetlesin: sadece rakamlardan oluşuyorsa `geçerli` yazıp **0** ile çıksın; değilse standart hataya `geçersiz: <arg>` yazıp **1** ile çıksın. `[[ ... =~ ... ]]` kullan.

```starter
echo "geçerli"
```

```meta
argv: 42
```

```test
r = calis(argv=["42"])
eq((r["kod"], r["cikti"]), (0, "geçerli\n"), "42 → geçerli, kod 0")
r = calis(argv=["4a2"])
eq(r["kod"], 1, "4a2 → kod 1")
ok("geçersiz: 4a2" in r["hata"], "hata mesajı standart hataya", got=r["hata"])
eq(calis(argv=[""])["kod"], 1, "boş argüman → kod 1")
ok("=~" in src, "=~ kullan")
```

```solution
if [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "geçerli"
else
    echo "geçersiz: $1" >&2
    exit 1
fi
```

```hint
Regex eşleşmesi: `[[ "$1" =~ ^[0-9]+$ ]]` (desen tırnak içine alınmaz). Standart hataya yazmak: `echo "..." >&2`. Çıkış kodu: `exit 1`.
```
:::
