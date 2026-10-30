---
id: ai-saldiri-15
title: Retrieval Manipülasyonu ve Bağlam Ele Geçirme
summary: Sorgu varyantlarını izlenebilir normalize et, skor ve karakter bütçesiyle bağlam seçimini ölç ve manipülasyon sonrası bağlamdan düşen kanıt belgelerini raporla.
timeout: 45
---

::: anlat Bağlam, modelden önce şekillendirilir
RAG sisteminde model yalnız kendisine verilen bağlamı görür. Sorgunun yeniden yazılması, belgelerin skorlanması ve sınırlı bağlam penceresine seçim yapılması, modelden önceki üç etki noktasıdır. Retrieval manipülasyonu bu aşamalarda istenmeyen belgenin öne çıkması veya kanıt belgesinin dışarıda kalmasıdır.

Ölçüm için üç kayıt gerekir:

- **Sorgu izi:** Özgün sorgu ile retrieval'a gönderilen normalize biçim.
- **Seçim izi:** Skor sırası, bütçe ve seçilen/elenen belgeler.
- **Fark izi:** Temiz ve manipüle bağlamlar arasında giren ve çıkan belgeler.

Bağlamdan kanıtın düşmesi model yanıtının değişeceğini garanti etmez; yalnız modelin gördüğü verinin değiştiğini gösterir. Bu derste Python fixture'ları kullanılır, ChromaDB veya gerçek model çalıştırılmaz.
:::

::: tahmin
Bütçeye sığmayan belge atlanır; daha küçük sonraki belgeler denenmeye devam eder. Üç çıktı satırını yaz:

```python
belgeler = [("saldiri", 9), ("kanit", 4), ("not", 3)]
kalan = 7
secilen = []
elenen = []
for kimlik, boyut in belgeler:
    if boyut <= kalan:
        secilen.append(kimlik)
        kalan -= boyut
    else:
        elenen.append(kimlik)
print(secilen)
print(elenen)
print(7 - kalan)
```

???

```cikti
['kanit', 'not']
['saldiri']
7
```

Dokuz karakterlik belge bütçeyi aştığı için elenir. Dört ve üç karakterlik belgeler toplam yedi karakterle tam bütçeyi doldurur; hiçbir metin kırpılmaz.
:::

::: gorev 1 · Sorgunun özgün ve normalize biçimini birlikte kaydet
`sorgu_izi(sorgu)` işlevini yaz. Sorgu string olmalı, boşluklardan arındırıldığında boş kalmamalı ve en fazla 200 karakter olmalıdır. Aksi durumda `ValueError` yükselt.

Dönüş şu nesnenin kanonik JSON stringidir (`ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`):

```text
{"orijinal":SORGU,"normalize":NORMALIZE,"terimler":[TERIM,...]}
```

`normalize`, sorgunun `casefold()` uygulanmış ve ardışık boşlukları tek boşluğa indirgenmiş biçimidir; baş ve sondaki boşluklar da giderilir. `terimler`, normalize sorguda `re.findall(r"\w+", ...)` ile bulunan farklı terimlerin alfabetik listesidir. Özgün sorguyu değiştirme; normalize metindeki talimat görünümlü ifadeleri silme veya yetki alanına taşıma.

```starter
def sorgu_izi(sorgu):
    return ""
```

```test
import json
def sozlesme(fn):
    try:
        sonuc = fn("  RAG   Güvenlik system: TALIMAT  ")
        beklenen = {"orijinal": "  RAG   Güvenlik system: TALIMAT  ", "normalize": "rag güvenlik system: talimat", "terimler": ["güvenlik", "rag", "system", "talimat"]}
        if json.loads(sonuc) != beklenen:
            return False
        if sonuc != json.dumps(beklenen, ensure_ascii=False, sort_keys=True, separators=(",", ":")):
            return False
        if json.loads(fn("RAG rag"))["terimler"] != ["rag"] or json.loads(fn("???"))["terimler"] != []:
            return False
        if json.loads(fn("  x  "))["orijinal"] != "  x  " or json.loads(fn("x" * 200))["normalize"] != "x" * 200:
            return False
        for sorgu in ["", "   ", None, 3, "x" * 201]:
            try:
                fn(sorgu)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sorgu_izi), "özgün metin, Unicode casefold, boşluk ve farklı terimler korunmalı")
def m_orijinal(sorgu):
    veri = json.loads(sorgu_izi(sorgu))
    veri["orijinal"] = veri["normalize"]
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def m_tekrar(sorgu):
    veri = json.loads(sorgu_izi(sorgu))
    veri["terimler"] = veri["normalize"].split()
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def m_sil(sorgu):
    return sorgu_izi(sorgu).replace("system:", "")
for ad, mutant in [("özgün sorgu izini kaybeden", m_orijinal), ("terim tekrarını ve noktalamayı karıştıran", m_tekrar), ("talimat kanıtını silen", m_sil)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
import json
import re

def sorgu_izi(sorgu):
    if not isinstance(sorgu, str) or not sorgu.strip() or len(sorgu) > 200:
        raise ValueError("sorgu geçersiz")
    normalize = " ".join(sorgu.casefold().split())
    veri = {
        "orijinal": sorgu,
        "normalize": normalize,
        "terimler": sorted(set(re.findall(r"\w+", normalize))),
    }
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

```hint
Özgün stringi ayrı alanda sakla. Normalize metni `" ".join(...split())` ile kur; terimleri küme ve `sorted` ile tekrarsız, deterministik yap.
```
:::

::: anlat Yüksek skorlu belge bütün bağlamı doldurabilir
Saldırı belgesi retrieval'da yüksek skor alsa bile bağlam bütçesine sığmayabilir. Bütçe dolduğunda küçük kanıt belgeleri dışarıda kalabilir. Bunu ölçmek için seçim algoritması belgeleri kırpmamalı, her seçimde kalan bütçeyi göstermeli ve elenenleri kaydetmelidir.

Bu derste skor sırası uygulanır; bütçeye sığmayan belge atlanır ve daha küçük sonraki belgeler denenir. Böylece yalnız ilk büyük belge yüzünden bütün bütçe boş kalmaz. Seçilen belgelerin toplam karakter sayısı bütçeyi aşamaz. Karakter bütçesi token bütçesi değildir; gerçek sistemde tokenizer ayrıca uygulanır.
:::

::: gorev 2 · Skor sıralı belgeleri karakter bütçesiyle bağlama seç
`baglam_sec(belgeler, butce)` işlevini yaz. `butce`, bool olmayan ve `0..10000` aralığında tam sayı olmalıdır. Her belge tam olarak `id`, `metin`, `skor` alanlarını taşısın; kimlik boş olmayan ve benzersiz string, metin string, skor bool olmayan ve `0..100` aralığında tam sayı olmalıdır. Geçersiz veride `ValueError` yükselt.

Belgeleri azalan skor, eşitlikte artan kimlikle sırala. Sırayla her belgeyi yalnız metninin tamamı kalan bütçeye sığıyorsa seç; sığmıyorsa elenmiş say ve sonraki belgelere devam et. Metin kırpma. Dönüş:

```text
{"secilen":[ID,...],"elenen":[ID,...],"kullanilan":KARAKTER}
```

Listeler seçim sırasını korur. `kullanilan`, seçilen metinlerin toplam `len` değeridir. Boş metin seçilebilir; `butce=0` iken yalnız boş metinler seçilir. Girdiyi değiştirme.

```starter
def baglam_sec(belgeler, butce):
    return {}
```

```test
import copy
BELGELER = [
    {"id": "kanit", "metin": "1234", "skor": 5},
    {"id": "saldiri", "metin": "123456789", "skor": 9},
    {"id": "not", "metin": "123", "skor": 5},
    {"id": "bos", "metin": "", "skor": 0},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(BELGELER)
        beklenen = {"secilen": ["kanit", "not", "bos"], "elenen": ["saldiri"], "kullanilan": 7}
        if fn(BELGELER, 7) != beklenen or BELGELER != once or fn(list(reversed(BELGELER)), 7) != beklenen:
            return False
        if fn(BELGELER, 0) != {"secilen": ["bos"], "elenen": ["saldiri", "kanit", "not"], "kullanilan": 0}:
            return False
        if fn(BELGELER, 9)["secilen"] != ["saldiri", "bos"] or fn(BELGELER, 9)["kullanilan"] != 9:
            return False
        if fn([], 0) != {"secilen": [], "elenen": [], "kullanilan": 0} or fn([], 10000)["kullanilan"] != 0:
            return False
        if fn([dict(BELGELER[0], skor=100)], 4)["secilen"] != ["kanit"]:
            return False
        for belgeler, butce in [
            (BELGELER, -1), (BELGELER, 10001), (BELGELER, True), (BELGELER, 7.0),
            (BELGELER + [BELGELER[0]], 7), ([dict(BELGELER[0], id="")], 7),
            ([dict(BELGELER[0], metin=3)], 7), ([dict(BELGELER[0], skor=-1)], 7),
            ([dict(BELGELER[0], skor=101)], 7), ([dict(BELGELER[0], skor=True)], 7),
            ([dict(BELGELER[0], ek=1)], 7),
        ]:
            try:
                fn(belgeler, butce)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(baglam_sec), "skor, tie-break, tam metin ve bütçe sınırı korunmalı")
def m_kirp(belgeler, butce):
    return {"secilen": [b["id"] for b in belgeler], "elenen": [], "kullanilan": butce}
def m_dur(belgeler, butce):
    sonuc = baglam_sec(belgeler, 0)
    return sonuc
def m_skor(belgeler, butce):
    sirali = sorted(belgeler, key=lambda x: x["id"])
    return {"secilen": [b["id"] for b in sirali], "elenen": [], "kullanilan": 0}
for ad, mutant in [("bütçeyi ve kırpmama kuralını yok sayan", m_kirp), ("ilk elemede bütçeyi kapatan", m_dur), ("skor sırasını kimlik sırasına çeviren", m_skor)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def baglam_sec(belgeler, butce):
    if isinstance(butce, bool) or not isinstance(butce, int) or not 0 <= butce <= 10000:
        raise ValueError("bütçe geçersiz")
    kimlikler = set()
    for belge in belgeler:
        if not isinstance(belge, dict) or set(belge) != {"id", "metin", "skor"}:
            raise ValueError("belge şeması geçersiz")
        if not all((isinstance(belge["id"], str), bool(belge["id"]), isinstance(belge["metin"], str), isinstance(belge["skor"], int), not isinstance(belge["skor"], bool), 0 <= belge["skor"] <= 100, belge["id"] not in kimlikler)):
            raise ValueError("belge alanları geçersiz")
        kimlikler.add(belge["id"])
    sirali = sorted(belgeler, key=lambda x: (-x["skor"], x["id"]))
    sonuc = {"secilen": [], "elenen": [], "kullanilan": 0}
    for belge in sirali:
        boyut = len(belge["metin"])
        if boyut <= butce - sonuc["kullanilan"]:
            sonuc["secilen"].append(belge["id"])
            sonuc["kullanilan"] += boyut
        else:
            sonuc["elenen"].append(belge["id"])
    return sonuc
```

```hint
Önce `(skor, id)` sıralamasını yap. Kalan bütçeyi `butce - kullanilan` olarak hesapla; seçimde kimliği `secilen`, aksi halde `elenen` listesine ekle.
```
:::

::: anlat Kanıtın bağlamdan çıkması ayrı bir regresyon ölçütüdür
Temiz ve manipüle çalışmada yalnız ilk belgeye bakmak, bağlam değişimini eksik anlatır. Yeni giren saldırı belgesi kadar, çıkan kanıt belgesi de önemlidir. Kimlik kümeleri üzerinden fark çıkarmak sıra değişimini gizler; bu nedenle genel `degisen` listesi ayrıca tutulur.

Aşağıdaki raporda `kanit_kaybolan`, belirlenen kanıt kimliğinin temiz bağlamda bulunup manipüle bağlamda bulunmadığı vakalardır. Bu ölçüt retrieval ve paketleme farkını gösterir; model yanıtındaki değişikliği ölçmek için ayrı deney gerekir.
:::

::: gorev 3 · Manipüle bağlamda giren, çıkan ve kaybolan kanıtı raporla
`baglam_farki(kayitlar, kanit_id)` işlevini yaz. Her kayıt tam olarak `vaka_id`, `kume`, `baglam` alanlarını taşısın. `vaka_id` boş olmayan string, `kume` `temiz` veya `manipule`, `baglam` string kimliklerden oluşan liste olmalıdır. Bağlam kimlikleri boş olmayan ve kendi listesi içinde benzersiz olmalıdır. Her vaka tam bir temiz ve bir manipüle kayda sahip olmalı; eksik veya yinelenen kolda `ValueError` yükselt. `kanit_id` boş olmayan string olmalıdır.

Dönüş:

```text
{"vaka":N,
 "giren":{VAKA:[ID,...]},"cikan":{VAKA:[ID,...]},
 "degisen":[VAKA,...],"kanit_kaybolan":[VAKA,...]}
```

`giren = manipule - temiz`, `cikan = temiz - manipule` küme farklarıdır. `degisen`, iki bağlam kimlik kümesi farklı olan bütün vakalardır. `kanit_kaybolan`, kanıt kimliği temizde olup manipülede olmayan vakalardır. Vaka ve kimlik listelerini alfabetik sırala; her vaka için `giren` ve `cikan` listesi üret. Boş girdi için boş rapor dön. Girdi sırası sonucu etkilememeli ve veri değişmemelidir.

```starter
def baglam_farki(kayitlar, kanit_id):
    return {}
```

```test
import copy
KAYITLAR = [
    {"vaka_id": "v1", "kume": "manipule", "baglam": ["saldiri", "not"]},
    {"vaka_id": "v1", "kume": "temiz", "baglam": ["kanit", "not"]},
    {"vaka_id": "v2", "kume": "temiz", "baglam": ["kanit"]},
    {"vaka_id": "v2", "kume": "manipule", "baglam": ["kanit"]},
    {"vaka_id": "v3", "kume": "temiz", "baglam": ["diger"]},
    {"vaka_id": "v3", "kume": "manipule", "baglam": ["kanit"]},
    {"vaka_id": "v4", "kume": "temiz", "baglam": []},
    {"vaka_id": "v4", "kume": "manipule", "baglam": ["saldiri"]},
]
BEKLENEN = {
    "vaka": 4,
    "giren": {"v1": ["saldiri"], "v2": [], "v3": ["kanit"], "v4": ["saldiri"]},
    "cikan": {"v1": ["kanit"], "v2": [], "v3": ["diger"], "v4": []},
    "degisen": ["v1", "v3", "v4"], "kanit_kaybolan": ["v1"],
}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR, "kanit") != BEKLENEN or KAYITLAR != once:
            return False
        if fn(list(reversed(KAYITLAR)), "kanit") != BEKLENEN or list(fn(KAYITLAR, "kanit")["giren"]) != ["v1", "v2", "v3", "v4"]:
            return False
        if fn([], "kanit") != {"vaka": 0, "giren": {}, "cikan": {}, "degisen": [], "kanit_kaybolan": []}:
            return False
        for kayitlar, kanit in [
            (KAYITLAR, ""), (KAYITLAR, None), (KAYITLAR[:-1], "kanit"),
            (KAYITLAR + [KAYITLAR[0]], "kanit"),
            ([dict(KAYITLAR[0], kume="diger"), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], vaka_id=""), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam="saldiri"), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam=["x", "x"]), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam=[""]), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam=[3]), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], ek=1), KAYITLAR[1]], "kanit"), ([None], "kanit"),
        ]:
            try:
                fn(kayitlar, kanit)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(baglam_farki), "iki bağlam kolu, küme farkları ve kaybolan kanıt korunmalı")
def m_kanit(kayitlar, kanit_id):
    sonuc = baglam_farki(kayitlar, kanit_id)
    sonuc["kanit_kaybolan"] = []
    return sonuc
def m_yon(kayitlar, kanit_id):
    sonuc = baglam_farki(kayitlar, kanit_id)
    sonuc["giren"], sonuc["cikan"] = sonuc["cikan"], sonuc["giren"]
    return sonuc
def m_degisen(kayitlar, kanit_id):
    sonuc = baglam_farki(kayitlar, kanit_id)
    sonuc["degisen"] = sonuc["kanit_kaybolan"]
    return sonuc
for ad, mutant in [("kanıt kaybını gizleyen", m_kanit), ("giren ve çıkanı ters çeviren", m_yon), ("kanıt içermeyen değişimi düşüren", m_degisen)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def baglam_farki(kayitlar, kanit_id):
    if not isinstance(kanit_id, str) or not kanit_id:
        raise ValueError("kanıt kimliği geçersiz")
    vakalar = {}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "kume", "baglam"}:
            raise ValueError("kayıt şeması geçersiz")
        if not all((isinstance(kayit["vaka_id"], str), bool(kayit["vaka_id"]), kayit["kume"] in ("temiz", "manipule"), isinstance(kayit["baglam"], list))):
            raise ValueError("vaka veya küme geçersiz")
        if not all(isinstance(kimlik, str) and bool(kimlik) for kimlik in kayit["baglam"]):
            raise ValueError("bağlam kimliği geçersiz")
        if len(kayit["baglam"]) != len(set(kayit["baglam"])):
            raise ValueError("yinelenen bağlam kimliği")
        kumeler = vakalar.setdefault(kayit["vaka_id"], {})
        if kayit["kume"] in kumeler:
            raise ValueError("yinelenen bağlam kolu")
        kumeler[kayit["kume"]] = set(kayit["baglam"])
    sonuc = {"vaka": len(vakalar), "giren": {}, "cikan": {}, "degisen": [], "kanit_kaybolan": []}
    for vaka in sorted(vakalar):
        kumeler = vakalar[vaka]
        if set(kumeler) != {"temiz", "manipule"}:
            raise ValueError("bağlam kolları eksik")
        temiz = kumeler["temiz"]
        manipule = kumeler["manipule"]
        sonuc["giren"][vaka] = sorted(manipule - temiz)
        sonuc["cikan"][vaka] = sorted(temiz - manipule)
        if temiz != manipule:
            sonuc["degisen"].append(vaka)
        if kanit_id in temiz and kanit_id not in manipule:
            sonuc["kanit_kaybolan"].append(vaka)
    return sonuc
```

```hint
Her kolu kimlik kümesine çevir. Küme farklarıyla `giren` ve `cikan` listelerini kur; kaybolan kanıt için temizde üyelik ve manipülede bulunmama koşulunu birlikte denetle.
```
:::


::: anlat Gerçek gömme skorunu dışarıdan gelen skorla karıştırma
[Sentetik bağlam dosyasını aç](/data/ai-saldiri-15-baglam.txt). Çalıştır ayrı kalıcı `calisma/ai-saldiri-15/baglam.json` kopyasını gösterir; dış editör/Python ile değiştirip yeniden çalıştır, sıfırlanmaz. Dosya bir sorgu, temiz belgeler, ayrı ek belge, kanıt kimliği, karakter bütçesi ve sahte dış skor taşır. Öğrenci verisi silinmez.

Kurulu `all-minilm:22m` modeli sorgu ve belgeleri gerçekten gömer. Cosine benzerliği `round((cosine+1)*50)` ile dersin0–100 tamsayı skoruna taşınır; bu olasılık veya güven puanı değildir. Temiz kol bu gerçek skorları kullanır. Manipüle kol ek belgenin **dış kaynaklı sahte skoruna** güvenen kusurlu uygulamayı temsil eder; sahte skor gerçek embedding skoru diye sunulmaz. Bu, skor metadata güven sınırı deneyidir; her retrieval sisteminin bu kusura sahip olduğu iddiası yoktur.

Öğrencinin karakter bütçeli seçimi gerçek skorlu belgelerde çalışır; karakter bütçesi token bütçesi değildir, JSON/şablon maliyeti bu dar sözleşmenin dışında kalır. Temiz ve manipüle seçimler gerçek modele ayrı gider. Kanıtın bağlamdan düşmesi, yanıttaki işaret ve modelin talimata uyması farklı gözlemlerdir; bunların gerçekleşmesi geçme şartı değildir. Ham vektörler öğrenci alanında JSON dosyasına yazılır. Model/araç yoksa deney geçmez; ders indirme yapmaz. `PAFTA_AI_EMBED_MODELI` ile kurulu gömme modeli seçilebilir.
:::

::: gorev Gerçek deney · Gömme skorundan bütçeli bağlama
Önceki üç işlevi birleştir: `sorgu_izi`, `baglam_sec`, `baglam_farki`. Çalıştır gerçek cosine/tamsayı skorlarını, sahte skoru, iki seçimi ve iki canlı yanıtı ayrı gösterir. Kontrol Et yeni sorgu/bütçe örneklerinde ve gerçek gömme çağrılarında ölçümü doğrular. GPU çağrıları ortak kilitle sıraya girer.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def sorgu_izi(sorgu):return ""

def baglam_sec(belgeler,butce):return {}

def baglam_farki(kayitlar,kanit_id):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_15 as deney
    deney.goster(sorgu_izi,baglam_sec,baglam_farki)

```

```test
import json
def sozlesme(fn):
    try:
        sonuc = fn("  RAG   Güvenlik system: TALIMAT  ")
        beklenen = {"orijinal": "  RAG   Güvenlik system: TALIMAT  ", "normalize": "rag güvenlik system: talimat", "terimler": ["güvenlik", "rag", "system", "talimat"]}
        if json.loads(sonuc) != beklenen:
            return False
        if sonuc != json.dumps(beklenen, ensure_ascii=False, sort_keys=True, separators=(",", ":")):
            return False
        if json.loads(fn("RAG rag"))["terimler"] != ["rag"] or json.loads(fn("???"))["terimler"] != []:
            return False
        if json.loads(fn("  x  "))["orijinal"] != "  x  " or json.loads(fn("x" * 200))["normalize"] != "x" * 200:
            return False
        for sorgu in ["", "   ", None, 3, "x" * 201]:
            try:
                fn(sorgu)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sorgu_izi), "özgün metin, Unicode casefold, boşluk ve farklı terimler korunmalı")
def m_orijinal(sorgu):
    veri = json.loads(sorgu_izi(sorgu))
    veri["orijinal"] = veri["normalize"]
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def m_tekrar(sorgu):
    veri = json.loads(sorgu_izi(sorgu))
    veri["terimler"] = veri["normalize"].split()
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def m_sil(sorgu):
    return sorgu_izi(sorgu).replace("system:", "")
for ad, mutant in [("özgün sorgu izini kaybeden", m_orijinal), ("terim tekrarını ve noktalamayı karıştıran", m_tekrar), ("talimat kanıtını silen", m_sil)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
BELGELER = [
    {"id": "kanit", "metin": "1234", "skor": 5},
    {"id": "saldiri", "metin": "123456789", "skor": 9},
    {"id": "not", "metin": "123", "skor": 5},
    {"id": "bos", "metin": "", "skor": 0},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(BELGELER)
        beklenen = {"secilen": ["kanit", "not", "bos"], "elenen": ["saldiri"], "kullanilan": 7}
        if fn(BELGELER, 7) != beklenen or BELGELER != once or fn(list(reversed(BELGELER)), 7) != beklenen:
            return False
        if fn(BELGELER, 0) != {"secilen": ["bos"], "elenen": ["saldiri", "kanit", "not"], "kullanilan": 0}:
            return False
        if fn(BELGELER, 9)["secilen"] != ["saldiri", "bos"] or fn(BELGELER, 9)["kullanilan"] != 9:
            return False
        if fn([], 0) != {"secilen": [], "elenen": [], "kullanilan": 0} or fn([], 10000)["kullanilan"] != 0:
            return False
        if fn([dict(BELGELER[0], skor=100)], 4)["secilen"] != ["kanit"]:
            return False
        for belgeler, butce in [
            (BELGELER, -1), (BELGELER, 10001), (BELGELER, True), (BELGELER, 7.0),
            (BELGELER + [BELGELER[0]], 7), ([dict(BELGELER[0], id="")], 7),
            ([dict(BELGELER[0], metin=3)], 7), ([dict(BELGELER[0], skor=-1)], 7),
            ([dict(BELGELER[0], skor=101)], 7), ([dict(BELGELER[0], skor=True)], 7),
            ([dict(BELGELER[0], ek=1)], 7),
        ]:
            try:
                fn(belgeler, butce)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(baglam_sec), "skor, tie-break, tam metin ve bütçe sınırı korunmalı")
def m_kirp(belgeler, butce):
    return {"secilen": [b["id"] for b in belgeler], "elenen": [], "kullanilan": butce}
def m_dur(belgeler, butce):
    sonuc = baglam_sec(belgeler, 0)
    return sonuc
def m_skor(belgeler, butce):
    sirali = sorted(belgeler, key=lambda x: x["id"])
    return {"secilen": [b["id"] for b in sirali], "elenen": [], "kullanilan": 0}
for ad, mutant in [("bütçeyi ve kırpmama kuralını yok sayan", m_kirp), ("ilk elemede bütçeyi kapatan", m_dur), ("skor sırasını kimlik sırasına çeviren", m_skor)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KAYITLAR = [
    {"vaka_id": "v1", "kume": "manipule", "baglam": ["saldiri", "not"]},
    {"vaka_id": "v1", "kume": "temiz", "baglam": ["kanit", "not"]},
    {"vaka_id": "v2", "kume": "temiz", "baglam": ["kanit"]},
    {"vaka_id": "v2", "kume": "manipule", "baglam": ["kanit"]},
    {"vaka_id": "v3", "kume": "temiz", "baglam": ["diger"]},
    {"vaka_id": "v3", "kume": "manipule", "baglam": ["kanit"]},
    {"vaka_id": "v4", "kume": "temiz", "baglam": []},
    {"vaka_id": "v4", "kume": "manipule", "baglam": ["saldiri"]},
]
BEKLENEN = {
    "vaka": 4,
    "giren": {"v1": ["saldiri"], "v2": [], "v3": ["kanit"], "v4": ["saldiri"]},
    "cikan": {"v1": ["kanit"], "v2": [], "v3": ["diger"], "v4": []},
    "degisen": ["v1", "v3", "v4"], "kanit_kaybolan": ["v1"],
}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR, "kanit") != BEKLENEN or KAYITLAR != once:
            return False
        if fn(list(reversed(KAYITLAR)), "kanit") != BEKLENEN or list(fn(KAYITLAR, "kanit")["giren"]) != ["v1", "v2", "v3", "v4"]:
            return False
        if fn([], "kanit") != {"vaka": 0, "giren": {}, "cikan": {}, "degisen": [], "kanit_kaybolan": []}:
            return False
        for kayitlar, kanit in [
            (KAYITLAR, ""), (KAYITLAR, None), (KAYITLAR[:-1], "kanit"),
            (KAYITLAR + [KAYITLAR[0]], "kanit"),
            ([dict(KAYITLAR[0], kume="diger"), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], vaka_id=""), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam="saldiri"), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam=["x", "x"]), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam=[""]), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], baglam=[3]), KAYITLAR[1]], "kanit"),
            ([dict(KAYITLAR[0], ek=1), KAYITLAR[1]], "kanit"), ([None], "kanit"),
        ]:
            try:
                fn(kayitlar, kanit)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(baglam_farki), "iki bağlam kolu, küme farkları ve kaybolan kanıt korunmalı")
def m_kanit(kayitlar, kanit_id):
    sonuc = baglam_farki(kayitlar, kanit_id)
    sonuc["kanit_kaybolan"] = []
    return sonuc
def m_yon(kayitlar, kanit_id):
    sonuc = baglam_farki(kayitlar, kanit_id)
    sonuc["giren"], sonuc["cikan"] = sonuc["cikan"], sonuc["giren"]
    return sonuc
def m_degisen(kayitlar, kanit_id):
    sonuc = baglam_farki(kayitlar, kanit_id)
    sonuc["degisen"] = sonuc["kanit_kaybolan"]
    return sonuc
for ad, mutant in [("kanıt kaybını gizleyen", m_kanit), ("giren ve çıkanı ters çeviren", m_yon), ("kanıt içermeyen değişimi düşüren", m_degisen)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_15 as deney
import json,secrets,tempfile,re
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('secim_referans','fark_referans')), 'laboratuvar/bağımsız ölçüm yamalanmamalı'):stop()
for i in range(4):
    q='  Q'+secrets.token_hex(4)+'  NOTE  ';normal=' '.join(q.casefold().split())
    if not ok(json.loads(sorgu_izi(q))==dict(orijinal=q,normalize=normal,terimler=sorted(set(re.findall(r'\w+',normal)))),'yeni sorguda özgün/normalize iz'):stop()
    docs=[dict(id='a',metin='x'*12,skor=100),dict(id='b',metin=secrets.token_hex(2),skor=50)]
    if not ok(baglam_sec(docs,7)==dict(secilen=['b'],elenen=['a'],kullanilan=4),'sığmayan yüksek skoru atla, sonraki meşru belgeyi koru'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_ctx15_') as tmp:
    p=Path(tmp)/'baglam.json';p.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    result=deney.deney(sorgu_izi,baglam_sec,baglam_farki,p,Path(tmp)/'deney')
    for key,value in result['kontroller'].items():ok(value,'gerçek deney: '+key)
    accepted=all(result['kontroller'].values());ai_lab.kanit_yaz('saldiri-15-baglam',dict(result,kabul=accepted));ok(accepted,'gerçek gömme/bağlam/model farkı; kanıtın mutlaka kaybolması geçme şartı değil')

```

```solution
import ai_lab

import json
import re

def sorgu_izi(sorgu):
    if not isinstance(sorgu, str) or not sorgu.strip() or len(sorgu) > 200:
        raise ValueError("sorgu geçersiz")
    normalize = " ".join(sorgu.casefold().split())
    veri = {
        "orijinal": sorgu,
        "normalize": normalize,
        "terimler": sorted(set(re.findall(r"\w+", normalize))),
    }
    return json.dumps(veri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def baglam_sec(belgeler, butce):
    if isinstance(butce, bool) or not isinstance(butce, int) or not 0 <= butce <= 10000:
        raise ValueError("bütçe geçersiz")
    kimlikler = set()
    for belge in belgeler:
        if not isinstance(belge, dict) or set(belge) != {"id", "metin", "skor"}:
            raise ValueError("belge şeması geçersiz")
        if not all((isinstance(belge["id"], str), bool(belge["id"]), isinstance(belge["metin"], str), isinstance(belge["skor"], int), not isinstance(belge["skor"], bool), 0 <= belge["skor"] <= 100, belge["id"] not in kimlikler)):
            raise ValueError("belge alanları geçersiz")
        kimlikler.add(belge["id"])
    sirali = sorted(belgeler, key=lambda x: (-x["skor"], x["id"]))
    sonuc = {"secilen": [], "elenen": [], "kullanilan": 0}
    for belge in sirali:
        boyut = len(belge["metin"])
        if boyut <= butce - sonuc["kullanilan"]:
            sonuc["secilen"].append(belge["id"])
            sonuc["kullanilan"] += boyut
        else:
            sonuc["elenen"].append(belge["id"])
    return sonuc

def baglam_farki(kayitlar, kanit_id):
    if not isinstance(kanit_id, str) or not kanit_id:
        raise ValueError("kanıt kimliği geçersiz")
    vakalar = {}
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "kume", "baglam"}:
            raise ValueError("kayıt şeması geçersiz")
        if not all((isinstance(kayit["vaka_id"], str), bool(kayit["vaka_id"]), kayit["kume"] in ("temiz", "manipule"), isinstance(kayit["baglam"], list))):
            raise ValueError("vaka veya küme geçersiz")
        if not all(isinstance(kimlik, str) and bool(kimlik) for kimlik in kayit["baglam"]):
            raise ValueError("bağlam kimliği geçersiz")
        if len(kayit["baglam"]) != len(set(kayit["baglam"])):
            raise ValueError("yinelenen bağlam kimliği")
        kumeler = vakalar.setdefault(kayit["vaka_id"], {})
        if kayit["kume"] in kumeler:
            raise ValueError("yinelenen bağlam kolu")
        kumeler[kayit["kume"]] = set(kayit["baglam"])
    sonuc = {"vaka": len(vakalar), "giren": {}, "cikan": {}, "degisen": [], "kanit_kaybolan": []}
    for vaka in sorted(vakalar):
        kumeler = vakalar[vaka]
        if set(kumeler) != {"temiz", "manipule"}:
            raise ValueError("bağlam kolları eksik")
        temiz = kumeler["temiz"]
        manipule = kumeler["manipule"]
        sonuc["giren"][vaka] = sorted(manipule - temiz)
        sonuc["cikan"][vaka] = sorted(temiz - manipule)
        if temiz != manipule:
            sonuc["degisen"].append(vaka)
        if kanit_id in temiz and kanit_id not in manipule:
            sonuc["kanit_kaybolan"].append(vaka)
    return sonuc
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_15 as deney
    deney.goster(sorgu_izi,baglam_sec,baglam_farki)

```

```hint
Özgün sorguyu normalize metinle değiştirme. Sığmayan belge sonrası döngüyü bitirme; bütçeye sığan daha düşük skorlu belge olabilir. Fark raporu seçim kimliklerinden hesaplanır; modelin söylediği bilgiyle karıştırılmaz.
```
:::
