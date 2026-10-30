---
id: pu12
title: Windows/Linux Yetki Yükseltme, AD Kimlik Doğrulama Saldırıları ve Yatay Hareket · Kayıt Analizi
summary: Kayıtlı Linux/Windows yapılandırma kanıtında riskli yetki ilişkilerini ve sentetik AD olaylarında parola püskürtme, kaba kuvvet, başarısızdan başarılıya geçiş ile kaynak-hedef zincirini analiz etmek; gerçek saldırı yürütmeden savunma bulgusu üretmek.
timeout: 60
---

::: anlat Kapsam: saldırıyı değil, bıraktığı izi incele
Bu ders **güvenli, yerel ve çevrimdışı** bir kayıt analizidir. Bütün veriler `pu06_lab.json` içinde önceden üretilmiş sentetik kayıtlardır. Gerçek sistemde ayrıcalık yükseltme, ACL/sudo/cron/JEA değiştirme, parola deneme, parola/hash/ticket çalma-kırma-yeniden kullanma, uzaktan kod veya servis çalıştırma **yapılmaz**. Komut adları yalnız daha önce kaydedilmiş çıktının hangi araçtan geldiğini belirtir; ders bunları çalıştırmaz.

CM23/24'teki ayrımı koru: token, DACL ve erişim sonucu farklı kanıtlardır. BS33'teki gibi capability'nin adı ve bayrakları birlikte okunur. PS24'teki JEA riskleri burada puanlanmaz; oturum bağlamıyla bulguya çevrilir. AD09'daki olay kimlikleri ile PU02'deki zaman ve varlık ilişkilendirmesi birleşir. AD16'daki temel kural da geçerlidir: **yapılandırma veya tek olay, saldırının kesin başarısı değildir.**

| Kayıt | Savunma sorusu |
|---|---|
| `id`, `getcap`, `sudo -l`, cron, PATH | Yanlış yapılandırma hangi güvenlik sınırını zayıflatıyor? |
| Token grup SID'leri, DACL, JEA özeti | Etkin SID nedir, yazma hakkı kime açık, tehlikeli komut hangi bağlamda görünür? |
| 4624/4625/4768/4769/4771/4776 | Denemeler birçok hesaba mı, tek hesaba mı; başarı hangi kaynaktan ve oturum türüyle geldi? |

> [!GÜVENLİK]
> Bulgu, inceleme önceliğidir; otomatik suçlama değildir. Özellikle 4768 TGT ve 4769 hizmet bileti isteğidir; tek başlarına yatay hareket kanıtı sayılmaz. Bu derste yatay kenar yalnız başarılı 4624, Logon Type 3 veya 10 ve farklı kaynak-hedef üzerinden modellenir.
:::

::: anlat Sentetik fixture ve ortak okuma kalıbı
Her görevin hazırlığı, `sandbox/attack_analysis_lab.py` içindeki salt-okunur yardımcıyla fixture'ı geçici çalışma klasörüne `pu06_lab.json` olarak kopyalar. Yardımcı yalnız JSON okur ve bu kopyayı oluşturur; ağ, alt süreç, kimlik bilgisi veya sistem API'si kullanmaz. Çözümler aynı yerel dosyayı `json.load` ile açar.

```python norun
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))
linux = v["linux"]
windows = v["windows"]
olaylar = v["ad_events"]
```

Zamanlar ISO 8601 UTC (`Z`) biçiminde ve aynı saniye çözünürlüğündedir. Metin sıralaması bu sabit biçimde kronolojik sırayla aynıdır; pencere hesabında yine `datetime` kullanılır. IP, hesap ve makine adları kurgusaldır.
:::

::: tahmin Başarılı bilet isteği yatay hareket mi?
```python
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))
for o in v["ad_events"]:
    if o["event_id"] in (4768, 4769):
        print(o["event_id"], o["account"], o["source_host"], o["target_host"])
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from attack_analysis_lab import hazirla
hazirla()
```

???

İki satır yazar: `4768 ayse PC-AYSE DC01` ve `4769 ayse SRV-PORTAL DC01`. İlki TGT, ikincisi `CIFS/srv-db` hizmet bileti isteğidir. 4769'daki `service` alanı hedef hizmet hakkında ipucu verir ama kaynak-hedef arasında başarılı oturum açıldığını tek başına kanıtlamaz. Sonraki görevde yatay zincir yalnız 4624 Type 3/10 kayıtlarından kurulacak.
:::

::: gorev 1 · Linux kayıtlarında zayıf yetki sınırları
`linux_bulgulari(v)` işlevini yaz. Girdi `v["linux"]` bölümüdür; dönüş, aşağıdaki kurallardan üretilen **yinelenmeyen ve sıralı** metin listesidir.

- **Capability:** `cap_setuid`, `cap_dac_override`, `cap_sys_admin`, `cap_sys_ptrace` bayraklarında `e` veya `p` varsa `CAP:<yol>:<capability>`. `cap_net_raw` bu görevin riskli kümesinde değildir.
- **sudo:** `runas == "root"`, `nopasswd` doğru ve komutta `*` varsa `SUDO:<kullanici>:<komut>`. Parolasız olsa bile argümanı sabit `systemctl restart yedek` satırını bu kural işaretlemez.
- **cron:** Dosya root'a ait değilse `CRON:<yol>:sahip-root-degil`; root'a aitken `root` dışında yazabilen varsa her yazan için `CRON:<yol>:yazabilir=<grup>`.
- **PATH:** Dizin boşsa veya `/` ile başlamıyorsa `PATH:<dizin-veya-<bos>>:goreceli`. Ayrıca `root` dışında yazabilen varsa her yazan için `PATH:<dizin>:yazabilir=<grup>`. Aynı satır iki koşulu da sağlayabilir.

Bu işlev komut çalıştırmaz; yalnız kayıtlı sözlükleri sınıflandırır.

```starter
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

def linux_bulgulari(v):
    return []

for bulgu in linux_bulgulari(v["linux"]):
    print(bulgu)
```

```test
import copy
need("linux_bulgulari")
beklenen = sorted([
    "CAP:/opt/lab/okuyucu:cap_dac_override",
    "CAP:/opt/lab/yardimci:cap_setuid",
    "CRON:/etc/cron.d/gecici:sahip-root-degil",
    "CRON:/etc/cron.d/rapor:yazabilir=users",
    "PATH:<bos>:goreceli",
    "PATH:./araclar:goreceli",
    "PATH:/opt/ortak/bin:yazabilir=users",
    "SUDO:operator:/usr/bin/less /var/log/*",
])
eq(linux_bulgulari(v["linux"]), beklenen, "dört kaynak türü, kesin ve sıralı bulgular")
x = copy.deepcopy(v["linux"])
x["getcap"] = [{"path": "/x", "capabilities": {"cap_setuid": "i", "cap_net_raw": "ep"}}]
x["sudo_l"] = [{"user": "u", "runas": "root", "nopasswd": False, "command": "/bin/*"}]
x["cron"] = [{"path": "/cron", "owner": "root", "writable_by": []}]
x["path"] = [{"directory": "/usr/bin", "owner": "root", "writable_by": []}]
eq(linux_bulgulari(x), [], "yalnız inheritable capability, parolalı sudo ve root salt-yazılır kayıtları bulgu değil")
x["getcap"][0]["capabilities"]["cap_sys_admin"] = "ep"
eq(linux_bulgulari(x), ["CAP:/x:cap_sys_admin"], "effective/permitted riskli capability yakalanır")
x = copy.deepcopy(v["linux"])
x["path"] = [{"directory": "", "owner": "root", "writable_by": ["root", "users"]}]
eq(linux_bulgulari(x), sorted([b for b in beklenen if not b.startswith("PATH:")] + ["PATH:<bos>:goreceli", "PATH::yazabilir=users"]),
   "boş PATH iki ayrı bulgu üretir; boş etiket yalnız göreli bulguda kullanılır")
x = copy.deepcopy(v["linux"])
x["sudo_l"][1]["runas"] = "operator"
eq([b for b in linux_bulgulari(x) if b.startswith("SUDO:")], [], "wildcard olsa bile root olmayan runas bu kurala girmez")
```

```solution
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

RISKLI_CAP = {"cap_setuid", "cap_dac_override", "cap_sys_admin", "cap_sys_ptrace"}

def linux_bulgulari(v):
    bulgular = set()
    for kayit in v["getcap"]:
        for ad, bayraklar in kayit["capabilities"].items():
            if ad in RISKLI_CAP and {"e", "p"} & set(bayraklar):
                bulgular.add(f'CAP:{kayit["path"]}:{ad}')
    for kayit in v["sudo_l"]:
        if kayit["runas"] == "root" and kayit["nopasswd"] and "*" in kayit["command"]:
            bulgular.add(f'SUDO:{kayit["user"]}:{kayit["command"]}')
    for kayit in v["cron"]:
        if kayit["owner"] != "root":
            bulgular.add(f'CRON:{kayit["path"]}:sahip-root-degil')
        for grup in kayit["writable_by"]:
            if kayit["owner"] == "root" and grup != "root":
                bulgular.add(f'CRON:{kayit["path"]}:yazabilir={grup}')
    for kayit in v["path"]:
        dizin = kayit["directory"]
        if not dizin.startswith("/"):
            bulgular.add(f'PATH:{dizin or "<bos>"}:goreceli')
        for grup in kayit["writable_by"]:
            if grup != "root":
                bulgular.add(f'PATH:{dizin}:yazabilir={grup}')
    return sorted(bulgular)

for bulgu in linux_bulgulari(v["linux"]):
    print(bulgu)
```

```hint
Bulguları bir kümeye ekle. Capability'de `{"e", "p"} & set(bayraklar)` kesişimi, PATH'te ise `not dizin.startswith("/")` hem boş hem göreli yolu yakalar.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from attack_analysis_lab import hazirla
hazirla()
```
:::

::: gorev 2 · Windows token, DACL ve JEA kanıtı
İki işlev yaz:

`erisim_var(token, nesne, hak)`: Kullanıcı SID'si ile **etkin ve deny-only olmayan** grup SID'lerini kullan. İstenen tek hak için ilgili deny ACE varsa `False`; yoksa ilgili allow ACE'lerin birleşimi hakkı veya `FullControl` içeriyorsa `True`; aksi hâlde `False`. SID eşleşmesi tamdır. Sahiplik bu basit modelde otomatik tam yetki sayılmaz.

`windows_bulgulari(v)`: Girdi `v["windows"]`; sıralı, yinelenmeyen bulgu listesi döndürür.

- Yönetici SID'si `S-1-5-32-544` deny-only ise `TOKEN:yonetici-deny-only`.
- `Everyone` (`S-1-1-0`) veya `BUILTIN\Users` (`S-1-5-32-545`) allow ACE'sinde `Write`/`FullControl` varsa `DACL:<yol>:<sid>:yazma`. Bu, geniş yazma yüzeyi bulgusudur; her kullanıcı için nihai erişim kararı değildir.
- `run_as_virtual_account` doğru olan JEA oturumunda `Invoke-Expression`, `Start-Process`, `New-Service`, `Invoke-Command`, `Add-LocalGroupMember` görünürse her biri için `JEA:<ad>:KOMUT:<komut>`.
- Aynı koşulda `C:\` benzeri sürücü köküyle başlamayan dış komut için `JEA:<ad>:DIS:<yol>`; `C:` + ters bölme kontrolü yeterlidir.
- Aynı koşulda özel fonksiyon gövdesinde yukarıdaki tehlikeli komutlardan biri geçiyorsa `JEA:<ad>:FONKSIYON:<fonksiyon>:<komut>`.

Deny-only Administrators ACE'ye güvenerek yazma izni verme; kullanıcıya özel deny ACE'yi de grup allow'undan önce uygula.

```starter
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

def erisim_var(token, nesne, hak):
    return True

def windows_bulgulari(v):
    return []

print(windows_bulgulari(v["windows"]))
```

```test
import copy
need("erisim_var"); need("windows_bulgulari")
w = v["windows"]
token, nesneler = w["token"], w["objects"]
eq(erisim_var(token, nesneler[0], "Write"), False, "deny-only Administrators olumlu izin vermez")
eq(erisim_var(token, nesneler[0], "ReadAndExecute"), True, "etkin Users allow okuma verir")
eq(erisim_var(token, nesneler[1], "Write"), True, "etkin Users yazma allow")
eq(erisim_var(token, nesneler[2], "Write"), False, "kullanıcı deny, grup FullControl allow'u aşar")
eq(erisim_var(token, nesneler[2], "ReadAndExecute"), True, "yalnız Write deny diğer hakkı kaldırmaz")
beklenen = [
    "DACL:C:\\Yonetim\\Korunan.ps1:S-1-5-32-545:yazma",
    "DACL:C:\\Yonetim\\Ortak.ps1:S-1-5-32-545:yazma",
    "JEA:PortalYonetim:DIS:whoami.exe",
    "JEA:PortalYonetim:FONKSIYON:Set-Portal:Invoke-Expression",
    "JEA:PortalYonetim:KOMUT:Invoke-Expression",
    "TOKEN:yonetici-deny-only",
]
eq(windows_bulgulari(w), beklenen, "token, iki geniş DACL ve üç JEA bulgusu")
x = copy.deepcopy(w)
x["token"]["groups"][-2]["deny_only"] = False
x["token"]["groups"][-2]["enabled"] = True
eq(erisim_var(x["token"], nesneler[0], "Write"), True, "etkin yönetici SID'si artık allow ile eşleşir")
x["jea"][1]["run_as_virtual_account"] = False
eq([b for b in windows_bulgulari(x) if b.startswith("JEA:")], [], "sanal hesap koşulu yoksa JEA kuralları üretmez")
x = copy.deepcopy(w)
x["objects"][2]["aces"][1]["type"] = "allow"
eq(erisim_var(token, x["objects"][2], "Write"), True, "deny kaldırılırsa FullControl yazmayı sağlar")
x = copy.deepcopy(w)
x["jea"][1]["visible_external_commands"] = ["D:\\Araclar\\whoami.exe"]
eq([b for b in windows_bulgulari(x) if ":DIS:" in b], [], "başka sürücüdeki tam yol da kabul edilir")
x = copy.deepcopy(w)
for grup in x["token"]["groups"]:
    if grup["sid"] == "S-1-5-32-545":
        grup["enabled"], grup["deny_only"] = False, False
eq(erisim_var(x["token"], nesneler[1], "Write"), False, "devre dışı grup SID'si deny-only olmasa da izin vermez")
x = copy.deepcopy(w)
for grup in x["token"]["groups"]:
    if grup["sid"] == "S-1-5-32-544":
        grup["deny_only"] = False
eq([b for b in windows_bulgulari(x) if b.startswith("TOKEN:")], [], "deny-only olmayan Administrators token bulgusu değildir")
```

```solution
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

TEHLIKELI = {"Invoke-Expression", "Start-Process", "New-Service", "Invoke-Command", "Add-LocalGroupMember"}

def etkin_sidler(token):
    sidler = {token["user_sid"]}
    for grup in token["groups"]:
        if grup["enabled"] and not grup["deny_only"]:
            sidler.add(grup["sid"])
    return sidler

def erisim_var(token, nesne, hak):
    sidler = etkin_sidler(token)
    ilgili = [ace for ace in nesne["aces"] if ace["sid"] in sidler]
    for ace in ilgili:
        if ace["type"] == "deny" and (hak in ace["rights"] or "FullControl" in ace["rights"]):
            return False
    for ace in ilgili:
        if ace["type"] == "allow" and (hak in ace["rights"] or "FullControl" in ace["rights"]):
            return True
    return False

def windows_bulgulari(v):
    bulgular = set()
    for grup in v["token"]["groups"]:
        if grup["sid"] == "S-1-5-32-544" and grup["deny_only"]:
            bulgular.add("TOKEN:yonetici-deny-only")
    for nesne in v["objects"]:
        for ace in nesne["aces"]:
            if (ace["type"] == "allow" and ace["sid"] in {"S-1-1-0", "S-1-5-32-545"}
                    and {"Write", "FullControl"} & set(ace["rights"])):
                bulgular.add(f'DACL:{nesne["path"]}:{ace["sid"]}:yazma')
    for oturum in v["jea"]:
        if not oturum["run_as_virtual_account"]:
            continue
        for komut in oturum["visible_cmdlets"]:
            if komut in TEHLIKELI:
                bulgular.add(f'JEA:{oturum["name"]}:KOMUT:{komut}')
        for yol in oturum["visible_external_commands"]:
            if len(yol) < 3 or not (yol[0].isalpha() and yol[1:3] == ":\\"):
                bulgular.add(f'JEA:{oturum["name"]}:DIS:{yol}')
        for fn in oturum["function_definitions"]:
            for komut in sorted(TEHLIKELI):
                if komut.lower() in fn["body"].lower():
                    bulgular.add(f'JEA:{oturum["name"]}:FONKSIYON:{fn["name"]}:{komut}')
    return sorted(bulgular)

print(windows_bulgulari(v["windows"]))
```

```hint
Önce etkin SID kümesini çıkar. Erişimde iki geçiş yap: herhangi bir deny varsa hemen `False`, sonra allow ara. DACL bulgusu ile `erisim_var` sonucunu bilinçli olarak ayrı tut.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from attack_analysis_lab import hazirla
hazirla()
```
:::

::: gorev 3 · Parola püskürtme, kaba kuvvet ve başarı geçişi
Başarısız kimlik doğrulama kaydı şunlardır: 4625, 4771 ve `status != "0x0"` olan 4776. Başarılı 4776 da kimlik doğrulama kanıtıdır ama bu görevde başarı geçişi yalnız **4624** ile kapanır.

`saldiri_tipleri(olaylar, esik=3)`: Kaynak IP başına başarısızlıkları grupla. Toplam denemesi `esik`ten az olan kaynakları atla. Dönüş `(kaynak_ip, tur, deneme_sayisi, farkli_hesap_sayisi)` dörtlülerinin kaynak IP'ye göre sıralı listesi olsun:

- Farklı hesap sayısı en az `esik` **ve hiçbir hesap `esik` denemeye ulaşmamışsa** `parola-puskurtme`.
- Tam bir hesap varsa `kaba-kuvvet`.
- Diğer yoğun örüntüler `karma`.

`basariya_gecis(olaylar, pencere=300)`: Aynı kaynak IP ve hesapta, başarılı 4624'ten önceki `0 < fark <= pencere` saniyelik başarısızlıkları bul. Her başarı için penceredeki **en eski** başarısızlığı seç ve `(kaynak_ip, hesap, ilk_hata_zamani, basari_zamani, hedef, logon_type)` döndür. Başarı zamanına göre sırala. Aynı hesabın başarıdan önceki denemeleri bir başarıyla kapandıktan sonra eski hatalar sonraki başarıya taşınmasın. Başarıdan sonraki hata geriye eşleşmez.

```starter
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

def saldiri_tipleri(olaylar, esik=3):
    return []

def basariya_gecis(olaylar, pencere=300):
    return []

print(saldiri_tipleri(v["ad_events"]))
print(basariya_gecis(v["ad_events"]))
```

```test
import copy
need("saldiri_tipleri"); need("basariya_gecis")
o = v["ad_events"]
eq(saldiri_tipleri(o), [("10.20.30.40", "parola-puskurtme", 5, 5), ("10.20.30.50", "kaba-kuvvet", 4, 1)],
   "çok hesaba azar deneme ile tek hesaba çok deneme ayrılır")
eq(saldiri_tipleri(o, esik=5), [("10.20.30.40", "parola-puskurtme", 5, 5)], "tam eşikteki kaynak dahil, altındaki hariç")
eq(saldiri_tipleri(o, esik=6), [], "eşik altındaki iki kaynak da dışarıda")
eq(basariya_gecis(o), [
    ("10.20.30.40", "ayse", "2026-10-26T09:00:00Z", "2026-10-26T09:05:00Z", "SRV-PORTAL", 3),
    ("10.20.30.50", "can", "2026-10-26T09:10:00Z", "2026-10-26T09:14:00Z", "SRV-ADM", 10),
], "iki başarısızdan başarılıya geçiş, en eski hata ve Logon Type")
eq(basariya_gecis(o, pencere=200), [("10.20.30.50", "can", "2026-10-26T09:11:00Z", "2026-10-26T09:14:00Z", "SRV-ADM", 10)],
   "pencereye giren en eski hata seçilir; 09:10 dışarıda, 09:11 içeridedir")
x = copy.deepcopy(o)
x[0]["account"] = "baska"
eq(basariya_gecis(x), [("10.20.30.50", "can", "2026-10-26T09:10:00Z", "2026-10-26T09:14:00Z", "SRV-ADM", 10)],
   "aynı kaynak ama farklı hesap eşleşmez; ayse geçişi kalmaz")
x = copy.deepcopy(o)
x[5]["time"] = "2026-10-26T08:59:00Z"
eq([g for g in basariya_gecis(x) if g[1] == "ayse"], [], "başarıdan sonraki hata geriye doğru eşleşmez")
x = copy.deepcopy(o)
for kayit in x:
    if kayit["source_ip"] == "10.20.30.40" and kayit["event_id"] in (4625, 4771, 4776):
        kayit["account"] = "ayse"
eq(saldiri_tipleri(x)[0], ("10.20.30.40", "kaba-kuvvet", 5, 1), "aynı hacim tek hesapta kaba kuvvet olur")
x = copy.deepcopy(o)
x.append(dict(x[0], account="yeni", time="2026-10-26T09:04:30Z"))
x.append(dict(x[0], account="ayse", time="2026-10-26T09:04:45Z"))
x.append(dict(x[0], account="ayse", time="2026-10-26T09:04:50Z"))
eq(saldiri_tipleri(x)[0][1], "karma", "bir hesap eşiğe ulaşırken birçok hesap varsa karma")
sablon = next(k for k in o if k["event_id"] == 4625)
puskurt = [dict(sablon, source_ip="10.9.9.9", account=f"h{i}", time=f"2026-10-26T10:0{i}:{s:02d}Z") for i in range(4) for s in (0, 30)]
eq(saldiri_tipleri(puskurt), [("10.9.9.9", "parola-puskurtme", 8, 4)], "hesap başına iki deneme eşik altında: hâlâ püskürtme")
basarili_ntlm = [dict(sablon, event_id=4776, status="0x0", source_ip="10.9.9.8", account=f"n{i}", time=f"2026-10-26T10:1{i}:00Z") for i in range(4)]
eq(saldiri_tipleri(basarili_ntlm), [], "0x0 durumlu 4776 başarılı doğrulamadır, hata sayılmaz")
hata = dict(sablon, source_ip="10.9.9.7", account="deniz", time="2026-10-26T11:00:00Z")
giris = dict(sablon, event_id=4624, status="0x0", source_ip="10.9.9.7", account="deniz", target_host="SRV-X", logon_type=3)
eq(basariya_gecis([hata, dict(giris, time="2026-10-26T11:05:00Z")])[0][2], "2026-10-26T11:00:00Z", "tam 300 sn önceki hata pencerede")
eq(basariya_gecis([hata, dict(giris, time="2026-10-26T11:05:01Z")]), [], "301 sn önceki hata varsayılan pencerenin dışında")
eq(basariya_gecis([hata, dict(giris, time="2026-10-26T11:00:00Z")]), [], "başarıyla aynı saniyedeki hata öncül sayılmaz")
eq(basariya_gecis([hata, dict(giris, event_id=4672, time="2026-10-26T11:01:00Z")]), [], "başka bir başarılı olay giriş değildir")
```

```solution
import datetime as dt
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

def zaman(metin):
    return dt.datetime.strptime(metin, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)

def hata_mi(o):
    return o["event_id"] in (4625, 4771) or (o["event_id"] == 4776 and o["status"] != "0x0")

def saldiri_tipleri(olaylar, esik=3):
    gruplar = {}
    for o in olaylar:
        if hata_mi(o):
            gruplar.setdefault(o["source_ip"], []).append(o)
    sonuc = []
    for kaynak, kayitlar in gruplar.items():
        if len(kayitlar) < esik:
            continue
        sayim = {}
        for o in kayitlar:
            sayim[o["account"]] = sayim.get(o["account"], 0) + 1
        if len(sayim) >= esik and max(sayim.values()) < esik:
            tur = "parola-puskurtme"
        elif len(sayim) == 1:
            tur = "kaba-kuvvet"
        else:
            tur = "karma"
        sonuc.append((kaynak, tur, len(kayitlar), len(sayim)))
    return sorted(sonuc)

def basariya_gecis(olaylar, pencere=300):
    bekleyen = {}
    sonuc = []
    for o in sorted(olaylar, key=lambda k: k["time"]):
        anahtar = (o["source_ip"], o["account"])
        if hata_mi(o):
            bekleyen.setdefault(anahtar, []).append(o)
            continue
        if o["event_id"] != 4624 or o["status"] != "0x0":
            continue
        adaylar = [h for h in bekleyen.get(anahtar, [])
                   if 0 < (zaman(o["time"]) - zaman(h["time"])).total_seconds() <= pencere]
        if adaylar:
            ilk = min(adaylar, key=lambda h: h["time"])
            sonuc.append((o["source_ip"], o["account"], ilk["time"], o["time"], o["target_host"], o["logon_type"]))
        bekleyen[anahtar] = []
    return sorted(sonuc, key=lambda g: g[3])

print(saldiri_tipleri(v["ad_events"]))
print(basariya_gecis(v["ad_events"]))
```

```hint
Başarısızlık sınıflandırmasını `hata_mi` içinde bir kez tanımla. Geçişte olayları zamana göre sırala; `(source_ip, account)` anahtarlı bekleyen listeleri tut ve her 4624 sonrası o anahtarı temizle.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from attack_analysis_lab import hazirla
hazirla()
```
:::

::: gorev 4 · Logon Type ile kaynak-hedef zinciri
`yatay_zincir(olaylar, baslangic, baslangic_zamani)` işlevini yaz. Başlangıç makinesinin ele geçirildiği varsayımıyla yalnız şu kayıtları kenar say:

- `event_id == 4624` ve `status == "0x0"`;
- Logon Type **3** (`ag`) veya **10** (`rdp`);
- `source_host != target_host`;
- kaynak makine o anda kapsamda ve olay zamanı `baslangic_zamani`ndan büyük/eşit.

Kenarları zaman sırasıyla gez; hedef yeni ise kapsama ekle ve `(zaman, hesap, kaynak, hedef, tur)` demetini sonuca ekle. `tur`, Type 3 için `ag`, Type 10 için `rdp` olsun. Daha önce kapsama giren hedef için yeni kenar yazma. 4768/4769/4776 ve Type 2 kenar değildir. Zaman sıralı gezinti, bir makinenin kapsama girmesinden önceki giden oturumlarını zincire katmaz.

Bu yalnız **aday zincir** çıkarımıdır; normal yönetim trafiği de aynı biçimde görünebilir. Olay bağlamı ve varlık envanteriyle doğrulanmalıdır.

```starter
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

def yatay_zincir(olaylar, baslangic, baslangic_zamani):
    return []

for kenar in yatay_zincir(v["ad_events"], "PC-AYSE", "2026-10-26T09:00:00Z"):
    print(kenar)
```

```test
import copy
need("yatay_zincir")
o = v["ad_events"]
beklenen = [
    ("2026-10-26T09:05:00Z", "ayse", "PC-AYSE", "SRV-PORTAL", "ag"),
    ("2026-10-26T09:08:00Z", "ayse", "SRV-PORTAL", "SRV-DB", "ag"),
    ("2026-10-26T09:09:00Z", "svc_yedek", "SRV-DB", "SRV-YEDEK", "ag"),
]
eq(yatay_zincir(o, "PC-AYSE", "2026-10-26T09:00:00Z"), beklenen, " üç zamanlı sıçrama; Kerberos ve ilgisiz trafik kenar değil")
eq(yatay_zincir(o, "PC-CAN", "2026-10-26T09:00:00Z"),
   [("2026-10-26T09:14:00Z", "can", "PC-CAN", "SRV-ADM", "rdp")], "Type 10 RDP etiketi")
eq(yatay_zincir(o, "PC-MERT", "2026-10-26T09:00:00Z"),
   [("2026-10-26T09:16:00Z", "mert", "PC-MERT", "SRV-DOSYA", "ag")], "Type 2 yerel oturum atlanır")
eq(yatay_zincir(o, "SRV-PORTAL", "2026-10-26T09:08:00Z"), beklenen[1:], "başlangıç anındaki kenar dahil, önceki kenar hariç")
eq(yatay_zincir(o, "PC-AYSE", "2026-10-26T09:08:00Z"), [], "başlangıç makinesinin eski giden oturumları geriye alınmaz")
x = copy.deepcopy(o)
x[8]["time"] = "2026-10-26T08:00:00Z"
eq(yatay_zincir(x, "PC-AYSE", "2026-10-26T09:00:00Z"), beklenen[:1], "kapsama girmeden önceki giden oturum zincire eklenmez")
x = copy.deepcopy(o)
x[5]["logon_type"] = 2
eq(yatay_zincir(x, "PC-AYSE", "2026-10-26T09:00:00Z"), [], "Type 2 başlangıç kenarı olamaz; sonraki kaynak kapsama girmez")
x = copy.deepcopy(o)
x[5]["status"] = "0xC000006A"
eq(yatay_zincir(x, "PC-AYSE", "2026-10-26T09:00:00Z"), [], "4624 olsa bile başarısız durum kenar değildir")
x = copy.deepcopy(o)
x[8]["target_host"] = "PC-AYSE"
eq(yatay_zincir(x, "PC-AYSE", "2026-10-26T09:00:00Z"), beklenen[:1], "kapsamda olan hedefe dönüş yeni kenar yazmaz")
```

```solution
import json
v = json.load(open("pu06_lab.json", encoding="utf-8"))

def yatay_zincir(olaylar, baslangic, baslangic_zamani):
    kapsam = {baslangic}
    sonuc = []
    for o in sorted(olaylar, key=lambda k: k["time"]):
        if o["time"] < baslangic_zamani:
            continue
        if o["event_id"] != 4624 or o["status"] != "0x0" or o["logon_type"] not in (3, 10):
            continue
        kaynak, hedef = o["source_host"], o["target_host"]
        if kaynak == hedef or kaynak not in kapsam or hedef in kapsam:
            continue
        tur = "ag" if o["logon_type"] == 3 else "rdp"
        sonuc.append((o["time"], o["account"], kaynak, hedef, tur))
        kapsam.add(hedef)
    return sonuc

for kenar in yatay_zincir(v["ad_events"], "PC-AYSE", "2026-10-26T09:00:00Z"):
    print(kenar)
```

```hint
Kapsamı başlangıç makinesiyle bir küme olarak başlat. Olayları zaman sırasına koy; kaynak kapsamda, hedef yeni ve tür 3/10 ise kenarı ekleyip hedefi kapsama al.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from attack_analysis_lab import hazirla
hazirla()
```
:::

::: anlat Bulgudan müdahaleye: kanıt sınırını koru
Dört çıktıyı birlikte okurken “riskli yapılandırma”, “kimlik doğrulama örüntüsü”, “başarılı oturum” ve “yatay hareket adayı” etiketlerini birbirine karıştırma. Örneğin JEA'da tehlikeli komutun görünür olması onun çalıştığını göstermez; 4769 hizmet bileti isteği hedefe oturum açıldığını kanıtlamaz; 4624 başarısı da tek başına kötü niyeti kanıtlamaz.

PU02'deki gibi zamanı ve kapsamı kaydet: hangi kaynak IP, hangi hesaplar, ilk hata ve ilk başarı, hangi Logon Type, hangi kaynak-hedef kenarları. Müdahale önerisi gerçek ortamın yetkili olay müdahale sürecine bırakılır. Bu derste hesap kilitleme, makineyi ağdan ayırma, kural değiştirme veya karşı erişim gibi eylemler de çalıştırılmaz.
:::
