---
id: ai-ile-guvenlik-16
title: "Güvenlik Ajanlarında Hassasiyet, Duyarlılık ve Maliyet Dengesi"
summary: Farklı istem ve model ayarlarında güvenlik ajanının precision, recall, F1, gecikme (ms) ve token maliyetini birlikte ölç; bütçe kısıtları altında Pareto optimal yapılandırmayı seç.
timeout: 300
---

::: anlat Gerçek biçimi bil, sentetik temsili ayırt et
Üretim ortamındaki bir SOC veya zafiyet triyajı ajanını değerlendirirken yalnız doğruluk (`F1`) puanına bakmak yanıltıcıdır: çok uzun düşünce zinciri kullanan bir yapılandırma saldırıların tamamını yakalayabilir (`recall = 1.0`), ancak olay başına `950` token ve `2400 ms` gecikme tüketerek gerçek zamanlı kuyruğu tıkayabilir (`ai-guvence-04` ve `ai-savunma-31` derslerindeki bütçe ve değerlendirme ilkelerini hatırla).

| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Çoklu istem/model değerlendirme koşularını (`promptfoo` / yerel değerlendirici), token sayaçlarını ve gecikme (`ms`) dağılımlarını | İlk üç görevde `ajan_kosu_sonuclari.json` içindeki **sentetik** koşu ölçümlerini; son görevde canlı `ai_lab.SohbetOturumu` ile Pareto seçim deneyini | Yalnızca ortalama gecikme (`ortalama_ms`) ölçümünün, yoğun trafik anındaki kuyruk şişmesini (`p99 tail latency`) tek başına temsil edebileceğini söyleyemez |

> [!GÜVENLİK]
> **Kapsam ve dürüstlük sınırı:** İlk üç görevdeki `ajan_kosu_sonuclari.json` dosyası **sentetik** eğitim verisidir; yalnız güvenlik ajanı kalite ve maliyet mühendisliği öğretilir ve dosyalar her çalıştırmada (`setup`) yeniden yüklenir.
:::

::: anlat Doğruluk ve maliyet dengesinde Pareto seçimi üç adımda yapılır
Güvenlik ajanı yapılandırmaları üç aşamada elenir ve sıralanır:

1. **Kalite ve Maliyet Metrikleri (`ajan_metrik_hesapla`):** Her koşu için `precision = round(tp / (tp + fp), 4)`, `recall = round(tp / (tp + fn), 4)` ve `f1 = round((2 * tp) / (2 * tp + fp + fn), 4)` hesaplanır.
2. **Pareto Baskınlık Kontrolü (`pareto_baskin_mi`):** `A` yapılandırması `B` yapılandırmasından en az onun kadar yüksek `f1` değerine (`f1_A >= f1_B`), en az onun kadar düşük token (`token_A <= token_B`) ve gecikme (`ms_A <= ms_B`) maliyetine sahipse **ve** bu üç ölçütün en az birinde kesin olarak daha iyiyse `A`, `B`'ye **Pareto baskındır** (`True`).
3. **Kısıt Kapısı ve Optimal Seçim (`optimal_ajan_sec`):** Önce `recall < asgari_recall` olanlar `"dusuk_recall"`, `ortalama_token > azami_token` veya `ortalama_ms > azami_ms` olanlar `"butce_asimi"` nedeniyle elenir. Kalanlar arasında başka bir uygun aday tarafından Pareto baskınlığına uğrayanlar `"pareto_baskin"` olarak ayrılır ve Pareto cephesindeki en yüksek `f1` (eşitlikte en düşük `ortalama_token`) değerine sahip ayar seçilir.
:::

::: anlat Bulguyu sınırlı ve doğrulanabilir yaz: aynı F1 puanında daha hantal olan elenir
İki ajan yapılandırması aynı `F1 = 0.9` başarısını gösteriyorsa, olay başına `410` token ve `820 ms` harcayan ayar, `540` token ve `1100 ms` harcayan ayara Pareto baskındır. Mühendislik kararı öznel tercihle değil, kısıt kapısı ve Pareto cephesiyle verilir.
:::

::: tahmin İki ajan ayarı arasında Pareto baskınlığını tahmin et
Aşağıdaki Python kodunun çıktısını tahmin et:

```python
a = {"f1": 0.9, "token": 410, "ms": 820}
b = {"f1": 0.9, "token": 540, "ms": 1100}
en_az_esit = a["f1"] >= b["f1"] and a["token"] <= b["token"] and a["ms"] <= b["ms"]
kesin_iyi = a["f1"] > b["f1"] or a["token"] < b["token"] or a["ms"] < b["ms"]
print(en_az_esit and kesin_iyi)
```

???

```cikti
True
```

`a` ayarı `b` ile aynı `f1` değerine sahipken hem daha az token hem de daha düşük gecikme kullandığı için `b` üzerinde Pareto baskındır (`True`).
:::

::: gorev 1 · Güvenlik ajanı koşusundan precision, recall ve F1 metriklerini hesapla
`ajan_metrik_hesapla(kosu)` işlevini yaz.

Kurallar:
- `kosu`: tam olarak `{"ayar_id", "tp", "fp", "tn", "fn", "ortalama_token", "ortalama_ms"}` anahtarlarına sahip `dict`; `ayar_id` boş olmayan `str`, sayısal alanlar negatif olmayan `int` (`bool` hariç) olmalıdır.
- `tp + fp > 0`, `tp + fn > 0`, `ortalama_token > 0` ve `ortalama_ms > 0` olmalıdır; aksi halde `ValueError` yükselt.
- Oranları 4 ondalığa yuvarlayarak hesapla:
  - `precision = round(tp / (tp + fp), 4)`
  - `recall = round(tp / (tp + fn), 4)`
  - `f1 = round((2 * tp) / (2 * tp + fp + fn), 4)`
- `{"ayar_id": ..., "precision": ..., "recall": ..., "f1": ..., "ortalama_token": ..., "ortalama_ms": ...}` sözlüğünü döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

kosular = json_yukle("ajan_kosu_sonuclari.json")["kosular"]

def ajan_metrik_hesapla(kosu):
    # HATA: Precision, recall ve F1 oranlarını hesaplamıyor.
    return {
        "ayar_id": kosu.get("ayar_id", ""),
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "ortalama_token": kosu.get("ortalama_token", 0),
        "ortalama_ms": kosu.get("ortalama_ms", 0),
    }

for k in kosular:
    print(ajan_metrik_hesapla(k))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-16")
```

```test
need("ajan_metrik_hesapla")

def sozlesme(fn):
    try:
        r1 = fn({
            "ayar_id": "a1",
            "tp": 9,
            "fp": 1,
            "tn": 9,
            "fn": 1,
            "ortalama_token": 410,
            "ortalama_ms": 820,
        })
        if r1 != {
            "ayar_id": "a1",
            "precision": 0.9,
            "recall": 0.9,
            "f1": 0.9,
            "ortalama_token": 410,
            "ortalama_ms": 820,
        }:
            return False

        r2 = fn({
            "ayar_id": "a2",
            "tp": 2,
            "fp": 1,
            "tn": 5,
            "fn": 1,
            "ortalama_token": 300,
            "ortalama_ms": 500,
        })
        if r2 != {
            "ayar_id": "a2",
            "precision": 0.6667,
            "recall": 0.6667,
            "f1": 0.6667,
            "ortalama_token": 300,
            "ortalama_ms": 500,
        }:
            return False

        for h in [
            None,
            {},
            {"ayar_id": "", "tp": 1, "fp": 1, "tn": 1, "fn": 1, "ortalama_token": 10, "ortalama_ms": 10},
            {"ayar_id": "a", "tp": 0, "fp": 0, "tn": 5, "fn": 2, "ortalama_token": 10, "ortalama_ms": 10},
            {"ayar_id": "a", "tp": 0, "fp": 2, "tn": 5, "fn": 0, "ortalama_token": 10, "ortalama_ms": 10},
            {"ayar_id": "a", "tp": 1, "fp": 1, "tn": 1, "fn": 1, "ortalama_token": 0, "ortalama_ms": 10},
            {"ayar_id": "a", "tp": True, "fp": 1, "tn": 1, "fn": 1, "ortalama_token": 10, "ortalama_ms": 10},
        ]:
            try:
                fn(h)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(ajan_metrik_hesapla), "ajan_metrik_hesapla: precision, recall ve F1 hesaplaması doğru")
ok(not sozlesme(lambda k: {"ayar_id": k["ayar_id"], "precision": 0.9, "recall": 0.9, "f1": 0.9, "ortalama_token": 410, "ortalama_ms": 820}), "mutasyon: sabit metrik döndüren işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_16 import _kosu_kontrol

def ajan_metrik_hesapla(kosu):
    _kosu_kontrol(kosu)
    tp = kosu["tp"]
    fp = kosu["fp"]
    fn = kosu["fn"]

    Payda_p = tp + fp
    Payda_r = tp + fn
    iki_tp = tp + tp

    return {
        "ayar_id": kosu["ayar_id"],
        "precision": round(tp / Payda_p, 4),
        "recall": round(tp / Payda_r, 4),
        "f1": round(iki_tp / (iki_tp + fp + fn), 4),
        "ortalama_token": kosu["ortalama_token"],
        "ortalama_ms": kosu["ortalama_ms"],
    }
```

```hint
`_kosu_kontrol(kosu)` doğrulamasından sonra `precision`, `recall` ve `f1` oranlarını `round(..., 4)` ile hesapla.
```
:::

::: gorev 2 · İki yapılandırma arasında Pareto baskınlığını kontrol et
`pareto_baskin_mi(aday_a, aday_b)` işlevini yaz.

Kurallar:
- `aday_a` ve `aday_b`: 1. görevin çıktısı olan metrik sözlüğü şemasına (`{"ayar_id", "precision", "recall", "f1", "ortalama_token", "ortalama_ms"}`) sahip olmalıdır; aksi halde `ValueError` yükselt.
- `aday_a` şu iki koşulu birlikte sağlıyorsa `True`, aksi halde `False` döndür:
  1. Tüm hedeflerde en az `aday_b` kadar iyi olma: `f1_a >= f1_b`, `token_a <= token_b` ve `ms_a <= ms_b`.
  2. En az bir hedefte kesin daha iyi olma: `f1_a > f1_b` veya `token_a < token_b` veya `ms_a < ms_b`.

```starter
def pareto_baskin_mi(aday_a, aday_b):
    # HATA: Token ve gecikme maliyetlerini karşılaştırmadan yalnız F1'e bakıyor.
    return False

print(pareto_baskin_mi(
    {"ayar_id": "a", "precision": 0.9, "recall": 0.9, "f1": 0.9, "ortalama_token": 400, "ortalama_ms": 800},
    {"ayar_id": "b", "precision": 0.9, "recall": 0.9, "f1": 0.9, "ortalama_token": 500, "ortalama_ms": 900},
))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-16")
```

```test
need("pareto_baskin_mi")

BAZ = {"ayar_id": "a", "precision": 0.9, "recall": 0.9, "f1": 0.9, "ortalama_token": 410, "ortalama_ms": 820}
HANTAL_TOKEN = {"ayar_id": "b", "precision": 0.9, "recall": 0.9, "f1": 0.9, "ortalama_token": 540, "ortalama_ms": 820}
HANTAL_MS = {"ayar_id": "c", "precision": 0.9, "recall": 0.9, "f1": 0.9, "ortalama_token": 410, "ortalama_ms": 1100}
DUSUK_F1 = {"ayar_id": "d", "precision": 0.8, "recall": 0.8, "f1": 0.8, "ortalama_token": 410, "ortalama_ms": 820}
TAKASLI = {"ayar_id": "e", "precision": 0.95, "recall": 0.95, "f1": 0.95, "ortalama_token": 600, "ortalama_ms": 820}

def sozlesme(fn):
    try:
        if fn(BAZ, HANTAL_TOKEN) is not True:
            return False
        if fn(BAZ, HANTAL_MS) is not True:
            return False
        if fn(BAZ, DUSUK_F1) is not True:
            return False
        if fn(BAZ, BAZ) is not False:
            return False
        if fn(HANTAL_TOKEN, BAZ) is not False:
            return False
        if fn(BAZ, TAKASLI) is not False or fn(TAKASLI, BAZ) is not False:
            return False

        for a_in, b_in in [
            (None, BAZ),
            (BAZ, {}),
            (dict(BAZ, f1=1.5), BAZ),
            (dict(BAZ, ortalama_token=0), BAZ),
        ]:
            try:
                fn(a_in, b_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(pareto_baskin_mi), "pareto_baskin_mi: F1, token ve gecikme eksenlerinde Pareto baskınlığını doğru saptamalı")
ok(not sozlesme(lambda a, b: True), "mutasyon: her çifti baskın sayan işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_16 import _metrik_sozlugu_kontrol

def pareto_baskin_mi(aday_a, aday_b):
    _metrik_sozlugu_kontrol(aday_a)
    _metrik_sozlugu_kontrol(aday_b)

    farklar = (
        aday_a["f1"] - aday_b["f1"],
        aday_b["ortalama_token"] - aday_a["ortalama_token"],
        aday_b["ortalama_ms"] - aday_a["ortalama_ms"],
    )
    return all(d >= 0 for d in farklar) and any(d > 0 for d in farklar)
```

```hint
İyileşme farklarını `(a["f1"] - b["f1"], b["ortalama_token"] - a["ortalama_token"], b["ortalama_ms"] - a["ortalama_ms"])` olarak kur; tümünün `>= 0` ve en az birinin `> 0` olup olmadığını kontrol et.
```
:::

::: gorev 3 · Kısıt kapısı ve Pareto cephesiyle optimal güvenlik ajanını seç
`optimal_ajan_sec(kosular, kisitlar)` işlevini yaz.

Kurallar:
- `kosular`: boş olmayan `list`; her öğesi 1. görevdeki şemaya uymalı ve `ayar_id` değerleri benzersiz olmalıdır.
- `kisitlar`: tam olarak `{"asgari_recall", "azami_token", "azami_ms"}` anahtarlarına sahip `dict` olmalıdır (aksi halde `ValueError` yükselt).
- Her koşuyu önce `ajan_metrik_hesapla` ile değerlendir ve kısıt kapısından geçir:
  - `recall < kisitlar["asgari_recall"]` ise `elenen_ayarlar[ayar_id] = "dusuk_recall"` olarak ayır.
  - `ortalama_token > kisitlar["azami_token"]` veya `ortalama_ms > kisitlar["azami_ms"]` ise `elenen_ayarlar[ayar_id] = "butce_asimi"` olarak ayır.
- Kısıtları geçen adaylar arasında başka bir uygun aday tarafından Pareto baskınlığına uğrayanları `elenen_ayarlar[ayar_id] = "pareto_baskin"` olarak ayır.
- Kalan Pareto cephesi adaylarını `(-f1, ortalama_token, ayar_id)` sırasına diz; ilkini `secilen_ayar_id` olarak seç (hiç aday kalmazsa `None`).
- `{"secilen_ayar_id": ..., "pareto_adaylari": [...], "elenen_ayarlar": ...}` sözlüğünü döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

veri = json_yukle("ajan_kosu_sonuclari.json")

def optimal_ajan_sec(kosular, kisitlar):
    # HATA: Kısıtları ve Pareto baskınlığını kontrol etmeden ilk ayarı seçiyor.
    return {
        "secilen_ayar_id": kosular[0]["ayar_id"],
        "pareto_adaylari": [],
        "elenen_ayarlar": {},
    }

print(optimal_ajan_sec(veri["kosular"], veri["kisitlar"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-16")
```

```test
need("optimal_ajan_sec")
from ai_ile_guvenlik_veri import json_yukle

VERI = json_yukle("ajan_kosu_sonuclari.json")
KOSULAR = VERI["kosular"]
KISITLAR = VERI["kisitlar"]

def sozlesme(fn):
    try:
        r = fn(KOSULAR, KISITLAR)
        if r != {
            "secilen_ayar_id": "ayar-dengeli-v1",
            "pareto_adaylari": ["ayar-dengeli-v1"],
            "elenen_ayarlar": {
                "ayar-hizli-kaba": "dusuk_recall",
                "ayar-dengeli-hantal": "pareto_baskin",
                "ayar-asiri-dusunen": "butce_asimi",
            },
        }:
            return False

        r_bos = fn([KOSULAR[0]], KISITLAR)
        if r_bos["secilen_ayar_id"] is not None or r_bos["pareto_adaylari"] != []:
            return False

        r_sinir = fn([KOSULAR[1]], {"asgari_recall": 0.9, "azami_token": 410, "azami_ms": 820})
        if r_sinir["secilen_ayar_id"] != "ayar-dengeli-v1":
            return False

        for k_in, s_in in [
            (None, KISITLAR),
            (123, KISITLAR),
            ([], KISITLAR),
            ([KOSULAR[0], KOSULAR[0]], KISITLAR),
            (KOSULAR, None),
            (KOSULAR, {}),
        ]:
            try:
                fn(k_in, s_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(optimal_ajan_sec), "optimal_ajan_sec: düşük recall, bütçe aşımı ve Pareto baskın adayları eleyip optimal ayarı seçmeli")
ok(not sozlesme(lambda k, s: {"secilen_ayar_id": "ayar-dengeli-hantal", "pareto_adaylari": [], "elenen_ayarlar": {}}), "mutasyon: Pareto baskın adayı seçen işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_16 import (
    _kisit_kontrol,
    ajan_metrik_hesapla_referans as _metrik,
    pareto_baskin_mi_referans as _baskin_mi,
)

def optimal_ajan_sec(kosular, kisitlar):
    if not (isinstance(kosular, list) and bool(kosular)):
        raise ValueError("kosular boş olmayan liste olmalı")
    _kisit_kontrol(kisitlar)

    uygunlar = []
    elenenler = {}
    gorulen = set()

    for k in kosular:
        m = _metrik(k)
        aid = m["ayar_id"]
        if aid in gorulen:
            raise ValueError("tekrarlanan ayar_id")
        gorulen.add(aid)

        if m["recall"] < kisitlar["asgari_recall"]:
            elenenler[aid] = "dusuk_recall"
            continue
        if any([m["ortalama_token"] > kisitlar["azami_token"], m["ortalama_ms"] > kisitlar["azami_ms"]]):
            elenenler[aid] = "butce_asimi"
            continue
        uygunlar.append(m)

    pareto_kumesi = []
    for m in uygunlar:
        if any(_baskin_mi(diger, m) for diger in uygunlar if diger["ayar_id"] != m["ayar_id"]):
            elenenler[m["ayar_id"]] = "pareto_baskin"
        else:
            pareto_kumesi.append(m)

    pareto_kumesi.sort(key=lambda x: (-x["f1"], x["ortalama_token"], x["ayar_id"]))
    secilen = pareto_kumesi[0]["ayar_id"] if pareto_kumesi else None

    return {
        "secilen_ayar_id": secilen,
        "pareto_adaylari": [x["ayar_id"] for x in pareto_kumesi],
        "elenen_ayarlar": elenenler,
    }
```

```hint
Önce `recall < asgari_recall` ve bütçe aşımı kontrollerini uygula; kalanlar içinde başka bir aday tarafından Pareto baskınlığına uğrayanları `"pareto_baskin"` olarak ayır.
```
:::

::: gorev Gerçek deney · Yerel modelle güvenlik ajanında doğruluk ve maliyet dengesi deneyi
Önceki üç görevde yazdığın `ajan_metrik_hesapla`, `pareto_baskin_mi` ve `optimal_ajan_sec` işlevlerini bu adımda birleştir.

Canlı deneyde:
1. Yerel Ollama modeli (`ai_lab.SohbetOturumu`) dar token bütçesiyle (`en_fazla=40`) SOC triyaj sınıflandırması yapar.
2. Farklı istem/model koşularının sonuçları senin yazdığın `optimal_ajan_sec` değerlendiricisinden geçirilir.
3. Düşük duyarlılıklı (`ayar-hizli-kaba`), bütçe aşan (`ayar-asiri-dusunen`) ve Pareto baskınlığına uğrayan (`ayar-dengeli-hantal`) ayarların elenip `ayar-dengeli-v1` yapılandırmasının seçildiği doğrulanır.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def ajan_metrik_hesapla(kosu):
    return {}

def pareto_baskin_mi(aday_a, aday_b):
    return False

def optimal_ajan_sec(kosular, kisitlar):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_16 as deney
    deney.goster(ajan_metrik_hesapla, pareto_baskin_mi, optimal_ajan_sec)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-16")
```

```test
import ai_lab
from sandbox import ai_gercek_ai_ile_guvenlik_16 as D

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for ad in ("ajan_metrik_hesapla", "pareto_baskin_mi", "optimal_ajan_sec"):
    need(ad)

sorun = ai_lab.kod_denetimi(
    src,
    ("ajan_metrik_hesapla_referans", "pareto_baskin_mi_referans", "optimal_ajan_sec_referans"),
)
ok(not sorun, "laboratuvar yamalanmamalı, referans işlevler çağrılmamalı")

def _on_sozlesme():
    try:
        for h in (None, {}, dict(D.ORNEK_KOSULAR[0], tp=0, fp=0)):
            try:
                ajan_metrik_hesapla(h)
                return False
            except ValueError:
                pass
        for a_in, b_in in [(None, {}), ({}, None)]:
            try:
                pareto_baskin_mi(a_in, b_in)
                return False
            except ValueError:
                pass
        for k_list in (None, [], [D.ORNEK_KOSULAR[0], D.ORNEK_KOSULAR[0]]):
            try:
                optimal_ajan_sec(k_list, D.KISITLAR)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_on_sozlesme(), "sentetik ön kontrol: F1, bütçe kısıtı ve Pareto seçim kuralları tam")

if not all(checks):
    stop()

try:
    r = D.deney(ajan_metrik_hesapla, pareto_baskin_mi, optimal_ajan_sec)
except Exception as e:
    ok(False, f"GERÇEK PARETO DENGE DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

for ad, deger in r["kontroller"].items():
    ok(deger, "gerçek deney: " + ad)

ai_lab.kanit_yaz("ile-guvenlik-16-denge", {
    "kaynak": "gercek",
    "kabul": all(checks),
    "ders": "ai-ile-guvenlik-16",
    "ortam": r["ortam"],
    "ayarlar": r["ayarlar"],
    "deney": r,
    "ozet": r["ozet"],
})
o = r["ozet"]
ok(
    True,
    f"BULGU ({o['model']}): secilen={o['secilen_ayar']}, elenen={o['elenen_ayarlar']}.",
)
```

```solution
import ai_lab
from sandbox.ai_gercek_ai_ile_guvenlik_16 import _kisit_kontrol, _kosu_kontrol, _metrik_sozlugu_kontrol

def ajan_metrik_hesapla(kosu):
    _kosu_kontrol(kosu)
    tp = kosu["tp"]
    fp = kosu["fp"]
    fn = kosu["fn"]

    payda_p = tp + fp
    payda_r = tp + fn
    iki_tp = tp + tp

    return {
        "ayar_id": kosu["ayar_id"],
        "precision": round(tp / payda_p, 4),
        "recall": round(tp / payda_r, 4),
        "f1": round(iki_tp / (iki_tp + fp + fn), 4),
        "ortalama_token": kosu["ortalama_token"],
        "ortalama_ms": kosu["ortalama_ms"],
    }

def pareto_baskin_mi(aday_a, aday_b):
    _metrik_sozlugu_kontrol(aday_a)
    _metrik_sozlugu_kontrol(aday_b)

    farklar = (
        aday_a["f1"] - aday_b["f1"],
        aday_b["ortalama_token"] - aday_a["ortalama_token"],
        aday_b["ortalama_ms"] - aday_a["ortalama_ms"],
    )
    return all(d >= 0 for d in farklar) and any(d > 0 for d in farklar)

def optimal_ajan_sec(kosular, kisitlar):
    if not (isinstance(kosular, list) and bool(kosular)):
        raise ValueError("kosular boş olmayan liste olmalı")
    _kisit_kontrol(kisitlar)

    uygunlar = []
    elenenler = {}
    gorulen = set()

    for k in kosular:
        m = ajan_metrik_hesapla(k)
        aid = m["ayar_id"]
        if aid in gorulen:
            raise ValueError("tekrarlanan ayar_id")
        gorulen.add(aid)

        if m["recall"] < kisitlar["asgari_recall"]:
            elenenler[aid] = "dusuk_recall"
            continue
        if any([m["ortalama_token"] > kisitlar["azami_token"], m["ortalama_ms"] > kisitlar["azami_ms"]]):
            elenenler[aid] = "butce_asimi"
            continue
        uygunlar.append(m)

    pareto_kumesi = []
    for m in uygunlar:
        if any(pareto_baskin_mi(diger, m) for diger in uygunlar if diger["ayar_id"] != m["ayar_id"]):
            elenenler[m["ayar_id"]] = "pareto_baskin"
        else:
            pareto_kumesi.append(m)

    pareto_kumesi.sort(key=lambda x: (-x["f1"], x["ortalama_token"], x["ayar_id"]))
    secilen = pareto_kumesi[0]["ayar_id"] if pareto_kumesi else None

    return {
        "secilen_ayar_id": secilen,
        "pareto_adaylari": [x["ayar_id"] for x in pareto_kumesi],
        "elenen_ayarlar": elenenler,
    }

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_16 as deney
    deney.goster(ajan_metrik_hesapla, pareto_baskin_mi, optimal_ajan_sec)
```

```hint
Önceki üç görevdeki `ajan_metrik_hesapla`, `pareto_baskin_mi` ve `optimal_ajan_sec` işlevlerini birleştir.
```
:::
