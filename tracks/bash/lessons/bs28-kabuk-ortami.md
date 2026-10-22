---
id: bs28
title: Kabuk Ortamı · Başlangıç Dosyaları, alias, sha256sum ve nice
summary: Login, etkileşimli ve etkileşimsiz kabukların okuduğu dosyalar (.bash_profile, .bashrc), source ile çocuk kabuk farkı, alias ve betiklerde expand_aliases, type, sha256sum ile özet çıkarmak ve -c ile doğrulamak, nice ve renice ile süreç önceliği.
kazanim: LPIC1 103.1, LPIC1 103.2, LPIC1 103.6, LPIC1 104.7, LPIC1 105.1
---

::: anlat Başlangıç dosyaları
Bash açılırken bazı dosyaları okur ve içindeki komutları çalıştırır. Hangisini okuyacağı kabuğun **türüne** bağlıdır:

| Kabuk türü | Örnek | Okunan dosyalar |
|---|---|---|
| **login** | SSH ile giriş, `bash -l`, metin konsolunda giriş | `/etc/profile`, sonra `~/.bash_profile`, `~/.bash_login`, `~/.profile`'dan **ilk bulunan** |
| **etkileşimli**, login olmayan | masaüstünde yeni bir terminal sekmesi | `~/.bashrc` |
| **etkileşimsiz** | bir betik | hiçbiri (`BASH_ENV` değişkeni bir dosya gösteriyorsa yalnızca o) |

Yaygın düzen: ortam değişkenleri (`export PATH=...`) `~/.bash_profile`'a, alias'lar, istem (`PS1`) ve fonksiyonlar `~/.bashrc`'ye yazılır; `~/.bash_profile` de `~/.bashrc`'yi okur:

```bash norun
# ~/.bash_profile
export EDITOR=nano
[ -f ~/.bashrc ] && . ~/.bashrc
```

Bir dosyayı **o anki kabukta** çalıştırmak için `source dosya` (kısaca `. dosya`) yazılır. `bash dosya` ise bir **çocuk kabuk** açar; orada tanımlanan değişkenler çocuk kapanınca kaybolur. `~/.bashrc`'yi değiştirdikten sonra `source ~/.bashrc` yazmanın nedeni budur:

```bash
printf 'export EKIP=altyapi\nSAYAC=1\n' > ayarlar.sh
bash ayarlar.sh; echo "çocuk: ${EKIP:-yok}"
source ayarlar.sh; echo "source: $EKIP $SAYAC"
```

Kabuğun türünü sorabilirsin: `$-` etkileşimli kabukta `i` harfini içerir; `shopt -q login_shell` login kabukta başarıyla döner.

> [!GÜVENLİK]
> Başlangıç dosyaları her oturumda kendiliğinden çalışan koddur. Sahibi sen olmalısın ve başkası yazamamalı (`chmod 644 ~/.bashrc`). `PATH`'in başına `.` ya da herkesin yazabildiği bir klasör koyma: o zaman `ls` yazdığında o klasördeki aynı adlı bir dosya çalışabilir.
:::

::: anlat alias ve type
**alias**, bir komutun başına konan kısaltmadır:

| Komut | Ne yapar |
|---|---|
| `alias ll='ls -la'` | `ll` yazınca `ls -la` çalışır |
| `alias` | tanımlı alias'ları listeler |
| `unalias ll` | siler |
| `\ls` ya da `command ls` | alias'ı atlayıp asıl komutu çalıştırır |
| `type ad` | bir adın ne olduğunu söyler: alias, fonksiyon, yerleşik komut ya da dosya |

Alias'ların üç kuralı:

1. Yalnızca bir komutun **ilk kelimesinde** açılır.
2. Etkileşimsiz kabukta, yani **betiklerde varsayılan olarak açılmaz**; `shopt -s expand_aliases` gerekir.
3. Bash bir satırı okurken alias'ları açar: aynı satırda tanımlanan alias o satırda henüz geçerli değildir.

Betiklerde alias yerine **fonksiyon** yazılır: argümanı istediğin yerde kullanabilir, tırnaklama sorunu çıkarmaz.

```bash
shopt -s expand_aliases
alias bugun='date +%Y'
alias
type bugun
yedekle() { cp -- "$1" "$1.bak"; }
type -t yedekle
```
:::

::: anlat sha256sum ve nice
`sha256sum dosya` bir dosyanın SHA-256 özetini yazar. Tek bayt değişse özet tamamen değişir; indirilen bir dosyanın doğruluğunu ya da bir klasörün değişip değişmediğini (Python'daki P52 ile aynı bütünlük fikri) böyle denetlersin:

| Komut | Ne yapar |
|---|---|
| `sha256sum a b > ozet.sha256` | her dosyanın özetini bir listeye yazar |
| `sha256sum -c ozet.sha256` | listedeki her dosyayı yeniden hesaplar: `a: OK` ya da `a: FAILED`; biri tutmazsa çıkış kodu 1 |
| `sha256sum -c --quiet ozet.sha256` | yalnızca tutmayanları yazar |

Liste satırı `özet  dosya` biçimindedir (iki boşluk). Git Bash'te `özet *dosya` görürsün: `*` dosyanın ikili kipte okunduğunu gösterir; `-c` ikisini de anlar. `md5sum` ve `sha1sum` aynı biçimde çalışır ama çakışma üretilebildiği için bütünlük için SHA-256 kullanılır.

```bash
printf 'merhaba\n' > a.txt
sha256sum a.txt | cut -d' ' -f1
```

**nice** bir komutu daha **düşük öncelikle** başlatır. Nezaket değeri -20 (en yüksek öncelik) ile 19 (en düşük) arasındadır; varsayılan 0'dır. Değeri artırmak herkesin hakkıdır, düşürmek yalnızca yöneticinin. Uzun bir sıkıştırma ya da yedekleme işini sistemi yormadan çalıştırmak için kullanılır:

```bash
nice
nice -n 7 nice
```

Çalışan bir sürecin önceliği `renice -n 10 -p PID` ile değiştirilir; `ps -o pid,ni,cmd` süreçlerin nezaket değerlerini gösterir. (`renice` Git Bash'te yoktur; Linux'ta bulunur.)
:::

::: tahmin
Dört satır yazar:

```bash
shopt -s expand_aliases
alias selam='echo merhaba'
selam dunya
printf 'veri\n' > a.txt
sha256sum a.txt > ozet.txt
sha256sum -c ozet.txt
printf 'degisti\n' > a.txt
sha256sum -c --quiet ozet.txt 2>/dev/null; echo "kod: $?"
```

???

`merhaba dunya`, `a.txt: OK`, `a.txt: FAILED` ve `kod: 1`. Alias yalnızca ilk kelimenin yerine geçer; `dunya` argüman olarak kalır. Dosya değişmeden önce doğrulama tutar. İçerik değişince özet tutmaz: `--quiet` yalnızca tutmayan dosyayı yazar ve `sha256sum` 1 koduyla çıkar.
:::

::: gorev Değişen dosyalar
Çalışma klasöründe `a.txt`, `b.txt`, `c.txt` ve bunların özgün özetlerini tutan `ozet.sha256` var. Betik, özeti artık tutmayan (değişmiş ya da silinmiş) dosyaların adlarını listedeki sırayla, her biri ayrı satırda yazsın; en sonda `değişen: N` yazsın. Değişen yoksa yalnızca `değişen: 0`.

```setup
import hashlib
icerik = {"a.txt": "bir\n", "b.txt": "iki\n", "c.txt": "üç\n"}
with open("ozet.sha256", "w", encoding="utf-8", newline="\n") as f:
    for ad, metin in icerik.items():
        f.write(hashlib.sha256(metin.encode("utf-8")).hexdigest() + "  " + ad + "\n")
for ad, metin in icerik.items():
    open(ad, "w", encoding="utf-8", newline="\n").write(metin)
open("b.txt", "w", encoding="utf-8", newline="\n").write("iki ve fazlası\n")
```

```starter
sha256sum -c ozet.sha256
```

```test
import os
eq(run(), "b.txt\ndeğişen: 1\n", "b.txt değişmiş")
open("b.txt", "w", encoding="utf-8", newline="\n").write("iki\n")
eq(run(), "değişen: 0\n", "b.txt eski hâline döndü: hiçbiri değişmedi")
os.remove("c.txt")
eq(run(), "c.txt\ndeğişen: 1\n", "silinen dosya da tutmayan sayılır")
open("a.txt", "w", encoding="utf-8", newline="\n").write("BIR\n")
eq(run(), "a.txt\nc.txt\ndeğişen: 2\n", "iki dosya, listedeki sırayla")
ok("sha256sum" in src and "-c" in src, "sha256sum -c ile doğrula")
```

```solution
degisen=$(sha256sum -c --quiet ozet.sha256 2>/dev/null | cut -d: -f1)
if [ -n "$degisen" ]; then
    printf '%s\n' "$degisen"
fi
echo "değişen: $(printf '%s' "$degisen" | grep -c .)"
```

```hint
`sha256sum -c --quiet ozet.sha256 2>/dev/null` yalnızca tutmayan satırları (`b.txt: FAILED`) yazar; uyarılar hata akışına gider. `cut -d: -f1` dosya adını alır.
```

```hint
Satırları saymak için `grep -c .` boş olmayan satırları sayar; değişken boşsa 0 verir.
```
:::

::: gorev Betikte alias
Betik `hatalar` adında bir **alias** tanımlasın: `grep -c ERROR`. Sonra ilk argümanla verilen dosyada bu alias'la sayım yapıp `hata: N` yazsın. Betik etkileşimsiz bir kabukta çalıştığı için alias'ların açılmasını sağlamalısın.

```setup
open("gunluk.txt", "w", encoding="utf-8", newline="\n").write(
    "INFO başladı\nERROR disk dolu\nWARN yavaş\nERROR zaman aşımı\nerror küçük harf sayılmaz\n")
open("temiz.txt", "w", encoding="utf-8", newline="\n").write("INFO her şey yolunda\n")
```

```starter
alias hatalar='grep -c ERROR'
echo "hata: $(hatalar "$1")"
```

```meta
argv: gunluk.txt
```

```test
eq(run(argv=["gunluk.txt"]), "hata: 2\n", "iki ERROR satırı (küçük harfli error sayılmaz)")
eq(run(argv=["temiz.txt"]), "hata: 0\n", "hatasız dosya")
ok("expand_aliases" in src, "betikte alias'lar için shopt -s expand_aliases")
ok("alias hatalar=" in src, "hatalar alias'ını tanımla")
```

```solution
shopt -s expand_aliases
alias hatalar='grep -c ERROR'
echo "hata: $(hatalar "$1")"
```

```hint
Etkileşimsiz kabukta alias'lar açılmaz: alias'ı tanımlamadan önce `shopt -s expand_aliases` yaz. Alias'ı ayrı bir satırda tanımla; aynı satırda henüz geçerli olmaz.
```
:::

::: gorev Nazik çalıştır
Betik ilk argümanı bir nezaket seviyesi olarak alsın, sınırlara çeksin ve seçtiği seviyeyi, `nice` ile çalıştırılan bir komutun gördüğü seviyeyle birlikte `seviye: N (nice: M)` diye yazsın:

- argüman bir tam sayı değilse (eksi işareti olabilir) hata akışına `geçersiz seviye: <argüman>` yazıp **2** koduyla çıksın
- 19'dan büyükse 19, 0'dan küçükse 0 seçsin (yönetici olmayan biri önceliği yükseltemez)
- `M`'yi `nice -n <seçilen seviye> nice` ile ölçsün

```starter
echo "seviye: $1 (nice: $(nice -n "$1" nice))"
```

```meta
argv: 7
```

```test
eq(run(argv=["7"]), "seviye: 7 (nice: 7)\n", "7")
eq(run(argv=["19"]), "seviye: 19 (nice: 19)\n", "üst sınır 19")
eq(run(argv=["20"]), "seviye: 19 (nice: 19)\n", "20 → 19 (betik kendisi sınırlar)")
eq(run(argv=["0"]), "seviye: 0 (nice: 0)\n", "alt sınır 0")
eq(run(argv=["-1"]), "seviye: 0 (nice: 0)\n", "-1 → 0")
eq(run(argv=["-30"]), "seviye: 0 (nice: 0)\n", "-30 → 0")
r = calis(argv=["yedi"])
eq((r["kod"], r["cikti"]), (2, ""), "sayı değil: çıkış kodu 2, çıktı yok")
ok("geçersiz seviye: yedi" in r["hata"], "hata mesajı hata akışında")
eq(calis(argv=["7x"])["kod"], 2, "rakamdan sonra harf")
eq(calis(argv=[])["kod"], 2, "argüman yok")
```

```solution
n="${1:-}"
if ! [[ "$n" =~ ^-?[0-9]+$ ]]; then
    echo "geçersiz seviye: $n" >&2
    exit 2
fi
if (( n > 19 )); then
    n=19
fi
if (( n < 0 )); then
    n=0
fi
echo "seviye: $n (nice: $(nice -n "$n" nice))"
```

```hint
`[[ "$n" =~ ^-?[0-9]+$ ]]` bir tam sayı olup olmadığını söyler; `^` ve `$` bütün metnin eşleşmesini sağlar. Sınırlar için `(( n > 19 ))` ve `(( n < 0 ))`. `nice` 19'un üstünü kendisi de 19'a çeker; ama hangi seviyeyi seçtiğini betiğin kendisi bilmeli.
```
:::
