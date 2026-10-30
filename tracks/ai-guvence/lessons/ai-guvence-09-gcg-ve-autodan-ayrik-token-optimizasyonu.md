---
id: ai-guvence-09
title: "GCG ve AutoDAN: Ayrık Token Optimizasyonu"
summary: Ayrık adayları karşılaştır; arama izlerini sorgu bütçesiyle özetle, transfer başarısını raporla ve sonda gerçek dil modeli üzerinde koordinat gradyanı (GCG) sonek araması yürüt.
timeout: 300
---

::: anlat Ayrık arama sürekli gradyanı doğrudan tokena çeviremez
GCG benzeri yöntemler gradyan bilgisini aday tokenları sıralamak için kullanabilir; AutoDAN benzeri yöntemler ise ayrık diziler üzerinde genetik arama yapabilir. İkisinde de seçilen sonuç sürekli bir vektör değil, belirli token kimliklerinden oluşan bir dizidir. Aday puanı ile gerçek modelde ölçülen kayıp aynı şey değildir.

İlk üç görevde bütün tokenlar ve ölçümler deterministik fixture olarak verilir; son görevde ise yerel `SmolLM2-135M` (`ai_lab.dil_modeli()`) ve `torch` (`ai_lab.torch_cihazi()`) üzerinde gerçek koordinat gradyanı hesaplanarak hedef dizgeyi (canary) üreten ayrık sonek araması yürütülür.
:::

::: anlat En iyi kayıp tek başına arama maliyetini anlatmaz
Bir arama izinde adım, o ana kadar yapılan toplam sorgu ve gözlenen kayıp birlikte tutulmalıdır. En düşük kayıp seçilirken eşitlikte daha erken adım tercih edilebilir; toplam sorgu ise son adımın kümülatif değeridir. Sorgu sayıları adımlar boyunca katı biçimde artmalıdır.

Transfer ölçümü ayrıdır: aynı yöntemin farklı hedeflerdeki başarılarının oranı, toplam sorgusu ve ortalama genel yetenek puanı raporlanır. Başarı alanı yalnız gerçek bool değerlerden oluşur; `1` veya `"true"` başarı sayılmaz.
:::

::: tahmin Ayrık seçim ve transfer oranını tahmin et
Üç çıktı satırını yaz:

```python
print(min([(0.4, 2), (0.2, 1)])[1])
print(round(2 / 3, 6))
print(sum([True, False, True]))
```

???

```cikti
1
0.666667
2
```

İlk satır düşük puanlı adayı, ikinci satır altı ondalıklı transfer oranını, üçüncü satır yalnız başarılı denemelerin sayısını gösterir.
:::

::: gorev 1 · Ayrık adayları bütçeyle seç
`ayrik_adaylari_sec(adaylar, butce)` işlevini yaz. Adaylar boş olmayan listedir; her aday tam olarak `token` ve `skor` alanlarını taşır. Token bool olmayan, sıfır veya pozitif tamsayıdır ve yinelenemez. Skor bool olmayan sonlu sayıdır. Bütçe bool olmayan pozitif tamsayıdır. Geçersiz veride `ValueError` yükselt.

En düşük skorlu adaylar seçilir; skor eşitliğinde küçük token önce gelir. Bütçe kadar, bütçe aday sayısından büyükse bütün adayları içeren token listesi döndür. Girdiyi değiştirme.

```starter
def ayrik_adaylari_sec(adaylar, butce):
    return []
```

```test
import copy
A = [
    {"token": 41, "skor": 0.4},
    {"token": 7, "skor": 0.2},
    {"token": 19, "skor": 0.2},
    {"token": 3, "skor": 0.9},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(A)
        if fn(A, 2) != [7, 19] or A != once:
            return False
        if fn(A, 10) != [7, 19, 41, 3] or fn(A, 1) != [7]:
            return False
        if fn([{"token": 0, "skor": -1}, {"token": 2, "skor": 0}], 1) != [0]:
            return False
        for adaylar, butce in [
            (None, 1), ({}, 1), ([], 1), ([None], 1), ([dict(A[0], ek=1)], 1),
            ([dict(A[0], token=True)], 1), ([dict(A[0], token=1.0)], 1), ([dict(A[0], token=-1)], 1),
            ([A[0], A[0]], 2), ([dict(A[0], skor=True)], 1), ([dict(A[0], skor="0.4")], 1),
            ([dict(A[0], skor=float("nan"))], 1), ([dict(A[0], skor=float("inf"))], 1),
            (A, 0), (A, -1), (A, True), (A, 1.0), (A, None),
        ]:
            try:
                fn(adaylar, butce)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(ayrik_adaylari_sec), "ayrık aday, sıralama ve bütçe kuralları korunmalı")
def m_skor(adaylar, butce):
    return ayrik_adaylari_sec([dict(x, skor=0.8) for x in adaylar], butce)
def m_token(adaylar, butce):
    return ayrik_adaylari_sec([dict(x, token=5) for x in adaylar], butce)
def m_butce(adaylar, butce):
    return ayrik_adaylari_sec(adaylar, 1)
for ad, mutant in [("skorları silen", m_skor), ("tokenları değiştiren", m_token), ("bütçeyi küçülten", m_butce)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def ayrik_adaylari_sec(adaylar, butce):
    import math
    if not isinstance(adaylar, list):
        raise ValueError("adaylar liste olmalı")
    if not adaylar:
        raise ValueError("adaylar boş olamaz")
    if isinstance(butce, bool):
        raise ValueError("bütçe tamsayı olmalı")
    if not isinstance(butce, int):
        raise ValueError("bütçe tamsayı olmalı")
    if butce <= 0:
        raise ValueError("bütçe pozitif olmalı")
    tokenlar = set()
    for aday in adaylar:
        if not isinstance(aday, dict):
            raise ValueError("aday sözlük olmalı")
        if set(aday) != {"token", "skor"}:
            raise ValueError("aday şeması geçersiz")
        token = aday["token"]
        if isinstance(token, bool):
            raise ValueError("token tamsayı olmalı")
        if not isinstance(token, int):
            raise ValueError("token tamsayı olmalı")
        if token < 0:
            raise ValueError("token negatif olamaz")
        if token in tokenlar:
            raise ValueError("token yinelenemez")
        skor = aday["skor"]
        if isinstance(skor, bool):
            raise ValueError("skor sayı olmalı")
        if not isinstance(skor, (int, float)):
            raise ValueError("skor sayı olmalı")
        if not math.isfinite(skor):
            raise ValueError("skor sonlu olmalı")
        tokenlar.add(token)
    sirali = sorted(adaylar, key=lambda x: (x["skor"], x["token"]))
    return [x["token"] for x in sirali[:butce]]
```

```hint
Bütün adayları doğruladıktan sonra `(skor, token)` çiftine göre sırala ve dilimi yalnız çıktı için kullan.
```
:::

::: gorev 2 · GCG ve AutoDAN arama izlerini özetle
`arama_izini_ozetle(kayitlar)` işlevini yaz. Kayıtlar boş olmayan listedir ve her kayıt tam olarak `yontem`, `adim`, `sorgu`, `kayip` alanlarını taşır. Yöntem yalnız `GCG` veya `AutoDAN` olabilir. Adım bool olmayan, sıfır veya pozitif tamsayı; sorgu bool olmayan pozitif tamsayı; kayıp bool olmayan sonlu sayı ve `[0,1]` aralığındadır.

Aynı yöntemde adım yinelenemez ve kümülatif sorgu sayısı adımlar boyunca katı artmalıdır. Geçersiz veride `ValueError` yükselt. Her yöntem için `{"yontem":Y,"en_iyi_adim":N,"en_iyi_kayip":X,"toplam_sorgu":N}` üret; en iyi sonuç en düşük kayıp, eşitlikte en küçük adımdır. Kaybı altı ondalık basamağa yuvarla, toplam sorguyu en büyük adımın kümülatif değeri olarak ver ve özeti yöntem adına göre sırala. Girdiyi değiştirme.

```starter
def arama_izini_ozetle(kayitlar):
    return []
```

```test
import copy
K = [
    {"yontem": "GCG", "adim": 2, "sorgu": 12, "kayip": 0.3},
    {"yontem": "AutoDAN", "adim": 0, "sorgu": 3, "kayip": 0.7},
    {"yontem": "GCG", "adim": 0, "sorgu": 4, "kayip": 0.8},
    {"yontem": "GCG", "adim": 1, "sorgu": 8, "kayip": 0.4},
    {"yontem": "AutoDAN", "adim": 1, "sorgu": 6, "kayip": 0.5},
]
BEKLENEN = [
    {"yontem": "AutoDAN", "en_iyi_adim": 1, "en_iyi_kayip": 0.5, "toplam_sorgu": 6},
    {"yontem": "GCG", "en_iyi_adim": 2, "en_iyi_kayip": 0.3, "toplam_sorgu": 12},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once:
            return False
        esit = fn([K[2], dict(K[3], kayip=0.8), dict(K[0], kayip=0.8)])
        if esit[0]["en_iyi_adim"] != 0 or esit[0]["toplam_sorgu"] != 12:
            return False
        sinir = fn([{"yontem": "GCG", "adim": 0, "sorgu": 1, "kayip": 0}, {"yontem": "GCG", "adim": 1, "sorgu": 2, "kayip": 1}])
        if sinir[0]["en_iyi_adim"] != 0:
            return False
        yuvarla = fn([{"yontem": "GCG", "adim": 0, "sorgu": 1, "kayip": 1 / 6}])
        if yuvarla[0]["en_iyi_kayip"] != 0.166667:
            return False
        for kayitlar in [
            None, {}, [], [None], [dict(K[0], ek=1)], [dict(K[0], yontem="gcg")], [dict(K[0], yontem=None)],
            [K[0], K[0]], [K[2], dict(K[3], sorgu=4)], [K[2], dict(K[3], sorgu=3)],
            [dict(K[0], adim=True)], [dict(K[0], adim=2.0)], [dict(K[0], adim=-1)],
            [dict(K[0], sorgu=True)], [dict(K[0], sorgu=12.0)], [dict(K[0], sorgu=0)], [dict(K[0], sorgu=-1)],
            [dict(K[0], kayip=True)], [dict(K[0], kayip="0.3")], [dict(K[0], kayip=float("nan"))],
            [dict(K[0], kayip=float("inf"))], [dict(K[0], kayip=-0.1)], [dict(K[0], kayip=1.1)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(arama_izini_ozetle), "arama izi, bütçe, en iyi adım ve sıralama korunmalı")
def m_kayip(kayitlar):
    return arama_izini_ozetle([dict(x, kayip=0.9) for x in kayitlar])
def m_sorgu(kayitlar):
    return arama_izini_ozetle([dict(x, sorgu=1) for x in kayitlar])
def m_adim(kayitlar):
    return arama_izini_ozetle([dict(x, adim=0) for x in kayitlar])
for ad, mutant in [("kayıpları silen", m_kayip), ("sorguları silen", m_sorgu), ("adımları silen", m_adim)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def arama_izini_ozetle(kayitlar):
    import math
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    ciftler = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"yontem", "adim", "sorgu", "kayip"}:
            raise ValueError("kayıt şeması geçersiz")
        if kayit["yontem"] not in ("GCG", "AutoDAN"):
            raise ValueError("yöntem geçersiz")
        adim = kayit["adim"]
        if isinstance(adim, bool):
            raise ValueError("adım tamsayı olmalı")
        if not isinstance(adim, int):
            raise ValueError("adım tamsayı olmalı")
        if adim < 0:
            raise ValueError("adım negatif olamaz")
        sorgu = kayit["sorgu"]
        if isinstance(sorgu, bool):
            raise ValueError("sorgu tamsayı olmalı")
        if not isinstance(sorgu, int):
            raise ValueError("sorgu tamsayı olmalı")
        if sorgu <= 0:
            raise ValueError("sorgu pozitif olmalı")
        kayip = kayit["kayip"]
        if isinstance(kayip, bool):
            raise ValueError("kayıp sayı olmalı")
        if not isinstance(kayip, (int, float)):
            raise ValueError("kayıp sayı olmalı")
        if not math.isfinite(kayip):
            raise ValueError("kayıp sonlu olmalı")
        if kayip < 0 or kayip > 1:
            raise ValueError("kayıp aralık dışında")
        cift = (kayit["yontem"], adim)
        if cift in ciftler:
            raise ValueError("yöntem ve adım çifti yinelenemez")
        ciftler.add(cift)
    sirali = sorted(kayitlar, key=lambda x: (x["yontem"], x["adim"]))
    onceki = {}
    for kayit in sirali:
        yontem = kayit["yontem"]
        if yontem in onceki and kayit["sorgu"] <= onceki[yontem]:
            raise ValueError("kümülatif sorgu katı artmalı")
        onceki[yontem] = kayit["sorgu"]
    ozet = []
    for yontem in sorted({x["yontem"] for x in kayitlar}):
        grup = [x for x in sirali if x["yontem"] == yontem]
        en_iyi = min(grup, key=lambda x: (x["kayip"], x["adim"]))
        ozet.append({"yontem": yontem, "en_iyi_adim": en_iyi["adim"], "en_iyi_kayip": round(en_iyi["kayip"], 6), "toplam_sorgu": grup[-1]["sorgu"]})
    return ozet
```

```hint
Önce kayıtları doğrula, sonra yöntem ve adıma göre sıralayıp sorgu artışını denetle. En iyi adımı `(kayıp, adım)` anahtarıyla seç.
```
:::

::: gorev 3 · Transfer başarısını ve yeteneği raporla
`transfer_ozeti(kayitlar)` işlevini yaz. Kayıtlar boş olmayan listedir; her kayıt tam olarak `yontem`, `hedef`, `sorgu`, `basari`, `yetenek` alanlarını taşır. Yöntem yalnız `GCG` veya `AutoDAN`; hedef 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir. Sorgu bool olmayan pozitif tamsayı, başarı bool, yetenek bool olmayan sonlu sayı ve `[0,1]` aralığındadır. Geçersiz veride `ValueError` yükselt.

Her yöntem için `{"yontem":Y,"deneme":N,"basari":N,"transfer_orani":X,"toplam_sorgu":N,"ortalama_yetenek":X}` döndür. Transfer oranı başarı/deneme, ortalama yetenek bütün denemelerin yetenek ortalamasıdır; ikisini de altı ondalık basamağa yuvarla. Özeti yöntem adına göre sırala ve girdiyi değiştirme.

```starter
def transfer_ozeti(kayitlar):
    return []
```

```test
import copy
K = [
    {"yontem": "GCG", "hedef": "model-a", "sorgu": 4, "basari": True, "yetenek": 0.8},
    {"yontem": "AutoDAN", "hedef": "model-a", "sorgu": 3, "basari": False, "yetenek": 0.9},
    {"yontem": "GCG", "hedef": "model-b", "sorgu": 5, "basari": False, "yetenek": 0.6},
    {"yontem": "GCG", "hedef": "model-c", "sorgu": 6, "basari": True, "yetenek": 0.7},
    {"yontem": "AutoDAN", "hedef": "model-b", "sorgu": 2, "basari": True, "yetenek": 0.6},
]
BEKLENEN = [
    {"yontem": "AutoDAN", "deneme": 2, "basari": 1, "transfer_orani": 0.5, "toplam_sorgu": 5, "ortalama_yetenek": 0.75},
    {"yontem": "GCG", "deneme": 3, "basari": 2, "transfer_orani": 0.666667, "toplam_sorgu": 15, "ortalama_yetenek": 0.7},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once:
            return False
        sinir = fn([{"yontem": "GCG", "hedef": "a" * 64, "sorgu": 1, "basari": False, "yetenek": 0}, {"yontem": "GCG", "hedef": "b", "sorgu": 1, "basari": False, "yetenek": 1}, {"yontem": "GCG", "hedef": "c", "sorgu": 1, "basari": False, "yetenek": 0}])
        if sinir != [{"yontem": "GCG", "deneme": 3, "basari": 0, "transfer_orani": 0.0, "toplam_sorgu": 3, "ortalama_yetenek": 0.333333}]:
            return False
        for kayitlar in [
            None, {}, [], [None], [dict(K[0], ek=1)], [dict(K[0], yontem="diğer")],
            [dict(K[0], hedef="")], [dict(K[0], hedef="a b")], [dict(K[0], hedef="a" * 65)], [dict(K[0], hedef=None)],
            [dict(K[0], sorgu=True)], [dict(K[0], sorgu=4.0)], [dict(K[0], sorgu=0)], [dict(K[0], sorgu=-1)],
            [dict(K[0], basari=1)], [dict(K[0], basari="true")], [dict(K[0], basari=None)],
            [dict(K[0], yetenek=True)], [dict(K[0], yetenek="0.8")], [dict(K[0], yetenek=float("nan"))],
            [dict(K[0], yetenek=float("inf"))], [dict(K[0], yetenek=-0.1)], [dict(K[0], yetenek=1.1)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(transfer_ozeti), "transfer oranı, başarı türü, bütçe ve yetenek korunmalı")
def m_basari(kayitlar):
    return transfer_ozeti([dict(x, basari=False) for x in kayitlar])
def m_sorgu(kayitlar):
    return transfer_ozeti([dict(x, sorgu=1) for x in kayitlar])
def m_yetenek(kayitlar):
    return transfer_ozeti([dict(x, yetenek=0) for x in kayitlar])
for ad, mutant in [("başarıları silen", m_basari), ("sorguları silen", m_sorgu), ("yeteneği silen", m_yetenek)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def transfer_ozeti(kayitlar):
    import math
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"yontem", "hedef", "sorgu", "basari", "yetenek"}:
            raise ValueError("kayıt şeması geçersiz")
        if kayit["yontem"] not in ("GCG", "AutoDAN"):
            raise ValueError("yöntem geçersiz")
        if not isinstance(kayit["hedef"], str):
            raise ValueError("hedef string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["hedef"]):
            raise ValueError("hedef geçersiz")
        sorgu = kayit["sorgu"]
        if isinstance(sorgu, bool):
            raise ValueError("sorgu tamsayı olmalı")
        if not isinstance(sorgu, int):
            raise ValueError("sorgu tamsayı olmalı")
        if sorgu <= 0:
            raise ValueError("sorgu pozitif olmalı")
        if not isinstance(kayit["basari"], bool):
            raise ValueError("başarı bool olmalı")
        yetenek = kayit["yetenek"]
        if isinstance(yetenek, bool):
            raise ValueError("yetenek sayı olmalı")
        if not isinstance(yetenek, (int, float)):
            raise ValueError("yetenek sayı olmalı")
        if not math.isfinite(yetenek):
            raise ValueError("yetenek sonlu olmalı")
        if yetenek < 0 or yetenek > 1:
            raise ValueError("yetenek aralık dışında")
    ozet = []
    for yontem in sorted({x["yontem"] for x in kayitlar}):
        grup = [x for x in kayitlar if x["yontem"] == yontem]
        basari = sum(1 for x in grup if x["basari"])
        ozet.append({"yontem": yontem, "deneme": len(grup), "basari": basari, "transfer_orani": round(basari / len(grup), 6), "toplam_sorgu": sum(x["sorgu"] for x in grup), "ortalama_yetenek": round(sum(x["yetenek"] for x in grup) / len(grup), 6)})
    return ozet
```

```hint
Yöntem gruplarını oluştur; başarıları yalnız bool alanından say. Oran ve ortalamada grup büyüklüğünü payda olarak kullan.
```
:::

::: anlat Gerçek dil modelinde (SmolLM2-135M + torch) koordinat gradyanı ile ayrık sonek araması
İlk üç görevde ayrık aday seçimini, arama izi özetini ve transfer raporunu deterministik fixture'lar üzerinde doğruladın. Şimdi aynı üç işlevi **gerçek `SmolLM2-135M` nedensel dil modeli** (`ai_lab.dil_modeli()`) ve `torch` (`ai_lab.torch_cihazi()`) üzerinde çalışan canlı bir GCG koordinat gradyanı deneyine bağlıyoruz:

1. Son sonek konumundaki gömme (embedding) vektörüne göre hedef `PAFTA` tokenının çapraz entropi kaybının **gerçek gradyanı (`backward()`)** alınır ve aday tokenların birinci derece koordinat gradyan skorları hesaplanır.
2. `ayrik_adaylari_sec` en düşük skorlu aday tokenları bütçeyle seçer.
3. Seçilen ayrık tokenlar soneke yerleştirilerek modelde gerçek ileri geçiş (`forward pass`) kaybı ölçülür; elde edilen izler `arama_izini_ozetle` ve `transfer_ozeti` ile raporlanıp kanıta yazılır.
:::

::: gorev Gerçek deney · SmolLM2-135M üzerinde GCG koordinat gradyanı ve ayrık sonek araması
Önceki üç görevde yazdığın `ayrik_adaylari_sec(adaylar, butce)`, `arama_izini_ozetle(kayitlar)` ve `transfer_ozeti(kayitlar)` işlevlerini burada birleştir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 300
```

```starter
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_09 as L

def ayrik_adaylari_sec(adaylar, butce):
    # KUSURLU BAŞLANGIÇ KODU: skor sırasına bakmadan ilk adayı döndürüyor!
    return [adaylar[0]["token"]] if adaylar else []

def arama_izini_ozetle(kayitlar):
    return []

def transfer_ozeti(kayitlar):
    return []

if ai_lab.CALISTIR:
    L.goster(ayrik_adaylari_sec, arama_izini_ozetle, transfer_ozeti)
```

```test
import copy
import ai_lab
from sandbox import ai_gercek_ai_guvence_09 as L

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for s in ai_lab.kod_denetimi(src, yasak=("ayrik_adaylari_sec_referans", "arama_izini_ozetle_referans", "transfer_ozeti_referans", "kanit_yaz")):
    ok(False, f"Güvenlik/kopya denetimi: {s}")
if not all(checks):
    stop()

def _sozlesme_kontrol():
    try:
        adaylar = [{"token": 41, "skor": 0.4}, {"token": 7, "skor": 0.2}, {"token": 19, "skor": 0.2}, {"token": 3, "skor": 0.9}]
        if ayrik_adaylari_sec(adaylar, 2) != [7, 19] or ayrik_adaylari_sec(adaylar, 10) != [7, 19, 41, 3]:
            return False
        for ba, bb in [(None, 1), ([], 1), ([adaylar[0], adaylar[0]], 2), (adaylar, 0), (adaylar, True), ([dict(adaylar[0], token=-1)], 1)]:
            try:
                ayrik_adaylari_sec(ba, bb)
                return False
            except ValueError:
                pass

        iz = [
            {"yontem": "GCG", "adim": 2, "sorgu": 12, "kayip": 0.3},
            {"yontem": "AutoDAN", "adim": 0, "sorgu": 3, "kayip": 0.7},
            {"yontem": "GCG", "adim": 0, "sorgu": 4, "kayip": 0.8},
            {"yontem": "GCG", "adim": 1, "sorgu": 8, "kayip": 0.4},
            {"yontem": "AutoDAN", "adim": 1, "sorgu": 6, "kayip": 0.5},
        ]
        bek_iz = [
            {"yontem": "AutoDAN", "en_iyi_adim": 1, "en_iyi_kayip": 0.5, "toplam_sorgu": 6},
            {"yontem": "GCG", "en_iyi_adim": 2, "en_iyi_kayip": 0.3, "toplam_sorgu": 12},
        ]
        if arama_izini_ozetle(iz) != bek_iz:
            return False
        for biz in [None, [], [iz[0], iz[0]], [iz[2], dict(iz[3], sorgu=4)], [dict(iz[0], kayip=1.2)], [dict(iz[0], yontem="x")]]:
            try:
                arama_izini_ozetle(biz)
                return False
            except ValueError:
                pass

        tr = [
            {"yontem": "GCG", "hedef": "model-a", "sorgu": 4, "basari": True, "yetenek": 0.8},
            {"yontem": "AutoDAN", "hedef": "model-a", "sorgu": 3, "basari": False, "yetenek": 0.9},
            {"yontem": "GCG", "hedef": "model-b", "sorgu": 5, "basari": False, "yetenek": 0.6},
            {"yontem": "GCG", "hedef": "model-c", "sorgu": 6, "basari": True, "yetenek": 0.7},
            {"yontem": "AutoDAN", "hedef": "model-b", "sorgu": 2, "basari": True, "yetenek": 0.6},
        ]
        bek_tr = [
            {"yontem": "AutoDAN", "deneme": 2, "basari": 1, "transfer_orani": 0.5, "toplam_sorgu": 5, "ortalama_yetenek": 0.75},
            {"yontem": "GCG", "deneme": 3, "basari": 2, "transfer_orani": 0.666667, "toplam_sorgu": 15, "ortalama_yetenek": 0.7},
        ]
        if transfer_ozeti(tr) != bek_tr:
            return False
        for btr in [None, [], [dict(tr[0], basari=1)], [dict(tr[0], hedef="a b")], [dict(tr[0], sorgu=0)]]:
            try:
                transfer_ozeti(btr)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_sozlesme_kontrol(), "ayrik_adaylari_sec, arama_izini_ozetle ve transfer_ozeti sözleşme ve sınır kontrollerini geçmeli")
if not all(checks):
    stop()

try:
    rapor = L.deney(ayrik_adaylari_sec, arama_izini_ozetle, transfer_ozeti)
except ai_lab.GercekLabYok as e:
    ok(False, str(e))
    stop()
except Exception as e:
    ok(False, f"GERÇEK GCG SONEK ARAMASI DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

k = rapor["kontroller"]
ok(k["aday_secimi_uyumu"], f"ayrik_adaylari_sec gerçek gradyan skorlarında referansla uyuşmalı: {rapor['secilen_tokenlar']}")
ok(k["arama_izi_uyumu"], f"arama_izini_ozetle canlı ileri geçiş kayıplarında referansla uyuşmalı: {rapor['iz_ozeti']}")
ok(k["transfer_ozeti_uyumu"], f"transfer_ozeti canlı kayıtlarda referansla uyuşmalı: {rapor['transfer_ozeti']}")
ok(k["gercek_gradyan_ve_kayip_olculdu"], f"SmolLM2-135M üzerinde gerçek gradyan ve kayıp ölçülmeli: {rapor['ozet']}")

kabul = all(checks)
kanit_yolu = ai_lab.kanit_yaz("guvence-09-gcg-autodan", dict(rapor, kaynak="gercek", kabul=kabul))
o = rapor["ozet"]
print(f"GERÇEK GCG DENEYİ: model={o['model']} cihaz={o['cihaz']} secilen={o['secilen_tokenlar']} iz={o['iz_ozeti']} kanıt={kanit_yolu}")
```

```solution
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_09 as L

def ayrik_adaylari_sec(adaylar, butce):
    if not isinstance(adaylar, list) or not adaylar:
        raise ValueError("adaylar geçersiz")
    if isinstance(butce, bool) or not isinstance(butce, int) or butce <= 0:
        raise ValueError("bütçe geçersiz")
    tokenlar = set()
    for aday in adaylar:
        if not isinstance(aday, dict) or set(aday) != {"token", "skor"}:
            raise ValueError("aday şeması geçersiz")
        token = aday["token"]
        if isinstance(token, bool) or not isinstance(token, int) or token < 0 or token in tokenlar:
            raise ValueError("token geçersiz")
        skor = aday["skor"]
        if isinstance(skor, bool) or not isinstance(skor, (int, float)) or not math.isfinite(skor):
            raise ValueError("skor geçersiz")
        tokenlar.add(token)
    sirali = sorted(adaylar, key=lambda x: (x["skor"], x["token"]))
    return [x["token"] for x in sirali[:butce]]

def arama_izini_ozetle(kayitlar):
    if not isinstance(kayitlar, list) or not kayitlar:
        raise ValueError("kayıtlar geçersiz")
    ciftler = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"yontem", "adim", "sorgu", "kayip"}:
            raise ValueError("kayıt şeması geçersiz")
        if kayit["yontem"] not in ("GCG", "AutoDAN"):
            raise ValueError("yöntem geçersiz")
        adim = kayit["adim"]
        if isinstance(adim, bool) or not isinstance(adim, int) or adim < 0:
            raise ValueError("adım geçersiz")
        sorgu = kayit["sorgu"]
        if isinstance(sorgu, bool) or not isinstance(sorgu, int) or sorgu <= 0:
            raise ValueError("sorgu geçersiz")
        kayip = kayit["kayip"]
        if isinstance(kayip, bool) or not isinstance(kayip, (int, float)) or not math.isfinite(kayip) or kayip < 0 or kayip > 1:
            raise ValueError("kayıp geçersiz")
        cift = (kayit["yontem"], adim)
        if cift in ciftler:
            raise ValueError("yinelenen adım")
        ciftler.add(cift)
    sirali = sorted(kayitlar, key=lambda x: (x["yontem"], x["adim"]))
    onceki = {}
    for kayit in sirali:
        yontem = kayit["yontem"]
        if yontem in onceki and kayit["sorgu"] <= onceki[yontem]:
            raise ValueError("kümülatif sorgu katı artmalı")
        onceki[yontem] = kayit["sorgu"]
    ozet = []
    for yontem in sorted({x["yontem"] for x in kayitlar}):
        grup = [x for x in sirali if x["yontem"] == yontem]
        en_iyi = min(grup, key=lambda x: (x["kayip"], x["adim"]))
        ozet.append({"yontem": yontem, "en_iyi_adim": en_iyi["adim"], "en_iyi_kayip": round(en_iyi["kayip"], 6), "toplam_sorgu": grup[-1]["sorgu"]})
    return ozet

def transfer_ozeti(kayitlar):
    if not isinstance(kayitlar, list) or not kayitlar:
        raise ValueError("kayıtlar geçersiz")
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"yontem", "hedef", "sorgu", "basari", "yetenek"}:
            raise ValueError("kayıt şeması geçersiz")
        if kayit["yontem"] not in ("GCG", "AutoDAN"):
            raise ValueError("yöntem geçersiz")
        if not isinstance(kayit["hedef"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["hedef"]):
            raise ValueError("hedef geçersiz")
        sorgu = kayit["sorgu"]
        if isinstance(sorgu, bool) or not isinstance(sorgu, int) or sorgu <= 0:
            raise ValueError("sorgu geçersiz")
        if not isinstance(kayit["basari"], bool):
            raise ValueError("başarı bool olmalı")
        yetenek = kayit["yetenek"]
        if isinstance(yetenek, bool) or not isinstance(yetenek, (int, float)) or not math.isfinite(yetenek) or yetenek < 0 or yetenek > 1:
            raise ValueError("yetenek geçersiz")
    ozet = []
    for yontem in sorted({x["yontem"] for x in kayitlar}):
        grup = [x for x in kayitlar if x["yontem"] == yontem]
        basari = sum(1 for x in grup if x["basari"])
        ozet.append({"yontem": yontem, "deneme": len(grup), "basari": basari, "transfer_orani": round(basari / len(grup), 6), "toplam_sorgu": sum(x["sorgu"] for x in grup), "ortalama_yetenek": round(sum(x["yetenek"] for x in grup) / len(grup), 6)})
    return ozet

if ai_lab.CALISTIR:
    L.goster(ayrik_adaylari_sec, arama_izini_ozetle, transfer_ozeti)
```

```hint
Önceki üç görevde yazdığın `ayrik_adaylari_sec`, `arama_izini_ozetle` ve `transfer_ozeti` işlevlerini eksiksiz taşı; canlı deneyde SmolLM2-135M üzerinde koordinat gradyanı ve ileri geçiş kayıpları hesaplanır.
```
:::
