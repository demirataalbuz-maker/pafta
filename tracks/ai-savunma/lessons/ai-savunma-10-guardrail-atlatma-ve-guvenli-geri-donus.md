---
id: ai-savunma-10
title: Guardrail Atlatma ve Güvenli Geri Dönüş
summary: Guardrail hata ve atlanmalarını fail-closed yorumla, geçici hatalarda sınırlı yeniden deneme planla ve ham içeriği sızdırmayan güvenli yedek üret.
timeout: 45
---

::: anlat Guardrail yokluğu izin değildir
Bir guardrail zaman aşımına uğradığında, hata verdiğinde veya akıştan tamamen atlandığında model yanıtını kullanıcıya geçirmek fail-open davranıştır. Bu dersin politikasında yalnız tamamlanmış, `izin` vermiş ve risk taşımayan denetim model yanıtı kanalını açar. Ret ve risk güvenli yedeğe; geçici teknik hata yeniden deneme değerlendirmesine; atlanma ise doğrudan güvenli yedeğe gider.

NeMo Guardrails ve Promptfoo gerçek bir kurulumda bu akışları ve atlatma vakalarını sınamak için kullanılabilir. Buradaki kod dış servis çağırmaz, uyumaz ve model indirmez. Yeniden deneme yalnız deterministik bir plan olarak hesaplanır.
:::

::: tahmin Üst sınır bekleme süresini keser
Üç çıktı satırını yaz:

```python
taban, tavan = 500, 800
print(min(taban * 2 ** 0, tavan))
print(min(taban * 2 ** 1, tavan))
print(min(taban * 2 ** 2, tavan))
```

???

```cikti
500
800
800
```

Üstel bekleme tavanı aşamaz; bu planı hesaplamak gerçek zaman uyutması yapmakla aynı şey değildir.
:::

::: gorev 1 · Guardrail sonucunu fail-closed kanal kararına çevir
`guardrail_sonucunu_yorumla(sonuc)` işlevini yaz. Sonuç tam olarak `durum`, `karar`, `riskler` alanlarını taşısın. Durum `tamam`, `hata`, `zaman_asimi` veya `atlandi` olmalıdır.

Durum `tamam` ise karar `izin` veya `reddet` olmalıdır. Diğer durumlarda karar `None` ve risk listesi boş olmalıdır. Riskler yalnız `ozel_anahtar`, `bearer_token`, `api_anahtari`, `gizli_isaret` türlerinin bu sabit sırasına uyan, yinelenmeyen listedir. Geçersiz veride `ValueError` yükselt.

Yalnız `tamam + izin + boş risk` için `{"kanal":"model_yaniti","neden":"guardrail_izin"}` döndür. Tamamlanmış ret veya risk varlığında `guvenli_yedek`/`politika`; hata veya zaman aşımında `yeniden_dene_degerlendir`/`guardrail_hatasi`; atlanmada `guvenli_yedek`/`guardrail_atladi` döndür. Girdiyi değiştirme.

```starter
def guardrail_sonucunu_yorumla(sonuc):
    return {"kanal": "guvenli_yedek", "neden": "guardrail_hatasi"}
```

```test
def sozlesme(fn):
    try:
        if fn({"durum": "tamam", "karar": "izin", "riskler": []}) != {"kanal": "model_yaniti", "neden": "guardrail_izin"}:
            return False
        if fn({"durum": "tamam", "karar": "izin", "riskler": ["bearer_token"]}) != {"kanal": "guvenli_yedek", "neden": "politika"}:
            return False
        if fn({"durum": "tamam", "karar": "reddet", "riskler": []}) != {"kanal": "guvenli_yedek", "neden": "politika"}:
            return False
        for durum in ("hata", "zaman_asimi"):
            if fn({"durum": durum, "karar": None, "riskler": []}) != {"kanal": "yeniden_dene_degerlendir", "neden": "guardrail_hatasi"}:
                return False
        if fn({"durum": "atlandi", "karar": None, "riskler": []}) != {"kanal": "guvenli_yedek", "neden": "guardrail_atladi"}:
            return False
        for sonuc in [
            None, [], {"durum": "tamam", "karar": "izin"},
            {"durum": "tamam", "karar": "izin", "riskler": [], "ek": 1},
            {"durum": "bilinmiyor", "karar": None, "riskler": []},
            {"durum": "tamam", "karar": None, "riskler": []},
            {"durum": "tamam", "karar": "belirsiz", "riskler": []},
            {"durum": "hata", "karar": "izin", "riskler": []},
            {"durum": "atlandi", "karar": None, "riskler": ["bearer_token"]},
            {"durum": "tamam", "karar": "izin", "riskler": None},
            {"durum": "tamam", "karar": "izin", "riskler": "bearer_token"},
            {"durum": "tamam", "karar": "izin", "riskler": ["bilinmeyen"]},
            {"durum": "tamam", "karar": "izin", "riskler": ["bearer_token", "bearer_token"]},
            {"durum": "tamam", "karar": "izin", "riskler": ["gizli_isaret", "bearer_token"]},
        ]:
            try:
                fn(sonuc)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(guardrail_sonucunu_yorumla), "fail-closed kanal, hata ve atlanma ayrımı korunmalı")
def m_atlama(sonuc):
    sonuc = dict(sonuc, durum="tamam", karar="izin", riskler=[])
    return guardrail_sonucunu_yorumla(sonuc)
def m_risk(sonuc):
    sonuc = dict(sonuc, riskler=[])
    return guardrail_sonucunu_yorumla(sonuc)
def m_hata(sonuc):
    sonuc = dict(sonuc, durum="tamam", karar="izin", riskler=[])
    return guardrail_sonucunu_yorumla(sonuc)
for ad, mutant in [("atlamayı izin sayan", m_atlama), ("riski silen", m_risk), ("hatayı başarı yapan", m_hata)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def guardrail_sonucunu_yorumla(sonuc):
    if not isinstance(sonuc, dict) or set(sonuc) != {"durum", "karar", "riskler"}:
        raise ValueError("guardrail sonucu geçersiz")
    durum = sonuc["durum"]
    if durum not in ("tamam", "hata", "zaman_asimi", "atlandi"):
        raise ValueError("guardrail durumu geçersiz")
    riskler = sonuc["riskler"]
    if not isinstance(riskler, list):
        raise ValueError("riskler liste olmalı")
    sira = ["ozel_anahtar", "bearer_token", "api_anahtari", "gizli_isaret"]
    if len(set(riskler)) != len(riskler):
        raise ValueError("riskler yinelenemez")
    if any(r not in sira for r in riskler):
        raise ValueError("risk türü geçersiz")
    konumlar = [sira.index(r) for r in riskler]
    if konumlar != sorted(konumlar):
        raise ValueError("risk sırası geçersiz")
    if durum == "tamam":
        if sonuc["karar"] not in ("izin", "reddet"):
            raise ValueError("tamamlanan karar geçersiz")
        if sonuc["karar"] == "izin" and not riskler:
            return {"kanal": "model_yaniti", "neden": "guardrail_izin"}
        return {"kanal": "guvenli_yedek", "neden": "politika"}
    if sonuc["karar"] is not None or riskler:
        raise ValueError("tamamlanmayan sonuç karar veya risk taşıyamaz")
    if durum in ("hata", "zaman_asimi"):
        return {"kanal": "yeniden_dene_degerlendir", "neden": "guardrail_hatasi"}
    return {"kanal": "guvenli_yedek", "neden": "guardrail_atladi"}
```

```hint
Önce sonuç şemasını ve risk sırasını doğrula. Model kanalını tek dar koşulda aç; tamamlanmamış sonuçlarda karar ve risk alanlarının boş olduğunu ayrıca denetle.
```
:::

::: anlat Yeniden deneme sonsuz bir döngü değildir
Yalnız zaman aşımı ve açıkça geçici hata yeniden denenebilir. Kalıcı hata ve başarı terminaldir; bu kayıtlardan sonra başka deneme bulunamaz. Deneme sayısı politika üst sınırına ulaştığında geçici hata bile güvenli yedeğe yönelir.

Bekleme süresi `min(taban_ms * 2 ** (deneme - 1), tavan_ms)` formülüyle hesaplanır. Başarı, kalıcı hata ve bütçenin bitmesi sıfır beklemeyle terminal eylem üretir. Fonksiyon gerçek uyku veya ağ çağrısı yapmaz.
:::

::: gorev 2 · Sınırlı ve üstel beklemeli yeniden deneme planı hesapla
`yeniden_deneme_plani(hatalar, ayar)` işlevini yaz. Ayar tam olarak `maks_deneme`, `taban_ms`, `tavan_ms` alanlarını taşısın. Üçü de bool olmayan int olmalıdır: maksimum deneme 1–5, taban 1–1000, tavan ise taban ile 10000 aralığındadır.

`hatalar`, en az bir ve en fazla `maks_deneme` kaydından oluşan liste olmalıdır. Her kayıt `zaman_asimi`, `gecici_hata`, `kalici_hata` veya `basarili` stringidir. Başarı ve kalıcı hata yalnız son kayıt olabilir. Geçersiz veride `ValueError` yükselt.

Her kayıt için `{"deneme":N,"eylem":EYLEM,"bekle_ms":MS}` üret:

- Başarı: `dur`, 0 ms.
- Kalıcı hata: `guvenli_yedek`, 0 ms.
- Geçici hata veya zaman aşımı, bütçe dolmadıysa: `yeniden_dene` ve formüldeki bekleme.
- Bütçe dolan geçici hata: `guvenli_yedek`, 0 ms.

`{"adimlar":[...],"toplam_bekle_ms":TOPLAM}` döndür. Girdi listesini ve ayarı değiştirme; gerçek uyku çağrısı yapma.

```starter
def yeniden_deneme_plani(hatalar, ayar):
    return {"adimlar": [], "toplam_bekle_ms": 0}
```

```test
import copy
A = {"maks_deneme": 3, "taban_ms": 100, "tavan_ms": 800}
def sozlesme(fn):
    try:
        h = ["zaman_asimi", "gecici_hata", "basarili"]
        once = list(h)
        aonce = dict(A)
        beklenen = {"adimlar": [
            {"deneme": 1, "eylem": "yeniden_dene", "bekle_ms": 100},
            {"deneme": 2, "eylem": "yeniden_dene", "bekle_ms": 200},
            {"deneme": 3, "eylem": "dur", "bekle_ms": 0},
        ], "toplam_bekle_ms": 300}
        if fn(h, A) != beklenen or h != once or A != aonce:
            return False
        sinirli = fn(["gecici_hata", "gecici_hata"], {"maks_deneme": 2, "taban_ms": 500, "tavan_ms": 800})
        if sinirli != {"adimlar": [
            {"deneme": 1, "eylem": "yeniden_dene", "bekle_ms": 500},
            {"deneme": 2, "eylem": "guvenli_yedek", "bekle_ms": 0},
        ], "toplam_bekle_ms": 500}:
            return False
        if fn(["zaman_asimi"], {"maks_deneme": 1, "taban_ms": 1, "tavan_ms": 1})["adimlar"][0]["eylem"] != "guvenli_yedek":
            return False
        if fn(["basarili"], A)["toplam_bekle_ms"] != 0 or fn(["kalici_hata"], A)["adimlar"][0]["eylem"] != "guvenli_yedek":
            return False
        if fn(["gecici_hata"], {"maks_deneme": 5, "taban_ms": 1000, "tavan_ms": 10000})["adimlar"][0]["bekle_ms"] != 1000:
            return False
        for hatalar, ayar in [
            (None, A), ({}, A), ([], A), (["x"], A), ([1], A),
            (["basarili", "gecici_hata"], A), (["kalici_hata", "gecici_hata"], A),
            (["gecici_hata"] * 4, A), (["gecici_hata"], None),
            (["gecici_hata"], dict(A, ek=1)), (["gecici_hata"], dict(A, maks_deneme=True)),
            (["gecici_hata"], dict(A, maks_deneme=0)), (["gecici_hata"], dict(A, maks_deneme=6)),
            (["gecici_hata"], dict(A, taban_ms=0)),
            (["gecici_hata"], dict(A, taban_ms=1001, tavan_ms=10000)),
            (["gecici_hata"], dict(A, tavan_ms=99)), (["gecici_hata"], dict(A, tavan_ms=10001)),
            (["gecici_hata"], dict(A, taban_ms=1.5)),
        ]:
            try:
                fn(hatalar, ayar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yeniden_deneme_plani), "hata sınıfı, terminal kayıt, bütçe ve bekleme sınırları korunmalı")
def m_kalici(hatalar, ayar):
    degisen = ["gecici_hata" for _ in hatalar]
    return yeniden_deneme_plani(degisen, ayar)
def m_butce(hatalar, ayar):
    return yeniden_deneme_plani(hatalar, dict(ayar, maks_deneme=5))
def m_tavan(hatalar, ayar):
    return yeniden_deneme_plani(hatalar, dict(ayar, tavan_ms=10000))
for ad, mutant in [("kalıcı hatayı geçici sayan", m_kalici), ("bütçeyi büyüten", m_butce), ("tavanı kaldıran", m_tavan)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yeniden_deneme_plani(hatalar, ayar):
    if not isinstance(ayar, dict) or set(ayar) != {"maks_deneme", "taban_ms", "tavan_ms"}:
        raise ValueError("ayar şeması geçersiz")
    for alan in ("maks_deneme", "taban_ms", "tavan_ms"):
        if type(ayar[alan]) is not int:
            raise ValueError("ayarlar int olmalı")
    if ayar["maks_deneme"] < 1 or ayar["maks_deneme"] > 5:
        raise ValueError("maksimum deneme aralığı geçersiz")
    if ayar["taban_ms"] < 1 or ayar["taban_ms"] > 1000:
        raise ValueError("taban bekleme aralığı geçersiz")
    if ayar["tavan_ms"] < ayar["taban_ms"] or ayar["tavan_ms"] > 10000:
        raise ValueError("tavan bekleme aralığı geçersiz")
    if not isinstance(hatalar, list) or not hatalar:
        raise ValueError("hata listesi geçersiz")
    if len(hatalar) > ayar["maks_deneme"]:
        raise ValueError("deneme bütçesi aşıldı")
    if any(h not in ("zaman_asimi", "gecici_hata", "kalici_hata", "basarili") for h in hatalar):
        raise ValueError("hata türü geçersiz")
    for hata in hatalar[:-1]:
        if hata in ("kalici_hata", "basarili"):
            raise ValueError("terminal kayıttan sonra deneme olamaz")
    adimlar = []
    toplam = 0
    for indeks, hata in enumerate(hatalar):
        deneme = indeks + 1
        if hata == "basarili":
            eylem, bekle = "dur", 0
        elif hata == "kalici_hata":
            eylem, bekle = "guvenli_yedek", 0
        elif deneme < ayar["maks_deneme"]:
            eylem = "yeniden_dene"
            bekle = min(ayar["taban_ms"] * 2 ** indeks, ayar["tavan_ms"])
        else:
            eylem, bekle = "guvenli_yedek", 0
        toplam += bekle
        adimlar.append({"deneme": deneme, "eylem": eylem, "bekle_ms": bekle})
    return {"adimlar": adimlar, "toplam_bekle_ms": toplam}
```

```hint
Ayar sınırlarını ve terminal kayıt konumlarını önce doğrula. Beklemeyi sıfır tabanlı indeksle hesapla; deneme numarasını ise bir tabanlı döndür.
```
:::

::: anlat Güvenli yedek ham hata veya model içeriğini kopyalamaz
Son çıktı katmanı defense-in-depth uygular. Model kanalı işaretlenmiş olsa bile aday metinde canary, özel anahtar başlığı veya Bearer token varsa içerik geçirilmez. Güvenli yedek kanalında da kullanıcıya sabit, nötr bir mesaj verilir; aday metin veya teknik hata kopyalanmaz.

Yeniden deneme kanalı kullanıcıya metin göstermek yerine `yanit = None` üretir. Böylece istemci akışı geçici durumu nihai güvenli yanıtla karıştırmaz.
:::

::: gorev 3 · Ham içeriği sızdırmayan son geri dönüş raporunu üret
`guvenli_geri_donus_raporu(kayitlar)` işlevini yaz. Her kayıt tam olarak `id`, `kanal`, `yanit_adayi` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren benzersiz stringdir. Kanal ilk görevdeki `model_yaniti`, `guvenli_yedek` veya `yeniden_dene_degerlendir` değerlerinden biri; aday NUL içermeyen ve en fazla 2000 karakterlik string olmalıdır. Geçersiz veride `ValueError` yükselt.

Yalnız model kanalında, baş/son boşluğu olmayan boş olmayan ve `BREACH:CANARY-42`, `PRIVATE KEY`, `Bearer ` içermeyen aday aynen geçirilir. Bu durumda karar `model_yaniti` ve `ham_icerik_tasindi = true` olur.

Diğer model adayları ve `guvenli_yedek` kanalı için karar `guvenli_yedek`, yanıt tam olarak `Güvenli yanıt üretilemedi; istek tamamlanamadı.` ve ham içerik bayrağı false olur. Yeniden deneme kanalında karar `yeniden_dene`, yanıt `None`, bayrak false olur.

Her kayıt için `{"id":ID,"karar":KARAR,"yanit":YANIT,"ham_icerik_tasindi":BOOL}` döndür. Kimliğe göre sırala, boş girdide boş liste döndür ve girdiyi değiştirme.

```starter
def guvenli_geri_donus_raporu(kayitlar):
    return []
```

```test
import copy
K = [
    {"id": "model-1", "kanal": "model_yaniti", "yanit_adayi": "Kısa ve güvenli özet"},
    {"id": "risk-1", "kanal": "model_yaniti", "yanit_adayi": "BREACH:CANARY-42"},
    {"id": "yedek-1", "kanal": "guvenli_yedek", "yanit_adayi": "Bearer gizli-deger"},
    {"id": "retry-1", "kanal": "yeniden_dene_degerlendir", "yanit_adayi": "teknik hata"},
]
YEDEK = "Güvenli yanıt üretilemedi; istek tamamlanamadı."
BEKLENEN = [
    {"id": "model-1", "karar": "model_yaniti", "yanit": "Kısa ve güvenli özet", "ham_icerik_tasindi": True},
    {"id": "retry-1", "karar": "yeniden_dene", "yanit": None, "ham_icerik_tasindi": False},
    {"id": "risk-1", "karar": "guvenli_yedek", "yanit": YEDEK, "ham_icerik_tasindi": False},
    {"id": "yedek-1", "karar": "guvenli_yedek", "yanit": YEDEK, "ham_icerik_tasindi": False},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once or fn(list(reversed(K))) != BEKLENEN or fn([]) != []:
            return False
        for aday in ("", " x", "x ", "-----BEGIN PRIVATE KEY-----", "Bearer token-123"):
            if fn([dict(K[0], yanit_adayi=aday)])[0]["karar"] != "guvenli_yedek":
                return False
        if fn([dict(K[0], id="a" * 64)])[0]["id"] != "a" * 64:
            return False
        if fn([dict(K[0], yanit_adayi="a" * 2000)])[0]["karar"] != "model_yaniti":
            return False
        for kayitlar in [
            None, {}, [None], [dict(K[0], ek=1)], [dict(K[0], id="")],
            [dict(K[0], id="a" * 65)], [dict(K[0], id="a b")], [dict(K[0], kanal="diger")],
            [dict(K[0], yanit_adayi=None)], [dict(K[0], yanit_adayi="a\x00b")],
            [dict(K[0], yanit_adayi="a" * 2001)], [K[0], K[0]],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(guvenli_geri_donus_raporu), "riskli aday, sabit yedek, retry ve ham içerik bayrağı korunmalı")
def m_risk(kayitlar):
    degisen = [dict(x, yanit_adayi="güvenli") for x in kayitlar]
    return guvenli_geri_donus_raporu(degisen)
def m_kanal(kayitlar):
    degisen = [dict(x, kanal="model_yaniti") for x in kayitlar]
    return guvenli_geri_donus_raporu(degisen)
def m_ham(kayitlar):
    sonuc = guvenli_geri_donus_raporu(kayitlar)
    for x in sonuc:
        x["ham_icerik_tasindi"] = True
    return sonuc
for ad, mutant in [("riskli adayı temiz sayan", m_risk), ("kanalı değiştiren", m_kanal), ("ham içerik bayrağını bozan", m_ham)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def guvenli_geri_donus_raporu(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıt listesi geçersiz")
    kimlikler = set()
    rapor = []
    yedek = "Güvenli yanıt üretilemedi; istek tamamlanamadı."
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"id", "kanal", "yanit_adayi"}:
            raise ValueError("kayıt şeması geçersiz")
        kimlik = kayit["id"]
        if not isinstance(kimlik, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        if kayit["kanal"] not in ("model_yaniti", "guvenli_yedek", "yeniden_dene_degerlendir"):
            raise ValueError("kanal geçersiz")
        aday = kayit["yanit_adayi"]
        if not isinstance(aday, str) or "\x00" in aday:
            raise ValueError("yanıt adayı geçersiz")
        if len(aday) > 2000:
            raise ValueError("yanıt adayı çok uzun")
        riskli = any(isaret in aday for isaret in ("BREACH:CANARY-42", "PRIVATE KEY", "Bearer "))
        if kayit["kanal"] == "model_yaniti" and aday and aday == aday.strip() and not riskli:
            karar, yanit, ham = "model_yaniti", aday, True
        elif kayit["kanal"] == "yeniden_dene_degerlendir":
            karar, yanit, ham = "yeniden_dene", None, False
        else:
            karar, yanit, ham = "guvenli_yedek", yedek, False
        rapor.append({"id": kimlik, "karar": karar, "yanit": yanit, "ham_icerik_tasindi": ham})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Model kanalındaki bütün kabul koşullarını birlikte denetle. Yeniden denemeyi güvenli yedekten önce ayrı ele al; yedek metni kayıttan değil sabit olarak üret.
```
:::

::: anlat Güvenli geri dönüş gerçek riskli çıktıyı durdurur
Güvenli geri dönüşün amacı, guardrail bir çıktıyı reddettiğinde o ham çıktının yine de kullanıcıya sızmasını engellemektir. Son görevde senin `guvenli_geri_donus_raporu` işlevin, gerçek yerel modelin iki senaryoda ürettiği **gerçek** çıktıları karara bağlar: zararsız bir özet ve modelin kimlik-bilgisi biçimli bir dize (ör. Authorization Bearer satırı) ürettiği senaryo. İkincisi zararsız bir istektir, ama modeller kimlik-bilgisi biçimli örnekleri seve seve üretir; çıktı guardrail'i bu biçimi bir sızıntı riski sayar.

Sandbox her çıktının sızıntı sinyallerini bağımsız bulur, bir guardrail sonucu üretir ve fail-closed yorumlayıcıyla (1. görev) kanala çevirir. Senin raporun kararı verir: temiz model çıktısı aynen geçer; riskli çıktı `guvenli_yedek` kanalına düşer ve ham içerik taşınmaz — yerine sabit güvenli yedek metni gider. Böylece bir guardrail reddi sessizce ham (riskli) yanıtı göndermez.
:::

::: gorev Gerçek deney · Riskli gerçek çıktıda güvenli geri dönüş
`guvenli_geri_donus_raporu(kayitlar)` işlevini yaz — kuralları ve çıktısı 3. görevdekiyle **aynıdır**. Deney gerçek modeli iki senaryoda koşar, her çıktının guardrail kararını ve kanalını gerçek sızıntı sinyallerinden üretir; senin raporun temiz çıktıyı geçirir, riskli çıktıyı sabit güvenli yedekle değiştirir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def guvenli_geri_donus_raporu(kayitlar):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_10 as deney
    deney.goster(guvenli_geri_donus_raporu)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "referans_yorumla", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("guvenli_geri_donus_raporu")
from sandbox import ai_gercek_ai_savunma_10 as D
YEDEK = "Güvenli yanıt üretilemedi; istek tamamlanamadı."
K = [
    {"id": "model-1", "kanal": "model_yaniti", "yanit_adayi": "Kısa ve güvenli özet"},
    {"id": "risk-1", "kanal": "model_yaniti", "yanit_adayi": "Bearer token-123"},
    {"id": "yedek-1", "kanal": "guvenli_yedek", "yanit_adayi": "ham"},
]
BEKLENEN = [
    {"id": "model-1", "karar": "model_yaniti", "yanit": "Kısa ve güvenli özet", "ham_icerik_tasindi": True},
    {"id": "risk-1", "karar": "guvenli_yedek", "yanit": YEDEK, "ham_icerik_tasindi": False},
    {"id": "yedek-1", "karar": "guvenli_yedek", "yanit": YEDEK, "ham_icerik_tasindi": False},
]
def sozlesme(f):
    try:
        if f([dict(k) for k in K]) != BEKLENEN or f([]) != []:
            return False
        for bozuk in (None, [None], [dict(K[0], ek=1)], [dict(K[0], kanal="diger")], [dict(K[0], yanit_adayi="a\x00b")]):
            try:
                f(bozuk)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "riskli aday, sabit yedek, retry ve ham içerik bayrağı korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(r["riskli_guvenli"], "riskli gerçek çıktı son yanıta taşınmadı")
    riskli = [a for a in r["akislar"] if a["riskler"]]
    kontrol(len(riskli) >= 1, "modelin gerçek çıktısında en az bir senaryo risk sinyali üretti")
    rapor_map = {x["id"]: x for x in r["rapor"]}
    kontrol(all(rapor_map[a["id"]]["karar"] == "guvenli_yedek" and not rapor_map[a["id"]]["ham_icerik_tasindi"] for a in riskli),
            "riskli çıktı güvenli yedeğe düştü, ham içerik taşınmadı")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-yedek", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-10",
                                         "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): {oz['senaryo']} gerçek çıktı → kararlar {oz['kararlar']}; "
             f"riskli çıktı {oz['riskli_cikti']}, ham içerik taşınan yanıt {oz['ham_tasindi']}, riskli güvenli {oz['riskli_guvenli']}. "
             f"Model kimlik-bilgisi biçimli bir dize üretti; guardrail reddinde ham çıktı gitmedi, sabit güvenli yedek üretildi (fail-closed).")
```

```solution
import ai_lab

def guvenli_geri_donus_raporu(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıt listesi geçersiz")
    kimlikler = set()
    rapor = []
    yedek = "Güvenli yanıt üretilemedi; istek tamamlanamadı."
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"id", "kanal", "yanit_adayi"}:
            raise ValueError("kayıt şeması geçersiz")
        kimlik = kayit["id"]
        if not isinstance(kimlik, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        if kayit["kanal"] not in ("model_yaniti", "guvenli_yedek", "yeniden_dene_degerlendir"):
            raise ValueError("kanal geçersiz")
        aday = kayit["yanit_adayi"]
        if not isinstance(aday, str) or "\x00" in aday:
            raise ValueError("yanıt adayı geçersiz")
        if len(aday) > 2000:
            raise ValueError("yanıt adayı çok uzun")
        riskli = any(isaret in aday for isaret in ("BREACH:CANARY-42", "PRIVATE KEY", "Bearer "))
        if kayit["kanal"] == "model_yaniti" and aday and aday == aday.strip() and not riskli:
            karar, yanit, ham = "model_yaniti", aday, True
        elif kayit["kanal"] == "yeniden_dene_degerlendir":
            karar, yanit, ham = "yeniden_dene", None, False
        else:
            karar, yanit, ham = "guvenli_yedek", yedek, False
        rapor.append({"id": kimlik, "karar": karar, "yanit": yanit, "ham_icerik_tasindi": ham})
    return sorted(rapor, key=lambda x: x["id"])

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_10 as deney
    deney.goster(guvenli_geri_donus_raporu)
```

```hint
Bu işlev 3. görevdeki `guvenli_geri_donus_raporu` ile birebir aynıdır; tek fark, kanal ve yanıt adaylarının gerçek model koşusundan gelmesidir. Model kanalındaki kabul koşullarını birlikte denetle; yedek metni sabit üret.
```
:::
