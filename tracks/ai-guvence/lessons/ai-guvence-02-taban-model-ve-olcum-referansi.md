---
id: ai-guvence-02
title: Taban Model ve Ölçüm Referansı
summary: Eğitim-test ayrımını doğrula; sınıf performansını ve tahmin belirsizliğini ölçülebilir bir taban referansına dönüştür.
timeout: 45
---

::: anlat Gerçek taban referansını bil, sentetik temsili ayırt et
Taban modelin sonucu ancak hangi kayıtların eğitimde ve testte kullanıldığı biliniyorsa yorumlanabilir. Aynı kayıt kimliğinin iki bölümde bulunması veri sızıntısıdır; yinelenen kimlikler de bağımsız ölçümü bozar. Sınıf etiketleri ve bölüm adları kapalı bir listede tutulduğunda yanlışlıkla oluşan yeni kategoriler erken fark edilir.

| Katman | Gerçek taban model değerlendirmesi ne içerir? | Bu ders ne kullanır? | Ne söyleyemez? |
|---|---|---|---|
| Veri ayrımı | Eğitim/test indekslerinin kriptografik hash'i ve grup/zaman sızıntısı denetimi | İlk 3 görevde `veri/ayrim_kayitlari.json` sentetik kayıtları; son görevde 160 örneklik canlı `sklearn` ayrımı | Kimlik ayrımı tek başına öznitelikler arası dolaylı sızıntıyı (feature leakage) engellemez |
| Sınıf ve belirsizlik ölçümü | Karışıklık matrisi (`TP, FP, FN, TN`), duyarlılık, kesinlik ve `predict_proba` olasılık marjı | İlk 3 görevde `veri/taban_tahminleri.json` sentetik dizileri; son görevde gerçek `LogisticRegression` tahmin ve olasılıkları | `min(p, 1-p)` marjı kalibre edilmemiş modellerde gerçek olasılıksal güven aralığı değildir |

> [!NOT]
> İlk üç görevde örnek dosyalar çalışma klasörünün `veri/` altına kopyalanır: `veri/ayrim_kayitlari.json` ve `veri/taban_tahminleri.json` (tümü **sentetik**). Bu dosyaları kodundan okuyup inceleyebilirsin; ancak her çalıştırmada temiz kopya yeniden yazılır (**kalıcılık yoktur**). Kontrol adımı bu dosyalardan bağımsız gizli verilerle sınama yapar.
:::

::: anlat Tek doğruluk oranı bütün hataları anlatmaz
Dengesiz sınıflarda doğruluk tek başına yeterli değildir. Duyarlılık gerçek yelkovanların ne kadarının bulunduğunu, kesinlik ise yelkovan denen tahminlerin ne kadarının doğru olduğunu gösterir. Payda sıfırsa oran üretmek yerine `None` döndürmek, tanımsız değeri sıfır sanmaktan daha güvenlidir.

Olasılığın `0.5`'e yakınlığı basit bir belirsizlik göstergesidir: `min(p, 1-p)`. Sıfır ve bir uçları kesin, `0.5` ise en belirsiz noktadır. Bu değer kalibre edilmiş gerçek belirsizlik kanıtı değildir; yalnız fixture üzerinde karşılaştırılabilir bir taban ölçütüdür.
:::

::: tahmin Bölüm ve ölçüm sonuçlarını tahmin et
Üç çıktı satırını yaz:

```python
print(sorted(["t-2", "e-1", "t-1"]))
print(round((1 + 1) / 4, 6))
print([round(min(p, 1 - p), 2) for p in [0, 0.25, 0.5]])
```

???

```cikti
['e-1', 't-1', 't-2']
0.5
[0, 0.25, 0.5]
```

Son satırda `0.5` olasılığı en yüksek belirsizliği verir.
:::

::: gorev 1 · Eğitim-test kayıtlarını doğrula
`veri_ayrimi_dogrula(kayitlar)` işlevini yaz. Kayıtlar boş olmayan liste olsun. Her kayıt tam olarak `id`, `etiket`, `bolum` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir ve yinelenemez. Etiket `yelkovan` veya `diger`, bölüm `egitim` veya `test` olmalıdır.

Eğitim ve test bölümlerinin her biri en az bir kayıt içersin. Geçersiz veride `ValueError` yükselt. `{"egitim":[KIMLIK,...],"test":[KIMLIK,...]}` döndür; kimlikleri her bölümde alfabetik sırala ve girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def veri_ayrimi_dogrula(kayitlar):
    # KUSURLU BAŞLANGIÇ KODU: kimlikleri doğrulamadan ve sıralamadan yalnız eğitim listesine topluyor!
    return {"egitim": [k.get("id", "") for k in (kayitlar or []) if isinstance(k, dict)], "test": []}

print("Örnek ayrım:", veri_ayrimi_dogrula(json_yukle("veri/ayrim_kayitlari.json")))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-02")
```

```test
import copy
K = [
    {"id": "e-2", "etiket": "diger", "bolum": "egitim"},
    {"id": "t-1", "etiket": "yelkovan", "bolum": "test"},
    {"id": "e-1", "etiket": "yelkovan", "bolum": "egitim"},
    {"id": "t-2", "etiket": "diger", "bolum": "test"},
]
BEKLENEN = {"egitim": ["e-1", "e-2"], "test": ["t-1", "t-2"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once:
            return False
        if fn([dict(K[0], id="a" * 64), K[1]]) != {"egitim": ["a" * 64], "test": ["t-1"]}:
            return False
        for kayitlar in [
            None, {}, [], [None], [dict(K[0], ek=1)], [dict(K[0], id=""), K[1]],
            [dict(K[0], id="a b"), K[1]], [dict(K[0], id="a" * 65), K[1]], [dict(K[0], id=None), K[1]],
            [dict(K[0], etiket="baska"), K[1]], [dict(K[0], etiket=None), K[1]],
            [dict(K[0], bolum="dogrulama"), K[1]], [dict(K[0], bolum=None), K[1]],
            [K[0], K[0]], [K[0]], [K[1]],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(veri_ayrimi_dogrula), "kimlik, etiket, bölüm ve sıralama korunmalı")
def m_test(kayitlar):
    return veri_ayrimi_dogrula([x for x in kayitlar if x["bolum"] != "test"])
def m_id(kayitlar):
    return veri_ayrimi_dogrula([dict(x, id="ortak") for x in kayitlar])
def m_sira(kayitlar):
    sonuc = veri_ayrimi_dogrula(kayitlar)
    return {b: sorted(v, reverse=True) for b, v in sonuc.items()}
for ad, mutant in [("testi silen", m_test), ("kimlikleri eşitleyen", m_id), ("sırayı bozan", m_sira)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def veri_ayrimi_dogrula(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    gorulen = set()
    sonuc = {"egitim": [], "test": []}
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "etiket", "bolum"}:
            raise ValueError("kayıt şeması geçersiz")
        kimlik = kayit["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in gorulen:
            raise ValueError("kimlik yinelenemez")
        if kayit["etiket"] not in ("yelkovan", "diger"):
            raise ValueError("etiket geçersiz")
        if kayit["bolum"] not in ("egitim", "test"):
            raise ValueError("bölüm geçersiz")
        gorulen.add(kimlik)
        sonuc[kayit["bolum"]].append(kimlik)
    if not sonuc["egitim"] or not sonuc["test"]:
        raise ValueError("iki bölüm de dolu olmalı")
    return {"egitim": sorted(sonuc["egitim"]), "test": sorted(sonuc["test"])}
```

```hint
Kayıtları tek geçişte doğrula ve kimlikleri bölüm listelerine ekle. Dönmeden önce iki listenin de dolu olduğunu denetleyip sırala.
```
:::

::: gorev 2 · Sınıf ölçümlerini taban referansına çevir
`sinif_olcumleri(gercek, tahmin)` işlevini yaz. Girdiler aynı uzunlukta, boş olmayan listelerdir; her öğe `yelkovan` veya `diger` olmalıdır. Geçersiz veride `ValueError` yükselt.

`yelkovan` pozitif sınıf kabul edilerek TP, FP, FN ve TN sayımlarını yap. `{"tp":N,"fp":N,"fn":N,"tn":N,"dogruluk":X,"duyarlilik":X,"kesinlik":X}` döndür. Doğruluk `(tp+tn)/n`, duyarlılık `tp/(tp+fn)`, kesinlik `tp/(tp+fp)` olsun. Paydası sıfır olan oran `None` olsun; diğer oranlar altı ondalık basamağa yuvarlansın. Girdileri değiştirme.

```starter
from ai_guvence_veri import json_yukle

def sinif_olcumleri(gercek, tahmin):
    # KUSURLU BAŞLANGIÇ KODU: yalnız toplam doğruluğu hesaplayıp duyarlılık ve kesinliği sabit 0.0 bırakıyor!
    esit = sum(g == t for g, t in zip(gercek or [], tahmin or []))
    n = len(gercek) if gercek else 1
    return {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "dogruluk": round(esit / n, 6), "duyarlilik": 0.0, "kesinlik": 0.0}

ornek = json_yukle("veri/taban_tahminleri.json")
print("Örnek sınıf ölçümleri:", sinif_olcumleri(ornek["gercek"], ornek["tahmin"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-02")
```

```test
import copy
G = ["yelkovan", "yelkovan", "diger", "diger"]
T = ["yelkovan", "diger", "yelkovan", "diger"]
BEKLENEN = {"tp": 1, "fp": 1, "fn": 1, "tn": 1, "dogruluk": 0.5, "duyarlilik": 0.5, "kesinlik": 0.5}
def sozlesme(fn):
    try:
        gonce = copy.deepcopy(G)
        tonce = copy.deepcopy(T)
        if fn(G, T) != BEKLENEN or G != gonce or T != tonce:
            return False
        if fn(["diger", "diger"], ["diger", "diger"]) != {"tp": 0, "fp": 0, "fn": 0, "tn": 2, "dogruluk": 1.0, "duyarlilik": None, "kesinlik": None}:
            return False
        if fn(["yelkovan", "diger", "diger"], ["yelkovan", "yelkovan", "diger"])["dogruluk"] != 0.666667:
            return False
        if fn(["yelkovan"] * 3, ["yelkovan", "diger", "diger"])["duyarlilik"] != 0.333333:
            return False
        if fn(["diger", "diger", "yelkovan"], ["yelkovan"] * 3)["kesinlik"] != 0.333333:
            return False
        if fn(["yelkovan"], ["yelkovan"]) != {"tp": 1, "fp": 0, "fn": 0, "tn": 0, "dogruluk": 1.0, "duyarlilik": 1.0, "kesinlik": 1.0}:
            return False
        if fn(["yelkovan"], ["diger"]) != {"tp": 0, "fp": 0, "fn": 1, "tn": 0, "dogruluk": 0.0, "duyarlilik": 0.0, "kesinlik": None}:
            return False
        if fn(["diger"], ["yelkovan"])["kesinlik"] != 0:
            return False
        for gercek, tahmin in [
            (None, T), (G, None), ({}, T), (G, {}), ([], []), (G, T[:3]),
            (["baska"], ["diger"]), (["diger"], ["baska"]), ([None], ["diger"]), (["diger"], [None]),
            ([True], ["diger"]), (["diger"], [True]),
        ]:
            try:
                fn(gercek, tahmin)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sinif_olcumleri), "karışıklık sayıları, sıfır paydalar ve oranlar korunmalı")
def m_sinif(gercek, tahmin):
    return sinif_olcumleri(gercek, ["diger" for _ in tahmin])
def m_yarim(gercek, tahmin):
    return sinif_olcumleri(gercek[:2], tahmin[:2])
def m_etiket(gercek, tahmin):
    return sinif_olcumleri(["diger" for _ in gercek], tahmin)
for ad, mutant in [("tahminleri değiştiren", m_sinif), ("kayıtları silen", m_yarim), ("gerçeği değiştiren", m_etiket)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def sinif_olcumleri(gercek, tahmin):
    if not isinstance(gercek, list) or not isinstance(tahmin, list):
        raise ValueError("girdiler liste olmalı")
    if not gercek or len(gercek) != len(tahmin):
        raise ValueError("girdiler aynı uzunlukta ve boş olmayan olmalı")
    for deger in gercek:
        if deger not in ("yelkovan", "diger"):
            raise ValueError("gerçek etiket geçersiz")
    for deger in tahmin:
        if deger not in ("yelkovan", "diger"):
            raise ValueError("tahmin etiketi geçersiz")
    tp = sum(g == "yelkovan" and t == "yelkovan" for g, t in zip(gercek, tahmin))
    fp = sum(g == "diger" and t == "yelkovan" for g, t in zip(gercek, tahmin))
    fn = sum(g == "yelkovan" and t == "diger" for g, t in zip(gercek, tahmin))
    tn = sum(g == "diger" and t == "diger" for g, t in zip(gercek, tahmin))
    duyarlilik = round(tp / (tp + fn), 6) if tp + fn else None
    kesinlik = round(tp / (tp + fp), 6) if tp + fp else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "dogruluk": round((tp + tn) / len(gercek), 6), "duyarlilik": duyarlilik, "kesinlik": kesinlik}
```

```hint
Dört karışıklık hücresini ayrı say. Oranları hesaplamadan önce ilgili paydanın sıfır olup olmadığına bak.
```
:::

::: gorev 3 · Olasılıkların belirsizlik özetini üret
`belirsizlik_ozeti(olasiliklar, esik=0.25)` işlevini yaz. Olasılıklar boş olmayan listedir; her değer bool olmayan, `0 <= p <= 1` aralığında sonlu sayı olmalıdır. Eşik bool olmayan, `0 <= esik <= 0.5` aralığında sonlu sayıdır. Geçersiz veride `ValueError` yükselt.

Her olasılık için belirsizlik `min(p, 1-p)` olsun. `{"adet":N,"ortalama_belirsizlik":X,"yuksek_belirsizlik":N,"maksimum_belirsizlik":X}` döndür. Yüksek belirsizlik sayımında `belirsizlik >= esik` kullan; ortalama ve maksimumu altı ondalık basamağa yuvarla. Girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def belirsizlik_ozeti(olasiliklar, esik=0.25):
    # KUSURLU BAŞLANGIÇ KODU: min(p, 1-p) yerine doğrudan olasılıkların ortalamasını alıyor!
    adet = len(olasiliklar) if isinstance(olasiliklar, list) and olasiliklar else 1
    ort = round(sum(olasiliklar) / adet, 6) if isinstance(olasiliklar, list) and olasiliklar else 0.0
    return {"adet": adet, "ortalama_belirsizlik": ort, "yuksek_belirsizlik": 0, "maksimum_belirsizlik": ort}

ornek = json_yukle("veri/taban_tahminleri.json")
print("Örnek belirsizlik özeti:", belirsizlik_ozeti(ornek["olasiliklar"], 0.25))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-02")
```

```test
import copy
P = [0, 0.25, 0.5, 0.75, 1]
BEKLENEN = {"adet": 5, "ortalama_belirsizlik": 0.2, "yuksek_belirsizlik": 3, "maksimum_belirsizlik": 0.5}
def sozlesme(fn):
    try:
        once = copy.deepcopy(P)
        if fn(P) != BEKLENEN or P != once:
            return False
        if fn([0.1, 0.9]) != {"adet": 2, "ortalama_belirsizlik": 0.1, "yuksek_belirsizlik": 0, "maksimum_belirsizlik": 0.1}:
            return False
        if fn([0.1, 0.2, 0.8])["ortalama_belirsizlik"] != 0.166667:
            return False
        if fn([1 / 3])["maksimum_belirsizlik"] != 0.333333:
            return False
        if fn([0, 0.5], 0)["yuksek_belirsizlik"] != 2 or fn([0.5], 0.5)["yuksek_belirsizlik"] != 1:
            return False
        if fn([0.2, 0.8], 0.5)["yuksek_belirsizlik"] != 0:
            return False
        for olasiliklar, esik in [
            (None, 0.25), ({}, 0.25), ([], 0.25), ([None], 0.25), ([True], 0.25), (["0.5"], 0.25),
            ([float("nan")], 0.25), ([float("inf")], 0.25), ([-0.1], 0.25), ([1.1], 0.25),
            (P, None), (P, True), (P, "0.25"), (P, float("nan")), (P, float("inf")), (P, -0.1), (P, 0.6),
        ]:
            try:
                fn(olasiliklar, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(belirsizlik_ozeti), "aralıklar, eşik ve belirsizlik özeti korunmalı")
def m_olasilik(olasiliklar, esik=0.25):
    return belirsizlik_ozeti([0 for _ in olasiliklar], esik)
def m_sil(olasiliklar, esik=0.25):
    return belirsizlik_ozeti(olasiliklar[:1], esik)
def m_esik(olasiliklar, esik=0.25):
    return belirsizlik_ozeti(olasiliklar, 0.5)
for ad, mutant in [("olasılıkları silen", m_olasilik), ("kayıtları azaltan", m_sil), ("eşiği değiştiren", m_esik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def belirsizlik_ozeti(olasiliklar, esik=0.25):
    import math
    if isinstance(esik, bool) or not isinstance(esik, (int, float)):
        raise ValueError("eşik sayı olmalı")
    if not math.isfinite(esik):
        raise ValueError("eşik sonlu olmalı")
    if esik < 0 or esik > 0.5:
        raise ValueError("eşik aralık dışında")
    if not isinstance(olasiliklar, list) or not olasiliklar:
        raise ValueError("olasılıklar boş olmayan liste olmalı")
    for p in olasiliklar:
        if isinstance(p, bool) or not isinstance(p, (int, float)):
            raise ValueError("olasılık sayı olmalı")
        if not math.isfinite(p):
            raise ValueError("olasılık sonlu olmalı")
        if p < 0 or p > 1:
            raise ValueError("olasılık aralık dışında")
    belirsizlikler = [min(p, 1 - p) for p in olasiliklar]
    return {"adet": len(belirsizlikler), "ortalama_belirsizlik": round(sum(belirsizlikler) / len(belirsizlikler), 6), "yuksek_belirsizlik": sum(b >= esik for b in belirsizlikler), "maksimum_belirsizlik": round(max(belirsizlikler), 6)}
```

```hint
Eşiği ve her olasılığı ayrı doğrula. Belirsizlik listesini bir kez üretip sayım ve ortalamayı bu listeden hesapla.
```
:::

::: anlat Canlı sınıflandırıcıda veri ayrımı, karışıklık matrisi ve olasılık belirsizliği
İlk üç görevde eğitim/test ayrımını, sınıf metriklerini ve belirsizlik marjını sentetik dosyalar üzerinde kurdun. Şimdi aynı üç işlevi **gerçek `scikit-learn` (`LogisticRegression`) taban modeline** bağlıyoruz:

1. 160 örneklik sentetik ikili sınıflandırma kümesinin kayıtları `veri_ayrimi_dogrula` ile sızıntısız olarak 110 eğitim ve 50 test kaydına ayrılır.
2. `LogisticRegression` modeli yalnız eğitim bölümünde eğitilir; test bölümündeki tahmin etiketleri `sinif_olcumleri` ile (`tp`, `fp`, `fn`, `tn`, `dogruluk`, `duyarlilik`, `kesinlik`) değerlendirilir.
3. Modelin `predict_proba` çıktısından elde edilen gerçek pozitif sınıf olasılıkları `belirsizlik_ozeti` ile analiz edilip kanıt dosyasına kaydedilir.
:::

::: gorev Gerçek deney · Canlı sınıflandırıcıda taban model ve belirsizlik referansı
Önceki üç görevde yazdığın `veri_ayrimi_dogrula(kayitlar)`, `sinif_olcumleri(gercek, tahmin)` ve `belirsizlik_ozeti(olasiliklar, esik=0.25)` işlevlerini burada birleştir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 180
```

```starter
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_02 as L

def veri_ayrimi_dogrula(kayitlar):
    # KUSURLU BAŞLANGIÇ KODU: tüm kayıtları eğitim bölümüne yazıp testi boş bırakıyor!
    return {"egitim": [k.get("id", "") for k in (kayitlar or []) if isinstance(k, dict)], "test": []}

def sinif_olcumleri(gercek, tahmin):
    return {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "dogruluk": 0.0, "duyarlilik": None, "kesinlik": None}

def belirsizlik_ozeti(olasiliklar, esik=0.25):
    return {"adet": 0, "ortalama_belirsizlik": 0.0, "yuksek_belirsizlik": 0, "maksimum_belirsizlik": 0.0}

if ai_lab.CALISTIR:
    L.goster(veri_ayrimi_dogrula, sinif_olcumleri, belirsizlik_ozeti)
```

```test
import copy
import ai_lab
from sandbox import ai_gercek_ai_guvence_02 as L

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for s in ai_lab.kod_denetimi(src, yasak=("veri_ayrimi_dogrula_referans", "sinif_olcumleri_referans", "belirsizlik_ozeti_referans", "kanit_yaz")):
    ok(False, f"Güvenlik/kopya denetimi: {s}")
if not all(checks):
    stop()

def _sozlesme_kontrol():
    try:
        K = [
            {"id": "e-2", "etiket": "diger", "bolum": "egitim"},
            {"id": "t-1", "etiket": "yelkovan", "bolum": "test"},
            {"id": "e-1", "etiket": "yelkovan", "bolum": "egitim"},
            {"id": "t-2", "etiket": "diger", "bolum": "test"},
        ]
        if veri_ayrimi_dogrula(K) != {"egitim": ["e-1", "e-2"], "test": ["t-1", "t-2"]}:
            return False
        for bk in [None, [], [K[0]], [K[0], K[0]], [dict(K[0], bolum="x"), K[1]]]:
            try:
                veri_ayrimi_dogrula(bk)
                return False
            except ValueError:
                pass

        G = ["yelkovan", "yelkovan", "diger", "diger"]
        T = ["yelkovan", "diger", "yelkovan", "diger"]
        if sinif_olcumleri(G, T) != {"tp": 1, "fp": 1, "fn": 1, "tn": 1, "dogruluk": 0.5, "duyarlilik": 0.5, "kesinlik": 0.5}:
            return False
        if sinif_olcumleri(["diger"], ["diger"])["duyarlilik"] is not None:
            return False
        for bg, bt in [(None, T), ([], []), (G, T[:2]), (["x"], ["diger"])]:
            try:
                sinif_olcumleri(bg, bt)
                return False
            except ValueError:
                pass

        P = [0, 0.25, 0.5, 0.75, 1]
        if belirsizlik_ozeti(P) != {"adet": 5, "ortalama_belirsizlik": 0.2, "yuksek_belirsizlik": 3, "maksimum_belirsizlik": 0.5}:
            return False
        for bp, be in [(None, 0.25), ([], 0.25), ([1.2], 0.25), (P, 0.6), (P, True)]:
            try:
                belirsizlik_ozeti(bp, be)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_sozlesme_kontrol(), "veri_ayrimi_dogrula, sinif_olcumleri ve belirsizlik_ozeti sözleşme kontrollerini geçmeli")
if not all(checks):
    stop()

try:
    rapor = L.deney(veri_ayrimi_dogrula, sinif_olcumleri, belirsizlik_ozeti)
except ai_lab.GercekLabYok as e:
    ok(False, str(e))
    stop()
except Exception as e:
    ok(False, f"GERÇEK TABAN MODEL DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

k = rapor["kontroller"]
ok(k["ayrim_uyumu"] and k["sizinti_yok"], f"veri_ayrimi_dogrula canlı eğitim/test ayrımında referansla uyuşmalı: {rapor['ozet']['egitim_adedi']}/{rapor['ozet']['test_adedi']}")
ok(k["sinif_olcum_uyumu"], f"sinif_olcumleri canlı test tahminlerinde referansla uyuşmalı: {rapor['sinif_olcumleri']}")
ok(k["belirsizlik_uyumu"], f"belirsizlik_ozeti canlı predict_proba olasılıklarında referansla uyuşmalı: {rapor['belirsizlik_ozeti']}")

kabul = all(checks)
kanit_yolu = ai_lab.kanit_yaz("guvence-02-taban-model", dict(rapor, kaynak="gercek", kabul=kabul))
o = rapor["ozet"]
print(f"GERÇEK TABAN MODEL DENEYİ: sklearn={o['sklearn_surum']} dogruluk={o['sinif_olcumleri']['dogruluk']} ort_belirsizlik={o['belirsizlik_ozeti']['ortalama_belirsizlik']} kanıt={kanit_yolu}")
```

```solution
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_02 as L

def veri_ayrimi_dogrula(kayitlar):
    if not isinstance(kayitlar, list) or not kayitlar:
        raise ValueError("kayıtlar boş olmayan liste olmalı")
    gorulen = set()
    sonuc = {"egitim": [], "test": []}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"id", "etiket", "bolum"}:
            raise ValueError("kayıt şeması geçersiz")
        kimlik = kayit["id"]
        if not isinstance(kimlik, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik) or kimlik in gorulen:
            raise ValueError("kimlik geçersiz")
        if kayit["etiket"] not in ("yelkovan", "diger") or kayit["bolum"] not in ("egitim", "test"):
            raise ValueError("etiket/bölüm geçersiz")
        gorulen.add(kimlik)
        sonuc[kayit["bolum"]].append(kimlik)
    if not sonuc["egitim"] or not sonuc["test"]:
        raise ValueError("iki bölüm de dolu olmalı")
    return {"egitim": sorted(sonuc["egitim"]), "test": sorted(sonuc["test"])}

def sinif_olcumleri(gercek, tahmin):
    if not isinstance(gercek, list) or not isinstance(tahmin, list) or not gercek or len(gercek) != len(tahmin):
        raise ValueError("girdiler geçersiz")
    if any(g not in ("yelkovan", "diger") for g in gercek) or any(t not in ("yelkovan", "diger") for t in tahmin):
        raise ValueError("etiket geçersiz")
    tp = sum(g == "yelkovan" and t == "yelkovan" for g, t in zip(gercek, tahmin))
    fp = sum(g == "diger" and t == "yelkovan" for g, t in zip(gercek, tahmin))
    fn = sum(g == "yelkovan" and t == "diger" for g, t in zip(gercek, tahmin))
    tn = sum(g == "diger" and t == "diger" for g, t in zip(gercek, tahmin))
    duyarlilik = round(tp / (tp + fn), 6) if tp + fn else None
    kesinlik = round(tp / (tp + fp), 6) if tp + fp else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "dogruluk": round((tp + tn) / len(gercek), 6), "duyarlilik": duyarlilik, "kesinlik": kesinlik}

def belirsizlik_ozeti(olasiliklar, esik=0.25):
    if isinstance(esik, bool) or not isinstance(esik, (int, float)) or not math.isfinite(esik) or esik < 0 or esik > 0.5:
        raise ValueError("eşik geçersiz")
    if not isinstance(olasiliklar, list) or not olasiliklar:
        raise ValueError("olasılıklar geçersiz")
    for p in olasiliklar:
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or p < 0 or p > 1:
            raise ValueError("olasılık geçersiz")
    belirsizlikler = [min(p, 1 - p) for p in olasiliklar]
    return {"adet": len(belirsizlikler), "ortalama_belirsizlik": round(sum(belirsizlikler) / len(belirsizlikler), 6), "yuksek_belirsizlik": sum(b >= esik for b in belirsizlikler), "maksimum_belirsizlik": round(max(belirsizlikler), 6)}

if ai_lab.CALISTIR:
    L.goster(veri_ayrimi_dogrula, sinif_olcumleri, belirsizlik_ozeti)
```

```hint
Önceki üç görevde yazdığın `veri_ayrimi_dogrula`, `sinif_olcumleri` ve `belirsizlik_ozeti` işlevlerini eksiksiz taşı; canlı deneyde 160 örneklik `LogisticRegression` modeli üzerinde sınanır.
```
:::
