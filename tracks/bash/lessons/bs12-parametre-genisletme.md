---
id: bs12
title: Parametre Genişletme Ustalığı
summary: Dış komut çağırmadan metin işlemek; varsayılan değerler, zorunlu parametreler, baştan ve sondan kırpma, değiştirme, büyük-küçük harf, alt metin ve dolaylı başvuru.
---

::: anlat ${...} bir mini dildir
`${degisken}` yalnızca değişkenin değerini vermez; süslü parantezin içine eklenen işleçlerle değeri **dönüştürür**. Hepsi kabuğun içinde çalışır: `sed`, `basename` gibi dış programlar başlatmaz, bu yüzden döngülerde çok daha hızlıdır.

| Yazım | Ne yapar |
|---|---|
| `${x:-v}` | x boş ya da tanımsızsa `v` kullan (x değişmez) |
| `${x:=v}` | x boş ya da tanımsızsa x'e `v` ata ve kullan |
| `${x:?mesaj}` | x boş ya da tanımsızsa mesajı stderr'e yaz ve betiği durdur |
| `${x:+v}` | x doluysa `v`, değilse boş |
| `${#x}` | uzunluk |
| `${x#desen}`, `${x##desen}` | baştan en kısa / en uzun eşleşmeyi sil |
| `${x%desen}`, `${x%%desen}` | sondan en kısa / en uzun eşleşmeyi sil |
| `${x/a/b}`, `${x//a/b}` | ilk / bütün `a`'ları `b` yap |
| `${x^^}`, `${x,,}` | büyük / küçük harf |
| `${x:baş:uzunluk}` | alt metin (0'dan sayar) |
| `${!ad}` | dolaylı: adı `ad` değişkeninde yazan değişkenin değeri |

Desenler glob desenidir (`*`, `?`, `[...]`), düzenli ifade değil.

```bash
dosya="/var/log/nginx/erisim.log.gz"
echo "${dosya##*/}"                 #! en uzun "*/" baştan silinir: dosya adı
echo "${dosya%/*}"                  #! en kısa "/*" sondan silinir: klasör
echo "${dosya%%.*}"                 #! ilk noktadan sonrası gider
ad="${dosya##*/}"
echo "${ad%.gz}"
echo "${#dosya}"
s="web01-web02"
echo "${s/web/srv}" "${s//web/srv}" "${s^^}" "${s:3:2}"
```

```bash
unset port
echo "${port:-8080}"     #! varsayılanı kullan, port yine tanımsız
echo "${port:=443}"      #! ata
echo "$port"
alan="cpu"; cpu=72
echo "${!alan}"          #! dolaylı: $cpu
```

> [!TUZAK]
> İki nokta önemlidir. `${x:-v}` x **boşsa da** varsayılanı kullanır; `${x-v}` yalnızca x **hiç tanımlanmamışsa** kullanır. Kullanıcının bilerek boş bıraktığı bir değeri korumak istiyorsan iki noktasız sürümü seç.
:::

::: tahmin
Dört satır yazar:

```bash
yol="arsiv/2026/rapor.tar.gz"
echo "${yol##*/}"
echo "${yol#*/}"
echo "${yol%.*}"
echo "${yol%%.*}"
```

???

`rapor.tar.gz`, `2026/rapor.tar.gz`, `arsiv/2026/rapor.tar`, `arsiv/2026/rapor`. `##*/` baştaki en uzun "…/" kısmını, `#*/` en kısasını siler. `%.*` sondaki en kısa ".…" kısmını (yalnızca `.gz`), `%%.*` en uzununu (`.tar.gz`) siler.
:::

::: gorev Uzantıyı değiştir
Girdinin her satırı bir dosya adı. Her birinin **son** uzantısını `.bak` yapıp yazdır; uzantısı yoksa sonuna `.bak` ekle. `sed` ya da `basename` gibi dış komut kullanma.

```starter
while read -r f; do
    echo "$f.bak"
done
```

```stdin
rapor.txt
arsiv.tar.gz
notlar
```

```test
eq(run("rapor.txt\narsiv.tar.gz\nnotlar\n"), "rapor.bak\narsiv.tar.bak\nnotlar.bak\n", "üç dosya")
eq(run("klasör/alt/veri.csv\n"), "klasör/alt/veri.bak\n", "yollu ad")
ok("sed" not in src and "basename" not in src, "dış komut kullanma; parametre genişletmesi yeter")
```

```solution
while read -r f; do
    echo "${f%.*}.bak"
done
```

```hint
`${f%.*}` sondaki en kısa ".…" kısmını siler; nokta yoksa hiçbir şey silmez.
```
:::

::: gorev Varsayılan ayarlar
Betik `host` ve `port` değerlerini 1. ve 2. argümandan alsın; verilmezse ya da boş verilirse `localhost` ve `8080` kullansın. `host=... port=...` yazdırsın.

```starter
host=$1
port=$2
echo "host=$host port=$port"
```

```test
eq(run(), "host=localhost port=8080\n", "argümansız")
eq(run(argv=["web01"]), "host=web01 port=8080\n", "yalnızca host")
eq(run(argv=["", "443"]), "host=localhost port=443\n", "boş host → varsayılan")
```

```solution
host="${1:-localhost}"
port="${2:-8080}"
echo "host=$host port=$port"
```

```hint
`${1:-localhost}`: 1. argüman boş ya da yoksa localhost.
```
:::

::: gorev Zorunlu parametre
Betik bir dosya adı argümanı istesin. Verilmezse stderr'e `kullanım: betik <dosya>` yazıp **sıfırdan farklı** bir kodla dursun; verilirse `dosya: <ad>` yazsın. Tek satırlık `${1:?...}` kalıbını kullan.

```starter
echo "dosya: $1"
```

```meta
argv: rapor.txt
```

```test
eq(out, "dosya: rapor.txt\n", "argümanla")
r = calis()
ok(r["kod"] != 0, "argümansız: sıfırdan farklı kod", got=r["kod"])
ok("kullanım: betik <dosya>" in r["hata"], "mesaj stderr'de", got=r["hata"])
eq(r["cikti"], "", "argümansız durumda stdout boş")
ok(":?" in src, "${1:?...} kalıbını kullan")
```

```solution
dosya="${1:?kullanım: betik <dosya>}"
echo "dosya: $dosya"
```

```hint
`${1:?mesaj}` 1. argüman yoksa mesajı stderr'e yazar ve betiği durdurur.
```
:::
