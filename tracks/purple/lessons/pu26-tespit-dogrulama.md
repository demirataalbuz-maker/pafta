---
id: pu26
title: Tespiti Doğrulama · Atomic Red Team Adımını İzole Konteynerde Koştur, Telemetride Yakala
summary: İzole bir Linux konteynerinde seçili Atomic Red Team kalıcılık adımlarını strace altında koştur; ham telemetriyi normalleştir, atomic tanımını oku, Sigma benzeri bir kuralla kalıcılık yazımını yakala ve meşru okumada yanlış pozitif vermediğini ölç.
timeout: 60
esleme: pu21 (tatbikat yönetimi), pu25 (CTID planı), pu05 (tespit kuralı)
---

::: anlat Saldırıyı koşmadan tespiti doğrulayamazsın
| Sahada ne olur | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Savunma ekibi bir tespit kuralı yazar ama gerçek bir saldırı adımıyla sınamadan çalışıp çalışmadığını bilmez | `pafta-linux-lab` konteyneri (`--network none`), 4 seçili dosya-tabanlı Atomic Red Team adımı, strace telemetrisi | Gerçek bir EDR'yi, auditd/Sysmon'u, çekirdek sensörünü ya da ağ tabanlı tespiti göstermez |
| Atomic Red Team testleri gerçek tekniklerin küçük, tekrar üretilebilir uygulamalarıdır | 6 gerçek atomic YAML tanımı (sabit revizyon), yalnız izin listesindeki zararsız adımlar | Deponun ağa çıkan ya da gerçek zarar veren testlerini çalıştırmaz |
| İyi bir kural saldırıyı yakalar **ve** meşru işi rahat bırakır | Aynı telemetride hem saldırı hem iyi huylu olaylar, TP/FP ölçümü | Bu küçük örnekteki oranlar kuralın genel başarısını ölçmez |

> [!NOT]
> İlk üç görev `tespit/ornekler.json` dosyasını okur; olaylar, atomic tanımı ve kural **sentetiktir**, elle yazılmıştır. Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Dosyayı görmek için başlangıç kodundaki `print` satırlarını kullan. Son görev, önceden onaylanmış `pafta-linux-lab` konteynerini `--network none`, `no-new-privileges`, bellek ve pid sınırıyla açar; içinde yalnız izin listesindeki zararsız `echo`/`grep`/`rm` adımları strace altında koşar. Konteyner içindeki güvenilir ayrıştırıcı ham strace'i normalleştirilmiş olaylara çevirir; sen bu olaylarla çalışırsın. Konteyner her koşuda atılır (`--rm`); ana makinede hiçbir dosya değişmez. Bu teknikleri sahibi olmadığın bir sisteme uygulamak yasa dışıdır; pu21'deki kapsam kapısı burada da geçerlidir.

**Telemetri nereden gelir?** Gerçek bir savunmada olay kaydı çekirdekten gelir: auditd, Sysmon for Linux, ya da bir EDR'nin sensörü. Bu ders bunları kuramaz (ölçüldü: bu konteyner motorunda audit arabirimi `EPERM` döner). Yerine **strace** kullanır: izlenen süreç ağacının yaptığı sistem çağrılarını kaydeder. strace bir EDR **değildir** — yalnız kendi başlattığı süreci görür, sistem geneli sensör değildir ve izlenen süreç izlendiğini anlayabilir. Ama tespit **mantığını** öğretmek için yeter: "hangi işlem, hangi dosyaya, ne yönde (oku/yaz/çalıştır) dokundu?" sorusu auditd'de de, EDR'de de aynıdır.

**Kalıcılığın kurulumu, tetiklenmesi değil.** Bu ders cron işinin **çalışmasını** beklemez (bir dakika sürerdi ve 60 sn sınırını aşardı). Bunun yerine kalıcılığın **kurulduğu** anı yakalar: `~/.bashrc`'ye komut eklenmesi, `/etc/cron.d/` altına dosya yazılması. Gerçek tespit de böyle çalışır: kalıcılık mekanizması kurulurken yakalanırsa, tetiklenmesini beklemek gerekmez.

**Saldırgan ne dener?** Küçük, gürültüsüz kalıcılık adımları: kabuk yapılandırmasına (`~/.bashrc`, `~/.bash_profile`, `/etc/profile`) komut eklemek (T1546.004), `/etc/cron.d/` altına zamanlanmış iş koymak (T1053.003). İzini silmek için bash geçmişini sıfırlar (T1070.003). Sistemdeki ayrıcalıklı hesapları sayar (T1087.001). Bu adımların çoğu tek bir dosya işlemidir ve meşru yönetim işine benzer.

**Savunma neden kırılır?** En sık hata, **yöne bakmamaktır**. "`.bashrc` dosyasına her dokunuş" diye yazılan kural, meşru bir `cat ~/.bashrc` okumasında da çalar: yanlış pozitif. Oysa kalıcılık bir **yazma**dır. Kural dosya adına ve yöne birlikte bakmalı: `.bashrc`'ye *yazma*, `/etc/cron.d/` altına *yazma*. Okuma, çalıştırma ve kütüphane gürültüsü elenmelidir. Tersi de olur: yalnız tam yol eşleşmesine bakan kural, `/etc/cron.d/` yerine `/etc/cron.daily/` kullanan bir varyantı kaçırır.

**Blue karşılığı.** Telemetriyi normalleştir (işlem, yön, hedef), sonra bir Sigma benzeri kuralla eşle. Kuralı iki yönden sına: saldırı adımlarını yakalıyor mu (TP), meşru işi rahat bırakıyor mu (FP = 0?). Yanlış pozitif üreten bir kural, tıpkı gürültülü bir SAST kuralı gibi (pu23), analisti kuralı kapatmaya iter. Bu yüzden tespiti saldırıyla doğrulamak, kuralı yazmak kadar önemlidir.

Kaynaklar: [Atomic Red Team · T1546.004](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1546.004/T1546.004.md), [MITRE ATT&CK · T1053.003 Cron](https://attack.mitre.org/techniques/T1053/003/), [MITRE ATT&CK · T1546.004 Unix Shell Configuration Modification](https://attack.mitre.org/techniques/T1546/004/), [SigmaHQ · Rule format](https://github.com/SigmaHQ/sigma-specification), [strace · man](https://man7.org/linux/man-pages/man1/strace.1.html). Bu dersteki bütün sayılar yalnız yerel kanıttan gelir.

Purple bağı: pu25 CTID APT29 planını tespit beklentisi yazılmış bir test planına çevirdi; bu ders o beklentinin bir satırını gerçek bir adımla sınar. pu21'deki tatbikat defterine bu koşunun "beklenen alarm" satırı girer; yakalanan kalıcılık pu05'teki Sigma kuralının telemetri alanlarıyla eşlenir.
:::

::: tahmin Yön, bayrak ve gürültü
Çıktıyı tahmin et, sonra Çalıştır ile karşılaştır.
```python
bayrak = ["O_WRONLY", "O_CREAT", "O_APPEND"]
yazma = {"O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC"}
print("yaz" if set(bayrak) & yazma else "oku")
print(any("/usr/lib/libc.so.6".startswith(p) for p in ("/usr/lib", "/lib")))
yol = "/etc/cron.d/pafta"
print(any(d in yol for d in ("/etc/cron.d/", ".bashrc")))
```
???
```cikti
yaz
True
True
```
Tahmininle gerçek çıktı arasındaki farkı tezgâhta yorum satırı olarak yaz: `O_RDONLY` için hangi bayrak kümesi boş kalır? Bir kütüphane açılışını (`.so`) neden elemek gerekir? Sonra üç kusurlu başlangıç kodunu çalıştır. Hangisi okuma ile yazmayı ayırmayıp her dokunuşu "yaz" sayıyor, hangisi atomic tanımındaki `guid`'i doğrulamayıp boş teste izin veriyor, hangisi kural koşulunu (`hepsi`/`herhangi`) yok sayıp tek alana bakıyor? Önce kendin teşhis et; açıklama çözümün ardından gelir.
:::

::: gorev 1 · strace olaylarını sınıfla
`olay_sinifla(olaylar)`: her olay `cagri` (sistem çağrısı), `comm` (işlem adı), `yol`, `argv` ve `bayrak` taşır. Her olay için `{"comm", "yon", "hedef"}` üret:

- `cagri` `execve` ise `yon` `"calistir"`, `hedef` `argv[0]`.
- `cagri` `openat` ise: `bayrak` içinde `O_WRONLY`, `O_RDWR`, `O_CREAT`, `O_APPEND` ya da `O_TRUNC` varsa `yon` `"yaz"`, yoksa `"oku"`; `hedef` `yol`.
- `cagri` `chmod`, `fchmodat`, `renameat2` ya da `unlinkat` ise `yon` `"yaz"`, `hedef` `yol`.
- `execve` dışındaki olayın hedefi gürültüyse (yol `/usr/lib`, `/lib`, `/usr/bin`, `/proc`, `/sys`, `/etc/ld`, `/dev` ile başlıyorsa ya da `.so` içeriyorsa) **ele**.
- Kalan olayları, geldikleri sırada döndür.

`comm` boşsa, `cagri` tanınmıyorsa, `execve`'de `argv` boş/yanlış türse, `openat`'te `yol` yoksa ya da `bayrak` liste değilse `ValueError`.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def olay_sinifla(olaylar):
    out = []
    for e in olaylar:
        if e["cagri"] == "execve":
            out.append({"comm": e["comm"], "yon": "calistir", "hedef": e["argv"][0]})
        else:
            out.append({"comm": e["comm"], "yon": "yaz", "hedef": e["yol"]})
    return out

import json
from pathlib import Path
v = json.loads(Path("tespit/ornekler.json").read_text(encoding="utf-8"))
for c in olay_sinifla(v["olaylar"]):
    print(c)
```

```solution
YAZMA_BAYRAK = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC")
CAGRILAR = ("execve", "openat", "chmod", "fchmodat", "renameat2", "unlinkat")
GURULTU_ON = ("/usr/lib", "/lib", "/usr/bin", "/proc", "/sys", "/etc/ld", "/dev")
def gurultu_mu(yol):
    return any(yol.startswith(p) for p in GURULTU_ON) or yol.endswith(".so") or ".so." in yol
def olay_sinifla(olaylar):
    if not isinstance(olaylar, list):
        raise ValueError("olaylar listesi")
    out = []
    try:
        for e in olaylar:
            cagri, comm = e["cagri"], e["comm"]
            if cagri not in CAGRILAR or not isinstance(comm, str) or not comm:
                raise ValueError("olay alanı")
            bayrak = e.get("bayrak") or []
            if not isinstance(bayrak, list) or any(not isinstance(b, str) for b in bayrak):
                raise ValueError("bayrak")
            if cagri == "execve":
                argv = e.get("argv")
                if not isinstance(argv, list) or not argv or any(not isinstance(a, str) for a in argv):
                    raise ValueError("argv")
                yon, hedef = "calistir", argv[0]
            else:
                yol = e.get("yol")
                if not isinstance(yol, str) or not yol:
                    raise ValueError("yol")
                hedef = yol
                if cagri == "openat":
                    yon = "yaz" if any(b in bayrak for b in YAZMA_BAYRAK) else "oku"
                else:
                    yon = "yaz"
            if yon != "calistir" and gurultu_mu(hedef):
                continue
            out.append({"comm": comm, "yon": yon, "hedef": hedef})
    except (KeyError, TypeError, AttributeError):
        raise ValueError("bozuk olay")
    return out

import json
from pathlib import Path
v = json.loads(Path("tespit/ornekler.json").read_text(encoding="utf-8"))
for c in olay_sinifla(v["olaylar"]):
    print(c)
```

```test
need('olay_sinifla')
def sinama1(f):
    try:
        def E(comm, cagri, yol=None, argv=None, bayrak=None):
            return {"pid": 1, "comm": comm, "cagri": cagri, "yol": yol, "argv": argv, "bayrak": bayrak or []}
        ol = [E("bash", "execve", argv=["/usr/bin/bash", "-c", "x"]),
              E("cat", "openat", yol="/usr/lib/libc.so.6", bayrak=["O_RDONLY"]),
              E("cat", "openat", yol="/root/.bashrc", bayrak=["O_RDONLY"]),
              E("bash", "openat", yol="/root/.bashrc", bayrak=["O_WRONLY", "O_APPEND"]),
              E("bash", "openat", yol="/etc/cron.d/x", bayrak=["O_WRONLY", "O_CREAT", "O_TRUNC"]),
              E("bash", "chmod", yol="/tmp/y"),
              E("bash", "unlinkat", yol="/root/.bash_history"),
              E("sh", "openat", yol="/proc/self/stat", bayrak=["O_RDONLY"]),
              E("app", "openat", yol="/opt/app/plugin.so", bayrak=["O_RDONLY"]),
              E("sh", "openat", yol="/home/u/.so.keep", bayrak=["O_RDONLY"])]
        bek = [{"comm": "bash", "yon": "calistir", "hedef": "/usr/bin/bash"},
               {"comm": "cat", "yon": "oku", "hedef": "/root/.bashrc"},
               {"comm": "bash", "yon": "yaz", "hedef": "/root/.bashrc"},
               {"comm": "bash", "yon": "yaz", "hedef": "/etc/cron.d/x"},
               {"comm": "bash", "yon": "yaz", "hedef": "/tmp/y"},
               {"comm": "bash", "yon": "yaz", "hedef": "/root/.bash_history"}]
        if f(ol) != bek:
            return False
        if f([]) != []:
            return False
        if f([E("x", "openat", yol="/a", bayrak=["O_RDWR"])]) != [{"comm": "x", "yon": "yaz", "hedef": "/a"}]:
            return False
        if f([E("x", "execve", argv=["/bin/ls", "/usr/lib/x"])]) != [{"comm": "x", "yon": "calistir", "hedef": "/bin/ls"}]:
            return False
        for a in ("x", None, [1], [{"cagri": "openat", "comm": "a"}], [{"cagri": "nope", "comm": "a", "yol": "/x"}],
                  [{"cagri": "openat", "comm": "", "yol": "/x"}], [{"cagri": "execve", "comm": "a", "argv": []}],
                  [{"cagri": "execve", "comm": "a", "argv": None}], [{"cagri": "execve", "comm": "a", "argv": [1]}],
                  [{"cagri": "openat", "comm": "a", "yol": None, "bayrak": []}],
                  [{"cagri": "openat", "comm": "a", "yol": "", "bayrak": []}],
                  [{"cagri": "openat", "comm": "a", "yol": "/x", "bayrak": "O_RDONLY"}],
                  [{"cagri": "openat", "comm": "a", "yol": "/x", "bayrak": [1]}]):
            try:
                f(a); return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sinama1(olay_sinifla),"execve→çalıştır, openat yazma bayrağı→yaz yoksa oku, chmod/unlinkat→yaz, kütüphane/proc gürültüsü elenir, bozuk girdi reddi")
def _bos(o):
    try:
        return olay_sinifla(o)
    except ValueError:
        return []
for ad, mut in [("sırasız", lambda o: list(reversed(olay_sinifla(o)))),
                ("gürültü de", lambda o: olay_sinifla(o) + [{"comm": "x", "yon": "oku", "hedef": "/usr/lib/a"}]),
                ("bozukta boş", _bos)]:
    ok(not sinama1(mut), "mutant reddedildi: " + ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tespit_lab import hazirla
hazirla()
```

```hint
Okuma ile yazmayı ayıran şey açılış bayraklarıdır; `O_RDONLY`'nin kendine ait bir biti yoktur, yazma bayraklarının yokluğudur. Kütüphane açılışlarını (`.so`) elemezsen her işlem onlarca gürültü üretir.
```
:::

::: anlat Atomic tanımı bir sözleşmedir
Bir Atomic Red Team testi, bir ATT&CK tekniğinin küçük ve tekrar üretilebilir bir uygulamasıdır. YAML tanımı tekniği (`attack_technique`), her testin adını, bir `auto_generated_guid`'ini, çalıştırıcı komutunu ve yükseltme gerekip gerekmediğini (`elevation_required`) taşır. Bu alanları okumak, hangi adımın hangi telemetriyi üreteceğini önceden bilmeni sağlar: `>> ~/.bashrc` komutu bir **yazma** olayı üretecektir. Bu ders deponun yalnız 6 tanımını ve içlerinden izin listesindeki zararsız adımları kullanır; ağa çıkan ya da sistemi kalıcı değiştiren testler koşmaz.
:::

::: gorev 2 · Atomic tanımını oku
`atomik_oku(yaml_metni)`: Atomic Red Team YAML tanımını ayrıştır.

- `attack_technique` alanından `teknik`; `T` + 4 rakam, isteğe bağlı `.` + 3 rakam (`T1546.004`).
- Her `- name:` bloğu bir testtir: `ad` (başlık), `guid` (`auto_generated_guid`, `8-4-4-4-12` onaltılık), `yukseltme` (`elevation_required: true` varsa `True`), `komut` (`command: |` bloğundaki boş olmayan satırlar, kırpılmış).
- Her testi `{"teknik", "ad", "guid", "yukseltme", "komut"}` olarak üret; listeyi `guid`'e göre sıralı döndür.

`teknik` biçimi yanlışsa, bir testin `ad`'ı ya da `guid`'i yoksa/bozuksa, `command` bloğu yoksa, hiç test yoksa ya da `guid` yinelenirse `ValueError`.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
import re
def atomik_oku(yaml_metni):
    teknik = re.search(r"attack_technique:\s*(\S+)", yaml_metni).group(1)
    out = []
    for blok in re.split(r"(?m)^- name:\s*", yaml_metni)[1:]:
        ad = blok.splitlines()[0].strip()
        out.append({"teknik": teknik, "ad": ad})
    return out

import json
from pathlib import Path
v = json.loads(Path("tespit/ornekler.json").read_text(encoding="utf-8"))
for t in atomik_oku(v["atomik_yaml"]):
    print(t["guid"], t["ad"], t["yukseltme"], t["komut"])
```

```solution
import re
def atomik_oku(yaml_metni):
    if not isinstance(yaml_metni, str) or not yaml_metni.strip():
        raise ValueError("yaml")
    m = re.search(r"(?m)^attack_technique:\s*(\S+)", yaml_metni)
    teknik = m.group(1).strip().strip('"') if m else None
    if not teknik or not re.fullmatch(r"T\d{4}(\.\d{3})?", teknik):
        raise ValueError("teknik")
    out = []
    for blok in re.split(r"(?m)^- name:", yaml_metni)[1:]:
        ad = blok.splitlines()[0].strip().strip('"')
        g = re.search(r"(?m)^\s*auto_generated_guid:\s*(\S+)", blok)
        guid = g.group(1).strip() if g else None
        if not ad or not guid or not re.fullmatch(r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}", guid):
            raise ValueError("test başlığı ya da guid")
        yukseltme = bool(re.search(r"(?m)^\s*elevation_required:\s*true", blok))
        c = re.search(r"(?m)^(?P<ind>[ \t]*)command:[ \t]*\|[ \t]*\n(?P<govde>(?:(?P=ind)[ \t]+.*\n?)+)", blok)
        if not c:
            raise ValueError("komut")
        satirlar = [s.strip() for s in c.group("govde").splitlines() if s.strip()]
        out.append({"teknik": teknik, "ad": ad, "guid": guid, "yukseltme": yukseltme, "komut": satirlar})
    if not out:
        raise ValueError("test yok")
    if len({t["guid"] for t in out}) != len(out):
        raise ValueError("yinelenen guid")
    return sorted(out, key=lambda t: t["guid"])

import json
from pathlib import Path
v = json.loads(Path("tespit/ornekler.json").read_text(encoding="utf-8"))
for t in atomik_oku(v["atomik_yaml"]):
    print(t["guid"], t["ad"], t["yukseltme"], t["komut"])
```

```test
need('atomik_oku')
def sinama2(f):
    try:
        y = ("attack_technique: T1546.004\n"
             "atomic_tests:\n"
             "- name: Ikinci\n"
             "  auto_generated_guid: bbbbbbbb-2222-3333-4444-555555555555\n"
             "  executor:\n    command: |\n      echo b >> ~/.bashrc\n      chmod 600 ~/.bashrc\n    name: sh\n"
             "- name: Birinci\n"
             "  auto_generated_guid: aaaaaaaa-2222-3333-4444-555555555555\n"
             "  executor:\n    elevation_required: true\n    command: |\n      echo a > /etc/cron.d/x\n    name: sh\n")
        r = f(y)
        if [t["guid"][0] for t in r] != ["a", "b"]:
            return False
        if r[0] != {"teknik": "T1546.004", "ad": "Birinci", "guid": "aaaaaaaa-2222-3333-4444-555555555555",
                    "yukseltme": True, "komut": ["echo a > /etc/cron.d/x"]}:
            return False
        if r[1]["yukseltme"] is not False or r[1]["komut"] != ["echo b >> ~/.bashrc", "chmod 600 ~/.bashrc"]:
            return False
        tek = f("attack_technique: T1053\natomic_tests:\n- name: X\n  auto_generated_guid: "
                "cccccccc-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n    name: sh\n")
        if tek[0]["teknik"] != "T1053":
            return False
        elf = ("attack_technique: T1001\natomic_tests:\n- name: X\n  auto_generated_guid: "
               "cccccccc-1111-2222-3333-444444444444\n  executor:\n    elevation_required: false\n"
               "    command: |\n      echo x\n    name: sh\n")
        if f(elf)[0]["yukseltme"] is not False:
            return False
        dup = ("attack_technique: T1001\natomic_tests:\n"
               "- name: A\n  auto_generated_guid: dddddddd-2222-3333-4444-555555555555\n"
               "  executor:\n    command: |\n      echo a\n    name: sh\n"
               "- name: B\n  auto_generated_guid: dddddddd-2222-3333-4444-555555555555\n"
               "  executor:\n    command: |\n      echo b\n    name: sh\n")
        bosad = ("attack_technique: T1001\natomic_tests:\n- name: \n  auto_generated_guid: "
                 "ffffffff-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n    name: sh\n")
        for bad in ("", "   ", "atomic_tests:\n- name: X\n", "attack_technique: BAD\natomic_tests:\n- name: X\n",
                    "attack_technique: T1\natomic_tests:\n- name: X\n  executor:\n    command: |\n      echo x\n",
                    "attack_technique: T1546.04\natomic_tests:\n- name: X\n  auto_generated_guid: "
                    "11111111-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n",
                    "attack_technique: T1546.004\natomic_tests:\n- name: X\n  auto_generated_guid: "
                    "AAAAAAAA-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n",
                    bosad,
                    "attack_technique: T1546.004\natomic_tests:\n- name: X\n  auto_generated_guid: nope\n"
                    "  executor:\n    command: |\n      echo x\n",
                    "attack_technique: T1546.004\natomic_tests:\n- name: X\n  auto_generated_guid: "
                    "eeeeeeee-2222-3333-4444-555555555555\n  executor:\n    name: sh\n", dup, 5, None):
            try:
                f(bad); return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sinama2(atomik_oku),"teknik+guid doğrulaması, guid'e göre sıralı, yükseltme ve komut satırları, yinelenen guid ve bozuk tanım reddi")
def _bos(y):
    try:
        return atomik_oku(y)
    except ValueError:
        return []
for ad, mut in [("sırasız", lambda y: atomik_oku(y)[::-1]),
                ("yükseltme ters", lambda y: [dict(t, yukseltme=not t["yukseltme"]) for t in atomik_oku(y)]),
                ("bozukta boş", _bos)]:
    ok(not sinama2(mut), "mutant reddedildi: " + ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tespit_lab import hazirla
hazirla()
```

```hint
Teknik ve guid'i düzenli ifadeyle doğrula; biri olmadan test geçerli sayılmaz. `command: |` çok satırlı olabilir; her satırı kırp ve boşları at.
```
:::

::: anlat Kural: alan, değer, koşul
Sigma benzeri bir kural bir **seçim** (hangi alan hangi değerleri taşımalı) ve bir **koşul** (`hepsi` mi, `herhangi` mi) taşır. `comm` işlemin adı, `yon` olayın yönü (`oku`/`yaz`/`calistir`), `hedef_icerir` ise hedef yolun içermesi gereken parçalardır. Kalıcılık kuralı iki alanı **hepsi** ile birleştirir: yön `yaz` **ve** hedef kabuk yapılandırması ya da cron dizini. Tek alana bakan ya da koşulu yok sayan kural ya çok geniştir (yanlış pozitif) ya da hiç eşleşmez.
:::

::: gorev 3 · Kuralı sınıflı olaylara uygula
`kural_uygula(sinifli, kural)`: `sinifli` Görev 1'in çıktısıdır (`{"comm", "yon", "hedef"}` listesi). `kural` bir `id`, bir `kosul` (`"hepsi"` ya da `"herhangi"`) ve bir `secim` sözlüğü taşır. `secim`'in alanları:

- `comm`: işlem adı değerlerden biri olmalı.
- `yon`: yön değerlerden biri olmalı.
- `hedef_icerir`: hedef, değerlerden **birini** içermeli.

Her olay için seçim alanlarının sonucunu topla; `kosul` `"hepsi"` ise **hepsi**, `"herhangi"` ise **en az biri** doğruysa olay eşleşir. Eşleşen her olay için `{"kural": kural["id"], "comm", "yon", "hedef"}` üret; olayların sırasını koru.

`id` boşsa, `kosul` ikisinden biri değilse, `secim` boşsa ya da tanınmayan alan/boş değer listesi taşırsa, `sinifli` liste değilse ya da bir olayın `yon`'u geçersizse `ValueError`.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def kural_uygula(sinifli, kural):
    out = []
    for e in sinifli:
        for alan, degerler in kural["secim"].items():
            if alan == "hedef_icerir" and any(d in e["hedef"] for d in degerler):
                out.append({"kural": kural["id"], "comm": e["comm"], "yon": e["yon"], "hedef": e["hedef"]})
    return out

import json
from pathlib import Path
v = json.loads(Path("tespit/ornekler.json").read_text(encoding="utf-8"))
for h in kural_uygula(v["sinifli"], v["kural"]):
    print(h)
```

```solution
def kural_uygula(sinifli, kural):
    if not isinstance(kural, dict) or not isinstance(kural.get("id"), str) or not kural["id"]:
        raise ValueError("kural id")
    if kural.get("kosul") not in ("hepsi", "herhangi"):
        raise ValueError("koşul")
    secim = kural.get("secim")
    if not isinstance(secim, dict) or not secim:
        raise ValueError("seçim")
    for alan, degerler in secim.items():
        if alan not in ("comm", "yon", "hedef_icerir") or not isinstance(degerler, list) or not degerler \
                or any(not isinstance(d, str) or not d for d in degerler):
            raise ValueError("seçim alanı")
    if not isinstance(sinifli, list):
        raise ValueError("sınıflı olaylar listesi")
    hepsi = kural["kosul"] == "hepsi"
    out = []
    for e in sinifli:
        if not isinstance(e, dict) or e.get("yon") not in ("oku", "yaz", "calistir") \
                or not isinstance(e.get("comm"), str) or not isinstance(e.get("hedef"), str):
            raise ValueError("sınıflı olay alanı")
        sonuc = []
        for alan, degerler in secim.items():
            if alan == "comm":
                sonuc.append(e["comm"] in degerler)
            elif alan == "yon":
                sonuc.append(e["yon"] in degerler)
            else:
                sonuc.append(any(d in e["hedef"] for d in degerler))
        if (all(sonuc) if hepsi else any(sonuc)):
            out.append({"kural": kural["id"], "comm": e["comm"], "yon": e["yon"], "hedef": e["hedef"]})
    return out

import json
from pathlib import Path
v = json.loads(Path("tespit/ornekler.json").read_text(encoding="utf-8"))
for h in kural_uygula(v["sinifli"], v["kural"]):
    print(h)
```

```test
need('kural_uygula')
def sinama3(f):
    try:
        S = [{"comm": "cat", "yon": "oku", "hedef": "/root/.bashrc"},
             {"comm": "bash", "yon": "yaz", "hedef": "/root/.bashrc"},
             {"comm": "bash", "yon": "yaz", "hedef": "/etc/cron.d/x"},
             {"comm": "grep", "yon": "oku", "hedef": "/etc/passwd"}]
        kal = {"id": "k1", "kosul": "hepsi", "secim": {"yon": ["yaz"], "hedef_icerir": [".bashrc", "/etc/cron.d/"]}}
        r = f(S, kal)
        if [x["hedef"] for x in r] != ["/root/.bashrc", "/etc/cron.d/x"] or any(x["kural"] != "k1" for x in r):
            return False
        saf = {"id": "s", "kosul": "herhangi", "secim": {"hedef_icerir": [".bashrc", "/etc/passwd"]}}
        if [x["hedef"] for x in f(S, saf)] != ["/root/.bashrc", "/root/.bashrc", "/etc/passwd"]:
            return False
        cg = {"id": "c", "kosul": "hepsi", "secim": {"comm": ["grep"], "yon": ["oku"]}}
        if [x["comm"] for x in f(S, cg)] != ["grep"]:
            return False
        if f([], kal) != []:
            return False
        if f(S, {"id": "z", "kosul": "herhangi", "secim": {"comm": ["yok"]}}) != []:
            return False
        for a in ((S, {"kosul": "hepsi", "secim": {"yon": ["yaz"]}}), (S, {"id": "", "kosul": "hepsi", "secim": {"yon": ["yaz"]}}),
                  (S, {"id": "x", "kosul": "belki", "secim": {"yon": ["yaz"]}}), (S, {"id": "x", "kosul": "hepsi", "secim": {}}),
                  (S, {"id": "x", "kosul": "hepsi", "secim": {"nope": ["a"]}}), (S, {"id": "x", "kosul": "hepsi", "secim": {"yon": []}}),
                  (S, {"id": "x", "kosul": "hepsi", "secim": {"yon": [1]}}), (S, {"id": "x", "kosul": "hepsi", "secim": {"yon": [""]}}),
                  ("x", kal), ([{"comm": "a", "yon": "ucmak", "hedef": "/x"}], kal), ([{"comm": "a", "hedef": "/x"}], kal),
                  ([{"yon": "yaz", "hedef": "/x"}], kal), ([{"comm": "a", "yon": "yaz"}], kal)):
            try:
                f(*a); return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sinama3(kural_uygula),"comm/yon/hedef_icerir alanları, hepsi/herhangi koşulu, geçersiz kural ve sınıflı olay reddi")
def _bos(s, k):
    try:
        return kural_uygula(s, k)
    except ValueError:
        return []
for ad, mut in [("sırasız", lambda s, k: kural_uygula(s, k)[::-1]),
                ("herhangi gibi", lambda s, k: kural_uygula(s, dict(k, kosul="herhangi"))),
                ("bozukta boş", _bos)]:
    ok(not sinama3(mut), "mutant reddedildi: " + ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tespit_lab import hazirla
hazirla()
```

```hint
`hepsi` için bütün alanların doğru olması, `herhangi` için en az birinin. Saf kural (yalnız `hedef_icerir`, `herhangi`) meşru okumayı da yakalar: yön alanını eklemek yanlış pozitifi düşürür.
```
:::

::: anlat Hata vitrini · yazar koşusu
Yazar son görevi referans işlevlerle ve `validate` ile birçok kez çalıştırdı (Python 3.13, Windows; `pafta-linux-lab:13-1` konteyneri). Koşu 3–5 sn sürdü, karar her koşuda aynıydı.

- **Telemetri:** Konteyner 1 meşru gürültü grubu + 4 saldırı adımı koştu; strace ayrıştırıcısı ~88 normalleştirilmiş olay üretti (koşu yüküne göre birkaç olay oynar).
- **Kalıcılık kuralı (yön `yaz` + hedef):** TP 2, FP 0. `~/.bashrc`'ye eklemeyi ve `/etc/cron.d/` altına yazmayı yakaladı; `/etc/passwd` okumasını (T1087, bir **okuma**) doğru biçimde görmezden geldi — çünkü o bir kalıcılık yazması değil.
- **Saf kural (yalnız hedef, yöne bakmaz):** TP 8, FP 2. Aynı dosyalara dokunan her olayı saydığı için meşru `cat ~/.bashrc` **okumasını** da "bulgu" saydı: iki yanlış pozitif.
- **Atomic okuma:** 4 teknik (T1053.003, T1070.003, T1087.001, T1546.004) tanımdan doğru ayrıştırıldı; her testin `guid`'i ve yükseltme bayrağı okundu.

Kendi cümlenle açıkla: saldırgan `~/.bashrc` yerine yeni bir `/etc/cron.daily/` betiği kullansaydı, kalıcılık kuralının `hedef_icerir` listesine ne eklerdin? Bu ekleme yanlış pozitifi artırır mıydı?
:::

::: gorev Gerçek deney · Atomic adımını koştur, telemetride yakala
Üç işlevi birleştir. Alttaki `calistir` satırı gerçek deneyi başlatır; silme. Koşu, önceden onaylanmış `pafta-linux-lab` konteynerini `--network none`, `no-new-privileges`, 512 MB bellek ve 256 pid sınırıyla açar. İçinde önce bir meşru gürültü grubu (`cat ~/.bashrc`, `ls`, dosyaya yazma), sonra dört seçili Atomic adımı strace altında koşar: `~/.bashrc`'ye ekleme (T1546.004), `/etc/cron.d/` altına yazma (T1053.003), `/etc/passwd` okuma (T1087.001), bash geçmişini silme (T1070.003). Konteyner içindeki güvenilir ayrıştırıcı ham strace'i normalleştirilmiş olaylara çevirir ve her olayı saldırı/iyi-huylu diye etiketler. Senin `olay_sinifla`'n telemetriyi sınıflar, `atomik_oku`'n dört tanımı okur, `kural_uygula`'n kalıcılık kuralını (yön `yaz` + kabuk/cron hedefi) sınıflı olaylara uygular. Lab, kuralının saldırı yazımlarını yakaladığını (TP) ve meşru okumada yanlış pozitif vermediğini (FP=0) ölçer; karşılaştırma için yalnız hedefe bakan 'saf' kuralın meşru okumada yanıldığını gösterir. Konteyner `--rm` ile atılır; Run deneme kanıtı, Check kabul kanıtı yazar.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def olay_sinifla(olaylar):
    out = []
    for e in olaylar:
        if e["cagri"] == "execve":
            out.append({"comm": e["comm"], "yon": "calistir", "hedef": e["argv"][0]})
        else:
            out.append({"comm": e["comm"], "yon": "yaz", "hedef": e["yol"]})
    return out

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
import re
def atomik_oku(yaml_metni):
    teknik = re.search(r"attack_technique:\s*(\S+)", yaml_metni).group(1)
    out = []
    for blok in re.split(r"(?m)^- name:\s*", yaml_metni)[1:]:
        ad = blok.splitlines()[0].strip()
        out.append({"teknik": teknik, "ad": ad})
    return out

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def kural_uygula(sinifli, kural):
    out = []
    for e in sinifli:
        for alan, degerler in kural["secim"].items():
            if alan == "hedef_icerir" and any(d in e["hedef"] for d in degerler):
                out.append({"kural": kural["id"], "comm": e["comm"], "yon": e["yon"], "hedef": e["hedef"]})
    return out

from purple_tespit_lab import calistir
calistir(olay_sinifla, atomik_oku, kural_uygula)
```

```solution
import re
YAZMA_BAYRAK = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC")
CAGRILAR = ("execve", "openat", "chmod", "fchmodat", "renameat2", "unlinkat")
GURULTU_ON = ("/usr/lib", "/lib", "/usr/bin", "/proc", "/sys", "/etc/ld", "/dev")
def gurultu_mu(yol):
    return any(yol.startswith(p) for p in GURULTU_ON) or yol.endswith(".so") or ".so." in yol
def olay_sinifla(olaylar):
    if not isinstance(olaylar, list):
        raise ValueError("olaylar listesi")
    out = []
    try:
        for e in olaylar:
            cagri, comm = e["cagri"], e["comm"]
            if cagri not in CAGRILAR or not isinstance(comm, str) or not comm:
                raise ValueError("olay alanı")
            bayrak = e.get("bayrak") or []
            if not isinstance(bayrak, list) or any(not isinstance(b, str) for b in bayrak):
                raise ValueError("bayrak")
            if cagri == "execve":
                argv = e.get("argv")
                if not isinstance(argv, list) or not argv or any(not isinstance(a, str) for a in argv):
                    raise ValueError("argv")
                yon, hedef = "calistir", argv[0]
            else:
                yol = e.get("yol")
                if not isinstance(yol, str) or not yol:
                    raise ValueError("yol")
                hedef = yol
                if cagri == "openat":
                    yon = "yaz" if any(b in bayrak for b in YAZMA_BAYRAK) else "oku"
                else:
                    yon = "yaz"
            if yon != "calistir" and gurultu_mu(hedef):
                continue
            out.append({"comm": comm, "yon": yon, "hedef": hedef})
    except (KeyError, TypeError, AttributeError):
        raise ValueError("bozuk olay")
    return out

def atomik_oku(yaml_metni):
    if not isinstance(yaml_metni, str) or not yaml_metni.strip():
        raise ValueError("yaml")
    m = re.search(r"(?m)^attack_technique:\s*(\S+)", yaml_metni)
    teknik = m.group(1).strip().strip('"') if m else None
    if not teknik or not re.fullmatch(r"T\d{4}(\.\d{3})?", teknik):
        raise ValueError("teknik")
    out = []
    for blok in re.split(r"(?m)^- name:", yaml_metni)[1:]:
        ad = blok.splitlines()[0].strip().strip('"')
        g = re.search(r"(?m)^\s*auto_generated_guid:\s*(\S+)", blok)
        guid = g.group(1).strip() if g else None
        if not ad or not guid or not re.fullmatch(r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}", guid):
            raise ValueError("test başlığı ya da guid")
        yukseltme = bool(re.search(r"(?m)^\s*elevation_required:\s*true", blok))
        c = re.search(r"(?m)^(?P<ind>[ \t]*)command:[ \t]*\|[ \t]*\n(?P<govde>(?:(?P=ind)[ \t]+.*\n?)+)", blok)
        if not c:
            raise ValueError("komut")
        satirlar = [s.strip() for s in c.group("govde").splitlines() if s.strip()]
        out.append({"teknik": teknik, "ad": ad, "guid": guid, "yukseltme": yukseltme, "komut": satirlar})
    if not out:
        raise ValueError("test yok")
    if len({t["guid"] for t in out}) != len(out):
        raise ValueError("yinelenen guid")
    return sorted(out, key=lambda t: t["guid"])

def kural_uygula(sinifli, kural):
    if not isinstance(kural, dict) or not isinstance(kural.get("id"), str) or not kural["id"]:
        raise ValueError("kural id")
    if kural.get("kosul") not in ("hepsi", "herhangi"):
        raise ValueError("koşul")
    secim = kural.get("secim")
    if not isinstance(secim, dict) or not secim:
        raise ValueError("seçim")
    for alan, degerler in secim.items():
        if alan not in ("comm", "yon", "hedef_icerir") or not isinstance(degerler, list) or not degerler \
                or any(not isinstance(d, str) or not d for d in degerler):
            raise ValueError("seçim alanı")
    if not isinstance(sinifli, list):
        raise ValueError("sınıflı olaylar listesi")
    hepsi = kural["kosul"] == "hepsi"
    out = []
    for e in sinifli:
        if not isinstance(e, dict) or e.get("yon") not in ("oku", "yaz", "calistir") \
                or not isinstance(e.get("comm"), str) or not isinstance(e.get("hedef"), str):
            raise ValueError("sınıflı olay alanı")
        sonuc = []
        for alan, degerler in secim.items():
            if alan == "comm":
                sonuc.append(e["comm"] in degerler)
            elif alan == "yon":
                sonuc.append(e["yon"] in degerler)
            else:
                sonuc.append(any(d in e["hedef"] for d in degerler))
        if (all(sonuc) if hepsi else any(sonuc)):
            out.append({"kural": kural["id"], "comm": e["comm"], "yon": e["yon"], "hedef": e["hedef"]})
    return out

from purple_tespit_lab import calistir
calistir(olay_sinifla, atomik_oku, kural_uygula)
```

```test
need('olay_sinifla');need('atomik_oku');need('kural_uygula')
from purple_tespit_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: referans/dinamik kod/özel öznitelik yok')
if not kod_koruma(src):stop()
def sinama1(f):
    try:
        def E(comm, cagri, yol=None, argv=None, bayrak=None):
            return {"pid": 1, "comm": comm, "cagri": cagri, "yol": yol, "argv": argv, "bayrak": bayrak or []}
        ol = [E("bash", "execve", argv=["/usr/bin/bash", "-c", "x"]),
              E("cat", "openat", yol="/usr/lib/libc.so.6", bayrak=["O_RDONLY"]),
              E("cat", "openat", yol="/root/.bashrc", bayrak=["O_RDONLY"]),
              E("bash", "openat", yol="/root/.bashrc", bayrak=["O_WRONLY", "O_APPEND"]),
              E("bash", "openat", yol="/etc/cron.d/x", bayrak=["O_WRONLY", "O_CREAT", "O_TRUNC"]),
              E("bash", "chmod", yol="/tmp/y"),
              E("bash", "unlinkat", yol="/root/.bash_history"),
              E("sh", "openat", yol="/proc/self/stat", bayrak=["O_RDONLY"]),
              E("app", "openat", yol="/opt/app/plugin.so", bayrak=["O_RDONLY"]),
              E("sh", "openat", yol="/home/u/.so.keep", bayrak=["O_RDONLY"])]
        bek = [{"comm": "bash", "yon": "calistir", "hedef": "/usr/bin/bash"},
               {"comm": "cat", "yon": "oku", "hedef": "/root/.bashrc"},
               {"comm": "bash", "yon": "yaz", "hedef": "/root/.bashrc"},
               {"comm": "bash", "yon": "yaz", "hedef": "/etc/cron.d/x"},
               {"comm": "bash", "yon": "yaz", "hedef": "/tmp/y"},
               {"comm": "bash", "yon": "yaz", "hedef": "/root/.bash_history"}]
        if f(ol) != bek:
            return False
        if f([]) != []:
            return False
        if f([E("x", "openat", yol="/a", bayrak=["O_RDWR"])]) != [{"comm": "x", "yon": "yaz", "hedef": "/a"}]:
            return False
        if f([E("x", "execve", argv=["/bin/ls", "/usr/lib/x"])]) != [{"comm": "x", "yon": "calistir", "hedef": "/bin/ls"}]:
            return False
        for a in ("x", None, [1], [{"cagri": "openat", "comm": "a"}], [{"cagri": "nope", "comm": "a", "yol": "/x"}],
                  [{"cagri": "openat", "comm": "", "yol": "/x"}], [{"cagri": "execve", "comm": "a", "argv": []}],
                  [{"cagri": "execve", "comm": "a", "argv": None}], [{"cagri": "execve", "comm": "a", "argv": [1]}],
                  [{"cagri": "openat", "comm": "a", "yol": None, "bayrak": []}],
                  [{"cagri": "openat", "comm": "a", "yol": "", "bayrak": []}],
                  [{"cagri": "openat", "comm": "a", "yol": "/x", "bayrak": "O_RDONLY"}],
                  [{"cagri": "openat", "comm": "a", "yol": "/x", "bayrak": [1]}]):
            try:
                f(a); return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
def sinama2(f):
    try:
        y = ("attack_technique: T1546.004\n"
             "atomic_tests:\n"
             "- name: Ikinci\n"
             "  auto_generated_guid: bbbbbbbb-2222-3333-4444-555555555555\n"
             "  executor:\n    command: |\n      echo b >> ~/.bashrc\n      chmod 600 ~/.bashrc\n    name: sh\n"
             "- name: Birinci\n"
             "  auto_generated_guid: aaaaaaaa-2222-3333-4444-555555555555\n"
             "  executor:\n    elevation_required: true\n    command: |\n      echo a > /etc/cron.d/x\n    name: sh\n")
        r = f(y)
        if [t["guid"][0] for t in r] != ["a", "b"]:
            return False
        if r[0] != {"teknik": "T1546.004", "ad": "Birinci", "guid": "aaaaaaaa-2222-3333-4444-555555555555",
                    "yukseltme": True, "komut": ["echo a > /etc/cron.d/x"]}:
            return False
        if r[1]["yukseltme"] is not False or r[1]["komut"] != ["echo b >> ~/.bashrc", "chmod 600 ~/.bashrc"]:
            return False
        tek = f("attack_technique: T1053\natomic_tests:\n- name: X\n  auto_generated_guid: "
                "cccccccc-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n    name: sh\n")
        if tek[0]["teknik"] != "T1053":
            return False
        elf = ("attack_technique: T1001\natomic_tests:\n- name: X\n  auto_generated_guid: "
               "cccccccc-1111-2222-3333-444444444444\n  executor:\n    elevation_required: false\n"
               "    command: |\n      echo x\n    name: sh\n")
        if f(elf)[0]["yukseltme"] is not False:
            return False
        dup = ("attack_technique: T1001\natomic_tests:\n"
               "- name: A\n  auto_generated_guid: dddddddd-2222-3333-4444-555555555555\n"
               "  executor:\n    command: |\n      echo a\n    name: sh\n"
               "- name: B\n  auto_generated_guid: dddddddd-2222-3333-4444-555555555555\n"
               "  executor:\n    command: |\n      echo b\n    name: sh\n")
        bosad = ("attack_technique: T1001\natomic_tests:\n- name: \n  auto_generated_guid: "
                 "ffffffff-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n    name: sh\n")
        for bad in ("", "   ", "atomic_tests:\n- name: X\n", "attack_technique: BAD\natomic_tests:\n- name: X\n",
                    "attack_technique: T1\natomic_tests:\n- name: X\n  executor:\n    command: |\n      echo x\n",
                    "attack_technique: T1546.04\natomic_tests:\n- name: X\n  auto_generated_guid: "
                    "11111111-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n",
                    "attack_technique: T1546.004\natomic_tests:\n- name: X\n  auto_generated_guid: "
                    "AAAAAAAA-2222-3333-4444-555555555555\n  executor:\n    command: |\n      echo x\n",
                    bosad,
                    "attack_technique: T1546.004\natomic_tests:\n- name: X\n  auto_generated_guid: nope\n"
                    "  executor:\n    command: |\n      echo x\n",
                    "attack_technique: T1546.004\natomic_tests:\n- name: X\n  auto_generated_guid: "
                    "eeeeeeee-2222-3333-4444-555555555555\n  executor:\n    name: sh\n", dup, 5, None):
            try:
                f(bad); return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
def sinama3(f):
    try:
        S = [{"comm": "cat", "yon": "oku", "hedef": "/root/.bashrc"},
             {"comm": "bash", "yon": "yaz", "hedef": "/root/.bashrc"},
             {"comm": "bash", "yon": "yaz", "hedef": "/etc/cron.d/x"},
             {"comm": "grep", "yon": "oku", "hedef": "/etc/passwd"}]
        kal = {"id": "k1", "kosul": "hepsi", "secim": {"yon": ["yaz"], "hedef_icerir": [".bashrc", "/etc/cron.d/"]}}
        r = f(S, kal)
        if [x["hedef"] for x in r] != ["/root/.bashrc", "/etc/cron.d/x"] or any(x["kural"] != "k1" for x in r):
            return False
        saf = {"id": "s", "kosul": "herhangi", "secim": {"hedef_icerir": [".bashrc", "/etc/passwd"]}}
        if [x["hedef"] for x in f(S, saf)] != ["/root/.bashrc", "/root/.bashrc", "/etc/passwd"]:
            return False
        cg = {"id": "c", "kosul": "hepsi", "secim": {"comm": ["grep"], "yon": ["oku"]}}
        if [x["comm"] for x in f(S, cg)] != ["grep"]:
            return False
        if f([], kal) != []:
            return False
        if f(S, {"id": "z", "kosul": "herhangi", "secim": {"comm": ["yok"]}}) != []:
            return False
        for a in ((S, {"kosul": "hepsi", "secim": {"yon": ["yaz"]}}), (S, {"id": "", "kosul": "hepsi", "secim": {"yon": ["yaz"]}}),
                  (S, {"id": "x", "kosul": "belki", "secim": {"yon": ["yaz"]}}), (S, {"id": "x", "kosul": "hepsi", "secim": {}}),
                  (S, {"id": "x", "kosul": "hepsi", "secim": {"nope": ["a"]}}), (S, {"id": "x", "kosul": "hepsi", "secim": {"yon": []}}),
                  (S, {"id": "x", "kosul": "hepsi", "secim": {"yon": [1]}}), (S, {"id": "x", "kosul": "hepsi", "secim": {"yon": [""]}}),
                  ("x", kal), ([{"comm": "a", "yon": "ucmak", "hedef": "/x"}], kal), ([{"comm": "a", "hedef": "/x"}], kal),
                  ([{"yon": "yaz", "hedef": "/x"}], kal), ([{"comm": "a", "yon": "yaz"}], kal)):
            try:
                f(*a); return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
tamam=sinama1(olay_sinifla) and sinama2(atomik_oku) and sinama3(kural_uygula)
ok(tamam,"üç işlev gizli verilerle doğru")
def _bos(o):
    try:
        return olay_sinifla(o)
    except ValueError:
        return []
for ad, mut in [("sırasız", lambda o: list(reversed(olay_sinifla(o)))),
                ("gürültü de", lambda o: olay_sinifla(o) + [{"comm": "x", "yon": "oku", "hedef": "/usr/lib/a"}]),
                ("bozukta boş", _bos)]:
    ok(not sinama1(mut), "mutant reddedildi: " + ad)
def _bos(y):
    try:
        return atomik_oku(y)
    except ValueError:
        return []
for ad, mut in [("sırasız", lambda y: atomik_oku(y)[::-1]),
                ("yükseltme ters", lambda y: [dict(t, yukseltme=not t["yukseltme"]) for t in atomik_oku(y)]),
                ("bozukta boş", _bos)]:
    ok(not sinama2(mut), "mutant reddedildi: " + ad)
def _bos(s, k):
    try:
        return kural_uygula(s, k)
    except ValueError:
        return []
for ad, mut in [("sırasız", lambda s, k: kural_uygula(s, k)[::-1]),
                ("herhangi gibi", lambda s, k: kural_uygula(s, dict(k, kosul="herhangi"))),
                ("bozukta boş", _bos)]:
    ok(not sinama3(mut), "mutant reddedildi: " + ad)
if not tamam:stop()
k=calistir(olay_sinifla,atomik_oku,kural_uygula,kabul=True)
eq(k['kaynak'],'gercek','gerçek strace telemetrisi')
ok(k['kabul'],'gerçek kabul: sınıflama, atomic okuma ve kural referansla aynı')
ok(k['cleanup'],'yalnız kendi başlattığı konteyner kapandı')
eq((k['kural_tp'],k['kural_fp']),(2,0),'kalıcılık kuralı iki yazımı yakaladı, yanlış pozitif yok')
ok(k['saf_fp']>=1,'saf kural meşru okumada yanlış pozitif verdi (hata vitrini)')
eq(k['atomik_teknikler'],['T1053.003','T1070.003','T1087.001','T1546.004'],'dört atomic teknik okundu')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tespit_lab import hazirla
hazirla()
```

```hint
Önceki üç işlevi aynen birleştir. Kalıcılık bir yazmadır: kuralın `yon` alanı olmadan meşru `cat ~/.bashrc` okuması da eşleşir.
```
:::

::: anlat Sınır
Bu ders seçili Atomic Red Team kalıcılık adımlarını izole bir `--network none` konteynerinde gerçekten koşturur, strace telemetrisini normalleştirir, atomic tanımını okur ve bir Sigma benzeri kuralla kalıcılık yazımını yakalayıp meşru okumada yanlış pozitif vermediğini ölçer. Gerçek bir EDR'yi, auditd/Sysmon telemetrisini, systemd servis kalıcılığını (konteynerde systemd yoktur), Windows tarafını, cron işinin tetiklenmesini ve bu TP/FP oranlarının başka ortamlara genellenmesini kapsamaz.
:::
