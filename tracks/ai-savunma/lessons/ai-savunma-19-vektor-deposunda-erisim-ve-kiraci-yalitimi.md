---
id: ai-savunma-19
title: Vektör Deposunda Erişim ve Kiracı Yalıtımı
summary: Vektör getirme politikasını doğrula, kiracı filtresi ve sonuç sınırlarını zorunlu kıl, çapraz kiracı kayıtlarını bağlam dışında tut.
timeout: 45
---

::: anlat Benzerlik araması yetki kontrolünün yerine geçmez
Qdrant gibi bir vektör deposu en yakın kayıtları bulabilir; ancak yüksek benzerlik skoru, kaydı görmeye yetkili olunduğunu göstermez. Sorgu kimliği doğrulanır, kiracı filtresi zorunlu tutulur ve getirme sonrasında da kiracı eşleşmesi yeniden denetlenir.

Bu derste Qdrant, FastAPI, ağ veya model kullanılmaz. Sorgular ve vektör deposu kayıtları deterministik fixture olarak verilir. Amaç, erişim politikasının gerçek servise bağlanmadan önce fail-closed biçimde sınanmasıdır.
:::

::: anlat Kiracı kimlikleri ve skorlar katı biçimde doğrulanır
Kiracı ve kayıt kimlikleri ASCII harf/rakamla başlar; yalnız ASCII harf, rakam, alt çizgi ve tire içerir. Skor bool olmayan, sonlu ve 0–1 aralığında bir sayıdır. Alt skor eşiğine eşit kayıt kabul edilir.

`top_k` pozitif bir tam sayıdır. Politika üst sınırını aşan sorgu kırpılmaz; reddedilir. Böylece istemci geniş bir sonuç kümesi isteyerek veri maruziyetini artıramaz.
:::

::: tahmin Kiracı ve skor sıralamasını tahmin et
Üç çıktı satırını yaz:

```python
sorgu = {"kiraci": "a", "filtre_kiraci": "a", "top_k": 2}
print(sorgu["kiraci"] == sorgu["filtre_kiraci"])
kayitlar = [{"id": "b-1", "skor": 0.8}, {"id": "a-1", "skor": 0.8}]
print([x["id"] for x in sorted(kayitlar, key=lambda x: (-x["skor"], x["id"]))])
print(0.8 >= 0.8)
```

???

```cikti
True
['a-1', 'b-1']
True
```

Skor eşitliğinde kimlik sıralaması deterministik çıktı sağlar. Kiracı eşitliği ise ayrı bir yetki koşuludur.
:::

::: gorev 1 · Vektör erişim politikasını doğrula
`vektor_politikasi_dogrula(politika)` işlevini yaz. Politika tam olarak `izinli_kiracilar`, `min_skor`, `max_top_k`, `filtre_zorunlu`, `capraz_kiraci` alanlarını taşısın. İzinli kiracılar boş olmayan, yinelenmeyen listedir; her kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir.

Skor eşiği bool olmayan, sonlu ve 0–1 aralığında int veya float; sonuç sınırı bool olmayan 1–20 arası int olmalıdır. `filtre_zorunlu` gerçek `True`, `capraz_kiraci` gerçek `False` olmalıdır. Geçersiz veride `ValueError` yükselt.

Politikayı yeni listeyle döndür; girdiyi değiştirme.

```starter
def vektor_politikasi_dogrula(politika):
    return {}
```

```test
import copy
P = {"izinli_kiracilar": ["a", "b"], "min_skor": 0.8, "max_top_k": 5, "filtre_zorunlu": True, "capraz_kiraci": False}
def sozlesme(fn):
    try:
        once = copy.deepcopy(P)
        sonuc = fn(P)
        if sonuc != P or P != once or sonuc is P or sonuc["izinli_kiracilar"] is P["izinli_kiracilar"]:
            return False
        for alan, deger in [("min_skor", 0), ("min_skor", 1), ("max_top_k", 1), ("max_top_k", 20)]:
            if fn(dict(P, **{alan: deger}))[alan] != deger:
                return False
        if fn(dict(P, izinli_kiracilar=["a" * 64]))["izinli_kiracilar"] != ["a" * 64]:
            return False
        for politika in [
            None, [], dict(P, ek=1), dict(P, izinli_kiracilar=[]), dict(P, izinli_kiracilar=None),
            dict(P, izinli_kiracilar=["a", "a"]), dict(P, izinli_kiracilar=[""]),
            dict(P, izinli_kiracilar=["a b"]), dict(P, izinli_kiracilar=["a" * 65]),
            dict(P, min_skor=-0.01), dict(P, min_skor=1.01), dict(P, min_skor=True),
            dict(P, min_skor=float("nan")), dict(P, min_skor=float("inf")),
            dict(P, max_top_k=0), dict(P, max_top_k=21), dict(P, max_top_k=False),
            dict(P, filtre_zorunlu=False), dict(P, filtre_zorunlu=1),
            dict(P, capraz_kiraci=True), dict(P, capraz_kiraci=0),
        ]:
            try:
                fn(politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(vektor_politikasi_dogrula), "kiracı, skor, sonuç ve filtre politikaları korunmalı")
def m_kiraci(politika):
    sonuc = vektor_politikasi_dogrula(politika)
    sonuc["izinli_kiracilar"].append("dis")
    return sonuc
def m_skor(politika):
    return vektor_politikasi_dogrula(dict(politika, min_skor=0.0))
def m_filtre(politika):
    sonuc = vektor_politikasi_dogrula(politika)
    sonuc["filtre_zorunlu"] = False
    return sonuc
for ad, mutant in [("kiracıyı açan", m_kiraci), ("skoru düşüren", m_skor), ("filtreyi kaldıran", m_filtre)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def vektor_politikasi_dogrula(politika):
    import math
    import re
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"izinli_kiracilar", "min_skor", "max_top_k", "filtre_zorunlu", "capraz_kiraci"}:
        raise ValueError("politika şeması geçersiz")
    kiracilar = politika["izinli_kiracilar"]
    if not isinstance(kiracilar, list):
        raise ValueError("kiracılar liste olmalı")
    if not kiracilar:
        raise ValueError("kiracı listesi boş olamaz")
    if len(set(kiracilar)) != len(kiracilar):
        raise ValueError("kiracılar yinelenemez")
    for kiraci in kiracilar:
        if not isinstance(kiraci, str):
            raise ValueError("kiracı kimliği string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kiraci):
            raise ValueError("kiracı kimliği geçersiz")
    skor = politika["min_skor"]
    if isinstance(skor, bool):
        raise ValueError("skor bool olamaz")
    if not isinstance(skor, (int, float)):
        raise ValueError("skor sayı olmalı")
    if not math.isfinite(skor):
        raise ValueError("skor sonlu olmalı")
    if skor < 0:
        raise ValueError("skor sıfırdan küçük olamaz")
    if skor > 1:
        raise ValueError("skor birden büyük olamaz")
    if type(politika["max_top_k"]) is not int:
        raise ValueError("sonuç sınırı int olmalı")
    if politika["max_top_k"] < 1:
        raise ValueError("sonuç sınırı pozitif olmalı")
    if politika["max_top_k"] > 20:
        raise ValueError("sonuç sınırı çok büyük")
    if politika["filtre_zorunlu"] is not True:
        raise ValueError("kiracı filtresi zorunlu")
    if politika["capraz_kiraci"] is not False:
        raise ValueError("çapraz kiracı erişimi kapalı olmalı")
    return {"izinli_kiracilar": list(kiracilar), "min_skor": skor, "max_top_k": politika["max_top_k"], "filtre_zorunlu": True, "capraz_kiraci": False}
```

```hint
Kiracı listesindeki her kimliği desenle doğrula. Sayısal sınırları ayrı kontrol et; iki güvenlik bayrağını `is True` ve `is False` ile sabitle.
```
:::

::: anlat Sorgu reddi bütün ihlalleri görünür kılar
Sorgunun kiracısı izinli değilse `kiraci`, filtre kiracısı sorgu kiracısından farklıysa `filtre`, sonuç sayısı politika sınırını aşıyorsa `top_k` nedeni üretilir. Nedenler bu sıradadır ve herhangi biri sorguyu reddeder.

Filtre alanının bulunması yeterli değildir; doğru kiracıya eşit olması gerekir. Sınır değerine eşit `top_k` kabul edilir.
:::

::: gorev 2 · Vektör sorgularını yetki açısından denetle
`vektor_sorgularini_denetle(sorgular, politika)` işlevini yaz. Politika ilk görevdeki bütün kuralları sağlasın. Sorgular liste; her kayıt tam olarak `id`, `kiraci`, `filtre_kiraci`, `top_k` alanlarını taşısın. Sorgu kimliği benzersizdir; bütün kimlikler ilk görevdeki desene uyar. `top_k` bool olmayan pozitif int olmalıdır. Geçersiz veride `ValueError` yükselt.

Yukarıdaki üç yetki nedenini sırayla uygula. Her kayıt için `{"id":ID,"karar":"reddet" if nedenler else "kabul","nedenler":[...]}` döndür. Kimliğe göre sırala, boş sorguda boş liste döndür ve girdileri değiştirme.

```starter
def vektor_sorgularini_denetle(sorgular, politika):
    return []
```

```test
import copy
P = {"izinli_kiracilar": ["a", "b"], "min_skor": 0.8, "max_top_k": 5, "filtre_zorunlu": True, "capraz_kiraci": False}
S = [
    {"id": "kabul-1", "kiraci": "a", "filtre_kiraci": "a", "top_k": 5},
    {"id": "ret-1", "kiraci": "dis", "filtre_kiraci": "baska", "top_k": 6},
    {"id": "filtre-1", "kiraci": "a", "filtre_kiraci": "b", "top_k": 1},
]
BEKLENEN = [
    {"id": "filtre-1", "karar": "reddet", "nedenler": ["filtre"]},
    {"id": "kabul-1", "karar": "kabul", "nedenler": []},
    {"id": "ret-1", "karar": "reddet", "nedenler": ["kiraci", "filtre", "top_k"]},
]
def sozlesme(fn):
    try:
        sonce = copy.deepcopy(S)
        ponce = copy.deepcopy(P)
        if fn(S, P) != BEKLENEN or S != sonce or P != ponce or fn(list(reversed(S)), P) != BEKLENEN or fn([], P) != []:
            return False
        if fn([dict(S[0], id="a" * 64)], P)[0]["id"] != "a" * 64:
            return False
        for alan, deger in [("min_skor", 0), ("min_skor", 1), ("max_top_k", 1), ("max_top_k", 20)]:
            if fn([], dict(P, **{alan: deger})) != []:
                return False
        for sorgular, politika in [
            (None, P), ({}, P), ([None], P), (S, None), (S, dict(P, filtre_zorunlu=False)),
            (S, dict(P, capraz_kiraci=True)), (S, dict(P, min_skor=float("nan"))), (S, dict(P, min_skor=2)),
            (S, dict(P, max_top_k=0)), (S, dict(P, max_top_k=21)), (S, dict(P, izinli_kiracilar=[])),
            (S, dict(P, izinli_kiracilar=["a" * 65])),
            ([dict(S[0], ek=1)], P), ([dict(S[0], id="")], P), ([dict(S[0], id="a b")], P),
            ([dict(S[0], id="a" * 65)], P), ([S[0], S[0]], P),
            ([dict(S[0], kiraci="")], P), ([dict(S[0], filtre_kiraci="a b")], P),
            ([dict(S[0], top_k=0)], P), ([dict(S[0], top_k=True)], P),
        ]:
            try:
                fn(sorgular, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(vektor_sorgularini_denetle), "kiracı, filtre ve top_k kararları korunmalı")
def m_kiraci(sorgular, politika):
    return vektor_sorgularini_denetle(sorgular, dict(politika, izinli_kiracilar=["a", "b", "dis"]))
def m_filtre(sorgular, politika):
    return vektor_sorgularini_denetle([dict(x, filtre_kiraci=x["kiraci"]) for x in sorgular], politika)
def m_topk(sorgular, politika):
    return vektor_sorgularini_denetle(sorgular, dict(politika, max_top_k=20))
for ad, mutant in [("kiracıyı açan", m_kiraci), ("filtreyi düzelten", m_filtre), ("sınırı büyüten", m_topk)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def vektor_sorgularini_denetle(sorgular, politika):
    import math
    import re
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"izinli_kiracilar", "min_skor", "max_top_k", "filtre_zorunlu", "capraz_kiraci"}:
        raise ValueError("politika şeması geçersiz")
    if not isinstance(politika["izinli_kiracilar"], list):
        raise ValueError("kiracılar liste olmalı")
    if not politika["izinli_kiracilar"]:
        raise ValueError("kiracı listesi boş olamaz")
    for kiraci in politika["izinli_kiracilar"]:
        if not isinstance(kiraci, str):
            raise ValueError("kiracı string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kiraci):
            raise ValueError("kiracı geçersiz")
    skor = politika["min_skor"]
    if isinstance(skor, bool):
        raise ValueError("skor bool olamaz")
    if not isinstance(skor, (int, float)):
        raise ValueError("skor sayı olmalı")
    if not math.isfinite(skor):
        raise ValueError("skor sonlu olmalı")
    if skor < 0:
        raise ValueError("skor aralık dışı")
    if skor > 1:
        raise ValueError("skor aralık dışı")
    if type(politika["max_top_k"]) is not int:
        raise ValueError("sonuç sınırı int olmalı")
    if politika["max_top_k"] < 1:
        raise ValueError("sonuç sınırı pozitif olmalı")
    if politika["max_top_k"] > 20:
        raise ValueError("sonuç sınırı çok büyük")
    if politika["filtre_zorunlu"] is not True:
        raise ValueError("filtre zorunlu")
    if politika["capraz_kiraci"] is not False:
        raise ValueError("çapraz kiracı kapalı olmalı")
    if not isinstance(sorgular, list):
        raise ValueError("sorgular liste olmalı")
    kimlikler = set()
    sonuc = []
    for sorgu in sorgular:
        if not isinstance(sorgu, dict):
            raise ValueError("sorgu sözlük olmalı")
        if set(sorgu) != {"id", "kiraci", "filtre_kiraci", "top_k"}:
            raise ValueError("sorgu şeması geçersiz")
        for alan in ("id", "kiraci", "filtre_kiraci"):
            if not isinstance(sorgu[alan], str):
                raise ValueError(alan + " string olmalı")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", sorgu[alan]):
                raise ValueError(alan + " geçersiz")
        if sorgu["id"] in kimlikler:
            raise ValueError("sorgu kimliği yinelenemez")
        kimlikler.add(sorgu["id"])
        if type(sorgu["top_k"]) is not int:
            raise ValueError("top_k int olmalı")
        if sorgu["top_k"] < 1:
            raise ValueError("top_k pozitif olmalı")
        nedenler = []
        if sorgu["kiraci"] not in politika["izinli_kiracilar"]:
            nedenler.append("kiraci")
        if sorgu["filtre_kiraci"] != sorgu["kiraci"]:
            nedenler.append("filtre")
        if sorgu["top_k"] > politika["max_top_k"]:
            nedenler.append("top_k")
        sonuc.append({"id": sorgu["id"], "karar": "reddet" if nedenler else "kabul", "nedenler": nedenler})
    return sorted(sonuc, key=lambda x: x["id"])
```

```hint
Üç yetki nedenini bağımsız üret. Filtreyi doğrudan sorgu kiracısıyla karşılaştır; `top_k` için yalnız politika üstünü ihlal say.
```
:::

::: anlat Getirme sonrasında kiracı yalıtımı yeniden uygulanır
Depodan dönen her kayıt yeniden filtrelenir. Yalnız sorgu kiracısına ait ve skoru politika eşiğine eşit veya üstünde olan kayıtlar kalır. Başka kiracının kaydı, skoru daha yüksek olsa bile sonuçta yer alamaz.

Sonuçlar skor azalan, eşitlikte kimlik artan sıralanır ve istenen `top_k` kadar kayıtla sınırlanır. Biçimi geçerli olduğu hâlde yetkisiz, yanlış filtreli veya aşırı geniş sorgu boş liste üretir.
:::

::: gorev 3 · Yalnız yetkili vektör kayıtlarını getir
`yetkili_vektorleri_getir(kayitlar, sorgu, politika)` işlevini yaz. Politika ilk görevdeki bütün kuralları, sorgu ikinci görevdeki biçim kurallarını sağlasın. Kayıtlar liste; her kayıt tam olarak `id`, `kiraci`, `skor`, `metin` alanlarını taşısın. Kayıt kimliği benzersizdir ve kimlik desenine uyar. Skor bool olmayan, sonlu ve 0–1 aralığındaki sayı; metin stringdir. Metin NUL ve LF/CR/TAB dışındaki kontrol karakterlerini içeremez. Geçersiz veride `ValueError` yükselt.

Sorgu kiracısı izinli değilse, filtre kiracıdan farklıysa veya `top_k` politika sınırını aşıyorsa boş liste döndür. Aksi hâlde yalnız aynı kiracıdaki ve skor eşiğini geçen kayıtları skor azalan, kimlik artan sırayla ilk `top_k` kadar döndür. Her sonuç `{"id":ID,"kiraci":KIRACI,"skor":SKOR,"metin":METIN}` olsun. Girdileri değiştirme.

```starter
def yetkili_vektorleri_getir(kayitlar, sorgu, politika):
    return []
```

```test
import copy
P = {"izinli_kiracilar": ["a", "b"], "min_skor": 0.8, "max_top_k": 5, "filtre_zorunlu": True, "capraz_kiraci": False}
Q = {"id": "q-1", "kiraci": "a", "filtre_kiraci": "a", "top_k": 3}
K = [
    {"id": "a-1", "kiraci": "a", "skor": 0.8, "metin": "A"},
    {"id": "b-1", "kiraci": "a", "skor": 0.95, "metin": "B"},
    {"id": "c-1", "kiraci": "b", "skor": 0.99, "metin": "C"},
    {"id": "d-1", "kiraci": "a", "skor": 0.79, "metin": "D"},
]
BEKLENEN = [
    {"id": "b-1", "kiraci": "a", "skor": 0.95, "metin": "B"},
    {"id": "a-1", "kiraci": "a", "skor": 0.8, "metin": "A"},
]
def sozlesme(fn):
    try:
        konce = copy.deepcopy(K)
        qonce = copy.deepcopy(Q)
        ponce = copy.deepcopy(P)
        if fn(K, Q, P) != BEKLENEN or K != konce or Q != qonce or P != ponce or fn(list(reversed(K)), Q, P) != BEKLENEN:
            return False
        if fn(K, dict(Q, top_k=1), P) != BEKLENEN[:1] or fn([], Q, P) != []:
            return False
        if fn(K, dict(Q, kiraci="b", filtre_kiraci="b"), P)[0]["id"] != "c-1":
            return False
        for sorgu in [dict(Q, kiraci="dis", filtre_kiraci="dis"), dict(Q, filtre_kiraci="b"), dict(Q, top_k=6)]:
            if fn(K, sorgu, P) != []:
                return False
        if fn([dict(K[0], id="a" * 64)], Q, P)[0]["id"] != "a" * 64:
            return False
        if fn([dict(K[0], skor=0)], dict(Q, top_k=1), dict(P, min_skor=0))[0]["skor"] != 0:
            return False
        if fn([dict(K[0], skor=1)], Q, P)[0]["skor"] != 1:
            return False
        if fn([dict(K[0], metin="A B")], Q, P)[0]["metin"] != "A B":
            return False
        if fn(K, dict(Q, top_k=5), P) != BEKLENEN or fn(K, Q, dict(P, max_top_k=3)) != BEKLENEN:
            return False
        for alan, deger in [("min_skor", 0), ("min_skor", 1), ("max_top_k", 1), ("max_top_k", 20)]:
            if fn([], Q, dict(P, **{alan: deger})) != []:
                return False
        for kayitlar, sorgu, politika in [
            (None, Q, P), ({}, Q, P), ([None], Q, P), (K, None, P), (K, Q, None),
            (K, Q, dict(P, filtre_zorunlu=False)), (K, Q, dict(P, capraz_kiraci=True)),
            (K, Q, dict(P, min_skor=float("nan"))), (K, Q, dict(P, min_skor=2)),
            (K, Q, dict(P, max_top_k=0)), (K, Q, dict(P, max_top_k=21)),
            (K, Q, dict(P, izinli_kiracilar=[])), (K, Q, dict(P, izinli_kiracilar=["a" * 65])),
            (K, dict(Q, ek=1), P), (K, dict(Q, id="a b"), P), (K, dict(Q, id="a" * 65), P),
            (K, dict(Q, kiraci="a" * 65), P), (K, dict(Q, filtre_kiraci="a" * 65), P),
            (K, dict(Q, top_k=0), P), (K, dict(Q, top_k=True), P), (K, dict(Q, kiraci=""), P),
            ([dict(K[0], ek=1)], Q, P), ([dict(K[0], id="a" * 65)], Q, P), ([K[0], K[0]], Q, P),
            ([dict(K[0], kiraci="a b")], Q, P), ([dict(K[0], skor=-0.1)], Q, P),
            ([dict(K[0], skor=1.1)], Q, P), ([dict(K[0], skor=True)], Q, P),
            ([dict(K[0], skor=float("nan"))], Q, P), ([dict(K[0], skor=float("inf"))], Q, P),
            ([dict(K[0], metin=None)], Q, P), ([dict(K[0], metin="a\0b")], Q, P),
            ([dict(K[0], metin="a\x01b")], Q, P),
        ]:
            try:
                fn(kayitlar, sorgu, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yetkili_vektorleri_getir), "kiracı yalıtımı, skor, sıralama ve top_k korunmalı")
def m_capraz(kayitlar, sorgu, politika):
    return yetkili_vektorleri_getir([dict(x, kiraci=sorgu["kiraci"]) for x in kayitlar], sorgu, politika)
def m_skor(kayitlar, sorgu, politika):
    return yetkili_vektorleri_getir(kayitlar, sorgu, dict(politika, min_skor=0.0))
def m_filtre(kayitlar, sorgu, politika):
    return yetkili_vektorleri_getir(kayitlar, dict(sorgu, filtre_kiraci=sorgu["kiraci"]), politika)
for ad, mutant in [("kiracıyı değiştiren", m_capraz), ("skoru düşüren", m_skor), ("filtreyi düzelten", m_filtre)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yetkili_vektorleri_getir(kayitlar, sorgu, politika):
    import math
    import re
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"izinli_kiracilar", "min_skor", "max_top_k", "filtre_zorunlu", "capraz_kiraci"}:
        raise ValueError("politika şeması geçersiz")
    if not isinstance(politika["izinli_kiracilar"], list):
        raise ValueError("kiracılar liste olmalı")
    if not politika["izinli_kiracilar"]:
        raise ValueError("kiracı listesi boş olamaz")
    for kiraci in politika["izinli_kiracilar"]:
        if not isinstance(kiraci, str):
            raise ValueError("kiracı string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kiraci):
            raise ValueError("kiracı geçersiz")
    esik = politika["min_skor"]
    if isinstance(esik, bool):
        raise ValueError("skor bool olamaz")
    if not isinstance(esik, (int, float)):
        raise ValueError("skor sayı olmalı")
    if not math.isfinite(esik):
        raise ValueError("skor sonlu olmalı")
    if esik < 0:
        raise ValueError("skor aralık dışı")
    if esik > 1:
        raise ValueError("skor aralık dışı")
    if type(politika["max_top_k"]) is not int:
        raise ValueError("sonuç sınırı int olmalı")
    if politika["max_top_k"] < 1:
        raise ValueError("sonuç sınırı pozitif olmalı")
    if politika["max_top_k"] > 20:
        raise ValueError("sonuç sınırı çok büyük")
    if politika["filtre_zorunlu"] is not True:
        raise ValueError("filtre zorunlu")
    if politika["capraz_kiraci"] is not False:
        raise ValueError("çapraz kiracı kapalı olmalı")
    if not isinstance(sorgu, dict):
        raise ValueError("sorgu sözlük olmalı")
    if set(sorgu) != {"id", "kiraci", "filtre_kiraci", "top_k"}:
        raise ValueError("sorgu şeması geçersiz")
    for alan in ("id", "kiraci", "filtre_kiraci"):
        if not isinstance(sorgu[alan], str):
            raise ValueError(alan + " string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", sorgu[alan]):
            raise ValueError(alan + " geçersiz")
    if type(sorgu["top_k"]) is not int:
        raise ValueError("top_k int olmalı")
    if sorgu["top_k"] < 1:
        raise ValueError("top_k pozitif olmalı")
    if not isinstance(kayitlar, list):
        raise ValueError("kayitlar liste olmalı")
    kimlikler = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "kiraci", "skor", "metin"}:
            raise ValueError("kayıt şeması geçersiz")
        for alan in ("id", "kiraci"):
            if not isinstance(kayit[alan], str):
                raise ValueError(alan + " string olmalı")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit[alan]):
                raise ValueError(alan + " geçersiz")
        if kayit["id"] in kimlikler:
            raise ValueError("kayıt kimliği yinelenemez")
        kimlikler.add(kayit["id"])
        skor = kayit["skor"]
        if isinstance(skor, bool):
            raise ValueError("skor bool olamaz")
        if not isinstance(skor, (int, float)):
            raise ValueError("skor sayı olmalı")
        if not math.isfinite(skor):
            raise ValueError("skor sonlu olmalı")
        if skor < 0:
            raise ValueError("skor sıfırdan küçük olamaz")
        if skor > 1:
            raise ValueError("skor birden büyük olamaz")
        metin = kayit["metin"]
        if not isinstance(metin, str):
            raise ValueError("metin string olmalı")
        for karakter in metin:
            if ord(karakter) < 32 and karakter not in "\n\r\t":
                raise ValueError("metin kontrol karakteri içeremez")
    if sorgu["kiraci"] not in politika["izinli_kiracilar"]:
        return []
    if sorgu["filtre_kiraci"] != sorgu["kiraci"]:
        return []
    if sorgu["top_k"] > politika["max_top_k"]:
        return []
    adaylar = [x for x in kayitlar if x["kiraci"] == sorgu["kiraci"] and x["skor"] >= esik]
    adaylar.sort(key=lambda x: (-x["skor"], x["id"]))
    return [{"id": x["id"], "kiraci": x["kiraci"], "skor": x["skor"], "metin": x["metin"]} for x in adaylar[:sorgu["top_k"]]]
```

```hint
Önce bütün girdileri doğrula, sonra yetkisiz sorguyu boş sonuçla reddet. Aday listesinde hem kiracı eşitliğini hem skor eşiğini birlikte uygula.
```
:::

::: anlat Benzerlik sıralaması kiracı sınırını aşamaz
Çok kiracılı bir vektör deposunda asıl risk, bir kiracının sorgusunun başka bir kiracının en benzer kaydını getirmesidir. Son görevde senin `yetkili_vektorleri_getir` işlevin, gerçek gömme modelinin (all-minilm:22m) ürettiği kosinüs skorlarıyla sıralanan kayıtları kiracı yalıtımına göre filtreler. Kayıtlardan biri sorguya en benzer olandır ama başka bir kiracıya aittir.

Deney şunu gösterir: en yüksek **gerçek embedding skoruna** sahip kayıt sorgunun kiracısına ait değilse sonuca girmez; getirilen bütün kayıtlar aynı kiracıdandır. Yani benzerlik tek başına erişim vermez; kiracı sınırı skordan önce gelir ve çapraz kiracı sızıntısı olmaz.
:::

::: gorev Gerçek deney · Gerçek skorlarla kiracı yalıtımı
`yetkili_vektorleri_getir(kayitlar, sorgu, politika)` işlevini yaz — kuralları ve çıktısı 3. görevdekiyle **aynıdır**. Deney gerçek gömme modeliyle skorları üretir; senin işlevin yalnız aynı kiracının skor eşiğini geçen kayıtlarını getirir; çapraz kiracı kaydı en yüksek skorlu olsa bile dışarıda kalır.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def yetkili_vektorleri_getir(kayitlar, sorgu, politika):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_19 as deney
    deney.goster(yetkili_vektorleri_getir)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("yetkili_vektorleri_getir")
from sandbox import ai_gercek_ai_savunma_19 as D
P = {"izinli_kiracilar": ["a", "b"], "min_skor": 0.3, "max_top_k": 5, "filtre_zorunlu": True, "capraz_kiraci": False}
Q = {"id": "q-1", "kiraci": "a", "filtre_kiraci": "a", "top_k": 3}
K = [
    {"id": "a-1", "kiraci": "a", "skor": 0.8, "metin": "A"},
    {"id": "c-1", "kiraci": "b", "skor": 0.99, "metin": "C"},
    {"id": "d-1", "kiraci": "a", "skor": 0.2, "metin": "D"},
]
BEKLENEN = [{"id": "a-1", "kiraci": "a", "skor": 0.8, "metin": "A"}]
def sozlesme(f):
    try:
        if f(K, Q, P) != BEKLENEN or f([], Q, P) != []:
            return False
        if f(K, dict(Q, kiraci="dis", filtre_kiraci="dis"), P) != []:
            return False
        if f(K, dict(Q, filtre_kiraci="b"), P) != []:
            return False
        for bozuk in (None, [None], [dict(K[0], ek=1)], [dict(K[0], kiraci="a b")]):
            try:
                f(bozuk, Q, P)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "kiracı yalıtımı, skor eşiği, sıralama ve top_k korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(r["sonuc_kiracilar"] == ["a"] and not r["capraz_sizinti"],
            "getirilen gerçek kayıtların hepsi sorgu kiracısına ait, çapraz sızıntı yok")
    kontrol(r["en_yuksek_kiraci"] == "b" and r["en_yuksek_dislandi"],
            "en yüksek gerçek skorlu kayıt çapraz kiracıydı ve dışlandı")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-kiraci", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-19",
                                          "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({(r['ortam'].get('gomme') or {}).get('model')}): gerçek skorlar {oz['skorlar']}; getirilen {oz['sonuc_idler']} (kiracılar {oz['sonuc_kiracilar']}). "
             f"En yüksek skorlu kayıt {oz['en_yuksek_id']} kiracı '{oz['en_yuksek_kiraci']}' idi ve dışlandı ({oz['en_yuksek_dislandi']}); çapraz kiracı sızıntısı {oz['capraz_sizinti']}. "
             f"Benzerlik sıralaması kiracı sınırını aşamadı.")
```

```solution
import ai_lab

def yetkili_vektorleri_getir(kayitlar, sorgu, politika):
    import math
    import re
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"izinli_kiracilar", "min_skor", "max_top_k", "filtre_zorunlu", "capraz_kiraci"}:
        raise ValueError("politika şeması geçersiz")
    if not isinstance(politika["izinli_kiracilar"], list):
        raise ValueError("kiracılar liste olmalı")
    if not politika["izinli_kiracilar"]:
        raise ValueError("kiracı listesi boş olamaz")
    for kiraci in politika["izinli_kiracilar"]:
        if not isinstance(kiraci, str):
            raise ValueError("kiracı string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kiraci):
            raise ValueError("kiracı geçersiz")
    esik = politika["min_skor"]
    if isinstance(esik, bool):
        raise ValueError("skor bool olamaz")
    if not isinstance(esik, (int, float)):
        raise ValueError("skor sayı olmalı")
    if not math.isfinite(esik):
        raise ValueError("skor sonlu olmalı")
    if esik < 0:
        raise ValueError("skor aralık dışı")
    if esik > 1:
        raise ValueError("skor aralık dışı")
    if type(politika["max_top_k"]) is not int:
        raise ValueError("sonuç sınırı int olmalı")
    if politika["max_top_k"] < 1:
        raise ValueError("sonuç sınırı pozitif olmalı")
    if politika["max_top_k"] > 20:
        raise ValueError("sonuç sınırı çok büyük")
    if politika["filtre_zorunlu"] is not True:
        raise ValueError("filtre zorunlu")
    if politika["capraz_kiraci"] is not False:
        raise ValueError("çapraz kiracı kapalı olmalı")
    if not isinstance(sorgu, dict):
        raise ValueError("sorgu sözlük olmalı")
    if set(sorgu) != {"id", "kiraci", "filtre_kiraci", "top_k"}:
        raise ValueError("sorgu şeması geçersiz")
    for alan in ("id", "kiraci", "filtre_kiraci"):
        if not isinstance(sorgu[alan], str):
            raise ValueError(alan + " string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", sorgu[alan]):
            raise ValueError(alan + " geçersiz")
    if type(sorgu["top_k"]) is not int:
        raise ValueError("top_k int olmalı")
    if sorgu["top_k"] < 1:
        raise ValueError("top_k pozitif olmalı")
    if not isinstance(kayitlar, list):
        raise ValueError("kayitlar liste olmalı")
    kimlikler = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "kiraci", "skor", "metin"}:
            raise ValueError("kayıt şeması geçersiz")
        for alan in ("id", "kiraci"):
            if not isinstance(kayit[alan], str):
                raise ValueError(alan + " string olmalı")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit[alan]):
                raise ValueError(alan + " geçersiz")
        if kayit["id"] in kimlikler:
            raise ValueError("kayıt kimliği yinelenemez")
        kimlikler.add(kayit["id"])
        skor = kayit["skor"]
        if isinstance(skor, bool):
            raise ValueError("skor bool olamaz")
        if not isinstance(skor, (int, float)):
            raise ValueError("skor sayı olmalı")
        if not math.isfinite(skor):
            raise ValueError("skor sonlu olmalı")
        if skor < 0:
            raise ValueError("skor sıfırdan küçük olamaz")
        if skor > 1:
            raise ValueError("skor birden büyük olamaz")
        metin = kayit["metin"]
        if not isinstance(metin, str):
            raise ValueError("metin string olmalı")
        for karakter in metin:
            if ord(karakter) < 32 and karakter not in "\n\r\t":
                raise ValueError("metin kontrol karakteri içeremez")
    if sorgu["kiraci"] not in politika["izinli_kiracilar"]:
        return []
    if sorgu["filtre_kiraci"] != sorgu["kiraci"]:
        return []
    if sorgu["top_k"] > politika["max_top_k"]:
        return []
    adaylar = [x for x in kayitlar if x["kiraci"] == sorgu["kiraci"] and x["skor"] >= esik]
    adaylar.sort(key=lambda x: (-x["skor"], x["id"]))
    return [{"id": x["id"], "kiraci": x["kiraci"], "skor": x["skor"], "metin": x["metin"]} for x in adaylar[:sorgu["top_k"]]]

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_19 as deney
    deney.goster(yetkili_vektorleri_getir)
```

```hint
Bu işlev 3. görevdeki `yetkili_vektorleri_getir` ile birebir aynıdır; tek fark, skorların gerçek gömme modelinden gelmesidir. Yetkisiz sorguyu boş sonuçla reddet; adaylarda kiracı eşitliği ve skor eşiğini birlikte uygula.
```
:::
