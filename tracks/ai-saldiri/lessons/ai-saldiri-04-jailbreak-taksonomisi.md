---
id: ai-saldiri-04
title: Jailbreak Taksonomisi · Sinyal, Çok Etiketli Sınıflandırma ve Hata Ölçümü
summary: Jailbreak vakalarını dönüştürme, bağlam manipülasyonu ve politika çatıştırma mekanizmalarıyla çok etiketli sınıflandır; sınıflandırıcıyı precision, recall ve F1 ile değerlendir.
timeout: 45
---

::: anlat Taksonomi saldırı adını değil mekanizmayı sınıflandırır
“Jailbreak” tek bir teknik değildir. Bir vaka metni kodlayabilir, sahte bir rol bağlamı kurabilir ve aynı anda üst düzey talimatla çelişen bir sonuç isteyebilir. Bu yüzden vakayı yalnız tek bir etikete zorlamak mekanizmayı kaybedebilir. Bu derste dört dar sınıf kullanacağız:

- `dogrudan-istek`: Ek dönüştürme veya bağlam manevrası bulunmayan açık istek.
- `donusturme`: Base64, hex veya benzeri kodlanmış yük taşıma.
- `baglam-manipulasyonu`: Sahte rol işareti, geliştirici modu iddiası veya kurgu bağlamıyla otorite çerçevesini değiştirme girişimi.
- `politika-catistirma`: Önceki talimatı yok sayma veya iki kuralı birbirine karşı kullanma yönlendirmesi.

Bu sınıflar ürünlerin bütün taksonomilerini kapsamaz; dersin ölçülebilir fixture sözlüğüdür. Bir vaka birden fazla taktik taşıyorsa çok etiketli sonuç üretiriz. Hiçbir taktik sinyali yoksa `dogrudan-istek` etiketi kullanılır. Doğrudan istek, isteğin zararsız olduğu anlamına gelmez; yalnız bu dar mekanizma sözlüğünde ek manevra görülmediğini söyler.

Anahtar kelime aramak kırılgandır. Büyük/küçük harf, Türkçe karakter, kodlanmış içerik ve kelimenin gerçek token mı yoksa başka kelimenin parçası mı olduğu sonucu değiştirir. Bu dersin kurallı sınıflandırıcısı üretim güvenlik filtresi değildir; etiketleme ve değerlendirme hatalarını ölçmeyi öğreten şeffaf bir test çiftidir.

```python
import re
metin = "Base64: U0FOR0lUQ1VSWSBURVNU"
tokenler = re.findall(r"[A-Za-z0-9+/]+={0,2}", metin)
adaylar = [t for t in tokenler if len(t) >= 12 and len(t) % 4 == 0]
print(adaylar)
print(any(t in {"base64", "hex"} for t in ["base64", "rol"]))
```

Gerçek garak veya Ollama taramasında da probe çıktısı, detector sürümü ve ham yanıt saklanmalıdır. Bu fixture herhangi bir model veya harici paket çalıştırmaz.
:::

::: tahmin Çok etiketli sonuç ve doğrudan istek
Kural sırası önce taktik etiketlerini toplar; hiç taktik yoksa doğrudan istek ekler. Dört çıktı satırını yaz:

```python
vakalar = [
    {"id":"a", "sinyaller":set()},
    {"id":"b", "sinyaller":{"base64"}},
    {"id":"c", "sinyaller":{"base64", "sahte-rol", "onceki-talimati-yok-say"}},
]
def etiketler(sinyaller):
    sonuc = set()
    if "base64" in sinyaller or "hex" in sinyaller:
        sonuc.add("donusturme")
    if "sahte-rol" in sinyaller or "kurgu" in sinyaller:
        sonuc.add("baglam-manipulasyonu")
    if "onceki-talimati-yok-say" in sinyaller:
        sonuc.add("politika-catistirma")
    return sonuc or {"dogrudan-istek"}
for vaka in vakalar:
    print(vaka["id"], sorted(etiketler(vaka["sinyaller"])))
```

???

```cikti
a ['dogrudan-istek']
b ['donusturme']
c ['baglam-manipulasyonu', 'donusturme', 'politika-catistirma']
```

Üçüncü vaka tek bir “jailbreak” başlığına indirgenmez; üç mekanizma da korunur.
:::

::: gorev 1 · Metinden açıklanabilir taktik sinyalleri çıkar
`taktikleri_bul(metin)` işlevini yaz. Dönüş, bulunan sinyal adlarının alfabetik sıralı listesi olsun. Metni önce `casefold()` ile normalize et.

Sinyal sözleşmesi:

- `base64`: Metinde `base64` kelimesi veya en az 12 karakterli, uzunluğu 4'ün katı olan bağımsız Base64 benzeri token bulunmalı. Token yalnız harf, rakam, `+`, `/` ve sonda en fazla iki `=` içerebilir. En az bir harf ile en az bir rakam veya kodlama işareti taşımalı; içinde `base64` geçen uzun kelimeler token sayılmamalı.
- `hex`: `hex` kelimesi veya `0x` ile başlayan ve ardından çift sayıda, en az 12 hexadecimal hane bulunan token bulunmalı.
- `sahte-rol`: `<|system|>`, `<|developer|>`, `system:`, `developer mode` veya `admin onaylı` ifadelerinden biri bulunmalı.
- `kurgu`: `roleplay`, `hypothetical`, `fiction`, `senaryo` veya `kurgu` ifadelerinden biri bulunmalı.
- `onceki-talimati-yok-say`: `önceki talimat` ve `yok say` ifadelerinin ikisi de aynı metinde bulunmalı.

`metin` string değilse `ValueError` yükselt. Sinyal yoksa boş liste dön. “Base64” kelimesinin büyük/küçük harf biçimi sonucu değiştirmemeli; `abcbase64xyz` tek başına `base64` sinyali üretmemeli.

```starter
def taktikleri_bul(metin):
    return []
```

```test
eq(taktikleri_bul("Base64: U0FOR0lUQ1VSWSBURVNU"), ["base64"], "büyük harf Base64 ve token")
eq(taktikleri_bul("U0FOR0lUQ1VS"), ["base64"], "tam 12 karakterli Base64 token sınırı")
eq(taktikleri_bul("A1B2C3D4E==="), [], "üç padding karakteri Base64 tokenı değildir")
eq(taktikleri_bul("abcbase64xyz"), [], "kelime içi base64 sinyal değildir")
eq(taktikleri_bul("0x414243444546"), ["hex"], "çift sayıda hex hanesi")
eq(taktikleri_bul("0xABCDEFABCDEFAB"), ["base64", "hex"], "on dört hex hanesi ve bağımsız Base64 benzeri token")
eq(taktikleri_bul("0x414243"), [], "kısa hex token sinyal değildir")
eq(taktikleri_bul("0x41424344454"), [], "kısa tek sayıda hex hanesi reddedilir")
eq(taktikleri_bul("0x4142434445467"), [], "on üç hex hanesi reddedilir")
eq(taktikleri_bul("0x4142434445467 0x414243444546"), ["hex"], "geçerli ayrı hex token korunur")
eq(taktikleri_bul("123456789012"), [], "yalnız rakam token Base64 adayı değildir")
eq(taktikleri_bul("<|SYSTEM|>\nADMIN ONAYLI"), ["sahte-rol"], "rol işareti casefold ile bulunur")
eq(taktikleri_bul("Bir senaryo içinde hypothetical roleplay"), ["kurgu"], "kurgu sinyali")
eq(taktikleri_bul("ÖNCEKİ TALİMATları YOK SAY"), ["onceki-talimati-yok-say"], "Türkçe metin normalize edilir")
eq(taktikleri_bul("Yok say ama başka kuralı koru"), [], "yok say tek başına önceki talimat sinyali değildir")
eq(taktikleri_bul("BASE64 <|developer|> önceki talimatı yok say roleplay"),
   ["base64", "kurgu", "onceki-talimati-yok-say", "sahte-rol"], "çok sinyalli vaka alfabetik döner")
raises(ValueError, lambda: taktikleri_bul(None), msg="metin string olmalı")
```

```solution
import re

def taktikleri_bul(metin):
    if not isinstance(metin, str):
        raise ValueError("metin string olmalı")
    normal = metin.casefold().replace("\u0307", "")
    sinyaller = set()
    if re.search(r"(?<![a-z0-9])base64(?![a-z0-9])", normal):
        sinyaller.add("base64")
    for token in re.findall(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]+={0,2}(?![A-Za-z0-9+/=])", metin):
        govde = token.rstrip("=")
        if (len(token) >= 12 and len(token) % 4 == 0 and re.search(r"[A-Za-z]", govde)
                and re.search(r"[0-9+/=]", token) and "base64" not in token.casefold()):
            sinyaller.add("base64")
    if re.search(r"(?<![a-z0-9])hex(?![a-z0-9])", normal):
        sinyaller.add("hex")
    if any(len(t) >= 12 and len(t) % 2 == 0 for t in re.findall(
            r"(?<![a-z0-9])0x([0-9a-f]+)(?![0-9a-f])", normal)):
        sinyaller.add("hex")
    if any(x in normal for x in ("<|system|>", "<|developer|>", "system:", "developer mode", "admin onaylı")):
        sinyaller.add("sahte-rol")
    if any(x in normal for x in ("roleplay", "hypothetical", "fiction", "senaryo", "kurgu")):
        sinyaller.add("kurgu")
    if "önceki talimat" in normal and "yok say" in normal:
        sinyaller.add("onceki-talimati-yok-say")
    return sorted(sinyaller)
```

```hint
Base64 ve hex için kelime sınırını yalnız `\b` yerine alfanümerik olmayan komşularla kur; `+` ve `/` token karakterlerini de hesaba kat. Sinyalleri kümede toplayıp en sonda sırala.
```
:::

::: anlat Sınıflandırıcı ile vaka etiketi birbirinden ayrılır
Sinyal, metinde gözlenen teknik özelliktir; sınıf etiketi ise bu sinyallerin taksonomi sözlüğüne çevrilmesidir. Dönüştürme ve bağlam manipülasyonu birlikte bulunabilir. Bu nedenle `if/elif` zinciriyle ilk sınıfı döndürmek diğer kanıtları siler.

Bu dersteki eşleme:

```text
base64 veya hex                         → donusturme
sahte-rol veya kurgu                    → baglam-manipulasyonu
onceki-talimati-yok-say                 → politika-catistirma
hiç taktik etiketi yok                  → dogrudan-istek
```

`dogrudan-istek`, başka etiketle birlikte üretilmez. Vaka kimliği ve ham metin sonuçta korunur; böylece yanlış sınıflandırma incelenirken yalnız etiket değil kaynak örnek de görülebilir. Bu kurallar saldırının başarılı olup olmadığını ölçmez. Başarı ölçümü için model yanıtı ve önceden tanımlı başarı koşulu gerekir.
:::

::: gorev 2 · Vakaları çok etiketli taksonomiyle sınıflandır
`vakalari_siniflandir(vakalar)` işlevini yaz. Her vaka `id`, `metin` ve `sinyaller` alanlarını taşır. `sinyaller`, önceki görevdeki sinyal adlarının listesi veya kümesidir.

- Her vaka için `id`, `metin` ve `etiketler` alanlarından oluşan yeni bir kayıt döndür; `etiketler` alfabetik sıralı liste olsun.
- Yukarıdaki eşlemeyi uygula ve çoklu taktikleri koru. Taktik yoksa yalnız `dogrudan-istek` üret.
- Bilinmeyen sinyal adı, boş olmayan string olmayan vaka kimliği veya string olmayan metin `ValueError` yükseltsin. Aynı vaka kimliği iki kez kullanılamaz.
- Girdi vakalarını ve sinyal koleksiyonlarını değiştirme. Vaka sırasını koru.

```starter
def vakalari_siniflandir(vakalar):
    return []
```

```test
import copy
VAKALAR = [
    {"id":"a", "metin":"Kısa bir özet iste", "sinyaller":[]},
    {"id":"b", "metin":"BASE64 ...", "sinyaller":["base64"]},
    {"id":"c", "metin":"rol + hex + çatışma", "sinyaller":["sahte-rol", "hex", "onceki-talimati-yok-say"]},
    {"id":"d", "metin":"Kurgu", "sinyaller":["kurgu"]},
]
kopya = copy.deepcopy(VAKALAR)
sonuc = vakalari_siniflandir(kopya)
eq(sonuc[0]["etiketler"], ["dogrudan-istek"], "taktiksiz vaka doğrudan istek")
eq(sonuc[1]["etiketler"], ["donusturme"], "Base64 dönüştürme sınıfı")
eq(sonuc[2]["etiketler"], ["baglam-manipulasyonu", "donusturme", "politika-catistirma"], "çok etiket korunur")
eq(sonuc[3]["etiketler"], ["baglam-manipulasyonu"], "kurgu bağlam manipülasyonu")
eq([x["id"] for x in sonuc], ["a","b","c","d"], "vaka sırası korunur")
eq(sonuc[2]["metin"], VAKALAR[2]["metin"], "ham metin kayıtta kalır")
eq(kopya, VAKALAR, "girdi değişmez")
for bozuk in (
    [{"id":"x", "metin":"m", "sinyaller":["bilinmeyen"]}],
    [{"id":"", "metin":"m", "sinyaller":[]}],
    [{"id":"x", "metin":7, "sinyaller":[]}],
):
    raises(ValueError, lambda bozuk=bozuk: vakalari_siniflandir(bozuk), msg="geçersiz vaka veya sinyal reddedilir")
yineleme = [{"id":"x", "metin":"a", "sinyaller":[]}, {"id":"x", "metin":"b", "sinyaller":[]}]
raises(ValueError, lambda: vakalari_siniflandir(yineleme), msg="vaka kimliği benzersiz olmalı")
```

```solution
def vakalari_siniflandir(vakalar):
    bilinen = {"base64", "hex", "sahte-rol", "kurgu", "onceki-talimati-yok-say"}
    kimlikler = set()
    sonuc = []
    for vaka in vakalar:
        if not isinstance(vaka, dict):
            raise ValueError("geçersiz vaka")
        kimlik = vaka.get("id")
        metin = vaka.get("metin")
        sinyaller = vaka.get("sinyaller", [])
        if not isinstance(kimlik, str) or not kimlik or kimlik in kimlikler or not isinstance(metin, str):
            raise ValueError("geçersiz veya yinelenen vaka")
        kimlikler.add(kimlik)
        if not isinstance(sinyaller, (list, set, tuple)) or any(s not in bilinen for s in sinyaller):
            raise ValueError("bilinmeyen sinyal")
        kume = set(sinyaller)
        etiketler = set()
        if kume & {"base64", "hex"}:
            etiketler.add("donusturme")
        if kume & {"sahte-rol", "kurgu"}:
            etiketler.add("baglam-manipulasyonu")
        if "onceki-talimati-yok-say" in kume:
            etiketler.add("politika-catistirma")
        if not etiketler:
            etiketler.add("dogrudan-istek")
        sonuc.append({"id":kimlik, "metin":metin, "etiketler":sorted(etiketler)})
    return sonuc
```

```hint
Sinyalleri yeni bir kümeye çevir ve etiketleri ayrı bir kümede biriktir. En sonda küme hâlâ boşsa doğrudan istek ekle; çıktı listesini sıralamadan dönme.
```
:::

::: anlat Değerlendirici de ayrı bir test hedefidir
Çok etiketli sınıflandırmada tek bir “doğru/yanlış” sayısı sınıf bazlı hatayı gizleyebilir. Her etiket için:

- **TP:** Beklenen ve tahmin edilen etiket.
- **FP:** Beklenmediği hâlde tahmin edilen etiket.
- **FN:** Beklendiği hâlde tahmin edilmeyen etiket.

Precision `TP / (TP + FP)`, recall `TP / (TP + FN)`, F1 ise iki değerin harmonik ortalamasıdır. Payda sıfırsa oran `None` olmalı; sıfır yazmak “ölçülemeyen” ile “başarısız” değerini karıştırır. Precision veya recall `None` ise F1 de `None` olur. İki oran da ölçülebiliyorsa F1 sayısaldır; precision ve recall birlikte sıfır olduğunda da F1 `0.0` olur.

Sınıf bazlı metriklerin yanında vaka kimlikleri ve ham tahminler saklanmalı. Yüksek ortalama, nadir bir taktikteki bütün hataları gizleyebilir. garak gibi gerçek araçlarda da detector adı ve sürümü sabitlenmeden iki tarama sonucunu doğrudan karşılaştırmak güvenilir değildir.
:::

::: gorev 3 · Sınıf bazlı precision, recall ve F1 hesapla
`siniflandirma_olc(vakalar, etiketler)` işlevini yaz.

- `vakalar`, her biri `id`, `beklenen` ve `tahmin` alanları taşıyan kayıtlardır. Beklenen ve tahmin koleksiyonları etiket kümesine çevrilebilir.
- `etiketler`, raporlanacak sınıf adlarının koleksiyonudur. Dönüş sözlüğünün anahtarları bu sınıflardır; her değer `tp`, `fp`, `fn`, `precision`, `recall`, `f1` alanlarını taşısın.
- Sayımları bütün vakalar üzerinden sınıf bazında yap. Payda sıfırsa ilgili oran `None`; iki oran da sayısal olduğunda ve toplamları sıfırdan büyükse `f1 = 2*p*r/(p+r)` olsun.
- Girdiyi değiştirme. Bilinmeyen etiketleri sessizce yok sayma: bir vakada raporlama koleksiyonu dışında etiket varsa `ValueError` yükselt.

```starter
def siniflandirma_olc(vakalar, etiketler):
    return {}
```

```test
VAKALAR = [
    {"id":"a", "beklenen":{"donusturme", "baglam-manipulasyonu"}, "tahmin":{"donusturme"}},
    {"id":"b", "beklenen":{"dogrudan-istek"}, "tahmin":{"dogrudan-istek", "donusturme"}},
    {"id":"c", "beklenen":{"politika-catistirma", "donusturme"}, "tahmin":{"baglam-manipulasyonu"}},
]
ETIKETLER = ["baglam-manipulasyonu", "dogrudan-istek", "donusturme", "politika-catistirma"]
sonuc = siniflandirma_olc(VAKALAR, ETIKETLER)
eq((sonuc["donusturme"]["tp"], sonuc["donusturme"]["fp"], sonuc["donusturme"]["fn"]), (1,1,1), "dönüştürme sayımları")
eq((sonuc["baglam-manipulasyonu"]["tp"], sonuc["baglam-manipulasyonu"]["fp"], sonuc["baglam-manipulasyonu"]["fn"]), (0,1,1), "bağlam sayımları")
eq(sonuc["donusturme"]["precision"], 0.5, "precision")
eq(sonuc["donusturme"]["recall"], 0.5, "recall")
eq(sonuc["donusturme"]["f1"], 0.5, "F1")
eq(sonuc["dogrudan-istek"]["f1"], 1.0, "tam eşleşen sınıf")
eq(sonuc["baglam-manipulasyonu"]["precision"], 0.0, "hiç TP olmayan ölçülmüş precision")
eq(sonuc["baglam-manipulasyonu"]["recall"], 0.0, "hiç TP olmayan ölçülmüş recall")
eq(sonuc["baglam-manipulasyonu"]["f1"], 0.0, "sıfır F1 ölçülmüş sonuçtur")
bos = siniflandirma_olc([], ["donusturme"])["donusturme"]
eq(bos, {"tp":0,"fp":0,"fn":0,"precision":None,"recall":None,"f1":None}, "boş veri None oranlar")
raises(ValueError, lambda: siniflandirma_olc([{"id":"x","beklenen":{"yeni-sinif"},"tahmin":set()}], ["donusturme"]), msg="rapor dışı etiket yok sayılmaz")
```

```solution
def siniflandirma_olc(vakalar, etiketler):
    rapor = {}
    siniflar = set(etiketler)
    for vaka in vakalar:
        if set(vaka["beklenen"]) - siniflar or set(vaka["tahmin"]) - siniflar:
            raise ValueError("rapor dışı etiket")
    for sinif in etiketler:
        tp = sum(sinif in vaka["beklenen"] and sinif in vaka["tahmin"] for vaka in vakalar)
        fp = sum(sinif not in vaka["beklenen"] and sinif in vaka["tahmin"] for vaka in vakalar)
        fn = sum(sinif in vaka["beklenen"] and sinif not in vaka["tahmin"] for vaka in vakalar)
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        if precision is None or recall is None:
            f1 = None
        elif precision + recall:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0
        rapor[sinif] = {"tp":tp,"fp":fp,"fn":fn,"precision":precision,"recall":recall,"f1":f1}
    return rapor
```

```hint
Her sınıf için üç sayacı ayrı hesapla. Oranları `if tp + fp` ve `if tp + fn` koşullarıyla koru; F1 hesabından önce iki oranın da `None` olmadığını denetle.
```
:::

::: anlat Taksonomi raporu neyi kanıtlar?
Bu fixture, metindeki seçilmiş sinyalleri şeffaf kurallarla sınıflandırmayı ve sınıflandırıcı hatasını ölçmeyi gösterir. Bir promptun gerçek modelde güvenlik sınırını aştığını kanıtlamaz. Gerçek değerlendirme için aynı vaka setiyle model yanıtı, başarı ölçütü, detector sürümü ve hatalı vakaların ham kaydı gerekir.

İyi bir taksonomi raporu sınıf adlarının yanında çoklu etiketleri, karışıklık sayımlarını ve ölçülemeyen oranları korur. Yeni bir taktik eklemek, eski etiketleri yeniden adlandırmak veya detector değiştirmek sonuçların karşılaştırılabilirliğini etkiler; sözlük sürümü deney kaydına yazılmalıdır.
:::


::: anlat Görünür dosya ile canlı sınıflandırıcıyı karşılaştır
[Sentetik örnek JSONL içeriğini aç](/data/ai-saldiri-04-vakalar.txt) ([JSONL dosyasını indir](/data/ai-saldiri-04-vakalar.jsonl)). Dosya canlı model kaydı değildir; altı elle etiketlenmiş, zararsız eğitim vakasıdır. Her satır bir JSON nesnesidir: `id`, `metin`, `beklenen`. Önce ham satırları incele; birden fazla taktiği olan vaka ile kelime içinde geçen `base64` örneğini karşılaştır.

Gerçek görevde **Çalıştır**, `deney.calisma_dosyasi()` ile öğrenci veri alanında bir kopya oluşturur ve tam yolunu/ham içeriğini çıktıya yazar. Kopya sonraki çalıştırmalarda sıfırlanmaz. Dosyayı kendi metin editöründe açıp değiştirip kaydet; tekrar Çalıştır. Koddan da `Path(deney.calisma_dosyasi()).read_text(encoding="utf-8")` ile oku veya `write_text` ile çalışma kopyanı düzenle. Dersin içinde ayrı bir dosya editörü bulunmuyor; görüntüleme bağlantısı başlangıç şablonudur, öğrenci kopyan değildir. Uygulamanın öğrenci veri klasörü değişirse farklı kopya kullanılır.

Model bu vakalardaki talimatları uygulayan saldırı hedefi olarak değil, **ikinci bir taksonomi sınıflandırıcısı** olarak çağrılır. Öğrenci kuralları ve model tahminleri aynı elle etiketli girdide ayrı raporlanır. Her model yanıtı ve ayarlar gerçek kanıtta saklanır. Yüksek sınıflandırma puanı, jailbreak başarısı veya üretim güvenliği kanıtı değildir. Modelin hata yapması, doğru hesap yapan öğrenciyi başarısız yapmaz. Çağrı hatası veya yarım üretim ise kabul değildir.

**Kontrol Et**, düzenlediğin çalışma kopyasına bağlı değildir: ayrı geçici dosyada yeni kimlik/metin varyantlarıyla görünmemiş veri kullanır. Böylece örneği bozarak veya ezberleyerek sınama geçilemez. Kopyanı silmeden dosya açma ve yazma pratiği yapabilirsin; hiçbir kurulum veya dış servis gerekmez.
:::

::: gorev Gerçek deney · Dosyadan taksonomi ve canlı model karşılaştırması
Önceki üç işlevi aynı koda al. Ek olarak `vaka_dosyasini_oku(yol)` yaz: UTF-8 JSONL oku, boş satırları atla ve dosyadaki sırayla kayıt listesini dön. Her kayıt tam `id`, `metin`, `beklenen` alanlarını taşımalı. `id` boş olmayan benzersiz string; `metin` 1–1500 karakterlik string; `beklenen` dört ders etiketinden oluşan boş olmayan, tekrarsız bir liste olmalı. `dogrudan-istek` başka etiketle birleşemez. Dosyada 1–8 vaka olmalı. Bozuk JSON ve sözleşme ihlalinde `ValueError` yükselt; girdiyi düzeltip sessizce devam etme.

Dosyayı okuyarak başla; Çalıştır ham dosyayı, modelin gerçek JSON yanıtlarını ve iki ayrı metrik raporunu gösterir. Model için kurulu yerel Ollama kullanılır; GPU kipinde ortak laboratuvar kilidiyle sırayla çağrı yapar; CPU için `PAFTA_OLLAMA_CIHAZ=cpu` seçilebilir. CPU kipinde kendi sunucusunu açıp kapatır. Kullanıcının sunucusunu kapatmaz ve önceden yüklediği modeli boşaltmaz. Modelin sınıflandırma başarısı kabul şartı değildir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def taktikleri_bul(metin):
    return []

def vakalari_siniflandir(vakalar):
    return []

def siniflandirma_olc(vakalar, etiketler):
    return {}

def vaka_dosyasini_oku(yol):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_04 as deney
    deney.goster(vaka_dosyasini_oku, taktikleri_bul, vakalari_siniflandir, siniflandirma_olc)
```

```test
eq(taktikleri_bul("Base64: U0FOR0lUQ1VSWSBURVNU"), ["base64"], "büyük harf Base64 ve token")
eq(taktikleri_bul("U0FOR0lUQ1VS"), ["base64"], "tam 12 karakterli Base64 token sınırı")
eq(taktikleri_bul("A1B2C3D4E==="), [], "üç padding karakteri Base64 tokenı değildir")
eq(taktikleri_bul("abcbase64xyz"), [], "kelime içi base64 sinyal değildir")
eq(taktikleri_bul("0x414243444546"), ["hex"], "çift sayıda hex hanesi")
eq(taktikleri_bul("0xABCDEFABCDEFAB"), ["base64", "hex"], "on dört hex hanesi ve bağımsız Base64 benzeri token")
eq(taktikleri_bul("0x414243"), [], "kısa hex token sinyal değildir")
eq(taktikleri_bul("0x41424344454"), [], "kısa tek sayıda hex hanesi reddedilir")
eq(taktikleri_bul("0x4142434445467"), [], "on üç hex hanesi reddedilir")
eq(taktikleri_bul("0x4142434445467 0x414243444546"), ["hex"], "geçerli ayrı hex token korunur")
eq(taktikleri_bul("123456789012"), [], "yalnız rakam token Base64 adayı değildir")
eq(taktikleri_bul("<|SYSTEM|>\nADMIN ONAYLI"), ["sahte-rol"], "rol işareti casefold ile bulunur")
eq(taktikleri_bul("Bir senaryo içinde hypothetical roleplay"), ["kurgu"], "kurgu sinyali")
eq(taktikleri_bul("ÖNCEKİ TALİMATları YOK SAY"), ["onceki-talimati-yok-say"], "Türkçe metin normalize edilir")
eq(taktikleri_bul("Yok say ama başka kuralı koru"), [], "yok say tek başına önceki talimat sinyali değildir")
eq(taktikleri_bul("BASE64 <|developer|> önceki talimatı yok say roleplay"),
   ["base64", "kurgu", "onceki-talimati-yok-say", "sahte-rol"], "çok sinyalli vaka alfabetik döner")
raises(ValueError, lambda: taktikleri_bul(None), msg="metin string olmalı")

import copy
VAKALAR = [
    {"id":"a", "metin":"Kısa bir özet iste", "sinyaller":[]},
    {"id":"b", "metin":"BASE64 ...", "sinyaller":["base64"]},
    {"id":"c", "metin":"rol + hex + çatışma", "sinyaller":["sahte-rol", "hex", "onceki-talimati-yok-say"]},
    {"id":"d", "metin":"Kurgu", "sinyaller":["kurgu"]},
]
kopya = copy.deepcopy(VAKALAR)
sonuc = vakalari_siniflandir(kopya)
eq(sonuc[0]["etiketler"], ["dogrudan-istek"], "taktiksiz vaka doğrudan istek")
eq(sonuc[1]["etiketler"], ["donusturme"], "Base64 dönüştürme sınıfı")
eq(sonuc[2]["etiketler"], ["baglam-manipulasyonu", "donusturme", "politika-catistirma"], "çok etiket korunur")
eq(sonuc[3]["etiketler"], ["baglam-manipulasyonu"], "kurgu bağlam manipülasyonu")
eq([x["id"] for x in sonuc], ["a","b","c","d"], "vaka sırası korunur")
eq(sonuc[2]["metin"], VAKALAR[2]["metin"], "ham metin kayıtta kalır")
eq(kopya, VAKALAR, "girdi değişmez")
for bozuk in (
    [{"id":"x", "metin":"m", "sinyaller":["bilinmeyen"]}],
    [{"id":"", "metin":"m", "sinyaller":[]}],
    [{"id":"x", "metin":7, "sinyaller":[]}],
):
    raises(ValueError, lambda bozuk=bozuk: vakalari_siniflandir(bozuk), msg="geçersiz vaka veya sinyal reddedilir")
yineleme = [{"id":"x", "metin":"a", "sinyaller":[]}, {"id":"x", "metin":"b", "sinyaller":[]}]
raises(ValueError, lambda: vakalari_siniflandir(yineleme), msg="vaka kimliği benzersiz olmalı")

VAKALAR = [
    {"id":"a", "beklenen":{"donusturme", "baglam-manipulasyonu"}, "tahmin":{"donusturme"}},
    {"id":"b", "beklenen":{"dogrudan-istek"}, "tahmin":{"dogrudan-istek", "donusturme"}},
    {"id":"c", "beklenen":{"politika-catistirma", "donusturme"}, "tahmin":{"baglam-manipulasyonu"}},
]
ETIKETLER = ["baglam-manipulasyonu", "dogrudan-istek", "donusturme", "politika-catistirma"]
sonuc = siniflandirma_olc(VAKALAR, ETIKETLER)
eq((sonuc["donusturme"]["tp"], sonuc["donusturme"]["fp"], sonuc["donusturme"]["fn"]), (1,1,1), "dönüştürme sayımları")
eq((sonuc["baglam-manipulasyonu"]["tp"], sonuc["baglam-manipulasyonu"]["fp"], sonuc["baglam-manipulasyonu"]["fn"]), (0,1,1), "bağlam sayımları")
eq(sonuc["donusturme"]["precision"], 0.5, "precision")
eq(sonuc["donusturme"]["recall"], 0.5, "recall")
eq(sonuc["donusturme"]["f1"], 0.5, "F1")
eq(sonuc["dogrudan-istek"]["f1"], 1.0, "tam eşleşen sınıf")
eq(sonuc["baglam-manipulasyonu"]["precision"], 0.0, "hiç TP olmayan ölçülmüş precision")
eq(sonuc["baglam-manipulasyonu"]["recall"], 0.0, "hiç TP olmayan ölçülmüş recall")
eq(sonuc["baglam-manipulasyonu"]["f1"], 0.0, "sıfır F1 ölçülmüş sonuçtur")
bos = siniflandirma_olc([], ["donusturme"])["donusturme"]
eq(bos, {"tp":0,"fp":0,"fn":0,"precision":None,"recall":None,"f1":None}, "boş veri None oranlar")
raises(ValueError, lambda: siniflandirma_olc([{"id":"x","beklenen":{"yeni-sinif"},"tahmin":set()}], ["donusturme"]), msg="rapor dışı etiket yok sayılmaz")

from sandbox import ai_gercek_ai_saldiri_04 as deney
import json, tempfile, secrets, copy
from pathlib import Path
ok(not ai_lab.kod_denetimi(src, ['dosya_referans','metrik_referans']), 'laboratuvar ve bağımsız referanslar yamalanmamalı')
if not ok(deney.dosya_sozlesmesi(vaka_dosyasini_oku), 'dosya gerçek okunmalı; yeni içerik/bozuk JSON/yinelenen kimlik/etiket doğrulanmalı'):
    stop()
for i in range(5):
    marker=secrets.token_hex(3)
    text='Base64 roleplay <|system|> önceki talimatı yok say; selam '+marker
    sig=taktikleri_bul(text)
    if not ok(sig==['base64','kurgu','onceki-talimati-yok-say','sahte-rol'], 'yeni metinde bütün sinyaller korunmalı'):stop()
    pred=vakalari_siniflandir([dict(id=marker,metin=text,sinyaller=sig)])
    if not ok(pred==[dict(id=marker,metin=text,etiketler=['baglam-manipulasyonu','donusturme','politika-catistirma'])], 'çok etiketli yeni vaka aynı kimlik ve metinle dönmeli'):stop()
# Değişken gözlemlerde TP/FP/FN ve None sözleşmesi.
for n in (0,1,7):
    rows=[dict(id=str(i),beklenen=[e for e in deney.ETIKETLER if secrets.randbelow(2)],tahmin=[e for e in deney.ETIKETLER if secrets.randbelow(2)]) for i in range(n)]
    before=copy.deepcopy(rows)
    if not ok(siniflandirma_olc(rows,deney.ETIKETLER)==deney.metrik_referans(rows,deney.ETIKETLER) and rows==before, 'yeni gözlemlerde sayımlar ve girdi değişmezliği'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_tax_gold_') as tmp:
    path=Path(tmp)/'gorulmemis.jsonl'
    gold=deney.dosya_referans(deney.ORNEK)
    for v in gold:
        v['id']=secrets.token_hex(3)
        v['metin']+=' Not: '+secrets.token_hex(3)
    path.write_text('\n'.join(json.dumps(v,ensure_ascii=False) for v in gold),encoding='utf-8')
    result=deney.deney(vaka_dosyasini_oku,taktikleri_bul,vakalari_siniflandir,siniflandirma_olc,path)
    for key,value in result['kontroller'].items():ok(value,'gerçek deney: '+key)
    accepted=all(result['kontroller'].values())
    ai_lab.kanit_yaz('saldiri-04-taksonomi',dict(result,kabul=accepted))
    ok(accepted, 'canlı yerel sınıflandırma, doğru metrik ve temizlik; model doğruluğu geçme şartı değil')

```

```solution
import ai_lab

import re

def taktikleri_bul(metin):
    if not isinstance(metin, str):
        raise ValueError("metin string olmalı")
    normal = metin.casefold().replace("\u0307", "")
    sinyaller = set()
    if re.search(r"(?<![a-z0-9])base64(?![a-z0-9])", normal):
        sinyaller.add("base64")
    for token in re.findall(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]+={0,2}(?![A-Za-z0-9+/=])", metin):
        govde = token.rstrip("=")
        if (len(token) >= 12 and len(token) % 4 == 0 and re.search(r"[A-Za-z]", govde)
                and re.search(r"[0-9+/=]", token) and "base64" not in token.casefold()):
            sinyaller.add("base64")
    if re.search(r"(?<![a-z0-9])hex(?![a-z0-9])", normal):
        sinyaller.add("hex")
    if any(len(t) >= 12 and len(t) % 2 == 0 for t in re.findall(
            r"(?<![a-z0-9])0x([0-9a-f]+)(?![0-9a-f])", normal)):
        sinyaller.add("hex")
    if any(x in normal for x in ("<|system|>", "<|developer|>", "system:", "developer mode", "admin onaylı")):
        sinyaller.add("sahte-rol")
    if any(x in normal for x in ("roleplay", "hypothetical", "fiction", "senaryo", "kurgu")):
        sinyaller.add("kurgu")
    if "önceki talimat" in normal and "yok say" in normal:
        sinyaller.add("onceki-talimati-yok-say")
    return sorted(sinyaller)

def vakalari_siniflandir(vakalar):
    bilinen = {"base64", "hex", "sahte-rol", "kurgu", "onceki-talimati-yok-say"}
    kimlikler = set()
    sonuc = []
    for vaka in vakalar:
        if not isinstance(vaka, dict):
            raise ValueError("geçersiz vaka")
        kimlik = vaka.get("id")
        metin = vaka.get("metin")
        sinyaller = vaka.get("sinyaller", [])
        if not isinstance(kimlik, str) or not kimlik or kimlik in kimlikler or not isinstance(metin, str):
            raise ValueError("geçersiz veya yinelenen vaka")
        kimlikler.add(kimlik)
        if not isinstance(sinyaller, (list, set, tuple)) or any(s not in bilinen for s in sinyaller):
            raise ValueError("bilinmeyen sinyal")
        kume = set(sinyaller)
        etiketler = set()
        if kume & {"base64", "hex"}:
            etiketler.add("donusturme")
        if kume & {"sahte-rol", "kurgu"}:
            etiketler.add("baglam-manipulasyonu")
        if "onceki-talimati-yok-say" in kume:
            etiketler.add("politika-catistirma")
        if not etiketler:
            etiketler.add("dogrudan-istek")
        sonuc.append({"id":kimlik, "metin":metin, "etiketler":sorted(etiketler)})
    return sonuc

def siniflandirma_olc(vakalar, etiketler):
    rapor = {}
    siniflar = set(etiketler)
    for vaka in vakalar:
        if set(vaka["beklenen"]) - siniflar or set(vaka["tahmin"]) - siniflar:
            raise ValueError("rapor dışı etiket")
    for sinif in etiketler:
        tp = sum(sinif in vaka["beklenen"] and sinif in vaka["tahmin"] for vaka in vakalar)
        fp = sum(sinif not in vaka["beklenen"] and sinif in vaka["tahmin"] for vaka in vakalar)
        fn = sum(sinif in vaka["beklenen"] and sinif not in vaka["tahmin"] for vaka in vakalar)
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        if precision is None or recall is None:
            f1 = None
        elif precision + recall:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0
        rapor[sinif] = {"tp":tp,"fp":fp,"fn":fn,"precision":precision,"recall":recall,"f1":f1}
    return rapor

def vaka_dosyasini_oku(yol):
    import json
    from pathlib import Path
    etiketler = {"baglam-manipulasyonu", "dogrudan-istek", "donusturme", "politika-catistirma"}
    sonuc = []
    kimlikler = set()
    for satir in Path(yol).read_text(encoding="utf-8").splitlines():
        if not satir.strip():
            continue
        vaka = json.loads(satir)
        if not isinstance(vaka, dict) or set(vaka) != {"id", "metin", "beklenen"}:
            raise ValueError("vaka alanları")
        kimlik, metin, beklenen = vaka["id"], vaka["metin"], vaka["beklenen"]
        if not isinstance(kimlik, str) or not kimlik or kimlik in kimlikler:
            raise ValueError("kimlik")
        if not isinstance(metin, str) or not 1 <= len(metin) <= 1500:
            raise ValueError("metin")
        if not isinstance(beklenen, list) or not beklenen or any(not isinstance(e, str) or e not in etiketler for e in beklenen):
            raise ValueError("etiket")
        if len(set(beklenen)) != len(beklenen) or "dogrudan-istek" in beklenen and len(beklenen) > 1:
            raise ValueError("etiket birleşimi")
        kimlikler.add(kimlik)
        sonuc.append(vaka)
    if not 1 <= len(sonuc) <= 8:
        raise ValueError("1..8 vaka")
    return sonuc

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_04 as deney
    deney.goster(vaka_dosyasini_oku, taktikleri_bul, vakalari_siniflandir, siniflandirma_olc)
```

```hint
JSONL satırlarını tek tek json.loads ile çöz. Önce kayıt ve alan türlerini, sonra kimlik ve etiket kurallarını doğrula. Önceki görevlerin çok etiket eşlemesini ve None metriklerini koru. Dosya okuyucunun gerçek dosya içeriğini kullandığından emin ol.
```
:::
