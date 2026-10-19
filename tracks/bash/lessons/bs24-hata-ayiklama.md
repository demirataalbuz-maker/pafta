---
id: bs24
title: Hata Ayıklama ve Klasik Tuzaklar
summary: bash -n, set -x ve PS4, ERR tuzağıyla satır numarası, local'in çıkış kodunu yutması, sekizlik sayı tuzağı, boş değişkenli [ ], cd'yi denetlemek ve ShellCheck'in en sık uyarıları.
---

::: anlat Betiğin içini görmek
| Araç | Ne yapar |
|---|---|
| `bash -n betik.sh` | çalıştırmadan sözdizimini denetler |
| `set -x` / `set +x` | her komutu genişlemiş haliyle stderr'e yazar (Röntgen bunu kullanır) |
| `PS4='+ ${LINENO}: '` | `set -x` satırlarının başına satır numarası koyar |
| `trap '...' ERR` + `set -E` | bir komut başarısız olunca, fonksiyonların içinde bile, yakalar |

```bash
trap 'echo "hata: satır $LINENO, komut: $BASH_COMMAND" >&2' ERR
echo "başla"
false
echo "devam"
```

### ShellCheck ve sık hatalar
ShellCheck, kabuk betiklerini okuyup hataları gösteren ücretsiz bir denetleyicidir. Uyarılarının çoğu aşağıdaki kalıplardandır; bunları tanımak, başkasının betiğini okurken de işe yarar:

| Kalıp | Sorun | Doğrusu |
|---|---|---|
| `rm $dosya` | boşlukta bölünür, `*` genişler | `rm -- "$dosya"` |
| `cd klasor; rm -f *` | `cd` başarısızsa yanlış klasörde siler | `cd klasor \|\| exit 1` |
| `for f in $(ls)` | adlar bozulur | `for f in *` |
| `local x=$(komut)` | `local`'in kodu, komutun kodunu **yutar** | önce `local x`, sonra `x=$(komut)` |
| `[ $x = evet ]` | x boşsa `[ = evet ]` sözdizimi hatası | `[[ $x == evet ]]` ya da `[ "$x" = evet ]` |
| `$(( 08 + 1 ))` | başında 0 olan sayı **sekizlik** sayılır; 8 ve 9 geçersiz | `$(( 10#08 + 1 ))` |
| `read satir` | ters eğik çizgileri yer | `read -r satir` |

```bash
x=08
echo $(( 10#$x + 1 ))                     #! 10# tabanı açıkça onluk yapar
bos=""
[[ $bos == evet ]] || echo "[[ ]] boş değişkende de güvenli"
```

> [!TUZAK]
> Saat ve tarih parçalarıyla aritmetik yapan betiklerdeki gizli hata: `saat=08; echo $(( saat * 60 ))` "08: değer taban için çok büyük" hatası verir, çünkü başında sıfır olan sayılar sekizlik tabanda yorumlanır. Sabahları bozulan ama öğleden sonra çalışan betiklerin klasik sebebi budur.
:::

::: tahmin
İki satır yazar:

```bash
f() { local s=$(false); echo "kod: $?"; }
g() { local s; s=$(false); echo "kod: $?"; }
f
g
```

???

`kod: 0`, sonra `kod: 1`. `f`'de `$?`, `local` komutunun kendi kodudur ve `local` başarıyla çalıştığı için 0'dır; `false`'un hatası kaybolur. `g`'de bildirim ve atama ayrı satırlarda olduğu için `$?` atamanın, yani `false`'un kodunu taşır.
:::

::: gorev Sekizlik tuzağı
Girdinin her satırı `SS:DD` biçiminde bir saat. Her biri için gece yarısından itibaren geçen dakikayı yazdır. Başlangıç kodu sabah saatlerinde hata veriyor; düzelt.

```starter
while IFS=: read -r s d; do
    echo $(( s * 60 + d ))
done
```

```stdin
08:09
12:30
```

```test
eq(run("08:09\n12:30\n"), "489\n750\n", "08:09 → 489, 12:30 → 750")
eq(run("00:00\n09:59\n"), "0\n599\n", "00:00 ve 09:59")
```

```solution
while IFS=: read -r s d; do
    echo $(( 10#$s * 60 + 10#$d ))
done
```

```hint
"08" ve "09" sekizlik tabanda geçersizdir. Tabanı açıkça onluk yap: `10#$s`.
```
:::

::: gorev Boş değişken
Betik bir satır okusun: `aktif` ise `açık`, değilse (boş satır dahil) `kapalı` yazsın. Boş girdide hiçbir hata mesajı çıkmamalı.

```starter
read -r durum
if [ $durum = "aktif" ]; then
    echo "açık"
else
    echo "kapalı"
fi
```

```test
eq(run("aktif\n"), "açık\n", "aktif")
eq(run("pasif\n"), "kapalı\n", "pasif")
r = calis("\n")
eq(r["cikti"], "kapalı\n", "boş satır → kapalı")
eq(r["hata"], "", "boş satırda stderr'e hata yazılmamalı")
```

```solution
read -r durum
if [[ $durum == "aktif" ]]; then
    echo "açık"
else
    echo "kapalı"
fi
```

```hint
`[ $durum = aktif ]` durum boşken `[ = aktif ]` olur ve hata verir. `[[ ]]` kelime bölme yapmaz; ya da değişkeni tırnakla.
```
:::

::: gorev cd'yi denetle
Betik 1. argümanda verilen klasöre girip içindeki `.tmp` dosyalarını silsin ve `temizlendi` yazsın. Klasöre girilemezse standart hataya `hata: klasöre girilemedi: <ad>` yazıp **1** koduyla çıksın ve **hiçbir şey silmesin**.

```setup
import os
os.makedirs("hedef", exist_ok=True)
open("hedef/a.tmp", "w").write("x")
open("hedef/kalsin.txt", "w").write("x")
open("onemli.tmp", "w").write("burada kalmalı")
```

```starter
cd "$1"
rm -f *.tmp
echo "temizlendi"
```

```meta
argv: hedef
```

```test
import os
eq(out, "temizlendi\n", "hedef temizlendi")
ok(not os.path.exists("hedef/a.tmp") and os.path.exists("hedef/kalsin.txt"), "yalnızca hedefteki .tmp silindi")
ok(os.path.exists("onemli.tmp"), "çalışma klasöründeki .tmp'ye dokunulmamalı")
r = calis(argv=["yok"])
eq(r["kod"], 1, "olmayan klasör → 1")
ok("hata: klasöre girilemedi: yok" in r["hata"], "hata mesajı", got=r["hata"])
ok(os.path.exists("onemli.tmp"), "cd başarısızken hiçbir şey silinmemeli")
```

```solution
if ! cd -- "$1" 2>/dev/null; then
    echo "hata: klasöre girilemedi: $1" >&2
    exit 1
fi
rm -f -- *.tmp
echo "temizlendi"
```

```hint
Başlangıç kodunda `cd` başarısız olursa `rm` **çalışma klasöründe** çalışır. `cd`'nin sonucunu denetle: `if ! cd -- "$1" 2>/dev/null; then ...; exit 1; fi`.
```
:::
