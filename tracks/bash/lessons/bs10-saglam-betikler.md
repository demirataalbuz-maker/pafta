---
id: bs10
title: Sağlam Betikler
summary: set -euo pipefail, doğru tırnaklama, trap ile temizlik, mktemp, kullanım mesajı ve çıkış kodları.
kazanim: LPIC1 105.2
---

::: anlat Hata olunca durmayan betik tehlikelidir
Bash varsayılan olarak hata olsa da **devam eder**. `cd /yanlis/klasor` başarısız olursa bir sonraki `rm -rf *` satırı **yanlış dizinde** çalışır. Sağlam betiklerin ilk satırları neredeyse hep şunlardır:

```bash norun
#!/usr/bin/env bash
set -euo pipefail
```

| Ayar | Anlamı |
|---|---|
| `set -e` | bir komut başarısız olunca betikten çık |
| `set -u` | tanımsız değişken kullanılırsa hata ver (yazım hatalarını yakalar) |
| `set -o pipefail` | borudaki **herhangi bir** komut başarısız olursa boru başarısız sayılsın |

`set -e`'nin istisnaları vardır: `if`, `while`, `&&` ve `||` içindeki komutlar betiği durdurmaz. Bir hatanın bilinçli olarak tolere edildiğini göstermek için `komut || true` yazılır.

```bash
set -e
echo "başla"
false || echo "kurtarıldı"          #! || içindeki hata betiği durdurmaz
echo "bitti"
```

### trap ve mktemp: arkanda çöp bırakma
Geçici dosya oluşturan betik, hata ya da kesinti olsa bile onu silmelidir. `trap` bir sinyal ya da çıkış anında çalışacak komutu kaydeder:

```bash
gecici=$(mktemp)                    #! benzersiz geçici dosya
trap 'rm -f "$gecici"' EXIT         #! betik nasıl biterse bitsin çalışır
echo "ara veri" > "$gecici"
wc -l < "$gecici"
```

### Kullanım mesajı ve çıkış kodları
Argüman bekleyen her betik, yanlış çağrıldığında ne beklediğini **stderr**'e yazıp sıfırdan farklı bir kodla çıkmalıdır:

```bash norun
kullanim() { echo "kullanım: $0 <log-dosyası>" >&2; exit 2; }
[[ $# -eq 1 ]] || kullanim
[[ -f "$1" ]] || { echo "hata: dosya yok: $1" >&2; exit 1; }
```

> [!NOT]
> **ShellCheck** (`shellcheck betik.sh`) Bash betiklerindeki tırnaksız değişkenleri, yanlış testleri ve taşınabilirlik sorunlarını bulan bir statik analiz aracıdır. Python'daki linter'ların (P50) Bash karşılığıdır; ciddi her betikte kullanılmalıdır.

> [!GÜVENLİK]
> `mktemp` yerine `/tmp/benim_dosyam` gibi tahmin edilebilir bir yol kullanmak, paylaşılan sistemlerde bir saldırganın aynı adla önceden bir sembolik bağ bırakmasına ve betiğin başka bir dosyanın üzerine yazmasına yol açabilir (P26'daki TOCTOU'nun kabuk hali). `mktemp` benzersiz ve güvenli izinli dosya üretir.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
set -e
echo "başla"
false || echo "kurtarıldı"
echo "bitti"
```

???

`başla`, `kurtarıldı`, `bitti`. `false` başarısız olur ama `||`'nin sol tarafında olduğu için `set -e` devreye girmez; sağdaki komut çalışır ve betik devam eder.
:::

::: gorev Boşluklu dosya adları
Betik kendisine verilen her argümanı ayrı satırda köşeli parantez içinde yazdırmalı. Şu an boşluklu argümanları bölüyor; düzelt. Tezgahta `"yıllık rapor.txt" notlar.txt` argümanlarıyla çalışır; beklenen çıktı:

```cikti
[yıllık rapor.txt]
[notlar.txt]
```

```starter
for f in $@; do
    echo "[$f]"
done
```

```meta
argv: "yıllık rapor.txt" notlar.txt
```

```test
eq(run(argv=["yıllık rapor.txt", "notlar.txt"]), "[yıllık rapor.txt]\n[notlar.txt]\n", "boşluklu ad bölünmemeli")
eq(run(argv=["  baştaki boşluk"]), "[  baştaki boşluk]\n", "baştaki boşluklar korunmalı")
```

```solution
for f in "$@"; do
    echo "[$f]"
done
```

```hint
`$@` tırnaksız kullanılınca kelimelere bölünür. `"$@"` her argümanı olduğu gibi korur.
```
:::

::: gorev Geçici dosya temizliği
Girdiden gelen satırları çalışma klasöründe oluşturduğun bir geçici dosyaya (`mktemp ./gecici.XXXXXX`) yaz, sonra `satır: N` biçiminde satır sayısını yazdır. Betik bittiğinde geçici dosya **kalmamalı**; bunu `trap` ile garanti et.

```starter
gecici=$(mktemp ./gecici.XXXXXX)
cat > "$gecici"
echo "satır: $(wc -l < "$gecici")"
```

```stdin
bir
iki
üç
```

```test
import glob
eq(run("bir\niki\nüç\n"), "satır: 3\n", "3 satır")
eq(glob.glob("gecici.*"), [], "geçici dosya silinmiş olmalı")
ok("trap" in src, "trap kullan")
```

```solution
gecici=$(mktemp ./gecici.XXXXXX)
trap 'rm -f "$gecici"' EXIT
cat > "$gecici"
echo "satır: $(wc -l < "$gecici")"
```

```hint
Dosyayı oluşturduktan hemen sonra: `trap 'rm -f "$gecici"' EXIT`.
```
:::

::: gorev Log özeti aracı
Bir log dosyasını özetleyen sağlam bir betik yaz. Log satırları `SEVİYE mesaj...` biçiminde.

- Argüman yoksa: stderr'e `kullanım: ...` yaz, **2** ile çık
- Dosya yoksa: stderr'e `hata: ...` yaz, **1** ile çık
- Varsa şunu yazdır:

```cikti
toplam: 7
hata: 4
en sık hata: bağlantı koptu
```

`en sık hata`, `ERROR` satırlarının mesaj kısmından en çok tekrar edenidir.

```setup
open("app.log", "w", encoding="utf-8", newline="\n").write(
    "INFO başladı\nERROR bağlantı koptu\nWARN yavaş yanıt\nERROR disk dolu\n"
    "ERROR bağlantı koptu\nINFO istek tamam\nERROR bağlantı koptu\n")
```

```starter
dosya=$1
echo "toplam: $(wc -l < "$dosya")"
```

```meta
argv: app.log
```

```test
eq(out, "toplam: 7\nhata: 4\nen sık hata: bağlantı koptu\n", "özet")
r = calis()
eq(r["kod"], 2, "argümansız → kod 2")
ok("kullanım" in r["hata"], "kullanım mesajı stderr'de", got=r["hata"])
r = calis(argv=["yok.log"])
eq(r["kod"], 1, "dosya yok → kod 1")
ok("hata" in r["hata"], "hata mesajı stderr'de", got=r["hata"])
```

```solution
set -euo pipefail

kullanim() { echo "kullanım: $0 <log-dosyası>" >&2; exit 2; }
[[ $# -eq 1 ]] || kullanim
dosya=$1
[[ -f "$dosya" ]] || { echo "hata: dosya yok: $dosya" >&2; exit 1; }

toplam=$(wc -l < "$dosya")
hata=$(grep -c '^ERROR' "$dosya" || true)
en_sik=$(grep '^ERROR' "$dosya" | cut -d' ' -f2- | sort | uniq -c | sort -rn | head -n 1 | sed -E 's/^ *[0-9]+ //')

echo "toplam: $toplam"
echo "hata: $hata"
echo "en sık hata: $en_sik"
```

```hint
Önce iki koruma: argüman sayısı (`[[ $# -eq 1 ]]`) ve dosya varlığı (`[[ -f "$dosya" ]]`).
```

```hint
En sık hata: `grep '^ERROR' | cut -d' ' -f2- | sort | uniq -c | sort -rn | head -n 1`, sonra baştaki sayıyı `sed -E 's/^ *[0-9]+ //'` ile at.
```
:::
