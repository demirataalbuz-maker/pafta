---
id: bt07
title: Madde 103 · Saldırı Zinciri ve Kanıt Üretimi
summary: Sabit UTC ve run_id ile kurgusal web/AD olaylarını normalize et; adım→ATT&CK eşlemesi, beklenen kanıt/tespit, negatif kontroller, KQL/SPL girdileri ve SHA-256 manifestiyle tekrarlanabilir kanıt demeti üret.
---

::: anlat Önce sınır: bu bir canlandırmadır
Bu pafta **gerçek bir saldırı gerçekleştirmez**. Web istekleri ve Active Directory olayları önceden tanımlı, kurgusal kayıtlardır. Üretici dış ağa bağlanmaz; parola veya token içermez; uzaktan kod yürütmez ve kalıcılık kurmaz. Amaç, savunma tarafında bir zincirin hangi kanıtlarla görülebileceğini tekrarlanabilir biçimde göstermektir.

`tracks/bitirme/veri/scenario.json` dört şeyi sabitler:

- bütün zamanlar için UTC (`...Z`) ve tek `run_id`;
- kurgusal host, hesap ve adresler;
- her adımın ATT&CK tekniği;
- beklenen kanıt kimlikleri ve tespit adı.

`negative_controls.json` içindeki olağan olaylar aynı normalize akışta bulunur ama `attack_technique` ve `detection_id` alanları boştur. Böylece kuralın yalnız “olay bulmayı” değil, yanlış alarmı dışlamayı da göstermesi beklenir.

> [!GÜVENLİK]
> Çıktıların tamamı sentetiktir. `203.0.113.10` belgeleme adresidir; hiçbir istek bu adrese gönderilmez.
:::

::: anlat Tek üretim, birkaç tüketim biçimi
Üretici kaynak web ve AD kayıtlarını NDJSON olarak, AD kayıtlarının kararlı alanlarını ayrıca XML olarak yazar. EVTX gerekli değildir: normalize NDJSON/XML, büyük ikili üretmeden aynı kanıtı taşır. Ortak normalize kayıtlar `normalized.jsonl` içine girer; aynı kayıtlar KQL için CSV, SPL için JSONL biçiminde de sunulur.

```bash norun
python sandbox/saldiri_zinciri_lab.py uret --senaryo tracks/bitirme/veri/scenario.json --cikti tracks/bitirme/veri/cikti
python sandbox/saldiri_zinciri_lab.py dogrula --senaryo tracks/bitirme/veri/scenario.json --cikti tracks/bitirme/veri/cikti
```

İki ayrı üretimde `normalized.jsonl` ve diğer bütün dosyalar bayt bayt aynıdır. `manifest.sha256.json` her kanıt dosyasının boyutunu ve SHA-256 özetini tutar. Doğrulama yalnız özete güvenmez: dosyaları senaryodan yeniden üretip içerikleri de karşılaştırır. Bu yüzden bozulan dosyanın manifestteki özeti güncellense bile tutarsızlık reddedilir.

```python
import hashlib
print(hashlib.sha256(b"sentetik-kanit").hexdigest())
```

Özel kanıt CLI'si mevcut ortak runner'a bağlı değildir; aşağıdaki görevler dersin Python koşucusunda normalize etme ve özet doğrulama mantığını çalıştırır.
:::

::: tahmin Negatif kontrol hangi satırı değiştirir?
Kod, pozitif ve negatif iki normalize kaydı ayırdığında ne yazdırır?

```python
import json
import sys
kayitlar = [json.loads(s) for s in sys.stdin.read().splitlines()]
print(sum(not k["is_negative"] for k in kayitlar))
print(sum(bool(k["detection_id"]) for k in kayitlar))
```

```stdin
{"event_id":"W001","is_negative":false,"detection_id":"BT01-D01"}
{"event_id":"N001","is_negative":true,"detection_id":""}
```

???

İlk satır **`1`**, ikinci satır **`1`** yazdırır. Negatif kontrol kanıt akışında kalır ama saldırı zincirine veya tespit sayısına eklenmez. Negatif kaydı silmek yerine işaretlemek, yanlış alarm denetimini mümkün kılar.
:::

::: gorev 1 · Pozitif zinciri normalize et
Standart girdideki NDJSON kayıtlarını `timestamp`, sonra `event_id` sırasına diz. Yalnız `is_negative` değeri `false` olanlar için `<event_id>|<attack_technique>` yazdır. Negatif kontrolü çıktıya katma.

```starter
import json
import sys
kayitlar = [json.loads(s) for s in sys.stdin.read().splitlines()]
for k in kayitlar:
    print(k["event_id"] + "|" + k["attack_technique"])
```

```stdin
{"timestamp":"2026-10-26T10:01:00Z","event_id":"A001","attack_technique":"T1078","is_negative":false}
{"timestamp":"2026-10-26T09:55:00Z","event_id":"N001","attack_technique":"","is_negative":true}
{"timestamp":"2026-10-26T10:01:00Z","event_id":"W001","attack_technique":"T1078","is_negative":false}
```

```test
eq(out, "A001|T1078\nW001|T1078\n", "Pozitif kanıtlar zaman/event_id sırasıyla; negatif kontrol yok")
EK = ('{"timestamp":"2026-10-26T10:02:00Z","event_id":"X009","attack_technique":"T9999","is_negative":true}\n'
      '{"timestamp":"2026-10-26T10:03:00Z","event_id":"W005","attack_technique":"","is_negative":false}\n')
eq(run(girdi.rstrip("\n") + "\n" + EK), "A001|T1078\nW001|T1078\nW005|\n",
   "Technique dolu negatif kayıt dışlanmalı; technique boş pozitif kayıt korunmalı")
```

```solution
import json
import sys
kayitlar = [json.loads(s) for s in sys.stdin.read().splitlines()]
for k in sorted(kayitlar, key=lambda k: (k["timestamp"], k["event_id"])):
    if not k["is_negative"]:
        print(k["event_id"] + "|" + k["attack_technique"])
```

```hint
`sorted(..., key=lambda k: (k["timestamp"], k["event_id"]))` kullan; yazdırmadan önce `if not k["is_negative"]` koşulunu ekle.
```
:::

::: gorev 2 · SHA-256 bütünlüğünü denetle
Girdi, her biri `path`, `content` ve `sha256` alanlarına sahip bir JSON listesidir. Her içeriğin UTF-8 baytları üzerinden SHA-256 özetini hesapla. Bütün özetler beklenenle aynıysa `2/2 SAĞLAM`, en az bir fark varsa `BUTUNLUK BOZUK` yazdır. Bu küçük görev yalnız özet denetimini gösterir; capstone CLI'si ayrıca dosya listesini, boyutu ve senaryodan beklenen içeriği de doğrular.

```starter
import json
import sys
kayitlar = json.loads(sys.stdin.read())
print(str(len(kayitlar)) + "/2 SAĞLAM")
```

```stdin
[{"path":"web.ndjson","content":"sentetik-web\n","sha256":"2aaec08f06dbd3c4954d042ea89ae973238616d4e92cac453893a6ee5706f3f1"},{"path":"ad.ndjson","content":"sentetik-ad\n","sha256":"9bc30e3d835722b83e5028f0d94e6c7a9a8d3643c66045f17b4f07241041f4ad"}]
```

```test
eq(out, "2/2 SAĞLAM\n", "İki içeriğin SHA-256 özeti de doğrulanmalı")
BOZUK = girdi.replace("9bc30e3d835722b83e5028f0d94e6c7a9a8d3643c66045f17b4f07241041f4ad", "0" * 64)
eq(run(BOZUK), "BUTUNLUK BOZUK\n", "Bozuk hash manifesti sağlam sayılamaz")
DEGISTIRILMIS = girdi.replace("sentetik-ad", "degistirilmis-ad")
eq(run(DEGISTIRILMIS), "BUTUNLUK BOZUK\n", "İçerik değişip özet aynı kaldığında bütünlük bozulmalı")
```

```solution
import hashlib
import json
import sys
kayitlar = json.loads(sys.stdin.read())
saglam = sum(hashlib.sha256(k["content"].encode("utf-8")).hexdigest() == k["sha256"] for k in kayitlar)
print(str(saglam) + "/2 SAĞLAM" if saglam == len(kayitlar) else "BUTUNLUK BOZUK")
```

```hint
`k["content"].encode("utf-8")` üzerinden `hashlib.sha256(...).hexdigest()` hesapla ve kayıttaki `sha256` ile karşılaştır.
```
:::

::: gorev 3 · Beklenen kanıtı kapat
Girdi, her adımda `step_id`, `expected_evidence` ve `observed_evidence` bulunan bir JSON listesidir. Her adımda beklenen kümenin gözlenen kümenin alt kümesi olup olmadığını denetle. Eksik kanıt varsa `REDDEDILDI:<step_id>`; bütün adımlar tamamsa `ZINCIR TAM` yazdır.

```starter
import json
import sys
adimlar = json.loads(sys.stdin.read())
print("ZINCIR TAM")
```

```stdin
[{"step_id":"oturum","expected_evidence":["W001","A001"],"observed_evidence":["W001","A001"]},{"step_id":"derleme","expected_evidence":["W003","A003"],"observed_evidence":["A003","W003","N003"]}]
```

```test
eq(out, "ZINCIR TAM\n", "Fazladan negatif kanıt zararsız; beklenenlerin ikisi de var")
EKSIK = '[{"step_id":"oturum","expected_evidence":["W001","A001"],"observed_evidence":["W001","A001"]},{"step_id":"derleme","expected_evidence":["W003","A003"],"observed_evidence":["W003"]}]'
eq(run(EKSIK), "REDDEDILDI:derleme\n", "Eksik observed_evidence bulunan adım kimliğiyle reddedilmeli")
ILK_EKSIK = '[{"step_id":"oturum","expected_evidence":["W001","A001"],"observed_evidence":["A001"]},{"step_id":"derleme","expected_evidence":["W003"],"observed_evidence":["W003"]}]'
eq(run(ILK_EKSIK), "REDDEDILDI:oturum\n", "İlk eksik adımda durulmalı; sonraki adımlar hatayı gizlememeli")
```

```solution
import json
import sys
adimlar = json.loads(sys.stdin.read())
for a in adimlar:
    if not set(a["expected_evidence"]).issubset(a["observed_evidence"]):
        print("REDDEDILDI:" + a["step_id"])
        break
else:
    print("ZINCIR TAM")
```

```hint
`set(a["expected_evidence"]).issubset(a["observed_evidence"])` yanlışsa adım kimliğiyle reddet; `for` döngüsünün `else` dalı yalnız `break` olmadığında çalışır.
```
:::
