---
id: ai-savunma-03
title: Katmanlı Savunma Referans Mimarisi
summary: Beş savunma katmanını doğrula, kontrol sonuçlarından fail-closed karar üret ve kontrol arızalarında yedekliliği ölç.
timeout: 45
---

::: anlat Tek bir guardrail bütün sistemi korumaz
Katmanlı savunmada girdi, model, çıktı, araç ve veri katmanları farklı hataları yakalar. Girdi şeması bozuk isteği durdurur; model katmanı sistem promptu ve model sürümünü sabitler; çıktı katmanı yapı ve veri sızıntısını denetler; araç katmanı yetkiyi; veri katmanı ise kiracı ve kaynak kapsamını korur.

Bu katmanlar birbirinin yedeği olmak zorunda değildir, fakat tek bir filtrenin hatası bütün sistemi savunmasız bırakmamalıdır. Kontrollerin bağımsız olması, aynı kontrol kimliğinin birden çok katmanda tekrar yazılması değil, her katmanın kendi sınanabilir kararının bulunmasıdır.

Bu dersteki FastAPI ve Ollama akışı sentetik olaylarla temsil edilir. Gerçek servis, model veya ağ gerekmez.
:::

::: tahmin Mimari sıra alfabetik sıra değildir
Üç çıktı satırını yaz:

```python
sira = ["girdi", "model", "cikti", "arac", "veri"]
print(sira.index("model"))
print(sorted(sira)[:2])
print(len({"girdi", "girdi", "veri"}))
```

???

```cikti
1
['arac', 'cikti']
2
```

Karar akışında tanımlı mimari sıra kullanılır; alfabetik sıralama yalnız belirli rapor alanlarında uygulanır.
:::

::: gorev 1 · Beş katmanlı mimariyi ve bağımsız kontrolleri doğrula
`savunma_mimarisini_dogrula(katmanlar)` işlevini yaz. Girdi, beş katmanın her birini tam bir kez içeren liste olmalıdır: `girdi`, `model`, `cikti`, `arac`, `veri`. Her kayıt tam olarak `id`, `kontroller` alanlarını taşısın. Kontroller boş olmayan, yinelenmeyen string listesidir ve yalnız şu katman kontrollerini içerebilir:

- `girdi`: `sema`, `boyut`, `icerik`
- `model`: `sistem_promptu`, `model_sabitleme`
- `cikti`: `cikti_semasi`, `dlp`
- `arac`: `yetki`, `onay`, `sandbox`
- `veri`: `kiraci`, `provenance`, `sorgu`

Geçersiz veride `ValueError` yükselt. Katmanları yukarıdaki mimari sırayla, kontrolleri alfabetik sırayla yeni listeler hâlinde döndür. Girdiyi değiştirme.

```starter
def savunma_mimarisini_dogrula(katmanlar):
    return []
```

```test
import copy
K = [
    {"id": "veri", "kontroller": ["provenance", "kiraci"]},
    {"id": "girdi", "kontroller": ["boyut", "sema"]},
    {"id": "arac", "kontroller": ["onay", "yetki"]},
    {"id": "model", "kontroller": ["model_sabitleme", "sistem_promptu"]},
    {"id": "cikti", "kontroller": ["dlp", "cikti_semasi"]},
]
BEKLENEN = [
    {"id": "girdi", "kontroller": ["boyut", "sema"]},
    {"id": "model", "kontroller": ["model_sabitleme", "sistem_promptu"]},
    {"id": "cikti", "kontroller": ["cikti_semasi", "dlp"]},
    {"id": "arac", "kontroller": ["onay", "yetki"]},
    {"id": "veri", "kontroller": ["kiraci", "provenance"]},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once or fn(list(reversed(K))) != BEKLENEN:
            return False
        for kayitlar in [
            None, {}, [], [None], K[:4], K + [K[0]],
            [dict(K[0], ek=1)] + K[1:], [dict(K[0], id="ag")] + K[1:],
            [dict(K[0], kontroller=[])] + K[1:],
            [dict(K[0], kontroller="kiraci")] + K[1:],
            [dict(K[0], kontroller=["kiraci", "kiraci"])] + K[1:],
            [dict(K[0], kontroller=["yetki"])] + K[1:],
            [dict(K[0], kontroller=[None])] + K[1:],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(savunma_mimarisini_dogrula), "beş katman, kontrol aidiyeti ve mimari sıra korunmalı")
def m_sira(katmanlar):
    return sorted(savunma_mimarisini_dogrula(katmanlar), key=lambda x: x["id"])
def m_kontrol(katmanlar):
    sonuc = savunma_mimarisini_dogrula(katmanlar)
    sonuc[0]["kontroller"] = []
    return sonuc
def m_aidiyet(katmanlar):
    degisen = copy.deepcopy(katmanlar)
    degisen[0]["kontroller"] = ["yetki"]
    return savunma_mimarisini_dogrula(degisen)
for ad, mutant in [("katmanları alfabetik sıralayan", m_sira), ("girdi kontrollerini silen", m_kontrol), ("kontrol aidiyetini bozan", m_aidiyet)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def savunma_mimarisini_dogrula(katmanlar):
    sira = ["girdi", "model", "cikti", "arac", "veri"]
    izinli = {
        "girdi": {"sema", "boyut", "icerik"},
        "model": {"sistem_promptu", "model_sabitleme"},
        "cikti": {"cikti_semasi", "dlp"},
        "arac": {"yetki", "onay", "sandbox"},
        "veri": {"kiraci", "provenance", "sorgu"},
    }
    if not isinstance(katmanlar, list):
        raise ValueError("katman listesi geçersiz")
    kayitlar = {}
    for katman in katmanlar:
        if not isinstance(katman, dict):
            raise ValueError("katman geçersiz")
        if set(katman) != {"id", "kontroller"}:
            raise ValueError("katman şeması geçersiz")
        kimlik = katman["id"]
        if kimlik not in izinli:
            raise ValueError("katman kimliği geçersiz")
        if kimlik in kayitlar:
            raise ValueError("katman yinelenemez")
        kontroller = katman["kontroller"]
        if not isinstance(kontroller, list):
            raise ValueError("kontrol listesi geçersiz")
        if not kontroller:
            raise ValueError("katman kontrolsüz olamaz")
        if len(set(kontroller)) != len(kontroller):
            raise ValueError("kontrol yinelenemez")
        for kontrol in kontroller:
            if not isinstance(kontrol, str):
                raise ValueError("kontrol kimliği geçersiz")
            if kontrol not in izinli[kimlik]:
                raise ValueError("kontrol bu katmana ait değil")
        kayitlar[kimlik] = sorted(kontroller)
    if set(kayitlar) != set(sira):
        raise ValueError("beş katman zorunlu")
    return [{"id": kimlik, "kontroller": kayitlar[kimlik]} for kimlik in sira]
```

```hint
Katman kimliğinden sıralı kontrol listesine bir sözlük kur. En son sözlüğün anahtarlarının beş zorunlu katmanla aynı küme olduğunu doğrula.
```
:::

::: anlat Hata ve eksik gözlem izin kararına dönüşmemeli
Bir kontrol `kaldi` veya `hata` durumundaysa istek reddedilir. `hata`, başarısız içerik anlamına gelmese de kontrolün çalıştığını kanıtlamaz; fail-closed yaklaşımında ikisi de erişimi durdurur. Kontrol sonucu eksikse ve başka hata yoksa karar `eksik` olur, yine `izin` olmaz.

Birden çok hata varsa raporlanan neden mimari sıradaki ilk başarısız veya hatalı kontroldür. Eksik kontroller de aynı sırayla `katman:kontrol` biçiminde listelenir. Böylece girdi sırası kararı değiştirmez.
:::

::: gorev 2 · Kontrol gözlemlerinden fail-closed istek kararı üret
`istek_karari_hesapla(mimari, olaylar)` işlevini yaz. `mimari`, ilk görevin normalize edilmiş çıktısıdır ve aynı kuralları sağlamalıdır. Her olay tam olarak `katman`, `kontrol`, `sonuc` alanlarını taşısın; katman-kontrol çifti mimaride bulunmalı ve olaylarda yinelenmemelidir. Sonuç yalnız `gecti`, `kaldi` veya `hata` olabilir. Geçersiz veride `ValueError` yükselt.

Dönüş:

```text
{"karar":"izin|reddet|eksik",
 "neden":{"katman":K,"kontrol":C,"sonuc":S}|None,
 "eksik":["katman:kontrol",...]}
```

Herhangi bir `kaldi` veya `hata` varsa `reddet`; yoksa eksik kontrol varsa `eksik`; bütün kontroller `gecti` ise `izin` döndür. Reddetmede `neden`, mimari sıradaki ilk hatalı/başarısız olaydır; diğer kararlarda None olur. Girdileri değiştirme.

```starter
def istek_karari_hesapla(mimari, olaylar):
    return {}
```

```test
import copy
M = [
    {"id": "girdi", "kontroller": ["boyut", "sema"]},
    {"id": "model", "kontroller": ["model_sabitleme"]},
    {"id": "cikti", "kontroller": ["cikti_semasi"]},
    {"id": "arac", "kontroller": ["onay", "yetki"]},
    {"id": "veri", "kontroller": ["kiraci"]},
]
O = [
    {"katman": "girdi", "kontrol": "boyut", "sonuc": "gecti"},
    {"katman": "girdi", "kontrol": "sema", "sonuc": "gecti"},
    {"katman": "model", "kontrol": "model_sabitleme", "sonuc": "gecti"},
    {"katman": "cikti", "kontrol": "cikti_semasi", "sonuc": "gecti"},
    {"katman": "arac", "kontrol": "onay", "sonuc": "gecti"},
    {"katman": "arac", "kontrol": "yetki", "sonuc": "gecti"},
    {"katman": "veri", "kontrol": "kiraci", "sonuc": "gecti"},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy((M, O))
        if fn(M, O) != {"karar": "izin", "neden": None, "eksik": []} or (M, O) != once:
            return False
        if fn(M, list(reversed(O)))["karar"] != "izin":
            return False
        if fn(M, O[:-1]) != {"karar": "eksik", "neden": None, "eksik": ["veri:kiraci"]}:
            return False
        bozuk = [dict(x, sonuc="hata") if x["kontrol"] == "sema" else x for x in O]
        sonuc = fn(M, bozuk)
        if sonuc["karar"] != "reddet" or sonuc["neden"] != {"katman": "girdi", "kontrol": "sema", "sonuc": "hata"}:
            return False
        cift = [dict(x, sonuc="kaldi") if x["kontrol"] in ("boyut", "yetki") else x for x in O[:-1]]
        sonuc = fn(M, cift)
        if sonuc["neden"]["kontrol"] != "boyut" or sonuc["eksik"] != ["veri:kiraci"]:
            return False
        for mimari, olaylar in [
            (None, []), (M, None), (M, [None]), (M, [dict(O[0], ek=1)]),
            (M, [dict(O[0], katman="ag")]), (M, [dict(O[0], kontrol="yetki")]),
            (M, [dict(O[0], sonuc="belirsiz")]), (M, [O[0], O[0]]),
            (M[:-1], []), ([dict(M[0], kontroller=[])]+M[1:], []),
            ([dict(M[0], kontroller=["yetki", "sema"])]+M[1:], []),
        ]:
            try:
                fn(mimari, olaylar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(istek_karari_hesapla), "hata ve eksik sonuçlar izin vermemeli; neden mimari sıradan seçilmeli")
def m_hata(mimari, olaylar):
    degisen = [dict(x, sonuc="gecti") if x["sonuc"] == "hata" else x for x in olaylar]
    return istek_karari_hesapla(mimari, degisen)
def m_eksik(mimari, olaylar):
    return istek_karari_hesapla(mimari, olaylar + [{"katman": "veri", "kontrol": "kiraci", "sonuc": "gecti"}])
def m_neden(mimari, olaylar):
    degisen = [dict(x, sonuc="kaldi") if x["kontrol"] in ("boyut", "yetki") else x for x in olaylar]
    return istek_karari_hesapla(mimari, degisen)
for ad, mutant in [("kontrol hatasında izin veren", m_hata), ("eksik gözlemi kapatan", m_eksik), ("ilk hatayı değiştiren", m_neden)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def istek_karari_hesapla(mimari, olaylar):
    sira = ["girdi", "model", "cikti", "arac", "veri"]
    izinli = {
        "girdi": {"sema", "boyut", "icerik"},
        "model": {"sistem_promptu", "model_sabitleme"},
        "cikti": {"cikti_semasi", "dlp"},
        "arac": {"yetki", "onay", "sandbox"},
        "veri": {"kiraci", "provenance", "sorgu"},
    }
    if not isinstance(mimari, list):
        raise ValueError("mimari geçersiz")
    if not isinstance(olaylar, list):
        raise ValueError("olay listesi geçersiz")
    if len(mimari) != len(sira):
        raise ValueError("beş katman zorunlu")
    kayitlar = {}
    for indeks, katman in enumerate(mimari):
        if not isinstance(katman, dict):
            raise ValueError("katman geçersiz")
        if set(katman) != {"id", "kontroller"}:
            raise ValueError("katman şeması geçersiz")
        if katman["id"] != sira[indeks]:
            raise ValueError("katman sırası geçersiz")
        kontroller = katman["kontroller"]
        if not isinstance(kontroller, list) or not kontroller:
            raise ValueError("kontrol listesi geçersiz")
        if kontroller != sorted(set(kontroller)):
            raise ValueError("kontroller normalize değil")
        for kontrol in kontroller:
            if kontrol not in izinli[katman["id"]]:
                raise ValueError("kontrol katmanı geçersiz")
        kayitlar[katman["id"]] = kontroller
    sonuclar = {}
    for olay in olaylar:
        if not isinstance(olay, dict):
            raise ValueError("olay geçersiz")
        if set(olay) != {"katman", "kontrol", "sonuc"}:
            raise ValueError("olay şeması geçersiz")
        anahtar = (olay["katman"], olay["kontrol"])
        if olay["katman"] not in kayitlar:
            raise ValueError("olay katmanı geçersiz")
        if olay["kontrol"] not in kayitlar[olay["katman"]]:
            raise ValueError("olay kontrolü geçersiz")
        if anahtar in sonuclar:
            raise ValueError("olay yinelenemez")
        if olay["sonuc"] not in ("gecti", "kaldi", "hata"):
            raise ValueError("olay sonucu geçersiz")
        sonuclar[anahtar] = olay["sonuc"]
    eksik = []
    neden = None
    for katman in sira:
        for kontrol in kayitlar[katman]:
            sonuc = sonuclar.get((katman, kontrol))
            if sonuc is None:
                eksik.append(katman + ":" + kontrol)
            if sonuc in ("kaldi", "hata") and neden is None:
                neden = {"katman": katman, "kontrol": kontrol, "sonuc": sonuc}
    if neden is not None:
        karar = "reddet"
    elif eksik:
        karar = "eksik"
    else:
        karar = "izin"
    return {"karar": karar, "neden": neden, "eksik": eksik}
```

```hint
Olayları `(katman, kontrol) → sonuç` sözlüğüne koy. Sonra yalnız mimari sırayla gez; eksikleri ve ilk olumsuz sonucu bu turda topla.
```
:::

::: anlat Yedeklilik kontrol arızasıyla sınanır
Bir katmandaki bütün kontroller aynı anda bozulursa o katman tek hata noktası hâline gelir. Yedeklilik analizi, senaryoda bozulan kontrolleri çıkarır ve etkilenen katmanlarda en az bir bağımsız kontrol kalıp kalmadığını ölçer. Bu analiz kalan kontrolün saldırıyı kesin yakalayacağını söylemez; yalnız mimaride çalışabilecek ayrı bir karar noktası bulunduğunu gösterir.

Senaryo kimlikleri sıralanır, bozulan kontrol listesi yinelenemez ve yalnız mimarideki kontrolleri içerebilir. Hiç kontrol bozulmayan senaryo yedeklidir ve tek nokta üretmez.
:::

::: gorev 3 · Kontrol arızası senaryolarında tek hata noktalarını bul
`katman_yedeklilik_raporu(mimari, senaryolar)` işlevini yaz. Mimari önceki kuralları sağlasın. Her senaryo tam olarak `id`, `bozulan` alanlarını taşısın. Kimlik baş/son boşluğu olmayan boş olmayan ve benzersiz string; `bozulan`, mimaride bulunan kontrol kimliklerinin yinelenmeyen listesi olmalıdır. Geçersiz veride `ValueError` yükselt.

Her senaryo için, en az bir kontrolü bozulan ve hiç sağlam kontrolü kalmayan katmanları `tek_noktalar` listesine mimari sırayla ekle. Etkilenen her katmanda en az bir kontrol sağlamsa veya hiç kontrol bozulmamışsa `yedekli` true olsun. Dönüş:

```text
{"senaryolar":[{"id":ID,"tek_noktalar":[KATMAN,...],"yedekli":BOOL},...],
 "tek_nokta_sayisi":N}
```

Senaryoları kimliğe göre sırala. `tek_nokta_sayisi`, tek nokta içeren senaryo sayısıdır. Girdileri değiştirme.

```starter
def katman_yedeklilik_raporu(mimari, senaryolar):
    return {}
```

```test
import copy
M = [
    {"id": "girdi", "kontroller": ["boyut", "sema"]},
    {"id": "model", "kontroller": ["model_sabitleme"]},
    {"id": "cikti", "kontroller": ["cikti_semasi"]},
    {"id": "arac", "kontroller": ["onay", "yetki"]},
    {"id": "veri", "kontroller": ["kiraci"]},
]
S = [
    {"id": "iki-katman", "bozulan": ["sema", "boyut", "yetki", "onay"]},
    {"id": "yedekli-girdi", "bozulan": ["sema"]},
    {"id": "bos", "bozulan": []},
]
BEKLENEN = {"senaryolar": [
    {"id": "bos", "tek_noktalar": [], "yedekli": True},
    {"id": "iki-katman", "tek_noktalar": ["girdi", "arac"], "yedekli": False},
    {"id": "yedekli-girdi", "tek_noktalar": [], "yedekli": True},
], "tek_nokta_sayisi": 1}
def sozlesme(fn):
    try:
        once = copy.deepcopy((M, S))
        if fn(M, S) != BEKLENEN or (M, S) != once or fn(M, list(reversed(S))) != BEKLENEN:
            return False
        if fn(M, []) != {"senaryolar": [], "tek_nokta_sayisi": 0}:
            return False
        if fn(M, [{"id": "arac", "bozulan": ["yetki", "onay"]}])["senaryolar"][0]["tek_noktalar"] != ["arac"]:
            return False
        for mimari, senaryolar in [
            (None, []), (M, None), (M, [None]), (M, [dict(S[0], ek=1)]),
            (M, [dict(S[0], id="")]), (M, [dict(S[0], id=" x")]),
            (M, [dict(S[0], id=None)]), (M, [dict(S[0], bozulan="sema")]),
            (M, [dict(S[0], bozulan=["yok"])]),
            (M, [dict(S[0], bozulan=["sema", "sema"])]),
            (M, [S[0], S[0]]), (M[:-1], []),
        ]:
            try:
                fn(mimari, senaryolar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(katman_yedeklilik_raporu), "yalnız bütün kontrolleri bozulan katmanlar tek nokta olmalı")
def m_yedek(mimari, senaryolar):
    degisen = [dict(s, bozulan=s["bozulan"][:1]) for s in senaryolar]
    return katman_yedeklilik_raporu(mimari, degisen)
def m_sira(mimari, senaryolar):
    sonuc = katman_yedeklilik_raporu(mimari, senaryolar)
    for s in sonuc["senaryolar"]:
        s["tek_noktalar"].sort()
    return sonuc
def m_sayac(mimari, senaryolar):
    sonuc = katman_yedeklilik_raporu(mimari, senaryolar)
    sonuc["tek_nokta_sayisi"] += 1
    return sonuc
for ad, mutant in [("bozuk kontrolleri görmezden gelen", m_yedek), ("katman sırasını bozan", m_sira), ("tek nokta sayacını artıran", m_sayac)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def katman_yedeklilik_raporu(mimari, senaryolar):
    sira = ["girdi", "model", "cikti", "arac", "veri"]
    izinli = {
        "girdi": {"sema", "boyut", "icerik"},
        "model": {"sistem_promptu", "model_sabitleme"},
        "cikti": {"cikti_semasi", "dlp"},
        "arac": {"yetki", "onay", "sandbox"},
        "veri": {"kiraci", "provenance", "sorgu"},
    }
    if not isinstance(mimari, list):
        raise ValueError("mimari geçersiz")
    if not isinstance(senaryolar, list):
        raise ValueError("senaryo listesi geçersiz")
    if len(mimari) != len(sira):
        raise ValueError("beş katman zorunlu")
    kayitlar = {}
    tum_kontroller = set()
    for indeks, katman in enumerate(mimari):
        if not isinstance(katman, dict):
            raise ValueError("katman geçersiz")
        if set(katman) != {"id", "kontroller"}:
            raise ValueError("katman şeması geçersiz")
        if katman["id"] != sira[indeks]:
            raise ValueError("katman sırası geçersiz")
        kontroller = katman["kontroller"]
        if not isinstance(kontroller, list):
            raise ValueError("kontrol listesi geçersiz")
        if not kontroller:
            raise ValueError("kontrol listesi boş olamaz")
        if kontroller != sorted(set(kontroller)):
            raise ValueError("kontroller normalize değil")
        for kontrol in kontroller:
            if kontrol not in izinli[katman["id"]]:
                raise ValueError("kontrol katmanı geçersiz")
        kayitlar[katman["id"]] = kontroller
        tum_kontroller.update(kontroller)
    rapor = []
    kimlikler = set()
    for senaryo in senaryolar:
        if not isinstance(senaryo, dict):
            raise ValueError("senaryo geçersiz")
        if set(senaryo) != {"id", "bozulan"}:
            raise ValueError("senaryo şeması geçersiz")
        kimlik = senaryo["id"]
        if not isinstance(kimlik, str):
            raise ValueError("senaryo kimliği geçersiz")
        if not kimlik:
            raise ValueError("senaryo kimliği boş olamaz")
        if kimlik != kimlik.strip():
            raise ValueError("senaryo kimliği boşluklu olamaz")
        if kimlik in kimlikler:
            raise ValueError("senaryo kimliği yinelenemez")
        bozulan = senaryo["bozulan"]
        if not isinstance(bozulan, list):
            raise ValueError("bozulan listesi geçersiz")
        if len(set(bozulan)) != len(bozulan):
            raise ValueError("bozulan kontrol yinelenemez")
        for kontrol in bozulan:
            if kontrol not in tum_kontroller:
                raise ValueError("bozulan kontrol geçersiz")
        kimlikler.add(kimlik)
        bozuk = set(bozulan)
        tek_noktalar = []
        for katman in sira:
            etkilenen = any(k in bozuk for k in kayitlar[katman])
            kalan = [k for k in kayitlar[katman] if k not in bozuk]
            if etkilenen and not kalan:
                tek_noktalar.append(katman)
        rapor.append({"id": kimlik, "tek_noktalar": tek_noktalar, "yedekli": not tek_noktalar})
    rapor.sort(key=lambda x: x["id"])
    return {"senaryolar": rapor, "tek_nokta_sayisi": sum(1 for x in rapor if x["tek_noktalar"])}
```

```hint
Her senaryoda bozulanları kümeye çevir. Katmanın etkilenip etkilenmediğini ve sağlam kontrol listesini ayrı hesapla; iki koşul birlikteyse katmanı ekle.
```
:::

::: anlat Fail-closed karar gerçek bir gözleme dayanmalı
Buraya kadar kontrol gözlemleri sentetik fixture'dı. Ama fail-closed mantığının değeri, gözlemler **gerçek** olduğunda ortaya çıkar. Son görevde senin `istek_karari_hesapla` işlevin, bir çıktı katmanı kontrolünün **gerçek bir model çalıştırmasından** gelen sonucuyla çalışır: deney modele iki görev verir ve çıktıyı bir şema guardrail'inden geçirir — yanıt beklenen biçime (yalnız tam sayı) uyuyorsa `cikti_semasi` kontrolü `gecti`, uymuyorsa `kaldi` üretir. Şemaya uyan çıktıda karar `izin`, uymayanda `reddet` olur. Böylece reddetme bir temenniden değil, modelin gerçek çıktısının şemayı ihlal etmesinden gelir; hatalı ya da eksik bir gözlem asla izne dönüşmez.
:::

::: gorev Gerçek deney · Gerçek çıktı-şeması gözlemiyle fail-closed karar
`istek_karari_hesapla(mimari, olaylar)` işlevini yaz — kuralları ve çıktısı 2. görevdekiyle **aynıdır**. Deney `cikti:cikti_semasi` kontrolü için gerçek bir model çıktısını şemadan geçirir (yalnız tam sayı mı), sonucunu (`gecti`/`kaldi`) olaylara koyar; diğer kontroller `gecti`dir. Senin kararın şemaya uyan çıktıda `izin`, uymayanda `reddet` üretmeli.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def istek_karari_hesapla(mimari, olaylar):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_03 as deney
    deney.goster(istek_karari_hesapla)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "referans_karar", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("istek_karari_hesapla")
from sandbox import ai_gercek_ai_savunma_03 as D
M = D.MIMARI
def tam(cikti):
    km = {k["id"]: k["kontroller"] for k in M}
    o = []
    for kat in ["girdi", "model", "cikti", "arac", "veri"]:
        for ktrl in km[kat]:
            o.append({"katman": kat, "kontrol": ktrl, "sonuc": cikti if (kat == "cikti" and ktrl == "cikti_semasi") else "gecti"})
    return o
def sozlesme(f):
    try:
        for c in ("gecti", "kaldi"):
            if f([dict(k) for k in M], tam(c)) != D.referans_karar(M, tam(c)):
                return False
        for mim, ol in [(None, []), (M, None), (M, [None]), (M, [dict(tam("gecti")[0], ek=1)]),
                        (M, [dict(tam("gecti")[0], sonuc="belirsiz")]), (M, [tam("gecti")[0], tam("gecti")[0]]),
                        (M[:-1], tam("gecti")), (M, [{"katman": "girdi", "kontrol": "yetki", "sonuc": "gecti"}])]:
            try:
                f(mim, ol)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "fail-closed karar doğru; geçersiz girdi reddedilmeli")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    for k in r["kayitlar"]:
        kontrol(k["karar"] == D.referans_karar(M, k["olaylar"]) if "olaylar" in k else True, "karar bağımsız hesapla aynı")
    oz = D.ozet(r)
    kontrol(oz["uyar_karar"] == "izin", f"şemaya uyan gerçek çıktı → izin ({oz['uyar_sema']})")
    kontrol(oz["bozuk_karar"] == "reddet", f"şemaya uymayan gerçek çıktı → reddet (fail-closed): cikti_semasi={oz['bozuk_sema']}")
yol = ai_lab.kanit_yaz("savunma-katman", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-03",
                                          "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): gerçek çıktı-şeması guardrail'i — sayı isteyen görevde çıktı şemaya uydu ({oz['uyar_sema']}) → {oz['uyar_karar']}; "
             f"düzyazı üreten görevde çıktı şemayı ihlal etti ({oz['bozuk_sema']}) → {oz['bozuk_karar']}. Karar gerçek model çıktısından geldi, fail-closed korundu.")
```

```solution
import ai_lab

def istek_karari_hesapla(mimari, olaylar):
    sira = ["girdi", "model", "cikti", "arac", "veri"]
    izinli = {"girdi": {"sema", "boyut", "icerik"}, "model": {"sistem_promptu", "model_sabitleme"},
              "cikti": {"cikti_semasi", "dlp"}, "arac": {"yetki", "onay", "sandbox"}, "veri": {"kiraci", "provenance", "sorgu"}}
    if not isinstance(mimari, list) or not isinstance(olaylar, list):
        raise ValueError("mimari/olay listesi geçersiz")
    if len(mimari) != len(sira):
        raise ValueError("beş katman zorunlu")
    kayit = {}
    for i, katman in enumerate(mimari):
        if not isinstance(katman, dict) or set(katman) != {"id", "kontroller"} or katman["id"] != sira[i]:
            raise ValueError("katman geçersiz")
        kontroller = katman["kontroller"]
        if not isinstance(kontroller, list) or not kontroller or kontroller != sorted(set(kontroller)) \
                or any(k not in izinli[katman["id"]] for k in kontroller):
            raise ValueError("kontrol geçersiz")
        kayit[katman["id"]] = kontroller
    sonuc = {}
    for o in olaylar:
        if not isinstance(o, dict) or set(o) != {"katman", "kontrol", "sonuc"}:
            raise ValueError("olay şeması geçersiz")
        if o["katman"] not in kayit or o["kontrol"] not in kayit[o["katman"]]:
            raise ValueError("olay katman/kontrolü geçersiz")
        if (o["katman"], o["kontrol"]) in sonuc:
            raise ValueError("olay yinelenemez")
        if o["sonuc"] not in ("gecti", "kaldi", "hata"):
            raise ValueError("olay sonucu geçersiz")
        sonuc[(o["katman"], o["kontrol"])] = o["sonuc"]
    eksik, neden = [], None
    for katman in sira:
        for kontrol in kayit[katman]:
            s = sonuc.get((katman, kontrol))
            if s is None:
                eksik.append(katman + ":" + kontrol)
            if s in ("kaldi", "hata") and neden is None:
                neden = {"katman": katman, "kontrol": kontrol, "sonuc": s}
    karar = "reddet" if neden else ("eksik" if eksik else "izin")
    return {"karar": karar, "neden": neden, "eksik": eksik}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_03 as deney
    deney.goster(istek_karari_hesapla)
```

```hint
Bu işlev 2. görevdeki `istek_karari_hesapla` ile birebir aynıdır; tek fark, `cikti_semasi` gözleminin gerçek bir model çıktısının şema denetiminden gelmesidir. Olayları `(katman, kontrol) → sonuç` sözlüğüne koy, mimari sırayla gez, ilk `kaldi`/`hata`yı neden yap; hiçbiri yoksa eksik varsa `eksik`, yoksa `izin`.
```
:::
