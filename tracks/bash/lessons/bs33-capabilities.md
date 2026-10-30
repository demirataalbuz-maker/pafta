---
id: bs33
title: Linux Capabilities · Root'un Parçalarını Denetlemek
summary: Root yetkisinin parçalara (capability) bölünmesi; /proc/PID/status'taki CapPrm, CapEff, CapBnd, CapAmb maskelerini capsh --decode ile okumak; dosya capability'leri (getcap, e/p/i bayrakları) ve çalışan bir süreçte görünmeleri; kullanıcı ad alanındaki capability'nin sınırı; getcap -r ile envanter ve getcap'in olmayan yolda bile 0 dönmesi.
kazanim: LPIC1 104.5
backend: wsl
timeout: 90
---

::: anlat Root tek bir yetki değildir
Eskiden Linux'ta ayrıcalık ikiye ayrılırdı: UID 0 her şeyi yapar, ötekiler yapamaz. Bugün root'un gücü kırktan fazla **capability**'ye bölünmüştür ve bir sürece ya da dosyaya yalnız gerekenler verilebilir: ham paket açmak için `cap_net_raw`, 1024 altındaki bir portu dinlemek için `cap_net_bind_service`, dosya sahibini değiştirmek için `cap_chown`. Denetimde soru "bu süreç root mu?" değil, "bu sürecin **hangi** capability'leri etkin?" olur.

Her sürecin capability kümeleri `/proc/PID/status` içinde 64 bitlik onaltılık maskeler olarak durur:

| Satır | Küme | Anlamı |
|---|---|---|
| `CapPrm` | permitted | sürecin kullanabileceği en geniş küme |
| `CapEff` | effective | çekirdeğin şu an **denetlediği** küme |
| `CapInh` | inheritable | `exec` ile korunabilecekler |
| `CapBnd` | bounding | bu süreç ve çocuklarının asla aşamayacağı tavan |
| `CapAmb` | ambient | yetkisiz bir programı `exec` ederken de korunanlar |

Maske okunmaz, çözülür: `capsh --decode=0000000000002000` → `cap_net_raw`. Her bit bir capability'dir; `0x2000` 13. bittir. Sıfır maske `capsh`'ta eşittir işaretinden sonra boş görünür.

```bash
grep -E '^Cap' /proc/self/status
/usr/sbin/capsh --decode="$(awk '/^CapBnd/ {print $2}' /proc/self/status)" | cut -c1-90
```

Sıradan bir kullanıcı kabuğunda `CapPrm` ve `CapEff` sıfırdır; `CapBnd` doludur, çünkü yalnız bir tavandır. Kali'de `getcap`, `setcap` ve `capsh` `/usr/sbin` altındadır ve sıradan kullanıcının `PATH`'inde olmayabilir; bu derste tam yollarıyla çağrılır.

Kaynak: [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html), [proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html).
:::

::: anlat Dosyadan sürece
Bir program root olmadan tek bir ayrıcalığa ihtiyaç duyuyorsa, eskiden setuid root yapılırdı ve her şeyi alırdı. Bugün dosyaya yalnız gereken capability yazılır. `getcap dosya` bunu gösterir; değer dosyanın `security.capability` genişletilmiş özniteliğinde saklanır:

```bash
/usr/sbin/getcap /usr/bin/fping /usr/bin/dumpcap
```

| Bayrak | Anlamı |
|---|---|
| `p` | permitted: program çalışınca sürecin permitted kümesine eklenir |
| `e` | effective: hemen etkin olur (program kendisi açmak zorunda kalmaz) |
| `i` | inheritable: yalnız çağıranın inheritable kümesinde de varsa alınır |

`fping cap_net_raw=ep`, `fping`'i **kim çalıştırırsa çalıştırsın** sürecin ham soket açabileceği anlamına gelir. Bunu çalışan süreçte görmek mümkündür:

```bash
fping -c 10 -p 200 127.0.0.1 >/dev/null 2>&1 &
pid=$!
sleep 0.5
grep -E '^Cap(Prm|Eff)' "/proc/$pid/status"
kill "$pid"; wait "$pid" 2>/dev/null || true
```

Bir dosyaya capability yazmak (`setcap`) normalde `CAP_SETFCAP` ister. **Kullanıcı ad alanı** (`unshare -Ur`) içinde süreç bütün capability'leri taşır görünür (`CapEff` dolar), ama bunlar yalnız o ad alanının sahip olduğu nesneler üzerinde geçerlidir: ana sistemin dosyalarına ya da ağına hükmetmez. Bu dersin testleri envanter dosyalarını böyle hazırlar.

> [!GÜVENLİK]
> Capability'li dosyalar ayrıcalık yükseltme denetimlerinin ilk baktığı yerdir. `cap_setuid`, `cap_dac_override`, `cap_sys_admin` ya da `cap_sys_ptrace` taşıyan bir program, kim çalıştırırsa çalıştırsın, root'a çok yakın bir güç verir. Sunucu sertleştirmede `getcap -r /` çıktısı her paket kurulumundan sonra beklenen listeyle karşılaştırılır; beklenmeyen her satır incelenir.
:::

::: tahmin Kabuk, dosya ve ad alanı
```bash
if (( EUID == 0 )); then
    setpriv --reuid=65534 --regid=65534 --clear-groups grep -E '^Cap(Prm|Eff)' /proc/self/status
else
    grep -E '^Cap(Prm|Eff)' /proc/self/status
fi
/usr/sbin/capsh --decode=0000000000003000
/usr/sbin/getcap /usr/bin/fping
unshare -Ur grep CapEff /proc/self/status
```

???

```text
CapPrm:	0000000000000000
CapEff:	0000000000000000
0x0000000000003000=cap_net_admin,cap_net_raw
/usr/bin/fping cap_net_raw=ep
CapEff:	000001ffffffffff
```

İlk komut, WSL varsayılan kullanıcısı root olsa da UID/GID 65534 ile ayrı bir süreç açar; bu ayrıcalıksız sürecin permitted ve effective kümeleri boştur. Host kullanıcı/grup ayarları değiştirilmez. `0x3000` 12. ve 13. bitlerdir: `cap_net_admin` ve `cap_net_raw`. `fping` dosyasında `cap_net_raw` permitted ve effective olarak yazılıdır. Kullanıcı ad alanının içinde aynı kullanıcının `CapEff`'i bounding kümesinin tamamıdır, ama bu yetkiler yalnız o ad alanında geçerlidir.
:::

::: gorev Bir sürecin yetkilerini çöz
Girdinin tek satırı bir süreç kimliğidir (PID). O sürecin **permitted**, **effective** ve **ambient** kümelerini çözüp tam olarak şu üç satırı yazdır:

```text
CapPrm: cap_a,cap_b
CapEff: cap_a
CapAmb: -
```

- Küme boşsa adın yerine `-` yaz.
- Adlar `capsh --decode`'un verdiği sırada, virgülle ve boşluksuz.
- Böyle bir süreç yoksa `yok` yazdır ve **1** ile çık.
- PID pozitif bir tam sayı değilse ya da satır boşsa `HATA` yazdır ve **2** ile çık.

```stdin
1
```

```starter
read -r pid
grep -E '^Cap' "/proc/$pid/status"
```

```test
import os, subprocess, time
def coz(pid):
    return run(stdin=f"{pid}\n")
drop = ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--inh-caps=-all", "--ambient-caps=-all"] if os.geteuid() == 0 else []
s = subprocess.Popen(drop + ["sleep", "30"])
eq(coz(s.pid), "CapPrm: -\nCapEff: -\nCapAmb: -\n", "sıradan süreç: üç küme de boş")
s.kill(); s.wait()
f = subprocess.Popen(drop + ["fping", "-c", "40", "-p", "200", "127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.6)
eq(coz(f.pid), "CapPrm: cap_net_raw\nCapEff: cap_net_raw\nCapAmb: -\n", "fping: dosya capability'si (=ep) süreçte görünüyor")
f.kill(); f.wait()
ns = subprocess.run(["unshare", "-Ur", "bash", "-c", 'bash betik.sh <<< "$$"'], capture_output=True, text=True)
from pathlib import Path
bound = next(line.split()[1] for line in Path("/proc/self/status").read_text().splitlines() if line.startswith("CapBnd:"))
tam = subprocess.run(["/usr/sbin/capsh", "--decode=" + bound], capture_output=True, text=True).stdout.strip().split("=", 1)[1]
eq(ns.stdout, f"CapPrm: {tam}\nCapEff: {tam}\nCapAmb: -\n", "kullanıcı ad alanındaki kabuk: bounding kümesinin tamamı")
ok(ns.stdout.startswith("CapPrm: cap_chown,cap_dac_override,"), "adlar capsh sırasında")
r = calis(stdin="999999999\n")
eq((r["kod"], r["cikti"]), (1, "yok\n"), "olmayan PID")
for kotu in ("abc\n", "\n", "-1\n", "0\n", "1 2\n", "../1\n"):
    r = calis(stdin=kotu)
    eq((r["kod"], r["cikti"]), (2, "HATA\n"), f"geçersiz PID: {kotu!r}")
```

```solution
read -r pid extra || true
if [[ ! $pid =~ ^[1-9][0-9]*$ || -n $extra ]]; then
    echo HATA
    exit 2
fi
if [[ ! -r /proc/$pid/status ]]; then
    echo yok
    exit 1
fi
for kume in CapPrm CapEff CapAmb; do
    maske=$(awk -v k="$kume:" '$1 == k {print $2}' "/proc/$pid/status")
    adlar=$(/usr/sbin/capsh --decode="$maske")
    adlar=${adlar#*=}
    echo "$kume: ${adlar:--}"
done
```

```hint
Her küme için `/proc/$pid/status`'tan maskeyi al (`awk '$1 == "CapEff:" {print $2}'`), `capsh --decode=$maske` ile çöz ve eşittir işaretinden öncesini at: `${adlar#*=}`.
```

```hint
Boş kümede `capsh` eşittir işaretinden sonra hiçbir şey yazmaz; `${adlar:--}` boşsa `-` koyar. PID'i `^[1-9][0-9]*$` ile denetle: `0`, `-1` ve `../1` geçmemeli.
```
:::

::: gorev Capability envanteri
Girdinin tek satırı bir klasördür. Klasörün altındaki (alt klasörler dahil) **capability taşıyan her dosyayı** yol sırasıyla, satır başına `yol<TAB>capability` biçiminde yazdır. Yol, `getcap`'in yazdığı gibi verilen klasörle başlar; capability `getcap`'in metnidir (`cap_net_raw=ep`).

- Capability'li dosya yoksa hiçbir şey yazdırma ve **0** ile çık.
- Klasör yoksa standart hataya bir ileti yaz ve **2** ile çık. Dikkat: `getcap` olmayan bir yolda da 0 döner.
- Satır boşsa `HATA` yazdır ve **2** ile çık.
- Adında boşluk olan dosyalar doğru yazılmalı.

Hazırlık `envanter/` klasörünü kurar: capability'li üç dosya (biri alt klasörde, biri adında boşlukla) ve capability'siz bir dosya. Capability'ler kullanıcı ad alanında yazılır.

```stdin
envanter
```

```setup
import os, shutil, subprocess
os.makedirs("envanter/alt", exist_ok=True)
for ad in ("envanter/zil", "envanter/ag araci", "envanter/alt/sahip", "envanter/duz"):
    shutil.copy("/usr/bin/true", ad)
subprocess.run(["unshare", "-Ur", "sh", "-c",
                "/usr/sbin/setcap cap_net_raw=ep envanter/zil && "
                "/usr/sbin/setcap cap_net_bind_service,cap_net_raw=eip 'envanter/ag araci' && "
                "/usr/sbin/setcap cap_chown=p envanter/alt/sahip"], check=True)
os.makedirs("bos", exist_ok=True)
```

```starter
read -r klasor
/usr/sbin/getcap -r "$klasor"
```

```test
import subprocess
eq(out, "envanter/ag araci\tcap_net_bind_service,cap_net_raw=eip\n"
        "envanter/alt/sahip\tcap_chown=p\n"
        "envanter/zil\tcap_net_raw=ep\n", "üç dosya, yol sırasıyla; boşluklu ad bütün")
eq(run(stdin="bos\n"), "", "capability'li dosya yok: boş çıktı")
eq(run(stdin="envanter/alt\n"), "envanter/alt/sahip\tcap_chown=p\n", "alt klasörden başlamak")
r = calis(stdin="olmayan\n")
ok(r["kod"] == 2 and r["hata"].strip() and not r["cikti"], "olmayan klasör: stderr ve çıkış 2 (getcap 0 dönse bile)", got=r)
r = calis(stdin="\n")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "boş satır")
subprocess.run(["unshare", "-Ur", "/usr/sbin/setcap", "-r", "envanter/zil"], check=True)
eq(run(stdin="envanter\n"), "envanter/ag araci\tcap_net_bind_service,cap_net_raw=eip\nenvanter/alt/sahip\tcap_chown=p\n",
   "capability'si kaldırılan dosya envanterden düşer")
```

```solution
read -r klasor || true
if [[ -z $klasor ]]; then
    echo HATA
    exit 2
fi
if [[ ! -d $klasor ]]; then
    echo "klasör yok: $klasor" >&2
    exit 2
fi
/usr/sbin/getcap -r "$klasor" | while IFS= read -r satir; do
    printf '%s\t%s\n' "${satir% *}" "${satir##* }"
done | LC_ALL=C sort
```

```hint
`getcap -r` satırları `yol capability` biçimindedir ve sırasızdır. Capability son boşluktan sonrasıdır: `${satir##* }`; yol ondan öncesi: `${satir% *}`. Böylece adındaki boşluk yolda kalır.
```

```hint
`getcap` olmayan yolu standart çıktıya yazar ve 0 döner; klasörü önce `[[ -d ]]` ile sen denetle. Sıralama için `LC_ALL=C sort`.
```
:::
