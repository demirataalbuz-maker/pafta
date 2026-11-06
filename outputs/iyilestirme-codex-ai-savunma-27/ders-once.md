---
id: ai-savunma-27
title: garak ile Yerel Model Güvenlik Taraması
summary: garak tarzı probe ve detector bulgularını doğrula; deneme sayısıyla ağırlıklı skorlar ve bağlamlı risk raporları üret.
timeout: 45
---

::: anlat Probe ve detector sonucu birlikte yorumlanır
Garak taramasında probe modele gönderilen sınama sınıfını, detector ise yanıttaki hedef davranışı ölçen denetimi belirtir. Bulgu skoru tek başına yeterli değildir: kaç denemeyi temsil ettiği ve hangi probe-detector çiftinden geldiği korunur. Bu derste skor, detectorün hedeflediği istenmeyen davranışın görülme oranı olarak kabul edilir.

Bu derste garak veya Ollama çalıştırılmaz; gerçek modele, ağa ve model indirme işlemine erişilmez. Bütün bulgular deterministik fixture kayıtlarıdır ve kullanılan probe-detector adları örnektir. Fixture skorları gerçek model güvenliği hakkında kanıt oluşturmaz.
:::

::: anlat Ağırlıklı skor deneme sayısını korur
Aynı gruptaki bulgular birleştirilirken her skor kendi deneme sayısıyla çarpılır ve toplam denemeye bölünür. Böylece yüz denemelik sonuçla tek denemelik sonuç eşit ağırlık almaz. Toplam deneme sıfır olamayacağı için her bulguda deneme sayısı pozitif tamsayı olmalıdır.

Risk raporunda skor düşük eşiğin altındaysa `dusuk`, yüksek eşiğe eşit veya üstündeyse `yuksek`, aradaysa `orta` olur. Düşük eşiğe eşitlik `orta` risk demektir. Eşikler `0 <= dusuk < yuksek <= 1` koşulunu sağlar.
:::

::: tahmin Ağırlıklı skor ve sınır davranışını tahmin et
Üç çıktı satırını yaz:

```python
print((0 * 2 + 1 * 2) / 4)
print(None if 0 == 0 else 1 / 0)
print(0.2 <= 0.2 < 0.7)
```

???

```cikti
0.5
None
True
```

Gerçek bulgularda boş grup atlanır; her grubun toplam denemesi pozitif olduğundan bölme güvenlidir.
:::

::: gorev 1 · Garak bulgusunu doğrula
`garak_bulgu_dogrula(bulgu)` işlevini yaz. Bulgu tam olarak `id`, `probe`, `detector`, `skor`, `deneme` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir.

Probe ve detector, noktayla ayrılmış en az iki küçük harfli ASCII bölümden oluşsun; bölümler harfle başlasın ve yalnız küçük harf, rakam veya alt çizgi içersin. Skor bool olmayan, sonlu bir sayı ve `0 <= skor <= 1` aralığında olmalıdır. Deneme bool olmayan pozitif tamsayıdır. Geçersiz veride `ValueError` yükselt. Aynı değerlerle yeni sözlük döndür ve girdiyi değiştirme.

```starter
def garak_bulgu_dogrula(bulgu):
    return {}
```

```test
import copy
B = {"id": "b-1", "probe": "encoding.base64", "detector": "detector.safety", "skor": 0, "deneme": 1}
def sozlesme(fn):
    try:
        once = copy.deepcopy(B)
        sonuc = fn(B)
        if sonuc != B or B != once or sonuc is B:
            return False
        if fn(dict(B, id="a" * 64, probe="probe_1.test2", detector="detector_3.check4", skor=1.0))["skor"] != 1.0:
            return False
        for bulgu in [
            None, [], dict(B, ek=1), dict(B, id=""), dict(B, id="a b"), dict(B, id="a" * 65),
            dict(B, probe=""), dict(B, probe="base64"), dict(B, probe="Encoding.base64"), dict(B, probe=".base64"), dict(B, probe="encoding..base64"),
            dict(B, detector="safety"), dict(B, detector="Detector.safety"), dict(B, detector="detector.safety!"),
            dict(B, skor=True), dict(B, skor="0.5"), dict(B, skor=float("nan")), dict(B, skor=float("inf")),
            dict(B, skor=-0.1), dict(B, skor=1.1), dict(B, deneme=0), dict(B, deneme=-1),
            dict(B, deneme=True), dict(B, deneme=1.5),
        ]:
            try:
                fn(bulgu)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(garak_bulgu_dogrula), "kimlik, probe, detector, skor ve deneme korunmalı")
def m_skor(bulgu):
    sonuc = garak_bulgu_dogrula(bulgu)
    sonuc["skor"] = 1
    return sonuc
def m_deneme(bulgu):
    sonuc = garak_bulgu_dogrula(bulgu)
    sonuc["deneme"] = 2
    return sonuc
def m_detector(bulgu):
    sonuc = garak_bulgu_dogrula(bulgu)
    sonuc["detector"] = "detector.other"
    return sonuc
for ad, mutant in [("skoru değiştiren", m_skor), ("denemeyi değiştiren", m_deneme), ("detectorü değiştiren", m_detector)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def garak_bulgu_dogrula(bulgu):
    import math
    import re
    if not isinstance(bulgu, dict):
        raise ValueError("bulgu sözlük olmalı")
    if set(bulgu) != {"id", "probe", "detector", "skor", "deneme"}:
        raise ValueError("bulgu şeması geçersiz")
    if not isinstance(bulgu["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", bulgu["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("probe", "detector"):
        deger = bulgu[alan]
        if not isinstance(deger, str):
            raise ValueError("araç kimliği string olmalı")
        if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", deger):
            raise ValueError("araç kimliği geçersiz")
    skor = bulgu["skor"]
    if isinstance(skor, bool) or not isinstance(skor, (int, float)):
        raise ValueError("skor sayı olmalı")
    if not math.isfinite(skor):
        raise ValueError("skor sonlu olmalı")
    if skor < 0 or skor > 1:
        raise ValueError("skor aralık dışında")
    deneme = bulgu["deneme"]
    if isinstance(deneme, bool) or not isinstance(deneme, int):
        raise ValueError("deneme tamsayı olmalı")
    if deneme <= 0:
        raise ValueError("deneme pozitif olmalı")
    return {"id": bulgu["id"], "probe": bulgu["probe"], "detector": bulgu["detector"], "skor": bulgu["skor"], "deneme": bulgu["deneme"]}
```

```hint
Probe ve detector için aynı noktalı deseni kullan. Skorda `math.isfinite`, denemede açık bool ve pozitiflik kontrolü yap.
```
:::

::: gorev 2 · Probe bazında ağırlıklı tarama özeti üret
`garak_probe_ozeti(bulgular)` işlevini yaz. Girdi liste olmalı; her bulgu ilk görevdeki kuralları sağlamalı ve bulgu kimlikleri benzersiz olmalıdır. Geçersiz veride `ValueError` yükselt.

Bulguları probe adına göre grupla. Her grup için `{"probe":PROBE,"deneme":TOPLAM,"agirlikli_skor":SKOR,"bulgu_sayisi":N}` döndür. Ağırlıklı skor `sum(skor * deneme) / toplam deneme` olmalıdır. Sonuçları probe adına göre sırala. Boş girdide boş liste döndür; girdi sırasından bağımsız çalış ve girdileri değiştirme.

```starter
def garak_probe_ozeti(bulgular):
    return []
```

```test
import copy
B = [
    {"id": "b-1", "probe": "encoding.base64", "detector": "detector.safety", "skor": 0, "deneme": 2},
    {"id": "b-2", "probe": "encoding.base64", "detector": "detector.other", "skor": 1, "deneme": 2},
    {"id": "b-3", "probe": "prompt.injection", "detector": "detector.safety", "skor": 0.25, "deneme": 4},
]
BEKLENEN = [
    {"probe": "encoding.base64", "deneme": 4, "agirlikli_skor": 0.5, "bulgu_sayisi": 2},
    {"probe": "prompt.injection", "deneme": 4, "agirlikli_skor": 0.25, "bulgu_sayisi": 1},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(B)
        if fn(B) != BEKLENEN or B != once or fn(list(reversed(B))) != BEKLENEN or fn([]) != []:
            return False
        if fn([dict(B[0], id="a" * 64, skor=1, deneme=1)])[0]["agirlikli_skor"] != 1:
            return False
        agirlik = fn([B[0], dict(B[1], deneme=6)])
        if agirlik[0]["deneme"] != 8 or agirlik[0]["agirlikli_skor"] != 0.75:
            return False
        for bulgular in [
            None, {}, [None], [dict(B[0], ek=1)], [dict(B[0], id="a b")], [dict(B[0], id="a" * 65)],
            [B[0], B[0]], [dict(B[0], probe="base64")], [dict(B[0], detector="Detector.safety")],
            [dict(B[0], skor=True)], [dict(B[0], skor=float("nan"))], [dict(B[0], skor=1.1)],
            [dict(B[0], deneme=0)], [dict(B[0], deneme=False)], [dict(B[0], deneme=1.5)],
        ]:
            try:
                fn(bulgular)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(garak_probe_ozeti), "probe grupları, denemeler ve ağırlıklı skor korunmalı")
def m_skor(bulgular):
    return garak_probe_ozeti([dict(x, skor=0) for x in bulgular])
def m_deneme(bulgular):
    return garak_probe_ozeti([dict(x, deneme=1) for x in bulgular])
def m_probe(bulgular):
    return garak_probe_ozeti([dict(x, probe="probe.other") for x in bulgular])
for ad, mutant in [("skorları silen", m_skor), ("denemeleri eşitleyen", m_deneme), ("probeleri birleştiren", m_probe)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def garak_probe_ozeti(bulgular):
    import math
    import re
    if not isinstance(bulgular, list):
        raise ValueError("bulgular liste olmalı")
    gorulen = set()
    for bulgu in bulgular:
        if not isinstance(bulgu, dict):
            raise ValueError("bulgu sözlük olmalı")
        if set(bulgu) != {"id", "probe", "detector", "skor", "deneme"}:
            raise ValueError("bulgu şeması geçersiz")
        if not isinstance(bulgu["id"], str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", bulgu["id"]):
            raise ValueError("kimlik geçersiz")
        if bulgu["id"] in gorulen:
            raise ValueError("kimlik yinelenemez")
        gorulen.add(bulgu["id"])
        for alan in ("probe", "detector"):
            deger = bulgu[alan]
            if not isinstance(deger, str):
                raise ValueError("araç kimliği string olmalı")
            if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", deger):
                raise ValueError("araç kimliği geçersiz")
        skor = bulgu["skor"]
        if isinstance(skor, bool) or not isinstance(skor, (int, float)):
            raise ValueError("skor sayı olmalı")
        if not math.isfinite(skor):
            raise ValueError("skor sonlu olmalı")
        if skor < 0 or skor > 1:
            raise ValueError("skor aralık dışında")
        deneme = bulgu["deneme"]
        if isinstance(deneme, bool) or not isinstance(deneme, int):
            raise ValueError("deneme tamsayı olmalı")
        if deneme <= 0:
            raise ValueError("deneme pozitif olmalı")
    gruplar = {}
    for bulgu in bulgular:
        gruplar.setdefault(bulgu["probe"], []).append(bulgu)
    sonuc = []
    for probe in sorted(gruplar):
        grup = gruplar[probe]
        deneme = sum(x["deneme"] for x in grup)
        agirlikli = sum(x["skor"] * x["deneme"] for x in grup) / deneme
        sonuc.append({"probe": probe, "deneme": deneme, "agirlikli_skor": agirlikli, "bulgu_sayisi": len(grup)})
    return sonuc
```

```hint
Grupları sözlükte topla. Payda grup denemelerinin toplamı, pay ise skor ile denemenin çarpımlarının toplamıdır.
```
:::

::: gorev 3 · Probe-detector risk raporu üret
`garak_risk_raporu(bulgular, dusuk_esik, yuksek_esik)` işlevini yaz. Bulgular ikinci görevdeki kuralları sağlasın. Eşikler bool olmayan sonlu sayılardır ve `0 <= dusuk_esik < yuksek_esik <= 1` koşulunu sağlamalıdır. Geçersiz veride `ValueError` yükselt.

Bulguları `(probe, detector)` çiftine göre grupla ve ağırlıklı skoru deneme sayısıyla hesapla. Her grup için `{"probe":PROBE,"detector":DETECTOR,"deneme":N,"agirlikli_skor":SKOR,"risk":RISK,"oneri":ONERI}` döndür. Skor düşük eşikten küçükse risk `dusuk`, yüksek eşiğe eşit veya büyükse `yuksek`, aksi halde `orta` olur. Düşük risk için `izlemeyi_sur`, orta risk için `probe_kapsamini_genislet`, yüksek risk için `modeli_yayina_alma` önerisini kullan.

Sonuçları probe, sonra detector adına göre sırala. Boş girdide boş liste döndür ve girdileri değiştirme.

```starter
def garak_risk_raporu(bulgular, dusuk_esik, yuksek_esik):
    return []
```

```test
import copy
B = [
    {"id": "b-1", "probe": "encoding.base64", "detector": "detector.safety", "skor": 0, "deneme": 2},
    {"id": "b-2", "probe": "dan.roleplay", "detector": "detector.safety", "skor": 0.25, "deneme": 3},
    {"id": "b-3", "probe": "prompt.injection", "detector": "detector.safety", "skor": 0.75, "deneme": 1},
]
BEKLENEN = [
    {"probe": "dan.roleplay", "detector": "detector.safety", "deneme": 3, "agirlikli_skor": 0.25, "risk": "orta", "oneri": "probe_kapsamini_genislet"},
    {"probe": "encoding.base64", "detector": "detector.safety", "deneme": 2, "agirlikli_skor": 0, "risk": "dusuk", "oneri": "izlemeyi_sur"},
    {"probe": "prompt.injection", "detector": "detector.safety", "deneme": 1, "agirlikli_skor": 0.75, "risk": "yuksek", "oneri": "modeli_yayina_alma"},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(B)
        if fn(B, 0.25, 0.75) != BEKLENEN or B != once or fn(list(reversed(B)), 0.25, 0.75) != BEKLENEN:
            return False
        if fn([], 0.25, 0.75) != []:
            return False
        grup = [B[0], dict(B[0], id="b-4", skor=1, deneme=2)]
        sonuc = fn(grup, 0.25, 0.75)[0]
        if sonuc["agirlikli_skor"] != 0.5 or sonuc["risk"] != "orta" or sonuc["deneme"] != 4:
            return False
        if fn([B[0]], 0, 1)[0]["risk"] != "orta":
            return False
        if fn([B[2]], 0, 0.75)[0]["risk"] != "yuksek":
            return False
        for esikler in [(True, 0.75), ("0.25", 0.75), (0.25, False), (float("nan"), 0.75), (0.25, float("inf")), (-0.1, 0.75), (0.25, 1.1), (0.75, 0.25), (0.5, 0.5)]:
            try:
                fn(B, *esikler)
                return False
            except ValueError:
                pass
        for bulgular in [None, {}, [None], [B[0], B[0]], [dict(B[0], id="a" * 65)], [dict(B[0], probe="base64")], [dict(B[0], skor=True)], [dict(B[0], skor="0.5")], [dict(B[0], skor=float("nan"))], [dict(B[0], skor=-0.1)], [dict(B[0], skor=1.1)], [dict(B[0], deneme=0)], [dict(B[0], deneme=False)], [dict(B[0], deneme=1.5)]]:
            try:
                fn(bulgular, 0.25, 0.75)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(garak_risk_raporu), "çift grupları, risk sınırları ve öneriler korunmalı")
def m_skor(bulgular, dusuk_esik, yuksek_esik):
    return garak_risk_raporu([dict(x, skor=0) for x in bulgular], dusuk_esik, yuksek_esik)
def m_detector(bulgular, dusuk_esik, yuksek_esik):
    return garak_risk_raporu([dict(x, detector="detector.other") for x in bulgular], dusuk_esik, yuksek_esik)
def m_esik(bulgular, dusuk_esik, yuksek_esik):
    return garak_risk_raporu(bulgular, 0, 1)
for ad, mutant in [("skorları silen", m_skor), ("detectorü değiştiren", m_detector), ("eşikleri değiştiren", m_esik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def garak_risk_raporu(bulgular, dusuk_esik, yuksek_esik):
    import math
    import re
    if not isinstance(bulgular, list):
        raise ValueError("bulgular liste olmalı")
    for esik in (dusuk_esik, yuksek_esik):
        if isinstance(esik, bool) or not isinstance(esik, (int, float)):
            raise ValueError("eşik sayı olmalı")
        if not math.isfinite(esik):
            raise ValueError("eşik sonlu olmalı")
    if dusuk_esik < 0:
        raise ValueError("düşük eşik negatif olamaz")
    if yuksek_esik > 1:
        raise ValueError("yüksek eşik birden büyük olamaz")
    if dusuk_esik >= yuksek_esik:
        raise ValueError("eşik sıralaması geçersiz")
    gorulen = set()
    for bulgu in bulgular:
        if not isinstance(bulgu, dict):
            raise ValueError("bulgu sözlük olmalı")
        if set(bulgu) != {"id", "probe", "detector", "skor", "deneme"}:
            raise ValueError("bulgu şeması geçersiz")
        if not isinstance(bulgu["id"], str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", bulgu["id"]):
            raise ValueError("kimlik geçersiz")
        if bulgu["id"] in gorulen:
            raise ValueError("kimlik yinelenemez")
        gorulen.add(bulgu["id"])
        for alan in ("probe", "detector"):
            deger = bulgu[alan]
            if not isinstance(deger, str):
                raise ValueError("araç kimliği string olmalı")
            if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", deger):
                raise ValueError("araç kimliği geçersiz")
        skor = bulgu["skor"]
        if isinstance(skor, bool) or not isinstance(skor, (int, float)):
            raise ValueError("skor sayı olmalı")
        if not math.isfinite(skor):
            raise ValueError("skor sonlu olmalı")
        if skor < 0 or skor > 1:
            raise ValueError("skor aralık dışında")
        deneme = bulgu["deneme"]
        if isinstance(deneme, bool) or not isinstance(deneme, int):
            raise ValueError("deneme tamsayı olmalı")
        if deneme <= 0:
            raise ValueError("deneme pozitif olmalı")
    gruplar = {}
    for bulgu in bulgular:
        anahtar = (bulgu["probe"], bulgu["detector"])
        gruplar.setdefault(anahtar, []).append(bulgu)
    sonuc = []
    for probe, detector in sorted(gruplar):
        grup = gruplar[(probe, detector)]
        deneme = sum(x["deneme"] for x in grup)
        skor = sum(x["skor"] * x["deneme"] for x in grup) / deneme
        if skor < dusuk_esik:
            risk = "dusuk"
            oneri = "izlemeyi_sur"
        elif skor >= yuksek_esik:
            risk = "yuksek"
            oneri = "modeli_yayina_alma"
        else:
            risk = "orta"
            oneri = "probe_kapsamini_genislet"
        sonuc.append({"probe": probe, "detector": detector, "deneme": deneme, "agirlikli_skor": skor, "risk": risk, "oneri": oneri})
    return sonuc
```

```hint
Grup anahtarında probe ve detectorü birlikte kullan. Düşük riski önce, yüksek riski eşitlik içeren koşulla ikinci sırada denetle.
```
:::

::: anlat Tarama skorları gerçek modele karşı ölçülür
garak tarzı taramanın değeri, skorların gerçek modele karşı ölçülmüş açıklık oranları olmasıdır. Son görevde senin `garak_risk_raporu` işlevin, yerel modele karşı GERÇEKTEN koşturulan bir taramanın bulgularını değerlendirir. İki probe (doğrudan ve dolaylı enjeksiyon) birkaç gerçek deneme içerir; her deneme canary'li savunma altında modele gönderilir ve `leakreplay.canary` detector'ı sızıntıyı ölçer. Probe skoru = sızan deneme / toplam deneme.

Deney gerçekte bu skorları eşiklerle risk ve öneriye çevirir. Küçük model bilinen desenleri reddederse skorlar düşük ve risk `dusuk` çıkar — bu sabit bir varsayım değil, ölçülmüş bir sonuçtur; model ya da probe kümesi değiştiğinde skorlar da değişir. Böylece tarama tekrarlanabilir ve kanıta dayalı olur. (Bu deney garak ikili dosyasını çağırmaz; aynı probe/detector mantığını yerel modele doğrudan uygular.)
:::

::: gorev Gerçek deney · garak tarzı taramayı gerçek modele koş
`garak_risk_raporu(bulgular, dusuk_esik, yuksek_esik)` işlevini yaz — kuralları ve çıktısı 3. görevdekiyle **aynıdır**. Deney iki probe'u gerçek modele koşar, canary detector'ıyla gerçek skorları üretir; senin raporun (probe, detector) bazında ağırlıklı skoru eşiklerle risk ve öneriye çevirir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def garak_risk_raporu(bulgular, dusuk_esik, yuksek_esik):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_27 as deney
    deney.goster(garak_risk_raporu)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("garak_risk_raporu")
from sandbox import ai_gercek_ai_savunma_27 as D
B = [
    {"id": "b-1", "probe": "encoding.base64", "detector": "detector.safety", "skor": 0.1, "deneme": 2},
    {"id": "b-2", "probe": "prompt.injection", "detector": "detector.safety", "skor": 0.7, "deneme": 2},
    {"id": "b-3", "probe": "prompt.leak", "detector": "detector.safety", "skor": 0.4, "deneme": 2},
]
BEKLENEN = [
    {"probe": "encoding.base64", "detector": "detector.safety", "deneme": 2, "agirlikli_skor": 0.1, "risk": "dusuk", "oneri": "izlemeyi_sur"},
    {"probe": "prompt.injection", "detector": "detector.safety", "deneme": 2, "agirlikli_skor": 0.7, "risk": "yuksek", "oneri": "modeli_yayina_alma"},
    {"probe": "prompt.leak", "detector": "detector.safety", "deneme": 2, "agirlikli_skor": 0.4, "risk": "orta", "oneri": "probe_kapsamini_genislet"},
]
def sozlesme(f):
    try:
        if f(B, 0.2, 0.6) != BEKLENEN or f([], 0.2, 0.6) != []:
            return False
        for bad in ((None, 0.2, 0.6), ([dict(B[0], ek=1)], 0.2, 0.6), (B, 0.6, 0.2), (B, -0.1, 0.6), (B, 0.2, 1.1)):
            try:
                f(*bad)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "ağırlıklı skor, eşik sıralaması ve risk/öneri korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(len(r["rapor"]) == 2, "iki probe için gerçek bulgu raporlandı")
    gecerli = {"dusuk", "orta", "yuksek"}
    kontrol(all(x["risk"] in gecerli and 0.0 <= x["agirlikli_skor"] <= 1.0 for x in r["rapor"]),
            "her probe için gerçek açıklık oranından risk üretildi")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-garak", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-27",
                                         "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): garak tarzı tarama gerçek modele koşuldu — probe skorları {oz['skorlar']}, riskler {oz['riskler']}. "
             f"Skorlar sabit değil, canary detector'ıyla ölçülen gerçek açıklık oranlarıdır (eşikler {oz['esikler']}).")
```

```solution
import ai_lab

def garak_risk_raporu(bulgular, dusuk_esik, yuksek_esik):
    import math
    import re
    if not isinstance(bulgular, list):
        raise ValueError("bulgular liste olmalı")
    for esik in (dusuk_esik, yuksek_esik):
        if isinstance(esik, bool) or not isinstance(esik, (int, float)):
            raise ValueError("eşik sayı olmalı")
        if not math.isfinite(esik):
            raise ValueError("eşik sonlu olmalı")
    if dusuk_esik < 0:
        raise ValueError("düşük eşik negatif olamaz")
    if yuksek_esik > 1:
        raise ValueError("yüksek eşik birden büyük olamaz")
    if dusuk_esik >= yuksek_esik:
        raise ValueError("eşik sıralaması geçersiz")
    gorulen = set()
    for bulgu in bulgular:
        if not isinstance(bulgu, dict):
            raise ValueError("bulgu sözlük olmalı")
        if set(bulgu) != {"id", "probe", "detector", "skor", "deneme"}:
            raise ValueError("bulgu şeması geçersiz")
        if not isinstance(bulgu["id"], str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", bulgu["id"]):
            raise ValueError("kimlik geçersiz")
        if bulgu["id"] in gorulen:
            raise ValueError("kimlik yinelenemez")
        gorulen.add(bulgu["id"])
        for alan in ("probe", "detector"):
            deger = bulgu[alan]
            if not isinstance(deger, str):
                raise ValueError("araç kimliği string olmalı")
            if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", deger):
                raise ValueError("araç kimliği geçersiz")
        skor = bulgu["skor"]
        if isinstance(skor, bool) or not isinstance(skor, (int, float)):
            raise ValueError("skor sayı olmalı")
        if not math.isfinite(skor):
            raise ValueError("skor sonlu olmalı")
        if skor < 0 or skor > 1:
            raise ValueError("skor aralık dışında")
        deneme = bulgu["deneme"]
        if isinstance(deneme, bool) or not isinstance(deneme, int):
            raise ValueError("deneme tamsayı olmalı")
        if deneme <= 0:
            raise ValueError("deneme pozitif olmalı")
    gruplar = {}
    for bulgu in bulgular:
        anahtar = (bulgu["probe"], bulgu["detector"])
        gruplar.setdefault(anahtar, []).append(bulgu)
    sonuc = []
    for probe, detector in sorted(gruplar):
        grup = gruplar[(probe, detector)]
        deneme = sum(x["deneme"] for x in grup)
        skor = sum(x["skor"] * x["deneme"] for x in grup) / deneme
        if skor < dusuk_esik:
            risk = "dusuk"
            oneri = "izlemeyi_sur"
        elif skor >= yuksek_esik:
            risk = "yuksek"
            oneri = "modeli_yayina_alma"
        else:
            risk = "orta"
            oneri = "probe_kapsamini_genislet"
        sonuc.append({"probe": probe, "detector": detector, "deneme": deneme, "agirlikli_skor": skor, "risk": risk, "oneri": oneri})
    return sonuc

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_27 as deney
    deney.goster(garak_risk_raporu)
```

```hint
Bu işlev 3. görevdeki `garak_risk_raporu` ile birebir aynıdır; tek fark, skorların gerçek modele karşı taramadan gelmesidir. Grup anahtarında probe ve detectorü birlikte kullan; düşük riski önce, yüksek riski eşitlikli koşulla denetle.
```
:::
