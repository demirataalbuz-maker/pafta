---
id: pu01
title: ATT&CK ile Tespit Kapsamı · Etiketten Haritaya
summary: MITRE ATT&CK'in yapısı (taktik, teknik, alt teknik) ve bir tekniğin birden çok taktikte bulunması; Sigma kurallarının attack.tNNNN etiketlerini gerçek ATT&CK verisine (Enterprise 19.2) eşlemek; emekliye ayrılmış (revoked) tekniği yerine geçenle değiştirmek, kullanım dışı (deprecated) ve var olmayan kimlikleri atmak; taktik başına kapsam, alt tekniğin üst tekniği kapsaması; ATT&CK Navigator katmanı ve öncelik listesinden boşluk raporu. ATT&CK 19'da Defense Evasion'ın yerini Stealth ve Defense Impairment'ın alması.
---

::: anlat Ortak bir harita
Bir SOC "elimizde 200 tespit kuralı var" dediğinde asıl soru şudur: **hangi saldırgan davranışlarını görüyoruz, hangilerini görmüyoruz?** Bu soruyu herkesin aynı dille sorması için MITRE **ATT&CK** kullanılır: gerçek saldırılarda gözlenen davranışların herkese açık bir kataloğu.

| Kavram | Örnek | Anlamı |
|---|---|---|
| Taktik | `execution` (TA0002) | saldırganın o adımdaki amacı |
| Teknik | `T1059` Command and Scripting Interpreter | amaca ulaşma yolu |
| Alt teknik | `T1059.001` PowerShell | tekniğin daha belirli bir biçimi |

Bir teknik **birden çok taktikte** bulunabilir: `T1078` Valid Accounts hem ilk erişim, hem kalıcılık, hem yetki yükseltme, hem de gizlenme içindir.

Sigma kuralları ATT&CK'e etiketle bağlanır: `attack.t1059.001` bir teknik, `attack.execution` bir taktik etiketidir. Kapsam haritası, kurallarının etiketlerini ATT&CK'e eşleyip hangi tekniklerin en az bir kuralla görüldüğünü saymaktır. Bu haritayı **ATT&CK Navigator** gibi araçlarda bir katman olarak gösterirsin; purple team çalışmasında hangi tekniğin önce sınanacağını bu harita belirler.

Bu yolda çalışma klasöründe `attack.json` var: MITRE'nin resmi ATT&CK Enterprise 19.2 verisinden üretilmiş bir özet.

```python norun
import json
attack = json.load(open("attack.json", encoding="utf-8"))
attack["taktikler"]   # matris sırasıyla [{"id": "TA0043", "kisa": "reconnaissance", "ad": "Reconnaissance"}, ...]
attack["teknikler"]   # etkin teknikler: [{"id": "T1059.001", "ad": "PowerShell", "taktikler": ["execution"], ...}, ...]
attack["emekli"]      # emekliye ayrılan teknik → yerine geçen: {"T1086": "T1059.001", ...}
attack["kullanim_disi"]  # yerine bir şey konmadan kaldırılanlar: ["T1026", ...]
```

> [!TUZAK] ATT&CK değişir
> ATT&CK yılda birkaç kez yeni sürüm yayımlar. Teknikler birleştirilir, bölünür ya da emekliye ayrılır: eski kurallarda sık görülen `attack.t1086` (PowerShell) artık `T1059.001`'dir. ATT&CK 19'da taktik listesi de değişti: eski **Defense Evasion** yerine **Stealth** ve yeni **Defense Impairment** geldi. Eski bir kural kümesini yeni sürümle eşlemeden saymak, var olmayan teknikleri "kapsıyoruz" demek olur.

ATT&CK® MITRE'nin tescilli markasıdır; veri © The MITRE Corporation, [kullanım koşullarıyla](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/) kullanılır.
:::

::: tahmin
`T1078` Valid Accounts kaç taktikte bulunuyor? Bu kod ne yazar?

```python
import json
attack = json.load(open("attack.json", encoding="utf-8"))
t = next(t for t in attack["teknikler"] if t["id"] == "T1078")
print(len(t["taktikler"]), t["taktikler"])
```

???

**`4 ['stealth', 'persistence', 'privilege-escalation', 'initial-access']`**

```
4 ['stealth', 'persistence', 'privilege-escalation', 'initial-access']
```

Aynı teknik dört taktikte. Taktik başına kapsam sayarken bu kural dört taktiğin sayısına da girer; "kuralların yüzde kaçı hangi taktikte" sorusunun toplamı bu yüzden yüzde yüzü aşar. Bu bir hata değil, ATT&CK'in yapısı. Ayrıca listede `defense-evasion` değil `stealth` var: ATT&CK 19'un adlandırması.
:::

::: gorev 1 · Etiketten tekniğe
`teknikler(etiketler, attack)` fonksiyonunu yaz: bir kuralın etiket listesinden kapsadığı **etkin** teknik kimliklerini sıralı ve tekrarsız döndür.

- Teknik etiketi `attack.t1059` ya da `attack.t1059.001` biçimindedir; harf büyüklüğü fark etmez. Kimliği büyük harfle döndür (`T1059.001`).
- Taktik etiketleri (`attack.execution`), grup ya da yazılım etiketleri (`attack.g0016`, `attack.s0001`) ve başka etiketler (`cve.2021-44228`) teknik değildir.
- Emekliye ayrılan teknik, yerine geçenle değiştirilir (`T1086` → `T1059.001`).
- Kullanım dışı ya da ATT&CK'te hiç olmayan kimlikler atılır.

Kurallar `kurallar.json`'da: `[{"title": ..., "tags": [...]}, ...]`.

```starter
import json

attack = json.load(open("attack.json", encoding="utf-8"))


def teknikler(etiketler, attack):
    return sorted(e[7:].upper() for e in etiketler if e.startswith("attack.t"))


for kural in json.load(open("kurallar.json", encoding="utf-8")):
    print(kural["title"], teknikler(kural["tags"], attack))
```

```test
import json
need("teknikler")
A = json.load(open("attack.json", encoding="utf-8"))
K = {k["title"]: k["tags"] for k in json.load(open("kurallar.json", encoding="utf-8"))}
eq({b: teknikler(e, A) for b, e in K.items()},
   {"PowerShell kodlanmış komut": ["T1059.001"], "Eski PowerShell kuralı": ["T1059.001"],
    "LSASS bellek erişimi": ["T1003.001"], "Zamanlanmış görev": ["T1053.005"],
    "Eski kural, kullanım dışı teknik": [], "Hatalı etiketler": [], "Geçerli hesap kullanımı": ["T1078"],
    "Oltalama eki": ["T1566.001"], "Komut yorumlayıcı": ["T1059"], "Run anahtarı": ["T1547.001"]},
   "on kuralın teknikleri: T1086 yerine T1059.001, T1026 kullanım dışı, T9999 yok")
eq(teknikler(["attack.T1086", "attack.t1059.001", "attack.t1059"], A), ["T1059", "T1059.001"],
   "emekli ve yeni kimlik tekrar etmez; üst teknik ile alt teknik ayrı kimliklerdir")
eq(teknikler(["attack.g0016", "attack.s0001", "attack.execution", "attack.t1059.0011", "attack.t105"], A), [],
   "grup, yazılım, taktik ve biçimi bozuk kimlikler teknik değildir")
```

```solution
import json
import re

attack = json.load(open("attack.json", encoding="utf-8"))


def teknikler(etiketler, attack):
    etkin = {t["id"] for t in attack["teknikler"]}
    sonuc = set()
    for etiket in etiketler:
        m = re.fullmatch(r"attack\.(t\d{4}(?:\.\d{3})?)", etiket.lower())
        if not m:
            continue
        kimlik = m.group(1).upper()
        kimlik = attack["emekli"].get(kimlik, kimlik)
        if kimlik in etkin:
            sonuc.add(kimlik)
    return sorted(sonuc)


for kural in json.load(open("kurallar.json", encoding="utf-8")):
    print(kural["title"], teknikler(kural["tags"], attack))
```

```hint
Biçimi tam eşleşmeyle denetle: `re.fullmatch(r"attack\.(t\d{4}(?:\.\d{3})?)", etiket.lower())`. Sonra `attack["emekli"].get(kimlik, kimlik)` ile yerine geçeni al ve etkin teknikler kümesinde var mı diye bak.
```

```setup
import json
kurallar = [
    {"title": "PowerShell kodlanmış komut", "tags": ["attack.execution", "attack.t1059.001"]},
    {"title": "Eski PowerShell kuralı", "tags": ["attack.execution", "attack.t1086"]},
    {"title": "LSASS bellek erişimi", "tags": ["attack.credential-access", "attack.t1003.001"]},
    {"title": "Zamanlanmış görev", "tags": ["attack.persistence", "attack.T1053.005"]},
    {"title": "Eski kural, kullanım dışı teknik", "tags": ["attack.t1026"]},
    {"title": "Hatalı etiketler", "tags": ["attack.t9999", "cve.2021-44228", "attack.t1059.01"]},
    {"title": "Geçerli hesap kullanımı", "tags": ["attack.t1078"]},
    {"title": "Oltalama eki", "tags": ["attack.initial-access", "attack.t1566.001"]},
    {"title": "Komut yorumlayıcı", "tags": ["attack.t1059"]},
    {"title": "Run anahtarı", "tags": ["attack.persistence", "attack.t1547.001"]},
]
json.dump(kurallar, open("kurallar.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::

::: gorev 2 · Taktik başına kapsam
`kapsam(kurallar, attack)` fonksiyonunu yaz: her taktik için **matris sırasıyla** `(taktik kısa adı, kapsanan üst teknik sayısı, toplam üst teknik sayısı)`.

- Yalnız **üst teknikleri** say (`T1059`, `T1547`; kimliğinde nokta olmayanlar). Bir alt tekniği kapsayan kural, onun üst tekniğini de kapsamış sayılır: `T1547.001` → `T1547`.
- Bir üst teknik, ATT&CK'te bulunduğu **her** taktiğin sayısına girer.
- Etiketleri gorev 1'deki kurallarla çöz (fonksiyonu bu kodda yeniden yaz ya da kopyala).

```starter
import json

attack = json.load(open("attack.json", encoding="utf-8"))


def kapsam(kurallar, attack):
    return [(t["kisa"], 0, 0) for t in attack["taktikler"]]


for satir in kapsam(json.load(open("kurallar.json", encoding="utf-8")), attack):
    print(*satir)
```

```test
import json
need("kapsam")
A = json.load(open("attack.json", encoding="utf-8"))
K = json.load(open("kurallar.json", encoding="utf-8"))
eq(kapsam(K, A), [("reconnaissance", 0, 12), ("resource-development", 0, 9), ("initial-access", 2, 11), ("execution", 2, 20),
                  ("persistence", 3, 22), ("privilege-escalation", 3, 13), ("stealth", 1, 30), ("defense-impairment", 0, 18),
                  ("credential-access", 1, 17), ("discovery", 0, 34), ("lateral-movement", 0, 9), ("collection", 0, 17),
                  ("command-and-control", 0, 18), ("exfiltration", 0, 9), ("impact", 0, 15)],
   "ATT&CK 19.2 matris sırası; T1078 dört taktikte, T1053 ile T1547 alt teknikleriyle sayılır")
tek = {t: k for t, k, _ in kapsam([{"title": "x", "tags": ["attack.t1078"]}], A)}
eq([t for t, k in tek.items() if k], ["initial-access", "persistence", "privilege-escalation", "stealth"],
   "tek bir T1078 kuralı dört taktikte görünür")
eq(sum(k for _, k, _ in kapsam([{"title": "y", "tags": ["attack.t1086", "attack.t1059.001", "attack.t1059"]}], A)), 1,
   "aynı üst teknik (T1059) üç etiketle de bir kez sayılır")
```

```solution
import json
import re

attack = json.load(open("attack.json", encoding="utf-8"))


def teknikler(etiketler, attack):
    etkin = {t["id"] for t in attack["teknikler"]}
    sonuc = set()
    for etiket in etiketler:
        m = re.fullmatch(r"attack\.(t\d{4}(?:\.\d{3})?)", etiket.lower())
        if not m:
            continue
        kimlik = attack["emekli"].get(m.group(1).upper(), m.group(1).upper())
        if kimlik in etkin:
            sonuc.add(kimlik)
    return sorted(sonuc)


def kapsam(kurallar, attack):
    kapsanan = {t.split(".")[0] for k in kurallar for t in teknikler(k["tags"], attack)}
    sonuc = []
    for taktik in attack["taktikler"]:
        ust = [t["id"] for t in attack["teknikler"] if "." not in t["id"] and taktik["kisa"] in t["taktikler"]]
        sonuc.append((taktik["kisa"], sum(1 for t in ust if t in kapsanan), len(ust)))
    return sonuc


for satir in kapsam(json.load(open("kurallar.json", encoding="utf-8")), attack):
    print(*satir)
```

```hint
Önce bütün kuralların tekniklerini topla ve noktadan öncesini al: `t.split(".")[0]`. Sonra `attack["taktikler"]` sırasıyla dolaş; her taktik için `taktikler` listesinde o taktik bulunan üst teknikleri say.
```

```setup
import json
kurallar = [
    {"title": "PowerShell kodlanmış komut", "tags": ["attack.execution", "attack.t1059.001"]},
    {"title": "Eski PowerShell kuralı", "tags": ["attack.execution", "attack.t1086"]},
    {"title": "LSASS bellek erişimi", "tags": ["attack.credential-access", "attack.t1003.001"]},
    {"title": "Zamanlanmış görev", "tags": ["attack.persistence", "attack.T1053.005"]},
    {"title": "Eski kural, kullanım dışı teknik", "tags": ["attack.t1026"]},
    {"title": "Hatalı etiketler", "tags": ["attack.t9999", "cve.2021-44228", "attack.t1059.01"]},
    {"title": "Geçerli hesap kullanımı", "tags": ["attack.t1078"]},
    {"title": "Oltalama eki", "tags": ["attack.initial-access", "attack.t1566.001"]},
    {"title": "Komut yorumlayıcı", "tags": ["attack.t1059"]},
    {"title": "Run anahtarı", "tags": ["attack.persistence", "attack.t1547.001"]},
]
json.dump(kurallar, open("kurallar.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::

::: gorev 3 · Navigator katmanı ve boşluk raporu
İki fonksiyon:

- `katman(kurallar, attack)`: bir ATT&CK Navigator katmanı sözlüğü: `{"name": "Pafta tespit kapsamı", "domain": "enterprise-attack", "techniques": [...]}`. Her kapsanan teknik **kendi kimliğiyle** bir öğe: `{"techniqueID": ..., "score": <o tekniği kapsayan kural sayısı>, "comment": <kural adları, sıralı, "; " ile>}`; öğeler kimliğe göre sıralı.
- `bosluklar(kurallar, attack, oncelik)`: öncelik listesindeki teknik kimliklerinden **kapsanmayanlar**, listedeki sırayla. Emekli kimlik önce yerine geçene çevrilir. Bir üst teknik, alt tekniklerinden biri kapsanıyorsa kapsanmış sayılır; bir alt teknik ise yalnız kendisi kapsanıyorsa.

```starter
import json

attack = json.load(open("attack.json", encoding="utf-8"))


def katman(kurallar, attack):
    return {"name": "Pafta tespit kapsamı", "domain": "enterprise-attack", "techniques": []}


def bosluklar(kurallar, attack, oncelik):
    return list(oncelik)
```

```test
import json
need("katman"); need("bosluklar")
A = json.load(open("attack.json", encoding="utf-8"))
K = json.load(open("kurallar.json", encoding="utf-8"))
k = katman(K, A)
eq((k["name"], k["domain"]), ("Pafta tespit kapsamı", "enterprise-attack"), "katman adı ve alanı")
eq([(t["techniqueID"], t["score"]) for t in k["techniques"]],
   [("T1003.001", 1), ("T1053.005", 1), ("T1059", 1), ("T1059.001", 2), ("T1078", 1), ("T1547.001", 1), ("T1566.001", 1)],
   "yedi teknik; T1059.001'i iki kural (biri eski T1086 etiketiyle) kapsıyor")
eq(next(t["comment"] for t in k["techniques"] if t["techniqueID"] == "T1059.001"),
   "Eski PowerShell kuralı; PowerShell kodlanmış komut", "yorum: kural adları sıralı")
json.dumps(k)
O = ["T1059.001", "T1003.001", "T1003.006", "T1021.001", "T1086", "T1547", "T1547.009", "T1021"]
eq(bosluklar(K, A, O), ["T1003.006", "T1021.001", "T1547.009", "T1021"],
   "T1086 = T1059.001 kapsanıyor; T1547 alt tekniğiyle kapsanıyor; T1547.009 ayrı bir alt teknik; hiç kapsanmayan üst teknik T1021 boşluk")
eq(bosluklar([], A, ["T1021.001", "T1086"]), ["T1021.001", "T1059.001"], "kural yoksa hepsi boşluk; emekli kimlik yeni adıyla raporlanır")
```

```solution
import json
import re

attack = json.load(open("attack.json", encoding="utf-8"))


def teknikler(etiketler, attack):
    etkin = {t["id"] for t in attack["teknikler"]}
    sonuc = set()
    for etiket in etiketler:
        m = re.fullmatch(r"attack\.(t\d{4}(?:\.\d{3})?)", etiket.lower())
        if not m:
            continue
        kimlik = attack["emekli"].get(m.group(1).upper(), m.group(1).upper())
        if kimlik in etkin:
            sonuc.add(kimlik)
    return sorted(sonuc)


def katman(kurallar, attack):
    kimin = {}
    for k in kurallar:
        for t in teknikler(k["tags"], attack):
            kimin.setdefault(t, []).append(k["title"])
    return {"name": "Pafta tespit kapsamı", "domain": "enterprise-attack",
            "techniques": [{"techniqueID": t, "score": len(adlar), "comment": "; ".join(sorted(adlar))}
                           for t, adlar in sorted(kimin.items())]}


def bosluklar(kurallar, attack, oncelik):
    kapsanan = {t for k in kurallar for t in teknikler(k["tags"], attack)}
    ustler = {t.split(".")[0] for t in kapsanan}
    sonuc = []
    for kimlik in oncelik:
        kimlik = attack["emekli"].get(kimlik, kimlik)
        if kimlik in kapsanan or ("." not in kimlik and kimlik in ustler):
            continue
        sonuc.append(kimlik)
    return sonuc
```

```hint
`katman` için önce teknik → kural adları sözlüğü kur (`setdefault(t, []).append(...)`), sonra kimliğe göre sıralı öğeler üret.
```

```hint
`bosluklar` için iki küme: kapsanan kimlikler ve onların üst teknikleri (`t.split(".")[0]`). Öncelik kimliği nokta içermiyorsa (üst teknik) ikincisine, içeriyorsa yalnız birincisine bak.
```

```setup
import json
kurallar = [
    {"title": "PowerShell kodlanmış komut", "tags": ["attack.execution", "attack.t1059.001"]},
    {"title": "Eski PowerShell kuralı", "tags": ["attack.execution", "attack.t1086"]},
    {"title": "LSASS bellek erişimi", "tags": ["attack.credential-access", "attack.t1003.001"]},
    {"title": "Zamanlanmış görev", "tags": ["attack.persistence", "attack.T1053.005"]},
    {"title": "Eski kural, kullanım dışı teknik", "tags": ["attack.t1026"]},
    {"title": "Hatalı etiketler", "tags": ["attack.t9999", "cve.2021-44228", "attack.t1059.01"]},
    {"title": "Geçerli hesap kullanımı", "tags": ["attack.t1078"]},
    {"title": "Oltalama eki", "tags": ["attack.initial-access", "attack.t1566.001"]},
    {"title": "Komut yorumlayıcı", "tags": ["attack.t1059"]},
    {"title": "Run anahtarı", "tags": ["attack.persistence", "attack.t1547.001"]},
]
json.dump(kurallar, open("kurallar.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::
