---
id: pu13
title: Atomic Red Team / Caldera · Rakip Öykünmesi Planı ve Tespit Kapsamı
summary: Gerçek Atomic test YAML'ı ve Caldera ability alanlarını komut çalıştırmadan incelemek; prerequisites, executor, input_arguments ve cleanup sözleşmesini doğrulamak; sentetik kayıtlarla beklenen telemetri ile detection coverage/gap raporu üretmek.
timeout: 60
---

::: anlat Öykünme planı, saldırı yürütme değildir
Rakip öykünmesinde savunma ekibi önce **ne yapılacağını ve hangi kanıtın beklendiğini** yazar. Atomic Red Team tek tek teknik testleri, Caldera ise ability adımlarını bir operasyon akışına bağlayabilir. Bu derste amaç iki aracın veri sözleşmesini karşılaştırmak ve ölçüm planını denetlemektir.

> [!GÜVENLİK]
> Bu pafta **hiçbir Atomic testini, Caldera ability'sini, komutunu veya cleanup adımını çalıştırmaz**. Araçların kurulu, yapılandırılmış veya daha önce çalıştırılmış olduğu iddia edilmez. Ajan başlatılmaz, paket kurulmaz, ağ bağlantısı açılmaz ve gerçek telemetri toplanmaz. Bütün olaylar sentetiktir; komut metinleri yalnız incelenen veridir.

Gerçek ortamda yetki, izolasyon, platform ve sürüm farkları ayrıca değerlendirilir. Bir YAML'ın varlığı testin çalıştığını; bir olayın varlığı saldırının başarılı olduğunu; bir kural eşleşmesi de saldırının engellendiğini kanıtlamaz.
:::

::: anlat Atomic ve Caldera sözleşmesini alan alan oku
`emulation/atomic_test.yaml` içinde Atomic'in olağan yapısı vardır: üstte `attack_technique`, altında `atomic_tests`; her testte benzersiz `auto_generated_guid`, `supported_platforms`, `input_arguments`, `dependencies` ve `executor` bulunur. `input_arguments` girdilerinin adı, türü ve varsayılanı vardır. Komutlardaki `#{output_file}` yer tutucusu çalıştırma öncesinde bağlanır. `dependencies` içindeki `prereq_command` ön koşulu sınar, `get_prereq_command` eksik gereksinimi sağlamaya yönelik araç tanımıdır; ikisini de bu ders çalıştırmaz.

`emulation/caldera_ability.yaml` içinde ability kimliği, `tactic`, `technique_id` ve `platforms → windows → psh` yoluyla executor'a özgü `command`/`cleanup` görülür. Caldera değişkenleri yine `#{...}` biçimindedir. `requirements` doğrudan mapping değil, **liste**dir. İlk öğe `requirements[0]`, tek anahtarlı `{plugins.stockpile.app.requirements.basic: [...]}` mapping'idir; modülün liste değeri doğrudan ilişki öğelerini taşır ve her öğede `source`, `edge`, `target` alanları bulunur. Yani gerçek yol `requirements[0] → plugins.stockpile.app.requirements.basic → source/edge/target` biçimindedir; arada ayrıca bir `relationship_match` katmanı yoktur. Atomic'in `dependency_executor_name` alanı ile Caldera'nın platform altındaki executor anahtarı aynı düzeyde değildir; raporda ikisini ayrı sakla.

| Denetim | Atomic karşılığı | Caldera karşılığı | Savunma sorusu |
|---|---|---|---|
| Kimlik ve teknik | `auto_generated_guid`, `attack_technique` | `id`, `technique_id` | Aynı teknik ve sürüm mü izleniyor? |
| Ön koşul | `dependencies`, `prereq_command` | `requirements` | Koşul sağlanmadıysa adım atlandı mı? |
| Yürütücü ve girdi | `executor.name`, `input_arguments` | platform altındaki `psh` vb., `#{...}` | Gerekli bağlamalar eksiksiz mi? |
| Temizlik | `executor.cleanup_command` | executor altında `cleanup` | Plan temizliği tanımlıyor mu? |
| Ölçüm | YAML'dan ayrı tasarlanır | ability'den ayrı tasarlanır | Hangi telemetri ve kural bekleniyor? |

`source_contract.json`, bu iki YAML'dan **elle çıkarılmış** küçük bir dizindir; Atomic/Caldera doğrulama çıktısı değildir. Ders genel amaçlı YAML ayrıştırıcısı yazdırmaz. Plan doğrulaması bu dürüst, sınırlı JSON sözleşmesini kullanır.
:::

::: tahmin Ön koşulu olmayan adım beklenen telemetri üretir mi?
```python
adimlar = [
    {"id": "A", "prereq": "met"},
    {"id": "B", "prereq": "unmet"},
]
beklenen = [a["id"] for a in adimlar if a["prereq"] == "met"]
print(beklenen)
```

???

Yalnız `['A']` yazdırılır. Ön koşulu sağlanmayan B adımı için telemetri beklemek, ölçümü yapay bir boşluğa çevirir. Öte yandan “telemetri yok” ile “adım planlı olarak atlandı” ayrımı raporda korunmalıdır.
:::

::: gorev 1 · Planı Atomic/Caldera sözleşmesiyle doğrula
`plan_dogrula(plan, sozlesme)` işlevini yaz. Hiçbir komut çalıştırmadan sıralı hata metinleri döndür; geçerli planda sonuç `[]` olur. Her hata `step_id:kod` biçimindedir. `schema_version != 1` ise ayrıca `plan:schema` ekle.

Her adımda şunları denetle:

- Atomic GUID ve ability ID sözleşmede bulunmalı; yoksa sırasıyla `atomic-bilinmiyor` veya `ability-bilinmiyor`. Bilinmeyen kimliğin alt alanlarını okumaya çalışma.
- Adımın tekniği iki sözleşmeyle de aynı olmalı (`teknik-uyusmuyor`); platform iki tarafça da desteklenmeli (`platform-uyusmuyor`).
- Atomic `executor` ve Caldera `caldera_executor` ilgili sözleşmede olmalı (`executor-uyusmuyor`).
- Atomic'in bütün `required_arguments` değerleri `input_bindings` içinde **boş olmayan** değerlerle bağlanmalı (`girdi-eksik`).
- Plan prerequisite kimlikleri Atomic sözleşmesindeki küme olmalı (`prereq-bilinmiyor`); durumlar yalnız `met`, `unmet`, `unknown` olabilir (`prereq-durum`).
- Hem adımda hem iki kaynak sözleşmede cleanup bildirimi doğru olmalı (`cleanup-eksik`).

Aynı hatayı tekrar ekleme. Kimlikleri eşleştirirken GUID'yi test adıyla değiştirme; ability executor'ını Atomic executor listesiyle karşılaştırma.

```starter
from emulation_lab import json_yukle
plan = json_yukle("emulation/plan.json")
sozlesme = json_yukle("emulation/source_contract.json")

def plan_dogrula(plan, sozlesme):
    return []

print(plan_dogrula(plan, sozlesme))
```

```test
import copy
need("plan_dogrula")
eq(plan_dogrula(plan, sozlesme), [], "referans plan geçerli")
x = copy.deepcopy(plan); x["schema_version"] = 2
eq(plan_dogrula(x, sozlesme), ["plan:schema"], "şema sürümü")
x = copy.deepcopy(plan); x["steps"][0]["atomic_guid"] = "yok"
eq(plan_dogrula(x, sozlesme), ["step-001:atomic-bilinmiyor"], "bilinmeyen Atomic kimliği alt alan okumaz")
x = copy.deepcopy(plan); x["steps"][0]["ability_id"] = "yok"
eq(plan_dogrula(x, sozlesme), ["step-001:ability-bilinmiyor"], "bilinmeyen ability kimliği alt alan okumaz")
x = copy.deepcopy(plan); x["steps"][0]["technique"] = "T1003"
eq(plan_dogrula(x, sozlesme), ["step-001:teknik-uyusmuyor"], "ATT&CK tekniği iki kaynakla eşleşir")
x = copy.deepcopy(plan); x["steps"][0]["platform"] = "linux"
eq(plan_dogrula(x, sozlesme), ["step-001:platform-uyusmuyor"], "platform her iki sözleşmede gerekli")
x = copy.deepcopy(plan); x["steps"][0]["executor"] = "cmd"
eq(plan_dogrula(x, sozlesme), ["step-001:executor-uyusmuyor"], "Atomic executor denetimi")
x = copy.deepcopy(plan); x["steps"][0]["caldera_executor"] = "powershell"
eq(plan_dogrula(x, sozlesme), ["step-001:executor-uyusmuyor"], "Caldera executor kendi listesiyle denetlenir")
x = copy.deepcopy(plan); x["steps"][0]["input_bindings"]["output_file"] = ""
eq(plan_dogrula(x, sozlesme), ["step-001:girdi-eksik"], "boş input argument bağlama değildir")
x = copy.deepcopy(plan); x["steps"][0]["prerequisites"] = [{"id": "uydurma", "status": "met"}]
eq(plan_dogrula(x, sozlesme), ["step-001:prereq-bilinmiyor"], "ön koşul kimliği sözleşmeden gelir")
x = copy.deepcopy(plan); x["steps"][0]["prerequisites"][0]["status"] = "belki"
eq(plan_dogrula(x, sozlesme), ["step-001:prereq-durum"], "ön koşul durumları kapalı kümedir")
x = copy.deepcopy(plan); x["steps"][0]["cleanup_declared"] = False
eq(plan_dogrula(x, sozlesme), ["step-001:cleanup-eksik"], "cleanup planda zorunlu")
x = copy.deepcopy(sozlesme); x["atomics"][plan["steps"][0]["atomic_guid"]]["cleanup_declared"] = False
eq(plan_dogrula(plan, x), ["step-001:cleanup-eksik", "step-002-prereq-yok:cleanup-eksik"], "kaynak Atomic cleanup eksikliği iki adımda görülür")
x = copy.deepcopy(sozlesme); x["abilities"][plan["steps"][0]["ability_id"]]["cleanup_declared"] = False
eq(plan_dogrula(plan, x), ["step-001:cleanup-eksik", "step-002-prereq-yok:cleanup-eksik"], "kaynak ability cleanup eksikliği iki adımda görülür")
```

```solution
from emulation_lab import json_yukle
plan = json_yukle("emulation/plan.json")
sozlesme = json_yukle("emulation/source_contract.json")

def plan_dogrula(plan, sozlesme):
    hatalar = set()
    if plan.get("schema_version") != 1:
        hatalar.add("plan:schema")
    for adim in plan["steps"]:
        sid = adim["step_id"]
        atomic = sozlesme["atomics"].get(adim.get("atomic_guid"))
        ability = sozlesme["abilities"].get(adim.get("ability_id"))
        if atomic is None:
            hatalar.add(f"{sid}:atomic-bilinmiyor")
        if ability is None:
            hatalar.add(f"{sid}:ability-bilinmiyor")
        if atomic is not None:
            if adim.get("technique") != atomic["technique"]:
                hatalar.add(f"{sid}:teknik-uyusmuyor")
            if adim.get("platform") not in atomic["platforms"]:
                hatalar.add(f"{sid}:platform-uyusmuyor")
            if adim.get("executor") not in atomic["executors"]:
                hatalar.add(f"{sid}:executor-uyusmuyor")
            baglamalar = adim.get("input_bindings", {})
            if any(not baglamalar.get(ad) for ad in atomic["required_arguments"]):
                hatalar.add(f"{sid}:girdi-eksik")
            prereqs = adim.get("prerequisites", [])
            if {p.get("id") for p in prereqs} != set(atomic["prerequisites"]):
                hatalar.add(f"{sid}:prereq-bilinmiyor")
            if any(p.get("status") not in {"met", "unmet", "unknown"} for p in prereqs):
                hatalar.add(f"{sid}:prereq-durum")
            if not adim.get("cleanup_declared") or not atomic["cleanup_declared"]:
                hatalar.add(f"{sid}:cleanup-eksik")
        if ability is not None:
            if adim.get("technique") != ability["technique"]:
                hatalar.add(f"{sid}:teknik-uyusmuyor")
            if adim.get("platform") not in ability["platforms"]:
                hatalar.add(f"{sid}:platform-uyusmuyor")
            if adim.get("caldera_executor") not in ability["executors"]:
                hatalar.add(f"{sid}:executor-uyusmuyor")
            if not adim.get("cleanup_declared") or not ability["cleanup_declared"]:
                hatalar.add(f"{sid}:cleanup-eksik")
    return sorted(hatalar)

print(plan_dogrula(plan, sozlesme))
```

```hint
Sözlük `.get()` ile kimliği bul; sonuç `None` ise yalnız kimlik hatası ekle. Hataları kümeye yazıp `sorted` ile döndür. Girdi için `all(baglamalar.get(ad) ...)` koşulunun tersini kullan.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from emulation_lab import hazirla
hazirla()
```
:::

::: gorev 2 · Beklenen telemetriyi ön koşul sonucuyla üret
`beklenen_telemetri(adimlar)` işlevini yaz. Yalnız **bütün prerequisite durumları `met`** olan adımları planlı yürütme adayı say. `unmet` veya `unknown` varsa o adımın beklenen gözlemlerini sonuca katma; bu bir komut çalıştırma değildir.

Her `expected_observations` öğesini kopyala, `step_id` ekle ve liste döndür. Alanları koru; kaynak gözlemi değiştirme. Sonucu `(step_id, kind, source, event_id)` ile sırala. Bu liste henüz gerçekleşmiş olay değil, **ölçüm beklentisidir**.

```starter
from emulation_lab import json_yukle
plan = json_yukle("emulation/plan.json")

def beklenen_telemetri(adimlar):
    return [dict(o, step_id=a["step_id"]) for a in adimlar for o in a["expected_observations"]]

print(beklenen_telemetri(plan["steps"]))
```

```test
import copy
need("beklenen_telemetri")
b = beklenen_telemetri(plan["steps"])
eq(len(b), 2, "unmet ikinci adım beklenen telemetri üretmez")
eq([(x["step_id"], x["kind"], x["event_id"]) for x in b],
   [("step-001", "artifact", 11), ("step-001", "process", 1)], "gözlem alanları ve kararlı sıra")
x = copy.deepcopy(plan["steps"]); x[1]["prerequisites"][0]["status"] = "met"
eq(len(beklenen_telemetri(x)), 3, "koşul met olunca ikinci adımın bir beklentisi eklenir")
x = copy.deepcopy(plan["steps"]); x[0]["prerequisites"][0]["status"] = "unknown"
eq([x["step_id"] for x in beklenen_telemetri(x)], [], "unknown da met değildir")
x = copy.deepcopy(plan["steps"]); x[0]["expected_observations"][1]["technique"] = "T9999"
eq(beklenen_telemetri(x)[0]["technique"], "T9999", "beklenti kaynağı değiştirilmeden kopyalanır")
```

```solution
from emulation_lab import json_yukle
plan = json_yukle("emulation/plan.json")

def beklenen_telemetri(adimlar):
    sonuc = []
    for adim in adimlar:
        if not adim.get("prerequisites") or any(p.get("status") != "met" for p in adim["prerequisites"]):
            continue
        for gozlem in adim.get("expected_observations", []):
            sonuc.append(dict(gozlem, step_id=adim["step_id"]))
    return sorted(sonuc, key=lambda o: (o["step_id"], o["kind"], o["source"], o["event_id"]))

print(beklenen_telemetri(plan["steps"]))
```

```hint
Önce adımı süz: prerequisite listesi boşsa ya da herhangi bir durum `met` değilse `continue`. Gözlemi `dict(gozlem, step_id=...)` ile kopyala.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from emulation_lab import hazirla
hazirla()
```
:::

::: gorev 3 · Detection coverage ve gap ölç
`kapsam_raporu(beklenen, olaylar, kurallar)` işlevini yaz. Beklenen her gözlemi `step_id + kind + source + event_id + technique` beşlisiyle sentetik olaya eşle. Kural eşleşmesinde `source + event_id + technique` kullan; `step_id` ve `kind` kural alanı değildir.

Dönüş sözlüğü:

```text
{"toplam": int, "gozlenen": int, "tespit": int,
 "kapsam_yuzdesi": float,
 "bosluklar": [{"step_id", "kind", "source", "event_id", "technique", "neden"}]}
```

- Olay ve kural birlikte varsa tespit sayılır.
- Olay var, kural yoksa `kural-yok` boşluğu üret.
- Olay yoksa kural olsa bile `telemetri-yok` boşluğu üret; tespit sayma.
- `kapsam_yuzdesi = 100 * tespit / toplam`, bir ondalığa yuvarlanır; sıfır beklentide `0.0`.
- Plana ait olmayan olaylar kapsamı artırmaz. Boşlukları `(step_id, kind, source, event_id)` ile sırala.

Buradaki oran **yalnız bu sentetik beklenti kümesinin detection coverage** değeridir; gerçek saldırı başarısı, engelleme oranı veya bütün ATT&CK kapsamı değildir.

```starter
from emulation_lab import json_yukle, olaylari_yukle
plan = json_yukle("emulation/plan.json")
olaylar = olaylari_yukle("emulation/telemetry.jsonl")
kurallar = json_yukle("emulation/rules.json")

def kapsam_raporu(beklenen, olaylar, kurallar):
    return {"toplam": len(beklenen), "gozlenen": len(olaylar), "tespit": len(kurallar),
            "kapsam_yuzdesi": 100.0, "bosluklar": []}

beklenen = [dict(o, step_id=plan["steps"][0]["step_id"]) for o in plan["steps"][0]["expected_observations"]]
print(kapsam_raporu(beklenen, olaylar, kurallar))
```

```test
import copy
need("kapsam_raporu")
b = [dict(o, step_id=plan["steps"][0]["step_id"]) for o in plan["steps"][0]["expected_observations"]]
beklenen_rapor = {
    "toplam": 2, "gozlenen": 2, "tespit": 1, "kapsam_yuzdesi": 50.0,
    "bosluklar": [{"step_id": "step-001", "kind": "artifact", "source": "synthetic_artifact",
                   "event_id": 11, "technique": "T1059.001", "neden": "kural-yok"}]
}
eq(kapsam_raporu(b, olaylar, kurallar), beklenen_rapor, "iki olaydan yalnız process kuralı tespit; artifact gap")
x = [o for o in olaylar if not (o["step_id"] == "step-001" and o["kind"] == "artifact")]
r = kapsam_raporu(b, x, kurallar)
eq((r["toplam"], r["gozlenen"], r["tespit"], r["kapsam_yuzdesi"]), (2, 1, 1, 50.0), "eksik olay gözlenen ve tespit sayılmaz")
eq(r["bosluklar"][0]["neden"], "telemetri-yok", "olay yokluğu kural yokluğuyla karışmaz")
x = copy.deepcopy(kurallar); x[0]["event_id"] = 999
r = kapsam_raporu(b, olaylar, x)
eq((r["tespit"], r["kapsam_yuzdesi"], sorted(g["neden"] for g in r["bosluklar"])),
   (0, 0.0, ["kural-yok", "kural-yok"]), "kural alanları tam eşleşmeli")
r = kapsam_raporu(b, [olaylar[-1]], [])
eq((r["gozlenen"], r["tespit"], len(r["bosluklar"])), (0, 0, 2), "ilgisiz olay kapsam üretmez")
process = next(x for x in b if x["kind"] == "process")
dogru_olay = next(o for o in olaylar if o["step_id"] == process["step_id"] and o["kind"] == "process")
for alan, yanlis_deger in (("source", "synthetic_baska"), ("event_id", 999), ("technique", "T9999")):
    yanlis_olay = dict(dogru_olay); yanlis_olay[alan] = yanlis_deger
    r = kapsam_raporu([process], [yanlis_olay], kurallar)
    eq((r["gozlenen"], r["tespit"], r["kapsam_yuzdesi"]), (0, 0, 0.0),
       f"aynı step/kind altında yanlış {alan} olay eşleşmesi değildir")
    eq(r["bosluklar"][0]["neden"], "telemetri-yok", f"yanlış {alan} telemetri boşluğu olarak kalır")
eq(kapsam_raporu([], olaylar, kurallar),
   {"toplam": 0, "gozlenen": 0, "tespit": 0, "kapsam_yuzdesi": 0.0, "bosluklar": []}, "sıfırda bölme yok")
```

```solution
from emulation_lab import json_yukle, olaylari_yukle
plan = json_yukle("emulation/plan.json")
olaylar = olaylari_yukle("emulation/telemetry.jsonl")
kurallar = json_yukle("emulation/rules.json")

def beklenen_telemetri(adimlar):
    sonuc = []
    for adim in adimlar:
        if not adim.get("prerequisites") or any(p.get("status") != "met" for p in adim["prerequisites"]):
            continue
        for gozlem in adim.get("expected_observations", []):
            sonuc.append(dict(gozlem, step_id=adim["step_id"]))
    return sorted(sonuc, key=lambda o: (o["step_id"], o["kind"], o["source"], o["event_id"]))

def kapsam_raporu(beklenen, olaylar, kurallar):
    bosluklar = []
    gozlenen = 0
    tespit = 0
    for b in beklenen:
        olay_var = any(all(o.get(k) == b[k] for k in ("step_id", "kind", "source", "event_id", "technique"))
                       for o in olaylar)
        kural_var = any(all(k.get(a) == b[a] for a in ("source", "event_id", "technique"))
                        for k in kurallar)
        if olay_var:
            gozlenen += 1
        if olay_var and kural_var:
            tespit += 1
            continue
        bosluklar.append({k: b[k] for k in ("step_id", "kind", "source", "event_id", "technique")} |
                         {"neden": "telemetri-yok" if not olay_var else "kural-yok"})
    toplam = len(beklenen)
    return {"toplam": toplam, "gozlenen": gozlenen, "tespit": tespit,
            "kapsam_yuzdesi": round(100 * tespit / toplam, 1) if toplam else 0.0,
            "bosluklar": sorted(bosluklar, key=lambda g: (g["step_id"], g["kind"], g["source"], g["event_id"]))}

print(kapsam_raporu(beklenen_telemetri(plan["steps"]), olaylar, kurallar))
```

```hint
Her beklenti için iki bağımsız `any(...)` hesapla: beş alanlı olay eşleşmesi ve üç alanlı kural eşleşmesi. Yalnız ikisi birden doğruysa `tespit` artar; boşluk nedeni olayın yokluğuna göre seçilir.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from emulation_lab import hazirla
hazirla()
```
:::

::: anlat Ölçümü kanıt sınırıyla kapat
Bu fixture'daki sonuç iki beklenen telemetriden ikisinin de sentetik olayının bulunduğunu, yalnız birinin sentetik kuralla eşleştiğini gösterir: **%50 detection coverage**. Diğer satır `kural-yok` gap'idir. Ön koşulu `unmet` olan ikinci adım paydaya girmez; bu, onun güvenli veya tespit edilmiş olduğu anlamına gelmez.

Gerçek çalışmada aynı rapora araç/sürüm, yetki, zaman penceresi, log kaybı, prerequisite sonucu, executor çıkışı ve cleanup sonucu ayrı kanıtlar olarak eklenir. PU01'deki ATT&CK kapsamı ile PU02'deki kanıt disiplinini birleştir: coverage ölçümünü yalnız tanımlı evren için yorumla, gap'i iyileştirme işine çevir ve çalıştırılmamış hiçbir adımı başarılı öykünme gibi sunma.
:::
