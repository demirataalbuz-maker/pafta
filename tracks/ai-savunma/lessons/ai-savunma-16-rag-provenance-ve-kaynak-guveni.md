---
id: ai-savunma-16
title: RAG Provenance ve Kaynak Güveni
summary: Kaynak defterini doğrula, RAG parçalarını kaynak sürümü ve imzayla ilişkilendir, yalnız doğrulanabilir parçaları güven eşiğiyle seç.
timeout: 45
---

::: anlat Provenance parçanın doğrulanabilir kimliğidir
RAG yanıtındaki her parça kaynak, belge sürümü ve içerik özetiyle ilişkilendirilir. Qdrant benzerlik skoru parçanın konuyla ilgisini ölçer; kaynağın güvenilir veya doğrulanabilir olduğunu kanıtlamaz. Bu nedenle skor ile kaynak güveni ayrı alanlardır.

Bu derste FastAPI veya Qdrant çağrısı yapılmaz. Kaynak defteri ve getirilen parçalar deterministik kayıtlar olarak işlenir. Kaynağı bulunmayan, sürümü uyuşmayan, imzasız veya pasif kaynaktan gelen parça doğrulanabilir sayılmaz.
:::

::: anlat Güven eşiği sıralama skorundan bağımsızdır
Güven düzeyleri `yuksek`, `orta`, `dusuk` sırasıyla değerlendirilir. `orta` eşiği yüksek ve orta kaynakları kapsar; düşük kaynağı kapsamaz. Yüksek benzerlik skoru, doğrulanamayan veya eşiğin altındaki parçayı yeniden güvenli yapmaz.
:::

::: tahmin Güven eşiğini tahmin et
Üç çıktı satırını yaz:

```python
sira = {"yuksek": 0, "orta": 1, "dusuk": 2}
for guven in ["yuksek", "orta", "dusuk"]:
    print(sira[guven] <= sira["orta"])
```

???

```cikti
True
True
False
```

Eşik kapsamı ile skor sıralaması iki ayrı karardır; seçimden önce provenance ve güven denetimi uygulanır.
:::

::: gorev 1 · RAG kaynak defterini doğrula
`kaynak_defteri_dogrula(kaynaklar)` işlevini yaz. Kaynaklar liste; her kayıt tam olarak `kaynak_id`, `tur`, `surum`, `guven`, `imzali`, `aktif` alanlarını taşısın. Kaynak kimliği 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren benzersiz stringdir.

Tür `kurumsal`, `acik`, `kullanici`; güven `yuksek`, `orta`, `dusuk` olmalıdır. Sürüm `MAJOR.MINOR.PATCH` biçiminde, her bileşeni başında gereksiz sıfır olmayan ASCII rakamlardan oluşan stringdir. `imzali` ve `aktif` gerçek bool olmalıdır. Geçersiz veride `ValueError` yükselt.

Kayıtları `kaynak_id` değerine göre sıralanmış yeni sözlükler olarak döndür. Boş defterde boş liste döndür ve girdiyi değiştirme.

```starter
def kaynak_defteri_dogrula(kaynaklar):
    return []
```

```test
import copy
K = [
    {"kaynak_id": "acik-1", "tur": "acik", "surum": "0.10.0", "guven": "dusuk", "imzali": False, "aktif": True},
    {"kaynak_id": "kurum-1", "tur": "kurumsal", "surum": "1.2.3", "guven": "yuksek", "imzali": True, "aktif": True},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != K or K != once or fn(list(reversed(K))) != K or fn([]) != []:
            return False
        sonuc = fn(K)
        if sonuc[0] is K[0] or fn([dict(K[0], kaynak_id="a" * 64)])[0]["kaynak_id"] != "a" * 64:
            return False
        for surum in ["0.0.0", "0.1.1", "10.20.30"]:
            if fn([dict(K[0], surum=surum)])[0]["surum"] != surum:
                return False
        for kaynaklar in [
            None, {}, [None], [dict(K[0], ek=1)], [dict(K[0], kaynak_id="")], [dict(K[0], kaynak_id="a b")],
            [dict(K[0], kaynak_id="a" * 65)], [K[0], K[0]], [dict(K[0], tur="diger")], [dict(K[0], guven="bilinmiyor")],
            [dict(K[0], surum="1.2")], [dict(K[0], surum="01.2.3")], [dict(K[0], surum="1.02.3")],
            [dict(K[0], surum="1.2.03")], [dict(K[0], surum="1.2.-3")], [dict(K[0], imzali=1)], [dict(K[0], aktif=0)],
        ]:
            try:
                fn(kaynaklar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kaynak_defteri_dogrula), "kaynak kimliği, tür, sürüm, güven ve durum korunmalı")
def m_imza(kaynaklar):
    return kaynak_defteri_dogrula([dict(x, imzali=False) for x in kaynaklar])
def m_surum(kaynaklar):
    return kaynak_defteri_dogrula([dict(x, surum="9.9.9") for x in kaynaklar])
def m_guven(kaynaklar):
    return kaynak_defteri_dogrula([dict(x, guven="dusuk") for x in kaynaklar])
for ad, mutant in [("imzayı silen", m_imza), ("sürümü değiştiren", m_surum), ("güveni düşüren", m_guven)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kaynak_defteri_dogrula(kaynaklar):
    import re
    if not isinstance(kaynaklar, list):
        raise ValueError("kaynaklar liste olmalı")
    kimlikler = set()
    defter = []
    for kaynak in kaynaklar:
        if not isinstance(kaynak, dict):
            raise ValueError("kaynak sözlük olmalı")
        if set(kaynak) != {"kaynak_id", "tur", "surum", "guven", "imzali", "aktif"}:
            raise ValueError("kaynak şeması geçersiz")
        kimlik = kaynak["kaynak_id"]
        if not isinstance(kimlik, str):
            raise ValueError("kaynak kimliği metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kaynak kimliği geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kaynak kimliği yinelenemez")
        kimlikler.add(kimlik)
        if kaynak["tur"] not in ("kurumsal", "acik", "kullanici"):
            raise ValueError("kaynak türü geçersiz")
        if not isinstance(kaynak["surum"], str):
            raise ValueError("sürüm metin olmalı")
        if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", kaynak["surum"]):
            raise ValueError("sürüm biçimi geçersiz")
        if kaynak["guven"] not in ("yuksek", "orta", "dusuk"):
            raise ValueError("güven düzeyi geçersiz")
        if type(kaynak["imzali"]) is not bool:
            raise ValueError("imza durumu bool olmalı")
        if type(kaynak["aktif"]) is not bool:
            raise ValueError("aktif durumu bool olmalı")
        defter.append(dict(kaynak))
    return sorted(defter, key=lambda x: x["kaynak_id"])
```

```hint
Her kaydı alan alan doğrula ve kimlik kümesiyle tekiliği koru. Sürümde her sayısal bileşen için ayrı desen kullan; dönüşte kayıtları kopyala.
```
:::

::: anlat Parça ile kaynak sürümü birebir eşleşir
Getirilen parçanın kaynak kimliği defterde yoksa `kaynak`, sürümü farklıysa `surum`, kaynak imzasızsa `imza`, kaynak pasifse `durum` nedeni eklenir. Kaynak yoksa sürüm karşılaştırması yapılmaz ve güven `bilinmiyor` olur. Bütün nedenler yoksa parça doğrulanabilirdir.

`metin_sha256` alanı içerik bütünlüğünün bağlantı noktasıdır. Bu ders özeti yeniden hesaplamaz; 64 küçük harfli hexadecimal karakterden oluşan kayıt biçimini doğrular.
:::

::: gorev 2 · RAG parçalarına provenance üret
`provenance_uret(parcalalar, kaynaklar)` işlevini yaz. Kaynak defteri ilk görevdeki bütün kuralları sağlasın. Parçalar liste; her kayıt tam olarak `id`, `kaynak_id`, `belge_id`, `surum`, `metin_sha256`, `skor` alanlarını taşısın. Parça ve belge kimlikleri ilk görevdeki desene uysun; parça kimliği benzersiz olsun. Kaynak kimliği ve sürüm stringdir. Özet 64 küçük harfli hexadecimal karakterdir. Skor bool olmayan, sonlu ve 0–1 arası int/float olmalıdır. Geçersiz veride `ValueError` yükselt.

Yukarıdaki sırayla `kaynak`, `surum`, `imza`, `durum` nedenlerini topla. Her kayıt için `{"id":ID,"kaynak_id":KAYNAK,"guven":GUVEN,"dogrulanabilir":not nedenler,"skor":SKOR,"nedenler":[...]}` döndür. Kimliğe göre sırala, boş parçada boş liste döndür ve girdileri değiştirme.

```starter
def provenance_uret(parcalalar, kaynaklar):
    return []
```

```test
import copy
K = [
    {"kaynak_id": "kurum-1", "tur": "kurumsal", "surum": "1.2.3", "guven": "yuksek", "imzali": True, "aktif": True},
    {"kaynak_id": "pasif-1", "tur": "acik", "surum": "2.0.0", "guven": "orta", "imzali": False, "aktif": False},
]
P = [
    {"id": "p-1", "kaynak_id": "kurum-1", "belge_id": "b-1", "surum": "1.2.3", "metin_sha256": "a" * 64, "skor": 0.9},
    {"id": "p-2", "kaynak_id": "kurum-1", "belge_id": "b-2", "surum": "1.2.4", "metin_sha256": "b" * 64, "skor": 0.8},
    {"id": "p-3", "kaynak_id": "yok-1", "belge_id": "b-3", "surum": "1.0.0", "metin_sha256": "c" * 64, "skor": 0.7},
    {"id": "p-4", "kaynak_id": "pasif-1", "belge_id": "b-4", "surum": "2.0.0", "metin_sha256": "d" * 64, "skor": 0.6},
]
BEKLENEN = [
    {"id": "p-1", "kaynak_id": "kurum-1", "guven": "yuksek", "dogrulanabilir": True, "skor": 0.9, "nedenler": []},
    {"id": "p-2", "kaynak_id": "kurum-1", "guven": "yuksek", "dogrulanabilir": False, "skor": 0.8, "nedenler": ["surum"]},
    {"id": "p-3", "kaynak_id": "yok-1", "guven": "bilinmiyor", "dogrulanabilir": False, "skor": 0.7, "nedenler": ["kaynak"]},
    {"id": "p-4", "kaynak_id": "pasif-1", "guven": "orta", "dogrulanabilir": False, "skor": 0.6, "nedenler": ["imza", "durum"]},
]
def sozlesme(fn):
    try:
        ponce = copy.deepcopy(P)
        konce = copy.deepcopy(K)
        if fn(P, K) != BEKLENEN or P != ponce or K != konce or fn(list(reversed(P)), K) != BEKLENEN or fn([], K) != []:
            return False
        for skor in (0, 1):
            if fn([dict(P[0], skor=skor)], K)[0]["skor"] != skor:
                return False
        if fn([dict(P[0], kaynak_id="a" * 64, surum="0.1.1")], [dict(K[0], kaynak_id="a" * 64, surum="0.1.1")])[0]["dogrulanabilir"] is not True:
            return False
        for parcalar, kaynaklar in [
            (None, K), ({}, K), ([None], K), (P, None), (P, [dict(K[0], imzali=1)]),
            (P, [dict(K[0], kaynak_id=None)]), (P, [dict(K[0], kaynak_id="a" * 65)]),
            (P, [dict(K[0], surum=None)]), (P, [dict(K[0], surum="01.2.3")]),
            ([dict(P[0], ek=1)], K), ([dict(P[0], id="")], K), ([dict(P[0], id="a b")], K),
            ([dict(P[0], id="a" * 65)], K), ([P[0], P[0]], K), ([dict(P[0], belge_id="")], K),
            ([dict(P[0], kaynak_id=None)], K), ([dict(P[0], surum=1)], K),
            ([dict(P[0], metin_sha256="a" * 63)], K), ([dict(P[0], metin_sha256="A" * 64)], K),
            ([dict(P[0], metin_sha256="g" * 64)], K), ([dict(P[0], skor=True)], K),
            ([dict(P[0], skor=-0.1)], K), ([dict(P[0], skor=1.1)], K),
            ([dict(P[0], skor=float("nan"))], K), ([dict(P[0], skor=float("inf"))], K),
        ]:
            try:
                fn(parcalar, kaynaklar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(provenance_uret), "kaynak, sürüm, imza, durum ve skor doğrulaması korunmalı")
def m_kaynak(parcalalar, kaynaklar):
    return provenance_uret([dict(x, kaynak_id="kurum-1", surum="1.2.3") for x in parcalalar], kaynaklar)
def m_surum(parcalalar, kaynaklar):
    return provenance_uret([dict(x, surum="1.2.3") for x in parcalalar], kaynaklar)
def m_durum(parcalalar, kaynaklar):
    return provenance_uret(parcalalar, [dict(x, imzali=True, aktif=True) for x in kaynaklar])
for ad, mutant in [("kaynağı zorlayan", m_kaynak), ("sürümü zorlayan", m_surum), ("durumu zorlayan", m_durum)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def provenance_uret(parcalalar, kaynaklar):
    import math
    import re
    if not isinstance(kaynaklar, list):
        raise ValueError("kaynaklar liste olmalı")
    defter = {}
    for kaynak in kaynaklar:
        if not isinstance(kaynak, dict):
            raise ValueError("kaynak sözlük olmalı")
        if set(kaynak) != {"kaynak_id", "tur", "surum", "guven", "imzali", "aktif"}:
            raise ValueError("kaynak şeması geçersiz")
        kimlik = kaynak["kaynak_id"]
        if not isinstance(kimlik, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kaynak kimliği geçersiz")
        if kimlik in defter:
            raise ValueError("kaynak yinelenemez")
        if kaynak["tur"] not in ("kurumsal", "acik", "kullanici"):
            raise ValueError("kaynak türü geçersiz")
        if not isinstance(kaynak["surum"], str) or not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", kaynak["surum"]):
            raise ValueError("sürüm geçersiz")
        if kaynak["guven"] not in ("yuksek", "orta", "dusuk"):
            raise ValueError("güven geçersiz")
        if type(kaynak["imzali"]) is not bool or type(kaynak["aktif"]) is not bool:
            raise ValueError("kaynak durumları bool olmalı")
        defter[kimlik] = kaynak
    if not isinstance(parcalalar, list):
        raise ValueError("parçalar liste olmalı")
    kimlikler = set()
    rapor = []
    for parca in parcalalar:
        if not isinstance(parca, dict):
            raise ValueError("parça sözlük olmalı")
        if set(parca) != {"id", "kaynak_id", "belge_id", "surum", "metin_sha256", "skor"}:
            raise ValueError("parça şeması geçersiz")
        for alan in ("id", "belge_id"):
            if not isinstance(parca[alan], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", parca[alan]):
                raise ValueError(alan + " geçersiz")
        if parca["id"] in kimlikler:
            raise ValueError("parça kimliği yinelenemez")
        kimlikler.add(parca["id"])
        if not isinstance(parca["kaynak_id"], str) or not isinstance(parca["surum"], str):
            raise ValueError("kaynak ve sürüm metin olmalı")
        if not isinstance(parca["metin_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", parca["metin_sha256"]):
            raise ValueError("içerik özeti geçersiz")
        if type(parca["skor"]) not in (int, float) or not math.isfinite(parca["skor"]):
            raise ValueError("skor sonlu sayı olmalı")
        if parca["skor"] < 0 or parca["skor"] > 1:
            raise ValueError("skor aralık dışı")
        kaynak = defter.get(parca["kaynak_id"])
        nedenler = []
        if kaynak is None:
            nedenler.append("kaynak")
        else:
            if parca["surum"] != kaynak["surum"]:
                nedenler.append("surum")
            if not kaynak["imzali"]:
                nedenler.append("imza")
            if not kaynak["aktif"]:
                nedenler.append("durum")
        rapor.append({"id": parca["id"], "kaynak_id": parca["kaynak_id"], "guven": kaynak["guven"] if kaynak else "bilinmiyor", "dogrulanabilir": not nedenler, "skor": parca["skor"], "nedenler": nedenler})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Defteri kaynak kimliğiyle haritala. Kaynak yoksa yalnız `kaynak` nedeni üret; varsa sürüm, imza ve aktiflik denetimlerini bağımsız uygula.
```
:::

::: anlat Son seçim provenance ve güven eşiğini birlikte uygular
Seçim girdisi ikinci görevin raporudur. `dogrulanabilir` alanı neden listesiyle tutarlı olmalıdır; çelişkili kayıt güvenlik açısından biçim hatasıdır. Eşiği geçen doğrulanabilir parçalar skor bakımından azalan, eşit skorda kimliğe göre artan sıralanır.

Seçim sonucunda neden listesi taşınmaz. Kullanıcıya veya sonraki aşamaya yalnız parça kimliği, kaynak, güven ve skor verilir; doğrulanamayan kayıtlar hiçbir zaman yüksek skorla listeye girmez.
:::

::: gorev 3 · Doğrulanabilir parçaları güven eşiğiyle seç
`guvenli_rag_secimi(provenance, minimum_guven)` işlevini yaz. Minimum güven `yuksek`, `orta`, `dusuk` olmalıdır. Provenance liste; her kayıt tam olarak `id`, `kaynak_id`, `guven`, `dogrulanabilir`, `skor`, `nedenler` alanlarını taşısın. Kimlikler ilk görevdeki desene uysun ve benzersiz olsun; kaynak kimliği stringdir. Güven `yuksek`, `orta`, `dusuk`, `bilinmiyor`; doğrulanabilirlik gerçek bool; skor ikinci görevdeki aralıktadır. Nedenler `kaynak`, `surum`, `imza`, `durum` değerlerinden oluşan yinelenmeyen listedir ve `dogrulanabilir == (nedenler boş)` olmalıdır. Geçersiz veride `ValueError` yükselt.

Yalnız doğrulanabilir ve güven düzeyi eşiği karşılayan kayıtları seç. `yuksek` yalnız yükseği, `orta` yüksek ve ortayı, `dusuk` üç güven düzeyini kapsar; `bilinmiyor` hiçbir eşikte seçilmez. Skora göre azalan, eşit skorda kimliğe göre artan sırala.

Her seçim için `{"id":ID,"kaynak_id":KAYNAK,"guven":GUVEN,"skor":SKOR}` döndür. Boş girdide boş liste döndür ve girdiyi değiştirme.

```starter
def guvenli_rag_secimi(provenance, minimum_guven):
    return []
```

```test
import copy
P = [
    {"id": "y-1", "kaynak_id": "kurum", "guven": "yuksek", "dogrulanabilir": True, "skor": 0.7, "nedenler": []},
    {"id": "y-2", "kaynak_id": "kurum", "guven": "yuksek", "dogrulanabilir": True, "skor": 0.9, "nedenler": []},
    {"id": "o-1", "kaynak_id": "acik", "guven": "orta", "dogrulanabilir": True, "skor": 0.8, "nedenler": []},
    {"id": "d-1", "kaynak_id": "kullanici", "guven": "dusuk", "dogrulanabilir": True, "skor": 0.95, "nedenler": []},
    {"id": "b-1", "kaynak_id": "yok", "guven": "bilinmiyor", "dogrulanabilir": False, "skor": 1.0, "nedenler": ["kaynak"]},
]
def beklenen(esik):
    secilen = [x for x in P if x["dogrulanabilir"] and x["guven"] in ({"yuksek": ["yuksek"], "orta": ["yuksek", "orta"], "dusuk": ["yuksek", "orta", "dusuk"]}[esik])]
    return [{k: x[k] for k in ("id", "kaynak_id", "guven", "skor")} for x in sorted(secilen, key=lambda x: (-x["skor"], x["id"]))]
def sozlesme(fn):
    try:
        once = copy.deepcopy(P)
        for esik in ("yuksek", "orta", "dusuk"):
            if fn(P, esik) != beklenen(esik) or P != once:
                return False
        if fn([], "dusuk") != [] or fn([P[0], P[1]], "yuksek")[0]["id"] != "y-2":
            return False
        if fn([dict(P[4], nedenler=[], dogrulanabilir=True)], "dusuk") != []:
            return False
        if fn([dict(P[0], skor=0)], "yuksek")[0]["skor"] != 0:
            return False
        for provenance, esik in [
            (None, "dusuk"), ({}, "dusuk"), ([None], "dusuk"), (P, "bilinmiyor"), (P, None),
            ([dict(P[0], ek=1)], "dusuk"), ([dict(P[0], id="")], "dusuk"), ([P[0], P[0]], "dusuk"),
            ([dict(P[0], id="a" * 65)], "dusuk"),
            ([dict(P[0], kaynak_id=None)], "dusuk"), ([dict(P[0], guven="diger")], "dusuk"),
            ([dict(P[0], dogrulanabilir=1)], "dusuk"), ([dict(P[0], skor=True)], "dusuk"),
            ([dict(P[0], skor=-0.1)], "dusuk"), ([dict(P[0], skor=1.1)], "dusuk"),
            ([dict(P[0], skor=float("nan"))], "dusuk"), ([dict(P[0], skor=float("inf"))], "dusuk"),
            ([dict(P[0], nedenler=None)], "dusuk"), ([dict(P[0], nedenler=["diger"])], "dusuk"),
            ([dict(P[0], nedenler=["kaynak", "kaynak"], dogrulanabilir=False)], "dusuk"),
            ([dict(P[0], nedenler=["kaynak"])], "dusuk"),
        ]:
            try:
                fn(provenance, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(guvenli_rag_secimi), "provenance tutarlılığı, güven eşiği ve sıralama korunmalı")
def m_dogrulama(provenance, esik):
    return guvenli_rag_secimi([dict(x, dogrulanabilir=True, nedenler=[]) for x in provenance], esik)
def m_guven(provenance, esik):
    return guvenli_rag_secimi([dict(x, guven="yuksek") for x in provenance], esik)
def m_skor(provenance, esik):
    return guvenli_rag_secimi([dict(x, skor=0) for x in provenance], esik)
for ad, mutant in [("doğrulamayı zorlayan", m_dogrulama), ("güveni yükselten", m_guven), ("skoru silen", m_skor)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def guvenli_rag_secimi(provenance, minimum_guven):
    import math
    import re
    sira = ("yuksek", "orta", "dusuk")
    if minimum_guven not in sira:
        raise ValueError("minimum güven geçersiz")
    if not isinstance(provenance, list):
        raise ValueError("provenance liste olmalı")
    kimlikler = set()
    secilen = []
    for kayit in provenance:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "kaynak_id", "guven", "dogrulanabilir", "skor", "nedenler"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["id"]):
            raise ValueError("kimlik geçersiz")
        if kayit["id"] in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kayit["id"])
        if not isinstance(kayit["kaynak_id"], str):
            raise ValueError("kaynak kimliği metin olmalı")
        if kayit["guven"] not in ("yuksek", "orta", "dusuk", "bilinmiyor"):
            raise ValueError("güven geçersiz")
        if type(kayit["dogrulanabilir"]) is not bool:
            raise ValueError("doğrulanabilirlik bool olmalı")
        if type(kayit["skor"]) not in (int, float) or not math.isfinite(kayit["skor"]):
            raise ValueError("skor sonlu sayı olmalı")
        if kayit["skor"] < 0 or kayit["skor"] > 1:
            raise ValueError("skor aralık dışı")
        if not isinstance(kayit["nedenler"], list):
            raise ValueError("nedenler liste olmalı")
        if len(set(kayit["nedenler"])) != len(kayit["nedenler"]):
            raise ValueError("nedenler yinelenemez")
        if any(neden not in ("kaynak", "surum", "imza", "durum") for neden in kayit["nedenler"]):
            raise ValueError("neden geçersiz")
        if kayit["dogrulanabilir"] != (not kayit["nedenler"]):
            raise ValueError("doğrulanabilirlik nedenlerle tutarsız")
        if kayit["dogrulanabilir"] and kayit["guven"] in sira and sira.index(kayit["guven"]) <= sira.index(minimum_guven):
            secilen.append({"id": kayit["id"], "kaynak_id": kayit["kaynak_id"], "guven": kayit["guven"], "skor": kayit["skor"]})
    return sorted(secilen, key=lambda x: (-x["skor"], x["id"]))
```

```hint
Önce raporun iç tutarlılığını doğrula. Güvenleri sayısal sıraya çevir; seçimi yaptıktan sonra `(-skor, id)` anahtarıyla sırala.
```
:::

::: anlat Alakalılık sıralaması güven vermez; seçim gerçek skorlarla sınanır
RAG provenance'ının değeri ancak **gerçek** retrieval skorları üzerinde görülür. Son görevde senin `guvenli_rag_secimi` işlevin, gerçek gömme modelinin (all-minilm:22m) bir sorgu ile aday parçalar arasında ürettiği kosinüs benzerliklerini kullanan provenance kayıtlarını seçer. Parçalardan biri sorguya alakalıdır ama tampered bir kaynaktan gelir (sürüm uyuşmazlığı) ve içinde enjeksiyon talimatı taşır.

Deney şunu gösterir: tampered parça, seçilen başka bir parçadan **daha yüksek gerçek embedding skoruna** sahip olsa bile, doğrulanabilir olmadığı için seçime girmez. Yani en alakalı içerik otomatik olarak güvenilir sayılmaz; provenance ve güven eşiği, poison'lu içeriği yüksek skora rağmen bağlam dışında tutar.
:::

::: gorev Gerçek deney · Gerçek skorlarla provenance seçimi
`guvenli_rag_secimi(provenance, minimum_guven)` işlevini yaz — kuralları ve çıktısı 3. görevdekiyle **aynıdır**. Deney gerçek gömme modeliyle skorları üretir, provenance'ı kaynak defterine göre kurar ve senin seçimin yalnız doğrulanabilir ve güven eşiğini karşılayan parçaları alır; tampered parça yüksek skorlu olsa bile elenir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def guvenli_rag_secimi(provenance, minimum_guven):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_16 as deney
    deney.goster(guvenli_rag_secimi)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "referans_provenance", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("guvenli_rag_secimi")
from sandbox import ai_gercek_ai_savunma_16 as D
P = [
    {"id": "y-1", "kaynak_id": "kurum", "guven": "yuksek", "dogrulanabilir": True, "skor": 0.7, "nedenler": []},
    {"id": "o-1", "kaynak_id": "acik", "guven": "orta", "dogrulanabilir": True, "skor": 0.5, "nedenler": []},
    {"id": "z-1", "kaynak_id": "kurum", "guven": "yuksek", "dogrulanabilir": False, "skor": 0.95, "nedenler": ["surum"]},
]
BEKLENEN = [
    {"id": "y-1", "kaynak_id": "kurum", "guven": "yuksek", "skor": 0.7},
    {"id": "o-1", "kaynak_id": "acik", "guven": "orta", "skor": 0.5},
]
def sozlesme(f):
    try:
        if f(P, "orta") != BEKLENEN or f([], "orta") != []:
            return False
        if f(P, "yuksek") != [{"id": "y-1", "kaynak_id": "kurum", "guven": "yuksek", "skor": 0.7}]:
            return False
        if f(P, "dusuk") != BEKLENEN:
            return False
        try:
            f(P, "gecersiz")
            return False
        except ValueError:
            pass
        for bozuk in (None, [None], [dict(P[0], ek=1)], [dict(P[0], dogrulanabilir=False)], [dict(P[0], nedenler=["bilinmeyen"])]):
            try:
                f(bozuk, "orta")
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "doğrulanabilirlik, güven eşiği, tutarlılık ve sıralama korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(not r["zehirli_secildi"] and r["zehirli_dogrulanabilir"] is False,
            "tampered parça doğrulanamadı ve seçime girmedi")
    kontrol(r["zehirli_daha_alakali_secilenden"],
            "tampered parça seçilen bir parçadan daha yüksek gerçek skora sahipti ama yine elendi")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-rag", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-16",
                                       "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({(r['ortam'].get('gomme') or {}).get('model')}): gerçek skorlar {oz['skorlar']}; seçilen {oz['secilen']}. "
             f"Tampered parça nedenler {oz['zehirli_nedenler']} ile seçilmedi; seçilen bir parçadan daha alakalı olsa bile elendi "
             f"({oz['zehirli_daha_alakali']}). Alakalılık sıralaması güven vermez; provenance karar verir.")
```

```solution
import ai_lab

def guvenli_rag_secimi(provenance, minimum_guven):
    import math
    import re
    sira = ("yuksek", "orta", "dusuk")
    if minimum_guven not in sira:
        raise ValueError("minimum güven geçersiz")
    if not isinstance(provenance, list):
        raise ValueError("provenance liste olmalı")
    kimlikler = set()
    secilen = []
    for kayit in provenance:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "kaynak_id", "guven", "dogrulanabilir", "skor", "nedenler"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["id"]):
            raise ValueError("kimlik geçersiz")
        if kayit["id"] in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kayit["id"])
        if not isinstance(kayit["kaynak_id"], str):
            raise ValueError("kaynak kimliği metin olmalı")
        if kayit["guven"] not in ("yuksek", "orta", "dusuk", "bilinmiyor"):
            raise ValueError("güven geçersiz")
        if type(kayit["dogrulanabilir"]) is not bool:
            raise ValueError("doğrulanabilirlik bool olmalı")
        if type(kayit["skor"]) not in (int, float) or not math.isfinite(kayit["skor"]):
            raise ValueError("skor sonlu sayı olmalı")
        if kayit["skor"] < 0 or kayit["skor"] > 1:
            raise ValueError("skor aralık dışı")
        if not isinstance(kayit["nedenler"], list):
            raise ValueError("nedenler liste olmalı")
        if len(set(kayit["nedenler"])) != len(kayit["nedenler"]):
            raise ValueError("nedenler yinelenemez")
        if any(neden not in ("kaynak", "surum", "imza", "durum") for neden in kayit["nedenler"]):
            raise ValueError("neden geçersiz")
        if kayit["dogrulanabilir"] != (not kayit["nedenler"]):
            raise ValueError("doğrulanabilirlik nedenlerle tutarsız")
        if kayit["dogrulanabilir"] and kayit["guven"] in sira and sira.index(kayit["guven"]) <= sira.index(minimum_guven):
            secilen.append({"id": kayit["id"], "kaynak_id": kayit["kaynak_id"], "guven": kayit["guven"], "skor": kayit["skor"]})
    return sorted(secilen, key=lambda x: (-x["skor"], x["id"]))

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_16 as deney
    deney.goster(guvenli_rag_secimi)
```

```hint
Bu işlev 3. görevdeki `guvenli_rag_secimi` ile birebir aynıdır; tek fark, skorların gerçek gömme modelinden gelmesidir. Raporun iç tutarlılığını doğrula; seçimi `(-skor, id)` anahtarıyla sırala.
```
:::
