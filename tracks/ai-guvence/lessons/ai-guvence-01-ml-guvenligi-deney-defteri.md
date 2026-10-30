---
id: ai-guvence-01
title: ML Güvenliği Deney Defteri
summary: Veri, model, tehdit ve ölçütleri tanımla; tekrarlı ölçümleri doğrulayıp deney kapsamındaki eksikleri raporla.
timeout: 45
---

::: anlat Gerçek deney defteri biçimini bil, sentetik temsili ayırt et
Tekrarlanabilir ML güvenliği deneyinde veri, model, tehdit varsayımı, ölçütler ve rastgelelik tohumu önceden kaydedilir. Ölçüt listesi deneyin yalnız ortalama performansını mı yoksa saldırı ve yanlış pozitif davranışını mı izlediğini açık hale getirir. Tohum kaydı tek başına bütün donanım veya kütüphane farklarını ortadan kaldırmaz.

| Katman | Gerçek ML güvenliği deney kaydı ne içerir? | Bu ders ne kullanır? | Ne söyleyemez? |
|---|---|---|---|
| Deney planı | MLflow/Weights & Biases veya JSON manifest: veri hash'i, model hiperparametreleri, tehdit modeli, tohum ve hedef metrikler | İlk 3 görevde `veri/plan.json` sentetik manifesti; son görevde canlı `sklearn` sınıflandırıcı planı | Tek bir tohum ve sentetik veri kümesi üretim ortamındaki dağılım kaymasını (drift) kanıtlamaz |
| Tekrarlı ölçümler | Her tohum/katlama (fold) için kaydedilen `dogruluk`, `f1`, `asr`, `fpr` serileri | İlk 3 görevde `veri/olcumler.json` sentetik kayıtları; son görevde 3 farklı tohumla eğitilen gerçek `LogisticRegression` ölçümleri | Eksiksiz kapsam tablosu tek başına modelin tüm saldırılara dayanıklı olduğunu göstermez |

> [!NOT]
> İlk üç görevde örnek dosyalar çalışma klasörünün `veri/` altına kopyalanır: `veri/plan.json` ve `veri/olcumler.json` (tümü **sentetik**). Bu dosyaları kodundan okuyup inceleyebilirsin; ancak her çalıştırmada temiz kopya yeniden yazılır (**kalıcılık yoktur**). Kontrol adımı bu dosyalardan bağımsız gizli verilerle sınama yapar.
:::

::: anlat Kapsam her ölçüt ve tekrar çiftini gerektirir
Her ölçüm bir ölçüt, pozitif tekrar numarası ve sıfır ile bir arasındaki sonlu değer taşır. Aynı ölçüt-tekrar çifti iki kez yazılamaz. Kapsam raporunda plandaki her ölçüt için `1..beklenen_tekrar` aralığının tamamı aranır.

Eksik çiftler ölçütlerin plan sırası, sonra tekrar numarasıyla listelenir. Hiç eksik yoksa karar `tamam`, aksi halde `eksik` olur. Boş ölçüm listesi geçerli bir girdidir fakat dolu planda tamamlanmış deney anlamına gelmez.
:::

::: tahmin Ölçüt-tekrar kapsamını tahmin et
Üç çıktı satırını yaz:

```python
print(sorted([("f1", 1), ("dogruluk", 2)]))
print([(m, t) for m in ["f1"] for t in range(1, 3) if (m, t) not in {("f1", 1)}])
print(2 * 2)
```

???

```cikti
[('dogruluk', 2), ('f1', 1)]
[('f1', 2)]
4
```

Son satır iki ölçüt ve iki tekrar için beklenen kayıt sayısıdır.
:::

::: gorev 1 · Deney planını doğrula
`deney_plani_dogrula(plan)` işlevini yaz. Plan tam olarak `id`, `veri`, `model`, `tehdit`, `olcutler`, `tohum` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir.

Veri, model ve tehdit başı/sonu boşluğu olmayan boş olmayan stringdir ve kontrol karakteri içeremez. Ölçütler boş olmayan, yinelenmeyen listedir; öğeler `dogruluk`, `f1`, `asr`, `fpr` olabilir. Tohum bool olmayan, sıfır veya pozitif tamsayıdır. Geçersiz veride `ValueError` yükselt. Yeni sözlük ve yeni ölçüt listesiyle döndür; girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def deney_plani_dogrula(plan):
    # KUSURLU BAŞLANGIÇ KODU: şema ve alan doğrulaması yapmadan doğrudan girdi sözlüğünü döndürüyor!
    return plan

ornek_plan = json_yukle("veri/plan.json")
print("Örnek plan:", deney_plani_dogrula(ornek_plan))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-01")
```

```test
import copy
P = {"id": "d-1", "veri": "yelkovan.csv", "model": "logistic regression", "tehdit": "veri zehirleme", "olcutler": ["dogruluk", "f1"], "tohum": 0}
def sozlesme(fn):
    try:
        once = copy.deepcopy(P)
        sonuc = fn(P)
        if sonuc != P or P != once or sonuc is P or sonuc["olcutler"] is P["olcutler"]:
            return False
        if fn(dict(P, id="a" * 64, olcutler=["asr", "fpr"], tohum=42))["tohum"] != 42:
            return False
        for plan in [
            None, [], dict(P, ek=1), dict(P, id=""), dict(P, id="a b"), dict(P, id="a" * 65), dict(P, id=None),
            dict(P, veri=""), dict(P, veri=" x"), dict(P, veri="a\0b"), dict(P, veri=None),
            dict(P, model=""), dict(P, model="x "), dict(P, model="a\0b"),
            dict(P, tehdit=""), dict(P, tehdit=" x"), dict(P, tehdit="a\0b"),
            dict(P, olcutler=[]), dict(P, olcutler=None), dict(P, olcutler="f1"),
            dict(P, olcutler=["f1", "f1"]), dict(P, olcutler=["diger"]), dict(P, olcutler=[None]),
            dict(P, tohum=-1), dict(P, tohum=True), dict(P, tohum=1.0), dict(P, tohum=None),
        ]:
            try:
                fn(plan)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(deney_plani_dogrula), "plan şeması, metinler, ölçütler ve tohum korunmalı")
def m_olcut(plan):
    sonuc = deney_plani_dogrula(plan)
    sonuc["olcutler"] = ["asr"]
    return sonuc
def m_tohum(plan):
    sonuc = deney_plani_dogrula(plan)
    sonuc["tohum"] = 1
    return sonuc
def m_tehdit(plan):
    sonuc = deney_plani_dogrula(plan)
    sonuc["tehdit"] = "baska tehdit"
    return sonuc
for ad, mutant in [("ölçütleri değiştiren", m_olcut), ("tohumu değiştiren", m_tohum), ("tehdidi değiştiren", m_tehdit)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def deney_plani_dogrula(plan):
    import re
    if not isinstance(plan, dict):
        raise ValueError("plan sözlük olmalı")
    if set(plan) != {"id", "veri", "model", "tehdit", "olcutler", "tohum"}:
        raise ValueError("plan şeması geçersiz")
    if not isinstance(plan["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", plan["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("veri", "model", "tehdit"):
        deger = plan[alan]
        if not isinstance(deger, str):
            raise ValueError("metin alanı string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("metin boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("metin kontrol karakteri içeremez")
    olcutler = plan["olcutler"]
    if not isinstance(olcutler, list):
        raise ValueError("ölçütler liste olmalı")
    if not olcutler:
        raise ValueError("ölçütler boş olamaz")
    for olcut in olcutler:
        if olcut not in ("dogruluk", "f1", "asr", "fpr"):
            raise ValueError("ölçüt geçersiz")
    if len(set(olcutler)) != len(olcutler):
        raise ValueError("ölçütler yinelenemez")
    if isinstance(plan["tohum"], bool) or not isinstance(plan["tohum"], int):
        raise ValueError("tohum tamsayı olmalı")
    if plan["tohum"] < 0:
        raise ValueError("tohum negatif olamaz")
    return {"id": plan["id"], "veri": plan["veri"], "model": plan["model"], "tehdit": plan["tehdit"], "olcutler": list(olcutler), "tohum": plan["tohum"]}
```

```hint
Metin alanlarını aynı döngüde doğrula. Ölçütleri izin listesi ve yineleme yönünden, tohumu tür ve sıfır sınırı yönünden ayrı denetle.
```
:::

::: gorev 2 · Tekrarlı ölçümleri doğrula ve sırala
`olcumleri_dogrula(plan, olcumler)` işlevini yaz. Plan ilk görevdeki bütün kuralları sağlasın. Ölçümler liste olmalı; her kayıt tam olarak `olcut`, `tekrar`, `deger` alanlarını taşısın. Ölçüt plandaki listede bulunmalı, tekrar bool olmayan pozitif tamsayı, değer bool olmayan sonlu sayı ve `0 <= deger <= 1` aralığında olmalıdır.

Aynı `(olcut, tekrar)` çifti yinelenemez. Geçersiz veride `ValueError` yükselt. Kayıtları ölçüt adı ve tekrar numarasına göre sıralayıp yeni sözlüklerle döndür. Boş ölçüm listesinde boş liste döndür ve girdileri değiştirme.

```starter
from ai_guvence_veri import json_yukle

def olcumleri_dogrula(plan, olcumler):
    # KUSURLU BAŞLANGIÇ KODU: ölçümleri sıralamadan ve aralık/yinelenme denetimi yapmadan döndürüyor!
    return list(olcumler) if isinstance(olcumler, list) else []

print("Örnek ölçümler:", olcumleri_dogrula(json_yukle("veri/plan.json"), json_yukle("veri/olcumler.json")))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-01")
```

```test
import copy
P = {"id": "d-1", "veri": "yelkovan.csv", "model": "logistic regression", "tehdit": "veri zehirleme", "olcutler": ["dogruluk", "f1"], "tohum": 0}
O = [
    {"olcut": "f1", "tekrar": 1, "deger": 0.25},
    {"olcut": "dogruluk", "tekrar": 2, "deger": 0.75},
    {"olcut": "dogruluk", "tekrar": 1, "deger": 0.5},
]
BEKLENEN = [O[2], O[1], O[0]]
def sozlesme(fn):
    try:
        ponce = copy.deepcopy(P)
        oonce = copy.deepcopy(O)
        sonuc = fn(P, O)
        if sonuc != BEKLENEN or P != ponce or O != oonce or fn(P, []) != []:
            return False
        if any(sonuc[i] is O[i] for i in range(len(O))):
            return False
        sinir = [{"olcut": "f1", "tekrar": 1, "deger": 0}, {"olcut": "f1", "tekrar": 2, "deger": 1}]
        if fn(dict(P, id="a" * 64), sinir)[1]["deger"] != 1:
            return False
        for plan, olcumler in [
            (None, O), (P, None), (P, {}), (P, [None]), (dict(P, olcutler=[]), O), (dict(P, olcutler=[]), []),
            (dict(P, id="a" * 65), O), (dict(P, veri=""), O), (dict(P, veri=" x"), O), (dict(P, olcutler=None), O),
            (dict(P, tohum=True), O), (dict(P, tohum="0"), O), (dict(P, tohum=-1), O),
            (P, [dict(O[0], ek=1)]), (P, [dict(O[0], olcut="asr")]), (P, [dict(O[0], olcut=None)]),
            (P, [dict(O[0], tekrar=0)]), (P, [dict(O[0], tekrar=-1)]), (P, [dict(O[0], tekrar=True)]), (P, [dict(O[0], tekrar=1.0)]),
            (P, [dict(O[0], deger=True)]), (P, [dict(O[0], deger="0.5")]), (P, [dict(O[0], deger=float("nan"))]),
            (P, [dict(O[0], deger=float("inf"))]), (P, [dict(O[0], deger=-0.1)]), (P, [dict(O[0], deger=1.1)]),
            (P, [O[0], O[0]]),
        ]:
            try:
                fn(plan, olcumler)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(olcumleri_dogrula), "ölçüt, tekrar, değer ve sıralama korunmalı")
def m_deger(plan, olcumler):
    return olcumleri_dogrula(plan, [dict(x, deger=0) for x in olcumler])
def m_tekrar(plan, olcumler):
    return olcumleri_dogrula(plan, [dict(x, tekrar=1) for x in olcumler])
def m_olcut(plan, olcumler):
    return olcumleri_dogrula(plan, [dict(x, olcut="f1") for x in olcumler])
for ad, mutant in [("değerleri silen", m_deger), ("tekrarları eşitleyen", m_tekrar), ("ölçütleri değiştiren", m_olcut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def olcumleri_dogrula(plan, olcumler):
    import math
    import re
    if not isinstance(plan, dict):
        raise ValueError("plan sözlük olmalı")
    if set(plan) != {"id", "veri", "model", "tehdit", "olcutler", "tohum"}:
        raise ValueError("plan şeması geçersiz")
    if not isinstance(plan["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", plan["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("veri", "model", "tehdit"):
        deger = plan[alan]
        if not isinstance(deger, str):
            raise ValueError("metin alanı string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("metin boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("metin kontrol karakteri içeremez")
    if not isinstance(plan["olcutler"], list) or not plan["olcutler"]:
        raise ValueError("ölçüt listesi geçersiz")
    for olcut in plan["olcutler"]:
        if olcut not in ("dogruluk", "f1", "asr", "fpr"):
            raise ValueError("plan ölçütü geçersiz")
    if len(set(plan["olcutler"])) != len(plan["olcutler"]):
        raise ValueError("plan ölçütleri yinelenemez")
    if isinstance(plan["tohum"], bool) or not isinstance(plan["tohum"], int) or plan["tohum"] < 0:
        raise ValueError("tohum geçersiz")
    if not isinstance(olcumler, list):
        raise ValueError("ölçümler liste olmalı")
    gorulen = set()
    for olcum in olcumler:
        if not isinstance(olcum, dict):
            raise ValueError("ölçüm sözlük olmalı")
        if set(olcum) != {"olcut", "tekrar", "deger"}:
            raise ValueError("ölçüm şeması geçersiz")
        if olcum["olcut"] not in plan["olcutler"]:
            raise ValueError("ölçüm planda yok")
        tekrar = olcum["tekrar"]
        if isinstance(tekrar, bool) or not isinstance(tekrar, int):
            raise ValueError("tekrar tamsayı olmalı")
        if tekrar <= 0:
            raise ValueError("tekrar pozitif olmalı")
        deger = olcum["deger"]
        if isinstance(deger, bool) or not isinstance(deger, (int, float)):
            raise ValueError("değer sayı olmalı")
        if not math.isfinite(deger):
            raise ValueError("değer sonlu olmalı")
        if deger < 0 or deger > 1:
            raise ValueError("değer aralık dışında")
        anahtar = (olcum["olcut"], tekrar)
        if anahtar in gorulen:
            raise ValueError("ölçüt ve tekrar yinelenemez")
        gorulen.add(anahtar)
    return sorted(({"olcut": x["olcut"], "tekrar": x["tekrar"], "deger": x["deger"]} for x in olcumler), key=lambda x: (x["olcut"], x["tekrar"]))
```

```hint
Ölçümün ölçütünü plan listesiyle sınırla. Çift anahtarını kayıt kümesine eklemeden önce bütün alanları doğrula.
```
:::

::: gorev 3 · Deney kapsamındaki eksikleri raporla
`deney_kapsam_raporu(plan, olcumler, beklenen_tekrar)` işlevini yaz. Plan ve ölçümler ikinci görevdeki kuralları sağlasın. Beklenen tekrar bool olmayan pozitif tamsayıdır; ayrıca her ölçümün tekrar numarası bu üst sınırı aşmamalıdır. Geçersiz veride `ValueError` yükselt.

Plandaki her ölçüt için `1..beklenen_tekrar` çiftlerini denetle. `{"plan_id":ID,"karar":KARAR,"beklenen":N,"kayitli":N,"eksikler":[{"olcut":OLCUT,"tekrar":N},...]}` döndür. Eksik yoksa karar `tamam`, varsa `eksik` olur. Eksikleri ölçütlerin plan sırası ve tekrar numarasıyla listele. Girdileri değiştirme.

```starter
from ai_guvence_veri import json_yukle

def deney_kapsam_raporu(plan, olcumler, beklenen_tekrar):
    # KUSURLU BAŞLANGIÇ KODU: eksik ölçüt-tekrar çiftlerini aramadan her zaman 'tamam' döndürüyor!
    return {
        "plan_id": plan.get("id", "") if isinstance(plan, dict) else "",
        "karar": "tamam",
        "beklenen": 0,
        "kayitli": len(olcumler) if isinstance(olcumler, list) else 0,
        "eksikler": [],
    }

print("Örnek kapsam:", deney_kapsam_raporu(json_yukle("veri/plan.json"), json_yukle("veri/olcumler.json"), 2))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-01")
```

```test
import copy
P = {"id": "d-1", "veri": "yelkovan.csv", "model": "logistic regression", "tehdit": "veri zehirleme", "olcutler": ["f1", "dogruluk"], "tohum": 0}
O = [
    {"olcut": "f1", "tekrar": 1, "deger": 0.25},
    {"olcut": "dogruluk", "tekrar": 1, "deger": 0.5},
    {"olcut": "dogruluk", "tekrar": 2, "deger": 0.75},
]
BEKLENEN = {"plan_id": "d-1", "karar": "eksik", "beklenen": 4, "kayitli": 3, "eksikler": [{"olcut": "f1", "tekrar": 2}]}
def sozlesme(fn):
    try:
        ponce = copy.deepcopy(P)
        oonce = copy.deepcopy(O)
        if fn(P, O, 2) != BEKLENEN or P != ponce or O != oonce:
            return False
        tam = [*O, {"olcut": "f1", "tekrar": 2, "deger": 1}]
        if fn(dict(P, id="a" * 64), tam, 2)["karar"] != "tamam":
            return False
        bos = fn(P, [], 2)
        if bos["karar"] != "eksik" or bos["beklenen"] != 4 or bos["kayitli"] != 0 or len(bos["eksikler"]) != 4:
            return False
        if bos["eksikler"][0] != {"olcut": "f1", "tekrar": 1} or bos["eksikler"][-1] != {"olcut": "dogruluk", "tekrar": 2}:
            return False
        if fn(P, O[:1], 1)["karar"] != "eksik":
            return False
        if fn(P, [dict(O[0], deger=0)], 1)["kayitli"] != 1:
            return False
        for tekrar in [0, -1, True, 1.0, None]:
            try:
                fn(P, [], tekrar)
                return False
            except ValueError:
                pass
        for plan, olcumler in [
            (None, O), (P, None), (P, [None]), (dict(P, olcutler=[]), O), (dict(P, olcutler=[]), []),
            (dict(P, id="a" * 65), O), (dict(P, veri=""), O), (dict(P, veri=" x"), O), (dict(P, olcutler=None), O),
            (dict(P, tohum=True), O), (dict(P, tohum="0"), O), (dict(P, tohum=-1), O),
            (P, [dict(O[0], olcut="asr")]), (P, [dict(O[0], tekrar=0)]), (P, [dict(O[0], tekrar=3)]),
            (P, [dict(O[0], tekrar=True)]), (P, [dict(O[0], tekrar="1")]),
            (P, [dict(O[0], deger=True)]), (P, [dict(O[0], deger="0.5")]),
            (P, [dict(O[0], deger=float("nan"))]), (P, [dict(O[0], deger=-0.1)]), (P, [dict(O[0], deger=1.1)]), (P, [O[0], O[0]]),
        ]:
            try:
                fn(plan, olcumler, 2)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(deney_kapsam_raporu), "beklenen çiftler, eksik sırası ve karar korunmalı")
def m_olcum(plan, olcumler, beklenen_tekrar):
    return deney_kapsam_raporu(plan, olcumler[:1], beklenen_tekrar)
def m_olcut(plan, olcumler, beklenen_tekrar):
    return deney_kapsam_raporu(dict(plan, olcutler=["f1"]), olcumler, beklenen_tekrar)
def m_tekrar(plan, olcumler, beklenen_tekrar):
    return deney_kapsam_raporu(plan, olcumler, 1)
for ad, mutant in [("ölçümleri silen", m_olcum), ("planı değiştiren", m_olcut), ("tekrarı azaltan", m_tekrar)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def deney_kapsam_raporu(plan, olcumler, beklenen_tekrar):
    import math
    import re
    if isinstance(beklenen_tekrar, bool) or not isinstance(beklenen_tekrar, int):
        raise ValueError("beklenen tekrar tamsayı olmalı")
    if beklenen_tekrar <= 0:
        raise ValueError("beklenen tekrar pozitif olmalı")
    if not isinstance(plan, dict):
        raise ValueError("plan sözlük olmalı")
    if set(plan) != {"id", "veri", "model", "tehdit", "olcutler", "tohum"}:
        raise ValueError("plan şeması geçersiz")
    if not isinstance(plan["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", plan["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("veri", "model", "tehdit"):
        deger = plan[alan]
        if not isinstance(deger, str):
            raise ValueError("metin alanı string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("metin boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("metin kontrol karakteri içeremez")
    if not isinstance(plan["olcutler"], list) or not plan["olcutler"]:
        raise ValueError("ölçüt listesi geçersiz")
    for olcut in plan["olcutler"]:
        if olcut not in ("dogruluk", "f1", "asr", "fpr"):
            raise ValueError("plan ölçütü geçersiz")
    if len(set(plan["olcutler"])) != len(plan["olcutler"]):
        raise ValueError("plan ölçütleri yinelenemez")
    if isinstance(plan["tohum"], bool) or not isinstance(plan["tohum"], int) or plan["tohum"] < 0:
        raise ValueError("tohum geçersiz")
    if not isinstance(olcumler, list):
        raise ValueError("ölçümler liste olmalı")
    gorulen = set()
    for olcum in olcumler:
        if not isinstance(olcum, dict):
            raise ValueError("ölçüm sözlük olmalı")
        if set(olcum) != {"olcut", "tekrar", "deger"}:
            raise ValueError("ölçüm şeması geçersiz")
        if olcum["olcut"] not in plan["olcutler"]:
            raise ValueError("ölçüm planda yok")
        tekrar = olcum["tekrar"]
        if isinstance(tekrar, bool) or not isinstance(tekrar, int):
            raise ValueError("tekrar tamsayı olmalı")
        if tekrar <= 0 or tekrar > beklenen_tekrar:
            raise ValueError("tekrar aralık dışında")
        deger = olcum["deger"]
        if isinstance(deger, bool) or not isinstance(deger, (int, float)):
            raise ValueError("değer sayı olmalı")
        if not math.isfinite(deger):
            raise ValueError("değer sonlu olmalı")
        if deger < 0 or deger > 1:
            raise ValueError("değer aralık dışında")
        anahtar = (olcum["olcut"], tekrar)
        if anahtar in gorulen:
            raise ValueError("ölçüt ve tekrar yinelenemez")
        gorulen.add(anahtar)
    eksikler = []
    for olcut in plan["olcutler"]:
        for tekrar in range(1, beklenen_tekrar + 1):
            if (olcut, tekrar) not in gorulen:
                eksikler.append({"olcut": olcut, "tekrar": tekrar})
    return {"plan_id": plan["id"], "karar": "tamam" if not eksikler else "eksik", "beklenen": len(plan["olcutler"]) * beklenen_tekrar, "kayitli": len(olcumler), "eksikler": eksikler}
```

```hint
Ölçüm çiftlerini kümeye al. Eksik listesini plan sırasını değiştirmeden iki döngüyle üret; beklenen sayıyı ölçüt sayısıyla tekrar sayısının çarpımı olarak hesapla.
```
:::

::: anlat Canlı sınıflandırıcı eğitiminde tekrarlı deney defteri ve kapsam kanıtı
İlk üç görevde deney planını, ölçüm sıralamasını ve kapsam kontrolünü sentetik dosyalar üzerinde kurdun. Şimdi aynı üç işlevi **gerçek `scikit-learn` (`LogisticRegression`) eğitim döngüsüne** bağlıyoruz:

1. Üç farklı rastgelelik tohumu (`tohum + tekrar`) ile ikili sınıflandırma verisi üretilir, eğitim kümesinin bir alt kümesine tetikleyici etiket kaydırma uygulanır ve `LogisticRegression` modeli gerçekten eğitilir.
2. Her tekrar sonunda gerçek `dogruluk`, `f1`, `asr` ve `fpr` değerleri ölçülüp `olcumleri_dogrula` ve `deney_kapsam_raporu` işlevlerinden geçirilir.
3. Önce bir ölçüt kaydı eksik bırakılarak `eksik` kararı, ardından tüm `4 × 3 = 12` ölçüm tamamlanarak `tamam` kararı doğrulanır ve kanıt dosyasına yazılır.
:::

::: gorev Gerçek deney · Canlı sınıflandırıcı eğitiminde deney defteri ve kapsam doğrulaması
Önceki üç görevde yazdığın `deney_plani_dogrula(plan)`, `olcumleri_dogrula(plan, olcumler)` ve `deney_kapsam_raporu(plan, olcumler, beklenen_tekrar)` işlevlerini burada birleştir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 180
```

```starter
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_01 as L

def deney_plani_dogrula(plan):
    # KUSURLU BAŞLANGIÇ KODU: şema ve alan doğrulaması yapmadan doğrudan girdi sözlüğünü döndürüyor!
    return plan

def olcumleri_dogrula(plan, olcumler):
    return list(olcumler) if isinstance(olcumler, list) else []

def deney_kapsam_raporu(plan, olcumler, beklenen_tekrar):
    return {"plan_id": "", "karar": "tamam", "beklenen": 0, "kayitli": 0, "eksikler": []}

if ai_lab.CALISTIR:
    L.goster(deney_plani_dogrula, olcumleri_dogrula, deney_kapsam_raporu)
```

```test
import copy
import ai_lab
from sandbox import ai_gercek_ai_guvence_01 as L

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for s in ai_lab.kod_denetimi(src, yasak=("deney_plani_dogrula_referans", "olcumleri_dogrula_referans", "deney_kapsam_raporu_referans", "kanit_yaz")):
    ok(False, f"Güvenlik/kopya denetimi: {s}")
if not all(checks):
    stop()

def _sozlesme_kontrol():
    try:
        P = {"id": "d-1", "veri": "yelkovan.csv", "model": "logistic regression", "tehdit": "veri zehirleme", "olcutler": ["f1", "dogruluk"], "tohum": 0}
        once = copy.deepcopy(P)
        sp = deney_plani_dogrula(P)
        if sp != P or P != once or sp is P or sp["olcutler"] is P["olcutler"]:
            return False
        for bp in [None, dict(P, ek=1), dict(P, id="a b"), dict(P, veri=" x"), dict(P, olcutler=["f1", "f1"]), dict(P, tohum=True), dict(P, tohum=-1)]:
            try:
                deney_plani_dogrula(bp)
                return False
            except ValueError:
                pass

        O = [
            {"olcut": "f1", "tekrar": 1, "deger": 0.25},
            {"olcut": "dogruluk", "tekrar": 1, "deger": 0.5},
            {"olcut": "dogruluk", "tekrar": 2, "deger": 0.75},
        ]
        so = olcumleri_dogrula(P, O)
        if so != [O[1], O[2], O[0]] or any(so[i] is O[i] for i in range(len(O))):
            return False
        for bo in [None, [dict(O[0], olcut="asr")], [dict(O[0], tekrar=0)], [dict(O[0], deger=1.2)], [O[0], O[0]]]:
            try:
                olcumleri_dogrula(P, bo)
                return False
            except ValueError:
                pass

        sr = deney_kapsam_raporu(P, O, 2)
        if sr != {"plan_id": "d-1", "karar": "eksik", "beklenen": 4, "kayitli": 3, "eksikler": [{"olcut": "f1", "tekrar": 2}]}:
            return False
        tam = [*O, {"olcut": "f1", "tekrar": 2, "deger": 1.0}]
        if deney_kapsam_raporu(P, tam, 2)["karar"] != "tamam":
            return False
        for bt in [0, -1, True]:
            try:
                deney_kapsam_raporu(P, O, bt)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_sozlesme_kontrol(), "deney_plani_dogrula, olcumleri_dogrula ve deney_kapsam_raporu sözleşme kontrollerini geçmeli")
if not all(checks):
    stop()

try:
    rapor = L.deney(deney_plani_dogrula, olcumleri_dogrula, deney_kapsam_raporu)
except ai_lab.GercekLabYok as e:
    ok(False, str(e))
    stop()
except Exception as e:
    ok(False, f"GERÇEK DENEY DEFTERİ DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

k = rapor["kontroller"]
ok(k["plan_dogrulama_uyumu"], f"deney_plani_dogrula canlı planda referansla uyuşmalı: {rapor['plan']}")
ok(k["olcum_siralama_uyumu"], f"olcumleri_dogrula 12 canlı ölçümde referansla uyuşmalı: {rapor['olcumler'][:4]}")
ok(k["eksik_kapsam_uyumu"], f"deney_kapsam_raporu eksik canlı koşuda 'eksik' döndürmeli: {rapor['eksik_rapor']}")
ok(k["tam_kapsam_uyumu"], f"deney_kapsam_raporu tam canlı koşuda 'tamam' döndürmeli: {rapor['tam_rapor']}")

kabul = all(checks)
kanit_yolu = ai_lab.kanit_yaz("guvence-01-deney-defteri", dict(rapor, kaynak="gercek", kabul=kabul))
o = rapor["ozet"]
print(f"GERÇEK DENEY DEFTERİ: sklearn={o['sklearn_surum']} kayitli={o['kayitli']}/{o['beklenen_kayit']} karar={o['tam_senaryo_karar']} kanıt={kanit_yolu}")
```

```solution
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_01 as L

def deney_plani_dogrula(plan):
    if not isinstance(plan, dict) or set(plan) != {"id", "veri", "model", "tehdit", "olcutler", "tohum"}:
        raise ValueError("plan şeması geçersiz")
    if not isinstance(plan["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", plan["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("veri", "model", "tehdit"):
        deger = plan[alan]
        if not isinstance(deger, str) or not deger or deger != deger.strip() or any(ord(k) < 32 for k in deger):
            raise ValueError("metin alanı geçersiz")
    olcutler = plan["olcutler"]
    if not isinstance(olcutler, list) or not olcutler or len(set(olcutler)) != len(olcutler):
        raise ValueError("ölçütler geçersiz")
    if any(o not in ("dogruluk", "f1", "asr", "fpr") for o in olcutler):
        raise ValueError("ölçüt geçersiz")
    if isinstance(plan["tohum"], bool) or not isinstance(plan["tohum"], int) or plan["tohum"] < 0:
        raise ValueError("tohum geçersiz")
    return {"id": plan["id"], "veri": plan["veri"], "model": plan["model"], "tehdit": plan["tehdit"], "olcutler": list(olcutler), "tohum": plan["tohum"]}

def olcumleri_dogrula(plan, olcumler):
    p = deney_plani_dogrula(plan)
    if not isinstance(olcumler, list):
        raise ValueError("ölçümler liste olmalı")
    gorulen = set()
    for olcum in olcumler:
        if not isinstance(olcum, dict) or set(olcum) != {"olcut", "tekrar", "deger"}:
            raise ValueError("ölçüm şeması geçersiz")
        if olcum["olcut"] not in p["olcutler"]:
            raise ValueError("ölçüm planda yok")
        tekrar = olcum["tekrar"]
        if isinstance(tekrar, bool) or not isinstance(tekrar, int) or tekrar <= 0:
            raise ValueError("tekrar geçersiz")
        deger = olcum["deger"]
        if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger) or deger < 0 or deger > 1:
            raise ValueError("değer geçersiz")
        anahtar = (olcum["olcut"], tekrar)
        if anahtar in gorulen:
            raise ValueError("yinelenen ölçüm")
        gorulen.add(anahtar)
    return sorted(({"olcut": x["olcut"], "tekrar": x["tekrar"], "deger": x["deger"]} for x in olcumler), key=lambda x: (x["olcut"], x["tekrar"]))

def deney_kapsam_raporu(plan, olcumler, beklenen_tekrar):
    if isinstance(beklenen_tekrar, bool) or not isinstance(beklenen_tekrar, int) or beklenen_tekrar <= 0:
        raise ValueError("beklenen tekrar geçersiz")
    p = deney_plani_dogrula(plan)
    dogrulanmis = olcumleri_dogrula(p, olcumler)
    if any(x["tekrar"] > beklenen_tekrar for x in dogrulanmis):
        raise ValueError("tekrar aralık dışında")
    gorulen = {(x["olcut"], x["tekrar"]) for x in dogrulanmis}
    eksikler = [{"olcut": o, "tekrar": t} for o in p["olcutler"] for t in range(1, beklenen_tekrar + 1) if (o, t) not in gorulen]
    return {"plan_id": p["id"], "karar": "tamam" if not eksikler else "eksik", "beklenen": len(p["olcutler"]) * beklenen_tekrar, "kayitli": len(dogrulanmis), "eksikler": eksikler}

if ai_lab.CALISTIR:
    L.goster(deney_plani_dogrula, olcumleri_dogrula, deney_kapsam_raporu)
```

```hint
Önceki üç görevde yazdığın `deney_plani_dogrula`, `olcumleri_dogrula` ve `deney_kapsam_raporu` işlevlerini eksiksiz taşı; canlı deneyde 3 tohum × 4 ölçüt (`LogisticRegression`) üzerinde sınanır.
```
:::
