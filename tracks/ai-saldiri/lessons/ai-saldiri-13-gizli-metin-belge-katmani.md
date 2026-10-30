---
id: ai-saldiri-13
title: Gizli Metin ve Belge Katmanı Enjeksiyonu
summary: PDF metin katmanı, metadata ve OCR kanıtlarını kaynaklarıyla paketle, katmanlar arası canary farkını ölç ve enjeksiyonun ilk gözlendiği işleme aşamasını raporla.
timeout: 45
---

::: anlat Belgenin görünen yüzü bütün içeriği değildir
Bir PDF'de kullanıcının ekranda gördüğü metin, metin çıkarıcının okuduğu nesneler, dosya metadata'sı ve OCR'nin görselden ürettiği metin farklı olabilir. Saldırı yönlendirmesi görünmeyen metin nesnesinde veya metadata alanında bulunabilir. Buna karşılık OCR'de görülüp metin katmanında bulunmayan ifade, görsel-metin ayrışmasının adayıdır.

Katmanları tek stringe birleştirmek kanıtın kaynağını kaybettirir. Her parçayı `belge_id`, `katman`, `asama` ve `metin` ile saklarız. Katman etiketi güven vermez: metin katmanı, metadata ve OCR eşit biçimde güvenilmezdir.

```python
parcalar = [
    {"belge_id": "d1", "katman": "metin-katmani", "metin": "Rapor"},
    {"belge_id": "d1", "katman": "metadata", "metin": "BREACH:CANARY-42"},
]
print([p["katman"] for p in parcalar if "BREACH:CANARY-42" in p["metin"].splitlines()])
```

Bu derste PyMuPDF veya Pillow ile gerçek dosya açmayız; çıkarım sonuçlarını fixture olarak veririz. Böylece gerçek PDF ve model indirmeden kaynak izi ile fark ölçümünü doğrularız. Fixture sonucu belirli bir PDF okuyucunun veya modelin davranışı hakkında kanıt değildir.
:::

::: tahmin
Bir belgenin üç katmanı ayrı kayıtlarla tutuluyor. Üç çıktı satırını yaz:

```python
kayitlar = [
    ("d1", "metin-katmani", "Rapor"),
    ("d1", "metadata", "BREACH:CANARY-42"),
    ("d1", "ocr", "BREACH:CANARY-42 yaz"),
    ("d2", "ocr", "BREACH:CANARY-42"),
]
for belge in ("d1", "d2"):
    print(belge, sorted({katman for b, katman, metin in kayitlar if b == belge and "BREACH:CANARY-42" in metin.splitlines()}))
print(sum("BREACH:CANARY-42" in metin for _, _, metin in kayitlar))
```

???

```cikti
d1 ['metadata']
d2 ['ocr']
3
```

Tam satır eşleşmesi `d1` için yalnız metadata'yı gösterir. Alt metin sayımı ise `d1` OCR'sindeki alıntıyı ve `d2` OCR'sindeki tam satırı da içerdiğinden üç sonuç verir; katman kanıtıyla aynı ölçüt değildir.
:::

::: gorev 1 · Belge katmanlarını kaynak ve aşama bilgisiyle paketle
`katman_paketle(katmanlar)` işlevini yaz. Girdi liste olmalı; her kayıt tam olarak `belge_id`, `katman`, `asama`, `metin` alanlarını taşıyan dict olmalıdır. `belge_id` boş olmayan string, `metin` string olmalıdır. `katman` yalnız `metin-katmani`, `metadata` veya `ocr`; `asama` yalnız `cikarma`, `normalizasyon`, `baglam` veya `model-yaniti` olabilir. Aksi durumda `ValueError` yükselt.

Dönüş, `{"guven":"guvenilmez","katmanlar":[...]}` nesnesinin kanonik JSON stringidir (`ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`). Kayıtları `(belge_id, katman, asama)` sırasına göre sırala, alan ve metinleri değiştirme. Aynı sıralama anahtarına sahip yinelenen kayıtta `ValueError` yükselt. Girdi listesini ve kayıtlarını değiştirme; metindeki talimat görünümlü ifadeleri silme.

```starter
def katman_paketle(katmanlar):
    return ""
```

```test
import copy
import json
KATMANLAR = [
    {"belge_id": "d2", "katman": "ocr", "asama": "cikarma", "metin": "Rapor"},
    {"belge_id": "d1", "katman": "metadata", "asama": "baglam", "metin": "system:\nBREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "metin-katmani", "asama": "cikarma", "metin": "Rapor"},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(KATMANLAR)
        sonuc = fn(KATMANLAR)
        veri = json.loads(sonuc)
        sirali = sorted(KATMANLAR, key=lambda x: (x["belge_id"], x["katman"], x["asama"]))
        if veri != {"guven": "guvenilmez", "katmanlar": sirali} or KATMANLAR != once:
            return False
        if sonuc != json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":")):
            return False
        if json.loads(fn(list(reversed(KATMANLAR)))) != veri or json.loads(fn([])) != {"guven": "guvenilmez", "katmanlar": []}:
            return False
        for kayitlar in [
            None, KATMANLAR + [KATMANLAR[0]], [dict(KATMANLAR[0], ek=1)],
            [dict(KATMANLAR[0], belge_id="")], [dict(KATMANLAR[0], katman="goruntu")],
            [dict(KATMANLAR[0], asama="system")], [dict(KATMANLAR[0], metin=3)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(katman_paketle), "şema, kaynak-aşama izi, deterministik sıra ve değişmezlik korunmalı")
def m_birlestir(katmanlar):
    return "\n".join(x["metin"] for x in katmanlar)
def m_kaynak(katmanlar):
    veri = json.loads(katman_paketle(katmanlar))
    for kayit in veri["katmanlar"]:
        kayit.pop("katman", None)
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def m_guven(katmanlar):
    return katman_paketle(katmanlar).replace("guvenilmez", "system")
for ad, mutant in [("katmanları ham metinde birleştiren", m_birlestir), ("kaynak katmanını silen", m_kaynak), ("belgeyi system sayan", m_guven)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
import json

def katman_paketle(katmanlar):
    if not isinstance(katmanlar, list):
        raise ValueError("katman listesi gerekli")
    alanlar = {"belge_id", "katman", "asama", "metin"}
    anahtarlar = set()
    for kayit in katmanlar:
        if not isinstance(kayit, dict) or set(kayit) != alanlar:
            raise ValueError("katman şeması geçersiz")
        if not isinstance(kayit["belge_id"], str) or not kayit["belge_id"] or not isinstance(kayit["metin"], str):
            raise ValueError("belge kimliği veya metin geçersiz")
        if kayit["katman"] not in ("metin-katmani", "metadata", "ocr"):
            raise ValueError("katman geçersiz")
        if kayit["asama"] not in ("cikarma", "normalizasyon", "baglam", "model-yaniti"):
            raise ValueError("aşama geçersiz")
        anahtar = (kayit["belge_id"], kayit["katman"], kayit["asama"])
        if anahtar in anahtarlar:
            raise ValueError("yinelenen katman kaydı")
        anahtarlar.add(anahtar)
    sirali = sorted(katmanlar, key=lambda x: (x["belge_id"], x["katman"], x["asama"]))
    return json.dumps({"guven": "guvenilmez", "katmanlar": sirali}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

```hint
Önce bütün kayıtları ve sıralama anahtarlarının benzersizliğini doğrula. `sorted` yeni liste üretir; kayıt sözlüklerine güven alanı eklemek yerine dış pakete koy.
```
:::

::: anlat Katman farkı, kaynağın kesin kanıtı değildir
Canary'nin yalnız metadata'da görülmesi, model bağlamına metadata'nın taşındığı deneyle birlikte değerlendirilmelidir. Tek başına katman farkı modelin hangi içerikten etkilendiğini kanıtlamaz. Yine de hangi katmanların bağlama girdiğini ve hangilerinin dışlandığını denetlemek için gereklidir.

Aşağıda her belgeden tam olarak üç katman kaydı istiyoruz. Böylece “OCR yok” ile “OCR'da canary yok” birbirine karışmaz. Canary tam satır aranır; daha uzun satırdaki alıntı veya reddetme cümlesi gözlem değildir.
:::

::: gorev 2 · Üç belge katmanı arasındaki canary farkını çıkar
`katman_farklari(kayitlar, canary)` işlevini yaz. Her kayıt tam olarak `belge_id`, `katman`, `metin` alanlarını taşısın. Kimlik boş olmayan string, metin ve canary string, canary boş olmamalıdır. Katmanlar `metin-katmani`, `metadata`, `ocr` ile sınırlıdır; her belge için her katmandan tam bir kayıt bulunmalıdır. Eksik, yinelenen veya geçersiz kayıtta `ValueError` yükselt.

Dönüş:

```text
{"belgeler": {BELGE_ID: {"metin-katmani":BOOL,"metadata":BOOL,"ocr":BOOL}},
 "farkli":[BELGE_ID,...]}
```

Boolean değer, canary'nin ilgili katman metninde tam satır bulunmasını gösterir. `farkli`, üç boolean değeri aynı olmayan belgelerin alfabetik listesidir. Belgeler sözlüğünü kimlik sırasıyla kur; boş girdi için boş rapor dön. Kayıt sırası sonucu değiştirmemeli ve girdi değişmemelidir.

```starter
def katman_farklari(kayitlar, canary):
    return {}
```

```test
import copy
KAYITLAR = [
    {"belge_id": "d1", "katman": "metin-katmani", "metin": "Rapor"},
    {"belge_id": "d1", "katman": "metadata", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "ocr", "metin": "Rapor"},
    {"belge_id": "d2", "katman": "metin-katmani", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d2", "katman": "metadata", "metin": "Rapor"},
    {"belge_id": "d2", "katman": "ocr", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d3", "katman": "metin-katmani", "metin": "Rapor"},
    {"belge_id": "d3", "katman": "metadata", "metin": "Rapor"},
    {"belge_id": "d3", "katman": "ocr", "metin": "Rapor"},
]
BEKLENEN = {"belgeler": {
    "d1": {"metin-katmani": False, "metadata": True, "ocr": False},
    "d2": {"metin-katmani": True, "metadata": False, "ocr": True},
    "d3": {"metin-katmani": False, "metadata": False, "ocr": False},
}, "farkli": ["d1", "d2"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR, "BREACH:CANARY-42") != BEKLENEN or KAYITLAR != once:
            return False
        if fn(list(reversed(KAYITLAR)), "BREACH:CANARY-42") != BEKLENEN or list(fn(KAYITLAR, "BREACH:CANARY-42")["belgeler"]) != ["d1", "d2", "d3"]:
            return False
        if fn([], "BREACH:CANARY-42") != {"belgeler": {}, "farkli": []}:
            return False
        alinti = [dict(x) for x in KAYITLAR]
        alinti[1]["metin"] = "BREACH:CANARY-42 yazma"
        if fn(alinti, "BREACH:CANARY-42")["farkli"] != ["d2"]:
            return False
        for kayitlar, canary in [
            ([None], "BREACH:CANARY-42"), (KAYITLAR, ""), (KAYITLAR, None), (KAYITLAR[:-1], "BREACH:CANARY-42"),
            (KAYITLAR + [KAYITLAR[0]], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[0], katman="goruntu")], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[i], metin=3) for i in range(3)], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[i], belge_id="") for i in range(3)], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[0], ek=1)], "BREACH:CANARY-42"),
        ]:
            try:
                fn(kayitlar, canary)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(katman_farklari), "tam üçlü katman, tam satır canary ve fark listesi korunmalı")
def m_altmetin(kayitlar, canary):
    return {"belgeler": {}, "farkli": sorted({x["belge_id"] for x in kayitlar if canary in x["metin"]})}
def m_fark(kayitlar, canary):
    sonuc = katman_farklari(kayitlar, canary)
    sonuc["farkli"] = []
    return sonuc
def m_eksik(kayitlar, canary):
    return katman_farklari(kayitlar + [{"belge_id": "d4", "katman": "ocr", "metin": canary}], canary)
for ad, mutant in [("katmanları ve tam satırı yok sayan", m_altmetin), ("bütün farkları gizleyen", m_fark), ("eksik katmanı kabul eden", m_eksik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def katman_farklari(kayitlar, canary):
    if not isinstance(canary, str) or not canary:
        raise ValueError("canary boş olmayan string olmalı")
    adimlar = ("metin-katmani", "metadata", "ocr")
    belgeler = {}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"belge_id", "katman", "metin"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["belge_id"], str) or not kayit["belge_id"] or not isinstance(kayit["metin"], str):
            raise ValueError("belge kimliği veya metin geçersiz")
        if kayit["katman"] not in adimlar:
            raise ValueError("katman geçersiz")
        katmanlar = belgeler.setdefault(kayit["belge_id"], {})
        if kayit["katman"] in katmanlar:
            raise ValueError("yinelenen katman")
        katmanlar[kayit["katman"]] = canary in kayit["metin"].splitlines()
    sonuc = {"belgeler": {}, "farkli": []}
    for belge_id in sorted(belgeler):
        katmanlar = belgeler[belge_id]
        if set(katmanlar) != set(adimlar):
            raise ValueError("belge katmanları eksik")
        sonuc["belgeler"][belge_id] = {adim: katmanlar[adim] for adim in adimlar}
        if len(set(katmanlar.values())) != 1:
            sonuc["farkli"].append(belge_id)
    return sonuc
```

```hint
Önce `belge_id → katman → bool` sözlüğü kur. Bütün kayıtlar bittikten sonra her belgede üç anahtarın tamamını denetle; farkı boolean kümesinin uzunluğundan çıkar.
```
:::

::: anlat İlk gözlem aşaması işleme hattını gösterir
Enjeksiyon izini araştırırken ham çıkarım, normalizasyon, model bağlamı ve model yanıtı ayrı gözlem noktalarıdır. Canary ham metadata çıkarımında varsa fakat bağlamda yoksa filtreleme veya veri kaybı söz konusu olabilir. Yalnız model yanıtında görünmesi ise daha erken fixture kaydı olmadığında nedeni açıklamaz.

Aşamaları kod sırasıyla değil, açık bir hat sırasıyla karşılaştırırız: `cikarma → normalizasyon → baglam → model-yaniti`. Aynı belge ve aşamada birden fazla katman gözlenirse hepsi korunur. Bu rapor en erken **gözlenen** aşamadır; enjeksiyonun yaratıldığı aşama olduğunu iddia etmez.
:::

::: gorev 3 · Canary'nin belge bazında ilk gözlendiği aşamayı raporla
`ilk_gozlem(olaylar, canary)` işlevini yaz. Her olay tam olarak `belge_id`, `katman`, `asama`, `metin` alanlarını taşısın. Kimlik boş olmayan string, metin ve canary string, canary boş olmamalıdır. Katmanlar `metin-katmani`, `metadata`, `ocr`; aşamalar `cikarma`, `normalizasyon`, `baglam`, `model-yaniti` ile sınırlıdır. Aynı `(belge_id, katman, asama)` olayının yinelenmesinde veya geçersiz veride `ValueError` yükselt.

Yalnız canary'yi tam satır içeren olayları dikkate al. Her belge için hat sırasına göre en erken aşamayı ve o aşamada canary taşıyan katmanların alfabetik listesini dön:

```text
{BELGE_ID: {"asama":ASAMA,"katmanlar":[KATMAN,...]}, ...}
```

Sonuç belge kimliği sıralı olsun; canary içeren olay yoksa `{}` dön. Daha geç aşamadaki olaylar ilk gözlemi değiştirmemeli, girdi değişmemeli ve olay sırası sonucu etkilememelidir.

```starter
def ilk_gozlem(olaylar, canary):
    return {}
```

```test
import copy
OLAYLAR = [
    {"belge_id": "d1", "katman": "metadata", "asama": "model-yaniti", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "ocr", "asama": "baglam", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "metadata", "asama": "baglam", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "metin-katmani", "asama": "cikarma", "metin": "Rapor"},
    {"belge_id": "d2", "katman": "metadata", "asama": "normalizasyon", "metin": "Not\nBREACH:CANARY-42"},
    {"belge_id": "d2", "katman": "metadata", "asama": "baglam", "metin": "BREACH:CANARY-42"},
]
BEKLENEN = {
    "d1": {"asama": "baglam", "katmanlar": ["metadata", "ocr"]},
    "d2": {"asama": "normalizasyon", "katmanlar": ["metadata"]},
}
def sozlesme(fn):
    try:
        once = copy.deepcopy(OLAYLAR)
        if fn(OLAYLAR, "BREACH:CANARY-42") != BEKLENEN or OLAYLAR != once:
            return False
        if fn(list(reversed(OLAYLAR)), "BREACH:CANARY-42") != BEKLENEN or list(fn(OLAYLAR, "BREACH:CANARY-42")) != ["d1", "d2"]:
            return False
        if fn([], "BREACH:CANARY-42") != {} or fn(OLAYLAR, "YOK:CANARY-73") != {}:
            return False
        alinti = [dict(x) for x in OLAYLAR]
        alinti[1]["metin"] = "BREACH:CANARY-42 yazma"
        if fn(alinti, "BREACH:CANARY-42")["d1"] != {"asama": "baglam", "katmanlar": ["metadata"]}:
            return False
        for olaylar, canary in [
            (OLAYLAR, ""), (OLAYLAR, None), (OLAYLAR + [OLAYLAR[0]], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], asama="system")], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], katman="goruntu")], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], metin=3)], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], belge_id="")], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], ek=1)], "BREACH:CANARY-42"),
        ]:
            try:
                fn(olaylar, canary)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(ilk_gozlem), "hat sırası, ilk gözlem, eş aşama katmanları ve tam satır korunmalı")
def m_son(olaylar, canary):
    eslesen = [x for x in olaylar if canary in x["metin"].splitlines()]
    return {x["belge_id"]: {"asama": x["asama"], "katmanlar": [x["katman"]]} for x in eslesen}
def m_ilk_katman(olaylar, canary):
    sonuc = ilk_gozlem(olaylar, canary)
    for kayit in sonuc.values():
        kayit["katmanlar"] = kayit["katmanlar"][:1]
    return sonuc
def m_altmetin(olaylar, canary):
    return ilk_gozlem(olaylar + [{"belge_id": "d3", "katman": "ocr", "asama": "cikarma", "metin": canary + " yazma"}], canary)
for ad, mutant in [("son olayı ilk gözlem sayan", m_son), ("eş aşamadaki katmanı düşüren", m_ilk_katman), ("alıntıyı gözlem sayan", m_altmetin)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def ilk_gozlem(olaylar, canary):
    if not isinstance(canary, str) or not canary:
        raise ValueError("canary boş olmayan string olmalı")
    sira = ("cikarma", "normalizasyon", "baglam", "model-yaniti")
    adimlar = ("metin-katmani", "metadata", "ocr")
    gozlemler = {}
    anahtarlar = set()
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"belge_id", "katman", "asama", "metin"}:
            raise ValueError("olay şeması geçersiz")
        if not isinstance(olay["belge_id"], str) or not olay["belge_id"] or not isinstance(olay["metin"], str):
            raise ValueError("belge kimliği veya metin geçersiz")
        if olay["katman"] not in adimlar or olay["asama"] not in sira:
            raise ValueError("katman veya aşama geçersiz")
        anahtar = (olay["belge_id"], olay["katman"], olay["asama"])
        if anahtar in anahtarlar:
            raise ValueError("yinelenen olay")
        anahtarlar.add(anahtar)
        if canary not in olay["metin"].splitlines():
            continue
        belge_id = olay["belge_id"]
        if belge_id not in gozlemler or sira.index(olay["asama"]) < sira.index(gozlemler[belge_id]["asama"]):
            gozlemler[belge_id] = {"asama": olay["asama"], "katmanlar": [olay["katman"]]}
        elif olay["asama"] == gozlemler[belge_id]["asama"]:
            gozlemler[belge_id]["katmanlar"].append(olay["katman"])
    return {belge_id: {"asama": gozlemler[belge_id]["asama"], "katmanlar": sorted(gozlemler[belge_id]["katmanlar"])} for belge_id in sorted(gozlemler)}
```

```hint
Aşamaları hat sırasındaki tuple üzerinde `index` ile karşılaştır. İlk eşleşmede kaydı kur, daha erken aşamada değiştir, aynı aşamada katmanı ekle; sonuçta belge ve katmanları sırala.
```
:::


::: anlat Aynı gerçek PDF'nin üç görünümünü karşılaştır
[Sentetik PDF tarif dosyasını aç](/data/ai-saldiri-13-tarif.txt). Bu tarif canlı kayıt değildir. Kurulu reportlab gerçek PDF üretir: görünen fatura bir görüntüdür, görünmeyen metin `render mode 3` ile PDF'ye yazılır, metadata ayrı alanlardır. pypdf gerçek dosyanın metin/metadata katmanını ve gömülü görüntüsünü çıkarır. Kurulu yerel vision modeli **PDF'den çıkarılan bu görüntüye** OCR uygular; bu genel çok sayfalı PDF render/OCR ürünü değildir. OCR sonucu önceden yazılmış metin tablosu değildir.

Çalıştır kalıcı `calisma/ai-saldiri-13/tarifler.json` kopyasını gösterir. Dış editörde veya Python ile düzenle: 1–3 benzersiz `id`, bool `gizli_metin` ve `metadata` alanları kullan. Her çalıştırma yeni sentetik canary ile ayrı PDF/PNG dosyaları üretir; bunlar öğrenci alanında korunur, mevcut dosyalar silinmez. Görünen görüntüde canary yoktur; görünmeyen metin/metadata tarifte seçilir. Bu, görsel ile çıkarılmış metnin farklı olabileceğini gösteren kontrollü bir örnektir.

Öğrenci gerçek üç katmanı paketler ve fark/ilk gözlem hesaplar. OCR bir çıkarma adımıdır. Metin/metadata/OCR çıkarımı, NFKC normalizasyonu ve kanonik bağlam ayrı olaylardır. Son gerçek sohbet çağrısı yalnız son belgenin metadata alanından tek satırda başlığı çıkarır; bu kaynağın bağlamı bilinir, birden çok katman için nedensellik iddia edilmez. JSON içindeki kaçışlı satırlar tam-satır canary ölçümünde farklı görünebilir. Modelin canary söylemesi kabul koşulu değildir.

PDF yardımcı Python'u varsayılan `.ai-araclar` içindir; `PAFTA_AI_PDF_PYTHON` ile değiştirilebilir. reportlab/pypdf/Pillow veya vision modeli yoksa deney geçmez; ders kurulum yapmaz. `PAFTA_AI_VISION_MODELI` varsayılanı kurulu `qwen2.5vl:3b` modelidir. GPU çağrıları ortak kilitle sıraya girer.
:::

::: gorev Gerçek deney · PDF metni, metadata ve gerçek vision OCR
Önceki üç işlevi birleştir: `katman_paketle`, `katman_farklari`, `ilk_gozlem`. Çalıştır PDF/PNG dosyalarını, gerçek çıkarılmış katmanları ve ilk gözlemi gösterir. Kontrol Et yeni kimlik/işaretlerle ve gerçek PDF/model çağrılarıyla doğrular. Saldırının başarılı olması şart değildir; bağımlılık veya deney hatası kabul değildir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def katman_paketle(katmanlar):return ""

def katman_farklari(kayitlar,canary):return {}

def ilk_gozlem(olaylar,canary):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_13 as deney
    deney.goster(katman_paketle,katman_farklari,ilk_gozlem)

```

```test
import copy
import json
KATMANLAR = [
    {"belge_id": "d2", "katman": "ocr", "asama": "cikarma", "metin": "Rapor"},
    {"belge_id": "d1", "katman": "metadata", "asama": "baglam", "metin": "system:\nBREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "metin-katmani", "asama": "cikarma", "metin": "Rapor"},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(KATMANLAR)
        sonuc = fn(KATMANLAR)
        veri = json.loads(sonuc)
        sirali = sorted(KATMANLAR, key=lambda x: (x["belge_id"], x["katman"], x["asama"]))
        if veri != {"guven": "guvenilmez", "katmanlar": sirali} or KATMANLAR != once:
            return False
        if sonuc != json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":")):
            return False
        if json.loads(fn(list(reversed(KATMANLAR)))) != veri or json.loads(fn([])) != {"guven": "guvenilmez", "katmanlar": []}:
            return False
        for kayitlar in [
            None, KATMANLAR + [KATMANLAR[0]], [dict(KATMANLAR[0], ek=1)],
            [dict(KATMANLAR[0], belge_id="")], [dict(KATMANLAR[0], katman="goruntu")],
            [dict(KATMANLAR[0], asama="system")], [dict(KATMANLAR[0], metin=3)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(katman_paketle), "şema, kaynak-aşama izi, deterministik sıra ve değişmezlik korunmalı")
def m_birlestir(katmanlar):
    return "\n".join(x["metin"] for x in katmanlar)
def m_kaynak(katmanlar):
    veri = json.loads(katman_paketle(katmanlar))
    for kayit in veri["katmanlar"]:
        kayit.pop("katman", None)
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def m_guven(katmanlar):
    return katman_paketle(katmanlar).replace("guvenilmez", "system")
for ad, mutant in [("katmanları ham metinde birleştiren", m_birlestir), ("kaynak katmanını silen", m_kaynak), ("belgeyi system sayan", m_guven)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KAYITLAR = [
    {"belge_id": "d1", "katman": "metin-katmani", "metin": "Rapor"},
    {"belge_id": "d1", "katman": "metadata", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "ocr", "metin": "Rapor"},
    {"belge_id": "d2", "katman": "metin-katmani", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d2", "katman": "metadata", "metin": "Rapor"},
    {"belge_id": "d2", "katman": "ocr", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d3", "katman": "metin-katmani", "metin": "Rapor"},
    {"belge_id": "d3", "katman": "metadata", "metin": "Rapor"},
    {"belge_id": "d3", "katman": "ocr", "metin": "Rapor"},
]
BEKLENEN = {"belgeler": {
    "d1": {"metin-katmani": False, "metadata": True, "ocr": False},
    "d2": {"metin-katmani": True, "metadata": False, "ocr": True},
    "d3": {"metin-katmani": False, "metadata": False, "ocr": False},
}, "farkli": ["d1", "d2"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR, "BREACH:CANARY-42") != BEKLENEN or KAYITLAR != once:
            return False
        if fn(list(reversed(KAYITLAR)), "BREACH:CANARY-42") != BEKLENEN or list(fn(KAYITLAR, "BREACH:CANARY-42")["belgeler"]) != ["d1", "d2", "d3"]:
            return False
        if fn([], "BREACH:CANARY-42") != {"belgeler": {}, "farkli": []}:
            return False
        alinti = [dict(x) for x in KAYITLAR]
        alinti[1]["metin"] = "BREACH:CANARY-42 yazma"
        if fn(alinti, "BREACH:CANARY-42")["farkli"] != ["d2"]:
            return False
        for kayitlar, canary in [
            ([None], "BREACH:CANARY-42"), (KAYITLAR, ""), (KAYITLAR, None), (KAYITLAR[:-1], "BREACH:CANARY-42"),
            (KAYITLAR + [KAYITLAR[0]], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[0], katman="goruntu")], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[i], metin=3) for i in range(3)], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[i], belge_id="") for i in range(3)], "BREACH:CANARY-42"),
            ([dict(KAYITLAR[0], ek=1)], "BREACH:CANARY-42"),
        ]:
            try:
                fn(kayitlar, canary)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(katman_farklari), "tam üçlü katman, tam satır canary ve fark listesi korunmalı")
def m_altmetin(kayitlar, canary):
    return {"belgeler": {}, "farkli": sorted({x["belge_id"] for x in kayitlar if canary in x["metin"]})}
def m_fark(kayitlar, canary):
    sonuc = katman_farklari(kayitlar, canary)
    sonuc["farkli"] = []
    return sonuc
def m_eksik(kayitlar, canary):
    return katman_farklari(kayitlar + [{"belge_id": "d4", "katman": "ocr", "metin": canary}], canary)
for ad, mutant in [("katmanları ve tam satırı yok sayan", m_altmetin), ("bütün farkları gizleyen", m_fark), ("eksik katmanı kabul eden", m_eksik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
OLAYLAR = [
    {"belge_id": "d1", "katman": "metadata", "asama": "model-yaniti", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "ocr", "asama": "baglam", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "metadata", "asama": "baglam", "metin": "BREACH:CANARY-42"},
    {"belge_id": "d1", "katman": "metin-katmani", "asama": "cikarma", "metin": "Rapor"},
    {"belge_id": "d2", "katman": "metadata", "asama": "normalizasyon", "metin": "Not\nBREACH:CANARY-42"},
    {"belge_id": "d2", "katman": "metadata", "asama": "baglam", "metin": "BREACH:CANARY-42"},
]
BEKLENEN = {
    "d1": {"asama": "baglam", "katmanlar": ["metadata", "ocr"]},
    "d2": {"asama": "normalizasyon", "katmanlar": ["metadata"]},
}
def sozlesme(fn):
    try:
        once = copy.deepcopy(OLAYLAR)
        if fn(OLAYLAR, "BREACH:CANARY-42") != BEKLENEN or OLAYLAR != once:
            return False
        if fn(list(reversed(OLAYLAR)), "BREACH:CANARY-42") != BEKLENEN or list(fn(OLAYLAR, "BREACH:CANARY-42")) != ["d1", "d2"]:
            return False
        if fn([], "BREACH:CANARY-42") != {} or fn(OLAYLAR, "YOK:CANARY-73") != {}:
            return False
        alinti = [dict(x) for x in OLAYLAR]
        alinti[1]["metin"] = "BREACH:CANARY-42 yazma"
        if fn(alinti, "BREACH:CANARY-42")["d1"] != {"asama": "baglam", "katmanlar": ["metadata"]}:
            return False
        for olaylar, canary in [
            (OLAYLAR, ""), (OLAYLAR, None), (OLAYLAR + [OLAYLAR[0]], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], asama="system")], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], katman="goruntu")], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], metin=3)], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], belge_id="")], "BREACH:CANARY-42"),
            ([dict(OLAYLAR[0], ek=1)], "BREACH:CANARY-42"),
        ]:
            try:
                fn(olaylar, canary)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(ilk_gozlem), "hat sırası, ilk gözlem, eş aşama katmanları ve tam satır korunmalı")
def m_son(olaylar, canary):
    eslesen = [x for x in olaylar if canary in x["metin"].splitlines()]
    return {x["belge_id"]: {"asama": x["asama"], "katmanlar": [x["katman"]]} for x in eslesen}
def m_ilk_katman(olaylar, canary):
    sonuc = ilk_gozlem(olaylar, canary)
    for kayit in sonuc.values():
        kayit["katmanlar"] = kayit["katmanlar"][:1]
    return sonuc
def m_altmetin(olaylar, canary):
    return ilk_gozlem(olaylar + [{"belge_id": "d3", "katman": "ocr", "asama": "cikarma", "metin": canary + " yazma"}], canary)
for ad, mutant in [("son olayı ilk gözlem sayan", m_son), ("eş aşamadaki katmanı düşüren", m_ilk_katman), ("alıntıyı gözlem sayan", m_altmetin)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_13 as deney
import tempfile,json,secrets
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('fark_referans','gozlem_referans')), 'laboratuvar/bağımsız ölçüm yamalanmamalı'):stop()
for i in range(3):
    marker='MARK-'+secrets.token_hex(4);ident='doc-'+secrets.token_hex(3)
    rows=[dict(belge_id=ident,katman=k,metin=marker if k=='metadata' else 'alıntı '+marker if k=='ocr' else 'görünür not') for k in ('metin-katmani','metadata','ocr')]
    if not ok(katman_farklari(rows,marker)==deney.fark_referans(rows,marker),'yeni belge/işarette katman farkı'):stop()
    events=[dict(v,asama='cikarma') for v in rows]+[dict(belge_id=ident,katman='metadata',asama='baglam',metin=marker)]
    if not ok(json.loads(katman_paketle(events))=={'guven':'guvenilmez','katmanlar':sorted(events,key=lambda v:(v['belge_id'],v['katman'],v['asama']))},'yeni olaylarda güven etiketi ve paket içeriği'):stop()
    if not ok(ilk_gozlem(events,marker)==deney.gozlem_referans(events,marker),'yeni olaylarda ilk gözlem'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_pdf13_') as tmp:
    recipe=Path(tmp)/'tarif.json';recipe.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    result=deney.deney(katman_paketle,katman_farklari,ilk_gozlem,recipe,Path(tmp)/'pdf')
    for key,value in result['kontroller'].items():ok(value,'gerçek deney: '+key)
    accepted=all(result['kontroller'].values());ai_lab.kanit_yaz('saldiri-13-pdf',dict(result,kabul=accepted));ok(accepted,'gerçek PDF katmanları/vision OCR ve doğru ölçüm; modelin işareti aktarması şart değil')

```

```solution
import ai_lab

import json

def katman_paketle(katmanlar):
    if not isinstance(katmanlar, list):
        raise ValueError("katman listesi gerekli")
    alanlar = {"belge_id", "katman", "asama", "metin"}
    anahtarlar = set()
    for kayit in katmanlar:
        if not isinstance(kayit, dict) or set(kayit) != alanlar:
            raise ValueError("katman şeması geçersiz")
        if not isinstance(kayit["belge_id"], str) or not kayit["belge_id"] or not isinstance(kayit["metin"], str):
            raise ValueError("belge kimliği veya metin geçersiz")
        if kayit["katman"] not in ("metin-katmani", "metadata", "ocr"):
            raise ValueError("katman geçersiz")
        if kayit["asama"] not in ("cikarma", "normalizasyon", "baglam", "model-yaniti"):
            raise ValueError("aşama geçersiz")
        anahtar = (kayit["belge_id"], kayit["katman"], kayit["asama"])
        if anahtar in anahtarlar:
            raise ValueError("yinelenen katman kaydı")
        anahtarlar.add(anahtar)
    sirali = sorted(katmanlar, key=lambda x: (x["belge_id"], x["katman"], x["asama"]))
    return json.dumps({"guven": "guvenilmez", "katmanlar": sirali}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def katman_farklari(kayitlar, canary):
    if not isinstance(canary, str) or not canary:
        raise ValueError("canary boş olmayan string olmalı")
    adimlar = ("metin-katmani", "metadata", "ocr")
    belgeler = {}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"belge_id", "katman", "metin"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["belge_id"], str) or not kayit["belge_id"] or not isinstance(kayit["metin"], str):
            raise ValueError("belge kimliği veya metin geçersiz")
        if kayit["katman"] not in adimlar:
            raise ValueError("katman geçersiz")
        katmanlar = belgeler.setdefault(kayit["belge_id"], {})
        if kayit["katman"] in katmanlar:
            raise ValueError("yinelenen katman")
        katmanlar[kayit["katman"]] = canary in kayit["metin"].splitlines()
    sonuc = {"belgeler": {}, "farkli": []}
    for belge_id in sorted(belgeler):
        katmanlar = belgeler[belge_id]
        if set(katmanlar) != set(adimlar):
            raise ValueError("belge katmanları eksik")
        sonuc["belgeler"][belge_id] = {adim: katmanlar[adim] for adim in adimlar}
        if len(set(katmanlar.values())) != 1:
            sonuc["farkli"].append(belge_id)
    return sonuc

def ilk_gozlem(olaylar, canary):
    if not isinstance(canary, str) or not canary:
        raise ValueError("canary boş olmayan string olmalı")
    sira = ("cikarma", "normalizasyon", "baglam", "model-yaniti")
    adimlar = ("metin-katmani", "metadata", "ocr")
    gozlemler = {}
    anahtarlar = set()
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"belge_id", "katman", "asama", "metin"}:
            raise ValueError("olay şeması geçersiz")
        if not isinstance(olay["belge_id"], str) or not olay["belge_id"] or not isinstance(olay["metin"], str):
            raise ValueError("belge kimliği veya metin geçersiz")
        if olay["katman"] not in adimlar or olay["asama"] not in sira:
            raise ValueError("katman veya aşama geçersiz")
        anahtar = (olay["belge_id"], olay["katman"], olay["asama"])
        if anahtar in anahtarlar:
            raise ValueError("yinelenen olay")
        anahtarlar.add(anahtar)
        if canary not in olay["metin"].splitlines():
            continue
        belge_id = olay["belge_id"]
        if belge_id not in gozlemler or sira.index(olay["asama"]) < sira.index(gozlemler[belge_id]["asama"]):
            gozlemler[belge_id] = {"asama": olay["asama"], "katmanlar": [olay["katman"]]}
        elif olay["asama"] == gozlemler[belge_id]["asama"]:
            gozlemler[belge_id]["katmanlar"].append(olay["katman"])
    return {belge_id: {"asama": gozlemler[belge_id]["asama"], "katmanlar": sorted(gozlemler[belge_id]["katmanlar"])} for belge_id in sorted(gozlemler)}
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_13 as deney
    deney.goster(katman_paketle,katman_farklari,ilk_gozlem)

```

```hint
Üç katmanı birbirine karıştırma. Tam satır canary ve aşama sırasını koru; JSON paketinin güven etiketi guvenilmez olmalı. OCR tahminini, PDF'nin metin katmanının kopyası diye kabul etme.
```
:::
