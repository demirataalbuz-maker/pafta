---
id: ai-guvence-16
title: Gizlilik Tehdit Modeli ve Bilgi Sızdıran Kanıtlar
summary: Varlık, çıktı kanalı ve saldırgan bilgisini tanımla; üyelik çıkarımı sinyalini taban doğrulukla karşılaştır.
timeout: 45
---

::: anlat Gizlilik riski varlık ve erişimle tanımlanır
Tehdit modelinde korunacak varlıklar, modelin görünür çıktı kanalları ve saldırganın önceden bildikleri açıkça yazılır. Metin, olasılık veya embedding çıktısı aynı bilgiyi açığa vurmayabilir; mimari bilmek ile örnek veriye sahip olmak da aynı varsayım değildir.

Bu derste gerçek kişisel veri, eğitim kaydı, model veya sorgu API'si kullanılmaz. Bütün üyelik etiketleri ve ölçümler sentetik, deterministik fixture olarak verilir. Amaç tehdit varsayımlarını ve kanıtları denetlenebilir biçimde kaydetmektir.
:::

::: anlat Doğruluk tek başına bilgi sızıntısı kanıtı değildir
Üyelik çıkarımında tahminler TP, FP, TN ve FN olarak sayılır. Üye doğru tahmin oranı ile üye olmayanların yanlış üye tahmin oranı arasındaki fark, bu derste avantaj olarak kullanılır. Paydası sıfır olan oran `0.0` kabul edilir.

Bir deneyin doğruluğu, sınıf dağılımından kaynaklanan taban doğrulukla karşılaştırılmalıdır. Kanıt bayrağı için avantaj eşiğe eşit veya büyük, doğruluk ise taban doğruluktan katı biçimde büyük olmalıdır. Bu ölçüm kesin sızıntı hükmü değil, ek inceleme gerektiren bir sinyaldir.
:::

::: tahmin Üyelik avantajı ve kanıt bayrağını tahmin et
Üç çıktı satırını yaz:

```python
print(round(0.75 - 0.25, 6))
print(round(2 / 3, 6))
print(0.4 >= 0.3 and 0.7 > 0.6)
```

???

```cikti
0.5
0.666667
True
```

İlk satır üyelik avantajını, ikinci satır doğruluğu, üçüncü satır avantaj ve taban koşullarının birlikte sağlanmasını gösterir.
:::

::: gorev 1 · Gizlilik tehdit modelini doğrula
`tehdit_modeli_dogrula(model)` işlevini yaz. Model tam olarak `id`, `varliklar`, `cikti_kanallari`, `saldirgan_bilgisi` alanlarını taşır. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir.

Üç alan da boş olmayan, yinelenmeyen string listeleridir. Varlıklar yalnız `egitim_verisi`, `model_parametreleri`, `kullanici_girdisi`; çıktılar yalnız `metin`, `olasilik`, `embedding`; saldırgan bilgisi yalnız `mimari`, `ornek_veri`, `sorgu_erisimi` içerebilir. Geçersiz veride `ValueError` yükselt. Aynı alanları, listeleri alfabetik sıralanmış bağımsız kopyalarla döndür ve girdiyi değiştirme.

```starter
def tehdit_modeli_dogrula(model):
    return {}
```

```test
import copy
M = {"id": "gizlilik-1", "varliklar": ["kullanici_girdisi", "egitim_verisi"], "cikti_kanallari": ["olasilik", "metin"], "saldirgan_bilgisi": ["sorgu_erisimi", "mimari"]}
BEKLENEN = {"id": "gizlilik-1", "varliklar": ["egitim_verisi", "kullanici_girdisi"], "cikti_kanallari": ["metin", "olasilik"], "saldirgan_bilgisi": ["mimari", "sorgu_erisimi"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(M)
        sonuc = fn(M)
        if sonuc != BEKLENEN or M != once or any(sonuc[k] is M[k] for k in ("varliklar", "cikti_kanallari", "saldirgan_bilgisi")):
            return False
        sinir = {"id": "a" * 64, "varliklar": ["model_parametreleri"], "cikti_kanallari": ["embedding"], "saldirgan_bilgisi": ["ornek_veri"]}
        if fn(sinir) != sinir:
            return False
        tam = dict(sinir, varliklar=["egitim_verisi", "model_parametreleri", "kullanici_girdisi"])
        if fn(tam)["varliklar"] != ["egitim_verisi", "kullanici_girdisi", "model_parametreleri"]:
            return False
        for model in [
            None, [], dict(M, ek=1), dict(M, id=""), dict(M, id="a b"), dict(M, id="a" * 65),
            dict(M, varliklar=[]), dict(M, varliklar=None), dict(M, varliklar={}), dict(M, varliklar=["diger"]),
            dict(M, varliklar=["egitim_verisi", "egitim_verisi"]), dict(M, varliklar=[1]),
            dict(M, cikti_kanallari=[]), dict(M, cikti_kanallari=None), dict(M, cikti_kanallari=["diger"]),
            dict(M, cikti_kanallari=["metin", "metin"]), dict(M, cikti_kanallari=[1]),
            dict(M, saldirgan_bilgisi=[]), dict(M, saldirgan_bilgisi=None), dict(M, saldirgan_bilgisi=["diger"]),
            dict(M, saldirgan_bilgisi=["mimari", "mimari"]), dict(M, saldirgan_bilgisi=[1]),
        ]:
            try:
                fn(model)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(tehdit_modeli_dogrula), "tehdit şeması, izinli değerler, sıralama ve kopyalar korunmalı")
def m_varlik(model):
    return tehdit_modeli_dogrula(dict(model, varliklar=[]))
def m_cikti(model):
    return tehdit_modeli_dogrula(dict(model, cikti_kanallari=[]))
def m_bilgi(model):
    return tehdit_modeli_dogrula(dict(model, saldirgan_bilgisi=[]))
for ad, mutant in [("varlıkları silen", m_varlik), ("çıktıları silen", m_cikti), ("saldırgan bilgisini silen", m_bilgi)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def tehdit_modeli_dogrula(model):
    import re
    if not isinstance(model, dict):
        raise ValueError("model sözlük olmalı")
    if set(model) != {"id", "varliklar", "cikti_kanallari", "saldirgan_bilgisi"}:
        raise ValueError("model şeması geçersiz")
    if not isinstance(model["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", model["id"]):
        raise ValueError("kimlik geçersiz")
    izinler = {
        "varliklar": {"egitim_verisi", "model_parametreleri", "kullanici_girdisi"},
        "cikti_kanallari": {"metin", "olasilik", "embedding"},
        "saldirgan_bilgisi": {"mimari", "ornek_veri", "sorgu_erisimi"},
    }
    for alan, izinli in izinler.items():
        degerler = model[alan]
        if not isinstance(degerler, list):
            raise ValueError(alan + " liste olmalı")
        if not degerler:
            raise ValueError(alan + " boş olamaz")
        if any(not isinstance(deger, str) for deger in degerler):
            raise ValueError(alan + " string listesi olmalı")
        if len(set(degerler)) != len(degerler):
            raise ValueError(alan + " yinelenemez")
        if not set(degerler) <= izinli:
            raise ValueError(alan + " izinli değerler dışında")
    return {"id": model["id"], "varliklar": sorted(model["varliklar"]), "cikti_kanallari": sorted(model["cikti_kanallari"]), "saldirgan_bilgisi": sorted(model["saldirgan_bilgisi"])}
```

```hint
Her listenin türünü, boşluğunu, tekrarını ve izinli kümesini ayrı doğrula. Çıktıda `sorted` ile yeni listeler üret.
```
:::

::: gorev 2 · Üyelik çıkarımı kanıtını ölç
`uyelik_kaniti_olc(kayitlar)` işlevini yaz. Kayıtlar boş olmayan listedir; her kayıt tam olarak `id`, `uye`, `tahmin_uye` alanlarını taşır. Kimlik ilk görevdeki biçimdedir ve yinelenemez. Diğer iki alan bool olmalıdır. Geçersiz veride `ValueError` yükselt.

`{"toplam":N,"tp":N,"fp":N,"tn":N,"fn":N,"dogruluk":X,"avantaj":X}` döndür. Doğruluk `(TP+TN)/toplam`; avantaj `TP/(TP+FN)-FP/(FP+TN)` olur. Paydası sıfır olan oran `0.0` kabul edilir. İki ölçümü de altı ondalık basamağa yuvarla ve girdiyi değiştirme.

```starter
def uyelik_kaniti_olc(kayitlar):
    return {}
```

```test
import copy
K = [
    {"id": "u-1", "uye": True, "tahmin_uye": True},
    {"id": "u-2", "uye": False, "tahmin_uye": True},
    {"id": "u-3", "uye": False, "tahmin_uye": False},
    {"id": "u-4", "uye": True, "tahmin_uye": False},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != {"toplam": 4, "tp": 1, "fp": 1, "tn": 1, "fn": 1, "dogruluk": 0.5, "avantaj": 0.0} or K != once:
            return False
        yuvarla = fn(K + [
            {"id": "u-5", "uye": True, "tahmin_uye": True},
            {"id": "u-6", "uye": False, "tahmin_uye": False},
        ])
        if yuvarla["dogruluk"] != 0.666667 or yuvarla["avantaj"] != 0.333333:
            return False
        sadece_uye = fn([{"id": "u", "uye": True, "tahmin_uye": True}])
        if sadece_uye["avantaj"] != 1 or sadece_uye["dogruluk"] != 1:
            return False
        sadece_dis = fn([{"id": "d", "uye": False, "tahmin_uye": False}])
        if sadece_dis["avantaj"] != 0:
            return False
        for kayitlar in [
            None, {}, [], [None], [dict(K[0], ek=1)], [K[0], K[0]],
            [dict(K[0], id="a b")], [dict(K[0], id="a" * 65)], [dict(K[0], id=None)],
            [dict(K[0], uye=1)], [dict(K[0], uye="true")], [dict(K[0], uye=None)],
            [dict(K[0], tahmin_uye=1)], [dict(K[0], tahmin_uye="true")], [dict(K[0], tahmin_uye=None)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(uyelik_kaniti_olc), "üyelik sayımları, doğruluk, avantaj ve sıfır payda korunmalı")
def m_uye(kayitlar):
    return uyelik_kaniti_olc([dict(x, uye=False) for x in kayitlar])
def m_tahmin(kayitlar):
    return uyelik_kaniti_olc([dict(x, tahmin_uye=False) for x in kayitlar])
def m_id(kayitlar):
    return uyelik_kaniti_olc([dict(x, id="u") for x in kayitlar])
for ad, mutant in [("üyeliği silen", m_uye), ("tahminleri silen", m_tahmin), ("kimlikleri birleştiren", m_id)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def uyelik_kaniti_olc(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    idler = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "uye", "tahmin_uye"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["id"], str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["id"]):
            raise ValueError("kimlik geçersiz")
        if kayit["id"] in idler:
            raise ValueError("kimlik yinelenemez")
        if not isinstance(kayit["uye"], bool):
            raise ValueError("üyelik bool olmalı")
        if not isinstance(kayit["tahmin_uye"], bool):
            raise ValueError("tahmin bool olmalı")
        idler.add(kayit["id"])
    tp = sum(1 for x in kayitlar if x["uye"] and x["tahmin_uye"])
    fp = sum(1 for x in kayitlar if not x["uye"] and x["tahmin_uye"])
    tn = sum(1 for x in kayitlar if not x["uye"] and not x["tahmin_uye"])
    fn = sum(1 for x in kayitlar if x["uye"] and not x["tahmin_uye"])
    tpr = tp / (tp + fn) if tp + fn > 0 else 0.0
    fpr = fp / (fp + tn) if fp + tn > 0 else 0.0
    return {"toplam": len(kayitlar), "tp": tp, "fp": fp, "tn": tn, "fn": fn, "dogruluk": round((tp + tn) / len(kayitlar), 6), "avantaj": round(tpr - fpr, 6)}
```

```hint
Dört kararı say, sonra iki oranın paydasını ayrı ele al. Avantaj üye yakalama oranı eksi yanlış üye alarmıdır.
```
:::

::: gorev 3 · Kanıtı taban doğrulukla karşılaştır
`gizlilik_kanit_raporu(kayitlar, avantaj_esik)` işlevini yaz. Kayıtlar boş olmayan listedir; her kayıt tam olarak `deney`, `dogruluk`, `taban_dogrulugu`, `avantaj` alanlarını taşır. Deney ilk görevdeki kimlik biçimindedir. Doğruluk, taban ve eşik bool olmayan sonlu sayı ve `[0,1]`; avantaj bool olmayan sonlu sayı ve `[-1,1]` aralığındadır. Geçersiz veride `ValueError` yükselt.

Her deneyin üç ortalamasını altı ondalık basamağa yuvarla. Ham avantaj eşiğe eşit veya büyük ve ham doğruluk ham tabandan katı büyükse `kanit=True` olur. Kanıtlı deneylerden en yüksek ham avantaj, eşitlikte en yüksek ham doğruluk, sonra alfabetik ad seçilir. `{"satirlar":[{"deney":D,"dogruluk":X,"taban_dogrulugu":X,"avantaj":X,"kanit":BOOL},...],"secilen":D veya None}` döndür. Satırları deney adına göre sırala; uygun yoksa `None` döndür ve girdiyi değiştirme.

```starter
def gizlilik_kanit_raporu(kayitlar, avantaj_esik):
    return {}
```

```test
import copy
K = [
    {"deney": "olasilik", "dogruluk": 0.8, "taban_dogrulugu": 0.6, "avantaj": 0.4},
    {"deney": "metin", "dogruluk": 0.7, "taban_dogrulugu": 0.6, "avantaj": 0.1},
    {"deney": "tabanli", "dogruluk": 0.6, "taban_dogrulugu": 0.6, "avantaj": 0.9},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        sonuc = fn(K, 0.3)
        if K != once or sonuc["secilen"] != "olasilik" or [x["kanit"] for x in sonuc["satirlar"]] != [False, True, False]:
            return False
        esikte = fn(K, 0.4)
        if esikte["secilen"] != "olasilik" or esikte["satirlar"][0]["kanit"]:
            return False
        if fn(K, 1)["secilen"] is not None:
            return False
        yuvarla = fn([
            {"deney": "a", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": 1},
            {"deney": "a", "dogruluk": 0, "taban_dogrulugu": 0, "avantaj": 0},
            {"deney": "a", "dogruluk": 0, "taban_dogrulugu": 0, "avantaj": 0},
        ], 0)
        if yuvarla["satirlar"][0] != {"deney": "a", "dogruluk": 0.333333, "taban_dogrulugu": 0.0, "avantaj": 0.333333, "kanit": True}:
            return False
        taban_yuvarla = fn([
            {"deney": "b", "dogruluk": 1, "taban_dogrulugu": 1, "avantaj": 1},
            {"deney": "b", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": 1},
            {"deney": "b", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": 1},
        ], 0)
        if taban_yuvarla["satirlar"][0]["taban_dogrulugu"] != 0.333333:
            return False
        sinir = fn([{"deney": "a", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": -1}], 0)
        if sinir["satirlar"][0]["avantaj"] != -1 or sinir["secilen"] is not None:
            return False
        for kayitlar, esik in [
            (None, 0.3), (K, None), ({}, 0.3), ([], 0.3), ([None], 0.3), ([dict(K[0], ek=1)], 0.3),
            ([dict(K[0], deney="a b")], 0.3), ([dict(K[0], deney="a" * 65)], 0.3),
            ([dict(K[0], dogruluk=True)], 0.3), ([dict(K[0], dogruluk="0.8")], 0.3), ([dict(K[0], dogruluk=float("nan"))], 0.3),
            ([dict(K[0], dogruluk=-0.1)], 0.3), ([dict(K[0], dogruluk=1.1)], 0.3),
            ([dict(K[0], taban_dogrulugu=True)], 0.3), ([dict(K[0], taban_dogrulugu=-0.1)], 0.3), ([dict(K[0], taban_dogrulugu=1.1)], 0.3),
            ([dict(K[0], avantaj=True)], 0.3), ([dict(K[0], avantaj="0.4")], 0.3), ([dict(K[0], avantaj=float("inf"))], 0.3),
            ([dict(K[0], avantaj=-1.1)], 0.3), ([dict(K[0], avantaj=1.1)], 0.3),
            (K, True), (K, "0.3"), (K, float("nan")), (K, float("inf")), (K, -0.1), (K, 1.1),
        ]:
            try:
                fn(kayitlar, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(gizlilik_kanit_raporu), "taban karşılaştırması, avantaj eşiği ve seçim korunmalı")
def m_avantaj(kayitlar, esik):
    return gizlilik_kanit_raporu([dict(x, avantaj=0) for x in kayitlar], esik)
def m_dogruluk(kayitlar, esik):
    return gizlilik_kanit_raporu([dict(x, dogruluk=0) for x in kayitlar], esik)
def m_taban(kayitlar, esik):
    return gizlilik_kanit_raporu([dict(x, taban_dogrulugu=1) for x in kayitlar], esik)
for ad, mutant in [("avantajı silen", m_avantaj), ("doğruluğu silen", m_dogruluk), ("tabanı değiştiren", m_taban)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def gizlilik_kanit_raporu(kayitlar, avantaj_esik):
    import math
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    if isinstance(avantaj_esik, bool):
        raise ValueError("eşik sayı olmalı")
    if not isinstance(avantaj_esik, (int, float)):
        raise ValueError("eşik sayı olmalı")
    if not math.isfinite(avantaj_esik):
        raise ValueError("eşik sonlu olmalı")
    if avantaj_esik < 0 or avantaj_esik > 1:
        raise ValueError("eşik aralık dışında")
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"deney", "dogruluk", "taban_dogrulugu", "avantaj"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["deney"], str):
            raise ValueError("deney string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["deney"]):
            raise ValueError("deney geçersiz")
        for alan in ("dogruluk", "taban_dogrulugu", "avantaj"):
            deger = kayit[alan]
            if isinstance(deger, bool):
                raise ValueError("ölçüm sayı olmalı")
            if not isinstance(deger, (int, float)):
                raise ValueError("ölçüm sayı olmalı")
            if not math.isfinite(deger):
                raise ValueError("ölçüm sonlu olmalı")
            alt = -1 if alan == "avantaj" else 0
            if deger < alt or deger > 1:
                raise ValueError("ölçüm aralık dışında")
    satirlar = []
    for deney in sorted({x["deney"] for x in kayitlar}):
        grup = [x for x in kayitlar if x["deney"] == deney]
        dogruluk = sum(x["dogruluk"] for x in grup) / len(grup)
        taban = sum(x["taban_dogrulugu"] for x in grup) / len(grup)
        avantaj = sum(x["avantaj"] for x in grup) / len(grup)
        satirlar.append({"deney": deney, "dogruluk": round(dogruluk, 6), "taban_dogrulugu": round(taban, 6), "avantaj": round(avantaj, 6), "kanit": avantaj >= avantaj_esik and dogruluk > taban, "_dogruluk": dogruluk, "_avantaj": avantaj})
    kanitlar = [x for x in satirlar if x["kanit"]]
    secilen = min(kanitlar, key=lambda x: (-x["_avantaj"], -x["_dogruluk"], x["deney"]))["deney"] if kanitlar else None
    for satir in satirlar:
        del satir["_dogruluk"]
        del satir["_avantaj"]
    return {"satirlar": satirlar, "secilen": secilen}
```

```hint
Kanit ve seçim kararlarını ham ortalamalarla ver. Avantaj eşiğini ve doğruluğun tabanı aşmasını iki ayrı koşul olarak uygula.
```
:::


::: anlat Gerçek model olasılıklarından gizlilik kanıtı çıkar
Ham sentetik ayar aynı Pafta sunucusunda `/data/ai-guvence-16-gizlilik.txt` adresindedir. Markdownrenderer linkleri tıklanabilir yapmaz;sunucuadresine bu yolu yaz. Çalıştır ayrı kalıcı `calisma/ai-guvence-16/gizlilik.json` kopyasının yolunu/içeriğini gösterir. Dış editör/Python ile seed ve örnek sayısını değiştirip yeniden Çalıştır;değişikliğin korunur. Test ayrı görülmemiş seed kullanır.

Bu deneyde Qwen yerine CPUda küçük bir PyTorch sınıflandırıcı gerçekten autograd ile eğitilir. Rastgele özellik/etiketler sentetiktir,modelin logits/olasılıkları gerçek inference çıktısıdır. Üyelik eşiği ayrı shadow modelinin üye/üyeolmayan örneklerinden seçilir;hedefmodel üyeliği eşikayarlamak için kullanılmaz. Üç bağımsız tekrar yapılır. Öğrenci gerçekhedefolasılıklarının ürettiği üyelik kayıtlarını ölçer,0.5çoğunluk tabanıyla ve TPR-FPRavantajıyla raporlar. Pozitifavantaj veya saldırıbaşarısı geçme şartı değildir.

Tehditmodeli gerçek varlığı(eğitimverisi/modelparametreleri),erişilenkanıtı(olasılık),saldırganbilgisini tanımlar. Bu ölçüm sohbetmodellerinin veya gerçekkişiselverinin gizliliği hakkında genelgaranti değildir. Gerçek eğitimloss/logit/olasılık/üyelik kaydı/sürüm/cihaz/ağırlıkhashi kanıttadır. Testgeçici ağırlıkları kapanınca silinir;JSONizleri kalır. Çalıştırda kendi deney klasöründeki ağırlıkları inceleyebilirsin. Kullanıcıverisi silinmez,yeni indirme yapılmaz.
:::

::: gorev Gerçek deney · Gizlilik iddiasını gerçek autograd modelinden ölç
Önceki `tehdit_modeli_dogrula`,`uyelik_kaniti_olc`,`gizlilik_kanit_raporu` işlevlerini birleştir. Kontrol Et saf sözleşmelerden sonra ayrı shadow/targetmodellerini gerçekten eğitip modelçıktılarından hesaplamanı sınar. Dengesiz veride doğruluğu üyelikavantajı diye yorumlama.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import ai_lab
def tehdit_modeli_dogrula(model):return {}
def uyelik_kaniti_olc(kayitlar):return {}
def gizlilik_kanit_raporu(kayitlar,avantaj_esik):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_guvence_16 as deney
    deney.goster(tehdit_modeli_dogrula,uyelik_kaniti_olc,gizlilik_kanit_raporu)

```

```test
import copy
M = {"id": "gizlilik-1", "varliklar": ["kullanici_girdisi", "egitim_verisi"], "cikti_kanallari": ["olasilik", "metin"], "saldirgan_bilgisi": ["sorgu_erisimi", "mimari"]}
BEKLENEN = {"id": "gizlilik-1", "varliklar": ["egitim_verisi", "kullanici_girdisi"], "cikti_kanallari": ["metin", "olasilik"], "saldirgan_bilgisi": ["mimari", "sorgu_erisimi"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(M)
        sonuc = fn(M)
        if sonuc != BEKLENEN or M != once or any(sonuc[k] is M[k] for k in ("varliklar", "cikti_kanallari", "saldirgan_bilgisi")):
            return False
        sinir = {"id": "a" * 64, "varliklar": ["model_parametreleri"], "cikti_kanallari": ["embedding"], "saldirgan_bilgisi": ["ornek_veri"]}
        if fn(sinir) != sinir:
            return False
        tam = dict(sinir, varliklar=["egitim_verisi", "model_parametreleri", "kullanici_girdisi"])
        if fn(tam)["varliklar"] != ["egitim_verisi", "kullanici_girdisi", "model_parametreleri"]:
            return False
        for model in [
            None, [], dict(M, ek=1), dict(M, id=""), dict(M, id="a b"), dict(M, id="a" * 65),
            dict(M, varliklar=[]), dict(M, varliklar=None), dict(M, varliklar={}), dict(M, varliklar=["diger"]),
            dict(M, varliklar=["egitim_verisi", "egitim_verisi"]), dict(M, varliklar=[1]),
            dict(M, cikti_kanallari=[]), dict(M, cikti_kanallari=None), dict(M, cikti_kanallari=["diger"]),
            dict(M, cikti_kanallari=["metin", "metin"]), dict(M, cikti_kanallari=[1]),
            dict(M, saldirgan_bilgisi=[]), dict(M, saldirgan_bilgisi=None), dict(M, saldirgan_bilgisi=["diger"]),
            dict(M, saldirgan_bilgisi=["mimari", "mimari"]), dict(M, saldirgan_bilgisi=[1]),
        ]:
            try:
                fn(model)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(tehdit_modeli_dogrula), "tehdit şeması, izinli değerler, sıralama ve kopyalar korunmalı")
def m_varlik(model):
    return tehdit_modeli_dogrula(dict(model, varliklar=[]))
def m_cikti(model):
    return tehdit_modeli_dogrula(dict(model, cikti_kanallari=[]))
def m_bilgi(model):
    return tehdit_modeli_dogrula(dict(model, saldirgan_bilgisi=[]))
for ad, mutant in [("varlıkları silen", m_varlik), ("çıktıları silen", m_cikti), ("saldırgan bilgisini silen", m_bilgi)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
K = [
    {"id": "u-1", "uye": True, "tahmin_uye": True},
    {"id": "u-2", "uye": False, "tahmin_uye": True},
    {"id": "u-3", "uye": False, "tahmin_uye": False},
    {"id": "u-4", "uye": True, "tahmin_uye": False},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != {"toplam": 4, "tp": 1, "fp": 1, "tn": 1, "fn": 1, "dogruluk": 0.5, "avantaj": 0.0} or K != once:
            return False
        yuvarla = fn(K + [
            {"id": "u-5", "uye": True, "tahmin_uye": True},
            {"id": "u-6", "uye": False, "tahmin_uye": False},
        ])
        if yuvarla["dogruluk"] != 0.666667 or yuvarla["avantaj"] != 0.333333:
            return False
        sadece_uye = fn([{"id": "u", "uye": True, "tahmin_uye": True}])
        if sadece_uye["avantaj"] != 1 or sadece_uye["dogruluk"] != 1:
            return False
        sadece_dis = fn([{"id": "d", "uye": False, "tahmin_uye": False}])
        if sadece_dis["avantaj"] != 0:
            return False
        for kayitlar in [
            None, {}, [], [None], [dict(K[0], ek=1)], [K[0], K[0]],
            [dict(K[0], id="a b")], [dict(K[0], id="a" * 65)], [dict(K[0], id=None)],
            [dict(K[0], uye=1)], [dict(K[0], uye="true")], [dict(K[0], uye=None)],
            [dict(K[0], tahmin_uye=1)], [dict(K[0], tahmin_uye="true")], [dict(K[0], tahmin_uye=None)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(uyelik_kaniti_olc), "üyelik sayımları, doğruluk, avantaj ve sıfır payda korunmalı")
def m_uye(kayitlar):
    return uyelik_kaniti_olc([dict(x, uye=False) for x in kayitlar])
def m_tahmin(kayitlar):
    return uyelik_kaniti_olc([dict(x, tahmin_uye=False) for x in kayitlar])
def m_id(kayitlar):
    return uyelik_kaniti_olc([dict(x, id="u") for x in kayitlar])
for ad, mutant in [("üyeliği silen", m_uye), ("tahminleri silen", m_tahmin), ("kimlikleri birleştiren", m_id)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
K = [
    {"deney": "olasilik", "dogruluk": 0.8, "taban_dogrulugu": 0.6, "avantaj": 0.4},
    {"deney": "metin", "dogruluk": 0.7, "taban_dogrulugu": 0.6, "avantaj": 0.1},
    {"deney": "tabanli", "dogruluk": 0.6, "taban_dogrulugu": 0.6, "avantaj": 0.9},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        sonuc = fn(K, 0.3)
        if K != once or sonuc["secilen"] != "olasilik" or [x["kanit"] for x in sonuc["satirlar"]] != [False, True, False]:
            return False
        esikte = fn(K, 0.4)
        if esikte["secilen"] != "olasilik" or esikte["satirlar"][0]["kanit"]:
            return False
        if fn(K, 1)["secilen"] is not None:
            return False
        yuvarla = fn([
            {"deney": "a", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": 1},
            {"deney": "a", "dogruluk": 0, "taban_dogrulugu": 0, "avantaj": 0},
            {"deney": "a", "dogruluk": 0, "taban_dogrulugu": 0, "avantaj": 0},
        ], 0)
        if yuvarla["satirlar"][0] != {"deney": "a", "dogruluk": 0.333333, "taban_dogrulugu": 0.0, "avantaj": 0.333333, "kanit": True}:
            return False
        taban_yuvarla = fn([
            {"deney": "b", "dogruluk": 1, "taban_dogrulugu": 1, "avantaj": 1},
            {"deney": "b", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": 1},
            {"deney": "b", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": 1},
        ], 0)
        if taban_yuvarla["satirlar"][0]["taban_dogrulugu"] != 0.333333:
            return False
        sinir = fn([{"deney": "a", "dogruluk": 1, "taban_dogrulugu": 0, "avantaj": -1}], 0)
        if sinir["satirlar"][0]["avantaj"] != -1 or sinir["secilen"] is not None:
            return False
        for kayitlar, esik in [
            (None, 0.3), (K, None), ({}, 0.3), ([], 0.3), ([None], 0.3), ([dict(K[0], ek=1)], 0.3),
            ([dict(K[0], deney="a b")], 0.3), ([dict(K[0], deney="a" * 65)], 0.3),
            ([dict(K[0], dogruluk=True)], 0.3), ([dict(K[0], dogruluk="0.8")], 0.3), ([dict(K[0], dogruluk=float("nan"))], 0.3),
            ([dict(K[0], dogruluk=-0.1)], 0.3), ([dict(K[0], dogruluk=1.1)], 0.3),
            ([dict(K[0], taban_dogrulugu=True)], 0.3), ([dict(K[0], taban_dogrulugu=-0.1)], 0.3), ([dict(K[0], taban_dogrulugu=1.1)], 0.3),
            ([dict(K[0], avantaj=True)], 0.3), ([dict(K[0], avantaj="0.4")], 0.3), ([dict(K[0], avantaj=float("inf"))], 0.3),
            ([dict(K[0], avantaj=-1.1)], 0.3), ([dict(K[0], avantaj=1.1)], 0.3),
            (K, True), (K, "0.3"), (K, float("nan")), (K, float("inf")), (K, -0.1), (K, 1.1),
        ]:
            try:
                fn(kayitlar, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(gizlilik_kanit_raporu), "taban karşılaştırması, avantaj eşiği ve seçim korunmalı")
def m_avantaj(kayitlar, esik):
    return gizlilik_kanit_raporu([dict(x, avantaj=0) for x in kayitlar], esik)
def m_dogruluk(kayitlar, esik):
    return gizlilik_kanit_raporu([dict(x, dogruluk=0) for x in kayitlar], esik)
def m_taban(kayitlar, esik):
    return gizlilik_kanit_raporu([dict(x, taban_dogrulugu=1) for x in kayitlar], esik)
for ad, mutant in [("avantajı silen", m_avantaj), ("doğruluğu silen", m_dogruluk), ("tabanı değiştiren", m_taban)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_guvence_16 as deney
import tempfile,secrets,json
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('olcu_ref','rapor_ref','_train')),'gerçek deney yamalanmamalı'):stop()
probe=[{'id':'u'+str(i),'uye':i<4,'tahmin_uye':i%3==0} for i in range(12)]
if not ok(uyelik_kaniti_olc(probe)==deney.olcu_ref(probe),'yeni dengesiz üyelikte TPR-FPR'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_privacy16_') as tmp:
    p=Path(tmp)/'ayar.json';p.write_text(json.dumps({'seed':secrets.randbelow(1000000),'ornek':32}),encoding='utf-8')
    r=deney.deney(tehdit_modeli_dogrula,uyelik_kaniti_olc,gizlilik_kanit_raporu,p,Path(tmp)/'deney')
    for k,v in r['kontroller'].items():ok(v,'gerçek deney: '+k)
    accepted=all(r['kontroller'].values());ai_lab.kanit_yaz('guvence-16-gizlilik',dict(r,kabul=accepted));ok(accepted,'gerçek autograd/modelolasılığı/üyelikölçümü; saldırıbaşarısı şart değil')

```

```solution
import ai_lab
def tehdit_modeli_dogrula(model):
    import re
    if not isinstance(model, dict):
        raise ValueError("model sözlük olmalı")
    if set(model) != {"id", "varliklar", "cikti_kanallari", "saldirgan_bilgisi"}:
        raise ValueError("model şeması geçersiz")
    if not isinstance(model["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", model["id"]):
        raise ValueError("kimlik geçersiz")
    izinler = {
        "varliklar": {"egitim_verisi", "model_parametreleri", "kullanici_girdisi"},
        "cikti_kanallari": {"metin", "olasilik", "embedding"},
        "saldirgan_bilgisi": {"mimari", "ornek_veri", "sorgu_erisimi"},
    }
    for alan, izinli in izinler.items():
        degerler = model[alan]
        if not isinstance(degerler, list):
            raise ValueError(alan + " liste olmalı")
        if not degerler:
            raise ValueError(alan + " boş olamaz")
        if any(not isinstance(deger, str) for deger in degerler):
            raise ValueError(alan + " string listesi olmalı")
        if len(set(degerler)) != len(degerler):
            raise ValueError(alan + " yinelenemez")
        if not set(degerler) <= izinli:
            raise ValueError(alan + " izinli değerler dışında")
    return {"id": model["id"], "varliklar": sorted(model["varliklar"]), "cikti_kanallari": sorted(model["cikti_kanallari"]), "saldirgan_bilgisi": sorted(model["saldirgan_bilgisi"])}

def uyelik_kaniti_olc(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    idler = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "uye", "tahmin_uye"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["id"], str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["id"]):
            raise ValueError("kimlik geçersiz")
        if kayit["id"] in idler:
            raise ValueError("kimlik yinelenemez")
        if not isinstance(kayit["uye"], bool):
            raise ValueError("üyelik bool olmalı")
        if not isinstance(kayit["tahmin_uye"], bool):
            raise ValueError("tahmin bool olmalı")
        idler.add(kayit["id"])
    tp = sum(1 for x in kayitlar if x["uye"] and x["tahmin_uye"])
    fp = sum(1 for x in kayitlar if not x["uye"] and x["tahmin_uye"])
    tn = sum(1 for x in kayitlar if not x["uye"] and not x["tahmin_uye"])
    fn = sum(1 for x in kayitlar if x["uye"] and not x["tahmin_uye"])
    tpr = tp / (tp + fn) if tp + fn > 0 else 0.0
    fpr = fp / (fp + tn) if fp + tn > 0 else 0.0
    return {"toplam": len(kayitlar), "tp": tp, "fp": fp, "tn": tn, "fn": fn, "dogruluk": round((tp + tn) / len(kayitlar), 6), "avantaj": round(tpr - fpr, 6)}

def gizlilik_kanit_raporu(kayitlar, avantaj_esik):
    import math
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    if not kayitlar:
        raise ValueError("kayıtlar boş olamaz")
    if isinstance(avantaj_esik, bool):
        raise ValueError("eşik sayı olmalı")
    if not isinstance(avantaj_esik, (int, float)):
        raise ValueError("eşik sayı olmalı")
    if not math.isfinite(avantaj_esik):
        raise ValueError("eşik sonlu olmalı")
    if avantaj_esik < 0 or avantaj_esik > 1:
        raise ValueError("eşik aralık dışında")
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"deney", "dogruluk", "taban_dogrulugu", "avantaj"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["deney"], str):
            raise ValueError("deney string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["deney"]):
            raise ValueError("deney geçersiz")
        for alan in ("dogruluk", "taban_dogrulugu", "avantaj"):
            deger = kayit[alan]
            if isinstance(deger, bool):
                raise ValueError("ölçüm sayı olmalı")
            if not isinstance(deger, (int, float)):
                raise ValueError("ölçüm sayı olmalı")
            if not math.isfinite(deger):
                raise ValueError("ölçüm sonlu olmalı")
            alt = -1 if alan == "avantaj" else 0
            if deger < alt or deger > 1:
                raise ValueError("ölçüm aralık dışında")
    satirlar = []
    for deney in sorted({x["deney"] for x in kayitlar}):
        grup = [x for x in kayitlar if x["deney"] == deney]
        dogruluk = sum(x["dogruluk"] for x in grup) / len(grup)
        taban = sum(x["taban_dogrulugu"] for x in grup) / len(grup)
        avantaj = sum(x["avantaj"] for x in grup) / len(grup)
        satirlar.append({"deney": deney, "dogruluk": round(dogruluk, 6), "taban_dogrulugu": round(taban, 6), "avantaj": round(avantaj, 6), "kanit": avantaj >= avantaj_esik and dogruluk > taban, "_dogruluk": dogruluk, "_avantaj": avantaj})
    kanitlar = [x for x in satirlar if x["kanit"]]
    secilen = min(kanitlar, key=lambda x: (-x["_avantaj"], -x["_dogruluk"], x["deney"]))["deney"] if kanitlar else None
    for satir in satirlar:
        del satir["_dogruluk"]
        del satir["_avantaj"]
    return {"satirlar": satirlar, "secilen": secilen}
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_guvence_16 as deney
    deney.goster(tehdit_modeli_dogrula,uyelik_kaniti_olc,gizlilik_kanit_raporu)

```

```hint
Shadoweşikayrı öğrenilir;hedefüyeliği yalnız ölçüm içindir. TPR-FPR ve tabandoğruluk koşullarını ayrı koru. Saldırının kazanması şart değildir.
```
:::
