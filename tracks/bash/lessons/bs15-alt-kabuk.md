---
id: bs15
title: Alt Kabuklar, Ortam ve Boru Tuzakları
summary: ( ) ile { } farkı, boru hattının alt kabukta çalışması ve kaybolan değişkenler, export ve geçici ortam, source, PIPESTATUS.
kazanim: LPIC1 103.1, LPIC1 105.1
---

::: anlat Alt kabuk ve grup
`( komutlar )` komutları bir **alt kabukta**, yani ayrı bir süreç kopyasında çalıştırır: içeride yapılan değişiklikler (değişkenler, `cd`, IFS) dışarı taşmaz. `{ komutlar; }` ise aynı kabukta çalışan bir **gruptur**; yalnızca yönlendirmeyi birlikte yapmak için kullanılır:

```bash
x=1
( x=2; cd /; echo "içeride: x=$x, klasör=$PWD" )
echo "dışarıda: x=$x"
{ echo "ilk"; echo "ikinci"; } > grup.txt      #! iki komutun çıktısı tek dosyaya
wc -l < grup.txt
```

### Boru hattı alt kabukta çalışır
Bir boru hattının (`a | b | c`) her parçası ayrı bir alt kabukta çalışır. Bu yüzden boruya bağlanmış bir `while` döngüsünün içinde değiştirilen değişkenler döngü bitince **kaybolur**:

```bash
say=0
printf 'a\nb\nc\n' | while read -r s; do (( say++ )); done
echo "borulu: $say"                            #! 0!
say=0
while read -r s; do (( say++ )); done < <(printf 'a\nb\nc\n')
echo "süreç ikameli: $say"                     #! 3
```

Çözüm: döngüyü boruya bağlamak yerine girdiyi döngünün sonuna yönlendir (`done < dosya` ya da `done < <(komut)`).

### Ortam ve export
Bir değişken varsayılan olarak yalnızca o kabuğundur; başlatılan programlar onu **görmez**. `export` onu ortama koyar. Tek bir komut için geçici ortam değişkeni `DEGISKEN=deger komut` biçiminde verilir:

```bash
BOLGE=ist
bash -c 'echo "çocuk görüyor mu: ${BOLGE:-hayır}"'
export BOLGE
bash -c 'echo "export sonrası: $BOLGE"'
DIL=tr bash -c 'echo "geçici: $DIL"'
echo "geçici sonrası: ${DIL:-tanımsız}"
```

`source dosya` (ya da `. dosya`) bir dosyayı **aynı kabukta** çalıştırır; içindeki değişken ve fonksiyonlar mevcut kabukta kalır. `bash dosya` ise alt süreçte çalıştırır.

### PIPESTATUS
`$?` yalnızca boru hattının **son** komutunun kodunu verir. Her parçanın kodu `PIPESTATUS` dizisindedir; bir sonraki komut çalışınca kaybolur, hemen okunmalıdır:

```bash
false | true | true
echo "\$? = $?, parçalar: ${PIPESTATUS[*]}"
```

> [!TUZAK]
> `set -o pipefail` olmadan `grep HATA log | wc -l` gibi bir hat, `log` dosyası hiç yokken bile başarılı (0) döner: hattın kodu son komutun, yani `wc`'nin kodudur. BS10'daki `set -euo pipefail` alışkanlığı bu yüzden önemlidir.
:::

::: tahmin
İki satır yazar:

```bash
say=0
printf 'a\nb\nc\n' | while read -r s; do say=$((say + 1)); done
echo "$say"
while read -r s; do say=$((say + 1)); done < <(printf 'a\nb\nc\n')
echo "$say"
```

???

`0`, sonra `3`. İlk döngü borunun sağında, bir alt kabukta çalışır; içeride artan `say` döngü bitince kaybolur ve dışarıdaki 0 kalır. İkinci döngü aynı kabukta çalışır, girdisini süreç ikamesinden alır: üç satır sayılır.
:::

::: gorev Kaybolan sayaç
Başlangıç kodu girdideki satırları sayıp `N satır` yazdırmaya çalışıyor ama her zaman 0 diyor. Düzelt.

```starter
say=0
cat | while read -r satir; do
    (( say++ ))
done
echo "$say satır"
```

```stdin
birinci
ikinci
```

```test
eq(run("birinci\nikinci\n"), "2 satır\n", "2 satır")
eq(run("a\nb\nc\nd\n"), "4 satır\n", "4 satır")
eq(run(""), "0 satır\n", "boş girdi")
```

```solution
say=0
while read -r satir; do
    (( say++ ))
done
echo "$say satır"
```

```hint
`cat |` döngüyü alt kabuğa itiyor. Döngü standart girdiyi zaten kendisi okuyabilir: boruyu kaldır.
```
:::

::: gorev Hattın kodları
Aşağıdaki boru hattını çalıştır ve ardından hattaki **her** komutun çıkış kodunu boşlukla ayırarak tek satırda yazdır: `cat yok.txt 2>/dev/null | sort | head -n 1`.

```starter
cat yok.txt 2>/dev/null | sort | head -n 1
echo "$?"
```

```test
eq(out, "1 0 0\n", "cat 1, sort 0, head 0")
ok("PIPESTATUS" in src, "PIPESTATUS kullan")
```

```solution
cat yok.txt 2>/dev/null | sort | head -n 1
echo "${PIPESTATUS[*]}"
```

```hint
`$?` yalnızca son komutun kodunu verir. Hepsi `"${PIPESTATUS[*]}"` içinde; hattın hemen ardından oku.
```
:::

::: gorev Geçici ortam
`alt.sh` betiği `BOLGE` ortam değişkenini yazdırıyor. Önce `alt.sh`'i `BOLGE=ist` ile, sonra hiç `BOLGE` olmadan çalıştır. Çıktı `BOLGE=ist` ve `BOLGE=yok` olmalı. Değişkeni kalıcı olarak export etme.

```setup
open("alt.sh", "w", encoding="utf-8", newline="\n").write('echo "BOLGE=${BOLGE:-yok}"\n')
```

```starter
BOLGE=ist
bash alt.sh
bash alt.sh
```

```test
eq(out, "BOLGE=ist\nBOLGE=yok\n", "önce ist, sonra yok")
ok("export" not in src, "export kullanma; tek komutluk geçici ortam yeter")
```

```solution
BOLGE=ist bash alt.sh
bash alt.sh
```

```hint
Değişkeni yalnızca tek bir komutun ortamına vermek için aynı satırda komuttan önce yaz: `BOLGE=ist bash alt.sh`.
```
:::
