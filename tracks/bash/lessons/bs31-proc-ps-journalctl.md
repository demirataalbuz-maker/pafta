---
id: bs31
title: Süreçler ve Günlükler: /proc, ps, journalctl
summary: Gerçek Linux'ta /proc/<pid> (status, NUL ile ayrılmış cmdline ve environ, 15 karakterlik ad, exec -a ile sahte argv[0]); ps -o sütunları, --ppid, -C ve durum harfleri (S, T, Z), Bash'in arka plan çocuğunu kendisinin biçmesi; systemd-journal-remote ile kendi journal dosyanı üretmek (zorunlu alanlar, son boş satır, kaydı kaybedip yine 0 dönmek) ve journalctl --file ile -p, -t, --since (yerel saat; --utc yalnız çıktıyı değiştirir), -o short-iso ve json, -q.
kazanim: LPIC1 103.5
backend: wsl
timeout: 120
---

::: anlat /proc: çekirdeğin süreç tablosu, dosya gibi
Bu dersin bütün adımları **gerçek Linux'ta** (Kali, WSL) çalışır. Sistem dosyalarına dokunmayacaksın: inceleyeceğin süreçleri kendin başlatıp kapatacaksın, günlükleri de kendi dosyana yazacaksın.

Linux her süreci `/proc/<pid>/` altında bir klasör olarak gösterir. Bu dosyalar diskte yoktur; okuduğun anda çekirdek üretir:

```bash
ARKA=gizli sleep 300 &
p=$!
sleep 0.2
grep -E '^(Name|State|PPid|VmRSS):' /proc/$p/status
tr '\0' '|' < /proc/$p/cmdline; echo
tr '\0' '\n' < /proc/$p/environ | grep '^ARKA='
readlink /proc/$p/exe
kill $p
```

| Yol | İçerik |
|---|---|
| `status` | İnsanın okuyacağı alanlar, `Ad:<sekme>değer` biçiminde: `Name`, `State` (`S (sleeping)`), `PPid` (ebeveyn), `VmRSS` (bellek) |
| `cmdline` | Argümanlar, aralarında **NUL** (`\0`) baytı; zombide boştur |
| `environ` | Ortam değişkenleri, yine NUL ile ayrılmış; yalnız sürecin sahibi ve root okuyabilir |
| `exe`, `cwd` | Çalışan programa ve çalışma klasörüne sembolik bağ |
| `fd/` | Açık dosya tanımlayıcıları: `0 1 2` ve fazlası |

Ayırıcı neden NUL? Çünkü bir argüman boşluk içerebilir, hatta boş olabilir; NUL ise bir argümanın içinde bulunamaz. Bash'te NUL ile ayrılmış bir dosyayı diziye almak için `mapfile -d '' -t dizi < /proc/$p/cmdline` kullanılır: `"a b"` tek eleman kalır, boş argüman da boş bir eleman olarak gelir.

`/proc/self` o dosyayı okuyan sürecin kendisidir. Bash'te `$$` ana kabuğun PID'idir; alt kabukta bile değişmez. O an çalışan sürecin PID'i için `$BASHPID` kullanılır.

> [!TUZAK] Süreç adı iki yerde durur, ikisine de güvenme
> `Name` alanı (aynısı `/proc/<pid>/comm` dosyasında) en fazla **15 karakter** tutar: `uzun_bir_uyku_programi` adlı bir program `uzun_bir_uyku_p` görünür. `pgrep uzun_bir_uyku_programi` bu yüzden hiçbir şey bulamaz ve uyarı verir; `pgrep -f` adı komut satırında arar. `cmdline`'ın ilk elemanı (`argv[0]`) ise programı başlatanın seçtiği bir metindir: `exec -a` ile istenen her ad yazılabilir. Süreç adını taklit etmek bilinen bir gizlenme yoludur. Bir süreç listesinde gördüğün ad tek başına kanıt sayılmaz; çalışan programın gerçek yolunu `exe` bağı gösterir.
:::

::: anlat ps, durum harfleri ve geçici test süreci
`ps` aynı tabloyu sütunlar hâlinde okur. Betikte sütunları kendin seç ve başlığı `=` ile kaldır:

```bash
sleep 300 &
p=$!
sleep 0.2
ps -o pid,ppid,state,comm -p $p
ps -o state= -p $p
kill -STOP $p; sleep 0.1; ps -o state= -p $p
kill -CONT $p; sleep 0.1; ps -o state= -p $p
kill $p
```

| Seçenek | Ne yapar |
|---|---|
| `-o pid,ppid,state,comm` | Gösterilecek sütunlar |
| `-o pid=,comm=` | `=` ile başlık satırı kalkar; betikte bunu kullan |
| `-p PID` | Yalnız o süreç; yoksa çıktı boş, çıkış kodu **1** |
| `--ppid PID` | O sürecin çocukları, PID sırasıyla |
| `-C ad` | Adı (`comm`) bu olan süreçler |
| `-e` | Bütün süreçler |

Durum harfleri: `R` çalışıyor ya da sırada, `S` bir şey bekliyor (uyuyor), `D` kesilemeyen bekleme (çoğunlukla disk), `T` durdurulmuş (`SIGSTOP`), `Z` zombi. `stat` sütunu bu harfe bayraklar ekler: `Ss` oturum lideri, `S+` ön planda, `Sl` çok iş parçacıklı demektir. Yalnız harfi istiyorsan `state` sütununu kullan.

**Zombi**, bitmiş ama ebeveyni çıkış kodunu henüz `wait` ile almamış bir süreçtir. Tabloda yalnız o kod için bir satır kalır:

```bash
bash -c 'sleep 0.1 & exec sleep 3' &
e=$!
sleep 0.5
ps --ppid $e -o pid=,state=,comm=
kill $e
```

İçerideki kabuk `sleep 0.1`'i başlattı, sonra `exec` ile kendini `sleep 3`'e çevirdi. `sleep` hiç `wait` çağırmaz, bu yüzden biten çocuk `Z` olarak kalır. `ps` onu `sleep <defunct>` diye gösterir; `cmdline` dosyası boştur.

Kendi test sürecini başlatırken kapatmayı garantiye al: `sleep 300 & p=$!` dedikten hemen sonra `trap 'kill "$p" 2> /dev/null' EXIT` yaz. Betik nasıl biterse bitsin süreç arkada kalmaz.

Bir sürecin `ps`'ten kaybolması ile sonucunun kaybolması aynı şey değildir:

```bash
sleep 30 & p=$!
kill $p
sleep 0.5
ps -o state= -p $p; echo "ps: $?"
wait $p; echo "wait: $?"
```

> [!TUZAK] Bash kendi arka plan çocuğunu kendisi biçer
> Bu derste ölçüldü: yukarıdaki betik `ps: 1` ve `wait: 143` yazar. Öldürülen `sleep` zombi olarak kalmadı. Bash, ön plandaki `sleep 0.5`'i beklerken biten bütün çocuklarını toplar ve çıkış kodlarını saklar. Bu yüzden `ps` süreci bulamaz, `wait` ise saklanan kodu döndürür: 128 + 15 (`SIGTERM`). `ps`'te görmemen, sonucun kaybolduğu anlamına gelmez.
:::

::: tahmin
Ne yazar?

```bash
(exec -a takma_ad sleep 300) & p=$!
sleep 0.3
awk '/^Name:/ {print $2}' /proc/$p/status
tr '\0' '|' < /proc/$p/cmdline; echo
kill $p
```

???

`sleep` ve `takma_ad|300|`.

`exec -a takma_ad`, programa `argv[0]` olarak `takma_ad` metnini verir; `cmdline` bunu aynen gösterir. Son `|` sondaki NUL'dur. `Name` ise çekirdeğin çalıştırdığı dosyanın adından gelir; `argv[0]` onu değiştirmez. `ps -o comm` `sleep`, `ps -o args` `takma_ad 300` gösterir. İki ad farklıysa birinin söylediği şeyi doğrulaman gerekir.
:::

::: gorev /proc'tan süreç kimliği
Girdinin ilk satırı bir PID'dir. O süreç hakkında yalnız `/proc`'u okuyarak (`ps` ve `pgrep` kullanmadan) şu dört satırı yazdır:

```text
ad=<status'taki Name>
durum=<State'in harfi: S, T, Z...>
ebeveyn=<PPid>
arguman=<cmdline'daki argümanlar, aralarında |>
```

- PID bir sayı değilse ya da girdi boşsa `HATA` yazdır.
- Böyle bir süreç yoksa `yok` yazdır.
- Argümanlardaki boşluklar, satır sonları ve boş argümanlar korunmalı: `python3 -c "..." "a b" ""` için satır `arguman=python3|-c|...|a b|` olur. Satır sonu içeren bir argüman çıktıda da satırı böler. Zombinin argümanı yoktur, satır `arguman=` olarak kalır.

Testler kendi süreçlerini başlatır: 15 karakterden uzun adlı bir program, adında boşluk olan bir program, `argv[0]`'ı değiştirilmiş bir `sleep`, durdurulmuş ve zombi süreçler.

```stdin
1
```

```starter
read -r pid
grep Name /proc/$pid/status
```

```test
import os, re, shutil, signal, subprocess, time
from subprocess import DEVNULL

def alanlar(pid):
    d = {}
    with open(f"/proc/{pid}/status", encoding="utf-8") as f:
        for satir in f:
            k, _, v = satir.rstrip("\n").partition(":\t")
            d[k] = v
    return d

def bekle(pid, harf):
    for _ in range(100):
        if alanlar(pid)["State"][0] == harf:
            return
        time.sleep(0.05)

def baslat(arg, harf="S", **kw):
    p = subprocess.Popen(arg, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, **kw)
    bekle(p.pid, harf)
    return p

def bir_numara():
    d = alanlar(1)
    with open("/proc/1/cmdline", "rb") as f:
        arg = f.read().decode().split("\0")[:-1]
    return f"ad={d['Name']}\ndurum={d['State'][0]}\nebeveyn={d['PPid']}\narguman={'|'.join(arg)}\n"

ben = os.getpid()
eq(out, bir_numara(), "stdin örneği: PID 1")
py = baslat(["python3", "-c", "import time; time.sleep(60)", "a b", "satir\nsonu", ""])
eq(run(stdin=f"{py.pid}\n"),
   f"ad=python3\ndurum=S\nebeveyn={ben}\narguman=python3|-c|import time; time.sleep(60)|a b|satir\nsonu|\n",
   "argümandaki boşluk ve satır sonu, sondaki boş argüman korunmalı: cmdline NUL ile ayrılır")
shutil.copy("/bin/sleep", "uzun_bir_uyku_programi")
uzun = baslat(["./uzun_bir_uyku_programi", "60"])
eq(run(stdin=f"{uzun.pid}\n"),
   f"ad=uzun_bir_uyku_p\ndurum=S\nebeveyn={ben}\narguman=./uzun_bir_uyku_programi|60\n",
   "Name 15 karakterde kesilir, cmdline kesilmez")
shutil.copy("/bin/sleep", "iki kelime")
iki = baslat(["./iki kelime", "60"])
eq(run(stdin=f"{iki.pid}\n"), f"ad=iki kelime\ndurum=S\nebeveyn={ben}\narguman=./iki kelime|60\n",
   "adında boşluk olan süreç: Name'i sekmeden sonra bütün olarak al")
takma = baslat(["takma_ad", "60"], executable=shutil.which("sleep"))
eq(run(stdin=f"{takma.pid}\n"), f"ad=sleep\ndurum=S\nebeveyn={ben}\narguman=takma_ad|60\n",
   "argv[0] değiştirilmiş süreç: Name gerçek programı söyler")
dur = baslat(["sleep", "60"])
os.kill(dur.pid, signal.SIGSTOP)
bekle(dur.pid, "T")
eq(run(stdin=f"{dur.pid}\n"), f"ad=sleep\ndurum=T\nebeveyn={ben}\narguman=sleep|60\n", "durdurulmuş süreç")
zombi = baslat(["sleep", "0"], harf="Z")
eq(run(stdin=f"{zombi.pid}\n"), f"ad=sleep\ndurum=Z\nebeveyn={ben}\narguman=\n", "zombi: cmdline boş")
biten = subprocess.Popen(["true"])
biten.wait()
eq(run(stdin=f"{biten.pid}\n"), "yok\n", "bitmiş ve biçilmiş süreç")
eq(run(stdin="4194305\n"), "yok\n", "pid_max'tan büyük PID")
eq(run(stdin="abc\n"), "HATA\n", "sayı olmayan girdi")
eq(run(stdin="-1\n"), "HATA\n", "eksi sayı")
eq(run(stdin="12 34\n"), "HATA\n", "iki sayı")
eq(run(stdin=""), "HATA\n", "boş girdi")
ok(not re.search(r"\b(ps|pgrep)\b", src), "yalnız /proc'u oku; ps ve pgrep kullanma")
for p in (py, uzun, iki, takma, dur):
    p.kill()
zombi.wait()
```

```solution
read -r pid || true
if [[ ! $pid =~ ^[0-9]+$ ]]; then
    echo HATA
    exit 0
fi
if [[ ! -r /proc/$pid/status ]]; then
    echo yok
    exit 0
fi
ad="" durum="" ebeveyn=""
while IFS=$'\t' read -r anahtar deger; do
    case $anahtar in
        Name:) ad=$deger ;;
        State:) durum=${deger%% *} ;;
        PPid:) ebeveyn=$deger ;;
    esac
done < "/proc/$pid/status"
mapfile -d '' -t argumanlar < "/proc/$pid/cmdline"
echo "ad=$ad"
echo "durum=$durum"
echo "ebeveyn=$ebeveyn"
(IFS='|'; echo "arguman=${argumanlar[*]}")
```

```hint
`status`'ta anahtar ile değer arasında **sekme** var. `while IFS=$'\t' read -r anahtar deger` ile oku: anahtar `Name:` olur, değer de boşluk içerse bütün kalır. `awk '{print $2}'` `iki kelime`nin yalnız ilk kelimesini alır.
```

```hint
`tr '\0' '|'` sona fazladan bir `|` koyar ve boş argümanı sondaki NUL'dan ayıramaz. `mapfile -d '' -t dizi` her NUL'u bir eleman sonu sayar; sonra bir alt kabukta `IFS='|'` ile `"${dizi[*]}"` elemanları `|` ile birleştirir.
```
:::

::: gorev ps ile süreç ağacı
Servisler PID'lerini çoğu zaman bir **PID dosyasına** yazar (`/run/nginx.pid` gibi): içinde tek satır, bir PID. Betiğin ilk argümanı böyle bir dosyanın yoludur. O PID'deki sürecin ve **bütün** alt süreçlerinin (çocuk, torun, ...) ağacını yazdır:

```text
4100 S pafta_kok
  4101 S sleep
  4102 T sleep
  4103 S sleep
    4107 Z sleep <defunct>
```

- Her satır `<PID> <durum harfi> <ad>`. Ad `ps`'in `comm` sütunudur; zombilerde `ps`'in eklediği ` <defunct>` olduğu gibi kalır.
- Her derinlik için başa iki boşluk eklenir. Kardeşler PID sırasıyla yazılır.
- Argüman yoksa, dosya yoksa ya da içeriği bir sayı değilse `HATA` yazdır.
- Dosyadaki PID'de süreç yoksa `bayat: <pid>` yazdır: süreç ölmüş, dosyası kalmış. Ağaç yazmaya kalkma.
- Bu görevde `ps` kullan.

Çalışma klasöründe `pafta_kok` adlı bir süreç çalışıyor ve PID'i `kok.pid`'de; ağacında bir durdurulmuş ve bir zombi süreç var. Testler kendi PID dosyalarını yazar: daha derin bir zincir, çocuksuz bir süreç, bitmiş bir süreç.

```meta
argv: kok.pid
```

```setup
import os, shutil, signal, subprocess, time

def tablo():
    t = {}
    for ad in os.listdir("/proc"):
        if ad.isdigit():
            try:
                with open(f"/proc/{ad}/stat", encoding="utf-8") as f:
                    veri = f.read()
            except OSError:
                continue
            bas, _, son = veri.rpartition(") ")
            alan = son.split()
            t[int(ad)] = (bas.split(" (", 1)[1], alan[0], int(alan[1]))
    return t

shutil.copy("/bin/bash", "pafta_kok")
kok = subprocess.Popen(["./pafta_kok", "-c", 'sleep 60 & sleep 60 & bash -c "sleep 0 & exec sleep 60" & wait'],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       start_new_session=True)
cocuk = []
for _ in range(100):
    t = tablo()
    cocuk = sorted(p for p, v in t.items() if v[2] == kok.pid)
    zombi = [p for p, v in t.items() if v[2] in cocuk and v[1] == "Z"]
    if len(cocuk) == 3 and all(t[c][0] == "sleep" for c in cocuk) and zombi:
        break
    time.sleep(0.05)
os.kill(cocuk[1], signal.SIGSTOP)
for _ in range(100):
    if tablo().get(cocuk[1], ("", ""))[1] == "T":
        break
    time.sleep(0.05)
with open("kok.pid", "w", encoding="utf-8") as f:
    f.write(f"{kok.pid}\n")
```

```starter
pid=$(cat "$1")
ps --ppid "$pid" -o pid=,state=,comm=
```

```test
import os, re, shutil, subprocess, time
from subprocess import DEVNULL

def tablo():
    t = {}
    for ad in os.listdir("/proc"):
        if ad.isdigit():
            try:
                with open(f"/proc/{ad}/stat", encoding="utf-8") as f:
                    veri = f.read()
            except OSError:
                continue
            bas, _, son = veri.rpartition(") ")
            alan = son.split()
            t[int(ad)] = (bas.split(" (", 1)[1], alan[0], int(alan[1]))
    return t

def agac(kok):
    t = tablo()
    satir = []
    def gez(pid, derin):
        ad, durum, _ = t[pid]
        satir.append("  " * derin + f"{pid} {durum} {ad}" + (" <defunct>" if durum == "Z" else ""))
        for c in sorted(p for p, v in t.items() if v[2] == pid):
            gez(c, derin + 1)
    gez(kok, 0)
    return "\n".join(satir) + "\n"

def pid_yaz(dosya, pid):
    with open(dosya, "w", encoding="utf-8") as f:
        f.write(f"{pid}\n")

def bekle(kosul):
    for _ in range(100):
        if kosul():
            return
        time.sleep(0.05)

def baslat(ad, kaynak, *arg):
    if not os.path.exists(ad):
        shutil.copy(kaynak, ad)
    return subprocess.Popen([f"./{ad}", *arg], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

with open("kok.pid", encoding="utf-8") as f:
    kok = int(f.read())
eq(out, agac(kok), "kurulu ağaç: oturum lideri kök, durdurulmuş (T) ve zombi (Z) torun")
with open("zincir.sh", "w", encoding="utf-8") as f:
    f.write('if (( $1 > 0 )); then bash zincir.sh $(( $1 - 1 )) & wait; else exec sleep 60; fi\n')
derin = baslat("pafta_derin", "/bin/bash", "zincir.sh", "3")

def derin_hazir():
    a = agac(derin.pid)
    return a.count("\n") == 4 and a.endswith(" S sleep\n")

bekle(derin_hazir)
pid_yaz("derin.pid", derin.pid)
eq(run(argv=["derin.pid"]), agac(derin.pid), "üç kuşak derinlikte zincir: girinti her kuşakta iki boşluk")
yalniz = baslat("pafta_yalniz", "/bin/sleep", "60")
bekle(lambda: tablo()[yalniz.pid][1] == "S")
pid_yaz("yalniz.pid", yalniz.pid)
eq(run(argv=["yalniz.pid"]), f"{yalniz.pid} S pafta_yalniz\n", "çocuğu olmayan süreç: tek satır")
biten = subprocess.Popen(["true"])
biten.wait()
pid_yaz("bayat.pid", biten.pid)
eq(run(argv=["bayat.pid"]), f"bayat: {biten.pid}\n", "süreci bitmiş PID dosyası")
with open("bozuk.pid", "w", encoding="utf-8") as f:
    f.write("12abc\n")
eq(run(argv=["bozuk.pid"]), "HATA\n", "içeriği sayı olmayan PID dosyası")
open("bos.pid", "w").close()
eq(run(argv=["bos.pid"]), "HATA\n", "boş PID dosyası")
eq(run(argv=["yok.pid"]), "HATA\n", "olmayan dosya")
eq(run(argv=[]), "HATA\n", "argüman yok")
ok(re.search(r"\bps\b", src), "bu görevde ps kullan")
for p in (derin, yalniz):
    p.kill()
```

```solution
dosya=${1:-}
pid=""
if [[ -f $dosya ]]; then
    read -r pid < "$dosya" || true
fi
if [[ ! $pid =~ ^[0-9]+$ ]]; then
    echo HATA
    exit 0
fi
if ! ps -p "$pid" > /dev/null; then
    echo "bayat: $pid"
    exit 0
fi

gez() {
    local pid=$1 girinti=$2 p durum isim cocuk
    read -r p durum isim < <(ps -o pid=,state=,comm= -p "$pid")
    echo "$girinti$p $durum $isim"
    for cocuk in $(ps --ppid "$pid" -o pid=); do
        gez "$cocuk" "$girinti  "
    done
}
gez "$pid" ""
```

```hint
`stat` sütunu kökte `Ss` verir (oturum lideri); tek harf için `state` kullan. `-o pid=,state=,comm=` ile başlık da gelmez.
```

```hint
Ağacı bir fonksiyonla gez: süreci yazdır, sonra `ps --ppid "$pid" -o pid=` ile çocuklarını bul ve her biri için fonksiyonu bir girinti fazlasıyla yeniden çağır. Fonksiyondaki değişkenleri `local` yap; yoksa iç çağrı dıştakinin `girinti`sini ezer ve sonraki kardeş yanlış girintiyle yazılır.
```
:::

::: anlat Kendi journal dosyan ve journalctl
systemd'nin günlüğü (journal) düz metin değildir. İkili, dizinli bir dosyadır ve her kayıt `ALAN=değer` çiftlerinden oluşur. `journalctl` varsayılan olarak sistemin günlüğünü okur. Bu derste ona hiç dokunmayacaksın: kendi dosyanı üretip `journalctl --file=` ile yalnız onu okuyacaksın.

Dosyayı **dışa aktarma biçiminden** (export format) `systemd-journal-remote` üretir. Bu araç aslında ağdan günlük toplayan bir sunucudur. Burada yalnız dosyadan okuyup dosyaya yazan kipi kullanılıyor; servis kapalı kalır.

```bash
cat > kayit.export <<'KAYIT'
__REALTIME_TIMESTAMP=1767258000000000
_BOOT_ID=0123456789abcdef0123456789abcdef
PRIORITY=6
SYSLOG_IDENTIFIER=yedekle
_PID=4242
MESSAGE=yedek basladi

__REALTIME_TIMESTAMP=1767258060000000
_BOOT_ID=0123456789abcdef0123456789abcdef
PRIORITY=3
SYSLOG_IDENTIFIER=yedekle
_PID=4242
MESSAGE=disk dolu

KAYIT
/usr/lib/systemd/systemd-journal-remote -o kendi.journal kayit.export
journalctl --file=kendi.journal --utc -o short-iso
```

Her satır `ALAN=değer` biçimindedir: değer ilk `=`'den sonraki her şeydir, içinde `=` geçebilir. Alan adları büyük harf, rakam ve `_`'dir; `mesaj=` gibi küçük harfli bir alan **sessizce düşer**. Kayıtlar **boş bir satırla** biter. `__REALTIME_TIMESTAMP` 1970'ten beri geçen **mikrosaniyedir** (saniye × 1 000 000). `_BOOT_ID` 32 onaltılık karakterdir. Bu ikisi zorunludur.

> [!TUZAK] Kaydı kaybedip yine 0 ile çıkmak
> Bu derste ölçüldü. Aşağıdaki durumların hepsinde `systemd-journal-remote` **0** ile çıkar:
> - Son kaydın ardından boş satır yoksa: `Premature EOF. 114 bytes lost.`, sonuç 0 kayıt.
> - Zorunlu alanlardan biri eksikse: `Entry is invalid, ignoring.`, kayıt yazılmaz.
> - Dosya zaten varsa üstüne yazmaz, **ekler**. Aynı betiği iki kez çalıştırırsan kayıtlar ikiye katlanır.
>
> Çıktı adının `.journal` ile bitmesi gerekir; bitmezse çıkış 1 olur. Yazdıktan sonra kayıtları `journalctl --file` ile **say**: çıkış kodu, kaydın yazıldığını kanıtlamaz.

| Seçenek | Ne yapar |
|---|---|
| `--file=F` | Yalnız bu dosyayı okur; sistem günlüğüne bakmaz |
| `-p warning` | Bu öncelik ve **daha ağırları**: `emerg` 0, `alert` 1, `crit` 2, `err` 3, `warning` 4, `notice` 5, `info` 6, `debug` 7. `-p 2..4` bir aralık verir. Yalnız bu adlar ve 0–7 geçerlidir: `error`, `warn`, `ERR` ve `8` reddedilir, çıkış 1 olur |
| `-t yedekle` | `SYSLOG_IDENTIFIER` eşleşmesi. `ALAN=değer` herhangi bir alanla eşleşir; aynı alan iki kez yazılırsa "ya o ya bu" demektir |
| `--since`, `--until` | Zaman aralığı, iki uç da dahil. Zaman **yerel saatle** yorumlanır; UTC için sonuna ` UTC` ekle |
| `-o cat`, `-o short-iso`, `-o json` | Yalnız mesaj; ISO zamanla kısa satır; her kayıt bir JSON satırı. JSON'da değerler hep metindir: `"PRIORITY":"3"` |
| `--utc` | Çıktıdaki saatleri UTC yazar |
| `-q` | Eşleşme yoksa `-- No entries --` satırını basmaz |
| `-n 5`, `-r` | Son 5 kaydı gösterir; sırayı ters çevirir |
| `-g desen` | `MESSAGE`'da düzenli ifade arar. Desende büyük harf varsa aramada büyük/küçük harf ayrımı yapılır |
| `-F ALAN` | Alanın aldığı farklı değerleri listeler |

> [!TUZAK] Önceliği olmayan kayıt hiçbir eşikte görünmez
> `PRIORITY` alanı olmayan bir kayıt, `-p` verildiğinde hiç listelenmez; `-p debug` bile onu göstermez. Kaydın kendisi dosyadadır: `-p` vermeden görünür.
:::

::: tahmin
Ne yazar? (`t.journal`'daki dört kayıt UTC ile 09:00, 09:01, 09:02 ve 09:03'te.)

```bash
for dk in 0 1 2 3; do
    printf '__REALTIME_TIMESTAMP=%s000000\n_BOOT_ID=0123456789abcdef0123456789abcdef\nSYSLOG_IDENTIFIER=deneme\nMESSAGE=dk%s\n\n' \
        $((1767258000 + dk * 60)) "$dk"
done > t.export
/usr/lib/systemd/systemd-journal-remote -o t.journal t.export 2> /dev/null
TZ=Europe/Istanbul journalctl --file=t.journal --utc -o short-iso -q --since "2026-01-01 09:02:00"
```

???

Dört kaydın **hepsi**:

```text
2026-01-01T09:00:00+00:00 deneme: dk0
2026-01-01T09:01:00+00:00 deneme: dk1
2026-01-01T09:02:00+00:00 deneme: dk2
2026-01-01T09:03:00+00:00 deneme: dk3
```

`--utc` yalnız **çıktıdaki** saatleri UTC yazar; `--since`'in nasıl okunacağını değiştirmez. `"2026-01-01 09:02:00"` İstanbul saatiyle okunur: UTC ile 06:02. Bütün kayıtlar bundan sonradır. Yalnız son iki kaydı istiyorsan `--since "2026-01-01 09:02:00 UTC"` yazmalısın.
:::

::: gorev Günlükten kanıt
Çalışma klasöründe `uygulama.journal` var: 2026-01-01 sabahı (UTC 09:00–09:09) `yedekle`, `web` ve `cron` adlı programların on kaydı. Girdi:

1. satır: öncelik (`emerg` ... `debug` ya da 0–7)
2. satır: başlangıç zamanı, **UTC** olarak, `YYYY-AA-GG SS:DD:ss` biçiminde
3. satır (isteğe bağlı): program kimliği (`SYSLOG_IDENTIFIER`)

O öncelikte ya da daha ağır olan ve başlangıç anından (dahil) sonraki kayıtları `journalctl`'in `short-iso` biçiminde, saatleri UTC olarak yazdır; en sona `toplam <kayıt sayısı>` ekle. Hiç kayıt yoksa yalnız `toplam 0` yazdır.

Öncelik ya da zaman geçersizse, eksikse veya girdi boşsa tek satır `HATA` yazdır.

```stdin
warning
2026-01-01 09:05:00
```

```setup
import subprocess
KAYITLAR = [
    (0, "yedekle", 4242, 6, "yedek basladi"),
    (90, "web", 5000, 4, "yavas istek /api/biletler 2300 ms"),
    (120, "yedekle", 4242, 3, "disk dolu: /var/yedek"),
    (190, "cron", 311, None, "gorev calisti"),
    (240, "web", 5000, 6, "GET /saglik 200"),
    (300, "web", 5000, 2, "veritabani baglantisi koptu"),
    (405, "yedekle", 4242, 5, "yedek bitti: 3 dosya"),
    (420, "web", 5001, 3, "istek zaman asimi /api/rapor"),
    (500, "cron", 311, 7, "ayrinti: kilit alindi"),
    (540, "yedekle", 4243, 4, "eski yedek silinemedi"),
]
with open("uygulama.export", "w", encoding="utf-8", newline="\n") as f:
    for sn, kimlik, pid, oncelik, mesaj in KAYITLAR:
        f.write(f"__REALTIME_TIMESTAMP={(1767258000 + sn) * 1000000}\n")
        f.write("_BOOT_ID=0123456789abcdef0123456789abcdef\n")
        if oncelik is not None:
            f.write(f"PRIORITY={oncelik}\n")
        f.write(f"SYSLOG_IDENTIFIER={kimlik}\n_PID={pid}\nMESSAGE={mesaj}\n\n")
subprocess.run(["/usr/lib/systemd/systemd-journal-remote", "-o", "uygulama.journal", "uygulama.export"],
               stderr=subprocess.DEVNULL, check=True)
```

```starter
read -r oncelik
read -r baslangic
journalctl --file=uygulama.journal -p "$oncelik" --since "$baslangic"
```

```test
eq(out, "2026-01-01T09:05:00+00:00 web[5000]: veritabani baglantisi koptu\n"
        "2026-01-01T09:07:00+00:00 web[5001]: istek zaman asimi /api/rapor\n"
        "2026-01-01T09:09:00+00:00 yedekle[4243]: eski yedek silinemedi\n"
        "toplam 3\n", "warning ve daha ağırları, 09:05 UTC'den sonra (yerel saatle okursan 3 saat önceden başlar)")
eq(run(stdin="err\n2026-01-01 09:00:00\nweb\n"),
   "2026-01-01T09:05:00+00:00 web[5000]: veritabani baglantisi koptu\n"
   "2026-01-01T09:07:00+00:00 web[5001]: istek zaman asimi /api/rapor\n"
   "toplam 2\n", "üçüncü satır: yalnız web")
eq(run(stdin="3\n2026-01-01 09:00:00\n"),
   "2026-01-01T09:02:00+00:00 yedekle[4242]: disk dolu: /var/yedek\n"
   "2026-01-01T09:05:00+00:00 web[5000]: veritabani baglantisi koptu\n"
   "2026-01-01T09:07:00+00:00 web[5001]: istek zaman asimi /api/rapor\n"
   "toplam 3\n", "sayıyla öncelik: 3 = err")
eq(run(stdin="debug\n2026-01-01 09:06:45\n"),
   "2026-01-01T09:06:45+00:00 yedekle[4242]: yedek bitti: 3 dosya\n"
   "2026-01-01T09:07:00+00:00 web[5001]: istek zaman asimi /api/rapor\n"
   "2026-01-01T09:08:20+00:00 cron[311]: ayrinti: kilit alindi\n"
   "2026-01-01T09:09:00+00:00 yedekle[4243]: eski yedek silinemedi\n"
   "toplam 4\n", "başlangıç anındaki kayıt dahil")
eq(run(stdin="debug\n2026-01-01 09:00:00\ncron\n"),
   "2026-01-01T09:08:20+00:00 cron[311]: ayrinti: kilit alindi\n"
   "toplam 1\n", "PRIORITY alanı olmayan cron kaydı -p ile görünmez")
eq(run(stdin="emerg\n2026-01-01 09:00:00\n"), "toplam 0\n", "eşleşme yok: -- No entries -- satırı basılmamalı")
eq(run(stdin="info\n2026-01-01 09:00:00\nyok\n"), "toplam 0\n", "olmayan kimlik")
eq(run(stdin="acil\n2026-01-01 09:00:00\n"), "HATA\n", "geçersiz öncelik adı")
eq(run(stdin="error\n2026-01-01 09:00:00\n"), "HATA\n", "error değil err")
eq(run(stdin="8\n2026-01-01 09:00:00\n"), "HATA\n", "öncelik 0–7")
eq(run(stdin="warning\ndun\n"), "HATA\n", "geçersiz zaman")
eq(run(stdin="warning\n"), "HATA\n", "zaman satırı yok")
eq(run(stdin=""), "HATA\n", "boş girdi")
ok("--file" in src, "yalnız kendi dosyanı oku: journalctl --file")
```

```solution
read -r oncelik || true
read -r baslangic || true
read -r kimlik || true
secenek=(--file=uygulama.journal --no-pager -q -o short-iso --utc -p "$oncelik" --since "$baslangic UTC")
if [[ -n $kimlik ]]; then
    secenek+=(-t "$kimlik")
fi
if ! journalctl "${secenek[@]}" > sonuc.txt 2> /dev/null; then
    echo HATA
    exit 0
fi
cat sonuc.txt
echo "toplam $(wc -l < sonuc.txt)"
```

```hint
Geçersiz öncelikte ve okunamayan zamanda `journalctl` 1 ile çıkar; denetimi ona bırakabilirsin. Çıktıyı bir dosyaya al, çıkış koduna bak, sonra satırları say.
```

```hint
`--utc` yalnız çıktıdaki saatleri değiştirir. Girdideki zamanın UTC olduğunu `--since "$baslangic UTC"` ile söyle. Eşleşme yokken basılan satırı `-q` kaldırır.
```
:::

::: gorev Kendi günlüğünü üret
Girdide bir uygulamanın düz metin günlüğü var. Her satır şu biçimde:

```text
2026-01-01T09:02:00Z err yedekle: disk dolu: /var/yedek
```

Sırasıyla UTC zaman (`YYYY-AA-GGTSS:DD:ssZ`), öncelik adı (`emerg` ... `debug`), sonu `:` ile biten program kimliği ve mesaj (satırın geri kalanı). Bunlardan `kendi.journal` dosyasını üret:

- Her geçerli satır bir kayıt olur: `__REALTIME_TIMESTAMP` (mikrosaniye), `_BOOT_ID` (32 onaltılık karakter, istediğin sabit), `PRIORITY` (0–7), `SYSLOG_IDENTIFIER` (`:` olmadan) ve `MESSAGE`.
- Zamanı biçime uymayan ya da gerçek bir tarih olmayan, önceliği bilinmeyen, kimliği `:` ile bitmeyen ya da mesajı boş olan satırlar **atlanır**. Boş satırlar sayılmaz.
- Betik her çalıştığında `kendi.journal` baştan üretilmeli.

Sonra `journalctl --file=kendi.journal`'daki kayıtları `short-iso` biçiminde, saatleri UTC olarak yazdır; en sona `yazilan <dosyadaki kayıt sayısı>, atlanan <atlanan satır sayısı>` ekle. Yazılanı **dosyadan say**, kendi sayacına güvenme.

```stdin
2026-01-01T09:00:00Z info yedekle: yedek basladi
2026-01-01T09:02:00Z err yedekle: disk dolu: /var/yedek

2026-01-01T09:03:00Z uyari web: yavas istek
bozuk satir
2026-01-01T09:04:00Z warning web: oturum = 42, disk %95
tomorrow info web: yarin
2026-02-30T10:00:00Z info web: olmayan gun
2026-01-01T09:05:00Z notice cron:
2026-01-01T09:06:00Z debug cron gorev calisti
2026-01-01T09:07:00Z crit web: veritabani koptu
```

```starter
while read -r zaman oncelik kimlik mesaj; do
    printf '__REALTIME_TIMESTAMP=%s\nMESSAGE=%s\n' "$zaman" "$mesaj"
done > girdi.export
/usr/lib/systemd/systemd-journal-remote -o kendi.journal girdi.export
journalctl --file=kendi.journal -o short-iso --utc
```

```test
import json, subprocess

def kayitlar():
    r = subprocess.run(["journalctl", "--file=kendi.journal", "-o", "json", "-q", "--no-pager"],
                       capture_output=True, text=True)
    return [(k["__REALTIME_TIMESTAMP"], k.get("PRIORITY"), k.get("SYSLOG_IDENTIFIER"), k.get("MESSAGE"))
            for k in map(json.loads, r.stdout.splitlines())]

GIRDI = ("2026-01-01T09:00:00Z info yedekle: yedek basladi\n"
         "2026-01-01T09:02:00Z err yedekle: disk dolu: /var/yedek\n"
         "\n"
         "2026-01-01T09:03:00Z uyari web: yavas istek\n"
         "bozuk satir\n"
         "2026-01-01T09:04:00Z warning web: oturum = 42, disk %95\n"
         "tomorrow info web: yarin\n"
         "2026-02-30T10:00:00Z info web: olmayan gun\n"
         "2026-01-01T09:05:00Z notice cron:\n"
         "2026-01-01T09:06:00Z debug cron gorev calisti\n"
         "2026-01-01T09:07:00Z crit web: veritabani koptu\n")
CIKTI = ("2026-01-01T09:00:00+00:00 yedekle: yedek basladi\n"
         "2026-01-01T09:02:00+00:00 yedekle: disk dolu: /var/yedek\n"
         "2026-01-01T09:04:00+00:00 web: oturum = 42, disk %95\n"
         "2026-01-01T09:07:00+00:00 web: veritabani koptu\n"
         "yazilan 4, atlanan 6\n")
eq(out, CIKTI, "dört geçerli satır; uyari, bozuk, tomorrow, 30 Şubat, boş mesaj ve :'sız kimlik atlanır")
eq(kayitlar(), [("1767258000000000", "6", "yedekle", "yedek basladi"),
                ("1767258120000000", "3", "yedekle", "disk dolu: /var/yedek"),
                ("1767258240000000", "4", "web", "oturum = 42, disk %95"),
                ("1767258420000000", "2", "web", "veritabani koptu")],
   "dosyadaki alanlar: mikrosaniye zaman, öncelik sayısı, kimlik, mesaj (son kayıt da dahil)")
eq(run(stdin=GIRDI), CIKTI, "ikinci çalıştırmada çıktı aynı kalmalı")
eq(len(kayitlar()), 4, "iki kez çalışınca kayıtlar ikiye katlanmamalı: dosyayı her seferinde baştan üret")
eq(run(stdin="2026-01-01T10:00:00Z notice son: satir sonu yok"),
   "2026-01-01T10:00:00+00:00 son: satir sonu yok\nyazilan 1, atlanan 0\n", "son satırda \\n yok")
eq(kayitlar(), [("1767261600000000", "5", "son", "satir sonu yok")], "tek kayıt, eski kayıtlar silinmiş")
eq(run(stdin="bozuk\n"), "yazilan 0, atlanan 1\n", "hiç geçerli satır yok")
eq(kayitlar(), [], "geçerli satır yoksa dosyada kayıt olmamalı")
eq(run(stdin=""), "yazilan 0, atlanan 0\n", "boş girdi")
eq(run(stdin="2026-01-01T11:00:00Z alert a: x\n2026-01-01T11:01:00Z debug b: y\n2026-01-01T11:02:00Z emerg c: z\n"),
   "2026-01-01T11:00:00+00:00 a: x\n2026-01-01T11:01:00+00:00 b: y\n2026-01-01T11:02:00+00:00 c: z\nyazilan 3, atlanan 0\n",
   "alert, debug ve emerg geçerli öncelikler")
eq([k[1] for k in kayitlar()], ["1", "7", "0"], "öncelik sayıları: alert 1, debug 7, emerg 0")
```

```solution
desen='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'
rm -f kendi.journal
: > girdi.export
atlanan=0
while IFS= read -r satir || [[ -n $satir ]]; do
    [[ -z $satir ]] && continue
    read -r zaman oncelik kimlik mesaj <<< "$satir"
    case $oncelik in
        emerg) p=0 ;; alert) p=1 ;; crit) p=2 ;; err) p=3 ;;
        warning) p=4 ;; notice) p=5 ;; info) p=6 ;; debug) p=7 ;;
        *) p="" ;;
    esac
    if [[ ! $zaman =~ $desen || -z $p || $kimlik != ?*: || -z $mesaj ]] \
        || ! saniye=$(date -u -d "$zaman" +%s 2> /dev/null); then
        atlanan=$((atlanan + 1))
        continue
    fi
    printf '__REALTIME_TIMESTAMP=%s000000\n_BOOT_ID=%s\nPRIORITY=%s\nSYSLOG_IDENTIFIER=%s\nMESSAGE=%s\n\n' \
        "$saniye" 0123456789abcdef0123456789abcdef "$p" "${kimlik%:}" "$mesaj" >> girdi.export
done
/usr/lib/systemd/systemd-journal-remote -o kendi.journal girdi.export 2> /dev/null
journalctl --file=kendi.journal --no-pager -q -o short-iso --utc 2> /dev/null
yazilan=$(journalctl --file=kendi.journal --no-pager -q -o cat 2> /dev/null | wc -l)
echo "yazilan $yazilan, atlanan $atlanan"
```

```hint
`read -r zaman oncelik kimlik mesaj <<< "$satir"` satırı dört parçaya böler; son değişken satırın geri kalanını, içindeki `: ` ve `=` ile birlikte alır. `date -u -d "$zaman" +%s` saniyeyi verir, sonuna `000000` eklersin. Ama `date` `tomorrow` sözcüğünü de tarih sayar; önce biçimi bir düzenli ifadeyle denetle.
```

```hint
Her kaydı `printf '...MESSAGE=%s\n\n'` ile bitir: son kayıttan sonraki boş satır eksik kalırsa araç o kaydı atar ve yine 0 ile çıkar. Mesajı biçim metnine değil `%s` argümanına koy; `%95` gibi bir parça biçim yönergesi sanılmasın. Döngüden önce `rm -f kendi.journal`: araç var olan dosyaya ekler.
```
:::
