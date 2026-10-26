---
id: bs30
title: ShellCheck ve Bats ile Kendi Aracını Sınamak
summary: Gerçek Linux'ta ShellCheck: bulgu seviyeleri ve -S'nin birikimli eşiği, -f gcc ve json1, çıkış kodları (0 temiz, 1 bulgu, 4 geçersiz seçenek), -e ve gerekçeli yönerge; Bats: @test, run, $status, $output, setup, TAP çıktısı, run'ın stderr'i de output'a katması ve testlerini bozuk bir uygulamaya karşı denemek.
backend: wsl
timeout: 120
---

::: anlat ShellCheck: betiğini çalıştırmadan okuyan denetçi
Bu dersin bütün adımları **gerçek Linux'ta** (Kali, WSL) çalışır; ShellCheck 0.11 ve Bats 1.13 orada kurulu.

BS24'te ShellCheck'in en sık uyarılarını adıyla gördün. Şimdi aracın kendisini çalıştıracaksın. ShellCheck betiği çalıştırmaz; okur ve kabuğun bilinen tuzaklarını işaretler:

```bash
cat > yedekle.sh <<'BETIK'
#!/bin/bash
hedef=$1
cd $hedef
for dosya in $(ls); do
    cp $dosya /tmp/yedek/
done
BETIK
shellcheck -f gcc yedekle.sh; echo "çıkış=$?"
```

Her satırda konum, **seviye**, açıklama ve `SC` kodu var. Seviyeler en ağırdan en hafife: `error`, `warning`, `info`, `style`. `-S seviye` o seviye **ve daha ağırları** gösterir; yani eşik birikimlidir. Bu derste ölçüldü: bir yedekleme betiğinde `-S error` 1, `-S warning` 3, `-S info` 10, `-S style` 12 bulgu verdi.

| Seçenek | Ne yapar |
|---|---|
| `-f gcc` | Derleyici biçimi: `dosya:satır:sütun: seviye: açıklama [SCxxxx]` |
| `-f json1` | Makinenin okuyacağı JSON: `.comments[]` içinde `code`, `level`, `line`, `message` |
| `-S warning` | Eşik: yalnız warning ve error |
| `-e SC2034` | Bir kodu dışla |
| `-s bash` | Shebang yoksa ya da betik stdin'den (`-`) geliyorsa kabuğu söyle |

Çıkış kodları: bulgu yoksa **0**, bulgu varsa **1**, geçersiz bir seçenek verirsen **4** (ör. `-S acil`). Shebang'i olmayan bir dosya ayrıca `SC2148` hatası alır: kabuğu bilmeden önerinin doğruluğu belirsizdir.

> [!TUZAK] Uyarıyı susturmak, hatayı düzeltmek değildir
> `# shellcheck disable=SC2086` yönergesi o satırdaki uyarıyı kapatır. Bazen haklıdır: argümanları bilerek kelimelere bölüyorsundur. O zaman yönergenin üstüne **neden** yazdığını açıklayan bir yorum koy. Gerekçesiz bir `disable`, bir sonraki okuyucuya "burada bir şey var ama bakma" demektir. Düzeltmesi tırnak eklemek kadar kolaysa düzelt.
:::

::: anlat Bats: betiğin sözleşmesini test etmek
Bir komut satırı aracının sözleşmesi üç şeydir: **çıktı**, **hata akışı** ve **çıkış kodu**. Bats bunları sınamak için yazılmış bir test çatısıdır. Bir `.bats` dosyası Bash'tir, artı `@test` blokları:

```bash
cat > topla.sh <<'BETIK'
#!/bin/bash
[[ $# -eq 2 ]] || { echo "kullanim: topla.sh a b" >&2; exit 2; }
echo $(( $1 + $2 ))
BETIK
chmod +x topla.sh

cat > topla.bats <<'TEST'
setup() {
    HEDEF=${HEDEF:-./topla.sh}
}

@test "iki sayıyı toplar" {
    run "$HEDEF" 2 3
    [ "$status" -eq 0 ]
    [ "$output" = "5" ]
}

@test "eksik argümanda 2 ile çıkar" {
    run "$HEDEF" 1
    [ "$status" -eq 2 ]
    [[ $output == *kullanim* ]]
}
TEST
bats --tap topla.bats; echo "çıkış=$?"
```

| Parça | Ne yapar |
|---|---|
| `@test "ad" { ... }` | Bir test; içindeki herhangi bir komut başarısız olursa test düşer |
| `run komut` | Komutu çalıştırır, sonucu **testi düşürmeden** değişkenlere koyar |
| `$status` | Çıkış kodu |
| `$output`, `${lines[@]}` | Çıktı, bütün olarak ve satır satır |
| `setup` / `teardown` | Her testten önce / sonra çalışır |
| `bats --tap` | TAP biçimi: `1..N`, `ok 1 ...`, `not ok 2 ...` |

`bats` bütün testler geçerse **0**, biri bile düşerse **1** ile çıkar; düşen testin altında hangi satırın tutmadığı yazar. Bu kurulumda `bats-assert` yardımcıları yok; karşılaştırmalar düz `[ ]` ve `[[ ]]` ile yapılır.

> [!TUZAK] `run` hata akışını da `$output`'a katar
> Bats 1.13'te `run` varsayılan olarak stdout ile stderr'i **birleştirir**: `echo out; echo err >&2` çalıştıran bir komutta `${#lines[@]}` 2 olur. Yukarıdaki `*kullanim*` denetimi bu yüzden çalışır, mesaj stderr'e yazıldığı hâlde. İkisini ayırman gerekirse `run --separate-stderr` ve `$stderr` kullan.

> [!DERİN] Testlerini kim test eder?
> Yukarıdaki `HEDEF` değişkeni testlerin hangi uygulamayı sınadığını dışarıdan değiştirmeye yarar. `HEDEF=./bozuk.sh bats topla.bats` ile testleri bilerek bozulmuş bir uygulamaya karşı çalıştırırsın: hiçbir test düşmüyorsa testlerin o hatayı göremiyordur. Bu, P69'daki mutasyon testinin kabuktaki karşılığıdır.
:::

::: tahmin
Ne yazar?

```bash
printf '#!/bin/bash\necho $1\ncd /tmp\n' > a.sh
shellcheck -S warning a.sh > /dev/null; echo "warning: $?"
shellcheck -S error a.sh > /dev/null; echo "error: $?"
shellcheck -S acil a.sh 2> /dev/null; echo "acil: $?"
```

???

`warning: 1`, `error: 0` ve `acil: 4`.

Betikte iki bulgu var: tırnaksız `$1` bir `info` (SC2086), `|| exit`'siz `cd` bir `warning`dır (SC2164). `-S warning` warning ve error'u gösterir; `cd` bulgusu eşiği geçer, çıkış 1 olur. `-S error` yalnız error'ları gösterir, ikisi de onun altında kaldığı için hiç bulgu yoktur ve çıkış 0'dır — aynı betik, eşiğe göre "temiz" sayılabilir. `acil` geçerli bir seviye değildir: ShellCheck seçeneği reddeder ve 4 ile çıkar.
:::

::: gorev Seviye eşiği
Çalışma klasöründe hatalı bir `yedekle.sh` var. Girdinin ilk satırı bir ShellCheck seviyesidir (`error`, `warning`, `info`, `style`). O eşikle ShellCheck'i çalıştır ve bulunan her **SC kodu** için kod sırasıyla `SC<kod> <seviye> <adet>` satırı yazdır; en sona `toplam <bulgu sayısı>` ekle.

Seviye bu dördünden biri değilse ya da girdi boşsa tek satır `HATA` yazdır. Çıktıyı metinden ayıklamaya çalışma; `-f json1` ve `jq` kullan.

```stdin
warning
```

```setup
import pathlib
pathlib.Path("yedekle.sh").write_text(
    "#!/bin/bash\n"
    "hedef=$1\n"
    "kaynak=$2\n"
    "gecici=$(mktemp -d)\n"
    "cd $hedef\n"
    "for dosya in $(ls $kaynak); do\n"
    "    cp $kaynak/$dosya $gecici\n"
    "done\n"
    "sayi=`ls $gecici | wc -l`\n"
    "if [ $? -ne 0 ]; then echo \"hata\"; fi\n"
    "local_degisken=5\n"
    "echo \"kopyalanan: $sayi\"\n",
    encoding="utf-8", newline="\n")
```

```starter
read -r seviye
shellcheck -S "$seviye" yedekle.sh
```

```test
eq(out, "SC2034 warning 1\nSC2045 error 1\nSC2164 warning 1\ntoplam 3\n", "warning eşiği: warning ve error")
eq(run(stdin="error\n"), "SC2045 error 1\ntoplam 1\n", "en dar eşik: yalnız error")
eq(run(stdin="info\n"), "SC2012 info 1\nSC2034 warning 1\nSC2045 error 1\nSC2086 info 6\nSC2164 warning 1\ntoplam 10\n",
   "info eşiği: SC2086 altı ayrı yerde")
eq(run(stdin="style\n"), "SC2006 style 1\nSC2012 info 1\nSC2034 warning 1\nSC2045 error 1\nSC2086 info 6\nSC2164 warning 1\nSC2181 style 1\ntoplam 12\n",
   "en geniş eşik: her şey")
eq(run(stdin="acil\n"), "HATA\n", "geçersiz seviye")
eq(run(stdin="Warning\n"), "HATA\n", "seviye adları küçük harf")
eq(run(stdin="\n"), "HATA\n", "boş girdi")
ok("json1" in src, "bulguları -f json1 ile oku")
```

```solution
read -r seviye || true
case $seviye in
    error | warning | info | style) ;;
    *) echo HATA; exit 0 ;;
esac
shellcheck -S "$seviye" -f json1 yedekle.sh > bulgular.json
jq -r '.comments | group_by(.code)[] | "SC\(.[0].code) \(.[0].level) \(length)"' bulgular.json
echo "toplam $(jq '.comments | length' bulgular.json)"
```

```hint
`shellcheck` bulgu bulunca 1 ile çıkar; betiğin `set -e` olmadan bunu dert etmez. Çıktıyı bir dosyaya al ve iki ayrı `jq` ile oku: biri gruplar, biri sayar.
```

```hint
`group_by(.code)` aynı koddaki bulguları bir diziye toplar ve kodlara göre sıralar; her grubun `length`'i adettir, `.[0].level` seviyesidir.
```
:::

::: gorev Betiği düzelt
Aşağıdaki betik bir klasördeki **dosyaları** (alt klasörler hariç, yalnız o düzeydekiler) sayıp en büyüğünün adını yazmalı. Ama boşluklu bir klasör adında `0` yazıyor ve ShellCheck üç bulgu veriyor. Düzelt:

- Klasör ilk argümandır. Çıktı tek satır: `<dosya sayısı> <en büyük dosyanın adı>`; klasör boşsa `0 -`.
- Argüman yoksa ya da klasör değilse stderr'e `dizin yok: <argüman>` yaz ve **2** ile çık.
- Betik `shellcheck -S style` ile **hiç bulgu vermemeli**.

Çalışma klasöründe şunlar hazır: `kayitlar 2026/` (içinde `rapor 1.txt` 30 bayt, `rapor 2.txt` 10 bayt, `-n.txt` 5 bayt ve bir alt klasör), boş `bos/`, `alt/` (içinde 1 baytlık `kok.txt` ve alt klasörde 50 baytlık bir dosya), `-eski/` (içinde 7 baytlık `not.txt`). Normal çalışmada stderr'e hiçbir şey yazılmamalı.

```setup
import pathlib
k = pathlib.Path("kayitlar 2026")
(k / "klasor").mkdir(parents=True, exist_ok=True)
(k / "rapor 1.txt").write_text("0" * 30, encoding="utf-8")
(k / "rapor 2.txt").write_text("0" * 10, encoding="utf-8")
(k / "-n.txt").write_text("0" * 5, encoding="utf-8")
pathlib.Path("bos").mkdir(exist_ok=True)
(pathlib.Path("alt") / "ic").mkdir(parents=True, exist_ok=True)
(pathlib.Path("alt") / "ic" / "derin.txt").write_text("0" * 50, encoding="utf-8")
(pathlib.Path("alt") / "kok.txt").write_text("x", encoding="utf-8")
pathlib.Path("-eski").mkdir(exist_ok=True)
(pathlib.Path("-eski") / "not.txt").write_text("0" * 7, encoding="utf-8")
```

```starter
#!/bin/bash
dizin=$1
sayi=0
for dosya in $(ls $dizin); do
    sayi=$((sayi + 1))
    enbuyuk=$dosya
done
echo $sayi $enbuyuk
```

```meta
argv: "kayitlar 2026"
```

```test
import subprocess
eq(out, "3 rapor 1.txt\n", "boşluklu klasör; alt klasör sayılmaz; - ile başlayan ad da dosyadır")
eq(run(argv=["bos"]), "0 -\n", "boş klasör")
eq(run(argv=["alt"]), "1 kok.txt\n", "yalnız o düzeydeki dosyalar: alt klasördeki büyük dosya sayılmaz")
eski = calis(argv=["-eski"])
eq(eski["cikti"], "1 not.txt\n", "adı - ile başlayan klasör")
eq(eski["hata"], "", "adı - ile başlayan klasörde stderr boş: yol seçenek sanılmamalı")
eq(calis(argv=["kayitlar 2026"])["hata"], "", "normal çalışmada stderr boş")
dosya = calis(argv=["alt/kok.txt"])
eq(dosya["kod"], 2, "klasör değil dosya verilince de çıkış 2")
yok = calis(argv=["yok"])
eq(yok["kod"], 2, "olmayan klasörde çıkış 2")
eq(yok["cikti"], "", "hata durumunda stdout boş")
ok("dizin yok: yok" in yok["hata"], "mesaj stderr'de")
bos = calis()
eq(bos["kod"], 2, "argüman yoksa çıkış 2")
denetim = subprocess.run(["shellcheck", "-s", "bash", "-S", "style", "-f", "gcc", "-"], input=src,
                         capture_output=True, text=True)
eq(denetim.stdout, "", "ShellCheck hiç bulgu vermemeli")
eq(denetim.returncode, 0, "ShellCheck çıkış kodu 0")
```

```solution
#!/bin/bash
dizin=${1:-}
if [[ ! -d $dizin ]]; then
    echo "dizin yok: $dizin" >&2
    exit 2
fi
sayi=0
enbuyuk="-"
enboyut=-1
for yol in "$dizin"/*; do
    [[ -f $yol ]] || continue
    sayi=$((sayi + 1))
    boyut=$(stat -c %s -- "$yol")
    if ((boyut > enboyut)); then
        enboyut=$boyut
        enbuyuk=${yol##*/}
    fi
done
echo "$sayi $enbuyuk"
```

```hint
`$(ls $dizin)` iki kez bozar: tırnaksız `$dizin` boşlukta ikiye bölünür, `ls`'in çıktısı da boşluklu adlarda bölünür (SC2045). Glob kullan: `for yol in "$dizin"/*`. Boş klasörde glob olduğu gibi kalır; `[[ -f $yol ]] || continue` onu da eler.
```

```hint
Boyut için `stat -c %s -- "$yol"`: `--`, `-` ile başlayan bir yolun (`-eski/not.txt`) seçenek sanılmasını önler. Adı yoldan `${yol##*/}` ile ayır.
```
:::

::: gorev Testlerini bozuk uygulamaya karşı dene
Çalışma klasöründe `topla.sh` var. Sözleşmesi:

- `topla.sh a b`: iki **tam sayı** (eksi olabilir) alır, toplamı yazar, **0** ile çıkar.
- Argüman sayısı iki değilse stderr'e kullanım mesajı yazar, **2** ile çıkar.
- Argümanlardan biri tam sayı değilse stderr'e `sayi degil: <argüman>` yazar, **2** ile çıkar.

Betiğin `topla.bats` adlı bir Bats test dosyası **yazsın** ve `bats --tap topla.bats` ile çalıştırsın. Testler sınanan programı `HEDEF` ortam değişkeninden alsın, yoksa `./topla.sh` kullansın.

Testlerin doğru uygulamada hepsi geçmeli. Klasörde ayrıca dört **bozuk** uygulama var; testlerinin **her birini** yakalaması (en az bir testin düşmesi) gerekiyor. Hangi hataları taşıdıklarını bilmiyorsun: sözleşmenin her maddesini, sınır ve hatalı girdiyle birlikte sına.

```setup
import pathlib, stat

def betik(ad, govde):
    yol = pathlib.Path(ad)
    yol.write_text("#!/bin/bash\n" + govde, encoding="utf-8", newline="\n")
    yol.chmod(yol.stat().st_mode | stat.S_IXUSR)

KULLANIM = 'if [[ $# -ne 2 ]]; then echo "kullanim: topla.sh a b" >&2; exit {kod}; fi\n'
DENETIM = ('for s in "$1" "$2"; do\n'
           '    if [[ ! $s =~ {desen} ]]; then echo "sayi degil: $s" >&2; exit 2; fi\n'
           'done\n')
betik("topla.sh", KULLANIM.format(kod=2) + DENETIM.format(desen="^-?[0-9]+$") + 'expr "$1" + "$2"\n')
betik("bozuk_fark.sh", KULLANIM.format(kod=2) + DENETIM.format(desen="^-?[0-9]+$") + 'expr "$1" - "$2"\n')
betik("bozuk_kod.sh", KULLANIM.format(kod=1) + DENETIM.format(desen="^-?[0-9]+$") + 'expr "$1" + "$2"\n')
betik("bozuk_eksi.sh", KULLANIM.format(kod=2) + DENETIM.format(desen="^[0-9]+$") + 'expr "$1" + "$2"\n')
betik("bozuk_harf.sh", KULLANIM.format(kod=2) + 'echo $(( $1 + $2 ))\n')
```

```starter
cat > topla.bats <<'TEST'
@test "çalışıyor" {
    run ./topla.sh 1 1
    [ "$status" -eq 0 ]
}
TEST
bats --tap topla.bats
```

```test
import os, subprocess
satirlar = out.splitlines()
ok(bool(satirlar) and satirlar[0].startswith("1.."), "TAP planı ilk satırda: 1..N")
n = int(satirlar[0][3:]) if satirlar and satirlar[0][3:].isdigit() else 0
ok(n >= 3, "en az üç test")
eq(sum(1 for s in satirlar if s.startswith("ok ")), n, "doğru uygulamada bütün testler geçmeli")
ok(not any(s.startswith("not ok") for s in satirlar), "doğru uygulamada düşen test olmamalı")

def dene(hedef):
    return subprocess.run(["bats", "--tap", "topla.bats"], env=dict(os.environ, HEDEF=hedef),
                          capture_output=True, text=True).returncode

eq(dene("./topla.sh"), 0, "HEDEF açıkça doğru uygulamayı gösterince de geçmeli")
ok(dene("./bozuk_fark.sh") != 0, "bozuk_fark.sh yakalanmadı: toplamın değerini sına")
ok(dene("./bozuk_kod.sh") != 0, "bozuk_kod.sh yakalanmadı: yanlış argüman sayısındaki çıkış kodunu sına")
ok(dene("./bozuk_eksi.sh") != 0, "bozuk_eksi.sh yakalanmadı: eksi sayıyı sına")
ok(dene("./bozuk_harf.sh") != 0, "bozuk_harf.sh yakalanmadı: sayı olmayan argümanı sına")
```

```solution
cat > topla.bats <<'TEST'
setup() {
    HEDEF=${HEDEF:-./topla.sh}
}

@test "iki sayıyı toplar" {
    run "$HEDEF" 2 3
    [ "$status" -eq 0 ]
    [ "$output" = "5" ]
}

@test "eksi sayılarla toplar" {
    run "$HEDEF" -4 1
    [ "$status" -eq 0 ]
    [ "$output" = "-3" ]
}

@test "eksik argümanda 2 ile çıkar" {
    run "$HEDEF" 1
    [ "$status" -eq 2 ]
    [[ $output == *kullanim* ]]
}

@test "fazla argümanda 2 ile çıkar" {
    run "$HEDEF" 1 2 3
    [ "$status" -eq 2 ]
}

@test "sayı olmayan argümanda 2 ile çıkar" {
    run "$HEDEF" 1 iki
    [ "$status" -eq 2 ]
    [[ $output == *"sayi degil"* ]]
}
TEST
bats --tap topla.bats
```

```hint
Her testte `"$HEDEF"`'i çalıştır, `./topla.sh`'yi değil; yoksa bozuk uygulamalar hiç sınanmaz. `setup` içinde `HEDEF=${HEDEF:-./topla.sh}`.
```

```hint
Yalnız "çıkış 0 mı?" diye sormak yetmez: değeri (`$output`), hata durumundaki **kodu** (`$status`) ve sınırdaki girdiyi (eksi sayı) ayrı ayrı sına.
```
:::


::: anlat teardown: test düştüğünde de temizle
Bats setup/teardown her testin öncesi/sonrasında çalışır. Testte false veya başarısız bir assertion olması teardown'ı atlamak için sebep değildir. Temizliği testin son satırına koyarsan o satıra ulaşılmayabilir. Her test kendi mktemp klasörünü alsın; temizlenecek yolu setup'ta sakla, teardown'da yalnız o yolu sil. Klasör adını sabitlemek testler arası veri sızıntısını gizleyebilir.

Bats'in yönettiği BATS_TEST_TMPDIR ile uygulamanın başka yerde ürettiği geçici dosya aynı şey değildir. Aşağıdaki görev kendi çalışma alanını açar; otomatik üst seviye temizliğe güvenmeden teardown'ın sildiğini ölçer. Zorla süreç öldürme/elektrik kesintisinde kullanıcı kodunun çalışacağı garantisi yoktur. Kaynak: [Bats setup/teardown](https://bats-core.readthedocs.io/en/stable/writing-tests.html#setup-and-teardown-pre-and-post-test-hooks).
:::

::: gorev Düşen testin çalışma alanını temizle
Betiğin temizlik.bats dosyasını yazsın. İki test olsun: ilki kendi alanında x dosyası üretip **bilerek false ile düşsün**; ikincisi kendi alanında x bulunmadığını doğrulayıp geçsin. setup her testte çalışma klasörünün içinde mktemp -d ile ayrı alan açsın ve tam yolunu alanlar.log'a bir satır eklesin. teardown yalnız o alanı silsin. dışarıdaki dokunma klasörünü koru.

Ana betik önce alanlar.log'u sıfırlasın, gerçek bats --tap temizlik.bats çalıştırsın ve TAP çıktısını tap.txt'ye alsın. Sonra üç satır yazsın: bats=<çıkış kodu>, alan=<logdaki yol sayısı>, kalan=<hâlâ var olan yol sayısı>. Doğru sonuç bats=1 / alan=2 / kalan=0; bilinçli düşüş beklenen test verisidir, ana betik 0 ile bitsin. Temizliği ana betikte yapma; testler Bats dosyanı ayrıca doğrudan çalıştırıp teardown'ı ölçecek.

```setup
from pathlib import Path
Path('dokunma').mkdir(exist_ok=True)
Path('dokunma/kanit.txt').write_text('korunacak',encoding='utf-8')
```

```starter
printf 'bats=1\nalan=2\nkalan=0\n'
```

```test
import pathlib,subprocess
root=pathlib.Path.cwd()
eq(out,'bats=1\nalan=2\nkalan=0\n','ana betiğin gerçek sonuç raporu')
def kontrol():
    lines=pathlib.Path('alanlar.log').read_text().splitlines()
    eq(len(lines),2,'iki setup çalıştı')
    eq(len(set(lines)),2,'her test ayrı alan açar')
    for line in lines:
        path=pathlib.Path(line)
        ok(path.is_absolute() and path.parent==root,'yalnız bu çalışma klasöründe alan')
        ok(not path.exists(),'başarılı ve başarısız testin alanı teardown ile silindi')
    eq(pathlib.Path('dokunma/kanit.txt').read_text(),'korunacak','başka alan silinmez')
kontrol()
pathlib.Path('alanlar.log').write_text('')
r=subprocess.run(['bats','--tap','temizlik.bats'],capture_output=True,text=True)
eq(r.returncode,1,'tek bilinçli düşüş')
plan=r.stdout.splitlines()
ok('1..2' in plan,'iki gerçek Bats testi')
ok(any(line.startswith('not ok 1 ') for line in plan),'ilk test gerçekten düşmeli')
ok(any(line.startswith('ok 2 ') for line in plan),'ikinci test gerçekten geçmeli')
kontrol()
```

```solution
cat > temizlik.bats <<'TEST'
setup() {
    ALAN=$(mktemp -d "$PWD/alan.XXXXXX")
    printf '%s\n' "$ALAN" >> "$PWD/alanlar.log"
}
teardown() {
    rm -rf -- "$ALAN"
}
@test "bilerek dusen" {
    printf veri > "$ALAN/x"
    false
}
@test "yalitilmis" {
    [ ! -e "$ALAN/x" ]
    printf veri > "$ALAN/y"
}
TEST
: > alanlar.log
bats --tap temizlik.bats > tap.txt
kod=$?
alan=0
kalan=0
while IFS= read -r yol; do
    alan=$((alan + 1))
    if [[ -e $yol ]]; then kalan=$((kalan + 1)); fi
done < alanlar.log
printf 'bats=%s\nalan=%s\nkalan=%s\n' "$kod" "$alan" "$kalan"
```
:::

::: anlat Git Bash'ten başlatmak ile Linux'ta çalıştırmak
Pafta'yı Git Bash'ten başlatabilirsin; backend: wsl olan bu ders yine Kali'nin gerçek Bash/Bats/ShellCheck araçlarında çalışır. Git Bash MSYS2 tabanlı bir Windows ortamıdır; WSL ise Linux ortamıdır. Git Bash'in /tmp ve /c gibi yollarını Linux yollarıyla aynı dosya sistemi sanma. MSYS2, bazı yerel Windows programlarına verilen Unix görünümlü argümanları Windows yoluna dönüştürür; cygpath -w dönüşümü açıkça gösterir. WSL'de /mnt/c Windows sürücüsüdür; bu dersin geçici çalışma alanı Linux /tmp altındadır.

| Ölçüm | Git Bash | Bu dersin Kali WSL ortamı |
|---|---|---|
| uname -s | MINGW/MSYS ailesi | Linux |
| Linux çekirdek kimliği /proc/sys/kernel/osrelease | Linux çekirdeği kanıtı olarak kullanılmaz | okunabilir Linux çekirdek sürümü |
| cygpath | MSYS/Windows yol dönüşümü | dersin araç sözleşmesi değil |
| journalctl, systemd journal | Git Bash'e ait Linux servis altyapısı varsayılmaz | BS31 gerçek journal araçlarıyla ayrı dosya okur |
| ShellCheck/Bats sürümü | PATH'teki kurulum ayrıca ölçülür | ders koşucusunun Linux PATH'i ölçülür |

Bir makinede Git Bash'te de bats bulunması onu WSL'ye dönüştürmez. ShellCheck sürümü/SC çıktıları değişebilir; BS30'un örnekleri kurulu sürümle ölçülmüştür. CRLF ile kaydedilmiş bir Bash dosyasının satır sonundaki CR komut/argümana karışabilir; depodaki betikleri UTF-8 ve LF olarak tut. Kaynak: [MSYS2 dosya sistemi yolları ve otomatik dönüşüm](https://www.msys2.org/docs/filesystem-paths/), [Git for Windows](https://gitforwindows.org/), [Bats belgeleri](https://bats-core.readthedocs.io/en/stable/writing-tests.html).
:::
