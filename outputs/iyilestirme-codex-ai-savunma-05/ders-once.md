---
id: ai-savunma-05
title: İzole ve Tekrarlanabilir Yerel Test Laboratuvarı
summary: İzolasyon ayarlarını doğrula, fixture manifestosu çıkar ve tekrarlanan koşuların determinizm kanıtını raporla.
timeout: 45
---

::: anlat İzolasyon gerçek kaynaklardan kopuştur
Güvenlik testi gerçek kullanıcı verisine, üretim kimlik bilgisine veya dış ağa ihtiyaç duymamalıdır. Bu dersin laboratuvar sözleşmesinde ağ kapalı, model fixture, veri sentetik, yetki salt okunur ve geçici dizin dar bir göreli addır. Tohum sabitlenir; böylece aynı girdinin tekrar koşulması karşılaştırılabilir olur.

Docker, Ollama ve Promptfoo gerçek bir kurulumda bu sınırları uygulayan araçlardır; ancak burada onları başlatmıyoruz. Yapılandırma ve koşu kayıtları standart Python ile sınanır. Bu fixture, gerçek sandbox veya ağ yalıtımı kurulduğunu tek başına kanıtlamaz; yalnız laboratuvar tanımının beklenen sözleşmeye uyduğunu doğrular.
:::

::: tahmin Aynı baytlar aynı SHA-256 özetini üretir
Üç çıktı satırını yaz:

```python
import hashlib
print(hashlib.sha256(b"a").hexdigest()[:8])
print(len(hashlib.sha256(b"a").hexdigest()))
print(hashlib.sha256(b"a").digest() == hashlib.sha256(b"a").digest())
```

???

```cikti
ca978112
64
True
```

Özet girdinin içeriğini saklamaz; manifestoda aynı fixture'ın kullanıldığını karşılaştırmak için kullanılır.
:::

::: gorev 1 · İzole laboratuvar yapılandırmasını doğrula
`lab_yapilandirmasi_dogrula(ayar)` işlevini yaz. Ayar tam olarak `ag`, `model`, `veri`, `yetki`, `tohum`, `gecici_dizin` alanlarını taşısın. Değerler sırasıyla yalnız `kapali`, `fixture`, `sentetik`, `salt_okunur` olmalıdır. Tohum bool olmayan, 0–4294967295 aralığında bir int olmalıdır. Geçici dizin, küçük harfle başlayan ve yalnız küçük ASCII harf, rakam, alt çizgi veya tire içeren bir dizin adıdır; yol ayırıcı içeremez. Geçersiz veride `ValueError` yükselt.

Alanları ve değerleri koruyan yeni bir sözlük döndür; girdiyi değiştirme.

```starter
def lab_yapilandirmasi_dogrula(ayar):
    return {}
```

```test
A = {"ag": "kapali", "model": "fixture", "veri": "sentetik", "yetki": "salt_okunur", "tohum": 42, "gecici_dizin": "lab_tmp-1"}
def sozlesme(fn):
    try:
        once = dict(A)
        if fn(A) != A or A != once or fn(A) is A:
            return False
        for tohum in (0, 4294967295):
            if fn(dict(A, tohum=tohum))["tohum"] != tohum:
                return False
        for ayar in [
            None, [], dict(A, ek=1), dict(A, ag="acik"), dict(A, model="ollama"),
            dict(A, veri="uretim"), dict(A, yetki="admin"), dict(A, tohum=True),
            dict(A, tohum=-1), dict(A, tohum=4294967296), dict(A, tohum=1.5),
            dict(A, gecici_dizin=""), dict(A, gecici_dizin="Lab"),
            dict(A, gecici_dizin="../tmp"), dict(A, gecici_dizin="/tmp"),
            dict(A, gecici_dizin="lab/tmp"), dict(A, gecici_dizin=None),
        ]:
            try:
                fn(ayar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(lab_yapilandirmasi_dogrula), "ağ, model, veri, yetki ve tohum sınırları korunmalı")
def m_ag(ayar):
    sonuc = lab_yapilandirmasi_dogrula(ayar)
    sonuc["ag"] = "acik"
    return sonuc
def m_veri(ayar):
    sonuc = lab_yapilandirmasi_dogrula(ayar)
    sonuc["veri"] = "uretim"
    return sonuc
def m_tohum(ayar):
    sonuc = lab_yapilandirmasi_dogrula(ayar)
    sonuc["tohum"] += 1
    return sonuc
for ad, mutant in [("ağı açan", m_ag), ("üretim verisi yazan", m_veri), ("tohumu değiştiren", m_tohum)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def lab_yapilandirmasi_dogrula(ayar):
    import re
    zorunlu = {"ag", "model", "veri", "yetki", "tohum", "gecici_dizin"}
    if not isinstance(ayar, dict):
        raise ValueError("ayar geçersiz")
    if set(ayar) != zorunlu:
        raise ValueError("ayar şeması geçersiz")
    beklenen = {"ag": "kapali", "model": "fixture", "veri": "sentetik", "yetki": "salt_okunur"}
    for alan, deger in beklenen.items():
        if ayar[alan] != deger:
            raise ValueError("izolasyon ayarı geçersiz: " + alan)
    tohum = ayar["tohum"]
    if type(tohum) is not int:
        raise ValueError("tohum int olmalı")
    if tohum < 0:
        raise ValueError("tohum negatif olamaz")
    if tohum > 4294967295:
        raise ValueError("tohum üst sınırı aştı")
    dizin = ayar["gecici_dizin"]
    if not isinstance(dizin, str):
        raise ValueError("geçici dizin geçersiz")
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", dizin):
        raise ValueError("geçici dizin geçersiz")
    return dict(ayar)
```

```hint
Dört izolasyon alanını sabit bir sözlükle karşılaştır. Tohumda `type(...) is int` kullan ve geçici dizini yol ayırıcı içermeyen bir desenle sınırla.
```
:::

::: anlat Manifesto fixture kimliğini kanıtlar
Her fixture dosyasının göreli adı, UTF-8 bayt sayısı ve SHA-256 özeti manifestoya yazılır. Böylece iki koşunun aynı veriyi kullanıp kullanmadığı karşılaştırılabilir. Dosya içeriğini rapora kopyalamak yerine özetini taşımak, sentetik olmayan içeriğin yanlışlıkla yayılmasını da azaltır.

Dosya adı `/` ile ayrılmış göreli parçalardan oluşabilir. Boş parça, `.`, `..`, ters eğik çizgi, sürücü iki noktası veya mutlak yol kabul edilmez. Aynı ad iki kez tanımlanamaz. Manifesto ada göre sıralanır.
:::

::: gorev 2 · Güvenli fixture dosyalarından SHA-256 manifestosu üret
`fixture_manifestosu_olustur(dosyalar)` işlevini yaz. Girdi liste; her dosya tam olarak `ad`, `icerik` alanlarını taşısın. İçerik stringdir. Ad, yukarıdaki güvenli göreli yol kurallarına uyan benzersiz stringdir; her parça yalnız ASCII harf, rakam, alt çizgi, tire veya nokta içerebilir. Geçersiz veride `ValueError` yükselt.

Her dosya için `{"ad":AD,"bayt":N,"sha256":HASH}` döndür. `bayt`, içeriğin UTF-8 bayt uzunluğu; `sha256`, aynı baytların küçük harf hex özetidir. Listeyi ada göre sırala, boş girdi için boş liste döndür ve girdiyi değiştirme.

```starter
def fixture_manifestosu_olustur(dosyalar):
    return []
```

```test
import copy
D = [
    {"ad": "senaryolar/enjeksiyon.json", "icerik": "{}"},
    {"ad": "metin.txt", "icerik": "ş"},
]
BEKLENEN = [
    {"ad": "metin.txt", "bayt": 2, "sha256": "ef6e788bf4e810d939be09c13bd226c4e98be8045356acfaf28db8bac285917b"},
    {"ad": "senaryolar/enjeksiyon.json", "bayt": 2, "sha256": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(D)
        sonuc = fn(D)
        if sonuc != BEKLENEN or D != once or sonuc != fn(list(reversed(D))) or fn([]) != []:
            return False
        if sonuc[0]["bayt"] != 2 or sonuc[1]["sha256"] != "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a":
            return False
        if fn([{"ad": "bos", "icerik": ""}])[0]["sha256"] != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
            return False
        for dosyalar in [
            None, {}, [None], [dict(D[0], ek=1)], [dict(D[0], icerik=None)],
            [dict(D[0], ad="")], [dict(D[0], ad="/tmp/a")],
            [dict(D[0], ad="../a")], [dict(D[0], ad="a/../b")],
            [dict(D[0], ad="a//b")], [dict(D[0], ad="a\\b")],
            [dict(D[0], ad="C:/a")], [dict(D[0], ad="a b")], [D[0], D[0]],
        ]:
            try:
                fn(dosyalar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(fixture_manifestosu_olustur), "güvenli yol, UTF-8 bayt sayısı ve SHA-256 korunmalı")
def m_yol(dosyalar):
    sonuc = fixture_manifestosu_olustur(dosyalar)
    sonuc[0]["ad"] = "../" + sonuc[0]["ad"]
    return sonuc
def m_bayt(dosyalar):
    sonuc = fixture_manifestosu_olustur(dosyalar)
    for x in sonuc:
        if x["ad"] == "metin.txt":
            x["bayt"] = 1
    return sonuc
def m_ozet(dosyalar):
    sonuc = fixture_manifestosu_olustur(dosyalar)
    sonuc[0]["sha256"] = "0" * 64
    return sonuc
for ad, mutant in [("yol sınırını bozan", m_yol), ("baytı karakter sayan", m_bayt), ("özeti değiştiren", m_ozet)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def fixture_manifestosu_olustur(dosyalar):
    import hashlib
    import re
    if not isinstance(dosyalar, list):
        raise ValueError("dosya listesi geçersiz")
    sonuc = []
    adlar = set()
    for dosya in dosyalar:
        if not isinstance(dosya, dict):
            raise ValueError("dosya geçersiz")
        if set(dosya) != {"ad", "icerik"}:
            raise ValueError("dosya şeması geçersiz")
        ad = dosya["ad"]
        icerik = dosya["icerik"]
        if not isinstance(ad, str):
            raise ValueError("dosya adı geçersiz")
        if not ad:
            raise ValueError("dosya adı boş olamaz")
        if ad.startswith("/"):
            raise ValueError("mutlak yol geçersiz")
        if "\\" in ad:
            raise ValueError("ters eğik çizgi geçersiz")
        if ":" in ad:
            raise ValueError("sürücü yolu geçersiz")
        if ad in adlar:
            raise ValueError("dosya adı yinelenemez")
        parcalar = ad.split("/")
        for parca in parcalar:
            if parca in ("", ".", ".."):
                raise ValueError("dosya parçası geçersiz")
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", parca):
                raise ValueError("dosya parçası geçersiz")
        if not isinstance(icerik, str):
            raise ValueError("içerik string olmalı")
        baytlar = icerik.encode("utf-8")
        adlar.add(ad)
        sonuc.append({"ad": ad, "bayt": len(baytlar), "sha256": hashlib.sha256(baytlar).hexdigest()})
    return sorted(sonuc, key=lambda x: x["ad"])
```

```hint
Yolu `/` parçalarına ayır ve her parçayı ayrı doğrula. SHA-256 ve uzunluk için `icerik.encode("utf-8")` sonucunu kullan.
```
:::

::: anlat Tekrarlanabilirlik koşu kayıtlarında aranır
Bir testin en az iki ayrı koşusu olmalıdır. Aynı testte tohum, girdi özeti, çıktı özeti veya durum değişirse sonuç tekrarlanabilir sayılmaz. Ayrıca bütün koşular `gecti` olmalıdır; deterministik biçimde başarısız olan test başarılı bir regresyon kanıtı değildir.

Rapor, her testin nedenlerini `tohum`, `girdi`, `cikti`, `durum` sırasıyla listeler. Koşum numarası yalnız kayıtları ayırt eder; determinizm hesabına katılmaz. Böylece aynı komutun iki kez çalıştırılmasıyla farklı fixture veya tohum kullanılması görünür olur.
:::

::: gorev 3 · Tekrarlanan koşuların determinizm raporunu çıkar
`tekrarlanabilirlik_raporu(kosular)` işlevini yaz. Her koşu tam olarak `test`, `kosum`, `tohum`, `girdi_sha256`, `cikti_sha256`, `durum` alanlarını taşısın. Test adı baş/son boşluğu olmayan boş olmayan string; koşum bool olmayan pozitif int; tohum ilk görevdeki aralıkta int; iki özet alanı tam 64 küçük hex karakteri; durum `gecti`, `kaldi` veya `hata` olmalıdır. `(test, kosum)` çifti benzersizdir ve her test en az iki koşu içermelidir. Geçersiz veride `ValueError` yükselt.

Her test için:

```text
{"test":AD,"kosum_sayisi":N,"tekrarlanabilir":BOOL,"nedenler":[NEDEN,...]}
```

Döndür. Testi ada göre sırala. Tohum, girdi, çıktı veya durum alanlarının koşular arasında farklı değerleri varsa ilgili nedeni ekle. Bütün koşular `gecti` değilse `durum` nedenine eklenir; aynı neden yinelenmez. Yalnız nedenler boşsa tekrarlanabilir true olur. Boş girdi için boş liste döndür ve girdiyi değiştirme.

```starter
def tekrarlanabilirlik_raporu(kosular):
    return []
```

```test
import copy
H1 = "a" * 64
H2 = "b" * 64
K = [
    {"test": "enjeksiyon", "kosum": 2, "tohum": 7, "girdi_sha256": H1, "cikti_sha256": H2, "durum": "gecti"},
    {"test": "enjeksiyon", "kosum": 1, "tohum": 7, "girdi_sha256": H1, "cikti_sha256": H2, "durum": "gecti"},
    {"test": "tohum-farki", "kosum": 1, "tohum": 1, "girdi_sha256": H1, "cikti_sha256": H2, "durum": "gecti"},
    {"test": "tohum-farki", "kosum": 2, "tohum": 2, "girdi_sha256": H1, "cikti_sha256": H1, "durum": "kaldi"},
]
BEKLENEN = [
    {"test": "enjeksiyon", "kosum_sayisi": 2, "tekrarlanabilir": True, "nedenler": []},
    {"test": "tohum-farki", "kosum_sayisi": 2, "tekrarlanabilir": False, "nedenler": ["tohum", "cikti", "durum"]},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once or fn(list(reversed(K))) != BEKLENEN or fn([]) != []:
            return False
        for tohum in (0, 4294967295):
            if not fn([dict(K[0], tohum=tohum), dict(K[1], tohum=tohum)])[0]["tekrarlanabilir"]:
                return False
        for kosular in [
            None, {}, [None], [dict(K[0], ek=1)],
            [dict(K[0], test=""), dict(K[1], test="")],
            [dict(K[0], test=" x"), dict(K[1], test=" x")],
            [dict(K[0], kosum=True), K[1]], [dict(K[0], kosum=0), K[1]],
            [dict(K[0], tohum=-1), K[1]], [dict(K[0], tohum=4294967296), K[1]],
            [dict(K[0], girdi_sha256="a" * 63), K[1]],
            [dict(K[0], girdi_sha256="a" * 65), K[1]],
            [dict(K[0], cikti_sha256="A" * 64), K[1]],
            [dict(K[0], durum="belirsiz"), K[1]],
            [K[0]], [K[0], K[0]], [dict(K[0], kosum=1), K[1]],
        ]:
            try:
                fn(kosular)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(tekrarlanabilirlik_raporu), "koşu tekilği, tohum, özet ve başarı durumu korunmalı")
def m_tohum(kosular):
    degisen = [dict(x, tohum=7) for x in kosular]
    return tekrarlanabilirlik_raporu(degisen)
def m_durum(kosular):
    degisen = [dict(x, durum="gecti") for x in kosular]
    return tekrarlanabilirlik_raporu(degisen)
def m_cikti(kosular):
    degisen = [dict(x, cikti_sha256="b" * 64) for x in kosular]
    return tekrarlanabilirlik_raporu(degisen)
for ad, mutant in [("tohum farkını silen", m_tohum), ("başarısızlığı başarı yapan", m_durum), ("çıktı farkını silen", m_cikti)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def tekrarlanabilirlik_raporu(kosular):
    import re
    if not isinstance(kosular, list):
        raise ValueError("koşu listesi geçersiz")
    gruplar = {}
    tekil = set()
    for k in kosular:
        if not isinstance(k, dict):
            raise ValueError("koşu geçersiz")
        if set(k) != {"test", "kosum", "tohum", "girdi_sha256", "cikti_sha256", "durum"}:
            raise ValueError("koşu şeması geçersiz")
        test = k["test"]
        if not isinstance(test, str):
            raise ValueError("test adı geçersiz")
        if not test:
            raise ValueError("test adı boş olamaz")
        if test != test.strip():
            raise ValueError("test adı boşluklu olamaz")
        if type(k["kosum"]) is not int:
            raise ValueError("koşum int olmalı")
        if k["kosum"] < 1:
            raise ValueError("koşum pozitif olmalı")
        if type(k["tohum"]) is not int:
            raise ValueError("tohum int olmalı")
        if k["tohum"] < 0:
            raise ValueError("tohum negatif olamaz")
        if k["tohum"] > 4294967295:
            raise ValueError("tohum üst sınırı aştı")
        for alan in ("girdi_sha256", "cikti_sha256"):
            if not isinstance(k[alan], str):
                raise ValueError("özet string olmalı")
            if not re.fullmatch(r"[0-9a-f]{64}", k[alan]):
                raise ValueError("özet geçersiz")
        if k["durum"] not in ("gecti", "kaldi", "hata"):
            raise ValueError("durum geçersiz")
        anahtar = (test, k["kosum"])
        if anahtar in tekil:
            raise ValueError("koşu kimliği yinelenemez")
        tekil.add(anahtar)
        gruplar.setdefault(test, []).append(k)
    rapor = []
    for test in sorted(gruplar):
        kayitlar = gruplar[test]
        if len(kayitlar) < 2:
            raise ValueError("her test en az iki koşu içermeli")
        nedenler = []
        for alan, neden in (("tohum", "tohum"), ("girdi_sha256", "girdi"), ("cikti_sha256", "cikti"), ("durum", "durum")):
            if len({x[alan] for x in kayitlar}) > 1:
                nedenler.append(neden)
        if any(x["durum"] != "gecti" for x in kayitlar) and "durum" not in nedenler:
            nedenler.append("durum")
        rapor.append({"test": test, "kosum_sayisi": len(kayitlar), "tekrarlanabilir": not nedenler, "nedenler": nedenler})
    return rapor
```

```hint
Koşuları test adına göre grupla. Dört alanın her biri için kümedeki değer sayısını karşılaştır; başarısız koşu varsa `durum` nedenini yalnız bir kez ekle.
```
:::

::: anlat Determinizm kâğıt üstünde değil, gerçek koşuyla kanıtlanır
Tekrarlanabilir bir regresyon laboratuvarının temeli determinizmdir: aynı girdi, aynı tohum ve sıcaklık 0 ile model her koşuda **aynı** çıktıyı vermeli. Değilse, bir savunmanın "işe yaradığı" bir koşuda görülüp başka koşuda kaybolabilir ve hiçbir kanıt güvenilir olmaz. Son görevde senin `tekrarlanabilirlik_raporu` işlevin, aynı istemi aynı tohumla **gerçek modele** birkaç kez koşan bir deneyin kayıtlarıyla çalışır: her koşunun çıktı SHA-256 özeti alınır ve rapor, özetlerin koşular arası aynı kalıp kalmadığına (determinizm) karar verir. Çıktı özetleri aynıysa test tekrarlanabilirdir; farklıysa `cikti` nedeni eklenir ve laboratuvar güvenilmezdir.
:::

::: gorev Gerçek deney · Gerçek koşularda determinizm raporu
`tekrarlanabilirlik_raporu(kosular)` işlevini yaz — kuralları ve çıktısı 3. görevdekiyle **aynıdır**. Deney aynı istemi aynı tohumla gerçek modele koşar, her koşunun girdi/çıktı SHA-256 özetini ve durumunu kaydeder; senin raporun bu gerçek koşuların tekrarlanabilir olup olmadığını belirler.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def tekrarlanabilirlik_raporu(kosular):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_05 as deney
    deney.goster(tekrarlanabilirlik_raporu)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "referans_rapor", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("tekrarlanabilirlik_raporu")
from sandbox import ai_gercek_ai_savunma_05 as D
H = "a" * 64
H2 = "b" * 64
KO = [{"test": "t", "kosum": 1, "tohum": 7, "girdi_sha256": H, "cikti_sha256": H, "durum": "gecti"},
      {"test": "t", "kosum": 2, "tohum": 7, "girdi_sha256": H, "cikti_sha256": H, "durum": "gecti"}]
FARK = [KO[0], dict(KO[1], cikti_sha256=H2)]
def sozlesme(f):
    try:
        if f([dict(k) for k in KO]) != D.referans_rapor(KO) or f([dict(k) for k in FARK]) != D.referans_rapor(FARK) or f([]) != []:
            return False
        for ol in [None, [None], [KO[0]], [dict(KO[0], ek=1)], [KO[0], KO[0]], [dict(KO[0], kosum=0)], [dict(KO[0], tohum=-1)],
                   [dict(KO[0], cikti_sha256="xyz")], [dict(KO[0], durum="belirsiz")], [dict(KO[0], test="")]]:
            try:
                f(ol)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "determinizm raporu (çıktı/durum farkı, en az iki koşu) doğru; geçersiz girdi reddedilmeli")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(r["rapor"] == D.referans_rapor(r["kosular"]), "determinizm raporu bağımsız hesapla aynı")
    beklenen = len(set(r["ciktilar"])) == 1
    kontrol(r["rapor"][0]["tekrarlanabilir"] == beklenen, f"rapor gerçek çıktı tutarlılığını yansıttı: {len(set(r['ciktilar']))} benzersiz çıktı → tekrarlanabilir {r['rapor'][0]['tekrarlanabilir']}")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-lab", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-05",
                                       "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): aynı istem + tohum={r['tohum']} + sıcaklık 0 ile {oz['tekrar']} koşu → {oz['benzersiz_cikti']} benzersiz çıktı; "
             f"tekrarlanabilir: {oz['tekrarlanabilir']} (nedenler {oz['nedenler']}). Determinizm regresyon laboratuvarının temelidir.")
```

```solution
import ai_lab

def tekrarlanabilirlik_raporu(kosular):
    import re
    if not isinstance(kosular, list):
        raise ValueError("koşu listesi geçersiz")
    gruplar, ciftler = {}, set()
    for k in kosular:
        if not isinstance(k, dict) or set(k) != {"test", "kosum", "tohum", "girdi_sha256", "cikti_sha256", "durum"}:
            raise ValueError("koşu şeması geçersiz")
        if not isinstance(k["test"], str) or not k["test"] or k["test"] != k["test"].strip():
            raise ValueError("test adı geçersiz")
        if isinstance(k["kosum"], bool) or not isinstance(k["kosum"], int) or k["kosum"] < 1:
            raise ValueError("koşum geçersiz")
        if isinstance(k["tohum"], bool) or not isinstance(k["tohum"], int) or not 0 <= k["tohum"] <= 4294967295:
            raise ValueError("tohum geçersiz")
        for alan in ("girdi_sha256", "cikti_sha256"):
            if not isinstance(k[alan], str) or not re.fullmatch(r"[0-9a-f]{64}", k[alan]):
                raise ValueError("özet geçersiz")
        if k["durum"] not in ("gecti", "kaldi", "hata"):
            raise ValueError("durum geçersiz")
        cift = (k["test"], k["kosum"])
        if cift in ciftler:
            raise ValueError("koşu çifti yinelenemez")
        ciftler.add(cift)
        gruplar.setdefault(k["test"], []).append(k)
    for test, runs in gruplar.items():
        if len(runs) < 2:
            raise ValueError("her test en az iki koşu içermeli")
    out = []
    for test in sorted(gruplar):
        runs = gruplar[test]
        nedenler = []
        for alan, ad in (("tohum", "tohum"), ("girdi_sha256", "girdi"), ("cikti_sha256", "cikti"), ("durum", "durum")):
            if len({r[alan] for r in runs}) > 1:
                nedenler.append(ad)
        if any(r["durum"] != "gecti" for r in runs) and "durum" not in nedenler:
            nedenler.append("durum")
        out.append({"test": test, "kosum_sayisi": len(runs), "tekrarlanabilir": not nedenler, "nedenler": nedenler})
    return out

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_05 as deney
    deney.goster(tekrarlanabilirlik_raporu)
```

```hint
Bu işlev 3. görevdeki `tekrarlanabilirlik_raporu` ile birebir aynıdır; tek fark, koşuların gerçek model çalıştırmalarından gelmesidir. Her testi grupla, en az iki koşu iste; tohum/girdi/çıktı/durum alanlarından koşular arası farklı olanı neden olarak ekle, başarısız koşuda `durum`'u bir kez ekle.
```
:::
