---
id: pu16
title: Linux Yetki Yükseltme Temelleri · Kayıtlı Kanıtla Karar Analizi
summary: CPTS odaklı SUID/SGID, sudo, cron/systemd, PATH ve capability kayıtlarını saldırı çalıştırmadan kanıt–önkoşul–risk–düzeltme bulgularına dönüştürmek; yanlış pozitifleri ve güvenli sınırları ayırmak.
timeout: 60
---

::: anlat Saldırıyı değil, kararın kanıtını üret
Bu ders **güvenli, yerel ve çevrimdışı** bir kayıt analizidir. `pu16_lab.json` içindeki bütün `find`, `stat`, `id`, `getcap`, `sudo -l`, `crontab`, systemd ve `PATH` çıktıları sentetiktir. Ders SUID/SGID veya sudo istismarı yapmaz; komut çalıştırmaz; setuid/capability, sahiplik, izin, sudo, cron ya da systemd yapılandırması değiştirmez. Komut adları yalnız incelenen veridir.

CPTS bakışındaki “daha yüksek yetkiye giden yol nerede?” sorusunu savunma raporuna çeviriyoruz. Her bulgu altı alan taşır:

```text
{"id", "kanit", "onkosul", "risk", "oncelik", "duzeltme"}
```

`oncelik` yalnız `kritik`, `yuksek` veya `orta` olur. **SUID bitinin bulunması otomatik kritik bulgu değildir.** Kullanıcı, hedef hesap/grup, çalıştırılabilirlik, yazma veya üst dizinden değiştirme koşulu birlikte okunur. Benzer biçimde `NOPASSWD`, wildcard ve capability adı da tek başına sonuç değildir.

PU12'deki genel “şüpheli satırı listele” yaklaşımını burada karar kanıtına dönüştürüyoruz. BS33'teki `e/p/i` ayrımı korunur; bu ders ayrıca dosya ile süreç capability'sini ve kullanıcı ad alanının güvenli sınırını ayırır.
:::

::: anlat Fixture ve kanıt sözleşmesi
Her görevin hazırlığı `sandbox/linux_privesc_lab.py` ile aynı JSON'u geçici çalışma klasörüne `pu16_lab.json` olarak kopyalar. Yardımcı yalnız JSON okur ve kopyalar; alt süreç, ağ veya sistem API'si kullanmaz.

```python norun
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))
print(v["identity"]["evidence"])
```

`files`, kayıtlı `find`/`stat` çıktısının karar alanlarını; `file_capabilities` ve `process_capabilities`, dosya ile süreç ayrımını; `sudo_rules`, sudoers eşleşmesini; `jobs` ve `path_entries`, zamanlanmış işin komut/PATH bağlamını taşır. `evidence` ile biten metinler rapor kanıtıdır. Alanlar gerçek sistem iddiası değil, sabit laboratuvar sözleşmesidir.
:::

::: tahmin Hangi SUID satırı eyleme dönük bulgudur?
```python
kayitlar = [
    {"yol": "/usr/bin/passwd", "suid": True, "sahip": "root", "yazabilir": False},
    {"yol": "/opt/root-report", "suid": True, "sahip": "root", "yazabilir": True},
    {"yol": "/opt/user-tool", "suid": True, "sahip": "analyst", "yazabilir": True},
]
print([k["yol"] for k in kayitlar
       if k["suid"] and k["sahip"] == "root" and k["yazabilir"]])
```

???

Yalnız `['/opt/root-report']` yazdırılır. `/usr/bin/passwd` envanterde önemli ama bu kayıtta çağıranın değiştirme önkoşulu yoktur; `/opt/user-tool` zaten çağıran kullanıcıya aittir ve yeni bir kullanıcı sınırı vermez. Bu üçlü, “SUID buldum” ile “kontrol edilebilir root SUID dosyası” arasındaki farktır.
:::

::: gorev 1 · SUID/SGID ve capability güvenlik sınırları
İki işlev yaz: `dosya_bulgulari(v)` ve `capability_bulgulari(v)`. Her ikisi de yukarıdaki altı alanlı sözlüklerin `id` sıralı listesini döndürür.

**Dosya kararları:**

- Yalnız `kind == "regular"`, `executable` doğru ve SUID veya SGID taşıyan kayıtları değerlendir. Çağıran `caller_write` veya `parent_replace` ile içeriği/dosyayı değiştiremiyorsa bulgu üretme.
- SUID sahibi `identity.user` dışında bir hesapsa `SUID:<yol>` üret. Sahip `root` ise öncelik `kritik`, başka hesap ise `yuksek`; risk metninde hedef hesabı belirt. Kendi hesabına SUID yeni sınır değildir.
- SGID grubu çağıranın mevcut `groups` kümesinde yoksa `SGID:<yol>` ve `yuksek` üret. Zaten üye olunan grup yeni etkin grup kazandırmaz.
- Kanıt `find_evidence` ve `stat_evidence` alanlarını; önkoşul yazma/değiştirme ve çalıştırma koşulunu içersin. Düzeltme biti kaldırmayı veya sahiplik/izinleri en az yetkiye indirmeyi söylesin; bu işlemleri çalıştırma.

**Capability kararları:**

- Dosyalarda düzenli ve çalıştırılabilir kayıtlarda yalnız `cap_setuid`, `cap_sys_admin`, `cap_dac_override`, `cap_sys_ptrace` için `e` veya `p` ara. Her capability için `CAP-DOSYA:<yol>:<ad>` üret. `cap_net_raw` ve yalnız `i` bu risk kümesinde değildir.
- `cap_setuid`/`cap_sys_admin` etkinse `kritik`, diğer iki riskli capability etkinse `yuksek`; yalnız `p` varsa bir basamak düşür (`kritik → yuksek`, `yuksek → orta`).
- Süreçlerde yalnız `user == identity.user` ve `namespace == "initial"` kayıtlarını değerlendir. `effective` veya `permitted` kümelerindeki aynı riskli capability'ler için `CAP-SUREC:<pid>:<ad>` üret; effective yoksa yine bir basamak düşür. Aynı PID/capability için tek bulgu olsun.
- Kullanıcı ad alanındaki (`namespace == "user"`) capability'yi ana sistem yetkisi sayma. Başka kullanıcının süreci de çağıranın mevcut yetkisi değildir. `CapBnd` tek başına kazanılmış yetki değildir ve bu sözleşmede bulgu üretmez.

```starter
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))

def dosya_bulgulari(v):
    return []

def capability_bulgulari(v):
    return []

print(dosya_bulgulari(v))
print(capability_bulgulari(v))
```

```test
import copy
need("dosya_bulgulari"); need("capability_bulgulari")
d = dosya_bulgulari(v)
c = capability_bulgulari(v)
eq([(x["id"], x["oncelik"]) for x in d], [
    ("SGID:/opt/pafta/legacy-sgid", "yuksek"),
    ("SUID:/opt/pafta/replace-root", "kritik"),
    ("SUID:/opt/pafta/root-report", "kritik"),
], "SUID/SGID sahip, grup ve değiştirme sınırları")
eq([(x["id"], x["oncelik"]) for x in c], [
    ("CAP-DOSYA:/opt/pafta/identity:cap_setuid", "kritik"),
    ("CAP-DOSYA:/opt/pafta/permitted:cap_setuid", "yuksek"),
    ("CAP-DOSYA:/opt/pafta/reader:cap_dac_override", "yuksek"),
    ("CAP-SUREC:620:cap_dac_override", "orta"),
    ("CAP-SUREC:730:cap_sys_admin", "kritik"),
], "dosya/süreç, e/p ve kullanıcı ad alanı ayrımı")
for x in d + c:
    eq(set(x), {"id", "kanit", "onkosul", "risk", "oncelik", "duzeltme"}, "rapor sözleşmesi")
    ok(all(x[k] for k in ("kanit", "onkosul", "risk", "duzeltme")), "her bulgu gerekçeli")
x = copy.deepcopy(v)
x["files"][1]["owner"] = "analyst"
eq([b["id"] for b in dosya_bulgulari(x) if "root-report" in b["id"]], [], "kendi kullanıcısına SUID yeni sınır değil")
x = copy.deepcopy(v)
x["files"][1]["caller_write"] = False
eq([b["id"] for b in dosya_bulgulari(x) if "root-report" in b["id"]], [], "salt okunur root SUID otomatik kritik değil")
x["files"][1]["parent_replace"] = True
eq([b["id"] for b in dosya_bulgulari(x) if "root-report" in b["id"]], ["SUID:/opt/pafta/root-report"], "üst dizinden değiştirme eşdeğer önkoşul")
x = copy.deepcopy(v)
x["files"][3]["group"] = "operators"
eq([b["id"] for b in dosya_bulgulari(x) if b["id"].startswith("SGID:")], [], "zaten üye olunan SGID grubu yeni yetki değil")
x = copy.deepcopy(v)
x["file_capabilities"][1]["capabilities"]["cap_dac_override"] = "i"
eq([b["id"] for b in capability_bulgulari(x) if "reader" in b["id"]], [], "yalnız inheritable dosya capability bulgu değil")
x = copy.deepcopy(v)
x["process_capabilities"][2]["effective"] = ["cap_dac_override"]
eq([b["oncelik"] for b in capability_bulgulari(x) if b["id"] == "CAP-SUREC:620:cap_dac_override"], ["yuksek"], "effective permitted'dan yüksek öncelikli")
x = copy.deepcopy(v)
x["process_capabilities"][3]["namespace"] = "user"
eq([b["id"] for b in capability_bulgulari(x) if b["id"] == "CAP-SUREC:730:cap_sys_admin"], [], "kullanıcı ad alanı ana sistem yetkisi değil")
x = copy.deepcopy(v)
x["files"][1]["executable"] = False
eq([b["id"] for b in dosya_bulgulari(x) if "root-report" in b["id"]], [], "çalıştırılamayan düz dosya bu yol için bulgu değil")
```

```solution
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))

ALANLAR = ("id", "kanit", "onkosul", "risk", "oncelik", "duzeltme")
RISKLI_CAP = {"cap_setuid", "cap_sys_admin", "cap_dac_override", "cap_sys_ptrace"}

def rapor(kimlik, kanit, onkosul, risk, oncelik, duzeltme):
    return dict(zip(ALANLAR, (kimlik, kanit, onkosul, risk, oncelik, duzeltme)))

def dosya_bulgulari(v):
    kimlik = v["identity"]
    sonuc = []
    for f in v["files"]:
        if f["kind"] != "regular" or not f["executable"] or not (f["suid"] or f["sgid"]):
            continue
        if not (f["caller_write"] or f["parent_replace"]):
            continue
        kanit = [f["find_evidence"], f["stat_evidence"]]
        kosul = "Çağıran dosyayı veya üst dizin üzerinden yerine koyacağı dosyayı değiştirebilmeli ve dosya çalıştırılabilir olmalı."
        if f["suid"] and f["owner"] != kimlik["user"]:
            kok = f["owner"] == "root"
            sonuc.append(rapor(
                f'SUID:{f["path"]}', kanit, kosul,
                f'Değiştirilen SUID program çalıştığında {f["owner"]} kullanıcı bağlamına geçiş riski.',
                "kritik" if kok else "yuksek",
                "Gereksiz SUID bitini kaldır; dosya ve üst dizin sahipliğini/yazma izinlerini en az yetkiye göre düzelt."))
        if f["sgid"] and f["group"] not in kimlik["groups"]:
            sonuc.append(rapor(
                f'SGID:{f["path"]}', kanit, kosul,
                f'Değiştirilen SGID program çalıştığında {f["group"]} grubunun yetkilerine geçiş riski.',
                "yuksek",
                "Gereksiz SGID bitini kaldır; grup yazmasını ve üst dizin değiştirme hakkını sınırla."))
    return sorted(sonuc, key=lambda b: b["id"])

def cap_oncelik(ad, etkin):
    kritik = ad in {"cap_setuid", "cap_sys_admin"}
    return ("kritik" if kritik else "yuksek") if etkin else ("yuksek" if kritik else "orta")

def capability_bulgulari(v):
    sonuc = []
    for f in v["file_capabilities"]:
        if f["kind"] != "regular" or not f["executable"]:
            continue
        for ad, bayraklar in f["capabilities"].items():
            if ad not in RISKLI_CAP or not ({"e", "p"} & set(bayraklar)):
                continue
            etkin = "e" in bayraklar
            sonuc.append(rapor(
                f'CAP-DOSYA:{f["path"]}:{ad}', [f["evidence"]],
                "Kullanıcı bu çalıştırılabilir dosyayı çalıştırabilmeli; p bayrağı programın capability'yi etkinleştirmesine izin verir.",
                f'{ad} dosya üzerinden aşırı dosya, kimlik veya süreç yetkisi riski.',
                cap_oncelik(ad, etkin),
                "Beklenen capability envanteriyle karşılaştır; gereksiz dosya capability'sini kaldır veya kapsamını daralt."))
    for p in v["process_capabilities"]:
        if p["user"] != v["identity"]["user"] or p["namespace"] != "initial":
            continue
        for ad in sorted(set(p["effective"]) | set(p["permitted"])):
            if ad not in RISKLI_CAP:
                continue
            etkin = ad in p["effective"]
            sonuc.append(rapor(
                f'CAP-SUREC:{p["pid"]}:{ad}', [p["evidence"]],
                "Süreç çağıran kullanıcıya ait ve initial kullanıcı ad alanında olmalı; effective/permitted küme birlikte okunmalı.",
                f'{ad} bu kullanıcı sürecinde ' + ("şu an etkin." if etkin else "etkinleştirilebilir permitted yetkidir."),
                cap_oncelik(ad, etkin),
                "Sürecin iş gerekçesini doğrula; gereksiz capability'yi kaldır ve hizmeti en az yetkili hesap/ad alanıyla sınırla."))
    return sorted(sonuc, key=lambda b: b["id"])

print(dosya_bulgulari(v))
print(capability_bulgulari(v))
```

```hint
Önce yanlış pozitifleri ele: dosya türü, çalıştırılabilirlik, aynı kullanıcı/grup ve değiştirme önkoşulu. Capability önceliğini tek bir yardımcıda belirle; `e` yoksa bir basamak düşür.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from linux_privesc_lab import hazirla
hazirla()
```
:::

::: gorev 2 · sudo kullanıcı/grup, kimlik doğrulama ve argüman sınırı
`sudo_bulgulari(v)` işlevini yaz. Önce kuralın çağırana uygulanıp uygulanmadığını denetle: `principal == identity.user` veya `principal` biçimi `%grup` olup grup `identity.groups` içinde olmalı. Başka kullanıcı ve üye olunmayan grup kurallarını raporlama.

Ardından yalnız **argümanı geniş** kuralları bulgula: `arguments == "*"` tamamen serbesttir; içinde `*` olan diğer değerler wildcard sınırıdır. `/usr/bin/systemctl restart pafta-agent` gibi tamamen sabit komut+argüman satırı bu görevde bulgu değildir. Wildcard'ın varlığı hangi alt komutların veya kaçışların mümkün olduğunu kanıtlamaz; `dangerous_if_unrestricted`, bu fixture'da komutun serbest argümanla tehlikeli alt işlev taşıdığı önceden doğrulanmış karar alanıdır.

Bulgu kimliği `SUDO:<rule_id>` olsun. Kanıt `evidence`; önkoşul eşleşen principal, `runas_users`/`runas_groups`, `auth`, argüman ve varsa `NOEXEC` bilgisini içersin.

- Hedef kullanıcı veya grup `root` içeriyorsa root sınırı vardır. Serbest argüman + tehlikeli komut + `NOPASSWD` + `NOEXEC` yoksa `kritik`; parola istenmesi veya `NOEXEC` varsa `yuksek`. `NOEXEC` tam güvenlik sınırı değildir, kuralı eleme.
- Root hedefli, tehlikeli-alt-işlev alanı false olan wildcard kuralı `orta` üretir; argüman sınırının genişliği yine düzeltilmelidir.
- Root olmayan hedefte serbest argüman + tehlikeli komut `NOPASSWD` ise `yuksek`, parolalıysa `orta`; diğer wildcard kuralları `orta` üretir.
- Risk metni hedef kullanıcı/grup ve parolasızlık/parola durumunu açıklasın. Düzeltme sabit komut ve tam argüman listesi, gerekiyorsa ayrı sarmalayıcı, en az ayrıcalıklı hedef ve kimlik doğrulama önersin; kuralı değiştirmeye çalışmasın.

```starter
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))

def sudo_bulgulari(v):
    return []

print(sudo_bulgulari(v))
```

```test
import copy
need("sudo_bulgulari")
b = sudo_bulgulari(v)
eq([(x["id"], x["oncelik"]) for x in b], [
    ("SUDO:S1", "kritik"),
    ("SUDO:S2", "yuksek"),
    ("SUDO:S3", "yuksek"),
    ("SUDO:S6", "yuksek"),
    ("SUDO:S7", "orta"),
], "kullanıcı/grup, root hedefi, parola, NOEXEC ve argüman kararları")
for x in b:
    eq(set(x), {"id", "kanit", "onkosul", "risk", "oncelik", "duzeltme"}, "rapor sözleşmesi")
    ok("NOPASSWD" in x["onkosul"] or "PASSWD" in x["onkosul"], "kimlik doğrulama kanıtı korunur")
x = copy.deepcopy(v); x["identity"]["groups"] = ["analyst"]
eq([b["id"] for b in sudo_bulgulari(x)], ["SUDO:S1", "SUDO:S2", "SUDO:S6", "SUDO:S7"], "üye olunmayan %operators kuralı uygulanmaz")
x = copy.deepcopy(v); x["sudo_rules"][0]["arguments"] = "/var/log/pafta/app.log"
eq([b["id"] for b in sudo_bulgulari(x) if b["id"] == "SUDO:S1"], [], "tam sabit argüman wildcard değildir")
x = copy.deepcopy(v); x["sudo_rules"][0]["auth"] = "PASSWD"
eq([b["oncelik"] for b in sudo_bulgulari(x) if b["id"] == "SUDO:S1"], ["yuksek"], "parola koşulu önceliği düşürür")
x = copy.deepcopy(v); x["sudo_rules"][0]["noexec"] = True
eq([b["oncelik"] for b in sudo_bulgulari(x) if b["id"] == "SUDO:S1"], ["yuksek"], "NOEXEC kuralı elemez")
x = copy.deepcopy(v); x["sudo_rules"][0]["runas_users"] = ["svc-backup"]
eq([b["oncelik"] for b in sudo_bulgulari(x) if b["id"] == "SUDO:S1"], ["yuksek"], "root dışı hedef root kritik değildir")
x = copy.deepcopy(v); x["sudo_rules"][2]["auth"] = "PASSWD"
eq([b["oncelik"] for b in sudo_bulgulari(x) if b["id"] == "SUDO:S3"], ["orta"], "root dışı parolalı kural")
x = copy.deepcopy(v); x["sudo_rules"][6]["arguments"] = "status pafta-agent"
eq([b["id"] for b in sudo_bulgulari(x) if b["id"] == "SUDO:S7"], [], "sabit systemctl argümanı yanlış pozitif üretmez")
```

```solution
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))

def rapor(kimlik, kanit, onkosul, risk, oncelik, duzeltme):
    return {"id": kimlik, "kanit": kanit, "onkosul": onkosul, "risk": risk,
            "oncelik": oncelik, "duzeltme": duzeltme}

def sudo_bulgulari(v):
    kimlik = v["identity"]
    sonuc = []
    for r in v["sudo_rules"]:
        principal = r["principal"]
        eslesti = principal == kimlik["user"] or (principal.startswith("%") and principal[1:] in kimlik["groups"])
        if not eslesti:
            continue
        arg = r["arguments"]
        serbest = arg == "*"
        wildcard = "*" in arg
        if not wildcard:
            continue
        hedefler = [f'kullanıcı={u}' for u in r["runas_users"]] + [f'grup={g}' for g in r["runas_groups"]]
        root = "root" in r["runas_users"] or "root" in r["runas_groups"]
        nopasswd = r["auth"] == "NOPASSWD"
        if root and r["dangerous_if_unrestricted"]:
            oncelik = "kritik" if serbest and nopasswd and not r["noexec"] else "yuksek"
        elif root:
            oncelik = "orta"
        elif serbest and r["dangerous_if_unrestricted"]:
            oncelik = "yuksek" if nopasswd else "orta"
        else:
            oncelik = "orta"
        hedef = ", ".join(hedefler)
        kosul = (f'{principal} kuralı çağırana eşleşmeli; hedef {hedef}; auth={r["auth"]}; '
                 f'arguments={arg}; NOEXEC={r["noexec"]}.')
        sonuc.append(rapor(
            f'SUDO:{r["rule_id"]}', [r["evidence"]], kosul,
            f'{hedef} bağlamında geniş argüman yüzeyi; kimlik doğrulama={r["auth"]}, root_siniri={root}.',
            oncelik,
            "Kuralı tek komut ve tam argüman listesiyle sınırla; gerekiyorsa dar bir sarmalayıcı ve root olmayan hedef kullan."))
    return sorted(sonuc, key=lambda b: b["id"])

print(sudo_bulgulari(v))
```

```hint
Principal eşleşmesini ve geniş argümanı önce süz. Önceliği tek karar zincirinde hesapla; root, tamamen serbest argüman, tehlikeli alt işlev, `NOPASSWD` ve `NOEXEC` alanlarını birbirine karıştırma.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from linux_privesc_lab import hazirla
hazirla()
```
:::

::: gorev 3 · cron/systemd betiği ve PATH hijack önkoşulları
`zamanli_gorev_bulgulari(v)` işlevini yaz. Yalnız `trigger_active` doğru ve `user` çağıranın kullanıcısından farklı olan işleri değerlendir. Bu derste root işi kritik/yüksek etki sınırını, başka bir hizmet hesabı ise aynı kurallarla kendi hesap sınırını temsil eder. Aynı kullanıcının crontab'ı yetki yükseltme değildir; inactive systemd kaydı da şu an tetiklenen yol değildir.

Her iş için şu bağımsız bulguları üret:

1. **Betik kontrolü:** `script` var ve `caller_script_write` veya `caller_parent_replace` doğruysa `IS:<job_id>:betik`, öncelik root için `kritik`, diğer hesap için `yuksek`. Mutlak komut yolu, betiğin kendisinin değiştirilemeyeceği anlamına gelmez.
2. **Yazılabilir PATH:** Komut yolu mutlak değilse işin `path` listesini sırayla `path_entries` içinde ara. `caller_write` doğru dizin için `IS:<job_id>:path-yazilabilir:<dizin>`, root için `kritik`, diğer hesap için `yuksek` üret. Aramada daha önce root'a ait salt-yazılır dizin bulunması, komut orada gerçekten bulunmadıkça sonraki yazılabilir dizini güvenli yapmaz; fixture'da kesin çözülen binary iddiası yoktur.
3. **Göreli/boş PATH:** Mutlak olmayan komutta `absolute == false` olan her dizin için `IS:<job_id>:path-goreceli:<dizin-veya-<bos>>` ve `orta` üret. `./tools` çalışma dizinine bağlıdır; boş bileşen de çalışma dizinini aramaya katar. Yazılabilirlik kanıtı olmadığı için bunlar kritik değil, belirsiz çalışma dizini riskidir.

Mutlak komutlu işlerde PATH hijack bulgusu üretme. Kök PATH dizinlerinin salt-yazılır olması göreli komut adını tek başına bulguya çevirmez. Her bulguda `jobs.evidence` ve ilgili PATH kaydının `evidence` alanı kanıt; aktif tetik, farklı kullanıcı, göreli komut ve yazma/değiştirme bilgisi önkoşul olsun. Düzeltmede mutlak yol, root'a ait salt-yazılır betik/dizinler, minimal PATH ve gereksiz zamanlanmış işin kaldırılması önerilsin; hiçbiri çalıştırılmasın.

```starter
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))

def zamanli_gorev_bulgulari(v):
    return []

print(zamanli_gorev_bulgulari(v))
```

```test
import copy
need("zamanli_gorev_bulgulari")
b = zamanli_gorev_bulgulari(v)
eq([(x["id"], x["oncelik"]) for x in b], [
    ("IS:J1:path-yazilabilir:/opt/shared/bin", "kritik"),
    ("IS:J2:betik", "kritik"),
    ("IS:J6:betik", "kritik"),
    ("IS:J8:path-goreceli:./tools", "orta"),
    ("IS:J9:path-goreceli:<bos>", "orta"),
], "aktif ayrıcalıklı iş, betik ve PATH kararları")
for x in b:
    eq(set(x), {"id", "kanit", "onkosul", "risk", "oncelik", "duzeltme"}, "rapor sözleşmesi")
    ok(len(x["kanit"]) >= 1 and x["onkosul"] and x["risk"] and x["duzeltme"], "gerekçeli bulgu")
x = copy.deepcopy(v); x["jobs"][0]["trigger_active"] = False
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J1:")], [], "inactive yol şu an tetiklenmez")
x = copy.deepcopy(v); x["jobs"][0]["user"] = "analyst"
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J1:")], [], "aynı kullanıcı yetki yükseltme sınırı değil")
x = copy.deepcopy(v); x["jobs"][0]["command_absolute"] = True
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J1:")], [], "mutlak komutta PATH araması yok")
x = copy.deepcopy(v); x["path_entries"][0]["caller_write"] = False
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J1:")], [], "PATH yazılabilir değilse J1 bulgusu kalmaz")
x = copy.deepcopy(v); x["jobs"][1]["caller_script_write"] = False
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"] == "IS:J2:betik"], [], "betik ve üst dizini değiştirilemiyor")
x["jobs"][1]["caller_parent_replace"] = True
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"] == "IS:J2:betik"], ["IS:J2:betik"], "üst dizinden betik değiştirme yakalanır")
x = copy.deepcopy(v); x["jobs"][0]["user"] = "svc-report"
eq([b["oncelik"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J1:")], ["yuksek"], "root olmayan hizmet hesabı kritik değil")
x = copy.deepcopy(v); x["jobs"][7]["path"] = ["/usr/bin", "./tools"]
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J8:")], ["IS:J8:path-goreceli:./tools"], "göreli bileşen listede sonradan da olsa raporlanır")
x = copy.deepcopy(v); x["jobs"][0]["path"] = ["", "/opt/shared/bin"]
eq([b["id"] for b in zamanli_gorev_bulgulari(x) if b["id"].startswith("IS:J1:")], ["IS:J1:path-goreceli:<bos>", "IS:J1:path-yazilabilir:/opt/shared/bin"], "aynı PATH iki bağımsız koşul üretebilir")
```

```solution
import json
v = json.load(open("pu16_lab.json", encoding="utf-8"))

def rapor(kimlik, kanit, onkosul, risk, oncelik, duzeltme):
    return {"id": kimlik, "kanit": kanit, "onkosul": onkosul, "risk": risk,
            "oncelik": oncelik, "duzeltme": duzeltme}

def zamanli_gorev_bulgulari(v):
    kullanici = v["identity"]["user"]
    dizinler = {p["directory"]: p for p in v["path_entries"]}
    sonuc = []
    for j in v["jobs"]:
        if not j["trigger_active"] or j["user"] == kullanici:
            continue
        root = j["user"] == "root"
        yuksek = "kritik" if root else "yuksek"
        ortak = f'İş aktif tetiklenmeli ve {j["user"]} hesabı çağırandan farklı olmalı; kaynak={j["source"]}.'
        if j["script"] and (j["caller_script_write"] or j["caller_parent_replace"]):
            sonuc.append(rapor(
                f'IS:{j["job_id"]}:betik', [j["evidence"]],
                ortak + " Çağıran betiği veya üst dizin üzerinden yerine koyacağı betiği değiştirebilmeli.",
                f'Zamanlanmış iş değiştirilen betiği {j["user"]} bağlamında çalıştırma riski.',
                yuksek,
                "Betiği ve üst dizinlerini root'a ait salt-yazılır yap; mutlak yol ve en az ayrıcalıklı hizmet hesabı kullan."))
        if not j["command_absolute"]:
            for ad in j["path"]:
                p = dizinler[ad]
                if p["caller_write"]:
                    sonuc.append(rapor(
                        f'IS:{j["job_id"]}:path-yazilabilir:{ad}', [j["evidence"], p["evidence"]],
                        ortak + f' Komut göreli olmalı ve PATH dizini çağıran tarafından yazılabilir olmalı: {ad}.',
                        f'Komut araması kontrol edilebilir dizine yönelerek {j["user"]} bağlamında istenmeyen program riski.',
                        yuksek,
                        "Komuta mutlak yol ver; PATH'i kısalt ve her bileşeni root'a ait salt-yazılır dizinle sınırla."))
                if not p["absolute"]:
                    etiket = ad or "<bos>"
                    sonuc.append(rapor(
                        f'IS:{j["job_id"]}:path-goreceli:{etiket}', [j["evidence"], p["evidence"]],
                        ortak + f' Komut göreli ve PATH bileşeni çalışma dizinine bağlı: {etiket}; yazılabilirlik ayrıca kanıtlanmalı.',
                        f'Çalışma dizinine bağlı komut çözümü {j["user"]} işinde öngörülemez arama riski.',
                        "orta",
                        "Boş/göreli PATH bileşenini kaldır; komut için mutlak yol ve sabit, minimal PATH tanımla."))
    return sorted(sonuc, key=lambda b: b["id"])

print(zamanli_gorev_bulgulari(v))
```

```hint
İşleri önce aktif tetik ve farklı kullanıcıyla süz. Betik kontrolünü PATH'ten bağımsız yap. PATH sözlüğünü `directory` ile kur; yazılabilir ve göreli/boş koşullarını ayrı `if` bloklarında değerlendir.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from linux_privesc_lab import hazirla
hazirla()
```
:::

::: anlat Raporlama: önceliği kanıtla, sınırı abartma
Bulgu listesi bir istismar rehberi değildir. `kritik`, kayıtlı kullanıcıya root sınırını kontrol ettiren açık bir yapılandırma önkoşulu olduğunu; `yuksek`, root dışı hesap/grup ya da ek çalışma koşulu taşıyan güçlü riski; `orta`, daraltılması gereken ama tek başına kontrol kanıtı olmayan yüzeyi belirtir. Bunlar gerçek ortamda varlık kritikliği ve bağımsız doğrulamayla tekrar önceliklendirilir.

Yanlış pozitifleri rapordan silmek yerine karar notunda koru: dağıtımdan gelen salt-yazılır SUID dosyası, sabit argümanlı sudo kuralı, aynı kullanıcı işi, inactive servis, yalnız inheritable capability ve kullanıcı ad alanındaki `CapEff` neden bulgu sayılmadı? Bu gerekçe, sonraki denetimde aynı satırın yeniden “kritik” diye şişirilmesini önler.
:::
