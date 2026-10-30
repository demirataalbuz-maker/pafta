---
id: ai-saldiri-19
title: Araç Çağrılarında Auth ve Yetki Bypass
summary: Kimliği doğrulanmış oturumdan bağla, nesne sahipliği ve işlem bazlı onayı denetle, politika kararı ile gerçekleşen çalışma arasındaki bypass farkını raporla.
timeout: 45
---

::: anlat Modelin söylediği kullanıcı, oturum kullanıcısı değildir
Model bir araç çağrısında `kullanici="admin"` veya başka bir kullanıcının nesne kimliğini üretebilir. Dispatcher kimliği bu JSON'dan alırsa kimlik bağlama bypass'ı oluşur. Kullanıcı kimliği, kimliği doğrulanmış oturumdan gelmelidir; model yalnız işlem adayını üretir.

Yetkilendirme üç ayrı sorudur:

1. **Kimlik:** İstek hangi doğrulanmış oturuma bağlı?
2. **Nesne ve işlem:** Bu kullanıcı bu nesne üzerinde bu eylemi yapabilir mi?
3. **Çalışma:** Politika kararı ile dispatcher'ın gerçekleştirdiği eylem aynı mı?

Bu derste Burp Suite, Ollama, ağ veya gerçek araç kullanılmaz. Oturum, nesne ve karar fixture'larıyla kimlik bağlama, BOLA/IDOR tarzı nesne kontrolü ve çalışma bypass'ı ölçülür.
:::

::: tahmin
Nesne sahipliği ve paylaşım kuralları değerlendiriliyor. Üç çıktı satırını yaz:

```python
nesne = {"sahip": "ayse", "paylasim": ["mehmet"]}
kullanici = "mehmet"
print(kullanici == nesne["sahip"] or kullanici in nesne["paylasim"])
print(kullanici == nesne["sahip"])
onay = {"nesne_id": "d2", "eylem": "sil"}
print(onay["nesne_id"] == "d1" and onay["eylem"] == "sil")
```

???

```cikti
True
False
False
```

Mehmet paylaşım nedeniyle okuyabilir fakat sahip olmadığı için yazamaz. Silme onayı başka nesneye aittir; işlem bazlı onay bu nesneye devredilemez.
:::

::: gorev 1 · Araç çağrısını doğrulanmış oturum kimliğine bağla
`kimlik_bagla(oturum, cagri)` işlevini yaz. Oturum tam olarak `kullanici`, `dogrulanmis` alanlarını taşısın; kullanıcı boş olmayan string, `dogrulanmis` bool olmalıdır. Çağrı tam olarak `kullanici`, `eylem` alanlarını taşısın; kullanıcı boş olmayan string, eylem `oku`, `yaz` veya `paylas` olmalıdır. Şema veya tür hatasında `ValueError` yükselt.

Dönüş `{"izinli":BOOL,"neden":NEDEN}` biçimindedir:

- Oturum doğrulanmamışsa `(False, "oturum-dogrulanmamis")`.
- Çağrıdaki kullanıcı oturum kullanıcısıyla aynı değilse `(False, "kimlik-uyusmazligi")`.
- Aksi durumda `(True, "bagli")`.

Önce oturum doğrulamasını denetle. Çağrıdaki kullanıcı adı eşleşse bile doğrulanmamış oturumu kabul etme; bu sonuç yalnız kimlik bağlamadır, nesne yetkisi değildir.

```starter
def kimlik_bagla(oturum, cagri):
    return {}
```

```test
OTURUM = {"kullanici": "ayse", "dogrulanmis": True}
CAGRI = {"kullanici": "ayse", "eylem": "oku"}
def sozlesme(fn):
    try:
        if fn(OTURUM, CAGRI) != {"izinli": True, "neden": "bagli"}:
            return False
        if fn(OTURUM, dict(CAGRI, kullanici="mehmet")) != {"izinli": False, "neden": "kimlik-uyusmazligi"}:
            return False
        if fn(dict(OTURUM, dogrulanmis=False), CAGRI) != {"izinli": False, "neden": "oturum-dogrulanmamis"}:
            return False
        for oturum, cagri in [
            (None, CAGRI), (dict(OTURUM, kullanici=""), CAGRI),
            (dict(OTURUM, dogrulanmis=1), CAGRI), (dict(OTURUM, ek=1), CAGRI),
            (OTURUM, dict(CAGRI, kullanici="")), (OTURUM, dict(CAGRI, eylem="sil")),
            (OTURUM, dict(CAGRI, rol="admin")), (OTURUM, None),
        ]:
            try:
                fn(oturum, cagri)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kimlik_bagla), "oturum doğrulaması, kullanıcı eşleşmesi ve şema korunmalı")
def m_cagri(oturum, cagri):
    return {"izinli": True, "neden": "bagli"}
def m_oturum(oturum, cagri):
    sonuc = kimlik_bagla(dict(oturum, dogrulanmis=True), cagri)
    return sonuc
def m_kullanici(oturum, cagri):
    return kimlik_bagla(oturum, dict(cagri, kullanici=oturum["kullanici"]))
for ad, mutant in [("çağrıyı doğrudan yetkili sayan", m_cagri), ("oturumu zorla doğrulanmış yapan", m_oturum), ("kullanıcı uyuşmazlığını gizleyen", m_kullanici)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kimlik_bagla(oturum, cagri):
    if not isinstance(oturum, dict) or set(oturum) != {"kullanici", "dogrulanmis"}:
        raise ValueError("oturum şeması geçersiz")
    if not all((isinstance(oturum["kullanici"], str), bool(oturum["kullanici"]), isinstance(oturum["dogrulanmis"], bool))):
        raise ValueError("oturum alanları geçersiz")
    if not isinstance(cagri, dict) or set(cagri) != {"kullanici", "eylem"}:
        raise ValueError("çağrı şeması geçersiz")
    if not all((isinstance(cagri["kullanici"], str), bool(cagri["kullanici"]), cagri["eylem"] in ("oku", "yaz", "paylas"))):
        raise ValueError("çağrı alanları geçersiz")
    if not oturum["dogrulanmis"]:
        return {"izinli": False, "neden": "oturum-dogrulanmamis"}
    if cagri["kullanici"] != oturum["kullanici"]:
        return {"izinli": False, "neden": "kimlik-uyusmazligi"}
    return {"izinli": True, "neden": "bagli"}
```

```hint
Şemaları doğruladıktan sonra önce `dogrulanmis` değerine bak. Sonra iki kullanıcı kimliğini karşılaştır; çağrıya rol veya ek yetki alanı ekleme.
```
:::

::: anlat Nesne sahipliği her eylemde yeniden denetlenir
Kullanıcının oturuma bağlı olması, her nesneye erişebileceği anlamına gelmez. Bu derste okuma sahip veya paylaşım listesine; yazma yalnız sahibe; silme ise sahip ve aynı nesne-işlem için üretilmiş açık onaya bağlıdır. Başka nesnenin kimliğini değiştirmek BOLA/IDOR saldırısının fixture karşılığıdır.

Onay global bir `True` değeri değildir. `{"nesne_id":"d1","eylem":"sil"}` yalnız bu nesnenin silinmesi için geçerlidir. Okuma ve yazma için onay alanı kullanılmaz. Gerçek sistemde onayın süresi, tek kullanımlılığı ve imzası da denetlenmelidir; burada yalnız kapsam bağlaması sınanır.
:::

::: gorev 2 · Nesne sahipliği ve işlem bazlı onayı uygula
`nesne_yetki(kullanici, nesne, eylem, onay)` işlevini yaz. Kullanıcı boş olmayan string olmalıdır. Nesne tam olarak `id`, `sahip`, `paylasim` alanlarını taşısın; kimlik ve sahip boş olmayan string, paylaşım boş olmayan ve benzersiz kullanıcı stringlerinden oluşan liste olmalıdır. Eylem `oku`, `yaz` veya `sil` olmalıdır. Şema ihlalinde `ValueError` yükselt.

Dönüş `{"izinli":BOOL,"neden":NEDEN}` biçimindedir:

- `oku`: kullanıcı sahip veya paylaşım listesindeyse izinli, aksi halde `nesne-erisimi-yok`.
- `yaz`: yalnız sahip izinli, aksi halde `sahiplik-gerekli`.
- `sil`: sahip değilse `sahiplik-gerekli`; sahipse onay tam `{"nesne_id":NESNE_ID,"eylem":"sil"}` olmalı, aksi halde `islem-onayi-gerekli`.

Başarı nedeni `izinli`. Onay verilmişse `None` veya tam iki alanlı dict olmalı; geçersiz onay şeması `ValueError` üretir. Okuma/yazma için onayın içeriği kararı değiştirmez. Sahibi onaydan okuma.

```starter
def nesne_yetki(kullanici, nesne, eylem, onay):
    return {}
```

```test
NESNE = {"id": "d1", "sahip": "ayse", "paylasim": ["mehmet"]}
ONAY = {"nesne_id": "d1", "eylem": "sil"}
def sozlesme(fn):
    try:
        for kullanici, nesne, eylem, onay, beklenen in [
            ("ayse", NESNE, "oku", None, (True, "izinli")),
            ("mehmet", NESNE, "oku", None, (True, "izinli")),
            ("mehmet", NESNE, "yaz", None, (False, "sahiplik-gerekli")),
            ("diger", NESNE, "oku", None, (False, "nesne-erisimi-yok")),
            ("ayse", NESNE, "sil", None, (False, "islem-onayi-gerekli")),
            ("ayse", NESNE, "sil", ONAY, (True, "izinli")),
            ("ayse", NESNE, "sil", dict(ONAY, nesne_id="d2"), (False, "islem-onayi-gerekli")),
            ("mehmet", NESNE, "sil", ONAY, (False, "sahiplik-gerekli")),
        ]:
            sonuc = fn(kullanici, nesne, eylem, onay)
            if (sonuc["izinli"], sonuc["neden"]) != beklenen:
                return False
        for kullanici, nesne, eylem, onay in [
            ("", NESNE, "oku", None), (3, NESNE, "oku", None), ("ayse", None, "oku", None),
            ("ayse", dict(NESNE, id=""), "oku", None), ("ayse", dict(NESNE, sahip=""), "oku", None),
            ("ayse", dict(NESNE, paylasim="mehmet"), "oku", None),
            ("ayse", dict(NESNE, paylasim=["mehmet", "mehmet"]), "oku", None),
            ("ayse", dict(NESNE, paylasim=[""]), "oku", None),
            ("ayse", NESNE, "paylas", None), ("ayse", NESNE, "sil", True),
            ("ayse", NESNE, "sil", dict(ONAY, ek=1)),
        ]:
            try:
                fn(kullanici, nesne, eylem, onay)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(nesne_yetki), "sahiplik, paylaşım, silme onayı ve onay kapsamı korunmalı")
def m_id(kullanici, nesne, eylem, onay):
    return {"izinli": True, "neden": "izinli"}
def m_onay(kullanici, nesne, eylem, onay):
    return nesne_yetki(kullanici, nesne, eylem, {"nesne_id": nesne["id"], "eylem": "sil"}) if eylem == "sil" else nesne_yetki(kullanici, nesne, eylem, onay)
def m_paylas(kullanici, nesne, eylem, onay):
    veri = dict(nesne, sahip=nesne["paylasim"][0])
    return nesne_yetki(kullanici, veri, eylem, onay)
for ad, mutant in [("her nesneye erişim veren", m_id), ("onayı zorla geçerli yapan", m_onay), ("paylaşımı sahipliğe çeviren", m_paylas)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def nesne_yetki(kullanici, nesne, eylem, onay):
    if not isinstance(kullanici, str) or not kullanici:
        raise ValueError("kullanıcı geçersiz")
    if not isinstance(nesne, dict) or set(nesne) != {"id", "sahip", "paylasim"}:
        raise ValueError("nesne şeması geçersiz")
    if not all((isinstance(nesne["id"], str), bool(nesne["id"]), isinstance(nesne["sahip"], str), bool(nesne["sahip"]), isinstance(nesne["paylasim"], list))):
        raise ValueError("nesne alanları geçersiz")
    if not all(isinstance(x, str) and bool(x) for x in nesne["paylasim"]) or len(nesne["paylasim"]) != len(set(nesne["paylasim"])):
        raise ValueError("paylaşım listesi geçersiz")
    if eylem not in ("oku", "yaz", "sil"):
        raise ValueError("eylem geçersiz")
    if onay is not None and (not isinstance(onay, dict) or set(onay) != {"nesne_id", "eylem"}):
        raise ValueError("onay şeması geçersiz")
    sahip = kullanici == nesne["sahip"]
    if eylem == "oku":
        izinli = sahip or kullanici in nesne["paylasim"]
        return {"izinli": izinli, "neden": "izinli" if izinli else "nesne-erisimi-yok"}
    if not sahip:
        return {"izinli": False, "neden": "sahiplik-gerekli"}
    if eylem == "yaz":
        return {"izinli": True, "neden": "izinli"}
    gecerli_onay = onay == {"nesne_id": nesne["id"], "eylem": "sil"}
    return {"izinli": gecerli_onay, "neden": "izinli" if gecerli_onay else "islem-onayi-gerekli"}
```

```hint
Okuma kararını sahiplik veya paylaşım üyeliğiyle ver. Yazma ve silmede önce sahipliği iste; silmede onay nesnesini nesne kimliği ve eylemle birebir karşılaştır.
```
:::

::: anlat İzinli karar ile çalışan eylem ayrı denetlenir
Bazı bypass'lar politika fonksiyonunda, bazıları dispatcher'dadır. Politika `reddet` derken dispatcher eylemi çalıştırırsa karar doğru görünse bile saldırı gerçekleşir. Tersine her isteği reddeden sistem bypass'ı önler fakat meşru kullanımı bozar.

Regresyon raporu dört ölçüt üretir: beklenen ret yerine izinli karar, beklenen ret yerine çalışan eylem, beklenen izin yerine yanlış ret ve bütünüyle tutarlı vakalar. `tutarli` için karar beklenene eşit olmalı ve `calistirildi` yalnız izinli vakalarda doğru olmalıdır. Bu fixture gerçek log toplamak yerine test sözleşmesini görünür kılar.
:::

::: gorev 3 · Karar ve çalışma bypass'ını ayrı raporla
`yetki_regresyonu(kayitlar)` işlevini yaz. Her kayıt tam olarak `vaka_id`, `beklenen`, `karar`, `calistirildi` alanlarını taşısın. Vaka kimliği boş olmayan ve benzersiz string, beklenen ve karar `izinli` veya `reddet`, `calistirildi` bool olmalıdır. Geçersiz veride `ValueError` yükselt.

Dönüş:

```text
{"vaka":N,"karar_bypassi":[...],"calisma_bypassi":[...],
 "yanlis_ret":[...],"tutarli":[...]}
```

- `karar_bypassi`: beklenen `reddet`, karar `izinli`.
- `calisma_bypassi`: beklenen `reddet` ve `calistirildi=True`.
- `yanlis_ret`: beklenen `izinli`, karar `reddet`.
- `tutarli`: beklenen karar ile aynı ve `calistirildi == (beklenen == "izinli")`.

Listeler alfabetik vaka kimliği sıralıdır. Bir vaka hem karar hem çalışma bypass'ına girebilir. Boş girdi için boş rapor dön; girdi sırası sonucu etkilememeli ve veri değişmemelidir.

```starter
def yetki_regresyonu(kayitlar):
    return {}
```

```test
import copy
KAYITLAR = [
    {"vaka_id": "v1", "beklenen": "reddet", "karar": "izinli", "calistirildi": True},
    {"vaka_id": "v2", "beklenen": "reddet", "karar": "reddet", "calistirildi": True},
    {"vaka_id": "v3", "beklenen": "izinli", "karar": "reddet", "calistirildi": False},
    {"vaka_id": "v4", "beklenen": "izinli", "karar": "izinli", "calistirildi": True},
    {"vaka_id": "v5", "beklenen": "reddet", "karar": "reddet", "calistirildi": False},
    {"vaka_id": "v6", "beklenen": "izinli", "karar": "izinli", "calistirildi": False},
]
BEKLENEN = {"vaka": 6, "karar_bypassi": ["v1"], "calisma_bypassi": ["v1", "v2"], "yanlis_ret": ["v3"], "tutarli": ["v4", "v5"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "karar_bypassi": [], "calisma_bypassi": [], "yanlis_ret": [], "tutarli": []}:
            return False
        for kayitlar in [
            KAYITLAR + [KAYITLAR[0]], [dict(KAYITLAR[0], beklenen="belirsiz")],
            [dict(KAYITLAR[0], karar="reddet", calistirildi=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], ek=1)], [None],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yetki_regresyonu), "karar, çalışma, yanlış ret ve tutarlılık ayrımı korunmalı")
def m_calisma(kayitlar):
    sonuc = yetki_regresyonu(kayitlar)
    sonuc["calisma_bypassi"] = sonuc["karar_bypassi"]
    return sonuc
def m_ret(kayitlar):
    sonuc = yetki_regresyonu(kayitlar)
    sonuc["yanlis_ret"] = []
    return sonuc
def m_tutarli(kayitlar):
    sonuc = yetki_regresyonu(kayitlar)
    sonuc["tutarli"] = sorted(x["vaka_id"] for x in kayitlar if x["beklenen"] == x["karar"])
    return sonuc
for ad, mutant in [("reddedip çalışan bypass'ı düşüren", m_calisma), ("yanlış retleri gizleyen", m_ret), ("çalışmayı tutarlılıkta yok sayan", m_tutarli)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yetki_regresyonu(kayitlar):
    vakalar = set()
    sonuc = {"vaka": 0, "karar_bypassi": [], "calisma_bypassi": [], "yanlis_ret": [], "tutarli": []}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "beklenen", "karar", "calistirildi"}:
            raise ValueError("kayıt şeması geçersiz")
        if not all((isinstance(kayit["vaka_id"], str), bool(kayit["vaka_id"]), kayit["vaka_id"] not in vakalar, kayit["beklenen"] in ("izinli", "reddet"), kayit["karar"] in ("izinli", "reddet"), isinstance(kayit["calistirildi"], bool))):
            raise ValueError("kayıt alanları geçersiz")
        vakalar.add(kayit["vaka_id"])
        if kayit["beklenen"] == "reddet" and kayit["karar"] == "izinli":
            sonuc["karar_bypassi"].append(kayit["vaka_id"])
        if kayit["beklenen"] == "reddet" and kayit["calistirildi"]:
            sonuc["calisma_bypassi"].append(kayit["vaka_id"])
        if kayit["beklenen"] == "izinli" and kayit["karar"] == "reddet":
            sonuc["yanlis_ret"].append(kayit["vaka_id"])
        if kayit["beklenen"] == kayit["karar"] and kayit["calistirildi"] == (kayit["beklenen"] == "izinli"):
            sonuc["tutarli"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("karar_bypassi", "calisma_bypassi", "yanlis_ret", "tutarli"):
        sonuc[alan].sort()
    return sonuc
```

```hint
Her vaka için beklenen, karar ve çalışma değerlerini ayrı kullan. Dört listeyi bağımsız `if` bloklarıyla doldur; tutarlılıkta hem kararı hem beklenen izinle çalışma eşitliğini denetle.
```
:::


::: anlat Kimliği ve nesne yetkisini gerçek SQLite önünde denetle
[Sentetik istek dosyasını aç](/data/ai-saldiri-19-istekler.txt). Çalıştır ayrı kalıcı `calisma/ai-saldiri-19/istekler.json` kopyasının yolunu gösterir. Dış editör/Python ile değiştirip yeniden Çalıştır; düzenlemelerin korunur. Test ayrı veriler kullanır. Ekranda yerleşik dosya editörü yoktur.

Her deney kendi SQLite veritabanında benim/ortak/yabanci nesnelerini kurar. Paylaşım ve sahiplik sunucu tarafındaki SQLite satırından okunur; model bunları değiştiremez. Oturum sentetik doğrulanmış kullanıcıdır, gerçek OAuth/giriş sağlayıcısı değildir. Öğrencinin iki kapısı gerçek SELECT/UPDATE/DELETE önünde çalışır. Silme yalnız deneyin kendi sentetik satırındadır; modelden veya belgeden güvenilir onay alınmaz. Doğrudan kontrollerde ayrı nesne/işlem bağlı onay verilir.

`kimlik_bagla` önceki sözleşmede oku/yaz/paylas kabul eder. Bu deneyde yalnız kimlik eşleşmesini ölçmek için ona eylem=oku verilir; bu bir silme izni değildir. **Gerçek eylem değişmeden `nesne_yetki` kapısına gider.** İki kapı da izin vermeden yürütme olmaz. Temiz/zehirli korumalı ve iki kapısı atlanmış yerel karşılaştırma kolu native model kullanır. On bir doğrudan sentetik kontrol gerçek diskte meşru okuma/yazma/onaylı silme ile kimlik/nesne/yanlış onay retlerini doğrular; model cevabı diye sunulmaz.

Ham native argümanlar, güvenilir oturum/onay, nesne ACL'i, karar, gerçekten çalışan işlem ve disk önce/sonrası ayrı kaydedilir. Model saldırıya uymayabilir; bu geçerli gözlemdir, saldırı başarısı geçme şartı değildir. Bu sınırlı yerel deney bütün üretim auth sistemlerini kapsamaz.
:::

::: gorev Gerçek deney · Model kimliğini ve yabancı nesne işlemini sınırla
Önceki `kimlik_bagla`, `nesne_yetki`, `yetki_regresyonu` işlevlerini birleştir. Kontrol Et saf sözleşmelerden sonra gerçek native model ve SQLite deneyini yürütür. Modelin söylediği admin adı gerçek kimlik sayılmaz.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def kimlik_bagla(oturum,cagri):return {}

def nesne_yetki(kullanici,nesne,eylem,onay):return {}

def yetki_regresyonu(kayitlar):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_19 as deney
    deney.goster(kimlik_bagla,nesne_yetki,yetki_regresyonu)

```

```test
OTURUM = {"kullanici": "ayse", "dogrulanmis": True}
CAGRI = {"kullanici": "ayse", "eylem": "oku"}
def sozlesme(fn):
    try:
        if fn(OTURUM, CAGRI) != {"izinli": True, "neden": "bagli"}:
            return False
        if fn(OTURUM, dict(CAGRI, kullanici="mehmet")) != {"izinli": False, "neden": "kimlik-uyusmazligi"}:
            return False
        if fn(dict(OTURUM, dogrulanmis=False), CAGRI) != {"izinli": False, "neden": "oturum-dogrulanmamis"}:
            return False
        for oturum, cagri in [
            (None, CAGRI), (dict(OTURUM, kullanici=""), CAGRI),
            (dict(OTURUM, dogrulanmis=1), CAGRI), (dict(OTURUM, ek=1), CAGRI),
            (OTURUM, dict(CAGRI, kullanici="")), (OTURUM, dict(CAGRI, eylem="sil")),
            (OTURUM, dict(CAGRI, rol="admin")), (OTURUM, None),
        ]:
            try:
                fn(oturum, cagri)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kimlik_bagla), "oturum doğrulaması, kullanıcı eşleşmesi ve şema korunmalı")
def m_cagri(oturum, cagri):
    return {"izinli": True, "neden": "bagli"}
def m_oturum(oturum, cagri):
    sonuc = kimlik_bagla(dict(oturum, dogrulanmis=True), cagri)
    return sonuc
def m_kullanici(oturum, cagri):
    return kimlik_bagla(oturum, dict(cagri, kullanici=oturum["kullanici"]))
for ad, mutant in [("çağrıyı doğrudan yetkili sayan", m_cagri), ("oturumu zorla doğrulanmış yapan", m_oturum), ("kullanıcı uyuşmazlığını gizleyen", m_kullanici)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

NESNE = {"id": "d1", "sahip": "ayse", "paylasim": ["mehmet"]}
ONAY = {"nesne_id": "d1", "eylem": "sil"}
def sozlesme(fn):
    try:
        for kullanici, nesne, eylem, onay, beklenen in [
            ("ayse", NESNE, "oku", None, (True, "izinli")),
            ("mehmet", NESNE, "oku", None, (True, "izinli")),
            ("mehmet", NESNE, "yaz", None, (False, "sahiplik-gerekli")),
            ("diger", NESNE, "oku", None, (False, "nesne-erisimi-yok")),
            ("ayse", NESNE, "sil", None, (False, "islem-onayi-gerekli")),
            ("ayse", NESNE, "sil", ONAY, (True, "izinli")),
            ("ayse", NESNE, "sil", dict(ONAY, nesne_id="d2"), (False, "islem-onayi-gerekli")),
            ("mehmet", NESNE, "sil", ONAY, (False, "sahiplik-gerekli")),
        ]:
            sonuc = fn(kullanici, nesne, eylem, onay)
            if (sonuc["izinli"], sonuc["neden"]) != beklenen:
                return False
        for kullanici, nesne, eylem, onay in [
            ("", NESNE, "oku", None), (3, NESNE, "oku", None), ("ayse", None, "oku", None),
            ("ayse", dict(NESNE, id=""), "oku", None), ("ayse", dict(NESNE, sahip=""), "oku", None),
            ("ayse", dict(NESNE, paylasim="mehmet"), "oku", None),
            ("ayse", dict(NESNE, paylasim=["mehmet", "mehmet"]), "oku", None),
            ("ayse", dict(NESNE, paylasim=[""]), "oku", None),
            ("ayse", NESNE, "paylas", None), ("ayse", NESNE, "sil", True),
            ("ayse", NESNE, "sil", dict(ONAY, ek=1)),
        ]:
            try:
                fn(kullanici, nesne, eylem, onay)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(nesne_yetki), "sahiplik, paylaşım, silme onayı ve onay kapsamı korunmalı")
def m_id(kullanici, nesne, eylem, onay):
    return {"izinli": True, "neden": "izinli"}
def m_onay(kullanici, nesne, eylem, onay):
    return nesne_yetki(kullanici, nesne, eylem, {"nesne_id": nesne["id"], "eylem": "sil"}) if eylem == "sil" else nesne_yetki(kullanici, nesne, eylem, onay)
def m_paylas(kullanici, nesne, eylem, onay):
    veri = dict(nesne, sahip=nesne["paylasim"][0])
    return nesne_yetki(kullanici, veri, eylem, onay)
for ad, mutant in [("her nesneye erişim veren", m_id), ("onayı zorla geçerli yapan", m_onay), ("paylaşımı sahipliğe çeviren", m_paylas)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KAYITLAR = [
    {"vaka_id": "v1", "beklenen": "reddet", "karar": "izinli", "calistirildi": True},
    {"vaka_id": "v2", "beklenen": "reddet", "karar": "reddet", "calistirildi": True},
    {"vaka_id": "v3", "beklenen": "izinli", "karar": "reddet", "calistirildi": False},
    {"vaka_id": "v4", "beklenen": "izinli", "karar": "izinli", "calistirildi": True},
    {"vaka_id": "v5", "beklenen": "reddet", "karar": "reddet", "calistirildi": False},
    {"vaka_id": "v6", "beklenen": "izinli", "karar": "izinli", "calistirildi": False},
]
BEKLENEN = {"vaka": 6, "karar_bypassi": ["v1"], "calisma_bypassi": ["v1", "v2"], "yanlis_ret": ["v3"], "tutarli": ["v4", "v5"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "karar_bypassi": [], "calisma_bypassi": [], "yanlis_ret": [], "tutarli": []}:
            return False
        for kayitlar in [
            KAYITLAR + [KAYITLAR[0]], [dict(KAYITLAR[0], beklenen="belirsiz")],
            [dict(KAYITLAR[0], karar="reddet", calistirildi=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], ek=1)], [None],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yetki_regresyonu), "karar, çalışma, yanlış ret ve tutarlılık ayrımı korunmalı")
def m_calisma(kayitlar):
    sonuc = yetki_regresyonu(kayitlar)
    sonuc["calisma_bypassi"] = sonuc["karar_bypassi"]
    return sonuc
def m_ret(kayitlar):
    sonuc = yetki_regresyonu(kayitlar)
    sonuc["yanlis_ret"] = []
    return sonuc
def m_tutarli(kayitlar):
    sonuc = yetki_regresyonu(kayitlar)
    sonuc["tutarli"] = sorted(x["vaka_id"] for x in kayitlar if x["beklenen"] == x["karar"])
    return sonuc
for ad, mutant in [("reddedip çalışan bypass'ı düşüren", m_calisma), ("yanlış retleri gizleyen", m_ret), ("çalışmayı tutarlılıkta yok sayan", m_tutarli)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_19 as deney
import tempfile,secrets,json
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('kimlik_ref','nesne_ref','rapor_ref')), 'laboratuvar/gerçek ölçüm yamalanmamalı'):stop()
for i in range(3):
    user='u-'+secrets.token_hex(3);oid='d-'+secrets.token_hex(3);o={'id':oid,'sahip':user,'paylasim':['diger']}
    if not ok(nesne_yetki(user,o,'sil',{'nesne_id':oid,'eylem':'sil'})==deney.nesne_ref(user,o,'sil',{'nesne_id':oid,'eylem':'sil'}),'yeni nesnede işlem bağlı onay'):stop()
    if not ok(kimlik_bagla({'kullanici':user,'dogrulanmis':True},{'kullanici':'baska','eylem':'oku'})=={'izinli':False,'neden':'kimlik-uyusmazligi'},'yeni oturumda kimlik eşleşmesi'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_auth19_') as tmp:
    p=Path(tmp)/'istekler.json';p.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    r=deney.deney(kimlik_bagla,nesne_yetki,yetki_regresyonu,p,Path(tmp)/'deney')
    for k,v in r['kontroller'].items():ok(v,'gerçek deney: '+k)
    accepted=all(r['kontroller'].values());ai_lab.kanit_yaz('saldiri-19-auth',dict(r,kabul=accepted));ok(accepted,'oturum/nesne kapısı gerçek SQLite etkisini denetler; saldırı başarısı şart değil')

```

```solution
import ai_lab
def kimlik_bagla(oturum, cagri):
    if not isinstance(oturum, dict) or set(oturum) != {"kullanici", "dogrulanmis"}:
        raise ValueError("oturum şeması geçersiz")
    if not all((isinstance(oturum["kullanici"], str), bool(oturum["kullanici"]), isinstance(oturum["dogrulanmis"], bool))):
        raise ValueError("oturum alanları geçersiz")
    if not isinstance(cagri, dict) or set(cagri) != {"kullanici", "eylem"}:
        raise ValueError("çağrı şeması geçersiz")
    if not all((isinstance(cagri["kullanici"], str), bool(cagri["kullanici"]), cagri["eylem"] in ("oku", "yaz", "paylas"))):
        raise ValueError("çağrı alanları geçersiz")
    if not oturum["dogrulanmis"]:
        return {"izinli": False, "neden": "oturum-dogrulanmamis"}
    if cagri["kullanici"] != oturum["kullanici"]:
        return {"izinli": False, "neden": "kimlik-uyusmazligi"}
    return {"izinli": True, "neden": "bagli"}

def nesne_yetki(kullanici, nesne, eylem, onay):
    if not isinstance(kullanici, str) or not kullanici:
        raise ValueError("kullanıcı geçersiz")
    if not isinstance(nesne, dict) or set(nesne) != {"id", "sahip", "paylasim"}:
        raise ValueError("nesne şeması geçersiz")
    if not all((isinstance(nesne["id"], str), bool(nesne["id"]), isinstance(nesne["sahip"], str), bool(nesne["sahip"]), isinstance(nesne["paylasim"], list))):
        raise ValueError("nesne alanları geçersiz")
    if not all(isinstance(x, str) and bool(x) for x in nesne["paylasim"]) or len(nesne["paylasim"]) != len(set(nesne["paylasim"])):
        raise ValueError("paylaşım listesi geçersiz")
    if eylem not in ("oku", "yaz", "sil"):
        raise ValueError("eylem geçersiz")
    if onay is not None and (not isinstance(onay, dict) or set(onay) != {"nesne_id", "eylem"}):
        raise ValueError("onay şeması geçersiz")
    sahip = kullanici == nesne["sahip"]
    if eylem == "oku":
        izinli = sahip or kullanici in nesne["paylasim"]
        return {"izinli": izinli, "neden": "izinli" if izinli else "nesne-erisimi-yok"}
    if not sahip:
        return {"izinli": False, "neden": "sahiplik-gerekli"}
    if eylem == "yaz":
        return {"izinli": True, "neden": "izinli"}
    gecerli_onay = onay == {"nesne_id": nesne["id"], "eylem": "sil"}
    return {"izinli": gecerli_onay, "neden": "izinli" if gecerli_onay else "islem-onayi-gerekli"}

def yetki_regresyonu(kayitlar):
    vakalar = set()
    sonuc = {"vaka": 0, "karar_bypassi": [], "calisma_bypassi": [], "yanlis_ret": [], "tutarli": []}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "beklenen", "karar", "calistirildi"}:
            raise ValueError("kayıt şeması geçersiz")
        if not all((isinstance(kayit["vaka_id"], str), bool(kayit["vaka_id"]), kayit["vaka_id"] not in vakalar, kayit["beklenen"] in ("izinli", "reddet"), kayit["karar"] in ("izinli", "reddet"), isinstance(kayit["calistirildi"], bool))):
            raise ValueError("kayıt alanları geçersiz")
        vakalar.add(kayit["vaka_id"])
        if kayit["beklenen"] == "reddet" and kayit["karar"] == "izinli":
            sonuc["karar_bypassi"].append(kayit["vaka_id"])
        if kayit["beklenen"] == "reddet" and kayit["calistirildi"]:
            sonuc["calisma_bypassi"].append(kayit["vaka_id"])
        if kayit["beklenen"] == "izinli" and kayit["karar"] == "reddet":
            sonuc["yanlis_ret"].append(kayit["vaka_id"])
        if kayit["beklenen"] == kayit["karar"] and kayit["calistirildi"] == (kayit["beklenen"] == "izinli"):
            sonuc["tutarli"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("karar_bypassi", "calisma_bypassi", "yanlis_ret", "tutarli"):
        sonuc[alan].sort()
    return sonuc
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_19 as deney
    deney.goster(kimlik_bagla,nesne_yetki,yetki_regresyonu)

```

```hint
Kimlik kapısı nesne sahipliğinin yerine geçmez. Silme onayı hem nesne kimliği hem işlemle eşleşmeli. Raporunda izinli karar ile gerçekten çalışan işlemi ayrı ölç; her şeyi reddeden çözüm meşru kontrolleri geçemez.
```
:::
